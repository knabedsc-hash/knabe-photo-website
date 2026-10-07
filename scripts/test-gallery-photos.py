"""Local checks of encryption, case sensitivity, and preservation of all photos."""
from base64 import b64decode
from io import BytesIO
import json
import unittest

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from PIL import Image
from gallery_photos import ROOT, BUNDLE, PASSWORD_FILE, PHOTO_DIRECTORY, ASSOCIATED_DATA


@unittest.skipUnless(PASSWORD_FILE.is_file(), "Requires the local, unpublished password file")
class GalleryEncryptionTest(unittest.TestCase):
    def setUp(self):
        self.bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
        self.password = PASSWORD_FILE.read_text(encoding="utf-8").rstrip("\r\n")

    def decrypt(self, password, ciphertext=None):
        key = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=b64decode(self.bundle["salt"]),
            iterations=self.bundle["iterations"],
        ).derive(password.encode("utf-8"))
        return AESGCM(key).decrypt(b64decode(self.bundle["iv"]),
            ciphertext if ciphertext is not None else b64decode(self.bundle["ciphertext"]), ASSOCIATED_DATA)

    def test_all_original_photos_and_bilingual_captions(self):
        photos = json.loads(self.decrypt(self.password))["photos"]
        manifest = json.loads((ROOT / "content" / "photos.json").read_text(encoding="utf-8"))
        self.assertEqual(len(photos), len(manifest))
        self.assertEqual(len(photos), 14)
        for photo, original in zip(photos, manifest):
            image_bytes = b64decode(photo["image"])
            self.assertEqual(image_bytes, (PHOTO_DIRECTORY / (original["stem"] + ".webp")).read_bytes())
            self.assertEqual(photo["captions"], original["captions"])
            self.assertEqual(photo["date"], original["date"])
            with Image.open(BytesIO(image_bytes)) as image:
                self.assertEqual(image.size, (photo["width"], photo["height"]))
                self.assertEqual(image.format, "WEBP")

    def test_case_changed_password_fails(self):
        self.assertNotEqual(self.password, self.password.swapcase())
        with self.assertRaises(InvalidTag):
            self.decrypt(self.password.swapcase())

    def test_extra_whitespace_fails(self):
        with self.assertRaises(InvalidTag):
            self.decrypt(self.password + " ")

    def test_modified_ciphertext_fails(self):
        modified = bytearray(b64decode(self.bundle["ciphertext"]))
        modified[0] ^= 1
        with self.assertRaises(InvalidTag):
            self.decrypt(self.password, bytes(modified))


if __name__ == "__main__":
    unittest.main()
