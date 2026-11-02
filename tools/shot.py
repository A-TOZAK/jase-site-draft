#!/usr/bin/env python3
"""直したあとに画面を焼いて確かめる道具。
ページごとに、パソコン（1440px）とスマホ（390px）の2枚を _shots/ に書き出す。_shots/ は git に入れない。
使い方：python3 tools/shot.py                    … すべてのページを焼く
        python3 tools/shot.py summit join       … 名前を挙げたページだけ焼く（.html は省いてよい）
        python3 tools/shot.py --memo index      … 気になる所メモを開いた状態で焼く
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_shots"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def trim(png):
    """下に余った背景の行を切る"""
    im = Image.open(png).convert("RGB")
    w, h = im.size
    px = im.load()
    bg = px[w // 2, h - 1]
    y = h - 1
    while y > 0 and all(px[x, y] == bg for x in range(0, w, 7)):
        y -= 1
    im.crop((0, 0, w, min(h, y + 2))).save(png)


def shoot(url, png, width, height):
    png.unlink(missing_ok=True)
    subprocess.run([CHROME, "--headless=new", "--hide-scrollbars", "--disable-gpu",
                    "--allow-file-access-from-files", "--virtual-time-budget=3000",
                    f"--window-size={width},{height}", f"--screenshot={png}", url],
                   capture_output=True)
    if not png.exists():
        raise SystemExit(f"焼けなかった: {png}")


def one(page, memo):
    url = (ROOT / page).as_uri() + ("?memo" if memo else "")
    stem = page.removesuffix(".html") + ("_メモ" if memo else "")

    pc = OUT / f"{stem}_パソコン.png"
    shoot(url, pc, 1440, 7000)
    trim(pc)

    # Chromeのヘッドレスは窓を390pxまで狭められないので、390px幅のiframeに入れて焼く
    wrap = OUT / "_sp_wrap.html"
    wrap.write_text('<!doctype html><html><body style="margin:0;background:#fff">'
                    f'<iframe src="{url}" style="width:390px;height:12000px;border:0;display:block">'
                    '</iframe></body></html>', encoding="utf-8")
    sp = OUT / f"{stem}_スマホ.png"
    shoot(wrap.as_uri(), sp, 800, 12000)
    Image.open(sp).crop((0, 0, 390, 12000)).save(sp)
    trim(sp)
    for p in (pc, sp):
        w, h = Image.open(p).size
        print(f"焼いた {p.name} {w}x{h}")


def main():
    OUT.mkdir(exist_ok=True)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    memo = "--memo" in sys.argv
    pages = [a if a.endswith(".html") else a + ".html" for a in args] or sorted(p.name for p in ROOT.glob("*.html"))
    for page in pages:
        if not (ROOT / page).exists():
            raise SystemExit(f"ページがない: {page}")
        one(page, memo)


if __name__ == "__main__":
    main()
