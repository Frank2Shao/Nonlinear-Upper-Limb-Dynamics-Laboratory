from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = (
    PROJECT_ROOT / "static_src" / "images" / "brand" / "nuldl-club-logo-transparent.png"
)
SOURCE_SHA256 = "65114bdc25ca376408b3c715a02b100fa979ca1eba182c9f5baf87911eaa89d1"
OUTPUT_DIRECTORY = PROJECT_ROOT / "static" / "images" / "brand"
VARIANTS = {
    480: OUTPUT_DIRECTORY / "nuldl-club-logo-480.webp",
    800: OUTPUT_DIRECTORY / "nuldl-club-logo-800.webp",
    1200: OUTPUT_DIRECTORY / "nuldl-club-logo-1200.webp",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def render_variant(source: Image.Image, width: int) -> bytes:
    height = round(source.height * width / source.width)
    resized = source.resize((width, height), Image.Resampling.LANCZOS)
    output = BytesIO()
    # The transparent source dominates file size through its alpha channel, so
    # alpha is compressed separately; method 6 is the slowest, smallest encoder.
    resized.save(
        output,
        format="WEBP",
        quality=75,
        alpha_quality=70,
        method=6,
        lossless=False,
        exif=b"",
        xmp=b"",
    )
    return output.getvalue()


def build(*, check_only: bool) -> None:
    source_bytes = SOURCE_PATH.read_bytes()
    if sha256(source_bytes) != SOURCE_SHA256:
        raise RuntimeError("The approved Home logo source has been modified.")

    with Image.open(BytesIO(source_bytes)) as source:
        if source.format != "PNG" or source.size != (1254, 1254):
            raise RuntimeError("The approved Home logo must remain a 1254 x 1254 PNG.")
        source.load()
        if source.mode != "RGBA" or source.getchannel("A").getextrema() != (0, 255):
            raise RuntimeError(
                "The approved Home logo must retain its RGBA transparency."
            )

        for width, target in VARIANTS.items():
            generated_bytes = render_variant(source, width)
            if check_only:
                if not target.is_file() or target.read_bytes() != generated_bytes:
                    raise RuntimeError(f"Generated Home image is stale: {target.name}")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(generated_bytes)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build responsive Home logo assets from the approved source image."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify that committed generated images are current.",
    )
    arguments = parser.parse_args()
    build(check_only=arguments.check)


if __name__ == "__main__":
    main()
