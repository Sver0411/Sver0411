#!/usr/bin/env python3
"""Generate a dependency-free pixel-style GitHub stats card."""

from __future__ import annotations

import html
import json
import os
from pathlib import Path
from urllib.request import Request, urlopen


USERNAME = "Sver0411"
API = "https://api.github.com"
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "github-stats.svg"


def github(path: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-card",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(Request(f"{API}{path}", headers=headers), timeout=20) as response:
        return json.load(response)


def main() -> None:
    user = github(f"/users/{USERNAME}")
    repos = github(f"/users/{USERNAME}/repos?per_page=100&sort=updated&type=owner")

    languages: dict[str, int] = {}
    stars = 0
    for repo in repos:
        if repo.get("fork"):
            continue
        stars += int(repo.get("stargazers_count", 0))
        try:
            for language, size in github(f"/repos/{USERNAME}/{repo['name']}/languages").items():
                languages[language] = languages.get(language, 0) + int(size)
        except Exception:
            # One archived or temporarily unavailable repo should not break the card.
            pass

    top = sorted(languages.items(), key=lambda item: item[1], reverse=True)[:4]
    total = sum(value for _, value in top) or 1
    palette = ["#59f6ff", "#a879ff", "#ff6bd6", "#ffd166"]
    bar_rows = []
    y = 188
    for index, (language, value) in enumerate(top):
        percent = round(value / total * 100)
        width = max(8, round(285 * value / total))
        color = palette[index]
        bar_rows.append(
            f'<text x="505" y="{y}" class="small">{html.escape(language)}</text>'
            f'<text x="815" y="{y}" class="small pct">{percent}%</text>'
            f'<rect x="505" y="{y + 10}" width="285" height="10" fill="#172b50"/>'
            f'<rect x="505" y="{y + 10}" width="{width}" height="10" fill="{color}"/>'
        )
        y += 43

    level = min(99, max(1, len(repos) * 2 + stars))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="390" viewBox="0 0 900 390">
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; }}
    .label {{ fill: #7897c9; font-size: 13px; letter-spacing: 2px; }}
    .value {{ fill: #f4f7ff; font-size: 27px; font-weight: 700; }}
    .small {{ fill: #c9d8f2; font-size: 14px; }}
    .pct {{ text-anchor: end; fill: #7897c9; }}
    .pixel {{ shape-rendering: crispEdges; }}
  </style>
  <rect width="900" height="390" rx="4" fill="#081426"/>
  <path d="M0 0H900V8H0zM0 382H900V390H0zM0 0H8V390H0zM892 0H900V390H892z" fill="#244c7c"/>
  <path d="M8 8H892V12H8zM8 378H892V382H8z" fill="#59f6ff" opacity=".55"/>
  <g opacity=".12" stroke="#59f6ff"><path d="M0 48H900M0 88H900M0 128H900M0 168H900M0 208H900M0 248H900M0 288H900M0 328H900M0 368H900"/></g>

  <text x="38" y="48" fill="#59f6ff" font-size="16" font-weight="700" letter-spacing="3">PLAYER DATA // LIVE</text>
  <circle cx="850" cy="42" r="6" fill="#66ff9a"/><text x="833" y="47" class="label" text-anchor="end">ONLINE</text>

  <g class="pixel" transform="translate(48 91)">
    <rect x="20" y="0" width="92" height="12" fill="#59f6ff"/>
    <rect x="8" y="12" width="116" height="12" fill="#59f6ff"/>
    <rect x="0" y="24" width="132" height="112" fill="#132c50"/>
    <rect x="12" y="36" width="108" height="76" fill="#09182d"/>
    <rect x="28" y="52" width="24" height="24" fill="#59f6ff"/>
    <rect x="80" y="52" width="24" height="24" fill="#a879ff"/>
    <rect x="40" y="88" width="52" height="8" fill="#ff6bd6"/>
    <rect x="20" y="136" width="92" height="12" fill="#244c7c"/>
    <rect x="36" y="148" width="60" height="12" fill="#172b50"/>
  </g>
  <text x="48" y="286" class="label">CALLSIGN</text>
  <text x="48" y="317" class="value">{html.escape(USERNAME)}</text>
  <text x="48" y="344" class="small">INDEPENDENT BUILDER</text>
  <text x="48" y="367" fill="#66ff9a" font-size="13">LV.{level:02d}  •  BUILD MODE</text>

  <path d="M232 82V354" stroke="#244c7c" stroke-width="2"/>
  <text x="268" y="112" class="label">PUBLIC REPOS</text>
  <text x="268" y="146" class="value">{int(user.get('public_repos', len(repos))):02d}</text>
  <text x="405" y="112" class="label">STARS</text>
  <text x="405" y="146" class="value">{stars:02d}</text>
  <text x="268" y="204" class="label">FOLLOWERS</text>
  <text x="268" y="238" class="value">{int(user.get('followers', 0)):02d}</text>
  <text x="380" y="204" class="label">FOLLOWING</text>
  <text x="380" y="238" class="value">{int(user.get('following', 0)):02d}</text>
  <rect x="268" y="278" width="174" height="50" fill="#102442" stroke="#244c7c" stroke-width="2"/>
  <text x="355" y="299" class="label" text-anchor="middle">STATUS</text>
  <text x="355" y="319" fill="#66ff9a" font-size="15" font-weight="700" text-anchor="middle">SHIPPING IDEAS</text>

  <path d="M470 82V354" stroke="#244c7c" stroke-width="2"/>
  <text x="505" y="112" class="label">LANGUAGE LOADOUT</text>
  {''.join(bar_rows)}
</svg>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
