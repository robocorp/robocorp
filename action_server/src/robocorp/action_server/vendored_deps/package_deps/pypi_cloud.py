import datetime
import logging
import typing
import weakref
from typing import Dict, Iterator, List, Optional, Sequence, Union

from ._deps_protocols import PyPiInfoTypedDict, ReleaseData, Versions, VersionStr

log = logging.getLogger(__name__)

# Interesting:
# https://github.com/python-poetry/poetry/blob/master/src/poetry/repositories/pypi_repository.py


class PackageData:
    def __init__(self, package_name: str, info: PyPiInfoTypedDict) -> None:
        self.package_name = package_name
        self._info: PyPiInfoTypedDict = info

        self._releases: Dict[str, ReleaseData] = {}

    def add_release(self, version_str: VersionStr, release_info: List[dict]) -> None:
        """
        Args:
            version_str: The version we have info on.
            release_info: For each release we may have a list of files available.
        """
        from .pip_impl import pip_packaging_version

        version = pip_packaging_version.parse(version_str)
        upload_time: Optional[str] = None
        for dct in release_info:
            upload_time = dct.get("upload_time")
            if upload_time:
                break

        self._releases[version_str] = ReleaseData(version, version_str, upload_time)

    @property
    def latest_version(self) -> VersionStr:
        return self._info["version"]

    def get_release_data(self, version: VersionStr) -> Optional[ReleaseData]:
        if not self._releases:
            return None
        try:
            return self._releases[version]
        except KeyError:
            return None

    def get_last_release_data(self) -> Optional[ReleaseData]:
        """
        Provides the last release data (if there's any release).
        """
        return self.get_release_data(self.latest_version)

    def iter_versions_released_after(
        self, after_datetime: Optional[datetime.datetime]
    ) -> Iterator[ReleaseData]:
        """
        Args:
            after_datetime: if none all releases (except pre-releases) will
            be provided.
        """

        last_release_data = self.get_last_release_data()
        latest_upload_datetime: Optional[datetime.datetime] = None
        if last_release_data and last_release_data.upload_time:
            latest_upload_datetime = datetime.datetime.strptime(
                last_release_data.upload_time, "%Y-%m-%dT%H:%M:%S"
            )

        for release_data in self._releases.values():
            if release_data.upload_time:
                upload_datetime = datetime.datetime.strptime(
                    release_data.upload_time, "%Y-%m-%dT%H:%M:%S"
                )

                if latest_upload_datetime:
                    # Hide pre-releases.
                    if upload_datetime > latest_upload_datetime:
                        continue

                if after_datetime is None or upload_datetime >= after_datetime:
                    yield release_data

    def iter_versions_newer_than(self, version: Versions) -> Iterator[ReleaseData]:
        for release_data in self.iter_versions_released_after(None):
            if release_data.version > version:
                yield release_data

    @property
    def info(self):
        return self._info


class PyPiCloud:
    def __init__(
        self, get_base_urls_weak_method: Optional[weakref.WeakMethod] = None
    ) -> None:
        self._cached_package_data: Dict[str, PackageData] = {}
        self._cached_cloud: Dict[str, PackageData] = {}
        self._last_base_urls: Sequence[str] = ()

        if get_base_urls_weak_method is None:
            # use pypi.org
            def get_weak():
                def get_pypi_url():
                    return ("https://pypi.org",)

                return get_pypi_url

            self.get_base_urls_weak_method = get_weak
        else:
            self.get_base_urls_weak_method = get_base_urls_weak_method

    def _get_json_from_cloud(self, url: str) -> Optional[dict]:
        try:
            return typing.cast(dict, self._cached_cloud[url])
        except KeyError:
            pass

        import json
        import urllib.request

        try:
            request = urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla"})
            )
            if request.status == 200:
                with request:
                    data = request.read().decode("utf-8", "replace")
                self._cached_cloud[url] = json.loads(data)
            else:
                log.info(
                    f"Unable to get url (as json): {url}. Status code: {request.status}"
                )
                return None
        except Exception as e:
            log.info(f"Unable to get url (as json): {url}. Error: {e}")
            return None

        return typing.cast(dict, self._cached_cloud[url])

    def get_package_data(self, package_name: str) -> Optional[PackageData]:
        get_base_urls = self.get_base_urls_weak_method()
        if get_base_urls is None:
            return None

        base_urls = get_base_urls()
        if base_urls != self._last_base_urls:
            # We need to clear packages if urls changed.
            self._last_base_urls = base_urls
            self._cached_package_data.clear()
            self._cached_cloud.clear()

        try:
            return self._cached_package_data[package_name]
        except KeyError:
            pass

        for base_url in base_urls:
            if base_url.endswith("/"):
                base_url = base_url[:-1]
            data = self._get_json_from_cloud(f"{base_url}/pypi/{package_name}/json")
            if not data:
                continue  # go to the next url

            try:
                releases = data["releases"]
            except KeyError:
                continue  # go to the next url

            try:
                info = data["info"]
            except KeyError:
                continue  # go to the next url

            package_data = PackageData(package_name, info)
            if releases and isinstance(releases, dict):
                for release_number, release_info in releases.items():
                    package_data.add_release(release_number, release_info)

            self._cached_package_data[package_name] = package_data
            return self._cached_package_data[package_name]

        # If there was no match, return.
        return None

    def get_versions_newer_than(
        self, package_name: str, version: Union[Versions, VersionStr]
    ) -> List[VersionStr]:
        """
        Args:
            package_name: The name of the package
            version: The minimum version (versions returned must be > than this one).

        Returns:
            A sorted list containing the versions > than the one passed (the last
            entry is the latest version).
        """

        if isinstance(version, VersionStr):
            from .pip_impl import pip_packaging_version

            version = pip_packaging_version.parse(version)

        package_data = self.get_package_data(package_name)
        if package_data is None:
            return []

        return [
            x.version_str
            for x in sorted(package_data.iter_versions_newer_than(version))
        ]
