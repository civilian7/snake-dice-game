"""요즘판 보드를 통짜 그림 한 장으로 굽는다.

원본 판(board.webp)은 격자·칸 번호·뱀·고속도로가 전부 그림 안에 있는 한 장이다.
요즘판도 같은 구조로 만들려면 같은 것들이 한 장에 들어가야 하는데, 그것을 새로
그릴 필요는 없다 — 게임이 이미 그 전부를 정확히 렌더링하고 있으므로, 브라우저로
크게 그려 그대로 찍으면 된다. 좌표를 다시 잴 일도 없다.

  python tools/bake-board.py                 # board-modern.webp 를 만든다
  python tools/bake-board.py --scale 4       # 더 크게 (기본 3배)
  python tools/bake-board.py --keep-png      # 중간 png 도 남긴다

칸 삽화(art/NNN.webp)가 있으면 그것이 들어간 채로 구워진다. 삽화를 새로 만들거나
바꾼 뒤에는 이 스크립트를 다시 돌려야 그림에 반영된다.
"""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.html"
OUT_WEBP = ROOT / "board-modern.webp"
OUT_PNG = ROOT / "board-modern.png"

# 원본과 같은 종횡비(520x758)를 유지한다. scale 은 그 배수다.
BASE_W, BASE_H = 520, 758


def bake(scale: int, keep_png: bool, quality: int) -> None:
    from playwright.sync_api import sync_playwright

    if not INDEX.exists():
        sys.exit(f"index.html 을 찾을 수 없다: {INDEX}")

    width = BASE_W * scale
    height = BASE_H * scale

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        # deviceScaleFactor 로 키우면 CSS 픽셀 기준 레이아웃은 그대로 두고 해상도만 오른다.
        # 창을 키우는 것과 달리 반응형 분기를 건드리지 않아 데스크톱 배치가 유지된다.
        page = browser.new_page(
            viewport={"width": 900, "height": 1100},
            device_scale_factor=scale,
        )
        page.goto(INDEX.as_uri())
        page.wait_for_function("typeof setBoardMode === 'function'")

        # ★코드로 그린 요즘판을 강제한다.
        # 그러지 않으면 지난번에 구운 그림이 배경으로 깔린 채 그 위를 다시 찍어
        # 두 번째 굽기부터 그림이 겹쳐 쌓인다.
        force_retro = """() => {
          closeSetup(false);              // 새 게임 창을 걷는다
          modernBaked = false;            // 구운 그림을 쓰지 않는다
          setBoardMode('retro');          // 코드로 그린 요즘판
          // 말은 그림에 들어가면 안 된다.
          for (const el of document.querySelectorAll('.token')) el.style.display = 'none';
          document.body.style.background = 'transparent';
        }"""
        page.evaluate(force_retro)

        # 삽화 <img> 가 붙는 것을 기다린다 — 없으면 픽토그램인 채로 구워진다.
        page.wait_for_timeout(700)
        page.wait_for_function("[...document.images].every(i => i.complete)")

        # probeModernBoard() 가 뒤늦게 끝나 모드를 되돌렸을 수 있다. 찍기 직전에 다시 못박는다.
        page.evaluate(force_retro)
        mode = page.evaluate("document.getElementById('board').dataset.bg")
        if mode != "retro":
            browser.close()
            sys.exit(f"코드 렌더 모드로 고정하지 못했다 (data-bg={mode}). 구우면 그림이 겹친다.")

        board = page.locator("#board")
        board.screenshot(path=str(OUT_PNG), scale="device")

        n_art = page.evaluate("document.querySelectorAll('.pic.has-img').length")
        browser.close()

    from PIL import Image

    im = Image.open(OUT_PNG).convert("RGB")
    im = im.resize((width, height), Image.LANCZOS)
    im.save(OUT_WEBP, "WEBP", quality=quality, method=6)

    if not keep_png:
        OUT_PNG.unlink()

    kb = OUT_WEBP.stat().st_size / 1024
    print(f"{OUT_WEBP.name} — {width}x{height}, {kb:.0f} KB, 삽화가 들어간 칸 {n_art}개")
    if n_art == 0:
        print("  (art/ 에 삽화가 없어 픽토그램인 채로 구웠다. 삽화를 만든 뒤 다시 돌리면 된다)")


def main() -> None:
    ap = argparse.ArgumentParser(description="요즘판 보드를 통짜 그림 한 장으로 굽는다")
    ap.add_argument("--scale", type=int, default=3, help="해상도 배수 (기본 3 → 1560x2274)")
    ap.add_argument("--quality", type=int, default=88, help="webp 품질 (기본 88)")
    ap.add_argument("--keep-png", action="store_true", help="중간 png 도 남긴다")
    args = ap.parse_args()

    if args.scale < 1 or args.scale > 6:
        sys.exit("--scale 은 1~6 이어야 한다")

    bake(args.scale, args.keep_png, args.quality)


if __name__ == "__main__":
    main()
