#!/usr/bin/env python3

# Creates a simple static downloads HTML page and JSON file to accommodated downloading the executable from one url
# Usage: python downloads_index.py -c ../docs/CHANGELOG.md -p index.html -j index.json

import argparse
import json
import pathlib
import re
import subprocess
import sys

LIMIT = 20

HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Robocorp Action Server downloads</title>
<link rel="preload" as="font" href="https://cdn.robocorp.com/fonts/BarlowSemiCondensed-SemiBold.woff2" type="font/woff2" crossorigin="anonymous" />
<style>
@font-face {
    font-family: "Barlow Semi Condensed";
    font-style: normal;
    font-weight: 600;
    font-display: swap;
    src: url("https://cdn.robocorp.com/fonts/BarlowSemiCondensed-SemiBold.woff2") format("woff2");
}

html, body {
    margin: 0;
    padding: 0;
}

body {
    padding: 2ex 4ex;
    background-color: #1E273B; /* Neutral Gray/10 */
    color: #CBD3E1; /* Neutral Gray/70 */
    font-family: sans-serif;
}

h1, h2, h3 {
    font-family: "Barlow Semi Condensed", sans-serif;
    font-weight: 600;
    color: #F8FAFC; /* Neutral Gray/90 */
}

h1 {
    margin: 1.5ex 0;
}

h3 {
    margin: 1.5ex 0;
}

a {
    color: #8C7FFF; /* Purple/60 */
}

hr {
    display: block; height: 1px;
    border: 0;
    border-top: 1px solid #64728B; /* Neutral Gray/50 */
    margin: 3ex 0;
    padding: 0;
}

h3 a.subtle {
    text-decoration: none;
}
</style>
</head>
<body>
<h1>Robocorp Action Server downloads</h1>
<p>
Machine readable version of this list is available <a href="index.json">here</a>.
And change log can be found <a href="https://github.com/robocorp/robo/blob/master/action_server/docs/CHANGELOG.md">there</a>.
</p>
""".strip()

TESTED_HEADER = """
<h2>Tested versions</h2>
<p>Consider these as more stable.</p>
""".strip()

LATEST_HEADER = """
<hr />
<h2>Latest versions (max. %(limit)d)</h2>
""".strip()

ENTRY = """
<h3>%(version)s&nbsp;<a class="subtle" href="#%(version)s" name="%(version)s">^</a></h3>
<p>Release date: %(when)s</p>
<ul>
<li>Windows: <a href="%(windows)s">%(windows)s</a></li>
<li>MacOS: <a href="%(macos)s">%(macos)s</a></li>
<li>Linux: <a href="%(linux)s">%(linux)s</a></li>
</ul>
""".strip()

FOOTER = """
<hr />
</body>
</html>
""".strip()

VERSION_PATTERN = re.compile(r"^##\s+([\d.]+)[\s-]+([\d-]+)")
TAG_PATTERN = re.compile(r"^(cli-[0-9.]+)\D*$")

DIRECTORY = pathlib.Path(__file__).parent.absolute()
CHANGELOG = DIRECTORY.joinpath("CHANGELOG.md")
REPO_ROOT = DIRECTORY.parent.absolute()

FETCH_TAGS = f"git -C {REPO_ROOT} fetch --tag"
TAGLISTING = f"git -C {REPO_ROOT} tag --list --sort='-taggerdate'"


def sh(command):
    task = subprocess.Popen(
        [command], shell=True, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    )
    out, _ = task.communicate()
    return task.returncode, out.decode()


def gittags_top(count):
    sh(FETCH_TAGS)
    code, out = sh(TAGLISTING)
    if code == 0:
        for line in out.splitlines():
            if count == 0:
                break
            if found := TAG_PATTERN.match(line):
                yield (found.group(1))
                count -= 1


def changelog_top(filename, count):
    with open(filename) as source:
        for line in source:
            if count == 0:
                break
            if found := VERSION_PATTERN.match(line):
                yield (found.groups())
                count -= 1


def download(version, suffix):
    return "https://downloads.robocorp.com/action-server/releases/%s/%s" % (
        version,
        suffix,
    )


def process_versions(options, sink):
    biglist = tuple(changelog_top(options.changelog, 10000))
    limited = biglist[:LIMIT] if len(biglist) > LIMIT else biglist

    daymap = dict()
    for version, when in biglist:
        daymap[version] = when

    tested = list()
    edge = list()
    result = dict(tested=tested, edge=edge)

    seen = set()
    # For now we only include the latest releases part
    """
    sink.write(TESTED_HEADER)
    for version in gittags_top(3):
        details = dict(version=version, when=daymap.get(version, 'N/A'))
        details['windows'] = download(version, 'windows64/action-server.exe')
        details['linux'] = download(version, 'linux64/action-server')
        details['macos'] = download(version, 'macos64/action-server')
        sink.write(ENTRY % details)
        seen.add(version)
        tested.append(details)
    """

    sink.write(LATEST_HEADER % dict(limit=LIMIT))
    for version, when in limited:
        details = dict(version=version, when=when)
        details["windows"] = download(version, "windows64/action-server.exe")
        details["linux"] = download(version, "linux64/action-server")
        details["macos"] = download(version, "macos64/action-server")
        sink.write(ENTRY % details)
        if version in seen:
            break
        edge.append(details)
    return result


def process(options):
    with open(options.page, "w+") as sink:
        sink.write(HEADER % dict(limit=LIMIT))
        data = process_versions(options, sink)
        sink.write(FOOTER)
    with open(options.json, "w+") as sink:
        json.dump(data, sink, indent=1)


def commandline(args):
    parser = argparse.ArgumentParser(description="shim -- a simple tool shimming")
    parser.add_argument(
        "--changelog",
        "-c",
        type=str,
        default=CHANGELOG,
        help="Name for changelog file.",
    )
    parser.add_argument(
        "--page",
        "-p",
        type=str,
        default="build/index.html",
        help='Name for "index.html" file.',
    )
    parser.add_argument(
        "--json",
        "-j",
        type=str,
        default="build/index.json",
        help='Name for "index.json" file.',
    )
    return parser.parse_args(args)


if __name__ == "__main__":
    process(commandline(sys.argv[1:]))
