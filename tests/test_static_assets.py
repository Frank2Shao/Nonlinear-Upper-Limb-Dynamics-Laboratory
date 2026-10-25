import hashlib
import json
from pathlib import Path

from django.conf import settings


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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

    assert manifest["packages"] == {
        "@fontsource/barlow-condensed": "5.3.0",
        "@fontsource/inter": "5.3.0",
        "alpinejs": "3.17.5",
        "htmx.org": "2.0.11",
        "maplibre-gl": "6.15.0",
    }
    for relative_path, expected_hash in manifest["files"].items():
        assert sha256(settings.BASE_DIR / relative_path) == expected_hash


def test_built_css_contains_design_and_accessibility_tokens():
    css = (settings.BASE_DIR / "static" / "css" / "site.css").read_text(encoding="utf8")

    assert "--color-ink:#090909" in css
    assert "--color-gold-bright:#ffd166" in css
    assert "Barlow Condensed" in css
    assert "Inter" in css
    assert "prefers-reduced-motion:reduce" in css
    assert ":focus-visible" in css


def test_key_text_and_focus_colours_meet_wcag_contrast_thresholds():
    assert contrast_ratio("#f4f0e7", "#090909") >= 4.5
    assert contrast_ratio("#bdb5a7", "#090909") >= 4.5
    assert contrast_ratio("#090909", "#d9ad50") >= 4.5
    assert contrast_ratio("#ff938b", "#171717") >= 4.5
    assert contrast_ratio("#ffd166", "#090909") >= 3


def test_phase_one_templates_do_not_load_third_party_cdns():
    roots = [settings.BASE_DIR / "templates", settings.BASE_DIR / "apps"]
    forbidden = ("cdn.jsdelivr", "unpkg.com", "fonts.googleapis", "tailwindcss.com")

    contents = "\n".join(
        path.read_text(encoding="utf8")
        for root in roots
        for path in root.rglob("*.html")
    )
    assert not any(host in contents for host in forbidden)
