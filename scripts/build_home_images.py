"""Build the responsive WebP images used by the public pages.

Each approved source image is protected by its SHA-256, format, size and mode;
the generated variants are deterministic, so ``--check`` can detect drift.
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIRECTORY = PROJECT_ROOT / "static_src" / "images"
OUTPUT_DIRECTORY = PROJECT_ROOT / "static" / "images"
# --color-gold-highlight; dark texture areas are lifted towards it.
GOLD_HIGHLIGHT = (0xF2, 0xBF, 0x5A)


@dataclass(frozen=True)
class ImageSource:
    label: str
    source: Path
    sha256: str
    size: tuple[int, int]
    mode: str
    # Generated file name pattern ("{width}" is replaced) relative to static/images.
    output: str
    widths: tuple[int, ...]
    quality: int
    alpha_quality: int | None = None
    # Blend strength towards GOLD_HIGHLIGHT, weighted by each pixel's darkness.
    lift_darks: float | None = None
    # An RGBA source without any transparency, encoded as RGB.
    opaque: bool = False

    def target(self, width: int) -> Path:
        return OUTPUT_DIRECTORY / self.output.format(width=width)


SOURCES = (
    ImageSource(
        label="Home logo",
        source=SOURCE_DIRECTORY / "brand" / "nuldl-club-logo-transparent.png",
        sha256="65114bdc25ca376408b3c715a02b100fa979ca1eba182c9f5baf87911eaa89d1",
        size=(1254, 1254),
        mode="RGBA",
        output="brand/nuldl-club-logo-{width}.webp",
        widths=(480, 800, 1200),
        # The transparent source dominates file size through its alpha channel,
        # so alpha is compressed separately.
        quality=75,
        alpha_quality=70,
    ),
    ImageSource(
        label="Gold texture",
        source=SOURCE_DIRECTORY / "brand" / "gold-texture-source.png",
        sha256="436775146db6758db4d9e258002ba9821b3c683fd898dbd1517952a690c6b13c",
        size=(1600, 640),
        mode="RGB",
        output="brand/gold-texture-{width}.webp",
        # 1x and 2x tiles for material fills and gold display text.
        widths=(800, 1600),
        quality=80,
    ),
    ImageSource(
        label="Gold texture",
        source=SOURCE_DIRECTORY / "brand" / "gold-texture-source.png",
        sha256="436775146db6758db4d9e258002ba9821b3c683fd898dbd1517952a690c6b13c",
        size=(1600, 640),
        mode="RGB",
        output="brand/gold-texture-button-{width}.webp",
        # Behind small dark text (buttons, tags): the dark patches are lifted so
        # every pixel keeps at least 4.5:1 against --color-on-gold.
        widths=(800,),
        quality=82,
        lift_darks=0.7,
    ),
    ImageSource(
        label="Hero specimen photo",
        source=SOURCE_DIRECTORY / "home" / "hero-specimen-source.png",
        sha256="95bf86e14599468e3dc55497681be12c573b2b9775ceff3bd823e3f530e63ec8",
        size=(1448, 1086),
        mode="RGBA",
        output="home/hero-specimen-{width}.webp",
        # Covers the whole wide-screen Hero (up to 80rem wide), so one width
        # close to the source suffices.
        widths=(1440,),
        quality=78,
        # The photo sits on its own black ground; the page fades its edges.
        opaque=True,
    ),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lift_dark_areas(image: Image.Image, strength: float) -> Image.Image:
    darkness = ImageOps.invert(image.convert("L"))
    mask = darkness.point(lambda value: min(255, round(value * strength)))
    highlight = Image.new("RGB", image.size, GOLD_HIGHLIGHT)
    return Image.composite(highlight, image, mask)


def render_variant(image: Image.Image, spec: ImageSource, width: int) -> bytes:
    if spec.opaque:
        image = image.convert("RGB")
    if spec.lift_darks is not None:
        image = lift_dark_areas(image, spec.lift_darks)
    height = round(image.height * width / image.width)
    resized = image.resize((width, height), Image.Resampling.LANCZOS)
    options = {"quality": spec.quality}
    if spec.alpha_quality is not None:
        options["alpha_quality"] = spec.alpha_quality
    output = BytesIO()
    # Method 6 is the slowest, smallest encoder; metadata is never carried over.
    resized.save(
        output,
        format="WEBP",
        method=6,
        lossless=False,
        exif=b"",
        xmp=b"",
        **options,
    )
    return output.getvalue()


def load_source(spec: ImageSource) -> Image.Image:
    source_bytes = spec.source.read_bytes()
    if sha256(source_bytes) != spec.sha256:
        raise RuntimeError(f"The approved {spec.label} source has been modified.")

    image = Image.open(BytesIO(source_bytes))
    expected = f"{spec.size[0]} x {spec.size[1]} {spec.mode} PNG"
    if image.format != "PNG" or image.size != spec.size or image.mode != spec.mode:
        raise RuntimeError(f"The approved {spec.label} must remain a {expected}.")
    image.load()
    alpha = image.getchannel("A").getextrema() if spec.mode == "RGBA" else None
    if alpha is not None and alpha != ((255, 255) if spec.opaque else (0, 255)):
        state = "stay fully opaque" if spec.opaque else "retain its transparency"
        raise RuntimeError(f"The approved {spec.label} must {state}.")
    return image


def build(*, check_only: bool) -> None:
    for spec in SOURCES:
        with load_source(spec) as image:
            for width in spec.widths:
                target = spec.target(width)
                generated_bytes = render_variant(image, spec, width)
                if check_only:
                    if not target.is_file() or target.read_bytes() != generated_bytes:
                        raise RuntimeError(f"Generated image is stale: {target.name}")
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(generated_bytes)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build responsive WebP images from the approved source images."
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
