# 요즘판 칸 삽화 — 이미지 생성 프롬프트 팩

「뱀주사위놀이 요즘판」의 칸 삽화 **50장**을 이미지 모델로 만들기 위한 프롬프트다.
그대로 복사해 제미나이(또는 다른 이미지 모델)에 넣으면 된다.
`tools/gen-art.py` 로 한꺼번에 돌릴 수도 있다.

## 왜 50장인가

원본 판의 성질 하나 — **고속도로·뱀이 쓰는 칸 50개가 모두 짝수**이고 그것이 2~100의
짝수 전부다. 홀수 칸은 인과에 쓰이지 않아 비워 둔다. 그래서 필요한 그림은 짝수 칸 50장이다.

각 칸은 **원인 아니면 결과**다.

- **시작 칸**(25장) — 「한 일」. 그 칸을 밟으면 고속도로를 타거나 뱀에게 물린다.
- **도착 칸**(25장) — 「그래서 된 일」. 고속도로·뱀이 데려다 놓는 칸이다.

글을 읽지 않고 **그림만 좇아도 인과가 읽혀야 한다.** 그것이 이 팩의 유일한 합격 기준이다.

## 출력 규격 (반드시 지킬 것)

| | |
|---|---|
| 비율 | **1:1 정사각** |
| 크기 | 512×512 이상 (게임에서는 48~64px 로 줄여 쓴다) |
| 파일명 | `art/004.webp` … `art/100.webp` — **칸 번호를 세 자리로 0 채움** |
| 배경 | 칸을 꽉 채우는 **full-bleed**. 테두리·액자·여백 없음 |
| 글자 | **절대 금지.** 숫자·한글·영문·말풍선 글씨가 하나도 없어야 한다 |

게임은 `art/004.webp` 가 있으면 자동으로 삽화를 쓰고, 없으면 지금의 SVG 픽토그램을 쓴다.
**한 장만 먼저 만들어 확인**하고 마음에 들면 나머지를 돌리면 된다.

## 공통 스타일 (모든 프롬프트 앞에 붙는다)

```
Retro Korean children's board-game illustration, 1970s-80s printed paper game board style.
Hand-drawn cartoon, bold black ink outlines, flat saturated poster colors
(mustard yellow, vermilion red, grass green, sky blue, cream), no gradients, no shading.
Slightly rough offset-print texture, cheerful and simple.
ONE simple scene, centered, filling the whole square edge to edge, full bleed.
Very high contrast and chunky shapes so it stays readable when scaled down to 48x48 pixels.
Absolutely NO text, NO letters, NO numbers, NO speech bubbles, NO watermark, NO frame, NO border.
Square 1:1 composition.
```

> **줄여도 읽히게** 가 이 스타일의 핵심이다. 칸은 화면에서 34~47px 밖에 안 된다.
> 인물은 크게, 배경은 최소로, 색은 세 가지 안쪽으로.

---

## 고속도로 — 시작 칸 (한 일)

| 칸 | 이야기 | 프롬프트 (공통 스타일 뒤에 붙인다) |
|---|---|---|
| **004** | 지하철에서 어르신께 자리를 양보했다 | `Scene: a child standing up from a subway seat and gesturing for a smiling elderly person with a walking cane to sit down.` |
| **008** | 꾸준히 운동해 대회에서 상을 받았다 | `Scene: a child lifting a heavy barbell overhead with a determined face, sweat drops, simple gym floor.` |
| **018** | 나무를 심어 헐벗은 산을 되살렸다 | `Scene: a child kneeling on a bare brown hillside planting a small green sapling, a shovel stuck in the soil.` |
| **020** | 보이스피싱을 알아채고 신고해 표창을 받았다 | `Scene: a child holding a phone away from their ear with a suspicious frown, pointing at the phone, alert expression.` |
| **024** | 쓰러진 사람에게 심폐소생술을 해 살렸다 | `Scene: a person kneeling on the ground pressing both hands on the chest of someone lying down, urgent expression.` |
| **032** | 미루지 않고 공부해 졸업했다 | `Scene: a student at a desk at night reading a thick book under a lamp, stack of books, focused face.` |
| **034** | 성실히 일해 첫 목돈을 모았다 | `Scene: a cheerful young worker in overalls walking to work carrying a toolbox, sleeves rolled up.` |
| **040** | 텃밭을 가꿔 손수 거두었다 | `Scene: a child watering leafy vegetables growing in a wooden planter box on a rooftop, watering can tilted.` |
| **048** | 분리수거를 꼼꼼히 해 칭찬을 받았다 | `Scene: a child dropping a plastic bottle into one of three separate recycling bins, other bins for paper and cans.` |
| **070** | 물에 빠진 사람을 구해 냈다 | `Scene: a person on a dock throwing an orange ring buoy toward someone splashing in the water.` |
| **076** | 연구에 몰두해 새로운 것을 밝혀냈다 | `Scene: a scientist in a white coat looking into a microscope, glass flasks with colored liquid on the bench.` |
| **080** | 달리기에서 일등을 하여 우승했다 | `Scene: a child sprinting and breaking through a finish-line tape in first place, arms back, joyful face.` |
| **090** | 헌혈에 참여해 누군가를 살렸다 | `Scene: a person lying calmly on a donation chair with a tube in their arm, a nurse standing beside with a blood bag.` |

## 고속도로 — 도착 칸 (그래서 된 일)

| 칸 | 어디서 왔나 | 프롬프트 |
|---|---|---|
| **016** | ← 004 자리 양보 | `Scene: a smiling elderly person patting a happy child on the head in praise, warm friendly mood.` |
| **012** | ← 008 운동 | `Scene: a child on a podium holding up a big shiny gold trophy with both hands, beaming.` |
| **038** | ← 018 나무 심기 | `Scene: a lush green forest of full-grown trees covering a whole mountain, birds in a blue sky.` |
| **074** | ← 020 신고 | `Scene: a police officer handing an award certificate and a medal to a proud child, saluting.` |
| **036** | ← 024 심폐소생술 | `Scene: a confident doctor in a white coat with a stethoscope around the neck, arms crossed, hospital behind.` |
| **056** | ← 032 공부 | `Scene: a graduate in cap and gown tossing the graduation cap into the air, holding a rolled diploma.` |
| **046** | ← 034 성실히 일함 | `Scene: a happy person holding a thick stack of banknotes and a savings bankbook, coins piled beside.` |
| **060** | ← 040 텃밭 | `Scene: a woven basket overflowing with freshly picked carrots, tomatoes and greens on the soil.` |
| **054** | ← 048 분리수거 | `Scene: a sparkling clean planet Earth with green continents and blue oceans, sparkle marks around it.` |
| **088** | ← 070 구조 | `Scene: a rescued person wrapped in a towel bowing deeply in thanks to their rescuer beside the water.` |
| **086** | ← 076 연구 | `Scene: a scientist throwing both arms up in delight, a big glowing lightbulb above their head.` |
| **100** | ← 080 달리기 | `Scene: a child wearing a gold winner's crown with both arms raised in victory, confetti falling.` |
| **092** | ← 090 헌혈 | `Scene: a patient sitting up smiling in a hospital bed, recovered, a big red heart shape floating above.` |

## 뱀 — 시작 칸 (한 일)

| 칸 | 이야기 | 프롬프트 |
|---|---|---|
| **022** | 얼어붙은 호수에 들어가 얼음이 깨져 빠졌다 | `Scene: a child ice-skating alone far out on a frozen lake, thin cracks spreading under the skates.` |
| **028** | 밤새 영상만 보다 시험을 망쳤다 | `Scene: a child lying in bed at night staring at a glowing phone with heavy tired eyes, dark room, moon in window.` |
| **030** | 남의 담벼락에 낙서를 하다 붙잡혔다 | `Scene: a child spray-painting scribbles on someone's brick wall while glancing over the shoulder guiltily.` |
| **044** | 친구를 때려 합의금을 물어 주었다 | `Scene: one angry child punching another child who is falling backward, impact burst mark.` |
| **058** | 남의 반려견을 괴롭히다 물렸다 | `Scene: a child poking a stranger's dog with a stick, the dog baring its teeth and growling.` |
| **066** | 남의 물건에 손을 대어 붙잡혀 갇혔다 | `Scene: a sneaky hand pulling a wallet out of someone's open bag from behind, the owner unaware.` |
| **068** | 배달 음식을 욕심껏 먹다 배탈이 났다 | `Scene: a child stuffing their mouth greedily in front of a huge pile of delivered fried chicken and pizza boxes.` |
| **072** | 위험한 물건을 장난삼아 다루다 크게 다쳤다 | `Scene: a child holding a lit firecracker with a burning fuse, sparks flying, careless grin.` |
| **084** | 선로에 내려가 사진을 찍다 큰일 날 뻔했다 | `Scene: a teenager standing on railway tracks holding a phone up to take a selfie, a train headlight far down the track.` |
| **094** | 불장난을 하다 불을 냈다 | `Scene: a child crouching with a lighter over a pile of dry straw, small flames already catching.` |
| **096** | 나무를 마구 베어 산사태가 났다 | `Scene: a person swinging an axe at the last tree on a stripped bare mountain, cut stumps everywhere.` |
| **098** | 난간에 올라갔다가 떨어졌다 | `Scene: a child climbing over a high balcony railing and leaning out dangerously, feet off the floor.` |

## 뱀 — 도착 칸 (그래서 된 일)

| 칸 | 어디서 왔나 | 프롬프트 |
|---|---|---|
| **002** | ← 022 언 호수 | `Scene: a child fallen through broken ice into freezing water, only head and arms above the surface, shivering, calling for help.` |
| **006** | ← 028 밤새 영상 | `Scene: a slumped student holding up a test paper with a big red X, head down, gloomy mood.` |
| **010** | ← 030 낙서 | `Scene: an angry adult with a raised finger scolding a child who hangs their head guiltily.` |
| **026** | ← 044 친구를 때림 | `Scene: a sad child reluctantly handing over a thick envelope of money with both hands, empty wallet on the floor.` |
| **042** | ← 058 반려견 | `Scene: a crying child with a big bandage wrapped around their forearm, tooth marks, the dog walking away.` |
| **014** | ← 066 남의 물건 | `Scene: a regretful child sitting on a bench behind thick jail bars, knees pulled up.` |
| **052** | ← 068 과식 | `Scene: a child doubled over clutching their stomach with a queasy green face, sweat drops.` |
| **050** | ← 072 위험한 물건 | `Scene: paramedics carrying a bandaged child on a stretcher into an emergency room, ambulance behind.` |
| **062** | ← 084 선로 사진 | `Scene: a speeding train rushing past inches away while a terrified person falls back off the tracks.` |
| **064** | ← 094 불장난 | `Scene: firefighters spraying a thick jet of water onto a burning house, a red fire engine beside them.` |
| **082** | ← 096 나무 벰 | `Scene: a brown muddy landslide sweeping down a bare mountainside toward small houses below.` |
| **078** | ← 098 난간 | `Scene: a child lying in a hospital bed with one leg raised in a white cast, crutches leaning nearby.` |

---

## 검수 기준

만들고 나서 **50장을 한 판에 늘어놓고** 아래를 본다. 하나라도 걸리면 그 칸만 다시 돌린다.

1. **글자가 있는가** — 한 자라도 있으면 버린다. 모델이 가장 자주 어기는 항목이다.
2. **48px 로 줄여도 무엇인지 알겠는가** — 이게 가장 많이 탈락한다. 인물이 작거나
   배경이 복잡하면 줄이는 순간 뭉갠다.
3. **원인과 결과가 짝지어 보이는가** — 004(양보)와 016(칭찬), 034(일)과 046(돈)을
   나란히 놓고 이야기가 이어지는지 본다.
4. **50장이 한 세트로 보이는가** — 선 굵기·채도·인물 크기가 튀는 장이 있으면 다시.
5. **칸을 꽉 채우는가** — 흰 여백이나 액자 테두리가 생기면 다시.

## 게임에 넣기

1. 만든 파일을 `art/` 에 칸 번호로 넣는다 — `art/004.webp` … `art/100.webp`
2. **`python tools/gen-art.py --manifest`** 를 돌려 `art/manifest.json` 을 만든다.
   게임은 이 목록을 보고 **있는 칸만** 불러온다 — 그래서 50장을 다 만들기 전에도
   아직 없는 칸을 요청하지 않는다. (스크립트로 생성하면 자동으로 갱신된다)
3. 브라우저에서 새로 고친다. 만든 칸은 삽화로, 아직 안 만든 칸은 SVG 픽토그램으로
   나온다. **코드를 고칠 필요가 없다.**
4. png 로 받았으면 webp 로 줄인다 (`tools/gen-art.py --convert` 또는 아래 한 줄)

```powershell
Get-ChildItem art\*.png | ForEach-Object {
  python -c "from PIL import Image; import sys; Image.open(sys.argv[1]).resize((256,256)).save(sys.argv[1][:-4]+'.webp','WEBP',quality=82)" $_.FullName
}
```

## 저작권

여기서 만든 그림은 **원본 판을 베끼지 않은 새 그림**이다. 원본 스캔(`board.webp`)과 달리
자유롭게 쓸 수 있다. 그래서 요즘판만으로도 게임이 온전히 굴러가고, 공개 배포에도 문제가 없다.
프롬프트에 원본 그림을 넣어 「이 그림처럼」 시키지 말 것 — 그러면 2차적저작물이 된다.
