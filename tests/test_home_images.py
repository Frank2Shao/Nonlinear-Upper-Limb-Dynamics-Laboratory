import hashlib
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "static_src" / "images"
GENERATED_DIRECTORY = PROJECT_ROOT / "static" / "images"

# (source, SHA-256, size, mode, generated pattern, generated widths)
APPROVED_SOURCES = {
    "logo": (
        "brand/nuldl-club-logo-transparent.png",
        "65114bdc25ca376408b3c715a02b100fa979ca1eba182c9f5baf87911eaa89d1",
        (1254, 1254),
        "RGBA",
        "brand/nuldl-club-logo-{width}.webp",
        (480, 800, 1200),
    ),
    "gold-texture": (
        "brand/gold-texture-source.png",
        "436775146db6758db4d9e258002ba9821b3c683fd898dbd1517952a690c6b13c",
        (1600, 640),
        "RGB",
        "brand/gold-texture-{width}.webp",
        (800, 1600),
    ),
    "gold-texture-button": (
        "brand/gold-texture-source.png",
        "436775146db6758db4d9e258002ba9821b3c683fd898dbd1517952a690c6b13c",
        (1600, 640),
        "RGB",
        "brand/gold-texture-button-{width}.webp",
        (800,),
    ),
    "hero-specimen": (
        "home/hero-specimen-source.png",
        "0fa0ed296310f24b07297a492a7b6dd7366d21dbe5d67351f039c864526431c9",
        (1122, 1402),
        "RGBA",
        "home/hero-specimen-{width}.webp",
        (560, 1120),
    ),
}


@pytest.mark.parametrize("name", APPROVED_SOURCES)
def test_approved_image_sources_are_preserved_exactly(name):
    relative_path, expected_hash, size, mode, _, _ = APPROVED_SOURCES[name]
    source = SOURCE_DIRECTORY / relative_path

    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected_hash
    with Image.open(source) as image:
        assert image.format == "PNG"
        assert image.size == size
        assert image.mode == mode
        if mode == "RGBA":
            assert image.getchannel("A").getextrema() == (0, 255)


@pytest.mark.parametrize("name", APPROVED_SOURCES)
def test_generated_variants_are_compressed_webp_images_without_metadata(name):
    relative_path, _, size, mode, pattern, widths = APPROVED_SOURCES[name]
    source = SOURCE_DIRECTORY / relative_path

    for width in widths:
        generated = GENERATED_DIRECTORY / pattern.format(width=width)
        assert generated.stat().st_size < source.stat().st_size
        with Image.open(generated) as image:
            assert image.format == "WEBP"
            assert image.size == (width, round(size[1] * width / size[0]))
            assert image.mode == mode
            assert "exif" not in image.info
            assert "xmp" not in image.info
            if mode == "RGBA":
                alpha = image.getchannel("A")
                assert alpha.getextrema() == (0, 255)
                assert alpha.getpixel((0, 0)) == 0


def test_committed_image_variants_are_reproducible():
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "build_home_images.py"),
            "--check",
        ],
        capture_output=True,
        check=False,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )

    output = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, output
