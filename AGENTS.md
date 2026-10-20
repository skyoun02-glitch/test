# HyperFrames Composition Project

> **이 폴더의 모든 영상은 파일 맨 아래 "내 디자인 규칙"을 반드시 지킨다.** HyperFrames 규칙과 겹치면 둘 다 지키고, 디자인 선택은 "내 디자인 규칙"이 우선한다.

## Skills — USE THESE FIRST

**Always invoke the relevant skill before writing or modifying compositions.** Skills encode framework-specific patterns (e.g., `window.__timelines` registration, `data-*` attribute semantics, shader-compatible CSS rules) that are NOT in generic web docs. Skipping them produces broken compositions.

**Doing anything with HyperFrames?** Start at `/hyperframes` — it tells you what HyperFrames can do and which skill or workflow handles your intent (make a video, TTS / BGM, prep footage, author / animate, render, install blocks), confirms your brief up front (the intent layer), and routes every "make me a…" request (a video, a deck, a composition port) to the right workflow. Read it first, especially when there's no project context to orient you. The workflows it routes to:

- `/product-launch-video` — any **website** URL or brief / script → a product launch / SaaS / promo video, or a site tour / showcase featuring the site's own captured visuals.
- `/faceless-explainer` — arbitrary text (topic / article / notes), **no URL, no website capture** → 60-90s faceless explainer.
- `/embedded-captions` — an existing talking-head video (MP4) → the same footage with captions / subtitles added (rail + embed, or pure-cinematic embed); the footage itself is untouched.
- `/talking-head-recut` — an existing talking-head / interview / podcast video (MP4) → the same footage **packaged with designed graphic overlays** (kinetic titles, lower-thirds, data callouts, pull-quotes, side panels, pip) synced to the transcript; the clip plays unchanged underneath. (Plain captions/subtitles → `/embedded-captions`.)
- `/pr-to-video` — a GitHub PR (URL / `owner/repo#N` / "this PR") → 30-90s code-change explainer (changelog / feature reveal / fix / refactor).
- `/motion-graphics` — a short (typically under 10s) design-led **motion graphic**, motion-is-the-message, no narration: kinetic type, a stat / number count-up, a chart, a logo sting, a lower-third / overlay, or an animated tweet / headline / captured-page highlight; rendered to MP4 or a transparent overlay. Longer / narrated / custom → `/general-video`.
- `/music-to-video` — a **music track** (audio file, video to pull audio from, or one generated from a mood brief) → beat-synced video (lyric / slideshow / kinetic promo). Music drives pacing; user-supplied images / videos are cut onto the same beat grid.
- `/slideshow` — a **presentation / pitch deck / interactive deck** — discrete slides, fragment reveals, branching, hotspot navigation, presenter mode. Output is a navigable deck, not a rendered video.
- `/general-video` — fallback for any other video (title card, longer brand / sizzle reel, multi-scene montage, static loop, custom composition) and the home of **companion mode** — co-create with the full HyperFrames toolbox; the original hyperframes authoring flow, any length.

**Porting an existing composition?** `/remotion-to-hyperframes` translates a Remotion (React) composition into HyperFrames HTML — a source migration, separate from the creation workflows above.

The domain skills (`/hyperframes-core`, `/hyperframes-animation`, `/hyperframes-keyframes`, `/hyperframes-creative`, `/hyperframes-cli`, `/media-use`, `/hyperframes-audio`, `/hyperframes-registry`, `/figma`) and the full capability map live inside `/hyperframes` — it is the single source of truth for which skill handles which intent.

**Changing how real footage or images look or reveal?** Load `/media-use` and read its `references/media-treatments.md` before editing, even when the request only says dark, flat, boring, retro, private, or “make the reveal cooler.” It governs how footage is treated, never whether media may be used. Use canonical media treatments and seek-safe motion; do not improvise equivalent CSS/SVG filters or overlays.

> **Tailwind v4 projects** (`hyperframes init --tailwind`): see `/hyperframes-core` → `references/tailwind.md`.

> **Using a HyperFrames plugin?** Load skills from that installed bundle and follow
> its `hyperframes/references/plugin-installation.md` execution rules. Update via
> the plugin manager, not the standalone commands below.
>
> **Standalone skill missing or stale?** Run `npx hyperframes skills update <name>` to install/refresh
> the specific skill you need (the `/hyperframes` router does this automatically before
> entering a workflow), or bare `npx hyperframes skills update` to refresh the core set plus
> everything already installed — neither pulls the full set. Restart the agent session so
> newly installed skills load.

## Commands

```bash
npm run dev          # human-operated foreground preview (blocks until stopped)
npx hyperframes preview --background  # agent-safe persistent Studio preview
npx hyperframes preview --status      # verify the persistent preview is listening
npx hyperframes preview --stop        # stop it when review is finished
npm run check        # lint + runtime + layout + motion + contrast (one command)
npm run render       # render to MP4
npm run publish      # publish and get a shareable link
npx hyperframes lint --verbose  # include info-level findings
npx hyperframes lint --json     # machine-readable output for CI
npx hyperframes docs <topic> # reference docs in terminal
```

> **Agents must use `npx hyperframes preview --background` for Studio handoff.** Do not rely
> on a shell/tool `run_in_background` wrapper around `npm run dev`: that foreground process
> remains owned by the invoking session and can disappear while the browser stays open,
> leaving refreshes at `ERR_CONNECTION_TIMED_OUT`. Verify with `preview --status`, keep it
> alive through review, and stop it explicitly with `preview --stop` afterward.

> **Back from the desktop app.** Once this project was opened in the HyperFrames desktop app, run `npx hyperframes catch-up` before your next change here: it lists what the person asked Framey in the app and which files changed since.

> **Pinned CLI version.** These scripts pin an exact `hyperframes@X.Y.Z` so this project re-renders identically over time. Weeks later that pin lags fixes shipped since. To move up: `npx hyperframes@latest upgrade --project . --check` (shows the delta), then `npx hyperframes@latest upgrade --project .` to rewrite the pins. Always unpinned — the pinned script re-runs the old version against itself.

## Documentation

**For quick reference**, use the local CLI docs command (no network required):

```bash
npx hyperframes docs <topic>
```

Topics: `data-attributes`, `gsap`, `compositions`, `rendering`, `examples`, `troubleshooting`

**For full documentation**, discover pages via the machine-readable index — do NOT guess URLs:

```
https://hyperframes.heygen.com/llms.txt
```

## Project Structure

- `index.html` — main composition (root timeline)
- `compositions/` — sub-compositions referenced via `data-composition-src`
- `meta.json` — project metadata (id, name)
- `transcript.json` — whisper word-level transcript (if generated)

## Linting — ALWAYS RUN AFTER CHANGES

After creating or editing any `.html` composition, **always** run the full check before considering the task complete:

```bash
npm run check
```

Fix all errors before presenting the result. Warnings should be reviewed before rendering.

## Key Rules

1. Every timed element needs `data-start` and a duration. `data-start` is what marks it as timed; `data-track-index` is an optional Studio display lane the render never reads
2. Give timed visual elements `class="clip"`. The framework keys visibility off `data-start`, not the class, but the shared `.clip` CSS is what gives a scene its full-frame box, and `lint` warns without it
3. Register one paused root timeline per composition on `window.__timelines`:
   ```js
   window.__timelines = window.__timelines || {};
   window.__timelines["composition-id"] = gsap.timeline({ paused: true });
   ```
   Scene timelines manually added to this root must not be paused. A paused
   child does not advance when the root is seeked. The runtime activates
   registered composition siblings, not arbitrary nested scene timelines.
4. A video with sound keeps it on the `<video>` (`data-has-audio="true"`, no `muted`). Use a separate `<audio>` for music, voiceover, replacement audio, J/L cuts, or audio detached in Studio. Silent footage and b-roll: `muted`.
5. Sub-compositions use `data-composition-src="compositions/file.html"` to reference other HTML files
6. Only deterministic logic — no `Date.now()`, no `Math.random()`, no network fetches

---

# 내 디자인 규칙

이 폴더에서 만드는 모든 영상(모션그래픽)은 아래 규칙을 지킨다. 사용자가 그 영상에 대해 따로 말한 것이 있으면 그 말이 우선한다.

## 1. 기본 규격

- **해상도:** 1080×1920 세로 릴스 (9:16). 루트에 `data-width="1080"` `data-height="1920"`, `<html data-resolution="portrait">`.
- **프레임:** 30fps. 렌더할 때 `--fps 30`.
- **기본 길이:** 30초. 루트 `data-duration="30"`.
- **장면:** 기본 6장면 (장면당 약 5초). 장면마다 `compositions/` 아래 하위 컴포지션으로 나눈다.

## 2. 글꼴

- `assets/fonts/` 안에 있는 글꼴 파일만 쓴다. `@font-face`로 그 파일을 불러오고, Google Fonts 같은 외부 글꼴이나 시스템 글꼴로 대신하지 않는다.
- 제목은 가지고 있는 굵기 중 가장 굵은 것을 쓴다.
- `assets/fonts/`가 비어 있거나 필요한 글자(한글 등)가 없으면, 작업을 멈추고 사용자에게 글꼴 파일을 넣어 달라고 말한다.

## 3. 색

- **배경:** `#FFFFFF` (흰색)
- **글자:** `#111111` (검정)
- **강조:** `#E63B2E` (빨강). 강조색은 한 장면에서 핵심 한 곳에만 쓴다.
- 위 세 색 밖의 색은 사용자가 지정했을 때만 쓴다.

## 4. 이징(움직임 속도)

- **들어올 때:** 감속 — 빠르게 들어와 천천히 멈춘다. (`power3.out`, `expo.out` 등 `.out`)
- **나갈 때:** 가속 — 천천히 출발해 빠르게 빠진다. (`power3.in`, `expo.in` 등 `.in`)
- **금지:** 같은 속도로 움직이는 것. `ease: "none"`, `linear`를 쓰지 않는다.

## 5. 글자

- 크게 쓴다. 제목 96px 이상, 본문 64px 이상.
- 한 문구는 다 나타난 뒤 최소 1.5초 동안 화면에 머문다 (들어오고 나가는 시간은 빼고 센다).

## 6. 안전 영역

- 위 15%(0–288px), 아래 20%(1536–1920px)에는 글자를 두지 않는다.
- 글자는 세로 288px–1536px 사이에만 둔다. 배경과 장식 도형은 안전 영역에 들어가도 된다.

## 7. 쓸 움직임 (이 목록에서 고른다)

- **슬라이드 인:** 옆이나 아래에서 미끄러져 들어오기
- **스케일 업:** 작게 시작해 원래 크기로 커지기
- **마스크 공개:** 가려진 상자가 걷히며 드러나기
- **글자 순차 등장:** 글자나 단어가 하나씩 차례로 나타나기
- **숫자 카운트업:** 사용자가 준 숫자까지 올라가기
- **선 그리기:** 선, 밑줄, 도형 테두리가 그려지기

장면마다 다른 움직임을 섞어 쓴다. 목록 밖의 움직임은 사용자가 원할 때만 쓴다.

## 8. 금지

- 모든 장면에 똑같은 페이드 전환 쓰기
- 의미 없는 모서리 라벨 (구석의 장식용 글자, 가짜 번호, "SCENE 01" 같은 것)
- 보라색 그라데이션 (배경, 글자, 도형 모두)
- 같은 효과음 반복
- 사용자가 주지 않은 숫자, 통계, 후기, 고객 이름 지어내기

## 9. 렌더

1. 렌더 전에 반드시 `npm run check`를 돌린다.
2. 오류나 경고가 하나라도 있으면 렌더하지 않고 먼저 고친다. 다시 check해서 통과해야 다음으로 간다.
3. 통과하면 `renders/` 폴더에 mp4로 렌더한다. (`npm run render -- -o renders/<이름>.mp4 --fps 30`)
4. `package.json`에 고정된 버전(`hyperframes@0.8.181`)으로만 실행한다. `@latest`나 버전 없는 `npx hyperframes`는 쓰지 않는다.
