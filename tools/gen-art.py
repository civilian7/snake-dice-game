"""요즘판 칸 삽화 50장을 이미지 모델로 만든다.

    pip install google-genai pillow
    set GEMINI_API_KEY=...            (PowerShell: $env:GEMINI_API_KEY="...")

    python tools/gen-art.py --only 4          # 한 장만 먼저 보고
    python tools/gen-art.py                   # 빠진 것만 전부
    python tools/gen-art.py --force --only 44 # 마음에 안 드는 칸만 다시
    python tools/gen-art.py --convert         # 이미 받은 png 를 webp 로

프롬프트 원문과 검수 기준은 docs/art-prompts.md 에 있다.
"""

import argparse
import io
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ART_DIR = ROOT / "art"

MODEL = "gemini-2.5-flash-image"     # 다른 모델을 쓰려면 --model 로 바꾼다
SIZE = 256                           # 저장 크기. 칸은 화면에서 34~47px 다
QUALITY = 82

# 줄여도 읽히게 — 이것이 이 스타일의 유일한 목표다.
STYLE = (
    "Retro Korean children's board-game illustration, 1970s-80s printed paper game board style. "
    "Hand-drawn cartoon, bold black ink outlines, flat saturated poster colors "
    "(mustard yellow, vermilion red, grass green, sky blue, cream), no gradients, no shading. "
    "Slightly rough offset-print texture, cheerful and simple. "
    "ONE simple scene, centered, filling the whole square edge to edge, full bleed. "
    "Very high contrast and chunky shapes so it stays readable when scaled down to 48x48 pixels. "
    "Absolutely NO text, NO letters, NO numbers, NO speech bubbles, NO watermark, NO frame, NO border. "
    "Square 1:1 composition. "
)

# 칸 번호 → (한 줄 설명, 프롬프트). 짝수 칸 50개가 전부다 —
# 고속도로·뱀이 쓰는 칸이 모두 짝수라서 홀수 칸에는 그림이 필요 없다.
SCENES = {
    # ── 고속도로 시작: 한 일
    4:  ("자리 양보", "Scene: a child standing up from a subway seat and gesturing for a smiling elderly person with a walking cane to sit down."),
    8:  ("운동", "Scene: a child lifting a heavy barbell overhead with a determined face, sweat drops, simple gym floor."),
    18: ("나무 심기", "Scene: a child kneeling on a bare brown hillside planting a small green sapling, a shovel stuck in the soil."),
    20: ("보이스피싱 신고", "Scene: a child holding a phone away from their ear with a suspicious frown, pointing at the phone, alert expression."),
    24: ("심폐소생술", "Scene: a person kneeling on the ground pressing both hands on the chest of someone lying down, urgent expression."),
    32: ("공부", "Scene: a student at a desk at night reading a thick book under a lamp, stack of books, focused face."),
    34: ("성실히 일함", "Scene: a cheerful young worker in overalls walking to work carrying a toolbox, sleeves rolled up."),
    40: ("텃밭", "Scene: a child watering leafy vegetables growing in a wooden planter box on a rooftop, watering can tilted."),
    48: ("분리수거", "Scene: a child dropping a plastic bottle into one of three separate recycling bins, other bins for paper and cans."),
    70: ("구조", "Scene: a person on a dock throwing an orange ring buoy toward someone splashing in the water."),
    76: ("연구", "Scene: a scientist in a white coat looking into a microscope, glass flasks with colored liquid on the bench."),
    80: ("달리기 일등", "Scene: a child sprinting and breaking through a finish-line tape in first place, arms back, joyful face."),
    90: ("헌혈", "Scene: a person lying calmly on a donation chair with a tube in their arm, a nurse standing beside with a blood bag."),

    # ── 고속도로 도착: 그래서 된 일
    16: ("칭찬받음", "Scene: a smiling elderly person patting a happy child on the head in praise, warm friendly mood."),
    12: ("트로피", "Scene: a child on a podium holding up a big shiny gold trophy with both hands, beaming."),
    38: ("푸른 숲", "Scene: a lush green forest of full-grown trees covering a whole mountain, birds in a blue sky."),
    74: ("표창", "Scene: a police officer handing an award certificate and a medal to a proud child, saluting."),
    36: ("의사가 됨", "Scene: a confident doctor in a white coat with a stethoscope around the neck, arms crossed, hospital behind."),
    56: ("졸업", "Scene: a graduate in cap and gown tossing the graduation cap into the air, holding a rolled diploma."),
    46: ("목돈", "Scene: a happy person holding a thick stack of banknotes and a savings bankbook, coins piled beside."),
    60: ("수확", "Scene: a woven basket overflowing with freshly picked carrots, tomatoes and greens on the soil."),
    54: ("깨끗한 지구", "Scene: a sparkling clean planet Earth with green continents and blue oceans, sparkle marks around it."),
    88: ("감사", "Scene: a rescued person wrapped in a towel bowing deeply in thanks to their rescuer beside the water."),
    86: ("발견", "Scene: a scientist throwing both arms up in delight, a big glowing lightbulb above their head."),
    100: ("우승", "Scene: a child wearing a gold winner's crown with both arms raised in victory, confetti falling."),
    92: ("살아난 사람", "Scene: a patient sitting up smiling in a hospital bed, recovered, a big red heart shape floating above."),

    # ── 뱀 시작: 한 일
    22: ("언 호수 스케이트", "Scene: a child ice-skating alone far out on a frozen lake, thin cracks spreading under the skates."),
    28: ("밤새 영상", "Scene: a child lying in bed at night staring at a glowing phone with heavy tired eyes, dark room, moon in window."),
    30: ("낙서", "Scene: a child spray-painting scribbles on someone's brick wall while glancing over the shoulder guiltily."),
    44: ("친구를 때림", "Scene: one angry child punching another child who is falling backward, impact burst mark."),
    58: ("반려견 괴롭힘", "Scene: a child poking a stranger's dog with a stick, the dog baring its teeth and growling."),
    66: ("남의 물건", "Scene: a sneaky hand pulling a wallet out of someone's open bag from behind, the owner unaware."),
    68: ("과식", "Scene: a child stuffing their mouth greedily in front of a huge pile of delivered fried chicken and pizza boxes."),
    72: ("위험한 물건", "Scene: a child holding a lit firecracker with a burning fuse, sparks flying, careless grin."),
    84: ("선로 셀카", "Scene: a teenager standing on railway tracks holding a phone up to take a selfie, a train headlight far down the track."),
    94: ("불장난", "Scene: a child crouching with a lighter over a pile of dry straw, small flames already catching."),
    96: ("나무 남벌", "Scene: a person swinging an axe at the last tree on a stripped bare mountain, cut stumps everywhere."),
    98: ("난간", "Scene: a child climbing over a high balcony railing and leaning out dangerously, feet off the floor."),

    # ── 뱀 도착: 그래서 된 일
    2:  ("얼음물에 빠짐", "Scene: a child fallen through broken ice into freezing water, only head and arms above the surface, shivering, calling for help."),
    6:  ("성적 추락", "Scene: a slumped student holding up a test paper with a big red X, head down, gloomy mood."),
    10: ("혼남", "Scene: an angry adult with a raised finger scolding a child who hangs their head guiltily."),
    26: ("합의금", "Scene: a sad child reluctantly handing over a thick envelope of money with both hands, empty wallet on the floor."),
    42: ("물림", "Scene: a crying child with a big bandage wrapped around their forearm, tooth marks, the dog walking away."),
    14: ("갇힘", "Scene: a regretful child sitting on a bench behind thick jail bars, knees pulled up."),
    52: ("배탈", "Scene: a child doubled over clutching their stomach with a queasy green face, sweat drops."),
    50: ("응급실", "Scene: paramedics carrying a bandaged child on a stretcher into an emergency room, ambulance behind."),
    62: ("기차", "Scene: a speeding train rushing past inches away while a terrified person falls back off the tracks."),
    64: ("소방", "Scene: firefighters spraying a thick jet of water onto a burning house, a red fire engine beside them."),
    82: ("산사태", "Scene: a brown muddy landslide sweeping down a bare mountainside toward small houses below."),
    78: ("입원", "Scene: a child lying in a hospital bed with one leg raised in a white cast, crutches leaning nearby."),
}


def out_path(n):
    return ART_DIR / f"{n:03d}.webp"


def write_manifest():
    """만들어 둔 칸 목록을 art/manifest.json 에 적는다.

    게임은 이 파일을 보고 있는 칸만 요청한다. 없으면 아직 안 만든 칸까지 요청해
    404 가 쏟아진다. 손으로 파일을 넣었다면 `--manifest` 로 다시 만들 것.
    """
    import json
    ART_DIR.mkdir(exist_ok=True)
    have = sorted(n for n in SCENES if out_path(n).exists())
    (ART_DIR / "manifest.json").write_text(json.dumps(have), encoding="utf-8")
    print(f"art/manifest.json — {len(have)}칸")
    return have


def save_webp(data, path):
    from PIL import Image
    img = Image.open(io.BytesIO(data)).convert("RGB")
    if img.width != img.height:                     # 모델이 비율을 어기면 가운데를 자른다
        s = min(img.size)
        l = (img.width - s) // 2
        t = (img.height - s) // 2
        img = img.crop((l, t, l + s, t + s))
    img.resize((SIZE, SIZE), Image.LANCZOS).save(path, "WEBP", quality=QUALITY)


def convert_existing():
    """이미 손으로 받아 둔 png/jpg 를 webp 로 줄인다."""
    ART_DIR.mkdir(exist_ok=True)
    done = 0
    for src in sorted(ART_DIR.iterdir()):
        if src.suffix.lower() not in (".png", ".jpg", ".jpeg"):
            continue
        try:
            n = int(src.stem)
        except ValueError:
            print(f"  건너뜀 (칸 번호가 아닌 이름): {src.name}")
            continue
        save_webp(src.read_bytes(), out_path(n))
        print(f"  {src.name} -> {out_path(n).name}")
        done += 1
    print(f"\n{done}장 변환")
    write_manifest()


def generate(nums, model, force, sleep):
    from google import genai
    from google.genai import types

    if not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        sys.exit("GEMINI_API_KEY 환경변수가 없다. 키를 넣고 다시 실행할 것.")

    ART_DIR.mkdir(exist_ok=True)
    client = genai.Client()

    made, skipped, failed = 0, 0, []
    for n in nums:
        label, scene = SCENES[n]
        path = out_path(n)

        if path.exists() and not force:
            skipped += 1
            continue

        print(f"[{n:3d}] {label} ... ", end="", flush=True)
        try:
            resp = client.models.generate_content(
                model=model,
                contents=STYLE + scene,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="1:1"),
                    candidate_count=1,
                ),
            )

            data = None
            for part in resp.candidates[0].content.parts:
                if getattr(part, "inline_data", None):
                    data = part.inline_data.data
                    break

            if not data:
                print("이미지가 안 왔다")
                failed.append(n)
            else:
                save_webp(data, path)
                print(f"저장 {path.name}")
                made += 1

        except Exception as e:                       # 한 장이 실패해도 나머지는 계속
            print(f"실패: {type(e).__name__}: {e}")
            failed.append(n)

        time.sleep(sleep)

    print(f"\n만든 것 {made} · 이미 있어 건너뜀 {skipped} · 실패 {len(failed)}")
    write_manifest()
    if failed:
        print("다시 돌릴 칸: --only " + ",".join(str(n) for n in failed))
    print("\n브라우저를 새로 고치면 게임이 자동으로 삽화를 쓴다.")
    print("마음에 안 드는 칸은  python tools/gen-art.py --force --only <번호>")


def main():
    ap = argparse.ArgumentParser(description="요즘판 칸 삽화 생성")
    ap.add_argument("--only", help="칸 번호만 골라서 (예: 4 또는 4,8,18)")
    ap.add_argument("--force", action="store_true", help="이미 있는 파일도 다시 만든다")
    ap.add_argument("--model", default=MODEL, help=f"이미지 모델 (기본 {MODEL})")
    ap.add_argument("--sleep", type=float, default=1.0, help="호출 사이 대기 초")
    ap.add_argument("--convert", action="store_true", help="art/ 의 png 를 webp 로 줄이기만 한다")
    ap.add_argument("--manifest", action="store_true", help="art/manifest.json 만 다시 만든다")
    ap.add_argument("--list", action="store_true", help="칸 목록만 보여 준다")
    args = ap.parse_args()

    if args.convert:
        convert_existing()
        return

    if args.manifest:
        write_manifest()
        return

    if args.list:
        for n in sorted(SCENES):
            mark = "있음" if out_path(n).exists() else "없음"
            print(f"{n:3d}  {mark}  {SCENES[n][0]}")
        return

    if args.only:
        nums = []
        for tok in args.only.replace(" ", "").split(","):
            n = int(tok)
            if n not in SCENES:
                sys.exit(f"{n}번 칸에는 그림이 없다(홀수 칸이거나 범위 밖). --list 로 확인할 것.")
            nums.append(n)
    else:
        nums = sorted(SCENES)

    generate(nums, args.model, args.force, args.sleep)


if __name__ == "__main__":
    main()
