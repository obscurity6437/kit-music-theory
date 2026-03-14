#!/usr/bin/env python3
"""
Session 8 — Melodic Expectation, Real-Piece Tension Analysis,
Spectral LCM, Missing Fundamental, and Polytonality

Building on the unified LCM + proximity gravity model from Session 7.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from fractions import Fraction
from math import gcd, log2
import warnings
warnings.filterwarnings('ignore')

# ─── Utility functions ───────────────────────────────────────────────────────

def lcm(a, b):
    """Integer LCM."""
    return abs(a * b) // gcd(a, b)

def lcm_complexity(ratio_num, ratio_den):
    """Log2-LCM of an interval given as integer ratio."""
    g = gcd(ratio_num, ratio_den)
    n, d = ratio_num // g, ratio_den // g
    return log2(lcm(n, d))

# Interval table: name → (num, den)
INTERVALS = {
    'Unison':       (1, 1),
    'min 2nd':      (16, 15),
    'Maj 2nd':      (9, 8),
    'min 3rd':      (6, 5),
    'Maj 3rd':      (5, 4),
    'Perfect 4th':  (4, 3),
    'Tritone':      (45, 32),
    'Perfect 5th':  (3, 2),
    'min 6th':      (8, 5),
    'Maj 6th':      (5, 3),
    'min 7th':      (9, 5),
    'Maj 7th':      (15, 8),
    'Octave':       (2, 1),
}

def semitones_to_ratio(semitones):
    """12-TET frequency ratio for a given number of semitones."""
    return 2 ** (semitones / 12)

# C major scale: note name → semitones from C4
C_MAJOR_NOTES = {
    'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11,
    'C5': 12
}

C_MAJOR_JI = {  # Just intonation ratios from C
    'C':  (1, 1),
    'D':  (9, 8),
    'E':  (5, 4),
    'F':  (4, 3),
    'G':  (3, 2),
    'A':  (5, 3),
    'B':  (15, 8),
    'C5': (2, 1),
}

TONIC_TRIAD = {'C', 'E', 'G'}  # stable tones

def gravity_to_note(note, tonic_triad, scale_ji):
    """
    Combined LCM + proximity gravity force toward tonic triad.
    Returns (direction, magnitude, dominant_force).
    """
    if note in tonic_triad:
        return ('ATTRACTOR', 1.0, 'stable')
    
    note_semitones = C_MAJOR_NOTES.get(note, None)
    if note_semitones is None:
        return ('unknown', 0, 'none')
    
    best_lcm_force = 0
    best_prox_force = 0
    best_target = None
    
    targets = {'C': 0, 'E': 4, 'G': 7}
    
    for stable, st_semi in targets.items():
        # LCM force
        n1, d1 = scale_ji.get(note, (1, 1))
        n2, d2 = scale_ji.get(stable, (1, 1))
        # ratio of note to stable
        num = n1 * d2
        den = d1 * n2
        g = gcd(num, den)
        num, den = num // g, den // g
        lcm_val = lcm(num, den)
        lcm_force = 1.0 / log2(max(lcm_val, 2))
        
        # Proximity force
        dist = abs(note_semitones - st_semi)
        if dist == 0:
            dist = 12  # same note, no pull
        prox_force = 2.0 / dist
        
        total = lcm_force + prox_force
        if total > best_lcm_force + best_prox_force:
            best_lcm_force = lcm_force
            best_prox_force = prox_force
            best_target = stable
    
    direction = f'→ {best_target}'
    magnitude = best_lcm_force + best_prox_force
    dom = 'proximity' if best_prox_force > best_lcm_force else 'harmonic'
    return (direction, magnitude, dom)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. MELODIC EXPECTATION MODEL
# ═══════════════════════════════════════════════════════════════════════════════

def compute_melodic_expectation(current_note, prev_note=None, tonic='C'):
    """
    Given current and previous note, compute probability distribution
    over the next note in C major using gravity + melodic momentum.
    
    Returns dict: {next_note: probability}
    """
    scale_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C5']
    scale_semi = {n: C_MAJOR_NOTES[n] for n in scale_notes}
    
    current_semi = scale_semi[current_note]
    
    scores = {}
    for candidate in scale_notes:
        if candidate == current_note:
            continue
        
        cand_semi = scale_semi[candidate]
        step_size = abs(cand_semi - current_semi)
        
        # 1. Step preference (smaller = more likely)
        step_score = 1.0 / (step_size ** 0.7) if step_size > 0 else 0
        
        # 2. Gravity force toward tonic stability
        _, grav_mag, _ = gravity_to_note(candidate, TONIC_TRIAD, C_MAJOR_JI)
        grav_score = grav_mag * 0.3
        
        # 3. Melodic momentum (continuation of previous direction)
        momentum_score = 0
        if prev_note is not None:
            prev_semi = scale_semi[prev_note]
            prev_direction = current_semi - prev_semi
            new_direction = cand_semi - current_semi
            if prev_direction * new_direction > 0:  # same direction
                momentum_score = 0.4
            elif prev_direction * new_direction < 0:  # reversal
                momentum_score = 0.15
        
        # 4. LCM simplicity from tonic
        n, d = C_MAJOR_JI.get(candidate, (1, 1))
        cand_complexity = log2(lcm(n, d))
        simplicity_score = 1.0 / max(cand_complexity, 0.5) * 0.5
        
        scores[candidate] = step_score + grav_score + momentum_score + simplicity_score
    
    # Normalize to probability
    total = sum(scores.values())
    probs = {k: v / total for k, v in scores.items()}
    return probs


# ═══════════════════════════════════════════════════════════════════════════════
# 2. REAL-PIECE TENSION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def chord_lcm_complexity(notes_ji):
    """
    Compute total pairwise LCM complexity for a chord.
    notes_ji: list of (num, den) JI ratios from root.
    """
    total = 0
    for i in range(len(notes_ji)):
        for j in range(i + 1, len(notes_ji)):
            n1, d1 = notes_ji[i]
            n2, d2 = notes_ji[j]
            # ratio of n1/d1 to n2/d2 = n1*d2 : n2*d1
            num = n1 * d2
            den = n2 * d1
            g = gcd(num, den)
            num, den = num // g, den // g
            total += log2(lcm(num, den))
    return total

# Chord library — triads and seventh chords as JI ratios from local root
CHORD_TYPES = {
    'major':     [(1, 1), (5, 4), (3, 2)],           # root, maj3, p5
    'minor':     [(1, 1), (6, 5), (3, 2)],            # root, min3, p5
    'dom7':      [(1, 1), (5, 4), (3, 2), (9, 5)],   # root, maj3, p5, min7
    'maj7':      [(1, 1), (5, 4), (3, 2), (15, 8)],  # root, maj3, p5, maj7
    'dim':       [(1, 1), (6, 5), (45, 32)],          # root, min3, tritone
    'aug':       [(1, 1), (5, 4), (8, 5)],            # root, maj3, aug5
    'sus4':      [(1, 1), (4, 3), (3, 2)],            # root, p4, p5
    'min7':      [(1, 1), (6, 5), (3, 2), (9, 5)],   # root, min3, p5, min7
    'half-dim7': [(1, 1), (6, 5), (45, 32), (9, 5)], # root, min3, tritone, min7
    'dim7':      [(1, 1), (6, 5), (45, 32), (9, 5)], # fully diminished approx
}

def get_chord_complexity(chord_type):
    return chord_lcm_complexity(CHORD_TYPES[chord_type])

# Pre-compute base complexities
BASE_COMPLEXITY = {c: get_chord_complexity(c) for c in CHORD_TYPES}

# Pachelbel's Canon — chord progression (I V vi iii IV I IV V in D major, normalized)
PACHELBEL = [
    ('I',  'major', 'D'),
    ('V',  'major', 'A'),
    ('vi', 'minor', 'B'),
    ('iii','minor', 'F#'),
    ('IV', 'major', 'G'),
    ('I',  'major', 'D'),
    ('IV', 'major', 'G'),
    ('V',  'major', 'A'),
]

# Beethoven 5th — first 8 measures sketched as chord changes
BEETHOVEN_5TH = [
    ('i',   'minor', 'C'),   # m1 — c minor tonic
    ('i',   'minor', 'C'),   # m2
    ('VII', 'major', 'Bb'),  # m3 — bVII
    ('VII', 'major', 'Bb'),  # m4
    ('i',   'minor', 'C'),   # m5
    ('V',   'dom7',  'G'),   # m6 — dominant 7th
    ('i',   'minor', 'C'),   # m7
    ('V',   'dom7',  'G'),   # m8
]

# Coltrane Changes (Giant Steps turnaround, 4 chords)
COLTRANE_GIANT_STEPS = [
    ('I',   'maj7', 'B'),
    ('V',   'dom7', 'G'),   # → E major 
    ('I',   'maj7', 'E'),
    ('V',   'dom7', 'C'),   # → Bb (tritone chain)
    ('I',   'maj7', 'Bb'),
    ('V',   'dom7', 'G'),   # back
    ('I',   'maj7', 'B'),
    ('V',   'dom7', 'D'),
]

def compute_piece_tension(progression, memory_decay=0.7):
    """
    Compute beat-by-beat tension arc for a chord progression.
    Returns list of (beat, tension, chord_name) tuples.
    """
    tension_values = []
    prev_tension = 0
    
    for i, (roman, chord_type, root) in enumerate(progression):
        base = BASE_COMPLEXITY[chord_type]
        
        # Transition cost from previous chord
        if i > 0:
            prev_type = progression[i-1][1]
            transition_cost = abs(base - BASE_COMPLEXITY[prev_type]) * 0.5
        else:
            transition_cost = 0
        
        # Memory carries over
        current = base + (prev_tension * memory_decay * 0.3) + transition_cost
        tension_values.append((i, current, f'{root}{roman}'))
        prev_tension = current
    
    return tension_values


# ═══════════════════════════════════════════════════════════════════════════════
# 3. MISSING FUNDAMENTAL
# ═══════════════════════════════════════════════════════════════════════════════

def find_missing_fundamental(harmonics, tolerance_cents=15):
    """
    Given a set of frequencies (as frequency ratios from an arbitrary reference),
    find the most likely missing fundamental F such that each presented
    frequency is an integer multiple of F.
    
    Returns: (fundamental ratio, confidence, integer_assignments)
    """
    # Try candidate fundamentals: each frequency divided by 1..16
    candidates = {}
    
    for f in harmonics:
        for n in range(1, 17):
            candidate_f = f / n
            if candidate_f < 0.05:  # too low to be practical
                continue
            
            # Check how well this candidate predicts all harmonics
            errors = []
            assignments = []
            for test_f in harmonics:
                # Find nearest integer multiple
                ratio = test_f / candidate_f
                nearest_n = round(ratio)
                if nearest_n < 1:
                    continue
                # Error in cents
                actual_cents = 1200 * log2(ratio / nearest_n) if nearest_n > 0 else 999
                errors.append(abs(actual_cents))
                assignments.append((test_f, nearest_n, actual_cents))
            
            if errors:
                mean_error = np.mean(errors)
                key = round(candidate_f * 100) / 100
                if key not in candidates or mean_error < candidates[key][0]:
                    candidates[key] = (mean_error, candidate_f, assignments)
    
    # Find best candidate
    best = min(candidates.values(), key=lambda x: x[0])
    mean_error, fund, assignments = best
    
    confidence = max(0, 1 - mean_error / 100)
    return fund, confidence, assignments


# Demonstration cases
MISSING_FUND_CASES = [
    {
        'name': 'Open G guitar (2nd, 3rd, 4th harmonics only)',
        'description': 'Remove fundamental G, present 392*2, 392*3, 392*4 Hz equivalently',
        'harmonics': [2.0, 3.0, 4.0],  # relative to missing fundamental at 1.0
        'true_fund': 1.0,
    },
    {
        'name': 'Barbershop 7th chord',
        'description': 'Harmonics 4,5,6,7 — the dominant 7th barbershop chord',
        'harmonics': [4.0, 5.0, 6.0, 7.0],
        'true_fund': 1.0,
    },
    {
        'name': 'Ambiguous fundamental',
        'description': 'Harmonics 6,10,15 — could be fund 1 or 2 or 5',
        'harmonics': [6.0, 10.0, 15.0],
        'true_fund': 1.0,  # LCM(6,10,15) = 30, but gcd too
    },
    {
        'name': 'Perfect fifth without root (horn 5th)',
        'description': 'Harmonics 3 and 2 only — what root does the ear construct?',
        'harmonics': [3.0, 2.0],
        'true_fund': 1.0,
    },
]


# ═══════════════════════════════════════════════════════════════════════════════
# 4. POLYTONALITY — LCM in KEY SPACE
# ═══════════════════════════════════════════════════════════════════════════════

def key_lcm_complexity(key1_root_ratio, key2_root_ratio):
    """
    Estimate the complexity of simultaneously sounding two keys.
    Keys are represented as frequency ratio (num, den) of their tonics.
    The LCM of the tonic ratios gives the period before both keys resolve.
    """
    n1, d1 = key1_root_ratio
    n2, d2 = key2_root_ratio
    
    # Cross-key ratio
    num = n1 * d2
    den = d1 * n2
    g = gcd(num, den)
    num, den = num // g, den // g
    
    return log2(lcm(num, den)), num, den


# Standard key pairs for polytonality analysis
KEY_PAIRS = [
    ('C major', 'G major', (1, 1), (3, 2)),       # Circle of fifths neighbors
    ('C major', 'F major', (1, 1), (4, 3)),       # Circle of fourths neighbors  
    ('C major', 'Eb major', (1, 1), (6, 5)),      # Minor third apart
    ('C major', 'E major', (1, 1), (5, 4)),       # Major third apart (chromatic mediant)
    ('C major', 'Gb major', (1, 1), (45, 32)),    # Tritone apart — Stravinsky Petrushka
    ('C major', 'Ab major', (1, 1), (8, 5)),      # Minor sixth apart
    ('C major', 'A major', (1, 1), (5, 3)),       # Major sixth apart
    ('C major', 'Bb major', (1, 1), (9, 5)),      # Minor seventh apart
    ('C major', 'B major', (1, 1), (15, 8)),      # Major seventh apart
    ('C major', 'D major', (1, 1), (9, 8)),       # Major second apart
    ('C major', 'Db major', (1, 1), (16, 15)),    # Minor second apart — maximally grinding
]


# ═══════════════════════════════════════════════════════════════════════════════
# VISUALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

def plot_melodic_expectation(ax_main, ax_from_F):
    """Plot melodic expectation distributions from two starting notes."""
    scale_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C5']
    
    # From E, no prior note
    probs_E = compute_melodic_expectation('E', prev_note=None)
    # From E, prior note was F (downward step, implies continuation or reversal)
    probs_EfromF = compute_melodic_expectation('E', prev_note='F')
    # From G, prior note was E (ascending, continuing up or turning around)
    probs_GfromE = compute_melodic_expectation('G', prev_note='E')
    # From F#... wait, F# not in scale. Let me use F instead.
    probs_F = compute_melodic_expectation('F', prev_note=None)
    
    candidates = [n for n in scale_notes if n != 'E']
    x = np.arange(len(candidates))
    
    p1 = [probs_E.get(n, 0) for n in candidates]
    p2 = [probs_EfromF.get(n, 0) for n in candidates]
    
    width = 0.35
    bars1 = ax_main.bar(x - width/2, p1, width, label='From E (no prior)', 
                         color='steelblue', alpha=0.8)
    bars2 = ax_main.bar(x + width/2, p2, width, label='From E (prior: F)', 
                         color='coral', alpha=0.8)
    
    ax_main.set_xticks(x)
    ax_main.set_xticklabels(candidates)
    ax_main.set_ylabel('Probability')
    ax_main.set_title('Melodic Expectation from E\n(LCM + Proximity + Momentum model)', fontsize=11)
    ax_main.legend(fontsize=9)
    ax_main.set_ylim(0, max(max(p1), max(p2)) * 1.3)
    
    # Mark tonic triad members
    for i, note in enumerate(candidates):
        if note in TONIC_TRIAD or note == 'C5':
            ax_main.axvspan(i - 0.5, i + 0.5, alpha=0.08, color='green')
    
    # Second plot: from F
    candidates_G = [n for n in scale_notes if n != 'F']
    probs_FnoP = compute_melodic_expectation('F', prev_note=None)
    probs_FfromG = compute_melodic_expectation('F', prev_note='G')
    
    xG = np.arange(len(candidates_G))
    pG1 = [probs_FnoP.get(n, 0) for n in candidates_G]
    pG2 = [probs_FfromG.get(n, 0) for n in candidates_G]
    
    ax_from_F.bar(xG - width/2, pG1, width, label='From F (no prior)',
                  color='mediumpurple', alpha=0.8)
    ax_from_F.bar(xG + width/2, pG2, width, label='From F (prior: G)',
                  color='goldenrod', alpha=0.8)
    ax_from_F.set_xticks(xG)
    ax_from_F.set_xticklabels(candidates_G)
    ax_from_F.set_ylabel('Probability')
    ax_from_F.set_title('Melodic Expectation from F (the "avoid note")\n', fontsize=11)
    ax_from_F.legend(fontsize=9)
    ax_from_F.set_ylim(0, max(max(pG1), max(pG2)) * 1.3)
    
    for i, note in enumerate(candidates_G):
        if note in TONIC_TRIAD or note == 'C5':
            ax_from_F.axvspan(i - 0.5, i + 0.5, alpha=0.08, color='green')
    
    ax_from_F.text(0.98, 0.95, 'Green = tonic triad notes', transform=ax_from_F.transAxes,
                   ha='right', va='top', fontsize=8, color='green', alpha=0.7)


def plot_piece_tensions(ax1, ax2, ax3):
    """Plot tension arcs for Pachelbel, Beethoven 5th, Coltrane."""
    for ax, progression, title, color in [
        (ax1, PACHELBEL, "Pachelbel Canon in D\n(I V vi iii IV I IV V)", 'steelblue'),
        (ax2, BEETHOVEN_5TH, "Beethoven Symphony 5, mm. 1–8\n(c minor opening)", 'firebrick'),
        (ax3, COLTRANE_GIANT_STEPS, "Coltrane — Giant Steps changes\n(chromatic mediant cycle)", 'forestgreen'),
    ]:
        tension_data = compute_piece_tension(progression)
        beats = [t[0] for t in tension_data]
        tensions = [t[1] for t in tension_data]
        labels = [t[2] for t in tension_data]
        
        ax.plot(beats, tensions, 'o-', color=color, linewidth=2, markersize=7)
        ax.fill_between(beats, tensions, alpha=0.15, color=color)
        
        for b, t, label in zip(beats, tensions, labels):
            ax.annotate(label, (b, t), textcoords='offset points',
                       xytext=(0, 8), ha='center', fontsize=8, color=color)
        
        ax.set_xticks(beats)
        ax.set_xticklabels([f'm.{i+1}' for i in beats])
        ax.set_ylabel('Tension (log₂-LCM)')
        ax.set_title(title, fontsize=10)
        
        # Mark high-tension and resolution points
        max_t = max(tensions)
        min_t = min(tensions)
        peak_i = tensions.index(max_t)
        trough_i = tensions.index(min_t)
        
        ax.axhline(np.mean(tensions), color='gray', linestyle='--', alpha=0.4, linewidth=1)
        ax.text(beats[-1], np.mean(tensions) + 0.1, ' mean', fontsize=7, color='gray')


def plot_missing_fundamental(ax_waveforms, ax_summary):
    """Demonstrate the missing fundamental principle via LCM."""
    
    # Case study: harmonics 4, 5, 6, 7 — barbershop 7th
    harmonics_case = [4.0, 5.0, 6.0, 7.0]
    
    t = np.linspace(0, 1, 4000)
    f_ref = 110.0  # reference pitch
    
    # Full harmonic series (with fundamental)
    full_wave = np.zeros_like(t)
    for i, h in enumerate([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]):
        amp = 1.0 / h
        full_wave += amp * np.sin(2 * np.pi * f_ref * h * t)
    
    # Missing fundamental version
    missing_wave = np.zeros_like(t)
    for h in harmonics_case:
        amp = 1.0 / h
        missing_wave += amp * np.sin(2 * np.pi * f_ref * h * t)
    
    # Just the fundamental
    fund_wave = np.sin(2 * np.pi * f_ref * t)
    
    # Plot waveforms
    show_samples = 400
    ax_waveforms.plot(t[:show_samples], full_wave[:show_samples], 
                     color='steelblue', alpha=0.8, linewidth=1.5, label='Full series (1–7)')
    ax_waveforms.plot(t[:show_samples], missing_wave[:show_samples] * 2 - 3, 
                     color='coral', alpha=0.8, linewidth=1.5, label='Missing fund (4–7)')
    ax_waveforms.plot(t[:show_samples], fund_wave[:show_samples] * 0.5 - 5.5, 
                     color='green', alpha=0.8, linewidth=1.5, label='Fundamental alone')
    
    ax_waveforms.set_title('Missing Fundamental\n(harmonics 4–7 only → ear reconstructs root)', fontsize=10)
    ax_waveforms.set_xlabel('Time')
    ax_waveforms.set_ylabel('Amplitude')
    ax_waveforms.legend(fontsize=8)
    ax_waveforms.set_yticks([])
    ax_waveforms.axhline(-3, color='gray', alpha=0.2, linewidth=0.5)
    ax_waveforms.axhline(-5.5, color='gray', alpha=0.2, linewidth=0.5)
    
    # LCM analysis of the cases
    case_names = []
    case_lcms = []
    case_descs = []
    
    for case in MISSING_FUND_CASES:
        harm = case['harmonics']
        # LCM of the integer harmonics
        cur = int(harm[0])
        for h in harm[1:]:
            cur = lcm(cur, int(h))
        case_names.append(case['name'].split('(')[0].strip())
        case_lcms.append(log2(cur))
        case_descs.append(f'LCM={cur}')
    
    colors = ['steelblue', 'coral', 'goldenrod', 'forestgreen']
    bars = ax_summary.barh(range(len(case_names)), case_lcms, color=colors, alpha=0.8)
    ax_summary.set_yticks(range(len(case_names)))
    ax_summary.set_yticklabels(case_names, fontsize=8)
    ax_summary.set_xlabel('log₂(LCM of presented harmonics)')
    ax_summary.set_title('Missing Fundamental: LCM of\nPresented Harmonics', fontsize=10)
    
    for i, (bar, desc) in enumerate(zip(bars, case_descs)):
        ax_summary.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height()/2,
                       desc, va='center', fontsize=9, color='gray')
    
    ax_summary.text(0.98, 0.02,
        'Low LCM → clear fundamental\nHigh LCM → ambiguous root',
        transform=ax_summary.transAxes, ha='right', va='bottom',
        fontsize=8, style='italic', color='gray')


def plot_polytonality(ax_scatter, ax_bar):
    """Visualize the complexity of simultaneous key pairs."""
    pair_names = []
    pair_complexities = []
    pair_intervals = []
    
    for name1, name2, r1, r2 in KEY_PAIRS:
        complexity, num, den = key_lcm_complexity(r1, r2)
        pair_names.append(f'{name2.replace(" major", "")}\n({name1[:1]} + {name2[:2]})')
        pair_complexities.append(complexity)
        pair_intervals.append(f'{num}:{den}')
    
    # Sort by complexity
    sorted_pairs = sorted(zip(pair_complexities, pair_names, pair_intervals))
    pair_complexities, pair_names, pair_intervals = zip(*sorted_pairs)
    
    # Color by complexity
    cmap = plt.cm.RdYlGn_r
    colors = [cmap(c / max(pair_complexities)) for c in pair_complexities]
    
    bars = ax_bar.barh(range(len(pair_names)), pair_complexities, color=colors, alpha=0.85)
    ax_bar.set_yticks(range(len(pair_names)))
    ax_bar.set_yticklabels(pair_names, fontsize=9)
    ax_bar.set_xlabel('log₂(LCM of tonic ratios)')
    ax_bar.set_title('Polytonality: Complexity by Key Pairing\n(C major + X)', fontsize=10)
    
    for i, (bar, interval) in enumerate(zip(bars, pair_intervals)):
        ax_bar.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
                   interval, va='center', fontsize=8, color='dimgray')
    
    # Notable annotations
    max_c = max(pair_complexities)
    min_c = min(pair_complexities)
    ax_bar.text(0.98, 0.02, 
                f'Petrushka chord (tritone):\nC+F# LCM complexity ≈ {pair_complexities[-1]:.1f}\n'
                f'Circle neighbors (5th): {pair_complexities[0]:.1f}',
                transform=ax_bar.transAxes, ha='right', va='bottom',
                fontsize=8, style='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.7))
    
    # Historical examples scatter
    examples = [
        ('Beethoven 5th\n(c+Bb, VII chord)', log2(lcm(9, 5)), 'minor'),
        ("Stravinsky\nPetrushka (C+F#)", log2(lcm(45, 32)), 'bitonal'),
        ('Brahms\nChromatic mediants', log2(lcm(5, 4)), 'chromatic'),
        ('Bach\nModal mixture', log2(lcm(6, 5)), 'modal'),
        ('Milhaud\nPolytonality (full)', log2(lcm(15, 8)), 'polytonal'),
        ('Ligeti\nMicropolyphony', log2(lcm(16, 15)), 'spectral'),
    ]
    
    xvals = [e[1] for e in examples]
    yvals = np.random.uniform(0.5, 5.5, len(examples))  # scatter
    labels = [e[0] for e in examples]
    ecols = ['steelblue', 'firebrick', 'goldenrod', 'forestgreen', 'purple', 'darkorange']
    
    for x, y, label, col in zip(xvals, yvals, labels, ecols):
        ax_scatter.scatter(x, y, s=150, color=col, alpha=0.8, zorder=5)
        ax_scatter.annotate(label, (x, y), textcoords='offset points',
                           xytext=(8, 0), va='center', fontsize=8, color=col)
    
    ax_scatter.set_xlabel('log₂(LCM tonic complexity)')
    ax_scatter.set_ylabel('(examples sorted by complexity)')
    ax_scatter.set_title('Historical Examples\non Polytonality Spectrum', fontsize=10)
    ax_scatter.set_yticks([])
    ax_scatter.set_xlim(0, 12)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN: COMPOSE THE FIGURE
# ═══════════════════════════════════════════════════════════════════════════════

fig = plt.figure(figsize=(20, 24))
fig.patch.set_facecolor('#f8f8f8')

gs = gridspec.GridSpec(5, 2, figure=fig, hspace=0.55, wspace=0.35,
                       top=0.95, bottom=0.03, left=0.06, right=0.97)

# Row 0: Melodic expectation
ax_mel_E = fig.add_subplot(gs[0, 0])
ax_mel_F = fig.add_subplot(gs[0, 1])
plot_melodic_expectation(ax_mel_E, ax_mel_F)

# Row 1: Piece tensions — Pachelbel
ax_pach = fig.add_subplot(gs[1, 0])
ax_beet = fig.add_subplot(gs[1, 1])

# Row 2: Coltrane + missing fundamental waveforms
ax_colt = fig.add_subplot(gs[2, 0])
ax_miss_wave = fig.add_subplot(gs[2, 1])

plot_piece_tensions(ax_pach, ax_beet, ax_colt)
plot_missing_fundamental(ax_miss_wave, fig.add_subplot(gs[3, 0]))

# Row 3-4: Polytonality
ax_poly_bar = fig.add_subplot(gs[3, 1])
ax_poly_scatter = fig.add_subplot(gs[4, :])
plot_polytonality(ax_poly_scatter, ax_poly_bar)

# Master title
fig.suptitle(
    'Session 8 — Melodic Expectation, Real-Piece Tension, Missing Fundamental & Polytonality\n'
    'LCM + Proximity model fully deployed across melody, harmony, timbre, and key space',
    fontsize=13, fontweight='bold', y=0.98
)

out_path = '/Users/agent-one/projects/music-theory/visualizations/session8_full.png'
plt.savefig(out_path, dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close()
print(f"Saved: {out_path}")

# ─── Also: individual focused plots ──────────────────────────────────────────

# 1. Melodic expectation detailed
fig2, axes = plt.subplots(2, 2, figsize=(14, 10))
fig2.suptitle('Melodic Expectation Model — Note-by-Note Probability\n'
              'Combined LCM complexity + proximity gravity + melodic momentum', fontsize=12, fontweight='bold')

scale_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C5']
test_cases = [
    ('E', None, 'From E (no prior)'),
    ('E', 'F', 'From E (prior: F, falling)'),
    ('G', 'E', 'From G (prior: E, rising)'),
    ('B', 'A', 'From B — leading tone (prior: A)'),
]
colors_mel = ['steelblue', 'coral', 'forestgreen', 'goldenrod']

for (current, prev, title), color, ax in zip(test_cases, colors_mel, axes.flat):
    probs = compute_melodic_expectation(current, prev_note=prev)
    candidates = [n for n in scale_notes if n != current]
    probs_list = [probs.get(n, 0) for n in candidates]
    
    bars = ax.bar(range(len(candidates)), probs_list, color=color, alpha=0.8)
    ax.set_xticks(range(len(candidates)))
    ax.set_xticklabels(candidates)
    ax.set_title(title, fontsize=10)
    ax.set_ylabel('Probability')
    
    # Highlight tonic triad
    for i, note in enumerate(candidates):
        if note in TONIC_TRIAD or note == 'C5':
            bars[i].set_edgecolor('green')
            bars[i].set_linewidth(2.5)
    
    # Mark most likely
    max_p = max(probs_list)
    for i, (p, note) in enumerate(zip(probs_list, candidates)):
        if p == max_p:
            ax.text(i, p + 0.005, '★', ha='center', fontsize=12, color='darkgreen')
    
    ax.text(0.98, 0.95, '★ most likely\n□ tonic triad', transform=ax.transAxes,
            ha='right', va='top', fontsize=8, color='dimgray')

plt.tight_layout()
plt.savefig('/Users/agent-one/projects/music-theory/visualizations/melodic_expectation.png',
            dpi=120, bbox_inches='tight')
plt.close()
print("Saved: melodic_expectation.png")

# 2. Piece tension arcs — standalone
fig3, axes3 = plt.subplots(3, 1, figsize=(14, 12))
fig3.suptitle('Real-Piece Tension Analysis\nLCM-based tension arcs for three landmark works',
              fontsize=12, fontweight='bold')

for ax, prog, title, col in [
    (axes3[0], PACHELBEL, "Pachelbel Canon in D — I V vi iii IV I IV V", 'steelblue'),
    (axes3[1], BEETHOVEN_5TH, "Beethoven Symphony No. 5, mm. 1–8 (c minor)", 'firebrick'),
    (axes3[2], COLTRANE_GIANT_STEPS, "Coltrane — Giant Steps (B maj → G7 → E maj → C7 → Bb maj cycle)", 'forestgreen'),
]:
    tension_data = compute_piece_tension(prog)
    beats = [t[0] for t in tension_data]
    tensions = [t[1] for t in tension_data]
    labels = [t[2] for t in tension_data]
    
    ax.plot(beats, tensions, 'o-', color=col, linewidth=2.5, markersize=9, zorder=5)
    ax.fill_between(beats, min(tensions) - 0.1, tensions, alpha=0.18, color=col)
    
    for b, t, label in zip(beats, tensions, labels):
        ax.annotate(label, (b, t), textcoords='offset points',
                   xytext=(0, 12), ha='center', fontsize=9, fontweight='bold', color=col)
    
    ax.axhline(np.mean(tensions), color='gray', linestyle='--', alpha=0.5, linewidth=1)
    ax.text(beats[-1] + 0.1, np.mean(tensions), ' mean', fontsize=8, color='gray', va='center')
    
    ax.set_xticks(beats)
    ax.set_xticklabels([f'm.{i+1}' for i in beats])
    ax.set_ylabel('Tension (log₂-LCM)')
    ax.set_title(title, fontsize=10)
    ax.set_xlim(-0.5, len(beats) - 0.5)

plt.tight_layout()
plt.savefig('/Users/agent-one/projects/music-theory/visualizations/real_piece_tension.png',
            dpi=120, bbox_inches='tight')
plt.close()
print("Saved: real_piece_tension.png")

# 3. Missing fundamental — detailed
fig4, axes4 = plt.subplots(1, 2, figsize=(14, 6))
fig4.suptitle('The Missing Fundamental — LCM Predicts Auditory Completion',
              fontsize=12, fontweight='bold')

ax_wave = axes4[0]
ax_lcm_bar = axes4[1]

t = np.linspace(0, 0.05, 8000)
f0 = 110.0

for case in MISSING_FUND_CASES:
    harm = sorted(case['harmonics'])
    wave = np.zeros_like(t)
    for h in harm:
        wave += (1.0 / h) * np.sin(2 * np.pi * f0 * h * t)
    
    cur = int(harm[0])
    for h in harm[1:]:
        cur = lcm(cur, int(h))
    lcm_val = cur
    
    # Period at f0
    period_ms = (1000 / f0) * lcm_val
    clarity = 'Clear' if period_ms < 50 else ('Ambiguous' if period_ms < 200 else 'Unclear')
    case['lcm_period_ms'] = period_ms
    case['clarity'] = clarity
    case['lcm_val'] = lcm_val

# LCM bar chart
case_labels = [c['name'][:30] for c in MISSING_FUND_CASES]
lcm_periods = [c['lcm_period_ms'] for c in MISSING_FUND_CASES]
clarities = [c['clarity'] for c in MISSING_FUND_CASES]
bar_colors = ['forestgreen' if c == 'Clear' else 'goldenrod' if c == 'Ambiguous' else 'firebrick'
              for c in clarities]

bars = ax_lcm_bar.barh(range(len(MISSING_FUND_CASES)), lcm_periods, color=bar_colors, alpha=0.85)
ax_lcm_bar.set_yticks(range(len(MISSING_FUND_CASES)))
ax_lcm_bar.set_yticklabels([c['name'] for c in MISSING_FUND_CASES], fontsize=9)
ax_lcm_bar.set_xlabel('LCM period (ms at A=110Hz)')
ax_lcm_bar.set_title('LCM Period → Clarity of Missing Fundamental', fontsize=10)
ax_lcm_bar.axvline(50, color='gray', linestyle='--', alpha=0.5, label='~50ms clarity threshold')
ax_lcm_bar.legend(fontsize=8)

for i, (bar, case) in enumerate(zip(bars, MISSING_FUND_CASES)):
    ax_lcm_bar.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                   f"LCM={case['lcm_val']}, {case['clarity']}", va='center', fontsize=8)

# Waveform visualization
t_short = np.linspace(0, 0.025, 2000)
case = MISSING_FUND_CASES[1]  # barbershop 7th
harm = case['harmonics']
full = np.zeros_like(t_short)
missing = np.zeros_like(t_short)
for h in [1.0, 2.0, 3.0] + harm:
    full += (1.0/h) * np.sin(2 * np.pi * f0 * h * t_short)
for h in harm:
    missing += (1.0/h) * np.sin(2 * np.pi * f0 * h * t_short)

ax_wave.plot(t_short * 1000, full / max(abs(full)), color='steelblue', alpha=0.8,
             label='Full (harmonics 1–7)', linewidth=1.5)
ax_wave.plot(t_short * 1000, missing / max(abs(missing)) * 0.7, color='coral', alpha=0.8,
             label='Missing fund (4–7 only)', linewidth=1.5, linestyle='--')
ax_wave.set_xlabel('Time (ms)')
ax_wave.set_ylabel('Amplitude (normalized)')
ax_wave.set_title('Barbershop 7th Chord\nWith vs. Without Fundamental', fontsize=10)
ax_wave.legend(fontsize=9)
ax_wave.text(0.02, 0.05, 
             'The ear constructs the\nmissing fundamental from\nthe periodic envelope',
             transform=ax_wave.transAxes, fontsize=9, style='italic', color='gray')

plt.tight_layout()
plt.savefig('/Users/agent-one/projects/music-theory/visualizations/missing_fundamental.png',
            dpi=120, bbox_inches='tight')
plt.close()
print("Saved: missing_fundamental.png")

# 4. Polytonality
fig5, axes5 = plt.subplots(1, 2, figsize=(16, 7))
fig5.suptitle('Polytonality: LCM Complexity in Key Space\n'
              'Why Stravinsky\'s Petrushka "grinds" and the circle of fifths feels smooth',
              fontsize=12, fontweight='bold')
plot_polytonality(axes5[0], axes5[1])
plt.tight_layout()
plt.savefig('/Users/agent-one/projects/music-theory/visualizations/polytonality.png',
            dpi=120, bbox_inches='tight')
plt.close()
print("Saved: polytonality.png")

print("\n✓ All Session 8 visualizations complete.")
