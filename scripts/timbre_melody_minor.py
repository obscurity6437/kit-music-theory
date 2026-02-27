"""
Session 3: Timbre, Melody-Memory, and Minor vs Major
2026-02-25

Three explorations:
1. How instrument timbre changes effective consonance (violin vs clarinet vs flute)
2. Melody as "remembered interference" — how sequential notes create virtual harmony
3. Why minor feels different from major mathematically (LCM 30 vs 20)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path

VIZ_DIR = Path(__file__).parent.parent / "visualizations"
VIZ_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# INSTRUMENT TIMBRE MODELS
# Each instrument = dict of {harmonic_number: relative_amplitude}
# Based on measured spectral data from acoustic physics literature
# ─────────────────────────────────────────────────────────────────────────────

def build_timbre(profile: str, n_harmonics: int = 16) -> np.ndarray:
    """Return amplitude array for harmonics 1..n_harmonics"""
    amps = np.zeros(n_harmonics + 1)  # index 0 unused
    
    if profile == "pure_sine":
        amps[1] = 1.0
    
    elif profile == "violin":
        # Rich spectrum, strong lower harmonics, gradual falloff
        # Bowed strings: all harmonics, lower ones dominate
        for n in range(1, n_harmonics + 1):
            amps[n] = 1.0 / (n ** 0.7)
        # Violin has a prominent 2nd harmonic (wolf note region)
        amps[2] *= 1.3
    
    elif profile == "clarinet":
        # Cylindrical bore → strong ODD harmonics, weak even
        # Classic clarinet timbre: 1st, 3rd, 5th, 7th...
        for n in range(1, n_harmonics + 1):
            if n % 2 == 1:  # odd harmonics
                amps[n] = 1.0 / n
            else:  # even harmonics suppressed (~20% amplitude)
                amps[n] = 0.05 / n
    
    elif profile == "flute":
        # Open cylindrical bore, nearly sine-wave
        # Very strong fundamental, weak upper harmonics
        amps[1] = 1.0
        amps[2] = 0.4
        amps[3] = 0.1
        amps[4] = 0.05
        for n in range(5, n_harmonics + 1):
            amps[n] = 0.02 / n
    
    elif profile == "trumpet":
        # Brass with mouthpiece: very rich, all harmonics, cup shape
        # Strong 2nd, 3rd, 4th harmonics — brighter timbre
        for n in range(1, n_harmonics + 1):
            amps[n] = 1.0 / (n ** 0.5)
        amps[1] = 0.7  # fundamental slightly softer relative to harmonics
        amps[2] *= 1.5
        amps[3] *= 1.4
    
    elif profile == "piano":
        # Struck string: inharmonic, but model as approximately harmonic
        # Decays with characteristic 1/n^1.5 envelope
        for n in range(1, n_harmonics + 1):
            amps[n] = 1.0 / (n ** 1.5)
        amps[1] = 1.0
        amps[2] = 0.6
    
    # Normalize to unit max
    amps /= max(amps[1:])
    return amps


def weighted_harmonic_overlap(ratio_p: int, ratio_q: int, timbre_A: np.ndarray,
                               timbre_B: np.ndarray, n_harmonics: int = 16) -> float:
    """
    Compute consonance score for two notes with ratio p:q, using instrument timbres.
    Score = sum of product of amplitudes at each shared harmonic frequency.
    
    A harmonic of note_A at frequency k*f_A aligns with harmonic of note_B at m*f_B
    when k * p = m * q  →  k/m = q/p.
    """
    f_A = ratio_p  # note A at frequency ratio_p (normalized)
    f_B = ratio_q  # note B at frequency ratio_q
    
    overlap_score = 0.0
    
    # Find frequencies where harmonics coincide
    # Harmonic k of A is at k*f_A; harmonic m of B is at m*f_B
    # They coincide when k*f_A = m*f_B → k/m = f_B/f_A = q/p
    # So k = q*t, m = p*t for t = 1, 2, 3...
    
    t = 1
    while True:
        k = ratio_q * t  # harmonic index of A
        m = ratio_p * t  # harmonic index of B
        if k > n_harmonics and m > n_harmonics:
            break
        if k <= n_harmonics and m <= n_harmonics:
            overlap_score += timbre_A[k] * timbre_B[m]
        t += 1
    
    return overlap_score


def plot_timbre_consonance():
    """
    Compare consonance scores across intervals for 5 instrument timbres.
    Shows how timbre shapes the consonance landscape.
    """
    instruments = ["pure_sine", "flute", "violin", "piano", "clarinet", "trumpet"]
    colors = ["#888888", "#4FC3F7", "#E57373", "#FFB74D", "#81C784", "#CE93D8"]
    labels = ["Pure Sine", "Flute", "Violin", "Piano", "Clarinet", "Trumpet"]
    n_harmonics = 24
    
    # Intervals to analyze (p:q ratios, p >= q, i.e. the upper note is p/q * lower)
    intervals = [
        ("Unison\n1:1",       1, 1,   0),
        ("Octave\n2:1",       2, 1,   12),
        ("Fifth\n3:2",        3, 2,   7),
        ("Fourth\n4:3",       4, 3,   5),
        ("Maj 3rd\n5:4",      5, 4,   4),
        ("Min 3rd\n6:5",      6, 5,   3),
        ("Maj 2nd\n9:8",      9, 8,   2),
        ("Min 2nd\n16:15",    16, 15, 1),
        ("Tritone\n45:32",    45, 32, 6),
    ]
    
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("Timbre Effects on Consonance: How Instrument Character Reshapes Harmony",
                 fontsize=14, fontweight="bold", y=0.98)
    
    all_scores = {inst: [] for inst in instruments}
    interval_names = [iv[0] for iv in intervals]
    x = np.arange(len(intervals))
    
    for inst in instruments:
        timbre = build_timbre(inst, n_harmonics)
        for _, p, q, _ in intervals:
            score = weighted_harmonic_overlap(p, q, timbre, timbre, n_harmonics)
            all_scores[inst].append(score)
    
    for idx, (inst, color, label) in enumerate(zip(instruments, colors, labels)):
        ax = axes[idx // 3][idx % 3]
        scores = all_scores[inst]
        bars = ax.bar(x, scores, color=color, alpha=0.8, edgecolor="white", linewidth=0.5)
        ax.set_title(label, fontsize=11, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(interval_names, fontsize=7)
        ax.set_ylabel("Overlap Score", fontsize=8)
        ax.set_ylim(0, max(max(all_scores[i]) for i in instruments) * 1.15)
        ax.grid(axis="y", alpha=0.3)
        
        # Annotate the top bar
        max_idx = np.argmax(scores)
        ax.annotate(f"max", xy=(max_idx, scores[max_idx]),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", fontsize=7, color="darkred")
    
    plt.tight_layout()
    path = VIZ_DIR / "timbre_consonance.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ timbre_consonance.png")
    return all_scores, instruments, labels


def plot_clarinet_detail():
    """
    Deep dive: clarinet's odd-harmonic suppression.
    Harmonic spectrum comparison and how it affects interval consonance.
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle("Clarinet's Odd-Harmonic Timbre and Its Consonance Consequences",
                 fontsize=13, fontweight="bold")
    
    n_harmonics = 16
    x = np.arange(1, n_harmonics + 1)
    
    # Panel 1: Harmonic spectra
    ax = axes[0]
    violin_amps = build_timbre("violin", n_harmonics)[1:]
    clarinet_amps = build_timbre("clarinet", n_harmonics)[1:]
    
    width = 0.35
    ax.bar(x - width/2, violin_amps, width, label="Violin", color="#E57373", alpha=0.8)
    ax.bar(x + width/2, clarinet_amps, width, label="Clarinet", color="#81C784", alpha=0.8)
    
    # Mark odd harmonics
    for n in x:
        if n % 2 == 1:
            ax.axvline(n, color="gray", alpha=0.2, linewidth=8)
    
    ax.set_xlabel("Harmonic Number")
    ax.set_ylabel("Relative Amplitude")
    ax.set_title("Harmonic Spectra\n(gray = odd harmonics)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    
    # Panel 2: Interval scores for violin vs clarinet
    ax = axes[1]
    intervals_short = [
        ("Oct", 2, 1),
        ("5th", 3, 2),
        ("4th", 4, 3),
        ("M3", 5, 4),
        ("m3", 6, 5),
        ("M2", 9, 8),
        ("m2", 16, 15),
        ("TT", 45, 32),
    ]
    
    violin_t = build_timbre("violin", n_harmonics)
    clarinet_t = build_timbre("clarinet", n_harmonics)
    
    v_scores = [weighted_harmonic_overlap(p, q, violin_t, violin_t, n_harmonics) for _, p, q in intervals_short]
    c_scores = [weighted_harmonic_overlap(p, q, clarinet_t, clarinet_t, n_harmonics) for _, p, q in intervals_short]
    
    x2 = np.arange(len(intervals_short))
    ax.bar(x2 - width/2, v_scores, width, label="Violin", color="#E57373", alpha=0.8)
    ax.bar(x2 + width/2, c_scores, width, label="Clarinet", color="#81C784", alpha=0.8)
    ax.set_xticks(x2)
    ax.set_xticklabels([i[0] for i in intervals_short])
    ax.set_ylabel("Overlap Score")
    ax.set_title("Consonance Scores by Interval\n(same two clarinets vs same two violins)")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    
    # Panel 3: Clarinet playing a fifth — odd harmonic coincidence
    ax = axes[2]
    # Clarinet playing C and G (3:2). 
    # Odd harmonics of C: 1f, 3f, 5f, 7f... (f = fundamental)
    # Odd harmonics of G: 1*(3/2)f, 3*(3/2)f, 5*(3/2)f... = 3/2, 9/2, 15/2...
    # Coincidences: 3f (C, 3rd harmonic) = 2*(3/2)f = NOT odd harmonic of G
    #              6f (C, but even → suppressed) 
    # Clarinet fifth is "hollower" because the even harmonics that would overlap are suppressed
    
    freqs = np.linspace(0, 18, 1000)
    
    def spectrum(fundamental, timbre_arr, freqs):
        power = np.zeros_like(freqs)
        for n in range(1, len(timbre_arr)):
            freq = n * fundamental
            # Delta function approximated by narrow Gaussian
            power += timbre_arr[n] * np.exp(-((freqs - freq)**2) / (0.02**2))
        return power
    
    c_spec = spectrum(1.0, build_timbre("clarinet", 16), freqs)
    g_spec = spectrum(1.5, build_timbre("clarinet", 16), freqs)
    overlap = np.minimum(c_spec, g_spec) * 2
    
    ax.fill_between(freqs, c_spec, alpha=0.4, color="#81C784", label="Clarinet C")
    ax.fill_between(freqs, g_spec, alpha=0.4, color="#4FC3F7", label="Clarinet G (×3/2)")
    ax.fill_between(freqs, overlap, color="purple", alpha=0.7, label="Overlap")
    ax.set_xlabel("Frequency (multiples of C fundamental)")
    ax.set_ylabel("Spectral Power")
    ax.set_title("Clarinet Fifth (3:2): Spectral Overlap\n(odd harmonics only → fewer overlaps)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    ax.set_xlim(0, 16)
    
    plt.tight_layout()
    path = VIZ_DIR / "clarinet_detail.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ clarinet_detail.png")


# ─────────────────────────────────────────────────────────────────────────────
# MELODY AS REMEMBERED INTERFERENCE
# ─────────────────────────────────────────────────────────────────────────────

def melody_memory_waveform(note_freq: float, memory_freq: float, decay: float,
                            t: np.ndarray) -> np.ndarray:
    """
    Model: brain hears new note at note_freq.
    Previous note (memory_freq) is still "active" with exponential amplitude decay.
    Combined signal = live_note + decayed_memory.
    """
    live = np.sin(2 * np.pi * note_freq * t)
    memory = np.exp(-decay * t) * np.sin(2 * np.pi * memory_freq * t)
    return live, memory, live + memory


def plot_melody_memory():
    """
    Visualize how sequential notes create virtual interference.
    Shows: C→G (consonant), C→E (major third), C→F# (tritone tension).
    """
    fig = plt.figure(figsize=(16, 11))
    fig.suptitle("Melody as Remembered Interference\nHow Sequential Notes Create Virtual Harmony",
                 fontsize=14, fontweight="bold")
    
    # Three melodic steps to analyze
    sequences = [
        {
            "name": "C → G (Perfect Fifth)",
            "ratio": "3:2",
            "lcm": 6,
            "note1_freq": 1.0,
            "note2_freq": 1.5,
            "color": "#4CAF50",
            "feel": "Consonant — familiar, resolved"
        },
        {
            "name": "C → E (Major Third)",
            "ratio": "5:4",
            "lcm": 20,
            "note1_freq": 1.0,
            "note2_freq": 1.25,
            "color": "#2196F3",
            "feel": "Warm — slightly complex, open"
        },
        {
            "name": "C → F# (Tritone)",
            "ratio": "45:32",
            "lcm": 1440,
            "note1_freq": 1.0,
            "note2_freq": 1.4062,  # 45/32
            "color": "#F44336",
            "feel": "Dissonant — unresolved, wants movement"
        },
    ]
    
    t_display = np.linspace(0, 8, 4000)   # 8 "cycles" of fundamental
    decay = 0.3  # memory decay constant
    
    for seq_idx, seq in enumerate(sequences):
        row = seq_idx
        
        # Panel A: Live + memory waveforms separately
        ax1 = fig.add_subplot(3, 3, row * 3 + 1)
        live, mem, combined = melody_memory_waveform(
            seq["note2_freq"], seq["note1_freq"], decay, t_display)
        
        ax1.plot(t_display, live, color=seq["color"], alpha=0.9, linewidth=1.2, label="Current note")
        ax1.plot(t_display, mem, color="gray", alpha=0.6, linewidth=1.0, linestyle="--", label="Remembered note")
        ax1.set_title(f"{seq['name']}\nRatio {seq['ratio']}, LCM period = {seq['lcm']}", fontsize=9)
        ax1.set_ylabel("Amplitude")
        ax1.set_ylim(-2.2, 2.2)
        ax1.legend(fontsize=7)
        ax1.grid(alpha=0.2)
        if row == 2:
            ax1.set_xlabel("Time (cycles)")
        
        # Panel B: Combined interference
        ax2 = fig.add_subplot(3, 3, row * 3 + 2)
        ax2.fill_between(t_display, combined, alpha=0.3, color=seq["color"])
        ax2.plot(t_display, combined, color=seq["color"], linewidth=1.0)
        ax2.axhline(0, color="black", linewidth=0.5)
        
        # Mark peaks/nodes to show pattern regularity
        # Find zero crossings as rough periodicity measure
        zero_crossings = np.where(np.diff(np.sign(combined)))[0]
        if len(zero_crossings) > 2:
            intervals_zc = np.diff(t_display[zero_crossings])
            pattern_regularity = 1.0 / (np.std(intervals_zc) + 0.001)
        else:
            pattern_regularity = 0
        
        ax2.set_title(f"Combined Waveform\nPattern regularity: {pattern_regularity:.1f}", fontsize=9)
        ax2.set_ylabel("Combined amplitude")
        ax2.set_ylim(-2.2, 2.2)
        ax2.grid(alpha=0.2)
        if row == 2:
            ax2.set_xlabel("Time (cycles)")
        
        # Panel C: Lissajous (phase portrait) — live vs memory
        ax3 = fig.add_subplot(3, 3, row * 3 + 3)
        t_phase = np.linspace(0, 20, 5000)  # longer for phase portrait
        live_p = np.sin(2 * np.pi * seq["note2_freq"] * t_phase)
        mem_p  = np.sin(2 * np.pi * seq["note1_freq"] * t_phase)
        
        # Color by time to show trajectory
        points = np.array([live_p, mem_p]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        from matplotlib.collections import LineCollection
        from matplotlib.colors import Normalize
        norm = Normalize(0, len(segments))
        lc = LineCollection(segments, cmap="viridis", norm=norm, linewidth=0.5, alpha=0.8)
        lc.set_array(np.arange(len(segments)))
        ax3.add_collection(lc)
        
        ax3.set_xlim(-1.2, 1.2)
        ax3.set_ylim(-1.2, 1.2)
        ax3.set_aspect("equal")
        ax3.set_title(f"Lissajous Phase Portrait\n\"{seq['feel']}\"", fontsize=9)
        ax3.set_xlabel("Current note")
        ax3.set_ylabel("Remembered note")
        ax3.grid(alpha=0.2)
    
    plt.tight_layout()
    path = VIZ_DIR / "melody_memory.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ melody_memory.png")


def plot_melodic_tension_arc():
    """
    Model a simple melodic phrase and show the running "tension" level
    as the brain accumulates and releases remembered interference.
    Phrase: C - E - G - F# - G - E - C  (classic tension → release arc)
    """
    # Frequency ratios relative to C=1.0
    notes = {
        "C": 1.0,
        "D": 9/8,
        "E": 5/4,
        "F": 4/3,
        "F#": 45/32,
        "G": 3/2,
        "A": 5/3,
        "B": 15/8,
        "C'": 2.0,
    }
    
    # Tension = complexity of current note vs "tonal center" C
    def tension(note_freq, tonic=1.0):
        """
        Approximate tension as log of LCM of the ratio to tonic.
        Clamp the ratio to nearest simple fraction first.
        """
        ratio = note_freq / tonic
        # Find nearest simple fraction
        frac = Fraction(ratio).limit_denominator(64)
        p, q = frac.numerator, frac.denominator
        l = lcm(p, q)
        return np.log2(l + 1)  # +1 to avoid log(0); log scale feels right
    
    # Two phrases to compare
    phrase_1 = ["C", "E", "G", "F#", "G", "E", "C"]
    phrase_2 = ["C", "D", "E", "F", "G", "A", "B", "C'"]
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 9))
    fig.suptitle("Melodic Tension Arc: How Sequential Notes Accumulate Tension",
                 fontsize=13, fontweight="bold")
    
    for phrase_idx, (phrase, phrase_name) in enumerate([
        (phrase_1, "Dramatic arc: C–E–G–F#–G–E–C\n(approach + resolution)"),
        (phrase_2, "Scale ascent: C–D–E–F–G–A–B–C'\n(gradual tension build)")
    ]):
        freqs = [notes[n] for n in phrase]
        tensions = [tension(f) for f in freqs]
        
        # Accumulated tension: memory of previous note bleeds into current
        decay = 0.6
        accumulated = []
        for i, t_val in enumerate(tensions):
            if i == 0:
                accumulated.append(t_val)
            else:
                # Previous tension decays and adds to current
                prev_decay = accumulated[-1] * decay
                # Interaction tension = distance from prev note to current
                interval_ratio = freqs[i] / freqs[i-1]
                frac = Fraction(interval_ratio).limit_denominator(64)
                p, q = frac.numerator, frac.denominator
                step_tension = np.log2(lcm(p, q) + 1)
                accumulated.append(t_val + step_tension * 0.4 + prev_decay * 0.3)
        
        # Plot 1: Note-by-note tension
        ax = axes[phrase_idx][0]
        colors_bar = plt.cm.RdYlGn_r(np.array(tensions) / max(tensions))
        bars = ax.bar(range(len(phrase)), tensions, color=colors_bar, edgecolor="white")
        ax.set_xticks(range(len(phrase)))
        ax.set_xticklabels(phrase, fontsize=10)
        ax.set_ylabel("Tension (log LCM vs tonic C)")
        ax.set_title(phrase_name, fontsize=9)
        ax.grid(axis="y", alpha=0.3)
        
        # Annotate
        for i, (t_val, note) in enumerate(zip(tensions, phrase)):
            ax.text(i, t_val + 0.02, f"{t_val:.2f}", ha="center", fontsize=8)
        
        # Plot 2: Accumulated tension over phrase
        ax2 = axes[phrase_idx][1]
        x_phrase = range(len(phrase))
        ax2.fill_between(x_phrase, accumulated, alpha=0.3,
                         color="#F44336" if phrase_idx == 0 else "#2196F3")
        ax2.plot(x_phrase, accumulated, "o-",
                 color="#F44336" if phrase_idx == 0 else "#2196F3",
                 linewidth=2, markersize=8)
        ax2.set_xticks(x_phrase)
        ax2.set_xticklabels(phrase, fontsize=10)
        ax2.set_ylabel("Accumulated tension")
        ax2.set_title("Cumulative tension with memory decay", fontsize=9)
        ax2.grid(alpha=0.3)
        
        # Mark the peak tension
        peak_idx = np.argmax(accumulated)
        ax2.annotate(f"Peak!\n{phrase[peak_idx]}",
                     xy=(peak_idx, accumulated[peak_idx]),
                     xytext=(peak_idx + 0.3, accumulated[peak_idx] + 0.1),
                     arrowprops=dict(arrowstyle="->", color="red"),
                     fontsize=8, color="red")
    
    plt.tight_layout()
    path = VIZ_DIR / "melodic_tension_arc.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ melodic_tension_arc.png")


# ─────────────────────────────────────────────────────────────────────────────
# MINOR VS MAJOR: MATHEMATICAL DEEP DIVE
# ─────────────────────────────────────────────────────────────────────────────

def triad_complexity(root, third, fifth):
    """
    Analyze the complexity of a triad.
    All three intervals interact: root-third, root-fifth, third-fifth.
    Returns dict of analysis metrics.
    """
    # Convert to Fraction for exact arithmetic
    r = Fraction(root).limit_denominator(100)
    t = Fraction(third).limit_denominator(100)
    f = Fraction(fifth).limit_denominator(100)
    
    # The three intervals
    rt_frac = t / r  # root to third
    rf_frac = f / r  # root to fifth
    tf_frac = f / t  # third to fifth
    
    def interval_lcm(frac):
        p, q = frac.numerator, frac.denominator
        return lcm(p, q)
    
    rt_lcm = interval_lcm(rt_frac)
    rf_lcm = interval_lcm(rf_frac)
    tf_lcm = interval_lcm(tf_frac)
    
    # Total triad complexity = product (not sum) — all three must "resolve" together
    total_lcm = lcm(lcm(rt_lcm, rf_lcm), tf_lcm)
    
    return {
        "root_third_lcm": rt_lcm,
        "root_fifth_lcm": rf_lcm,
        "third_fifth_lcm": tf_lcm,
        "total_lcm": total_lcm,
        "root_third": str(rt_frac),
        "root_fifth": str(rf_frac),
        "third_fifth": str(tf_frac),
    }


def plot_minor_vs_major():
    """
    Compare major and minor triads mathematically.
    Show why minor ≠ just a lower-LCM version of major.
    """
    # Major triad: root=1, major third (5:4), perfect fifth (3:2)
    major = triad_complexity(1, 5/4, 3/2)
    # Minor triad: root=1, minor third (6:5), perfect fifth (3:2)
    minor = triad_complexity(1, 6/5, 3/2)
    
    # Also: diminished (minor third + diminished fifth 45/32) and augmented
    dim   = triad_complexity(1, 6/5, 45/32)
    aug   = triad_complexity(1, 5/4, 8/5)   # augmented fifth = 8/5
    
    print("\n=== TRIAD COMPLEXITY ANALYSIS ===")
    for name, data in [("Major", major), ("Minor", minor), ("Diminished", dim), ("Augmented", aug)]:
        print(f"\n{name} triad:")
        print(f"  Root→Third  ({data['root_third']}): LCM = {data['root_third_lcm']}")
        print(f"  Root→Fifth  ({data['root_fifth']}): LCM = {data['root_fifth_lcm']}")
        print(f"  Third→Fifth ({data['third_fifth']}): LCM = {data['third_fifth_lcm']}")
        print(f"  Total LCM:  {data['total_lcm']}")
    
    fig = plt.figure(figsize=(16, 12))
    fig.suptitle("Minor vs Major: The Mathematics of Emotional Character",
                 fontsize=14, fontweight="bold")
    
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)
    
    # ── Panel 1: Interval LCMs for all four triads ─────────────────────────
    ax1 = fig.add_subplot(gs[0, :2])
    
    triads_data = [
        ("Major\n(1 : 5/4 : 3/2)", major, "#4CAF50"),
        ("Minor\n(1 : 6/5 : 3/2)", minor, "#2196F3"),
        ("Diminished\n(1 : 6/5 : 45/32)", dim, "#F44336"),
        ("Augmented\n(1 : 5/4 : 8/5)", aug, "#FF9800"),
    ]
    
    interval_labels = ["Root→3rd", "Root→5th", "3rd→5th"]
    x = np.arange(4)
    width = 0.25
    
    for i, label in enumerate(interval_labels):
        vals = []
        for _, data, _ in triads_data:
            key = ["root_third_lcm", "root_fifth_lcm", "third_fifth_lcm"][i]
            vals.append(data[key])
        ax1.bar(x + i * width, vals, width, 
               label=label, alpha=0.8,
               color=["#80CBC4", "#FFE082", "#EF9A9A"][i])
    
    ax1.set_xticks(x + width)
    ax1.set_xticklabels([t[0] for t in triads_data], fontsize=9)
    ax1.set_ylabel("LCM Period")
    ax1.set_title("Pairwise Interval Complexity Within Each Triad", fontsize=10)
    ax1.legend()
    ax1.set_yscale("log")
    ax1.grid(axis="y", alpha=0.3)
    ax1.annotate("Log scale!", xy=(0.02, 0.95), xycoords="axes fraction", fontsize=7, color="gray")
    
    # ── Panel 2: Total triad LCM comparison ────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 2])
    total_lcms = [data["total_lcm"] for _, data, _ in triads_data]
    colors_triads = [c for _, _, c in triads_data]
    bars = ax2.bar([t[0].split("\n")[0] for t in triads_data], total_lcms,
                   color=colors_triads, alpha=0.8, edgecolor="white")
    ax2.set_ylabel("Total LCM (log scale)")
    ax2.set_title("Total Triad\nComplexity", fontsize=10)
    ax2.set_yscale("log")
    ax2.grid(axis="y", alpha=0.3)
    for bar, val in zip(bars, total_lcms):
        ax2.text(bar.get_x() + bar.get_width()/2, val * 1.1, str(val),
                ha="center", va="bottom", fontsize=8, fontweight="bold")
    
    # ── Panel 3: Waveforms — C major vs C minor triad ──────────────────────
    t = np.linspace(0, 12, 8000)
    
    def triad_wave(root_f, third_f, fifth_f, t):
        return (np.sin(2*np.pi*root_f*t) + 
                np.sin(2*np.pi*third_f*t) * 0.8 + 
                np.sin(2*np.pi*fifth_f*t) * 0.6)
    
    major_wave = triad_wave(1.0, 1.25, 1.5, t)
    minor_wave = triad_wave(1.0, 1.2, 1.5, t)  # 6/5 = 1.2
    
    ax3 = fig.add_subplot(gs[1, :])
    ax3.plot(t, major_wave, color="#4CAF50", alpha=0.8, linewidth=0.8,
             label="Major triad (1 : 5/4 : 3/2)")
    ax3.plot(t, minor_wave - 3.5, color="#2196F3", alpha=0.8, linewidth=0.8,
             label="Minor triad (1 : 6/5 : 3/2)  [offset −3.5]")
    
    # Mark repeating periods
    # Major: LCM(20, 6, ...) = we need to compute
    # For visual, the combined wave should repeat at some period
    # Mark every 20 cycles as approximate major period
    for period_t in np.arange(20, 13, -20):  # show one major period
        ax3.axvline(period_t, color="#4CAF50", alpha=0.4, linestyle=":")
    
    ax3.axhline(-1.75, color="gray", alpha=0.2, linewidth=0.5)
    ax3.set_title("Combined Waveforms: Major vs Minor Triad\n(Minor third is 6/5 ≈ 1.2 vs major third 5/4 = 1.25 — just 50¢ different, yet perceptually worlds apart)",
                  fontsize=9)
    ax3.legend(loc="upper right", fontsize=9)
    ax3.set_xlabel("Time (cycles of root)")
    ax3.grid(alpha=0.2)
    ax3.set_xlim(0, 12)
    
    # ── Panel 4: The 50-cent question — interval distance vs LCM complexity ─
    ax4 = fig.add_subplot(gs[2, :2])
    
    # Map from ratio to cents and LCM
    def cents(ratio):
        return 1200 * np.log2(ratio)
    
    # Survey of ratios from 1.0 to 2.0 — what's their LCM complexity?
    test_ratios = []
    test_lcms = []
    test_cents_vals = []
    
    for p in range(1, 50):
        for q in range(1, 50):
            if gcd(p, q) == 1 and 1 < p/q <= 2:
                test_ratios.append(p/q)
                test_lcms.append(lcm(p, q))
                test_cents_vals.append(cents(p/q))
    
    # Sort by cents
    sorted_idx = np.argsort(test_cents_vals)
    sorted_cents = [test_cents_vals[i] for i in sorted_idx]
    sorted_lcms  = [test_lcms[i] for i in sorted_idx]
    
    ax4.scatter(sorted_cents, sorted_lcms, c=sorted_lcms, cmap="RdYlGn_r",
                s=30, alpha=0.7, norm=plt.Normalize(0, 200))
    
    # Highlight major and minor thirds
    maj3_cents = cents(5/4)
    min3_cents = cents(6/5)
    
    ax4.annotate("Major 3rd\n5:4 (386¢)\nLCM=20",
                 xy=(maj3_cents, 20), xytext=(maj3_cents + 30, 40),
                 arrowprops=dict(arrowstyle="->", color="#4CAF50"),
                 color="#4CAF50", fontsize=8, fontweight="bold")
    ax4.annotate("Minor 3rd\n6:5 (316¢)\nLCM=30",
                 xy=(min3_cents, 30), xytext=(min3_cents - 100, 55),
                 arrowprops=dict(arrowstyle="->", color="#2196F3"),
                 color="#2196F3", fontsize=8, fontweight="bold")
    
    ax4.set_xlabel("Interval size (cents — 1200¢ = octave)")
    ax4.set_ylabel("LCM complexity")
    ax4.set_title("The Complexity Landscape: Every Simple Ratio Between Unison and Octave\n70¢ difference in pitch → 50% difference in LCM → noticeable perceptual shift",
                  fontsize=9)
    ax4.set_ylim(0, 250)
    ax4.set_xlim(0, 1250)
    ax4.grid(alpha=0.3)
    
    # Add cent markers for key intervals
    for name, ratio in [("5th", 3/2), ("4th", 4/3), ("Oct", 2/1), ("M6", 5/3), ("m6", 8/5)]:
        c = cents(ratio)
        ax4.axvline(c, color="gray", alpha=0.3, linestyle="--")
        ax4.text(c, 220, name, ha="center", fontsize=7, color="gray")
    
    # ── Panel 5: Minor third as "compound" interval ─────────────────────────
    ax5 = fig.add_subplot(gs[2, 2])
    
    # Show: minor third 6:5 can be heard as (octave 2:1) relative to (minor sixth 8:5)
    # The key insight: minor third has ratio 6:5, which in the harmonic series appears
    # at positions 5 and 6 — higher up than major third (4, 5)
    
    harmonic_series = list(range(1, 17))
    positions_major3 = [4, 5]  # 5:4 appears between harmonics 4 and 5
    positions_minor3 = [5, 6]  # 6:5 appears between harmonics 5 and 6
    
    bar_colors = []
    for h in harmonic_series:
        if h in positions_major3:
            bar_colors.append("#4CAF50")
        elif h in positions_minor3:
            bar_colors.append("#2196F3")
        else:
            bar_colors.append("#BBDEFB")
    
    ax5.bar(harmonic_series, [1/h for h in harmonic_series],
            color=bar_colors, edgecolor="white", linewidth=0.5)
    
    # Annotations
    ax5.annotate("Major 3rd\n(4→5)", xy=(4.5, 1/4.5),
                 xytext=(6, 0.28), arrowprops=dict(arrowstyle="->", color="#4CAF50"),
                 color="#4CAF50", fontsize=8)
    ax5.annotate("Minor 3rd\n(5→6)", xy=(5.5, 1/5.5),
                 xytext=(8, 0.20), arrowprops=dict(arrowstyle="->", color="#2196F3"),
                 color="#2196F3", fontsize=8)
    
    ax5.set_xlabel("Harmonic number")
    ax5.set_ylabel("Amplitude (1/n)")
    ax5.set_title("Position in Harmonic Series\nMinor 3rd = one step higher up = weaker", fontsize=9)
    ax5.grid(axis="y", alpha=0.3)
    
    path = VIZ_DIR / "minor_vs_major.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ minor_vs_major.png")
    
    return major, minor, dim, aug


# ─────────────────────────────────────────────────────────────────────────────
# BONUS: The Difference Between Melody and Harmony — Information Rates
# ─────────────────────────────────────────────────────────────────────────────

def plot_information_density():
    """
    Chord vs melody: same notes, different information density.
    Shows why harmonies can be "richer" even with same pitch content.
    """
    # C major chord vs C-E-G melody at same tempo
    t_harm = np.linspace(0, 8, 4000)
    t_step = 8/3  # each note lasts 8/3 time units
    
    # Harmonic version: all three at once
    harmony = (np.sin(2*np.pi*1.0*t_harm) + 
               np.sin(2*np.pi*1.25*t_harm) + 
               np.sin(2*np.pi*1.5*t_harm))
    
    # Melodic version: sequential
    melody = np.zeros_like(t_harm)
    for i, freq in enumerate([1.0, 1.25, 1.5]):
        mask = (t_harm >= i*t_step) & (t_harm < (i+1)*t_step)
        melody[mask] = np.sin(2*np.pi*freq*t_harm[mask])
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 9))
    fig.suptitle("Harmony vs Melody: Same Notes, Different Information Structure",
                 fontsize=13, fontweight="bold")
    
    ax1 = axes[0]
    ax1.plot(t_harm, harmony, color="#4CAF50", linewidth=0.8)
    ax1.fill_between(t_harm, harmony, alpha=0.2, color="#4CAF50")
    ax1.set_title("C Major Chord (all three notes simultaneously)\nAll interference patterns present at once — brain processes multiple relationships in parallel")
    ax1.set_ylabel("Amplitude")
    ax1.grid(alpha=0.2)
    ax1.set_xlim(0, 8)
    
    ax2 = axes[1]
    ax2.plot(t_harm, melody, color="#2196F3", linewidth=0.8)
    ax2.fill_between(t_harm, melody, alpha=0.2, color="#2196F3")
    # Mark note boundaries
    for note_t in [t_step, 2*t_step]:
        ax2.axvline(note_t, color="red", alpha=0.5, linestyle="--", linewidth=1.5)
    ax2.set_title("C–E–G Melody (same notes, sequential)\nInterference only via memory — each note must be held while next arrives")
    ax2.set_ylabel("Amplitude")
    ax2.grid(alpha=0.2)
    ax2.set_xlim(0, 8)
    for i, (note_t_start, label) in enumerate([(0, "C"), (t_step, "E"), (2*t_step, "G")]):
        ax2.text(note_t_start + t_step/2, 0.8, label, ha="center", fontsize=10, fontweight="bold",
                 color="#1565C0")
    
    # Panel 3: FFT comparison — frequency content
    ax3 = axes[2]
    N = len(t_harm)
    freqs_fft = np.fft.rfftfreq(N, d=(t_harm[1]-t_harm[0]))
    
    harm_fft = np.abs(np.fft.rfft(harmony)) / N
    mel_fft  = np.abs(np.fft.rfft(melody)) / N
    
    ax3.plot(freqs_fft, harm_fft, color="#4CAF50", linewidth=1.2, label="Chord (simultaneous)", alpha=0.9)
    ax3.plot(freqs_fft, mel_fft, color="#2196F3", linewidth=1.2, label="Melody (sequential)", alpha=0.9, linestyle="--")
    ax3.set_xlim(0, 3)
    ax3.set_xlabel("Frequency (multiples of fundamental)")
    ax3.set_ylabel("Amplitude spectrum")
    ax3.set_title("Frequency Content\nChord: sharp peaks at 3 frequencies. Melody: blurred peaks (temporal smearing = bandwidth).")
    ax3.legend()
    ax3.grid(alpha=0.3)
    # Mark the three fundamental frequencies
    for freq, name in [(1.0, "C"), (1.25, "E"), (1.5, "G")]:
        ax3.axvline(freq, color="red", alpha=0.3, linestyle=":")
        ax3.text(freq, ax3.get_ylim()[1] * 0.9 if ax3.get_ylim()[1] > 0 else 0.1, 
                 name, ha="center", fontsize=8, color="red")
    
    plt.tight_layout()
    path = VIZ_DIR / "harmony_vs_melody.png"
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  ✓ harmony_vs_melody.png")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Session 3: Timbre, Melody-Memory, and Minor vs Major")
    print("=" * 55)
    
    print("\n[1/5] Timbre effects on consonance...")
    all_scores, instruments, labels = plot_timbre_consonance()
    
    print("\n[2/5] Clarinet odd-harmonic detail...")
    plot_clarinet_detail()
    
    print("\n[3/5] Melody as remembered interference...")
    plot_melody_memory()
    
    print("\n[4/5] Melodic tension arc...")
    plot_melodic_tension_arc()
    
    print("\n[5/5] Minor vs major mathematics...")
    major, minor, dim, aug = plot_minor_vs_major()
    
    print("\n[6/6] Harmony vs melody information density...")
    plot_information_density()
    
    print("\n✓ All visualizations complete.")
    print(f"  Output: {VIZ_DIR}")
    
    # Print key numerical findings
    print("\n=== KEY FINDINGS ===")
    print(f"Major triad total LCM: {major['total_lcm']}")
    print(f"Minor triad total LCM: {minor['total_lcm']}")
    print(f"Ratio minor/major complexity: {minor['total_lcm']/major['total_lcm']:.2f}×")
    print(f"Diminished triad total LCM: {dim['total_lcm']}")
    print(f"Augmented triad total LCM: {aug['total_lcm']}")
