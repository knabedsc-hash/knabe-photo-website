"""Prepare gallery media for the static site; source files remain unpublished."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps
import shutil
import subprocess
import tempfile
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "CoverPictures"
COVERS = ROOT / "site" / "media" / "covers"
VIDEO_SOURCE = ROOT / "RhCrOx-AgTaO3.MOV"
VIDEO_TARGET = ROOT / "site" / "media" / "videos" / "rhcrox-agtao3.mp4"
POPPLER = Path(r"C:\Users\waken\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
TARGET_HEIGHT = 1200
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

COVERS.mkdir(parents=True, exist_ok=True)
VIDEO_TARGET.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix="covers-") as temporary:
    temporary_path = Path(temporary)
    processed = []
    for source in sorted(SOURCE.iterdir()):
        if not source.is_file():
            continue
        if source.suffix.lower() == ".pdf":
            prefix = temporary_path / source.stem
            arguments = [str(POPPLER), "-f", "1", "-l", "1", "-r", "220", "-png"]
            if source.stem in {"2023AdvEnergyMater", "2024AdvMaterInterfaces"}:
                arguments.append("-cropbox")
            subprocess.run(arguments + [str(source), str(prefix)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            image_source = next(temporary_path.glob(source.stem + "-1.png"))
        elif source.suffix.lower() in {".jpg", ".jpeg"}:
            image_source = source
        else:
            continue
        with Image.open(image_source) as original:
            image = ImageOps.exif_transpose(original).convert("RGB")
            width = round(image.width * TARGET_HEIGHT / image.height)
            image = image.resize((width, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            target = COVERS / (source.stem + ".webp")
            image.save(target, "WEBP", quality=90, method=6)
            processed.append((source.name, target, image.size))

    tiles = []
    for _, target, _ in processed:
        with Image.open(target) as original:
            image = original.copy()
            image.thumbnail((260, 260), Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (290, 315), "white")
            tile.paste(image, ((290 - image.width) // 2, 10))
            ImageDraw.Draw(tile).text((10, 280), target.stem, fill="#172d39")
            tiles.append(tile)
    columns = 3
    rows = (len(tiles) + columns - 1) // columns
    contact_sheet = Image.new("RGB", (columns * 290, rows * 315), "#f2f6f7")
    for index, tile in enumerate(tiles):
        contact_sheet.paste(tile, ((index % columns) * 290, (index // columns) * 315))
    contact_sheet.save(temporary_path / "cover-contact-sheet.jpg", quality=92)
    shutil.copy2(temporary_path / "cover-contact-sheet.jpg", ROOT / "tmp-cover-contact-sheet.jpg")

subprocess.run([FFMPEG, "-y", "-i", str(VIDEO_SOURCE), "-map", "0:v:0", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(VIDEO_TARGET)], check=True)
for source, target, size in processed:
    print(f"{source} -> {target.name}: {size[0]}x{size[1]}")
print(f"Prepared {len(processed)} cover images and converted {VIDEO_TARGET.name}.")