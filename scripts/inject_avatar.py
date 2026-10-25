"""Embed the GitHub profile picture into assets/banner-v3.svg.

The banner is an SVG loaded as an <img>, so it cannot reference the avatar by URL;
the picture has to live inside the file. This script downloads the current avatar
and writes it between the <!--AVATAR--> markers. Safe to run repeatedly.

Usage: python3 scripts/inject_avatar.py <github-username> [path-to-local-image]
"""
import base64, pathlib, re, sys, urllib.request

owner = sys.argv[1] if len(sys.argv) > 1 else "sangralrahul"
svg_path = pathlib.Path(__file__).resolve().parent.parent / "assets" / "banner-v3.svg"

if len(sys.argv) > 2:
    data = pathlib.Path(sys.argv[2]).read_bytes()
else:
    req = urllib.request.Request(f"https://github.com/{owner}.png?size=400", headers={"User-Agent": "profile-readme-banner"})
    data = urllib.request.urlopen(req, timeout=30).read()

if data[:8] == b"\x89PNG\r\n\x1a\n":
    mime = "image/png"
elif data[:2] == b"\xff\xd8":
    mime = "image/jpeg"
elif data[:3] == b"GIF":
    mime = "image/gif"
elif data[8:12] == b"WEBP":
    mime = "image/webp"
else:
    sys.exit("Unrecognised image format")

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
