import hashlib
import json
import re
from pathlib import Path

import pytest
from django.conf import settings


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def theme_tokens() -> dict[str, str]:
    """Read colour tokens from the single Tailwind source of design tokens."""
    source = (settings.BASE_DIR / "static_src" / "css" / "site.css").read_text(
        encoding="utf8"
    )
    theme = re.search(r"@theme\s*\{(?P<body>.*?)\}", source, re.S)
    assert theme, "static_src/css/site.css must declare an @theme block."
    return dict(re.findall(r"(--color-[\w-]+):\s*(#[0-9a-fA-F]{6})\s*;", theme["body"]))


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(first: str, second: str) -> float:
    lighter, darker = sorted(
        (relative_luminance(first), relative_luminance(second)), reverse=True
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_static_and_template_directories_are_configured():
    assert settings.TEMPLATES[0]["DIRS"] == [settings.BASE_DIR / "templates"]
    assert settings.STATICFILES_DIRS == [settings.BASE_DIR / "static"]
    assert settings.STATIC_ROOT == settings.BASE_DIR / "staticfiles"


def test_generated_vendor_manifest_matches_local_assets():
    manifest_path = settings.BASE_DIR / "static" / "vendor" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf8"))

    package = json.loads(
        (settings.BASE_DIR / "package.json").read_text(encoding="utf8")
    )

    # Every runtime npm dependency is vendored, at the exact locked version.
    assert manifest["packages"] == package["dependencies"]
    for relative_path, expected_hash in manifest["files"].items():
        assert sha256(settings.BASE_DIR / relative_path) == expected_hash


def test_built_css_contains_design_and_accessibility_tokens():
    css = (settings.BASE_DIR / "static" / "css" / "site.css").read_text(encoding="utf8")
    tokens = theme_tokens()

    for name in ("--color-ink", "--color-gold-bright"):
        assert re.search(rf"{name}:\s*{tokens[name]}", css, re.I), name
    assert "Barlow Condensed" in css
    assert "Inter" in css
    assert re.search(r"prefers-reduced-motion:\s*reduce", css)
    assert ":focus-visible" in css


@pytest.mark.parametrize(
    ("foreground", "background", "minimum"),
    (
        ("--color-cream", "--color-ink", 4.5),
        ("--color-muted", "--color-ink", 4.5),
        ("--color-ink", "--color-gold", 4.5),
        ("--color-error", "--color-surface", 4.5),
        ("--color-gold-bright", "--color-ink", 3),
    ),
)
def test_key_text_and_focus_colours_meet_wcag_contrast_thresholds(
    foreground, background, minimum
):
    tokens = theme_tokens()

    assert contrast_ratio(tokens[foreground], tokens[background]) >= minimum


def test_phase_one_templates_do_not_load_third_party_cdns():
    roots = [settings.BASE_DIR / "templates", settings.BASE_DIR / "apps"]
    forbidden = ("cdn.jsdelivr", "unpkg.com", "fonts.googleapis", "tailwindcss.com")

    contents = "\n".join(
        path.read_text(encoding="utf8")
        for root in roots
        for path in root.rglob("*.html")
    )
    assert not any(host in contents for host in forbidden)
