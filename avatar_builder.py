from PIL import Image, ImageEnhance, ImageFilter
import os

# === Avatar Asset Maps ===
base_map = {
    "Flame": "assets/avatars/base_flame.png",
    "Guardian": "assets/avatars/base_guardian.png",
    "Oracle": "assets/avatars/base_oracle.png"
}
halo_map = {
    "Gold": "assets/avatars/halo_gold.png",
    "Mint": "assets/avatars/halo_mint.png",
    "Blue": "assets/avatars/halo_blue.png"
}
aura_map = {
    "Gold": "assets/avatars/aura_gold.png",
    "Blue": "assets/avatars/aura_blue.png"
}
face_map = {
    "🙂": "assets/avatars/faces/smile.png"
}
accessory_path = "assets/avatars/accessory_star.png"

# === Load Image Helper ===
def load_img(path):
    try:
        return Image.open(path).convert("RGBA")
    except FileNotFoundError:
        print(f"[ERROR] Missing image: {path}")
        return Image.new("RGBA", (512, 512), (0, 0, 0, 0))

# === Build Composite Avatar ===
def build_avatar(base, halo, aura, accessory=False, face_emoji="🙂"):
    base_img = load_img(base_map.get(base, base_map["Flame"]))
    halo_img = load_img(halo_map.get(halo, halo_map["Gold"]))
    aura_img = load_img(aura_map[aura]) if aura and aura in aura_map else None
    accessory_img = load_img(accessory_path) if accessory else None
    face_img = load_img(face_map[face_emoji]) if face_emoji in face_map else None

    # Create glow backdrop
    glow = Image.new("RGBA", base_img.size, (255, 223, 0, 25)).filter(ImageFilter.GaussianBlur(radius=22))

    # Assemble layers
    composite = Image.new("RGBA", base_img.size)
    composite.paste(glow, (0, 0), glow)
    composite.paste(base_img, (0, 0), base_img)
    composite.paste(halo_img, (0, 0), halo_img)
    if aura_img:
        composite.paste(aura_img, (0, 0), aura_img)
    if accessory_img:
        composite.paste(accessory_img, (0, 0), accessory_img)
    if face_img:
        composite.paste(face_img, (0, 0), face_img)

    # Enhance brightness
    composite = ImageEnhance.Brightness(composite).enhance(1.15)
    return composite

# === Save Composite to File ===
def save_avatar_image(img, user_id="default"):
    path = f"assets/generated_avatars/avatar_{user_id}.png"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    return path

# === URL Generator for Display ===
def get_avatar_url(user_id="default"):
    return f"assets/generated_avatars/avatar_{user_id}.png"
