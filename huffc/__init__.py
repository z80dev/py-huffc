import contextlib
import os
import pathlib
import itertools

import requests
import semantic_version as semver


class VersionManager:
    HUFFC_DIR = pathlib.Path.home() / ".huffc"

    def __init__(self):
        self.session = None
        self.HUFFC_DIR.mkdir(exist_ok=True)

    def fetch_remote_versions(self):
        versions = []
        for page in itertools.count(1):
            r = self.session.get(
                "https://api.github.com/repos/huff-language/huff-rs/releases",
                params={"per_page": 100, "page": page},
            )

            for release in (releases := r.json()):
                with contextlib.suppress(ValueError):
                    versions.append(semver.Version(release["name"].removeprefix("v")))

            if len(releases) < 100:
                break

        return versions

    def fetch_local_versions(self):
        versions = []
        for binary in self.HUFFC_DIR.iterdir():
            versions.append(semver.Version(binary.removeprefix("huffc-")))

        return versions

    def __enter__(self):
        session = requests.Session()
        session.headers.update({"Accept": "application/json", "X-GitHub-Api-Version": "2022-11-28"})

        if token := os.getenv("GITHUB_TOKEN"):
            session.headers.update({"Authorization": f"token {token}"})

        self.session = session
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()
        self.session = None
