"""Encrypt local gallery photos; public builds reuse the encrypted bundle."""
from base64 import b64decode, b64encode
from pathlib import Path
import json
import os

ROOT = Path(__file__).resolve().parents[1]
PHOTO_DIRECTORY = ROOT / ".private" / "gallery-photos"
PASSWORD_FILE = ROOT / ".private" / "gallery-photo-password.txt"
BUNDLE = ROOT / "site" / "media" / "photos" / "protected.json"
ITERATIONS = 600_000
ASSOCIATED_DATA = b"kenta-watanabe/gallery-photos/v1"


def build_protected_photos():
    # CI never needs the password, original photos, or encryption dependencies.
    if not PASSWORD_FILE.is_file():
        if not BUNDLE.is_file():
            raise FileNotFoundError("Prepare the encrypted photo bundle locally first.")
        return

    from cryptography.exceptions import InvalidTag
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from PIL import Image

    password = PASSWORD_FILE.read_text(encoding="utf-8").rstrip("\r\n").encode("utf-8")
    if not password:
        raise ValueError("The gallery password must not be empty.")
    manifest = json.loads((ROOT / "content" / "photos.json").read_text(encoding="utf-8"))
    photos = []
    for item in manifest:
        source = PHOTO_DIRECTORY / (item["stem"] + ".webp")
        with Image.open(source) as image:
            width, height = image.size
        photos.append({
            "date": item["date"], "captions": item["captions"],
            "width": width, "height": height,
            "image": b64encode(source.read_bytes()).decode("ascii"),
        })
    plaintext = json.dumps({"photos": photos}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")

    def cipher(salt, iterations):
        key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=iterations).derive(password)
        return AESGCM(key)

    if BUNDLE.is_file():
        existing = json.loads(BUNDLE.read_text(encoding="utf-8"))
        try:
            previous = cipher(b64decode(existing["salt"]), existing["iterations"]).decrypt(
                b64decode(existing["iv"]), b64decode(existing["ciphertext"]), ASSOCIATED_DATA,
            )
            if previous == plaintext and existing["iterations"] == ITERATIONS:
                return
        except InvalidTag:
            pass  # A password change requires fresh ciphertext and random parameters.

    salt, iv = os.urandom(16), os.urandom(12)
    ciphertext = cipher(salt, ITERATIONS).encrypt(iv, plaintext, ASSOCIATED_DATA)
    bundle = {
        "version": 1, "algorithm": "AES-GCM", "kdf": "PBKDF2", "hash": "SHA-256",
        "iterations": ITERATIONS, "salt": b64encode(salt).decode("ascii"),
        "iv": b64encode(iv).decode("ascii"), "ciphertext": b64encode(ciphertext).decode("ascii"),
    }
    BUNDLE.parent.mkdir(parents=True, exist_ok=True)
    BUNDLE.write_text(json.dumps(bundle, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"Encrypted {len(photos)} gallery photos.")


if __name__ == "__main__":
    build_protected_photos()
