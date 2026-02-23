#!/usr/bin/env python3
"""
Deep waveform interference analysis.
Session: 2026-02-23 — Modeling WHY consonance works.

Goals:
1. Measure waveform periodicity mathematically (LCM-based period)
2. Compute harmonic overlap density
3. Compare beat patterns for octave / fifth / fourth
4. Generate Lissajous-style phase portraits
5. Explore polyrhythm analogy (is 3:2 time "consonant"?)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from math import gcd
from fractions import Fraction
from pathlib import Path

SAMPLE_RATE = 44100
BASE_FREQ = 440.0  # A4
VIZ_DIR = Path(__file__).parent.parent / 'visualizations'
VIZ_DIR.mkdir(exist_ok=True)


# ─── Mathematical foundations ────────────────────────────────────────────────

def lcm(a, b):
    """Least common multiple — the key to understanding consonance."""
    return abs(a * b) // gcd(a, b)


def ratio_period(p, q):
    """
    For a ratio p:q (in lowest terms), the combined waveform repeats
    every lcm(p,q) cycles of the fundamental.
    
    Lower = more consonant.
    Octave 2:1 → lcm(2,1)=2 (repeats every 2 cycles)
    Fifth 3:2 → lcm(3,2)=6 (repeats every 6 cycles)
    Fourth 4:3 → lcm(4,3)=12
    Major Third 5:4 → lcm(5,4)=20
    Tritone 45:32 → lcm(45,32)=1440
    """
    frac = Fraction(p, q).limit_denominator(100)
    return lcm(frac.numerator, frac.denominator)


def harmonic_overlap(freq1, freq2, num_harmonics=32):
    """
    Count shared frequencies in the harmonic series of two tones.
    Returns count and list of shared frequencies.
    """
    h1 = set(round(freq1 * n, 2) for n in range(1, num_harmonics + 1))
    h2 = set(round(freq2 * n, 2) for n in range(1, num_harmonics + 1))
    
    # Use tolerance for float matching
    shared = []
    for f in sorted(h1):
        if any(abs(f - g) < 0.5 for g in h2):
            shared.append(f)
    
    return len(shared), shared


def consonance_metrics(freq1, freq2, num_harmonics=32):
    """Comprehensive consonance analysis for a two-note interval."""
    ratio = freq2 / freq1
    frac = Fraction(ratio).limit_denominator(64)
    p, q = frac.numerator, frac.denominator
    period = ratio_period(p, q)
    overlaps, shared = harmonic_overlap(freq1, freq2, num_harmonics)
    beat_freq = abs(freq2 - freq1)
    
    # Roughness estimate: beating within 5-30 Hz is most unpleasant
    rough_harmonics = 0
    h1 = [freq1 * n for n in range(1, num_harmonics + 1)]
    h2 = [freq2 * n for n in range(1, num_harmonics + 1)]
    for a in h1:
        for b in h2:
            diff = abs(a - b)
            if 5 < diff < 35:  # "Critical bandwidth" beating zone
                rough_harmonics += 1
    
    return {
        'ratio': ratio,
        'fraction': f'{p}/{q}',
        'period': period,          # lower = more consonant
        'harmonic_overlaps': overlaps,
        'beat_freq_hz': beat_freq,
        'roughness_pairs': rough_harmonics,  # higher = more dissonant
        'shared_harmonics': shared[:8],       # first 8 for display
    }


# ─── Key intervals to analyze ────────────────────────────────────────────────

INTERVALS = [
    ('Unison',        1/1,    440.0),
    ('Octave',        2/1,    880.0),
    ('Perfect Fifth', 3/2,    660.0),
    ('Perfect Fourth',4/3,    586.67),
    ('Major Third',   5/4,    550.0),
    ('Minor Third',   6/5,    528.0),
    ('Major Second',  9/8,    495.0),
    ('Minor Second',  16/15,  469.33),
    ('Tritone',       45/32,  618.75),
]


# ─── Visualization 1: Waveform interference panels ───────────────────────────

def plot_interference_comparison():
    """Plot waveform interference for key intervals in one figure."""
    intervals = [
        ('Octave 2:1',        440, 880),
        ('Perfect Fifth 3:2', 440, 660),
        ('Perfect Fourth 4:3',440, 586.67),
        ('Major Third 5:4',   440, 550),
        ('Tritone 45:32',     440, 618.75),
        ('Minor Second 16:15',440, 469.33),
    ]
    
    fig, axes = plt.subplots(len(intervals), 1, figsize=(14, 16))
    fig.suptitle('Waveform Interference Patterns: Consonance → Dissonance\n(showing 40ms of combined wave)', 
                 fontsize=13, fontweight='bold')
    
    duration = 0.04  # 40ms
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))
    
    colors = ['#2196F3', '#4CAF50', '#8BC34A', '#FFC107', '#FF5722', '#F44336']
    
    for i, (label, f1, f2) in enumerate(intervals):
        wave1 = np.sin(2 * np.pi * f1 * t)
        wave2 = np.sin(2 * np.pi * f2 * t)
        combined = (wave1 + wave2) / 2
        
        axes[i].plot(t * 1000, combined, color=colors[i], linewidth=0.8)
        axes[i].set_ylabel(label, fontsize=9, rotation=0, labelpad=100, va='center')
        axes[i].set_ylim(-1.1, 1.1)
        axes[i].axhline(0, color='gray', linewidth=0.3)
        axes[i].grid(True, alpha=0.2)
        
        # Annotate period
        frac = Fraction(f2/f1).limit_denominator(64)
        p, q = frac.numerator, frac.denominator
        per = ratio_period(p, q)
        axes[i].annotate(f'period: {per} cycles', xy=(0.02, 0.75), 
                        xycoords='axes fraction', fontsize=8, alpha=0.7)
        
        if i < len(intervals) - 1:
            axes[i].set_xticklabels([])
    
    axes[-1].set_xlabel('Time (ms)')
    plt.tight_layout()
    path = VIZ_DIR / 'interference_comparison.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {path.name}")
    return path


# ─── Visualization 2: Harmonic overlap heatmap ───────────────────────────────

def plot_harmonic_series():
    """Visual showing harmonic series and where octave/fifth/fourth align."""
    fig, axes = plt.subplots(4, 1, figsize=(16, 10))
    fig.suptitle('Harmonic Series Alignment: Why Octaves & Fifths Resonate',
                fontsize=13, fontweight='bold')
    
    base = 220.0  # A3
    harmonics = 24
    
    configs = [
        ('A3  (220 Hz)', base, '#2196F3'),
        ('A4  (440 Hz) — Octave', base * 2, '#4CAF50'),
        ('E4  (330 Hz) — Perfect Fifth', base * 3/2, '#FF9800'),
        ('D4  (293 Hz) — Perfect Fourth', base * 4/3, '#E91E63'),
    ]
    
    for ax, (label, freq, color) in zip(axes, configs):
        freqs = [freq * n for n in range(1, harmonics + 1)]
        heights = [1.0 / n for n in range(1, harmonics + 1)]  # Falling amplitude
        
        ax.bar(freqs, heights, width=15, color=color, alpha=0.7, label=label)
        
        # Mark shared harmonics with base
        base_harmonics = set(round(base * n) for n in range(1, harmonics + 1))
        for n, f in enumerate(freqs, 1):
            if round(f) in base_harmonics:
                ax.bar(f, heights[n-1], width=15, color='black', alpha=0.9)
        
        ax.set_xlim(0, base * harmonics + 100)
        ax.set_ylabel('Amplitude')
        ax.set_title(label, fontsize=10, loc='left', pad=2)
        ax.grid(True, alpha=0.2)
        
        # Count overlaps
        note_harmonics = set(round(freq * n) for n in range(1, harmonics + 1))
        overlap_count = len(base_harmonics & note_harmonics)
        ax.annotate(f'{overlap_count} shared harmonics (black bars)', 
                   xy=(0.7, 0.8), xycoords='axes fraction', fontsize=9)
    
    axes[-1].set_xlabel('Frequency (Hz)')
    plt.tight_layout()
    path = VIZ_DIR / 'harmonic_overlap.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {path.name}")
    return path


# ─── Visualization 3: Lissajous phase portraits ──────────────────────────────

def plot_lissajous():
    """
    Lissajous figures: plot wave1 vs wave2 in x-y space.
    Consonant intervals → simple closed curves
    Dissonant intervals → complex, chaotic paths
    """
    intervals = [
        ('Unison\n1:1',      1,  1),
        ('Octave\n2:1',      2,  1),
        ('Fifth\n3:2',       3,  2),
        ('Fourth\n4:3',      4,  3),
        ('Maj 3rd\n5:4',     5,  4),
        ('Min 3rd\n6:5',     6,  5),
        ('Maj 2nd\n9:8',     9,  8),
        ('Tritone\n~45:32', 45, 32),
    ]
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    fig.suptitle('Lissajous Figures: Consonance as Geometric Simplicity\n'
                '(x-axis = note 1, y-axis = note 2; more loops = more complex)',
                fontsize=12, fontweight='bold')
    
    t = np.linspace(0, 4 * np.pi, 10000)
    
    cmap = plt.cm.viridis
    
    for idx, (label, p, q) in enumerate(intervals):
        ax = axes[idx // 4][idx % 4]
        x = np.sin(p * t)
        y = np.sin(q * t + 0.01)  # tiny phase offset to fill curves
        
        period = lcm(p, q)
        complexity = period  # direct measure
        
        # Color by "time" to show direction
        colors_arr = np.linspace(0, 1, len(t))
        for j in range(0, len(t)-1, 10):
            ax.plot(x[j:j+10], y[j:j+10], 
                   color=cmap(colors_arr[j]), linewidth=0.5, alpha=0.7)
        
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(-1.1, 1.1)
        ax.set_title(label, fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.15)
        ax.annotate(f'period={period}', xy=(0.02, 0.05), 
                   xycoords='axes fraction', fontsize=8)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
    
    plt.tight_layout()
    path = VIZ_DIR / 'lissajous_consonance.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {path.name}")
    return path


# ─── Visualization 4: Consonance score plot ──────────────────────────────────

def plot_consonance_scores():
    """Plot multiple consonance metrics for all intervals."""
    names = []
    periods = []
    overlaps = []
    roughness = []
    
    for name, ratio, freq2 in INTERVALS:
        m = consonance_metrics(BASE_FREQ, freq2)
        names.append(name)
        periods.append(m['period'])
        overlaps.append(m['harmonic_overlaps'])
        roughness.append(m['roughness_pairs'])
    
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig.suptitle('Consonance Metrics by Interval', fontsize=13, fontweight='bold')
    
    x = range(len(names))
    colors = plt.cm.RdYlGn_r(np.linspace(0, 1, len(names)))
    
    # Panel 1: Waveform period (lower = more consonant)
    axes[0].bar(x, periods, color=colors)
    axes[0].set_xticks(list(x))
    axes[0].set_xticklabels(names, rotation=30, ha='right', fontsize=9)
    axes[0].set_ylabel('LCM Period\n(cycles to repeat)')
    axes[0].set_title('Waveform Period (LOWER = more consonant)', fontsize=10)
    axes[0].set_yscale('log')
    for i, v in enumerate(periods):
        axes[0].text(i, v * 1.1, str(v), ha='center', va='bottom', fontsize=8)
    
    # Panel 2: Harmonic overlaps (higher = more consonant)
    axes[1].bar(x, overlaps, color=colors[::-1])
    axes[1].set_xticks(list(x))
    axes[1].set_xticklabels(names, rotation=30, ha='right', fontsize=9)
    axes[1].set_ylabel('Shared Harmonics\n(out of 32 each)')
    axes[1].set_title('Harmonic Overlap (HIGHER = more consonant)', fontsize=10)
    for i, v in enumerate(overlaps):
        axes[1].text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=8)
    
    # Panel 3: Roughness (lower = more consonant)
    axes[2].bar(x, roughness, color=colors)
    axes[2].set_xticks(list(x))
    axes[2].set_xticklabels(names, rotation=30, ha='right', fontsize=9)
    axes[2].set_ylabel('Rough Harmonic Pairs\n(5–35 Hz apart)')
    axes[2].set_title('Roughness/Beating (LOWER = more consonant)', fontsize=10)
    for i, v in enumerate(roughness):
        axes[2].text(i, v + 0.1, str(v), ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    path = VIZ_DIR / 'consonance_scores.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {path.name}")
    return path


# ─── Visualization 5: Polyrhythm analog ──────────────────────────────────────

def plot_polyrhythm_analysis():
    """
    Does rhythm work like frequency?
    
    If 3:2 frequency ratio is consonant, is 3:2 polyrhythm also "consonant"?
    Model: two pulse trains, measure how often they coincide.
    
    Consonant rhythms: pulses align more often (simple ratios)
    Dissonant rhythms: pulses rarely align (complex ratios)
    """
    # Rhythm ratios to compare
    rhythms = [
        ('2:1 (simple double)', 2, 1),
        ('3:2 (perfect "fifth")', 3, 2),
        ('4:3 (perfect "fourth")', 4, 3),
        ('5:4 (major "third")', 5, 4),
        ('7:4 (jazz triplet)', 7, 4),
        ('7:5 (tritone analog)', 7, 5),
        ('11:8 (complex)', 11, 8),
    ]
    
    fig, axes = plt.subplots(len(rhythms), 1, figsize=(14, 14))
    fig.suptitle('Polyrhythm Analysis: Rhythm as Pattern (the time analog of frequency)\n'
                '3:2 in rhythm = 3:2 in pitch? Coincidences = consonance',
                fontsize=11, fontweight='bold')
    
    total_beats = 24  # grid length
    
    for i, (label, p, q) in enumerate(rhythms):
        ax = axes[i]
        ax.set_xlim(-0.5, total_beats + 0.5)
        ax.set_ylim(-0.5, 2.5)
        ax.set_yticks([0.5, 1.5])
        ax.set_yticklabels([f'×{q}', f'×{p}'], fontsize=9)
        ax.set_title(label, fontsize=9, loc='left', pad=2)
        
        period = lcm(p, q)
        
        # Draw pulse grids
        for t in range(0, total_beats + 1, q):
            ax.axvline(t, color='#2196F3', alpha=0.8, linewidth=1.5)
            ax.plot(t, 0.5, 'o', color='#2196F3', markersize=8, zorder=5)
        
        for t in range(0, total_beats + 1, p):
            ax.axvline(t, color='#F44336', alpha=0.8, linewidth=1.5)
            ax.plot(t, 1.5, 's', color='#F44336', markersize=7, zorder=5)
        
        # Mark coincidences
        coincidences = [t for t in range(0, total_beats + 1)
                       if t % p == 0 and t % q == 0]
        for t in coincidences:
            ax.axvspan(t - 0.3, t + 0.3, alpha=0.25, color='gold', zorder=3)
        
        # Count coincidences per period
        coinc_rate = len(coincidences) / (total_beats / period)
        ax.annotate(f'LCM period={period} | coincidences/{period}beats = {1}',
                   xy=(0.55, 0.5), xycoords='axes fraction', fontsize=8, alpha=0.8)
        
        ax.set_facecolor('#f8f8f8')
        ax.grid(False)
        
        if i < len(rhythms) - 1:
            ax.set_xticklabels([])
    
    axes[-1].set_xlabel('Beats (tick marks)')
    plt.tight_layout()
    path = VIZ_DIR / 'polyrhythm_analysis.png'
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✓ Saved: {path.name}")
    return path


# ─── Main ─────────────────────────────────────────────────────────────────────

def run_analysis():
    print("=" * 60)
    print("DEEP INTERFERENCE ANALYSIS — 2026-02-23")
    print("=" * 60)
    
    # Print consonance metrics table
    print("\n── Consonance Metrics ──────────────────────────────────────")
    print(f"{'Interval':<20} {'Ratio':<10} {'Period':<8} {'Overlaps':<10} {'Roughness'}")
    print("-" * 60)
    
    for name, ratio, freq2 in INTERVALS:
        m = consonance_metrics(BASE_FREQ, freq2)
        print(f"{name:<20} {m['fraction']:<10} {m['period']:<8} "
              f"{m['harmonic_overlaps']:<10} {m['roughness_pairs']}")
    
    # Mathematical findings
    print("\n── Key Mathematical Findings ───────────────────────────────")
    
    oct_m = consonance_metrics(BASE_FREQ, 880.0)
    fif_m = consonance_metrics(BASE_FREQ, 660.0)
    fou_m = consonance_metrics(BASE_FREQ, 586.67)
    tri_m = consonance_metrics(BASE_FREQ, 618.75)
    
    print(f"\nOCTAVE (2:1):")
    print(f"  Period: {oct_m['period']} cycles (repeats fastest)")
    print(f"  Overlaps: {oct_m['harmonic_overlaps']} (every even harmonic is shared)")
    print(f"  Roughness: {oct_m['roughness_pairs']} pairs")
    
    print(f"\nPERFECT FIFTH (3:2):")
    print(f"  Period: {fif_m['period']} cycles")
    print(f"  Overlaps: {fif_m['harmonic_overlaps']} (shared every 3rd harmonic of lower)")
    print(f"  Roughness: {fif_m['roughness_pairs']} pairs")
    
    print(f"\nPERFECT FOURTH (4:3):")
    print(f"  Period: {fou_m['period']} cycles")
    print(f"  Overlaps: {fou_m['harmonic_overlaps']}")
    print(f"  Roughness: {fou_m['roughness_pairs']} pairs")
    
    print(f"\nTRITONE (45:32):")
    print(f"  Period: {tri_m['period']} cycles (essentially never repeats)")
    print(f"  Overlaps: {tri_m['harmonic_overlaps']}")
    print(f"  Roughness: {tri_m['roughness_pairs']} pairs (maximum!)")
    
    print("\n── Polyrhythm Analog ────────────────────────────────────────")
    print("3:2 polyrhythm: LCM = 6 (every 6 beats, the pulses align)")
    print("7:5 polyrhythm: LCM = 35 (must wait 35 beats for alignment)")
    print("Conclusion: simple-ratio rhythms 'resolve' faster = perceptually 'consonant'")
    
    print("\n── Generating Visualizations ───────────────────────────────")
    plot_interference_comparison()
    plot_harmonic_series()
    plot_lissajous()
    plot_consonance_scores()
    plot_polyrhythm_analysis()
    
    print("\n── Done ─────────────────────────────────────────────────────")
    print(f"All visualizations saved to: {VIZ_DIR}")
    return True


if __name__ == '__main__':
    run_analysis()
