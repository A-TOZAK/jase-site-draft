#!/usr/bin/env python3
"""トップ（index.html）にある共通の部品を、ほかのページへ写す道具。
部品は <!-- part:名前 --> と <!-- /part:名前 --> ではさんだ所で、次の4つ。
  bar（下書きの帯）、notice（重要なお知らせの帯）、header（ヘッダーとメニュー）、footer（フッター）
ヘッダーとフッターは、まず index.html で直してから、これを動かす。
メニューでは、開いているページのリンクに aria-current="page" をつける。
使い方：python3 tools/parts.py           … 写す
        python3 tools/parts.py --check   … 写し忘れがないかだけ確かめる（直さない）
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = ["bar", "notice", "header", "footer"]
# 記事のページでは、メニューの「お知らせ」を開いている扱いにする
CURRENT = {"news-article.html": "news.html"}


def pattern(name):
    return re.compile(r"<!-- part:%s -->.*?<!-- /part:%s -->" % (name, name), re.S)


def mark(block, page):
    block = block.replace(' aria-current="page"', "")
    if page == "index.html":
        return block
    href = CURRENT.get(page, page)
    # ヘッダーの中の、そのページへのリンク（ロゴは index.html なので当たらない）
    return re.sub(r'(<a (?:class="[^"]*" )?href="%s")' % re.escape(href), r'\1 aria-current="page"', block)


def main():
    check = "--check" in sys.argv
    src = (ROOT / "index.html").read_text(encoding="utf-8")
    blocks = {}
    for name in PARTS:
        m = pattern(name).search(src)
        if not m:
            raise SystemExit(f"index.html に part:{name} がない")
        blocks[name] = m.group(0)

    pages = sorted(p for p in ROOT.glob("*.html"))
    bad = 0
    for p in pages:
        s = p.read_text(encoding="utf-8")
        new = s
        for name in PARTS:
            if not pattern(name).search(new):
                print(f"✗ {p.name}: part:{name} の印がない")
                bad += 1
                continue
            block = mark(blocks[name], p.name) if name == "header" else blocks[name]
            new = pattern(name).sub(lambda _m: block, new, count=1)
        if new != s:
            if check:
                print(f"✗ {p.name}: 部品が index.html と違う")
                bad += 1
            else:
                p.write_text(new, encoding="utf-8")
                print(f"写した {p.name}")
    if check:
        print("✓ すべてのページの部品が index.html とそろっている" if not bad else f"そろっていない所 {bad}件")
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
