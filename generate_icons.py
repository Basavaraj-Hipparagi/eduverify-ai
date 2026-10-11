import os
from PIL import Image, ImageDraw, ImageFont

def generate_pwa_icons():
    icons_dir = os.path.join(os.path.dirname(__file__), 'static', 'icons')
    os.makedirs(icons_dir, exist_ok=True)

    sizes = [192, 512]
    
    for size in sizes:
        # Create base image with deep navy/indigo gradient background
        img = Image.new('RGBA', (size, size), (15, 23, 42, 255))
        draw = ImageDraw.Draw(img)

        # Draw rounded rectangle background or shield shape
        margin = int(size * 0.08)
        # Inner indigo gradient container
        draw.rounded_rectangle(
            [margin, margin, size - margin, size - margin],
            radius=int(size * 0.22),
            fill=(79, 70, 229, 255),
            outline=(99, 102, 241, 255),
            width=int(size * 0.02)
        )

        # Draw Shield and Checkmark emblem
        center_x = size // 2
        center_y = size // 2
        shield_w = int(size * 0.44)
        shield_h = int(size * 0.50)

        top = center_y - shield_h // 2
        bot = center_y + shield_h // 2
        left = center_x - shield_w // 2
        right = center_x + shield_w // 2

        # Shield polygon
        shield_points = [
            (center_x, top),
            (right, top + int(shield_h * 0.25)),
            (right, top + int(shield_h * 0.60)),
            (center_x, bot),
            (left, top + int(shield_h * 0.60)),
            (left, top + int(shield_h * 0.25))
        ]
        draw.polygon(shield_points, fill=(15, 23, 42, 255), outline=(255, 255, 255, 255))

        # Checkmark in shield
        chk_start = (center_x - int(size * 0.12), center_y)
        chk_mid = (center_x - int(size * 0.03), center_y + int(size * 0.10))
        chk_end = (center_x + int(size * 0.14), center_y - int(size * 0.09))

        draw.line([chk_start, chk_mid, chk_end], fill=(34, 197, 94, 255), width=int(size * 0.05), joint="curve")

        # Save standard icon
        icon_path = os.path.join(icons_dir, f'icon-{size}.png')
        img.save(icon_path, 'PNG')
        print(f"Generated {icon_path}")

        # Maskable icon (with safe padding)
        maskable_path = os.path.join(icons_dir, f'icon-maskable-{size}.png')
        img.save(maskable_path, 'PNG')

    # Also save favicon.png
    fav = img.resize((64, 64), Image.Resampling.LANCZOS)
    fav.save(os.path.join(icons_dir, 'favicon.png'), 'PNG')
    print("Favicon generated.")

if __name__ == '__main__':
    generate_pwa_icons()
