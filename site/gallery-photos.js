(() => {
  "use strict";
  const section = document.getElementById("photos");
  const form = document.getElementById("photo-password-form");
  if (!section || !form) return;

  const password = document.getElementById("photo-password");
  const submit = form.querySelector("button");
  const status = document.getElementById("photo-status");
  const gallery = document.getElementById("photo-gallery");
  const lock = document.getElementById("photo-lock");
  const language = document.documentElement.lang === "ja" ? "ja" : "en";
  const messages = language === "ja" ? {
    loading: "写真を開いています…",
    wrong: "パスワードが違います。大文字・小文字を確認してください。",
    network: "写真を読み込めませんでした。時間をおいて再度お試しください。",
    unavailable: "対応するブラウザで、HTTPSのページを開いてください。",
    opened: "写真を表示しました。",
    locked: "写真を閉じました。",
  } : {
    loading: "Opening photos…",
    wrong: "Incorrect password. Please check uppercase and lowercase letters.",
    network: "Could not load the photos. Please try again later.",
    unavailable: "Please open this page over HTTPS in a supported browser.",
    opened: "Photos are now visible.",
    locked: "Photos are locked.",
  };
  const encoder = new TextEncoder();
  const decode = value => Uint8Array.from(atob(value), character => character.charCodeAt(0));
  const imageUrls = [];
  let bundle;

  function clearPhotos() {
    gallery.replaceChildren();
    for (const url of imageUrls) URL.revokeObjectURL(url);
    imageUrls.length = 0;
    gallery.hidden = true;
  }

  function renderPhotos(photos) {
    clearPhotos();
    const cards = document.createDocumentFragment();
    for (const photo of photos) {
      const card = document.createElement("article");
      card.className = "photo-card";
      const frame = document.createElement("div");
      frame.className = "photo-image-frame";
      const image = document.createElement("img");
      const url = URL.createObjectURL(new Blob([decode(photo.image)], { type: "image/webp" }));
      imageUrls.push(url);
      image.src = url;
      image.alt = photo.captions[language];
      image.width = photo.width;
      image.height = photo.height;
      image.loading = "lazy";
      frame.append(image);
      const copy = document.createElement("div");
      copy.className = "photo-card-copy";
      const date = document.createElement("p");
      date.className = "eyebrow";
      date.textContent = photo.date;
      const caption = document.createElement("h3");
      caption.textContent = photo.captions[language];
      copy.append(date, caption);
      card.append(frame, copy);
      cards.append(card);
    }
    gallery.append(cards);
    gallery.hidden = false;
  }

  form.addEventListener("submit", async event => {
    event.preventDefault();
    if (submit.disabled) return;
    if (!globalThis.crypto?.subtle) {
      status.textContent = messages.unavailable;
      return;
    }
    submit.disabled = true;
    password.disabled = true;
    password.removeAttribute("aria-invalid");
    status.textContent = messages.loading;
    try {
      if (!bundle) {
        const response = await fetch(form.dataset.photoBundle, { cache: "no-cache" });
        if (!response.ok) throw new Error("Photo fetch failed");
        const fetched = await response.json();
        if (fetched.version !== 1 || fetched.algorithm !== "AES-GCM" || fetched.kdf !== "PBKDF2"
          || fetched.hash !== "SHA-256" || fetched.iterations !== 600000) {
          throw new Error("Unsupported photo bundle");
        }
        bundle = fetched;
      }
      // Preserve the exact password: no trimming or case conversion.
      const material = await crypto.subtle.importKey("raw", encoder.encode(password.value), "PBKDF2", false, ["deriveKey"]);
      const key = await crypto.subtle.deriveKey({
        name: "PBKDF2", salt: decode(bundle.salt), iterations: bundle.iterations, hash: "SHA-256",
      }, material, { name: "AES-GCM", length: 256 }, false, ["decrypt"]);
      let plaintext;
      try {
        plaintext = await crypto.subtle.decrypt({
          name: "AES-GCM", iv: decode(bundle.iv),
          additionalData: encoder.encode("kenta-watanabe/gallery-photos/v1"), tagLength: 128,
        }, key, decode(bundle.ciphertext));
      } catch (error) {
        if (error.name !== "OperationError") throw error;
        password.setAttribute("aria-invalid", "true");
        status.textContent = messages.wrong;
        return;
      }
      renderPhotos(JSON.parse(new TextDecoder().decode(plaintext)).photos);
      password.value = "";
      form.hidden = true;
      lock.hidden = false;
      status.textContent = messages.opened;
      lock.focus();
    } catch {
      clearPhotos();
      bundle = undefined;
      status.textContent = messages.network;
    } finally {
      submit.disabled = false;
      password.disabled = false;
      if (!form.hidden) password.focus();
    }
  });

  lock.addEventListener("click", () => {
    clearPhotos();
    lock.hidden = true;
    form.hidden = false;
    status.textContent = messages.locked;
    password.focus();
  });
  if (globalThis.crypto?.subtle) {
    password.disabled = false;
    submit.disabled = false;
  } else {
    status.textContent = messages.unavailable;
  }
})();
