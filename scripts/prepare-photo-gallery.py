"""Prepare gallery photos for the static site; source files remain unpublished."""
from pathlib import Path
import subprocess
import sys
import tempfile
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Photo"
TARGET = ROOT / "site" / "media" / "photos"
PRIVATE_TOOLS = ROOT / ".private" / "gallery-tools"
if PRIVATE_TOOLS.is_dir():
    sys.path.insert(0, str(PRIVATE_TOOLS))
import imageio_ffmpeg

PHOTO_SOURCES = {
    "20260914_平山先生誕生日会.jpg": "20260914-hirayama-birthday",
    "20260401_Kateさんと食事会.jpg": "20260401-dinner-with-kate",
    "20260124_菅野先生古希祝賀会.JPG": "20260124-kanno-70th-birthday",
    "20250613_光がかかわる触媒化学シンポジウム後の飲み会.jpg": "20250613-photocatalysis-symposium-gathering",
    "20250403_全固体電池研究センターメンバー.jpg": "20250403-assb-center-members",
    "20250403_平山研メンバー.jpg": "20250403-hirayama-lab-members",
    "20240411_全固体電池研究センターメンバー.jpg": "20240411-assb-center-members",
    "20240411_平山研メンバー.jpg": "20240411-hirayama-lab-members",
    "240328_謝恩会.HEIC": "20240328-appreciation-party",
    "20230220_歓迎会&お疲れ様会.jpg": "20230220-welcome-and-farewell-party",
}

TARGET.mkdir(parents=True, exist_ok=True)
ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
processed = []
with tempfile.TemporaryDirectory(prefix="gallery-photos-") as temporary:
    temporary = Path(temporary)
    for source_name, stem in PHOTO_SOURCES.items():
        source = SOURCE / source_name
        if not source.is_file():
            raise FileNotFoundError(source)
        image_source = source
        if source.suffix.lower() == ".heic":
            image_source = temporary / f"{stem}.png"
            subprocess.run([ffmpeg, "-y", "-i", str(source), "-frames:v", "1", str(image_source)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with Image.open(image_source) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
            image.thumbnail((1800, 1350), Image.Resampling.LANCZOS)
            target = TARGET / f"{stem}.webp"
            image.save(target, "WEBP", quality=86, method=6)
            processed.append((source_name, target.name, image.size))
for source_name, target_name, size in processed:
    print(f"{source_name} -> {target_name}: {size[0]}x{size[1]}")
print(f"Prepared {len(processed)} gallery photos.")
