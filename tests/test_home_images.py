import hashlib
import subprocess
import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).parents[1]
SOURCE = (
    PROJECT_ROOT / "static_src" / "images" / "brand" / "nuldl-club-logo-transparent.png"
)
GENERATED_DIRECTORY = PROJECT_ROOT / "static" / "images" / "brand"


def test_approved_logo_source_is_preserved_exactly():
    source_bytes = SOURCE.read_bytes()

    assert (
        hashlib.sha256(source_bytes).hexdigest()
        == "65114bdc25ca376408b3c715a02b100fa979ca1eba182c9f5baf87911eaa89d1"
    )
    with Image.open(SOURCE) as image:
        assert image.format == "PNG"
        assert image.size == (1254, 1254)
        assert image.mode == "RGBA"
        assert image.getchannel("A").getextrema() == (0, 255)


def test_responsive_logo_variants_are_compressed_square_webp_images():
    for width in (480, 800, 1200):
        generated = GENERATED_DIRECTORY / f"nuldl-club-logo-{width}.webp"
        assert generated.stat().st_size < SOURCE.stat().st_size
        with Image.open(generated) as image:
            assert image.format == "WEBP"
            assert image.size == (width, width)
            assert image.mode == "RGBA"
            alpha = image.getchannel("A")
            assert alpha.getextrema() == (0, 255)
            assert alpha.getpixel((0, 0)) == 0


def test_committed_logo_variants_are_reproducible():
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
        timeout=60,
    )

    output = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, output
