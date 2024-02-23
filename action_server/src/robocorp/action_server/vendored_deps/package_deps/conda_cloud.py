import datetime
import enum
import itertools
import json
import logging
import os
import shutil
import threading
import time
import typing
from concurrent.futures import Future
from contextlib import contextmanager
from functools import partial
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Sequence, Set, Tuple, Union

from ._deps_protocols import (
    CondaVersionInfo,
    IOnFinished,
    LatestIndexInfoTypedDict,
    SubdirToBuildAndDependsJsonBytesType,
)

if typing.TYPE_CHECKING:
    # No need for sqlite3 until it's actually used.
    from sqlite3 import Cursor
else:
    Cursor = object

log = logging.getLogger(__name__)

TABLE_PACKAGES_SQL = """
    CREATE TABLE Packages (
        package_id INTEGER PRIMARY KEY,
        package_name TEXT UNIQUE
    );
"""

TABLE_VERSIONS_SQL = """
    CREATE TABLE Versions (
        version_id INTEGER PRIMARY KEY,
        package_id INTEGER,
        depends TEXT,
        timestamp INTEGER,
        version TEXT,
        subdir TEXT,
        build TEXT,
        FOREIGN KEY (package_id) REFERENCES Packages(package_id)
    );
"""

CREATE_INDEXES_SQL = [
    """
CREATE UNIQUE INDEX package_name_index 
ON Packages(package_name);
""",
    """
CREATE INDEX package_id_on_versions_index 
ON Versions(package_id);
""",
    """
CREATE INDEX version_index 
ON Versions(version);
""",
]


class State(enum.Enum):
    initial = 1
    downloading = 2
    done = 3


def timestamp_to_datetime(timestamp_milliseconds: float) -> datetime.datetime:
    timestamp_seconds = timestamp_milliseconds / 1000  # Convert to seconds
    return datetime.datetime.fromtimestamp(timestamp_seconds)


class SqliteQueries:
    def __init__(self, sqlite_file: Union[Path, Sequence[Path]]):
        sqlite_files: Sequence[Path]
        if isinstance(sqlite_file, Path):
            sqlite_files = [sqlite_file]
        else:
            sqlite_files = sqlite_file
        self.sqlite_files: Sequence[Path] = sqlite_files

    @contextmanager
    def db_cursors(
        self, db_cursor: Optional[Sequence[Cursor]] = None
    ) -> Iterator[Sequence[Cursor]]:
        if db_cursor is not None:
            yield db_cursor
            return

        import sqlite3

        db_cursors: List[Cursor] = []
        db_connections: list = []
        for path in self.sqlite_files:
            db_connections.append(sqlite3.connect(path))
            db_cursors.append(db_connections[-1].cursor())
        try:
            yield db_cursors
        finally:
            for cursor in db_cursors:
                try:
                    cursor.close()
                except Exception:
                    log.exception("Error closing sqlite cursor.")

            for db_connection in db_connections:
                try:
                    db_connection.close()
                except Exception:
                    log.exception("Error closing sqlite connection.")

    def query_names(self, db_cursors: Optional[Sequence[Cursor]] = None) -> Set[str]:
        with self.db_cursors(db_cursors) as db_cursors:
            package_names: Set[str] = set()
            for db_cursor in db_cursors:
                db_cursor.execute("SELECT package_name FROM packages")
                rows = db_cursor.fetchall()

                package_names.update(row[0] for row in rows)
            return package_names

    def query_versions(
        self, package_name, db_cursors: Optional[Sequence[Cursor]] = None
    ) -> Set[str]:
        with self.db_cursors(db_cursors) as db_cursors:
            versions: Set[str] = set()
            for db_cursor in db_cursors:
                db_cursor.execute(
                    """
SELECT Versions.version
FROM Packages
INNER JOIN Versions ON Packages.package_id = Versions.package_id
WHERE Packages.package_name = ?
""",
                    (package_name,),
                )
                rows = db_cursor.fetchall()

                # Note that we exclude release candidates and development versions.
                versions.update(
                    row[0]
                    for row in rows
                    if "_rc" not in row[0] and "_dev" not in row[0]
                )

            return versions

    def query_version_info(
        self,
        package_name: str,
        version: str,
        db_cursors: Optional[Sequence[Cursor]] = None,
    ) -> CondaVersionInfo:
        """
        Note that the same package/version may have multiple infos
        because of build ids (but in this API this isn't given,
        so, if the same depends are available then they're shown
        only as one).
        """
        with self.db_cursors(db_cursors) as db_cursors:
            subdir_to_build_and_depends: SubdirToBuildAndDependsJsonBytesType = {}
            max_timestamp = 0

            for db_cursor in db_cursors:
                db_cursor.execute(
                    """
SELECT Versions.depends, Versions.timestamp, Versions.subdir, Versions.build
FROM Packages
INNER JOIN Versions ON Packages.package_id = Versions.package_id
WHERE Packages.package_name = ? and Versions.version = ?
""",
                    (package_name, version),
                )

                for row in db_cursor.fetchall():
                    depends, timestamp, subdir, build = row
                    try:
                        lst = subdir_to_build_and_depends[subdir]
                    except KeyError:
                        lst = subdir_to_build_and_depends[subdir] = []

                    lst.append((build, depends))

                    max_timestamp = max(max_timestamp, timestamp)

            return CondaVersionInfo(
                package_name, version, max_timestamp, subdir_to_build_and_depends
            )


def version_key(version_info: CondaVersionInfo):
    from .conda_impl.conda_version import VersionOrder

    version_order = VersionOrder(version_info.version)
    return version_order


def sort_conda_version_infos(
    versions: Union[Sequence[CondaVersionInfo], Set[CondaVersionInfo]],
) -> List[CondaVersionInfo]:
    return list(sorted(versions, key=version_key))


def version_str_key(version: str):
    from .conda_impl.conda_version import VersionOrder

    version_order = VersionOrder(version)
    return version_order


def sort_conda_versions(
    versions: Union[Sequence[str], Set[str]],
) -> List[str]:
    return list(sorted(versions, key=version_str_key))


# Can be used in tests to index just a few libraries.
INDEX_FOR_LIBRARIES: Optional[Set[str]] = None


def index_conda_info(json_file: Path, target_sqlite_file: Path):
    import sqlite3

    # Using msgspec cuts the time in half (from 1 second to 0.5 seconds
    # for the full process in one use case).
    # Not only the decoding is faster (from 0.44 to 0.28), but accessing
    # things from the structure it provides is faster than accessing from
    # python structures (dict/list).
    import msgspec

    # Use Struct types to define the JSON schema. For efficiency we only define
    # the fields we actually need.
    class Package(msgspec.Struct):
        name: str
        depends: Optional[List[str]] = []
        version: Optional[str] = ""
        subdir: Optional[str] = ""
        timestamp: Optional[int] = 0
        build: Optional[str] = ""

    class Info(msgspec.Struct):
        subdir: str = ""

    class RepoData(msgspec.Struct):
        info: Info
        packages: Optional[Dict[str, Package]]
        packages_conda: Optional[Dict[str, Package]] = msgspec.field(
            name="packages.conda",
            default=None,
        )

    # Decode the data as a `RepoData` type
    with open(json_file, "rb") as stream:
        bytes_read = stream.read()
    data = msgspec.json.decode(bytes_read, type=RepoData)

    # This is actually the arch.
    default_subdir = data.info.subdir

    # Step 3: Create SQLite database and table
    db_connection = sqlite3.connect(target_sqlite_file)
    try:
        db_cursor = db_connection.cursor()
        try:
            db_cursor.execute(TABLE_PACKAGES_SQL)

            db_cursor.execute(TABLE_VERSIONS_SQL)

            for sql in CREATE_INDEXES_SQL:
                db_cursor.execute(sql)

            package_name_to_id: Dict[str, int] = {}
            rows = []
            # Step 4: Insert package information into the database
            for package_filename, package_info in itertools.chain(
                (data.packages or {}).items(), (data.packages_conda or {}).items()
            ):
                # "2dfatmic-1.0-hbb7d975_1.tar.bz2": {
                #   "build": "hbb7d975_1",
                #   "build": 1,
                #   "depends": [
                #     "libgfortran 5.*",
                #     "libgfortran5 >=9.3.0"
                #   ],
                #   "license": "Public Domain",
                #   "license_family": "OTHER",
                #   "md5": "0abb38856a2c0a45595bbf3888405507",
                #   "name": "2dfatmic",
                #   "sha256": "54d7427b37a4984e97c0529f94c927f9bccfbc9e5b57d0fb52030e4be92ce38a",
                #   "size": 173360,
                #   "subdir": "osx-64",
                #   "timestamp": 1602245771778,
                #   "version": "1.0"
                # },
                name = package_info.name
                if not name:
                    continue
                if INDEX_FOR_LIBRARIES:
                    if name not in INDEX_FOR_LIBRARIES:
                        continue

                try:
                    package_id = package_name_to_id[name]
                except KeyError:
                    db_cursor.execute(
                        """INSERT INTO Packages (package_name) VALUES (?);""", (name,)
                    )
                    lastrowid = db_cursor.lastrowid
                    if lastrowid is None:
                        continue
                    package_id = package_name_to_id[name] = lastrowid

                depends = msgspec.json.encode(package_info.depends)
                version = package_info.version
                timestamp = package_info.timestamp  # 0 means unknown
                build = package_info.build  # '' means unknown
                subdir = package_info.subdir or default_subdir

                if not version:
                    log.info(
                        f"Unable to get version for package_filename: {package_filename}. Subdir: {subdir}"
                    )
                    continue
                rows.append((package_id, depends, timestamp, version, subdir, build))

            db_cursor.executemany(
                "INSERT INTO Versions (package_id, depends, timestamp, version, subdir, build) VALUES (?, ?, ?, ?, ?, ?);",
                rows,
            )
        finally:
            db_cursor.close()

        db_connection.commit()
    finally:
        db_connection.close()


Arch = str


class _Callback(object):
    """
    Note that it's thread safe to register/unregister callbacks while callbacks
    are being notified, but it's not thread-safe to register/unregister at the
    same time in multiple threads.
    """

    def __init__(self):
        self._callbacks = []

    def register(self, callback):
        new_callbacks = self._callbacks[:]
        new_callbacks.append(callback)
        self._callbacks = new_callbacks

    def unregister(self, callback):
        new_callbacks = [x for x in self._callbacks if x != callback]
        self._callbacks = new_callbacks

    def __call__(self, *args, **kwargs):
        for c in self._callbacks:
            try:
                c(*args, **kwargs)
            except Exception:
                log.exception("Error in callback.")

    def __len__(self):
        return len(self._callbacks)

    def clear(self):
        self._callbacks = []


class _AfterDownloadMakeSqlite:
    def __init__(
        self, available_arch: List[Arch], cache_dir: Path, index_cache_dir: Path
    ):
        self._available_arch = available_arch
        self._lock = threading.Lock()
        self._count = 0
        self._call_on_finished = _Callback()
        self._finished = False
        self._arch_to_sqlite: Dict[str, Path] = {}
        self._index_cache_dir = index_cache_dir
        self._cache_dir = cache_dir

    def _convert_to_sqlite(self, json_file: Path, arch: Arch) -> Path:
        target_sqlite_file = self._index_cache_dir / f"{arch}.db"
        index_conda_info(json_file, target_sqlite_file)
        return target_sqlite_file

    def __call__(self, download_future: "Future[Tuple[Path, Arch]]"):
        json_file = None
        try:
            json_file, arch = download_future.result()
            self._arch_to_sqlite[arch] = self._convert_to_sqlite(json_file, arch)
        except BaseException:
            # Handle all exceptions (because the on_finished calls
            # must always be called).
            log.exception("Error when converting to sqlite.")

        try:
            if json_file is not None:
                # After we convert to sqlite, there's no need to keep the
                # (big) json file around anymore.
                os.remove(json_file)
        except Exception:
            log.exception(f"Error removing: {json_file}.")

        with self._lock:
            self._count += 1
            last = self._count == len(self._available_arch)
            if last:
                self._finished = True
                # If we're the last, change the information on the
                # cache dir to use.
                latest_path = self._cache_dir / "latest_index_info.json"
                latest_path.write_text(
                    json.dumps(
                        {
                            # Note: save relative to the cache dir.
                            "index_dir": os.path.basename(str(self._index_cache_dir)),
                            "timestamp": datetime.datetime.now().isoformat(),
                        }
                    ),
                    encoding="utf-8",
                )

                self._call_on_finished()

    def register_on_finished(self, on_finished: IOnFinished):
        with self._lock:
            if self._finished:
                on_finished()
            else:
                self._call_on_finished.register(on_finished)


def _extract_dir_number(dirname) -> int:
    try:
        _n, number = dirname.split("_")
        return int(number)
    except Exception:
        # Return zero if not what we expected.
        return 0


class CondaCloud:
    """
    Manages information from conda.

    The cache_dir is where we hold information on disk.

    The basic structure is:
        /cache_dir
        /cache_dir/tmp_0001 <-- used to download information and build the sqlite db.
        /cache_dir/tmp_0001/noarch.json <-- actually removed after the sqlite db is built.
        /cache_dir/tmp_0001/win-64.json
        /cache_dir/index_0001/noarch.db <-- sqlite db we actually use
        /cache_dir/index_0001/win-64.db
        /cache_dir/latest_index_info.json <-- will be used to point to index_0001
    """

    def __init__(self, cache_dir: Path, reindex_if_old: bool = True) -> None:
        self._base_url = "https://conda.anaconda.org/conda-forge"
        self._available_arch = [
            "noarch",
            "win-64",
            "linux-64",
            "osx-64",
        ]

        self._json_name = "current_repodata.json"

        self._cache_dir = cache_dir
        cache_dir.mkdir(parents=True, exist_ok=True)

        self._lock = threading.Lock()
        self._state: State = State.initial
        self._call_on_finished: List[IOnFinished] = []

        if self.is_information_cached():
            if reindex_if_old:
                # When a new CondaCloud is created, set it as done already if
                # 4 hours haven't elapsed from the last time it was requested.
                latest_index_info = self.load_latest_index_info()
                if latest_index_info is not None:
                    diff = datetime.datetime.now() - latest_index_info["timestamp"]
                    eight_hours = datetime.timedelta(hours=4)
                    if diff < eight_hours:
                        self._state = State.done
            else:
                self._state = State.done

    def _download(self, url: str, target_json: Path, arch: str) -> Tuple[Path, Arch]:
        import urllib.request

        CHUNK_SIZE = 32768

        with target_json.open("wb") as stream:
            request = urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "Mozilla"})
            )

            if request.status != 200:
                raise RuntimeError(
                    f"HTTP error (unable to open: {url}): {request.status}"
                )

            with request:
                for chunk in iter(lambda: request.read(CHUNK_SIZE), b""):
                    if chunk:  # Filter out keep-alive new chunks
                        stream.write(chunk)
        return target_json, arch

    def _call_on_finished_callbacks(self):
        for on_finished in self._call_on_finished:
            try:
                on_finished()
            except Exception:
                log.exception("Unexpected exception.")
        del self._call_on_finished[:]

    def schedule_update(
        self, on_finished: Optional[IOnFinished] = None, wait=False, force=False
    ) -> None:
        """
        This can be called at any time (in any thread). It schedules the download
        of the information we need.

        If it's currently downloading already it'll not do a new request and if it
        was already downloaded it'll only redownload if force == True.
        """
        import random

        with self._lock:
            if on_finished is not None:
                self._call_on_finished.append(on_finished)

            if self._state == State.initial:
                # Keep on going...
                pass

            elif self._state == State.downloading:
                # Ok, already downloading, nothing to do besides registering
                # the on_finished if given (already done)
                return

            elif self._state == State.done:
                if force:
                    # Forcing: go back to the initial state
                    self._state = State.initial
                else:
                    # Already finished, just call the registered callback now.
                    self._call_on_finished_callbacks()
                    return

            assert self._state in (State.initial, State.done)

            # We need to compute the target for the files
            dir_entries = os.listdir(self._cache_dir)

            stale_dirs: List[Path] = []
            max_tries = 3
            for i in range(max_tries):
                max_number: int = 0
                for dir_name in dir_entries:
                    if dir_name.startswith("tmp_") or dir_name.startswith("index_"):
                        max_number = max(max_number, _extract_dir_number(dir_name))

                for dir_name in dir_entries:
                    if dir_name.startswith("tmp_") or dir_name.startswith("index_"):
                        i = _extract_dir_number(dir_name)
                        if i < max_number:
                            stale_dirs.append(self._cache_dir / dir_name)

                max_number += 1

                tmp_cache_dir = self._cache_dir / ("tmp_%04d" % (max_number,))
                index_cache_dir = self._cache_dir / ("index_%04d" % (max_number,))
                try:
                    # If we failed to create the dir,
                    tmp_cache_dir.mkdir(parents=True, exist_ok=False)
                    index_cache_dir.mkdir(parents=True, exist_ok=False)
                except Exception:
                    if i == max_tries - 1:
                        raise
                    # Sleep a bit and retry, we could be running in parallel
                    # with another process (so, we may compute a new max_number).
                    time.sleep(random.random())
                else:
                    break

            # Just change the state when we have the directory structure in place.
            # (but still inside the self._lock session).
            self._state = State.downloading

            on_done = _AfterDownloadMakeSqlite(
                self._available_arch, self._cache_dir, index_cache_dir
            )

            def mark_as_done(*args, **kwargs):
                with self._lock:
                    self._state = State.done

                    # Now, remove stale dirs.
                    for directory in stale_dirs:
                        try:
                            shutil.rmtree(directory, ignore_errors=False)
                        except Exception:
                            log.exception(
                                f"Error removing old conda cloud dirs from: {directory}"
                            )

                    self._call_on_finished_callbacks()

            on_done.register_on_finished(mark_as_done)

            if on_finished:
                self._call_on_finished.append(on_finished)

        from concurrent.futures.thread import ThreadPoolExecutor

        executor = ThreadPoolExecutor(max_workers=4)

        for arch in self._available_arch:
            name = tmp_cache_dir / f"{arch}.json"
            # Something as:
            # https://conda.anaconda.org/conda-forge/linux-64/current_repodata.json
            url = f"{self._base_url}/{arch}/{self._json_name}"
            future = executor.submit(partial(self._download, url, name, arch))
            future.add_done_callback(on_done)
        executor.shutdown(wait=wait)

    def load_latest_index_info(self) -> Optional[LatestIndexInfoTypedDict]:
        try:
            latest_dir_info = self._cache_dir / "latest_index_info.json"
            with latest_dir_info.open("rb") as stream:
                info = json.load(stream)

            # index_dir is relative to the .json.
            index_dir_info: LatestIndexInfoTypedDict = {
                "index_dir": str(self._cache_dir / info["index_dir"]),
                "timestamp": datetime.datetime.fromisoformat(info["timestamp"]),
            }
            return index_dir_info
        except Exception:
            return None

    def _load_latest_index_dir_location(self) -> Optional[Path]:
        latest_dir_info = self.load_latest_index_info()
        if not latest_dir_info:
            return None

        try:
            index_dir_location = latest_dir_info["index_dir"]
        except Exception:
            return None

        index_dir_path = Path(index_dir_location)
        return index_dir_path

    def _iter_index_files(self) -> Iterator[Path]:
        """
        Returns:
            An iterator which provides the paths to the sqlite files
            which contain the indexed conda informations (one for each arch).
        """
        index_dir_path = self._load_latest_index_dir_location()
        if not index_dir_path or not index_dir_path.exists():
            return

        for arch in self._available_arch:
            f = index_dir_path / f"{arch}.db"
            if f.exists():
                yield f

    def is_information_cached(self) -> bool:
        index_dir_path = self._load_latest_index_dir_location()
        if not index_dir_path or not index_dir_path.exists():
            return False

        for arch in self._available_arch:
            if not (index_dir_path / f"{arch}.db").exists():
                return False

        return True

    def sqlite_queries(self) -> Optional[SqliteQueries]:
        index_dir_files = tuple(self._iter_index_files())
        if not index_dir_files:
            return None
        return SqliteQueries(index_dir_files)
