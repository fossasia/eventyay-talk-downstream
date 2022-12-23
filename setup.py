import os
from distutils.command.build import build

from django.core import management
from setuptools import find_packages, setup

try:
    with open(
        os.path.join(os.path.dirname(__file__), "README.rst"), encoding="utf-8"
    ) as f:
        long_description = f.read()
except Exception:
    long_description = ""


class CustomBuild(build):
    def run(self):
        management.call_command("compilemessages", verbosity=1)
        build.run(self)


cmdclass = {"build": CustomBuild}


setup(
    name="pretalx-downstream",
    version="1.1.5",
    description="This plugin allows you to use pretalx passively, by letting it import another event's schedule.",
    long_description=long_description,
    url="https://github.com/pretalx/pretalx-downstream",
    author="Tobias Kunze",
    author_email="r@rixx.de",
    license="Apache Software License",
    install_requires=[],
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    cmdclass=cmdclass,
    entry_points="""
[pretalx.plugin]
pretalx_downstream=pretalx_downstream:PretalxPluginMeta
""",
)
