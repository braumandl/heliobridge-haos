from pathlib import Path
import re
import yaml

root = Path(__file__).resolve().parents[1]
cfg = yaml.safe_load((root / "config.yaml").read_text())
script = (root / "run.sh").read_text()

assert cfg["version"] == "1.2.0"
assert cfg["slug"] == "heliobridge_updater"
assert cfg["hassio_api"] is True
assert cfg["hassio_role"] == "manager"
assert cfg["options"]["target_app_name"] == "Heliobridge"
assert cfg["options"]["target_app_slug"] == ""
assert "local_apps" not in (root / "config.yaml").read_text()
assert 'readonly TARGET=' not in script
assert 'APP_SLUG=' not in script
assert "/addons" in script
assert "/store/addons/${slug}/update" in script
assert "target_repository_url" in script
assert "SUPERVISOR_TOKEN" in script
assert not re.search(r'\\b(?:192\\.168\\.|10\\.|172\\.(?:1[6-9]|2[0-9]|3[01])\\.)', script)
assert "longsleep/heliobridge/releases/latest" not in script
assert (root / "README.md").exists()
assert (root / "DOCS.md").exists()
print("Package static checks passed.")
