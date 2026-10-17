import os
from PIL import Image, ImageDraw

def generate_assets():
    # 1. Load source image and extract the logo with alpha anti-aliasing
    src_path = 'src/assets/icon.jpeg'
    im = Image.open(src_path).convert('RGB')
    w, h = im.size
    pixels = im.load()

    rgba = Image.new('RGBA', (w, h))
    rgba_pix = rgba.load()
    min_x, min_y, max_x, max_y = w, h, 0, 0

    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            diff = 254.0 - max(g, b)
            if diff <= 6:
                rgba_pix[x, y] = (255, 255, 255, 0)
            else:
                a = min(255, int((diff / (254.0 - 90.0)) * 255))
                rgba_pix[x, y] = (r, g, b, a)
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    logo = rgba.crop((min_x, min_y, max_x + 1, max_y + 1))
    lw, lh = logo.size
    print(f'Extracted logo size: {lw}x{lh}')

    res_dir = 'android/app/src/main/res'

    def get_scaled_logo(target_h):
        scale = target_h / float(lh)
        target_w = max(1, int(round(lw * scale)))
        return logo.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # 2. Mipmap Icons
    mipmaps = {
        'mipmap-mdpi': {'icon': 48, 'fg': 108},
        'mipmap-hdpi': {'icon': 72, 'fg': 162},
        'mipmap-xhdpi': {'icon': 96, 'fg': 216},
        'mipmap-xxhdpi': {'icon': 144, 'fg': 324},
        'mipmap-xxxhdpi': {'icon': 192, 'fg': 432},
    }

    for folder, sizes in mipmaps.items():
        fpath = os.path.join(res_dir, folder)
        os.makedirs(fpath, exist_ok=True)
        
        # Adaptive foreground (108dp canvas, safe zone 72dp)
        fg_size = sizes['fg']
        fg_canvas = Image.new('RGBA', (fg_size, fg_size), (0, 0, 0, 0))
        fg_logo_h = int(fg_size * 0.56)
        scaled_fg = get_scaled_logo(fg_logo_h)
        sw, sh = scaled_fg.size
        fg_canvas.paste(scaled_fg, ((fg_size - sw) // 2, (fg_size - sh) // 2), scaled_fg)
        fg_canvas.save(os.path.join(fpath, 'ic_launcher_foreground.png'))
        
        # Legacy Square / Squircle Icon
        icon_size = sizes['icon']
        legacy_canvas = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(legacy_canvas)
        radius = int(icon_size * 0.22)
        padding = max(1, int(icon_size * 0.03))
        draw.rounded_rectangle([padding, padding, icon_size - padding - 1, icon_size - padding - 1], radius=radius, fill=(255, 255, 255, 255))
        icon_logo_h = int(icon_size * 0.68)
        scaled_icon = get_scaled_logo(icon_logo_h)
        iw, ih = scaled_icon.size
        legacy_canvas.paste(scaled_icon, ((icon_size - iw) // 2, (icon_size - ih) // 2), scaled_icon)
        legacy_canvas.save(os.path.join(fpath, 'ic_launcher.png'))
        
        # Round Icon
        round_canvas = Image.new('RGBA', (icon_size, icon_size), (0, 0, 0, 0))
        rdraw = ImageDraw.Draw(round_canvas)
        r_pad = max(1, int(icon_size * 0.03))
        rdraw.ellipse([r_pad, r_pad, icon_size - r_pad - 1, icon_size - r_pad - 1], fill=(255, 255, 255, 255))
        round_logo_h = int(icon_size * 0.62)
        scaled_round = get_scaled_logo(round_logo_h)
        rw, rh = scaled_round.size
        round_canvas.paste(scaled_round, ((icon_size - rw) // 2, (icon_size - rh) // 2), scaled_round)
        round_canvas.save(os.path.join(fpath, 'ic_launcher_round.png'))

    # 3. Splash Screens
    splashes = {
        'drawable': (480, 320),
        'drawable-land-mdpi': (480, 320),
        'drawable-land-hdpi': (800, 480),
        'drawable-land-xhdpi': (1280, 720),
        'drawable-land-xxhdpi': (1600, 960),
        'drawable-land-xxxhdpi': (1920, 1280),
        'drawable-port-mdpi': (320, 480),
        'drawable-port-hdpi': (480, 800),
        'drawable-port-xhdpi': (720, 1280),
        'drawable-port-xxhdpi': (960, 1600),
        'drawable-port-xxxhdpi': (1280, 1920),
    }

    for folder, (sw, sh) in splashes.items():
        fpath = os.path.join(res_dir, folder)
        os.makedirs(fpath, exist_ok=True)
        splash_im = Image.new('RGB', (sw, sh), (255, 255, 255))
        min_dim = min(sw, sh)
        splash_logo_h = int(min_dim * 0.28) if sw < sh else int(min_dim * 0.35)
        scaled_splash = get_scaled_logo(splash_logo_h)
        lw_s, lh_s = scaled_splash.size
        splash_im.paste(scaled_splash, ((sw - lw_s) // 2, (sh - lh_s) // 2), scaled_splash)
        splash_im.save(os.path.join(fpath, 'splash.png'))

    # 4. Android 12+ Splash Icon
    splash_icon_canvas = Image.new('RGBA', (288, 288), (0, 0, 0, 0))
    splash_icon_h = 160
    scaled_splash_icon = get_scaled_logo(splash_icon_h)
    si_w, si_h = scaled_splash_icon.size
    splash_icon_canvas.paste(scaled_splash_icon, ((288 - si_w) // 2, (288 - si_h) // 2), scaled_splash_icon)
    splash_icon_canvas.save(os.path.join(res_dir, 'drawable', 'splash_icon.png'))

    print('All Android icons and splash screens successfully generated!')

if __name__ == '__main__':
    generate_assets()
