import datetime as dt
import hashlib
import json
from contextlib import suppress
from logging import getLogger
from xml.etree import ElementTree as ET

import requests
from dateutil.parser import parse
from django.db import transaction
from django.db.utils import IntegrityError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_scopes import scope, scopes_disabled
from pretalx.celery_app import app
from pretalx.event.models import Event
from pretalx.person.models import SpeakerProfile, User
from pretalx.schedule.models import Room, TalkSlot
from pretalx.submission.models import Submission, SubmissionType, Track

from .models import UpstreamResult

logger = getLogger("pretalx_downstream")


@app.task()
def task_refresh_upstream_schedule(event_slug):
    with scopes_disabled():
        event = Event.objects.get(slug__iexact=event_slug)
    with scope(event=event):
        logger.info(f"processing {event.slug}")
        url = event.settings.downstream_upstream_url
        if not url:
            raise Exception(
                _(
                    "The pretalx-downstream plugin is installed for {event_slug}, but no upstream URL was configured."
                ).format(event_slug=event_slug)
            )

        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(
                _(
                    "Could not retrieve upstream schedule for {event_slug}, received {response} response."
                ).format(event_slug=event_slug, response=response.status_code)
            )

        content = response.content.decode()
        last_result = event.upstream_results.order_by("timestamp").first()
        m = hashlib.sha256()
        m.update(response.content)
        current_result = m.hexdigest()

        if last_result:
            logger.debug(f"last known checksum: {last_result.checksum}")
            logger.debug(f"checksum now: {current_result}")

            if current_result == last_result.checksum:
                event.settings.upstream_last_sync = now()
                return

        root = ET.fromstring(content)
        schedule_version = root.find("version").text

        if event.settings.downstream_discard_after:
            schedule_version = schedule_version.split(
                event.settings.downstream_discard_after
            )[0]

        logger.debug(f"Found schedule version '{schedule_version}'")

        release_new_version = (
            not event.current_schedule
            or schedule_version != event.current_schedule.version
        )
        logger.debug(f"release_new_version={release_new_version}")
        changes, schedule = process_frab(
            root, event, release_new_version=release_new_version
        )
        UpstreamResult.objects.create(
            event=event, schedule=schedule, changes=json.dumps(changes), content=content
        )
        event.settings.upstream_last_sync = now()
        logger.info(f"refreshed schedule of {event.slug}")


@transaction.atomic()
def process_frab(root, event, release_new_version):
    """Take an xml document root and an event, and releases a schedule with the
    data from the xml document.

    Copied directly from pretalx.schedule.utils.process_frab
    """

    changes = dict()
    for day in root.findall("day"):
        for rm in day.findall("room"):
            guid = rm.attrib.get("guid")
            if guid:
                room, _ = Room.objects.get_or_create(
                    event=event, guid=guid, defaults={"name": rm.attrib["name"]}
                )
            else:
                room, _ = Room.objects.get_or_create(
                    event=event, name=rm.attrib["name"]
                )
            for talk in rm.findall("event"):
                changes.update(_create_talk(talk=talk, room=room, event=event))

    schedule = None
    if release_new_version:
        schedule_version = root.find("version").text

        if event.settings.downstream_discard_after:
            schedule_version = schedule_version.split(
                event.settings.downstream_discard_after
            )[0]

        try:
            event.wip_schedule.freeze(schedule_version, notify_speakers=False)
            schedule = event.schedules.get(version=schedule_version)
        except Exception as e:
            raise Exception(
                f'Could not import "{event.name}" schedule version "{schedule_version}": {e}.'
            )

        schedule.talks.update(is_visible=True)
        start = schedule.talks.order_by("start").first().start
        end = schedule.talks.order_by("-end").first().end
        event.date_from = start.date()
        event.date_to = end.date()
        event.save()
    return changes, schedule


def _create_user(name, event):
    user, _ = User.objects.get_or_create(
        email=f"{name[:110]}@localhost".lower(), defaults={"name": name[:120]}
    )
    SpeakerProfile.objects.get_or_create(user=user, event=event)
    return user


def _get_changes(talk, optout, sub):
    changes = dict()
    change_tracking_data = {
        "title": talk.find("title").text,
        "do_not_record": optout,
        "content_locale": talk.find("language").text if talk.find("language") else "en",
    }
    for key in ("description", "abstract"):
        try:
            change_tracking_data[key] = talk.find(key.text)
        except Exception:
            change_tracking_data[key] = ""
    if talk.find("subtitle").text:
        change_tracking_data["description"] = (
            talk.find("subtitle").text + "\n" + change_tracking_data["description"]
        ).strip()

    for key, value in change_tracking_data.items():
        if not getattr(sub, key) == value:
            changes[key] = {"old": getattr(sub, key), "new": value}
            setattr(sub, key, value)
    return changes


def _create_talk(*, talk, room, event):
    date = talk.find("date").text
    start = parse(date + " " + talk.find("start").text)
    hours, minutes = talk.find("duration").text.split(":")
    duration = dt.timedelta(hours=int(hours), minutes=int(minutes))
    duration_in_minutes = duration.total_seconds() / 60
    try:
        end = parse(date + " " + talk.find("end").text)
    except AttributeError:
        end = start + duration
    sub_type = SubmissionType.objects.filter(
        event=event, name=talk.find("type").text, default_duration=duration_in_minutes
    ).first()

    if not sub_type:
        sub_type = SubmissionType.objects.create(
            name=talk.find("type").text or "default",
            event=event,
            default_duration=duration_in_minutes,
        )

    track = None
    if talk.find("track").text:
        tracks = Track.objects.filter(
            event=event, name__icontains=talk.find("track").text
        )
        track = [t for t in tracks if str(t.name) == talk.find("track").text]

        if track:
            track = track[0]
        else:
            track = Track.objects.create(name=talk.find("track").text, event=event)

    optout = False
    with suppress(AttributeError):
        optout = talk.find("recording").find("optout").text == "true"

    code = None
    if (
        Submission.objects.filter(code__iexact=talk.attrib["id"], event=event).exists()
        or not Submission.objects.filter(code__iexact=talk.attrib["id"]).exists()
    ):
        code = talk.attrib["id"]
    elif (
        Submission.objects.filter(
            code__iexact=talk.attrib["guid"][:16], event=event
        ).exists()
        or not Submission.objects.filter(code__iexact=talk.attrib["guid"][:16]).exists()
    ):
        code = talk.attrib["guid"][:16]

    try:
        sub, created = Submission.objects.get_or_create(
            event=event, code=code, defaults={"submission_type": sub_type}
        )
    except IntegrityError:
        new_code = f"{event.slug[:16-len(code)]}{code}"
        sub, created = Submission.objects.get_or_create(
            event=event, code=new_code, defaults={"submission_type": sub_type}
        )

    sub.submission_type = sub_type
    if track:
        sub.track = track

    changes = _get_changes(talk, optout, sub)
    sub.save()

    persons = talk.find("persons")
    if persons:
        for person in persons.findall("person"):
            if person.text and person.text.strip():
                user = _create_user(person.text.strip(), event)
                sub.speakers.add(user)

    slot, _ = TalkSlot.objects.get_or_create(
        submission=sub, schedule=event.wip_schedule, defaults={"is_visible": True}
    )
    slot.room = room
    slot.is_visible = True
    slot.start = start
    slot.end = end
    slot.save()
    if not created and changes:
        return {sub.code: changes}
    return dict()
