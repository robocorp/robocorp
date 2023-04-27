import urllib.request
import os
import platform
import stat
import sys
from pathlib import Path

from invoke import task

CURDIR = Path(__file__).parent
BUILD = CURDIR / "build"

RCC_EXE = "rcc.exe" if platform.system() == "Windows" else "rcc"
RCC_PATH = CURDIR / "include" / "bin" / RCC_EXE
RCC_VERSION = "11.28.0"
RCC_URL = {
    "Windows": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/windows64/rcc.exe",
    "Darwin": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/macos64/rcc",
    "Linux": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/linux64/rcc",
}[platform.system()]


def run(ctx, *parts):
    args = " ".join(str(part) for part in parts)
    ctx.run(args, pty=platform.system() != "Windows", echo=True)


@task
def pretty(ctx):
    """Auto-format code"""
    run(ctx, "gofmt", "-s", "-w", CURDIR)


@task
def build(ctx):
    """Build robo binary"""
    if not RCC_PATH.is_file():
        print("rcc executable missing, run 'invoke include'")
        sys.exit(1)

    BUILD.mkdir(parents=True, exist_ok=True)
    run(ctx, "go", "build", "-o", BUILD / "robo", CURDIR)


@task
def include(ctx):
    """Download static assets to include/ directory"""
    print(f"Downloading '{RCC_URL}' to '{RCC_PATH}'")
    urllib.request.urlretrieve(RCC_URL, RCC_PATH)

    st = os.stat(RCC_PATH)
    os.chmod(RCC_PATH, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


@task
def sign(ctx):
    cert_data = os.environ.get("MACOS_SIGNING_CERT")
    assert cert_data
    cert_password = os.environ.get("MACOS_SIGNING_CERT_PASSWORD")
    assert cert_password
    try:
        print("create-keychain")
        ctx.run(f"xcrun security create-keychain -p {cert_password} build.keychain")
        print("default-keychain")
        ctx.run("xcrun security default-keychain -s build.keychain")
        print("unlock-keychain")
        ctx.run(f"xcrun security unlock-keychain -p {cert_password} build.keychain")
        print("cert.p12")
        ctx.run(f"echo {cert_data}| base64 --decode -o cert.p12")
        print("security import")
        ctx.run(f"xcrun security import cert.p12 -A -P {cert_password}")
        print("security set-key-partition-list")
        ctx.run(
            f"xcrun security set-key-partition-list -S apple-tool:,apple: -s -k {cert_password} build.keychain"
        )
        print("codesign")
        ctx.run(
            # TODO: change to build/macos64/robo
            'xcrun codesign --entitlements ./signing/entitlements.mac.plist --deep -o runtime -s "Robocorp Technologies, Inc." --timestamp build/robo'
        )
        print("codesign")
        # ctx.run('codesign --entitlements entitlements.mac.plist --deep -o runtime -s "Robocorp Technologies, Inc." --timestamp build/macos64/arm/rcc')
    finally:
        Path("cert.p12").unlink()


@task
def notarize(ctx):
    # ctx.run(
    #     'xcrun altool --notarize-app --username "AC_USERNAME" --password "@keychain:AC_PASSWORD" --asc-provider <ProviderShortname> --file macos64/rcc'
    # )

    apple_id = os.environ.get("MACOS_APP_ID_FOR_SIGNING")
    assert apple_id
    signing_password = os.environ.get("MACOS_APP_ID_PASS_FOR_SIGNING")
    assert signing_password

    # removed args that we didn't previously use, but that notarytool man page included: --issuer <uuid>
    # these are just confusing: --key path/to/AuthKey_7UD13000.p8 --key-id 7UD13000, it seems we don't need them if we're using the "raw" apple account params

    ctx.run("zip robo.zip build/robo")
    ctx.run(
        f"xcrun notarytool submit robo.zip --apple-id {apple_id} --password {signing_password} --team-id 2H9N5J72C7 --wait"
    )
    ctx.run("mkdir dist")
    ctx.run("unzip robo.zip -d dist")
    ctx.run("ls dist/")
    ctx.run("ls dist/build")
