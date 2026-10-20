"""밝고 가벼운 배경음을 코드로 합성해 WAV로 저장한다.

- 템포 100BPM, 4/4박자, C장조 (C - G - Am - F 반복)
- 장면이 바뀌는 시점마다 악기가 하나씩 더해진다
  (패드 -> 킥 -> 베이스 -> 하이햇 -> 아르페지오 -> 벨 멜로디)
- 마지막은 서서히 작아진다 (페이드아웃)

사용법:
  python scripts/make_bgm.py                          # 기본: 30초, 5초마다 장면 전환
  python scripts/make_bgm.py --length 15 --scenes 0,4,8,12 --out assets/audio/bgm.wav

필요한 것: Python 3.9+, numpy. 무작위 값은 고정 시드를 써서 매번 같은 소리가 나온다.
"""

import argparse
import wave
from pathlib import Path

import numpy as np

SR = 44100
BPM = 100
BEAT = 60 / BPM          # 0.6초
BAR = BEAT * 4           # 2.4초
SIXTEENTH = BEAT / 4     # 0.15초

# C - G - Am - F, 한 마디에 한 화음 (MIDI 음 번호)
CHORDS = [
    [60, 64, 67],  # C
    [59, 62, 67],  # G
    [57, 60, 64],  # Am
    [57, 60, 65],  # F
]
ROOTS = [36, 43, 45, 41]  # C2, G2, A2, F2

# 2마디 멜로디 (박 위치, 길이(박), MIDI) — C장조 펜타토닉 위주
MELODY = [
    (0.0, 1.0, 76), (1.0, 0.5, 79), (1.5, 0.5, 76), (2.0, 2.0, 74),
    (4.0, 1.0, 72), (5.0, 0.5, 74), (5.5, 0.5, 76), (6.0, 2.0, 79),
]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, start_s, sig):
    """sig를 buf의 start_s 위치에 더한다 (끝에서 잘림)."""
    i = int(round(start_s * SR))
    if i >= len(buf):
        return
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n]


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def adsr(n, attack, release, sr=SR):
    env = np.ones(n)
    a = min(n, int(attack * sr))
    r = min(n - a, int(release * sr))
    if a:
        env[:a] = np.linspace(0, 1, a)
    if r:
        env[n - r:] = np.linspace(1, 0, r)
    return env


# ---------- 악기 ----------

def pad(total):
    """부드러운 화음 패드: 사인 + 약한 배음, 살짝 어긋난 두 음으로 넓게."""
    buf = np.zeros(int(total * SR))
    n_bars = int(np.ceil(total / BAR))
    for b in range(n_bars):
        t = t_axis(BAR + 0.4)
        env = adsr(len(t), 0.35, 0.6)
        tone = np.zeros_like(t)
        for m in CHORDS[b % 4]:
            for cents in (-4, 4):
                f = midi_hz(m) * 2 ** (cents / 1200)
                tone += np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
        place(buf, b * BAR, tone * env / 6)
    return buf


def kick(total):
    """부드러운 킥: 120Hz -> 50Hz로 떨어지는 사인, 매 박."""
    buf = np.zeros(int(total * SR))
    t = t_axis(0.3)
    freq = 50 + 70 * np.exp(-t * 35)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    hit = np.sin(phase) * np.exp(-t * 14)
    for k in range(int(total / BEAT) + 1):
        place(buf, k * BEAT, hit)
    return buf


def bass(total):
    """통통 튀는 베이스: 정박에 근음, 뒷박에 한 옥타브 위."""
    buf = np.zeros(int(total * SR))
    for k in range(int(total / BEAT) + 1):
        root = ROOTS[int(k * BEAT // BAR) % 4]
        for off, m, dur in ((0.0, root, 0.4), (BEAT / 2, root + 12, 0.2)):
            t = t_axis(dur)
            f = midi_hz(m)
            tone = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)
            place(buf, k * BEAT + off, tone * np.exp(-t * 6) * adsr(len(t), 0.005, 0.03))
    return buf


def hihat(total, rng):
    """하이햇: 고음만 남긴 짧은 잡음, 뒷박(8분음표 '앤')마다."""
    buf = np.zeros(int(total * SR))
    t = t_axis(0.06)
    noise = rng.standard_normal(len(t))
    noise = noise - np.convolve(noise, np.ones(8) / 8, mode="same")  # 간단한 고역 통과
    hit = noise * np.exp(-t * 70)
    for k in range(int(total / BEAT) + 1):
        place(buf, k * BEAT + BEAT / 2, hit)
    return buf


def arp(total):
    """맑은 아르페지오: 화음 음을 한 옥타브 위에서 8분음표로 오르내림."""
    buf = np.zeros(int(total * SR))
    order = [0, 1, 2, 1]
    step = BEAT / 2
    for k in range(int(total / step) + 1):
        chord = CHORDS[int(k * step // BAR) % 4]
        m = chord[order[k % 4]] + 12
        t = t_axis(0.35)
        f = midi_hz(m)
        # 삼각파 느낌: 홀수 배음을 약하게
        tone = np.sin(2 * np.pi * f * t) + np.sin(6 * np.pi * f * t) / 9
        place(buf, k * step, tone * np.exp(-t * 11) * adsr(len(t), 0.003, 0.05))
    return buf


def bell(total):
    """벨(글로켄슈필) 멜로디: 비정수 배음으로 반짝이는 소리, 2마디 반복."""
    buf = np.zeros(int(total * SR))
    for rep in range(int(np.ceil(total / (BAR * 2)))):
        for beat, length, m in MELODY:
            t = t_axis(length * BEAT + 0.8)
            f = midi_hz(m)
            tone = (np.sin(2 * np.pi * f * t)
                    + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6)
                    + 0.12 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12))
            place(buf, rep * BAR * 2 + beat * BEAT, tone * np.exp(-t * 3.2) * adsr(len(t), 0.002, 0.1))
    return buf


def echo(x, delay_s=BEAT * 0.75, fb=0.3, taps=4):
    """공간감을 주는 간단한 메아리."""
    out = x.copy()
    d = int(delay_s * SR)
    for k in range(1, taps + 1):
        out[d * k:] += x[:-d * k] * fb ** k
    return out


# ---------- 믹스 ----------

def gate(total, start_s, ramp=0.03):
    """start_s부터 소리가 나도록 하는 문(짧게 페이드인)."""
    n = int(total * SR)
    g = np.zeros(n)
    i = int(round(start_s * SR))
    r = int(ramp * SR)
    if i < n:
        g[i:i + r] = np.linspace(0, 1, len(g[i:i + r]))
        g[i + r:] = 1
    return g


def quantize(t):
    """장면 전환 시점을 가장 가까운 16분음표에 맞춘다 (최대 0.075초 차이)."""
    return round(t / SIXTEENTH) * SIXTEENTH


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--length", type=float, default=30.0, help="전체 길이(초)")
    ap.add_argument("--scenes", default="0,5,10,15,20,25", help="장면 시작 시점(초), 쉼표로 구분")
    ap.add_argument("--fade", type=float, default=3.5, help="끝 페이드아웃 길이(초)")
    ap.add_argument("--out", default="assets/audio/bgm.wav")
    args = ap.parse_args()

    total = args.length
    scenes = [float(s) for s in args.scenes.split(",")]
    rng = np.random.default_rng(7)

    # (이름, 소리, 음량, 좌우 위치 -1=왼쪽 ~ 1=오른쪽)
    layers = [
        ("pad", echo(pad(total)), 0.20, 0.0),
        ("kick", kick(total), 0.55, 0.0),
        ("bass", bass(total), 0.30, 0.0),
        ("hihat", hihat(total, rng), 0.10, 0.35),
        ("arp", echo(arp(total)), 0.16, -0.35),
        ("bell", echo(bell(total)), 0.14, 0.3),
    ]

    n = int(total * SR)
    left = np.zeros(n)
    right = np.zeros(n)
    for idx, (name, sig, gain, pan) in enumerate(layers):
        if idx >= len(scenes):
            break  # 장면 수보다 악기가 많으면 남는 악기는 쓰지 않는다
        start = quantize(scenes[idx])
        s = sig[:n] * gain * gate(total, start)
        left += s * np.sqrt((1 - pan) / 2) * np.sqrt(2)
        right += s * np.sqrt((1 + pan) / 2) * np.sqrt(2)
        print(f"  {name:<6} 시작 {start:5.2f}s")

    # 끝: 코사인 곡선으로 서서히 작아짐
    fade_n = int(args.fade * SR)
    fade = 0.5 * (1 + np.cos(np.linspace(0, np.pi, fade_n)))
    for ch in (left, right):
        ch[n - fade_n:] *= fade
        ch[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))  # 첫 소리 '딱' 방지

    stereo = np.stack([left, right], axis=1)
    stereo = np.tanh(stereo * 1.2)                 # 부드러운 리미터
    stereo *= 0.89 / np.max(np.abs(stereo))        # 최대 약 -1 dBFS

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((stereo * 32767).astype("<i2").tobytes())
    print(f"저장: {out}  ({total:.1f}s, {BPM}BPM)")


if __name__ == "__main__":
    main()
