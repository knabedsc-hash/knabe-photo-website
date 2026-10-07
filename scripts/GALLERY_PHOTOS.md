# Password-protected gallery photos

The Japanese and English galleries decrypt the same AES-256-GCM bundle in the
browser. PBKDF2-SHA-256 derives the key from the exact password (600,000
iterations, a random 16-byte salt, and a random 12-byte GCM IV). The password and
unencrypted photo exports remain in the ignored `.private` directory. Neither
the password nor the key is stored in browser storage. Reloading locks the
photos again; the gallery also offers a lock button.

For local updates:

1. Keep the password in `.private/gallery-photo-password.txt` (one line).
2. Update `content/photos.json` and the source mapping in
   `scripts/prepare-photo-gallery.py` when adding photos.
3. Run `python scripts/prepare-photo-gallery.py` to resize the local originals
   into `.private/gallery-photos` and rebuild the encrypted bundle. This needs
   Pillow, cryptography, and the existing image-conversion tools.
4. Run `python scripts/build.py`, `python scripts/check.py`, and
   `python scripts/test-gallery-photos.py` before committing.

GitHub Actions builds reuse the checked-in encrypted bundle without requiring
the password or the encryption dependencies. Avoid putting plaintext photo
exports back under `site`.

This limits access to the current website's photo section, not to photos that
were previously published. Plaintext photos remain retrievable in older Git
commits and may already have been copied. Removing that history requires a
separate repository-history cleanup. Readers with the shared password can save
or redistribute decrypted photos. Browser decryption uses Web Crypto and needs
HTTPS or a trusted localhost context.
