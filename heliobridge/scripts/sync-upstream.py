#!/usr/bin/env python3
"""Mirror the latest stable upstream Heliobridge GitHub release into this HAOS app repo."""
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
UPSTREAM_API = "https://api.github.com/repos/longsleep/heliobridge/releases/latest"
SOURCE_DIR = ROOT / "heliobridge" / "heliobridge-source"
CONFIG = ROOT / "heliobridge" / "config.yaml"
DOCKERFILE = ROOT / "heliobridge" / "Dockerfile"
VERSION_FILE = ROOT / "UPSTREAM_VERSION"


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "braumandl-heliobridge-haos-updater",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def fetch_bytes(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "braumandl-heliobridge-haos-updater"}
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        return response.read()


def cargo_version(path: Path) -> str:
    text = (path / "Cargo.toml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    if not match:
        raise RuntimeError("Cargo.toml version field not found")
    version = match.group(1)
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        raise RuntimeError(f"Unsupported upstream version format: {version}")
    return version


def safe_extract(tar_bytes: bytes, destination: Path) -> Path:
    archive_path = destination / "upstream.tar.gz"
    archive_path.write_bytes(tar_bytes)
    extract_dir = destination / "extract"
    extract_dir.mkdir()
    with tarfile.open(archive_path, "r:gz") as archive:
        members = archive.getmembers()
        # Reject absolute paths, traversal, and links. Upstream source should be a plain tree.
        for member in members:
            p = Path(member.name)
            if p.is_absolute() or ".." in p.parts or member.issym() or member.islnk():
                raise RuntimeError(f"Unsafe archive member: {member.name}")
        archive.extractall(extract_dir)
    roots = [p for p in extract_dir.iterdir() if p.is_dir()]
    if len(roots) != 1 or not (roots[0] / "Cargo.toml").is_file():
        raise RuntimeError("Unexpected GitHub source archive layout")
    return roots[0]


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"Could not update {label}: expected exactly one match, got {count}")
    return new_text


def main() -> int:
    release = fetch_json(UPSTREAM_API)
    if release.get("draft") or release.get("prerelease"):
        raise RuntimeError("GitHub API returned a draft or prerelease as latest")
    tag = release.get("tag_name", "")
    match = re.fullmatch(r"v?(\d+\.\d+\.\d+)", tag)
    if not match:
        raise RuntimeError(f"Unsupported upstream release tag: {tag!r}")
    version = match.group(1)
    current = VERSION_FILE.read_text(encoding="utf-8").strip() if VERSION_FILE.exists() else ""
    if current == version:
        print(f"Upstream Heliobridge {version} is already mirrored.")
        return 0

    archive_url = release.get("tarball_url")
    if not archive_url:
        raise RuntimeError("Latest GitHub release has no tarball_url")

    with tempfile.TemporaryDirectory(prefix="heliobridge-upstream-") as temp:
        temp_dir = Path(temp)
        archive_root = safe_extract(fetch_bytes(archive_url), temp_dir)
        downloaded_version = cargo_version(archive_root)
        if downloaded_version != version:
            raise RuntimeError(
                f"Release tag is {version}, but Cargo.toml reports {downloaded_version}"
            )

        # Prepare source in a sibling directory, then replace only the source tree.
        staged_source = temp_dir / "heliobridge-source"
        shutil.copytree(archive_root, staged_source)
        if SOURCE_DIR.exists():
            shutil.rmtree(SOURCE_DIR)
        shutil.copytree(staged_source, SOURCE_DIR)

    app_version = f"{version}.1"
    config_text = CONFIG.read_text(encoding="utf-8")
    config_text = replace_once(
        config_text,
        r'(?m)^version:\s*"[^\"]+"',
        f'version: "{app_version}"',
        "app package version",
    )
    CONFIG.write_text(config_text, encoding="utf-8")

    docker_text = DOCKERFILE.read_text(encoding="utf-8")
    docker_text = replace_once(
        docker_text,
        r"(?m)^# Unmodified source tree from https://github\.com/longsleep/heliobridge tag v\d+\.\d+\.\d+$",
        f"# Unmodified source tree from https://github.com/longsleep/heliobridge tag v{version}",
        "Dockerfile upstream source tag",
    )
    docker_text = replace_once(
        docker_text,
        r'io\.hass\.version="[^"]+"',
        f'io.hass.version="{app_version}"',
        "Dockerfile app version label",
    )
    DOCKERFILE.write_text(docker_text, encoding="utf-8")

    VERSION_FILE.write_text(version + "\n", encoding="utf-8")
    print(f"Mirrored upstream Heliobridge {version}; HAOS app package is {app_version}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
