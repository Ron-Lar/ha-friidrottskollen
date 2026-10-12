"""Tolkar Friidrottskollen och TV-tablån på friidrott.se.

Ren Python utan Home Assistant-beroenden, så att den går att testa fristående.
"""
from __future__ import annotations

import html as _html
import re

MAN = {
    "januari": 1, "februari": 2, "mars": 3, "april": 4, "maj": 5, "juni": 6,
    "juli": 7, "augusti": 8, "september": 9, "oktober": 10, "november": 11, "december": 12,
}

# Rubriker och tabellrader i den ordning de står på sidan
TOKEN = re.compile(r"<h([1-6])[^>]*>(.*?)</h\1>|<tr[^>]*>(.*?)</tr>", re.S | re.I)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)
HREF = re.compile(r'href="([^"]+)"', re.I)

STOPP = {
    "diamond", "league", "games", "grand", "prix", "folksam", "memorial", "meeting",
    "continental", "tour", "international", "internationales", "wanda", "med", "och",
    "the", "gala", "galan",
}


def rentext(fragment: str) -> str:
    s = re.sub(r"<br\s*/?>", ", ", fragment, flags=re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = _html.unescape(s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*/\s*", "/", s)
    return s.strip(" ,")


def datumspann(text: str, ar: int | None, man: int | None) -> tuple[str, str] | None:
    tal = [int(x) for x in re.findall(r"\d{1,2}", text)]
    if not tal or not ar or not man:
        return None
    d1 = tal[0]
    d2 = tal[-1] if len(tal) > 1 else d1
    ar2, man2 = ar, man
    if d2 < d1:
        man2 += 1
        if man2 > 12:
            man2, ar2 = 1, ar2 + 1
    return f"{ar}-{man:02d}-{d1:02d}", f"{ar2}-{man2:02d}-{d2:02d}"


def _plats_ur_namn(namn: str) -> str | None:
    delar = [re.sub(r"\(.*?\)", "", d).strip() for d in namn.split(",")]
    delar = [d for d in delar if d]
    if len(delar) < 2:
        return None
    for d in delar[1:]:
        if not re.search(r"diamond league|continental tour|grand prix", d, re.I):
            return d
    return delar[0]


def parse_kollen(page: str, atlet: str) -> list[dict]:
    """Alla tävlingar där atleten står som anmäld, äldre som kommande."""
    ar = man = None
    ut: dict[str, dict] = {}
    for m in TOKEN.finditer(page):
        if m.group(2) is not None:
            rubrik = rentext(m.group(2)).lower()
            y = re.search(r"\b(20\d\d)\b", rubrik)
            if y:
                ar, man = int(y.group(1)), None
            if rubrik in MAN:
                man = MAN[rubrik]
            continue

        rad = m.group(3)
        celler = CELL.findall(rad)
        if len(celler) < 3:
            continue
        txt = [rentext(c) for c in celler]
        if not any(atlet in t for t in txt):
            continue
        spann = datumspann(txt[0], ar, man)
        if not spann:
            continue

        namn = txt[1]
        if len(celler) >= 5 and atlet not in txt[2]:
            plats = txt[2]          # äldre tabeller har egen platskolumn
        else:
            plats = _plats_ur_namn(namn)
        href = HREF.search(rad)
        ut[spann[0] + namn] = {
            "datum": spann[0],
            "slut": spann[1],
            "namn": namn,
            "plats": plats,
            "tid": None,
            "tv": None,
            "tvLank": None,
            "lank": _html.unescape(href.group(1)) if href else None,
        }
    return sorted(ut.values(), key=lambda t: t["datum"])


def parse_tv(page: str) -> list[dict]:
    """Alla sändningar i TV-tablån."""
    ar = man = None
    rader: list[dict] = []
    for m in TOKEN.finditer(page):
        if m.group(2) is not None:
            y = re.fullmatch(r"(20\d\d)", rentext(m.group(2)))
            if y:
                ar, man = int(y.group(1)), None
            continue

        raa = CELL.findall(m.group(3))
        txt = [rentext(c) for c in raa]
        if not txt:
            continue
        forsta = txt[0]
        if re.fullmatch(r"20\d\d", forsta):
            ar, man = int(forsta), None
            continue
        if forsta.lower() in MAN:
            man = MAN[forsta.lower()]
            continue
        if not re.match(r"\d", forsta) or len(txt) < 3:
            continue
        spann = datumspann(forsta, ar, man)
        if not spann:
            continue

        if len(txt) >= 5:
            tavling, kanal, tid, kanal_idx = f"{txt[1]}, {txt[2]}", txt[3], txt[4], 3
        else:
            tavling, kanal, tid, kanal_idx = txt[1], txt[2], (txt[3] if len(txt) > 3 else ""), 2
        if len(tid) > 40:
            tid = ", ".join(re.findall(r"\d{1,2}[.:]\d{2}", tid))
        href = HREF.search(raa[kanal_idx])
        rader.append({
            "start": spann[0],
            "slut": spann[1],
            "tavling": tavling,
            "kanal": kanal,
            "tid": tid,
            "lank": _html.unescape(href.group(1)) if href else None,
        })
    return rader


def _ord(s: str) -> set[str]:
    s = re.sub(r"\(.*?\)", " ", s.lower())
    return {w for w in re.split(r"[^a-zåäöéüæø]+", s) if len(w) > 2 and w not in STOPP}


def match_tv(tavlingar: list[dict], rader: list[dict]) -> None:
    """Fyller i tv, tid och tvLank: samma datum + gemensamma ord i namnet."""
    for t in tavlingar:
        tw = _ord(f"{t['namn']} {t['plats'] or ''}")
        dl = bool(re.search(r"diamond league", t["namn"], re.I))
        poang = []
        for r in rader:
            if r["start"] > t["slut"] or r["slut"] < t["datum"]:
                continue
            p = len(tw & _ord(r["tavling"])) * 2
            if dl and re.search(r"diamond league", r["tavling"], re.I):
                p += 1
            if p:
                poang.append((p, r))
        if not poang:
            continue
        bast = max(p for p, _ in poang)
        valda = sorted((r for p, r in poang if p == bast), key=lambda r: r["start"])

        kanaler = list(dict.fromkeys(r["kanal"] for r in valda if r["kanal"]))
        t["tv"] = " / ".join(kanaler) or None
        t["tvLank"] = next((r["lank"] for r in valda if r["lank"]), None)
        flera = len({r["start"] for r in valda}) > 1
        tider = []
        for r in valda:
            prefix = f"{int(r['start'][8:])}/{int(r['start'][5:7])} " if flera else ""
            s = (prefix + r["tid"]).strip()
            if re.search(r"\d", s):
                tider.append(s)
        t["tid"] = ", ".join(tider) or None
