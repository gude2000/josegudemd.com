#!/usr/bin/env python3
"""
build_audio.py — synthesize two new audio assets:

  assets/audio/schumann-hum.mp3   — Earth Schumann modes brought into audible
                                     range (× 50). 45 s stereo drone.
  assets/audio/phi-vs-et-phi.mp3  — phi-tuned E/G♯/C chord (10 s)
  assets/audio/phi-vs-et-et.mp3   — 12-TET E/G♯/C chord  (10 s)

Run from repo root:
    python3 scripts/build_audio.py
"""
from __future__ import annotations
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import numpy as np

SR = 44100
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "audio"
OUT.mkdir(parents=True, exist_ok=True)


# ---------- helpers ----------
def fade_envelope(n, fade_s=1.0):
    """Symmetric raised-cosine fade in / fade out."""
    env = np.ones(n)
    fade_n = int(fade_s * SR)
    if 2 * fade_n >= n:
        fade_n = n // 3
    if fade_n <= 0:
        return env
    fade = 0.5 - 0.5 * np.cos(np.pi * np.arange(fade_n) / fade_n)
    env[:fade_n] = fade
    env[-fade_n:] = fade[::-1]
    return env


def write_wav(path: Path, stereo: np.ndarray):
    """stereo shape (n, 2), float64 in [-1, 1]."""
    import wave, struct
    # normalize headroom
    peak = float(np.max(np.abs(stereo)))
    if peak > 0:
        stereo = stereo * (0.95 / peak)
    interleaved = (stereo * 32767).astype(np.int16).flatten()
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(interleaved.tobytes())


def to_mp3(wav_path: Path, mp3_path: Path, bitrate="192k"):
    cmd = ["ffmpeg", "-y", "-loglevel", "error",
           "-i", str(wav_path), "-codec:a", "libmp3lame", "-b:a", bitrate,
           str(mp3_path)]
    subprocess.run(cmd, check=True)


# ---------- Schumann hum ----------
def build_schumann_hum():
    """Schumann modes at × 50 (so 7.83 Hz → 391.5 Hz). Five partials,
    each quieter than the previous; a 7.83 Hz amplitude modulation rides
    on the sum so the actual Schumann rhythm is heard as a slow pulse."""
    duration = 45.0
    n = int(duration * SR)
    t = np.arange(n) / SR

    SCHUMANN = [7.83, 14.3, 20.8, 27.3, 33.8]  # Earth-ionosphere modes (Hz)
    MULT = 50.0

    base = np.zeros(n)
    amps = [1.0, 0.55, 0.32, 0.20, 0.12]
    # Slight detune between L and R for stereo width
    for i, (f, a) in enumerate(zip(SCHUMANN, amps)):
        # tiny per-mode phase offset so the sine partials don't all line up
        phase = (i * 0.31) * 2 * np.pi
        base += a * np.sin(2 * np.pi * (f * MULT) * t + phase)

    # 7.83 Hz amplitude modulation — let the listener hear the actual cavity rhythm
    am = 1.0 + 0.18 * np.sin(2 * np.pi * SCHUMANN[0] * t)
    signal = base * am

    # Subtle low-pass shelf — soften the upper partials a touch
    # (cheap 1-pole IIR low-pass)
    def lowpass(x, fc=2500.0):
        rc = 1.0 / (2 * math.pi * fc)
        dt = 1.0 / SR
        alpha = dt / (rc + dt)
        y = np.empty_like(x)
        y[0] = x[0] * alpha
        for i in range(1, len(x)):
            y[i] = y[i-1] + alpha * (x[i] - y[i-1])
        return y
    signal = lowpass(signal, 2800.0)

    env = fade_envelope(n, fade_s=2.5)

    # Stereo: left/right detune ~0.5 Hz on the fundamental for slow chorus
    left = signal * env
    # Build a right channel with a slightly detuned fundamental
    right_base = np.zeros(n)
    for i, (f, a) in enumerate(zip(SCHUMANN, amps)):
        phase = (i * 0.47) * 2 * np.pi
        detune = 1.0 + 0.0015 * (i + 1)  # slightly different detune per partial
        right_base += a * np.sin(2 * np.pi * (f * MULT * detune) * t + phase)
    right_am = 1.0 + 0.18 * np.sin(2 * np.pi * SCHUMANN[0] * t + 0.5)
    right = lowpass(right_base * right_am, 2800.0) * env

    stereo = np.stack([left, right], axis=1)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = Path(f.name)
    try:
        write_wav(wav, stereo)
        to_mp3(wav, OUT / "schumann-hum.mp3")
    finally:
        wav.unlink(missing_ok=True)
    print(f"  wrote {OUT / 'schumann-hum.mp3'}")


# ---------- Phi vs ET A/B ----------
def build_phi_vs_et():
    """Two ~10 s loops of the same three pitches (E / G♯ / C), one in
    12-TET, one in φ-ratios. Sine waves, gentle envelope, no panning so
    the difference is purely tuning-based."""
    duration = 10.0
    n = int(duration * SR)
    t = np.arange(n) / SR

    # phi-tuned
    F_E = 164.81
    F_GS_PHI = 209.64
    F_C_PHI  = 266.67

    # 12-TET, anchored at the same E so the comparison is fair
    F_GS_ET = F_E * 2 ** (4 / 12)   # ≈ 207.65 Hz
    F_C_ET  = F_E * 2 ** (8 / 12)   # ≈ 261.63 Hz

    env = fade_envelope(n, fade_s=0.6)

    def chord(freqs):
        sig = np.zeros(n)
        for f in freqs:
            sig += np.sin(2 * np.pi * f * t)
        sig = sig / len(freqs)
        return sig * env

    for name, fs in [
        ("phi-vs-et-phi", [F_E, F_GS_PHI, F_C_PHI]),
        ("phi-vs-et-et",  [F_E, F_GS_ET,  F_C_ET]),
    ]:
        sig = chord(fs)
        stereo = np.stack([sig, sig], axis=1)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav = Path(f.name)
        try:
            write_wav(wav, stereo)
            to_mp3(wav, OUT / f"{name}.mp3")
        finally:
            wav.unlink(missing_ok=True)
        print(f"  wrote {OUT / (name + '.mp3')}  (freqs: {[round(f,2) for f in fs]} Hz)")


# ---------- main ----------
if __name__ == "__main__":
    if shutil.which("ffmpeg") is None:
        print("ffmpeg not on PATH — install it first.", file=sys.stderr)
        sys.exit(1)
    print("Schumann hum…")
    build_schumann_hum()
    print("Phi vs equal-temperament A/B…")
    build_phi_vs_et()
    print("done.")
