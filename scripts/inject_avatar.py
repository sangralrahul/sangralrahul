"""Embed the GitHub profile picture into assets/banner-v6.svg.

The banner is an SVG loaded as an <img>, so it cannot reference the avatar by URL;
the picture has to live inside the file. This script downloads the current avatar
and writes it between the <!--AVATAR--> markers. Safe to run repeatedly.

Usage: python3 scripts/inject_avatar.py <github-username> [path-to-local-image]
"""
import base64, io, pathlib, re, sys, urllib.request

owner = sys.argv[1] if len(sys.argv) > 1 else "sangralrahul"
svg_path = pathlib.Path(__file__).resolve().parent.parent / "assets" / "banner-v6.svg"

if len(sys.argv) > 2:
    data = pathlib.Path(sys.argv[2]).read_bytes()
else:
    req = urllib.request.Request(f"https://github.com/{owner}.png?size=240", headers={"User-Agent": "profile-readme-banner"})
    data = urllib.request.urlopen(req, timeout=30).read()

# Keep the banner light: 200px progressive JPEG (~15 KB) instead of a raw PNG.
try:
    from PIL import Image
    im = Image.open(io.BytesIO(data)).convert("RGB")
    im.thumbnail((200, 200), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    data, mime = buf.getvalue(), "image/jpeg"
except ImportError:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        mime = "image/png"
    elif data[:2] == b"\xff\xd8":
        mime = "image/jpeg"
    else:
        sys.exit("Unrecognised image format; install Pillow")

uri = f"data:{mime};base64,{base64.b64encode(data).decode()}"
image = (f'<image x="64" y="104" width="172" height="172" clip-path="url(#avclip)" '
         f'preserveAspectRatio="xMidYMid slice" xlink:href="{uri}" href="{uri}"/>')

svg = svg_path.read_text(encoding="utf-8")
new = re.sub(r"<!--AVATAR-->.*?<!--/AVATAR-->", lambda _: f"<!--AVATAR-->{image}<!--/AVATAR-->", svg, flags=re.S)
if new == svg:
    print("Banner already up to date")
else:
    svg_path.write_text(new, encoding="utf-8")
    print(f"Avatar embedded ({mime}, {len(data)//1024} KB)")
