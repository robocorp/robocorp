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
RCC_URLS = {
    "Windows": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/windows64/rcc.exe",
    "Darwin": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/macos64/rcc",
    "Linux": f"https://downloads.robocorp.com/rcc/releases/v{RCC_VERSION}/linux64/rcc",
}


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
def include(ctx, target_os=None):
    """Download static assets to include/ directory"""
    if target_os:
        rcc_url = RCC_URLS[target_os]
        rcc_exe = "rcc.exe" if target_os == "Windows" else "rcc"
        rcc_path = CURDIR / "include" / "bin" / rcc_exe
    else:
        # Default is to use current platforms settings
        rcc_url = RCC_URLS[platform.system()]
        rcc_exe = RCC_EXE
        rcc_path = RCC_PATH

    print(f"Downloading '{rcc_url}' to '{rcc_path}'")
    urllib.request.urlretrieve(rcc_url, rcc_path)
    st = os.stat(rcc_path)
    os.chmod(rcc_path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return rcc_path


@task
def build_all_platforms(ctx):
    """Build for all platforms"""
    for arch, go_os, target_dir, executable_name in [
        ("amd64", "Windows", "windows64", "robo.exe"),
        ("amd64", "Linux", "linux64", "robo"),
        ("amd64", "Darwin", "macos64", "robo"),
    ]:
        rcc_path = include(ctx, target_os=go_os)
        os.environ["GOOS"] = go_os.lower()
        os.environ["GOARCH"] = arch

        # RCC uses -ldsflags, '-s' flags for building, are they relevant for us?
        # sh "go build -ldflags '-s' -o build/linux64/ ./cmd/..."
        # RCC makes a shasum, should we also do that?
        # sh "sha256sum build/linux64/* || true"
        os.makedirs(BUILD / target_dir, exist_ok=True)
        run(ctx, "go", "build", "-o", BUILD / target_dir / executable_name, CURDIR)

        # Remove the rcc executable, so it's not included for next platform in the loop
        rcc_path.unlink()


@task
def sign_macos(ctx):
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
            'xcrun codesign --entitlements ./signing/entitlements.mac.plist --deep -o runtime -s "Robocorp Technologies, Inc." --timestamp build/macos64/robo'
        )
        print("codesign")
        # ctx.run('codesign --entitlements entitlements.mac.plist --deep -o runtime -s "Robocorp Technologies, Inc." --timestamp build/macos64/arm/rcc')
    finally:
        Path("cert.p12").unlink()


@task
def notarize_macos(ctx):
    apple_id = os.environ.get("MACOS_APP_ID_FOR_SIGNING")
    assert apple_id
    signing_password = os.environ.get("MACOS_APP_ID_PASS_FOR_SIGNING")
    assert signing_password

    # removed args that we didn't previously use, but that notarytool man page included: --issuer <uuid>
    # these are just confusing: --key path/to/AuthKey_7UD13000.p8 --key-id 7UD13000, it seems we don't need them if we're using the "raw" apple account params

    ctx.run("zip robo.zip build/macos64/robo")
    # TODO: can we do a sort of bundling so that the data is inside the binary, to reduce latency when it's opened first time
    ctx.run(
        f"xcrun notarytool submit robo.zip --apple-id {apple_id} --password {signing_password} --team-id 2H9N5J72C7 --wait"
    )
    ctx.run("mkdir -p dist")
    ctx.run("unzip robo.zip -d dist")
    ctx.run("ls dist/")
    ctx.run("ls dist/build")
