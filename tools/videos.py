#!/usr/bin/env python3
"""学会のYouTubeチャンネルの動画を、トップと「教材と動画」のページに並べる道具。
YouTube の公開フィード（新しい15本）を読み、data/videos.json の題名と種類で表に出す。
題名が data/videos.json にない新しい動画は、YouTube の題名のまま出して、ここで知らせる。
  （人のお名前が題名に入っていたら、data/videos.json に題名を足して、もう一度動かす）
書きかえる所は、ページの中の次の印ではさんだ所だけ。
  index.html   … <!-- videos:slide --> カルーセルの3枚目、<!-- videos:top --> 動画と対談の3本
  library.html … <!-- videos:side --> ページの頭の右の、新しい3本のスライド
                 <!-- videos:library --> ウェビナーと学術集会の講演の一覧
使い方：python3 tools/videos.py
"""
import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "videos.json"
CACHE = ROOT / "data" / "videos-feed.json"
CUR = ' aria-current="true"'
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}


def fetch(channel_id):
    """フィードを読む。読めないときは、前に読んだ控えを使う"""
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            root = ET.fromstring(r.read())
        items = [{"id": e.find("yt:videoId", NS).text,
                  "title": e.find("a:title", NS).text,
                  "date": e.find("a:published", NS).text[:10]}
                 for e in root.findall("a:entry", NS)]
        CACHE.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        return items
    except Exception as err:  # 回線がないときなど
        print(f"フィードを読めなかったので、控えを使います（{err}）")
        return json.loads(CACHE.read_text(encoding="utf-8"))


def card(v, size="mqdefault"):
    e = html.escape
    return (f'<a class="v-card" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener">'
            f'<div class="th"><img src="https://i.ytimg.com/vi/{v["id"]}/{size}.jpg" alt="" loading="lazy" width="320" height="180"><small>YouTube</small></div>'
            f'<span class="v-kind">{e(v["kind"])}</span><p>{e(v["title"])}</p>'
            f'<time datetime="{v["date"]}">{v["date"].replace("-", ".")}</time></a>')


def put(path, name, body):
    s = path.read_text(encoding="utf-8")
    pat = re.compile(r"(<!-- videos:%s -->\n).*?(<!-- /videos:%s -->)" % (name, name), re.S)
    if not pat.search(s):
        raise SystemExit(f"{path.name} に videos:{name} の印がない")
    path.write_text(pat.sub(lambda m: m.group(1) + body + "\n" + m.group(2), s, count=1), encoding="utf-8")


def main():
    conf = json.loads(DATA.read_text(encoding="utf-8"))
    videos, new = [], []
    for it in fetch(conf["channel_id"]):
        t = conf["titles"].get(it["id"])
        if not t:
            new.append(it)
            t = {"kind": "ウェビナー" if "ebinar" in it["title"].lower() else "動画", "title": it["title"]}
        videos.append({**it, **t})
    videos.sort(key=lambda v: v["date"], reverse=True)

    top = videos[0]
    e = html.escape
    slide = (f'<article class="slide s3" aria-roledescription="slide" aria-label="3枚目（全3枚）">\n'
             f'<div class="bg"><img src="https://i.ytimg.com/vi/{top["id"]}/hqdefault.jpg" alt=""><div class="play"></div></div>\n'
             f'<p class="kind">動画 VIDEOS　いちばん新しい動画</p>\n'
             f'<p class="ja v-title">{e(top["title"])}</p>\n'
             f'<p class="meta">学会のYouTubeチャンネル　{top["date"].replace("-", ".")}</p>\n'
             f'<a class="go" href="library.html#videos">動画の一覧へ</a>\n'
             f'</article>')
    put(ROOT / "index.html", "slide", slide)
    put(ROOT / "index.html", "top", "\n".join(card(v) for v in videos[:3]))

    side = []
    for k, v in enumerate(videos[:3]):
        side.append(f'<article class="slide s3" aria-roledescription="slide" aria-label="{k+1}枚目（全3枚）">\n'
                    f'<div class="bg"><img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt=""></div>\n'
                    f'<p class="kind">NEW VIDEO　{e(v["kind"])}</p>\n'
                    f'<p class="ja v-title">{e(v["title"])}</p>\n'
                    f'<p class="meta">{v["date"].replace("-", ".")}</p>\n'
                    f'<a class="go" href="https://www.youtube.com/watch?v={v["id"]}" target="_blank" rel="noopener">YouTubeで見る</a>\n'
                    f'</article>')
    ui = ('<div class="dots" role="tablist">' + "".join(
        f'<button aria-label="{k+1}枚目"{CUR if k == 0 else ""}></button>' for k in range(len(side))) + '</div>\n'
          '<div class="car-ui"><button class="prev" aria-label="前へ">‹</button><button class="pause" aria-label="自動の切りかえを止める">Ⅱ</button><button class="next" aria-label="次へ">›</button></div>')
    put(ROOT / "library.html", "side",
        '<div class="car side" aria-roledescription="carousel" aria-label="新しい動画">\n<div class="track">\n'
        + "\n".join(side) + '\n</div>\n' + ui + '\n</div>')

    groups = []
    for kind, label in (("ウェビナー", "JASE ウェビナー"), ("学術集会", "学術集会の講演"), ("動画", "そのほかの動画")):
        vs = [v for v in videos if v["kind"] == kind]
        if vs:
            groups.append(f'<h3 class="v-group">{label}<small>{len(vs)}本</small></h3>\n'
                          f'<div class="v-grid lib">\n' + "\n".join(card(v) for v in vs) + "\n</div>")
    put(ROOT / "library.html", "library", "\n".join(groups))

    print(f"動画 {len(videos)}本を並べました（トップに3本、教材と動画に全部）")
    for it in new:
        print(f"⚠ 題名を data/videos.json に足してください：{it['id']}　{it['title']}")
    if new:
        sys.exit(2)


if __name__ == "__main__":
    main()
