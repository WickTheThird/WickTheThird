#!/usr/bin/env python3
"""Move Wick through the README dungeon and render its SVG board."""

from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "game" / "state.json"
SVG_PATH = ROOT / "assets" / "dungeon.svg"
README_PATH = ROOT / "README.md"

MAP = (
    "#################",
    "#...T.......F...#",
    "#.###.#####.###.#",
    "#...............#",
    "#.###.#...#.###.#",
    "#.....#...#.....#",
    "#.###.#...#.###.#",
    "#...G.......D...#",
    "#################",
)

DIRECTIONS = {
    "up": (0, -1),
    "down": (0, 1),
    "left": (-1, 0),
    "right": (1, 0),
}

PORTALS = {
    "T": {"name": "TRIBUTUM", "color": "#7dd3fc"},
    "F": {"name": "FINTREX", "color": "#f1b86a"},
    "G": {"name": "TAGLEDGERS", "color": "#b89bea"},
    "D": {"name": "DZEN INTERIORS", "color": "#8be0b0"},
}

TILE = 42
BOARD_X = 50
BOARD_Y = 105


def load_state() -> dict[str, int]:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if not all(isinstance(state.get(key), int) for key in ("x", "y", "moves")):
        raise ValueError("Invalid dungeon state")
    if MAP[state["y"]][state["x"]] == "#":
        raise ValueError("Wick cannot start inside a wall")
    return state


def save_state(state: dict[str, int]) -> None:
    STATE_PATH.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def move(state: dict[str, int], direction: str) -> str:
    if direction not in DIRECTIONS:
        raise ValueError("Direction must be up, down, left, or right")

    dx, dy = DIRECTIONS[direction]
    target_x = state["x"] + dx
    target_y = state["y"] + dy
    if MAP[target_y][target_x] == "#":
        return f"A wall blocks the way {direction}."

    state["x"] = target_x
    state["y"] = target_y
    state["moves"] += 1
    save_state(state)

    tile = MAP[target_y][target_x]
    if tile in PORTALS:
        return f"Wick found {PORTALS[tile]['name']}."
    return f"Wick moved {direction}."


def render(state: dict[str, int]) -> None:
    board_width = len(MAP[0]) * TILE
    board_height = len(MAP) * TILE
    current_tile = MAP[state["y"]][state["x"]]
    status = (
        f"FOUND: {PORTALS[current_tile]['name']} — LINK BELOW"
        if current_tile in PORTALS
        else "WICK IS SOMEWHERE IN THE DUNGEON"
    )

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620" role="img" aria-labelledby="title desc" shape-rendering="crispEdges">',
        '<title id="title">Wick wandering through a collaborative dungeon</title>',
        '<desc id="desc">Use the controls below the image to move Wick through the maze and discover four client-work portals.</desc>',
        "<defs>",
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0d1018"/><stop offset="1" stop-color="#181421"/></linearGradient>',
        '<radialGradient id="fog" cx="48%" cy="48%" r="58%"><stop stop-color="#6f547f" stop-opacity=".11"/><stop offset="1" stop-color="#0d1018" stop-opacity="0"/></radialGradient>',
        '<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="1200" height="1" fill="#fff" opacity=".018"/></pattern>',
        "</defs>",
        "<style>",
        ".px{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}",
        ".portal{animation:pulse 2.6s steps(3,end) infinite;transform-origin:center}",
        ".wick{animation:bob 1.2s steps(2,end) infinite;transform-origin:center}",
        ".flame{animation:flame .7s steps(3,end) infinite;transform-origin:center bottom}",
        ".blink{animation:blink 1.4s steps(2,end) infinite}",
        "@keyframes pulse{50%{opacity:.45;transform:scale(.9)}}",
        "@keyframes bob{50%{transform:translateY(-3px)}}",
        "@keyframes flame{33%{transform:scale(.75,1.14) translateX(2px)}66%{transform:scale(1.08,.88) translateX(-2px)}}",
        "@keyframes blink{50%{opacity:.2}}",
        "@media(prefers-reduced-motion:reduce){*{animation-duration:.001ms!important;animation-iteration-count:1!important}}",
        "</style>",
        '<rect width="1200" height="620" rx="18" fill="url(#bg)"/>',
        '<rect width="1200" height="620" rx="18" fill="url(#fog)"/>',
        '<rect x="2" y="2" width="1196" height="616" rx="16" fill="none" stroke="#50465b" stroke-width="3"/>',
        '<text class="px" x="50" y="53" fill="#ece8ef" font-size="30" font-weight="700">nothing special.</text>',
        f'<text class="px" x="1150" y="51" text-anchor="end" fill="#625b6b" font-size="13">MOVE {state["moves"]:04d}</text>',
        f'<rect x="{BOARD_X - 10}" y="{BOARD_Y - 10}" width="{board_width + 20}" height="{board_height + 20}" fill="#080a10" stroke="#3b3542" stroke-width="3"/>',
    ]

    for y, row in enumerate(MAP):
        for x, tile in enumerate(row):
            px = BOARD_X + x * TILE
            py = BOARD_Y + y * TILE
            if tile == "#":
                shade = "#292430" if (x + y) % 2 else "#302a37"
                parts.append(
                    f'<rect x="{px}" y="{py}" width="{TILE}" height="{TILE}" fill="{shade}" stroke="#17141c" stroke-width="2"/>'
                )
                parts.append(
                    f'<path d="M{px + 5} {py + 12}h{TILE - 10}M{px + 5} {py + 31}h{TILE - 10}" stroke="#403847" stroke-width="2"/>'
                )
            else:
                shade = "#151722" if (x + y) % 2 else "#181a26"
                parts.append(
                    f'<rect x="{px}" y="{py}" width="{TILE}" height="{TILE}" fill="{shade}" stroke="#20222e"/>'
                )
                parts.append(f'<circle cx="{px + 9}" cy="{py + 11}" r="1" fill="#343440"/>')

            if tile in PORTALS:
                portal = PORTALS[tile]
                cx = px + TILE // 2
                cy = py + TILE // 2
                parts.extend(
                    [
                        f'<g class="portal" style="animation-delay:-{(x + y) % 3}.2s">',
                        f'<circle cx="{cx}" cy="{cy}" r="15" fill="none" stroke="{portal["color"]}" stroke-width="4"/>',
                        f'<circle cx="{cx}" cy="{cy}" r="8" fill="{portal["color"]}" opacity=".28"/>',
                        f'<path d="M{cx - 5} {cy}h10M{cx} {cy - 5}v10" stroke="{portal["color"]}" stroke-width="2"/>',
                        "</g>",
                    ]
                )

    # A few small wall torches make the map feel inhabited without turning it into a dashboard.
    for tx, ty in ((2, 2), (14, 2), (2, 6), (14, 6)):
        x = BOARD_X + tx * TILE + TILE // 2
        y = BOARD_Y + ty * TILE + TILE // 2
        parts.extend(
            [
                f'<rect x="{x - 2}" y="{y + 2}" width="4" height="14" fill="#6b4a37"/>',
                f'<g class="flame" transform="translate({x} {y})"><path d="M0 4c-9-8-5-17 1-24 8 10 8 17-1 24z" fill="#f2a85d"/><path d="M0 1c-4-4-2-9 1-13 4 5 3 9-1 13z" fill="#ffe69a"/></g>',
            ]
        )

    # Wick is intentionally a tiny, anonymous hooded sprite rather than a fake portrait.
    player_x = BOARD_X + state["x"] * TILE + TILE // 2
    player_y = BOARD_Y + state["y"] * TILE + TILE // 2
    parts.extend(
        [
            f'<g class="wick" transform="translate({player_x} {player_y})">',
            '<ellipse cx="0" cy="16" rx="14" ry="5" fill="#000" opacity=".35"/>',
            '<path d="M-12 15-9-7 0-16 9-7 12 15z" fill="#d8b65c"/>',
            '<rect x="-7" y="-7" width="14" height="12" fill="#17151b"/>',
            '<rect x="-5" y="-4" width="3" height="3" fill="#8be5ef"/>',
            '<rect x="2" y="-4" width="3" height="3" fill="#8be5ef"/>',
            '<path d="M-12 15h24l-4 6H-8z" fill="#96783f"/>',
            "</g>",
        ]
    )

    sidebar_x = 820
    parts.extend(
        [
            f'<text class="px" x="{sidebar_x}" y="128" fill="#827989" font-size="13">FOUR EXITS</text>',
            f'<text class="px" x="{sidebar_x}" y="161" fill="#cbc5ce" font-size="16">move Wick with the arrows below.</text>',
            f'<text class="px" x="{sidebar_x}" y="185" fill="#625b69" font-size="13">anyone with GitHub can take a step.</text>',
        ]
    )

    for index, portal in enumerate(PORTALS.values()):
        y = 238 + index * 58
        parts.extend(
            [
                f'<circle cx="{sidebar_x + 10}" cy="{y - 5}" r="8" fill="none" stroke="{portal["color"]}" stroke-width="3"/>',
                f'<text class="px" x="{sidebar_x + 34}" y="{y}" fill="#aaa3af" font-size="15">{html.escape(portal["name"])}</text>',
            ]
        )

    parts.extend(
        [
            f'<rect x="{sidebar_x}" y="478" width="330" height="48" fill="#11121b" stroke="#37323d"/>',
            f'<text class="px" x="{sidebar_x + 16}" y="508" fill="#d8b65c" font-size="13">{html.escape(status)}</text>',
            '<text class="px" x="50" y="570" fill="#77717c" font-size="13">“But, if you have nothing at all to create, then perhaps you create yourself.” — Carl Jung</text>',
            '<rect class="blink" x="50" y="590" width="8" height="8" fill="#d8b65c"/>',
            '<text class="px" x="67" y="598" fill="#504a54" font-size="11">waiting for somebody to move</text>',
            '<rect width="1200" height="620" rx="18" fill="url(#scan)" pointer-events="none"/>',
            "</svg>",
        ]
    )

    SVG_PATH.write_text("\n".join(parts) + "\n", encoding="utf-8")


def refresh_readme_cache(move_number: int) -> None:
    readme = README_PATH.read_text(encoding="utf-8")
    updated = re.sub(r"dungeon\.svg\?v=\d+", f"dungeon.svg?v={move_number}", readme)
    if updated == readme and f"dungeon.svg?v={move_number}" not in readme:
        raise ValueError("README dungeon image marker is missing")
    README_PATH.write_text(updated, encoding="utf-8")


def main() -> None:
    state = load_state()
    if len(sys.argv) == 2 and sys.argv[1] == "render":
        result = "Rendered the current dungeon."
    elif len(sys.argv) == 2 and sys.argv[1] == "move":
        title = os.environ.get("MOVE_TITLE", "")
        direction = title.removeprefix("[move] ").strip()
        result = move(state, direction)
    else:
        raise SystemExit("Usage: game.py render | game.py move")

    render(state)
    refresh_readme_cache(state["moves"])
    print(result)


if __name__ == "__main__":
    main()
