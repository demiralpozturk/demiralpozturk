"""Özel repolar dahil tüm repoların dil dağılımını toplayıp assets/languages.svg üretir.

Kullanım:  python tools/diller.py      (gh CLI oturumu gerekir; repo adları SVG'ye yazılmaz)
"""
import json
import subprocess
from pathlib import Path

KULLANICI = "demiralpozturk"
ADET = 8
CIKTI = Path(__file__).resolve().parent.parent / "assets" / "languages.svg"

# GitHub Linguist renkleri
RENK = {
    "C#": "#178600", "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Python": "#3572A5",
    "HTML": "#e34c26", "CSS": "#663399", "PHP": "#4F5D95", "PowerShell": "#012456",
    "Shell": "#89e051", "TSQL": "#e38c00", "PLpgSQL": "#336790", "Dockerfile": "#384d54",
    "Batchfile": "#C1F12E", "Kotlin": "#A97BFF", "Java": "#b07219",
}


def gh(*args):
    return subprocess.run(["gh", *args], capture_output=True, text=True, encoding="utf-8", check=True).stdout


def topla():
    repolar = json.loads(gh("repo", "list", KULLANICI, "--limit", "200", "--json", "name,isFork"))
    toplam = {}
    for r in repolar:
        if r["isFork"]:
            continue
        for dil, bayt in json.loads(gh("api", f"repos/{KULLANICI}/{r['name']}/languages")).items():
            toplam[dil] = toplam.get(dil, 0) + bayt
    return toplam


def svg(toplam):
    s = sum(toplam.values())
    ust = sorted(toplam.items(), key=lambda x: -x[1])[:ADET]
    oran = [(d, 100 * b / s) for d, b in ust]
    W, BAR_X, BAR_W = 350, 25, 300
    satir = (len(oran) + 1) // 2
    H = 90 + satir * 24
    parcalar, x = [], BAR_X
    for i, (d, p) in enumerate(oran):
        w = BAR_W * p / sum(q for _, q in oran)
        parcalar.append(f'<rect x="{x:.2f}" y="0" width="{w:.2f}" height="8" fill="{RENK.get(d, "#8b949e")}"/>')
        x += w
    etiket = []
    for i, (d, p) in enumerate(oran):
        cx, cy = (25 if i % 2 == 0 else 185), 88 + (i // 2) * 24
        etiket.append(
            f'<circle cx="{cx + 5}" cy="{cy - 4}" r="5" fill="{RENK.get(d, "#8b949e")}"/>'
            f'<text x="{cx + 16}" y="{cy}" class="t">{d} {p:.1f}%</text>'
        )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Most used languages">
<style>.h{{font:600 18px 'Segoe UI',Ubuntu,sans-serif;fill:#58a6ff}}.t{{font:400 12px 'Segoe UI',Ubuntu,sans-serif;fill:#c9d1d9}}</style>
<rect width="{W}" height="{H}" rx="4.5" fill="#0d1117"/>
<text x="25" y="35" class="h">Most Used Languages</text>
<clipPath id="c"><rect x="{BAR_X}" y="55" width="{BAR_W}" height="8" rx="4"/></clipPath>
<g clip-path="url(#c)" transform="translate(0,55)">{"".join(parcalar)}</g>
{"".join(etiket)}
</svg>
'''


if __name__ == "__main__":
    t = topla()
    CIKTI.parent.mkdir(parents=True, exist_ok=True)
    CIKTI.write_text(svg(t), encoding="utf-8")
    print(f"yazıldı: {CIKTI}")
