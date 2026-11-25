#!/usr/bin/env python3
"""Mirror the newest stable semver Git tag from longsleep/heliobridge."""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAGS_API = "https://api.github.com/repos/longsleep/heliobridge/tags?per_page=100"
SOURCE_DIR = ROOT / "heliobridge" / "heliobridge-source"
CONFIG = ROOT / "heliobridge" / "config.yaml"
DOCKERFILE = ROOT / "heliobridge" / "Dockerfile"
VERSION_FILE = ROOT / "UPSTREAM_VERSION"
TAG_RE = re.compile(r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def request(url: str) -> bytes:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "braumandl-heliobridge-haos-sync",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()


def fetch_tags() -> list[dict]:
    tags: list[dict] = []
    # Follow GitHub pagination; do not assume the API's display order is semver order.
    for page in range(1, 11):
        url = TAGS_API + f"&page={page}"
        page_tags = json.loads(request(url))
        if not isinstance(page_tags, list):
            raise RuntimeError("GitHub tags API returned an unexpected response")
        tags.extend(page_tags)
        if len(page_tags) < 100:
            break
    else:
        raise RuntimeError("More than 1,000 tags; refusing incomplete version selection")
    return tags


def latest_stable_tag(tags: list[dict]) -> tuple[str, tuple[int, int, int], str]:
    candidates = []
    for item in tags:
        name = item.get("name", "")
        match = TAG_RE.fullmatch(name)
        if not match:
            continue  # Excludes prereleases and non-semver tags.
        version_tuple = tuple(int(part) for part in match.groups())
        tarball_url = item.get("tarball_url")
        if not tarball_url:
            raise RuntimeError(f"Tag {name} has no tarball URL")
        candidates.append((version_tuple, name, tarball_url))
    if not candidates:
        raise RuntimeError("No stable X.Y.Z Git tags found in upstream repository")
    version_tuple, tag, tarball_url = max(candidates, key=lambda entry: entry[0])
    return tag, version_tuple, tarball_url


def cargo_version(path: Path) -> str:
    text = (path / "Cargo.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    if not match:
        raise RuntimeError("Cargo.toml version field not found")
    version = match.group(1)
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise RuntimeError(f"Unsupported Cargo.toml version format: {version}")
    return version


def safe_extract(tar_bytes: bytes, destination: Path) -> Path:
    archive_path = destination / "upstream.tar.gz"
    archive_path.write_bytes(tar_bytes)
    extract_dir = destination / "extract"
    extract_dir.mkdir()
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        if len(members) > 20000:
            raise RuntimeError("Upstream archive contains too many entries")
        total_size = 0
        for member in members:
            p = Path(member.name)
            if p.is_absolute() or ".." in p.parts:
                raise RuntimeError(f"Unsafe archive path: {member.name}")
            if not (member.isdir() or member.isfile()):
                raise RuntimeError(f"Unsupported archive entry type: {member.name}")
            total_size += member.size
            if total_size > 500 * 1024 * 1024:
                raise RuntimeError("Upstream archive exceeds 500 MiB uncompressed")
        # Python's data filter blocks path traversal and unsafe file modes.
        archive.extractall(extract_dir, filter="data")
    roots = [p for p in extract_dir.iterdir() if p.is_dir()]
    if len(roots) != 1 or not (roots[0] / "Cargo.toml").is_file():
        raise RuntimeError("Unexpected GitHub tag archive layout")
    return roots[0]


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Could not update {label}: expected one match, got {count}")
    return new_text


def main() -> int:
    tag, version_tuple, tarball_url = latest_stable_tag(fetch_tags())
    version = ".".join(str(part) for part in version_tuple)
    current = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else ""
    if current == version:
        print(f"Upstream Heliobridge {tag} is already mirrored.")
        return 0

    with tempfile.TemporaryDirectory(prefix="heliobridge-upstream-", dir=ROOT) as temp:
        temp_dir = Path(temp)
        archive_root = safe_extract(request(tarball_url), temp_dir)
        downloaded_version = cargo_version(archive_root)
        if downloaded_version != version:
            raise RuntimeError(
                f"Git tag is {tag}, but Cargo.toml reports {downloaded_version}"
            )

        staged_source = temp_dir / "heliobridge-source.new"
        shutil.copytree(archive_root, staged_source)

        app_version = f"{version}.1"
        config_text = replace_once(
            CONFIG.read_text(encoding="utf-8"),
            r'(?m)^version:\s*"[^"]+"',
            f'version: "{app_version}"',
            "app package version",
        )
        docker_text = DOCKERFILE.read_text(encoding="utf-8")
        docker_text = replace_once(
            docker_text,
            r"(?m)^# Unmodified source tree from https://github\.com/longsleep/heliobridge tag v?\d+\.\d+\.\d+$",
            f"# Unmodified source tree from https://github.com/longsleep/heliobridge tag {tag}",
            "Dockerfile upstream source tag",
        )
        docker_text = replace_once(
            docker_text,
            r'io\.hass\.version="[^"]+"',
            f'io.hass.version="{app_version}"',
            "Dockerfile app version label",
        )

        # Prepare metadata before touching the current source tree.
        staged_config = temp_dir / "config.yaml.new"
        staged_docker = temp_dir / "Dockerfile.new"
        staged_version = temp_dir / "UPSTREAM_VERSION.new"
        staged_config.write_text(config_text, encoding="utf-8")
        staged_docker.write_text(docker_text, encoding="utf-8")
        staged_version.write_text(version + "\n", encoding="utf-8")

        old_source = temp_dir / "heliobridge-source.old"
        had_old_source = SOURCE_DIR.exists()
        try:
            if had_old_source:
                os.replace(SOURCE_DIR, old_source)
            os.replace(staged_source, SOURCE_DIR)
            os.replace(staged_config, CONFIG)
            os.replace(staged_docker, DOCKERFILE)
            os.replace(staged_version, VERSION_FILE)
        except Exception:
            if SOURCE_DIR.exists():
                shutil.rmtree(SOURCE_DIR)
            if had_old_source and old_source.exists():
                os.replace(old_source, SOURCE_DIR)
            raise

    print(f"Mirrored upstream {tag}; HAOS app package version is {app_version}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
