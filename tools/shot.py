#!/usr/bin/env python3
"""直したあとに画面を焼いて確かめる道具。
パソコン（1440px）とスマホ（390px）の2枚を _shots/ に書き出す。_shots/ は git に入れない。
使い方：python3 tools/shot.py          … index.html を焼く
        python3 tools/shot.py --memo   … 気になる所メモを開いた状態で焼く
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
                    "--allow-file-access-from-files",
                    f"--window-size={width},{height}", f"--screenshot={png}", url],
                   capture_output=True)
    if not png.exists():
        raise SystemExit(f"焼けなかった: {png}")


def main():
    OUT.mkdir(exist_ok=True)
    memo = "--memo" in sys.argv
    url = (ROOT / "index.html").as_uri() + ("?memo" if memo else "")
    tag = "_メモ" if memo else ""

    pc = OUT / f"パソコン{tag}.png"
    shoot(url, pc, 1440, 5200)
    trim(pc)

    # Chromeのヘッドレスは窓を390pxまで狭められないので、390px幅のiframeに入れて焼く
    wrap = OUT / "_sp_wrap.html"
    wrap.write_text('<!doctype html><html><body style="margin:0;background:#fff">'
                    f'<iframe src="{url}" style="width:390px;height:7000px;border:0;display:block">'
                    '</iframe></body></html>', encoding="utf-8")
    sp = OUT / f"スマホ{tag}.png"
    shoot(wrap.as_uri(), sp, 800, 7000)
    Image.open(sp).crop((0, 0, 390, 7000)).save(sp)
    trim(sp)
    for p in (pc, sp):
        w, h = Image.open(p).size
        print(f"焼いた {p.name} {w}x{h}")


if __name__ == "__main__":
    main()
