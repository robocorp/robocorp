import shutil
from pathlib import Path

from setuptools import find_packages, setup

_here = Path(__file__).parent.resolve()
_parent = _here.parent
_root = _parent.parent

_readme = _here / "README.md"
_thirdparty = _here / "ThirdPartyNotices.txt"
_license = _here / "LICENSE"
_copyright = _here / "COPYRIGHT"

# Note: always overwrite files from the original place if those exist.

_origin = _parent / _readme.name
if _origin.exists():
    shutil.copy2(_origin, _readme)

for path in [_thirdparty, _license, _copyright]:
    _origin = _root / path.name
    if _origin.exists():
        shutil.copy2(_origin, path)

setup(
    name="robocorp-logging",
    version="0.0.3",
    description="Structured logging for Robocorp Robots.",
    long_description=_readme.read_text(),
    url="https://github.com/robocorp/robocorp-logging",
    author="Fabio Zadrozny",
    license="Apache-2.0",
    copyright="Robocorp Technologies, Inc.",
    packages=find_packages(),
    package_data={"robocorp_logging": ["py.typed"]},
    zip_safe=False,
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
    # List run-time dependencies here. These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[test]
    extras_require={
        "test": [
            "mock",
            "pytest",
            "pytest-regressions==1.0.6",
            "pytest-xdist",
            "pytest-timeout",
        ],
    },
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
