"""
Session 5: Modulation Paths, Non-Western Scales, Chord Inversions, 
           Progression Entropy, Borrowed Chords
2026-03-02
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractions import Fraction
from math import gcd, lcm, log2
import itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "visualizations"
OUT.mkdir(exist_ok=True)

def interval_lcm(ratio):
    f = Fraction(ratio).limit_denominator(128)
    return lcm(f.numerator, f.denominator)

# ══════════════════════════════════════════════════════════════════
# 1. CIRCLE OF FIFTHS AS MINIMUM-LCM ADJACENCY GRAPH
# ══════════════════════════════════════════════════════════════════

def analyze_modulation_paths():
    print("=== Modulation as LCM-Minimum Path ===")
    
    # 12 major keys as scale degrees from C (0=C, 7=G, 2=D, 9=A, 4=E, 11=B,
    # 6=F#/Gb, 1=Db, 8=Ab, 3=Eb, 10=Bb, 5=F)
    key_semitones = list(range(12))
    key_names = ['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B']
    
    # Key similarity: fraction of shared notes between major scales
    major_scale_intervals = [0,2,4,5,7,9,11]
    
    def key_lcm_distance(k1, k2):
        """Complexity of modulating from key k1 to key k2.
        Model: interval between the two tonics, weighted by 
        how many notes they share (fewer shared = more cognitive distance)."""
        semis = abs(k1 - k2) % 12
        semis = min(semis, 12 - semis)  # shortest path in semitone space
        notes1 = set((k1 + i) % 12 for i in major_scale_intervals)
        notes2 = set((k2 + i) % 12 for i in major_scale_intervals)
        shared = len(notes1 & notes2)
        # Tonic interval complexity
        if semis == 0: ratio = Fraction(1)
        elif semis == 7: ratio = Fraction(3,2)
        elif semis == 5: ratio = Fraction(4,3)
        elif semis == 4: ratio = Fraction(5,4)
        elif semis == 3: ratio = Fraction(6,5)
        elif semis == 2: ratio = Fraction(9,8)
        elif semis == 1: ratio = Fraction(16,15)
        elif semis == 6: ratio = Fraction(45,32)
        elif semis == 9: ratio = Fraction(5,3)
        elif semis == 8: ratio = Fraction(8,5)
        elif semis == 10: ratio = Fraction(16,9)
        elif semis == 11: ratio = Fraction(15,8)
        else: ratio = Fraction(1)
        tonic_lcm = log2(lcm(ratio.numerator, ratio.denominator))
        note_penalty = (7 - shared) * 1.5  # each unshared note adds cost
        return tonic_lcm + note_penalty
    
    # Build distance matrix
    n = 12
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i][j] = key_lcm_distance(i, j)
    
    # Circle of fifths order
    cof_order = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
    cof_names = [key_names[i] for i in cof_order]
    
    # Nearest neighbor for each key
    print("\nNearest key (min modulation cost) for each key:")
    for i in range(12):
        distances = [(D[i][j], key_names[j]) for j in range(12) if j != i]
        distances.sort()
        top3 = [f"{n}({d:.1f})" for d,n in distances[:3]]
        print(f"  {key_names[i]:4s} → {', '.join(top3)}")
    
    # Verify circle of fifths = minimum adjacency
    cof_cost = D[0][7]  # C→G (fifth)
    tritone_cost = D[0][6]  # C→F# (tritone)
    minor2_cost = D[0][1]  # C→Db (minor second)
    print(f"\nC→G (fifth):        {cof_cost:.2f}")
    print(f"C→F# (tritone):     {tritone_cost:.2f}")
    print(f"C→Db (minor 2nd):   {minor2_cost:.2f}")
    print(f"CoF is minimum-cost adjacency: {cof_cost < tritone_cost and cof_cost < minor2_cost}")
    
    # Plot: heatmap of modulation costs (reordered by CoF)
    D_cof = D[np.ix_(cof_order, cof_order)]
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Modulation Paths: Circle of Fifths as Minimum-LCM Graph", 
                 fontsize=14, fontweight='bold')
    
    im = axes[0].imshow(D_cof, cmap='YlOrRd', aspect='auto')
    axes[0].set_xticks(range(12)); axes[0].set_xticklabels(cof_names, rotation=45)
    axes[0].set_yticks(range(12)); axes[0].set_yticklabels(cof_names)
    axes[0].set_title("Modulation Cost Matrix\n(circle-of-fifths order)", fontsize=11)
    plt.colorbar(im, ax=axes[0], label='LCM distance + note penalty')
    
    # Circle of fifths diagram with LCM distances
    ax2 = axes[1]
    angles = np.linspace(0, 2*np.pi, 12, endpoint=False) - np.pi/2
    xc, yc = np.cos(angles)*1.1, np.sin(angles)*1.1
    
    # Draw connections - adjacent (fifths, cost ~3), all others dimmer
    for i in range(12):
        for j in range(i+1, 12):
            xi, yi = np.cos(angles[i])*1.0, np.sin(angles[i])*1.0
            xj, yj = np.cos(angles[j])*1.0, np.sin(angles[j])*1.0
            cost_ij = D_cof[i][j]
            if abs(i-j) == 1 or abs(i-j) == 11:  # adjacent in CoF
                ax2.plot([xi,xj],[yi,yj],'g-',lw=3,alpha=0.7,zorder=1)
            elif cost_ij < 10:
                ax2.plot([xi,xj],[yi,yj],color='orange',lw=1,alpha=0.2,zorder=1)
    
    ax2.scatter(np.cos(angles)*1.0, np.sin(angles)*1.0, 
                s=350, c='white', edgecolors='black', lw=2, zorder=3)
    for i,(x,y,n) in enumerate(zip(xc, yc, cof_names)):
        ax2.annotate(n, (x-0.06, y-0.04), fontsize=11, fontweight='bold', ha='center')
    
    ax2.set_xlim(-1.5,1.5); ax2.set_ylim(-1.5,1.5)
    ax2.set_aspect('equal'); ax2.axis('off')
    ax2.set_title("Green = adjacent (cheapest modulations)\nOrange = secondary connections", 
                  fontsize=10)
    
    plt.tight_layout()
    plt.savefig(OUT/'modulation_paths.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: modulation_paths.png")

# ══════════════════════════════════════════════════════════════════
# 2. NON-WESTERN SCALES IN LCM SPACE
# ══════════════════════════════════════════════════════════════════

def analyze_non_western_scales():
    print("\n=== Non-Western Scales in LCM Space ===")
    
    semi_to_ji = {
        0:(1,1), 1:(16,15), 2:(9,8), 3:(6,5),
        4:(5,4), 5:(4,3), 6:(45,32), 7:(3,2),
        8:(8,5), 9:(5,3), 10:(16,9), 11:(15,8), 12:(2,1),
    }
    
    def scale_profile(semitones):
        return [log2(lcm(semi_to_ji[s][0], semi_to_ji[s][1])) for s in semitones]
    
    def scale_mean(semitones):
        return np.mean(scale_profile(semitones))
    
    scales = {
        # Western
        'Major (Ionian)':        [0,2,4,5,7,9,11,12],
        'Natural Minor':         [0,2,3,5,7,8,10,12],
        'Harmonic Minor':        [0,2,3,5,7,8,11,12],
        # Pentatonic
        'Major Pentatonic':      [0,2,4,7,9,12],
        'Minor Pentatonic':      [0,3,5,7,10,12],
        'Blues Scale':           [0,3,5,6,7,10,12],
        # Middle Eastern / Arabic (rough JI approximation)
        'Hijaz (Phrygian Dom)':  [0,1,4,5,7,8,10,12],  # b2, M3, P4, P5, b6, b7
        'Double Harmonic':       [0,1,4,5,7,8,11,12],   # Spanish/Byzantine
        # Japanese
        'Hirajoshi':             [0,2,3,7,8,12],
        'In Scale':              [0,1,5,7,8,12],
        # Indian (rough semi approximation)
        'Bhairav (Raga)':        [0,1,4,5,7,8,11,12],   # Double harmonic analog
        'Yaman (Raga)':          [0,2,4,6,7,9,11,12],   # Lydian analog
        # Whole tone + diminished
        'Whole Tone':            [0,2,4,6,8,10,12],
        'Octatonic (dim)':       [0,1,3,4,6,7,9,10,12],
    }
    
    print("\nScale complexity rankings:")
    ranked = sorted([(name, scale_mean(semis)) for name,semis in scales.items()],
                    key=lambda x:x[1])
    for name, m in ranked:
        bar = '█' * int(m * 2)
        print(f"  {m:.2f}  {bar:<12}  {name}")
    
    # Major pentatonic deep dive: WHY is it universally accessible?
    print("\nMajor Pentatonic analysis:")
    print("  Omitted from major scale: 4th (LCM=12) and 7th (LCM=120)")
    print("  The 4th creates tension as leading tone 'lower neighbor'")
    print("  The 7th creates tension as leading tone 'upper neighbor'")
    print("  Removing both = zero leading tones = no strong pull, just space")
    print("  Remaining notes: root(1), M2(LCM=72), M3(LCM=20), P5(LCM=6), M6(LCM=15)")
    print("  Mean complexity: {:.2f} vs Major: {:.2f}".format(
        scale_mean([0,2,4,7,9,12]), scale_mean([0,2,4,5,7,9,11,12])))
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Non-Western Scales in LCM Complexity Space", fontsize=14, fontweight='bold')
    
    # Panel 1: bar chart of mean complexity
    colors_by_origin = {
        'Major (Ionian)': '#3498db', 'Natural Minor': '#3498db', 
        'Harmonic Minor': '#3498db',
        'Major Pentatonic': '#27ae60', 'Minor Pentatonic': '#27ae60',
        'Blues Scale': '#27ae60',
        'Hijaz (Phrygian Dom)': '#e67e22', 'Double Harmonic': '#e67e22',
        'Hirajoshi': '#9b59b6', 'In Scale': '#9b59b6',
        'Bhairav (Raga)': '#e74c3c', 'Yaman (Raga)': '#e74c3c',
        'Whole Tone': '#95a5a6', 'Octatonic (dim)': '#95a5a6',
    }
    
    names = [n for n,m in ranked]
    means = [m for n,m in ranked]
    cols = [colors_by_origin.get(n, 'gray') for n in names]
    
    axes[0].barh(range(len(names)), means, color=cols, alpha=0.85, edgecolor='white')
    axes[0].set_yticks(range(len(names)))
    axes[0].set_yticklabels(names, fontsize=9)
    axes[0].set_xlabel("Mean log₂(LCM) complexity from root", fontsize=11)
    axes[0].set_title("Scale Complexity Rankings\n(blue=Western  green=Pentatonic  orange=Arabic  purple=Japanese  red=Indian)", 
                      fontsize=10)
    axes[0].axvline(scale_mean([0,2,4,5,7,9,11,12]), color='blue', ls='--', alpha=0.4, label='Major')
    axes[0].axvline(scale_mean([0,2,4,7,9,12]), color='green', ls='--', alpha=0.4, label='Maj Pent')
    axes[0].legend(fontsize=9)
    axes[0].grid(axis='x', alpha=0.3)
    
    # Panel 2: line profiles of selected scales
    ax2 = axes[1]
    selected = ['Major (Ionian)', 'Natural Minor', 'Major Pentatonic', 
                'Hijaz (Phrygian Dom)', 'Hirajoshi', 'Whole Tone']
    palette = ['#3498db','#2980b9','#27ae60','#e67e22','#9b59b6','#95a5a6']
    
    for name, col in zip(selected, palette):
        semis = scales[name]
        profile = scale_profile(semis)
        x = list(range(len(profile)))
        ax2.plot(x, profile, '-o', color=col, lw=2, ms=6, label=name, alpha=0.85)
    
    ax2.set_xlabel("Scale Degree Index", fontsize=11)
    ax2.set_ylabel("log₂(LCM) complexity from root", fontsize=11)
    ax2.set_title("Complexity Profiles: Selected Scales", fontsize=11)
    ax2.legend(fontsize=9, loc='upper left')
    ax2.grid(alpha=0.3)
    ax2.set_xticks(range(8))
    ax2.set_xticklabels(['1','2','3','4','5','6','7','8'], fontsize=10)
    
    plt.tight_layout()
    plt.savefig(OUT/'non_western_scales.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: non_western_scales.png")

# ══════════════════════════════════════════════════════════════════
# 3. CHORD INVERSIONS AND BASS-ROOTED COMPLEXITY
# ══════════════════════════════════════════════════════════════════

def analyze_inversions():
    print("\n=== Chord Inversions: Bass-Rooted Complexity ===")
    
    # C major triad: C=1, E=5/4, G=3/2
    # Root pos: bass=C  → intervals from bass: C-E (5:4, LCM=20), C-G (3:2, LCM=6), E-G (6:5, LCM=30)
    # 1st inv:  bass=E  → intervals from bass: E-G (6:5, LCM=30), E-C5 (8:5, LCM=40)
    # 2nd inv:  bass=G  → intervals from bass: G-C5 (4:3, LCM=12), G-E5 (5:3, LCM=15)
    
    inversions = {
        'Root position (C)': {
            'bass': 'C',
            'intervals_from_bass': [('C-E', 5/4), ('C-G', 3/2), ('E-G', 6/5)],
        },
        '1st inversion (E bass)': {
            'bass': 'E',
            'intervals_from_bass': [('E-G', 6/5), ('E-C5', 8/5), ('G-C5', 4/3)],
        },
        '2nd inversion (G bass)': {
            'bass': 'G',
            'intervals_from_bass': [('G-C5', 4/3), ('G-E5', 5/3), ('C5-E5', 5/4)],
        },
    }
    
    # Also do C7 inversions
    c7_inversions = {
        'C7 root (C bass)': [('C-E', 5/4), ('C-G', 3/2), ('C-Bb', 16/9), ('E-G', 6/5), ('E-Bb', 45/32), ('G-Bb', 16/9)],
        'C7 1st inv (E bass)': [('E-G', 6/5), ('E-Bb', 45/32), ('E-C5', 8/5), ('G-Bb', 16/9), ('G-C5', 4/3), ('Bb-C5', 9/8)],
        'C7 2nd inv (G bass)': [('G-Bb', 16/9), ('G-C5', 4/3), ('G-E5', 5/3), ('Bb-C5', 9/8), ('Bb-E5', 45/32), ('C5-E5', 5/4)],
        'C7 3rd inv (Bb bass)': [('Bb-C5', 9/8), ('Bb-E5', 45/32), ('Bb-G5', 5/3), ('C5-E5', 5/4), ('C5-G5', 3/2), ('E5-G5', 6/5)],
    }
    
    print("\nC major triad inversions (sum log₂-LCM from bass):")
    inversion_costs = {}
    for name, data in inversions.items():
        total = sum(log2(interval_lcm(r)) for _, r in data['intervals_from_bass'])
        # Weight: intervals involving the bass note count double
        bass_intervals = data['intervals_from_bass'][:2]  # first two involve bass
        bass_cost = sum(log2(interval_lcm(r)) for _, r in bass_intervals)
        other_cost = sum(log2(interval_lcm(r)) for _, r in data['intervals_from_bass'][2:])
        weighted = bass_cost * 2 + other_cost
        inversion_costs[name] = (total, weighted)
        print(f"  {name}: total={total:.2f}, bass-weighted={weighted:.2f}")
    
    print("\nC7 inversions (all pairwise, then bass-weighted):")
    c7_costs = {}
    for name, intervals in c7_inversions.items():
        total = sum(log2(interval_lcm(r)) for _, r in intervals)
        bass_intervals = intervals[:3]  # 3 intervals involving bass note in a 4-note chord
        bass_cost = sum(log2(interval_lcm(r)) for _, r in bass_intervals) * 2
        other_cost = sum(log2(interval_lcm(r)) for _, r in intervals[3:])
        weighted = bass_cost + other_cost
        c7_costs[name] = (total, weighted)
        print(f"  {name}: total={total:.2f}, bass-weighted={weighted:.2f}")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Chord Inversions: Bass-Rooted Complexity", fontsize=14, fontweight='bold')
    
    # C major inversions
    inv_names = list(inversion_costs.keys())
    totals = [inversion_costs[n][0] for n in inv_names]
    weighted = [inversion_costs[n][1] for n in inv_names]
    x = np.arange(3)
    axes[0].bar(x-0.2, totals, 0.35, label='Equal-weighted', color='#3498db', alpha=0.85)
    axes[0].bar(x+0.2, weighted, 0.35, label='Bass-weighted (×2)', color='#e74c3c', alpha=0.85)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([n.split('(')[0].strip() for n in inv_names], fontsize=10)
    axes[0].set_ylabel("Σ log₂(LCM)")
    axes[0].set_title("C Major Triad: Root vs 1st vs 2nd Inversion", fontsize=11)
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)
    
    # C7 inversions
    c7_names = list(c7_costs.keys())
    totals7 = [c7_costs[n][0] for n in c7_names]
    weighted7 = [c7_costs[n][1] for n in c7_names]
    x7 = np.arange(4)
    axes[1].bar(x7-0.2, totals7, 0.35, label='Equal-weighted', color='#3498db', alpha=0.85)
    axes[1].bar(x7+0.2, weighted7, 0.35, label='Bass-weighted (×2)', color='#e74c3c', alpha=0.85)
    axes[1].set_xticks(x7)
    axes[1].set_xticklabels(['Root','1st inv','2nd inv','3rd inv'], fontsize=10)
    axes[1].set_ylabel("Σ log₂(LCM)")
    axes[1].set_title("C7 Chord: All Four Inversions", fontsize=11)
    axes[1].legend()
    axes[1].grid(axis='y', alpha=0.3)
    
    for ax in axes:
        ax.text(0.5, -0.15, 
                "Higher bass-weighted cost = more 'weighty' / less stable inversion",
                transform=ax.transAxes, ha='center', fontsize=9, style='italic')
    
    plt.tight_layout()
    plt.savefig(OUT/'chord_inversions.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: chord_inversions.png")

# ══════════════════════════════════════════════════════════════════
# 4. INFORMATION ENTROPY OF CHORD PROGRESSIONS
# ══════════════════════════════════════════════════════════════════

def analyze_progression_entropy():
    print("\n=== Information Entropy of Chord Progressions ===")
    
    # Map chord complexity to "expectedness" in a key
    # Simple chords = expected; complex = surprising
    # P(chord) ∝ 1/complexity → high complexity = low prob = high surprise
    
    chord_cx = {
        'I':    14.4,  'ii':  18.4,  'iii': 17.9,  'IV': 14.4,
        'V':    15.9,  'V7':  30.0,  'vi':  14.9,  'vii°': 48.0,
        # Borrowed
        '♭VII': 18.0,  '♭VI': 20.0,  '♭III': 16.0,  'IV/IV': 22.0,
        # Secondary dominants
        'V/V':  18.0,  'V/IV': 18.0,
    }
    
    def progression_entropy(chord_seq):
        """Shannon entropy using complexity-inverse as probability proxy."""
        total_cx = sum(chord_cx.get(c, 20) for c in chord_seq)
        probs = [chord_cx.get(c, 20) / total_cx for c in chord_seq]
        entropy = -sum(p * log2(p) for p in probs if p > 0)
        return entropy
    
    def progression_surprise(chord_seq):
        """Surprise = average complexity-jump magnitude."""
        cxs = [chord_cx.get(c, 20) for c in chord_seq]
        diffs = [abs(cxs[i+1] - cxs[i]) for i in range(len(cxs)-1)]
        return np.mean(diffs) if diffs else 0
    
    progressions = {
        'I-I-I-I (tonic pedal)':       ['I','I','I','I'],
        'I-V-I-V (simple alternation)': ['I','V','I','V'],
        'I-V-vi-IV (pop axis)':         ['I','V','vi','IV'],
        'I-IV-V-I (classical)':         ['I','IV','V','I'],
        'I-vi-IV-V (doo-wop)':          ['I','vi','IV','V'],
        'ii-V7-I (jazz ii-V-I)':        ['ii','V7','I'],
        'I-V/V-V-I (classical ext)':    ['I','V/V','V','I'],
        'I-♭VII-IV-I (rock)':           ['I','♭VII','IV','I'],
        'I-♭VI-♭VII-I (epic)':          ['I','♭VI','♭VII','I'],
        'I-vii°-I-vii° (chromatic)':    ['I','vii°','I','vii°'],
    }
    
    results = []
    for name, seq in progressions.items():
        H = progression_entropy(seq)
        S = progression_surprise(seq)
        mean_cx = np.mean([chord_cx.get(c,20) for c in seq])
        results.append((name, H, S, mean_cx))
        print(f"  {name:40s} H={H:.2f}  surprise={S:.1f}  mean_cx={mean_cx:.1f}")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Information Entropy of Chord Progressions\n(Higher entropy = more complex/surprising)", 
                 fontsize=14, fontweight='bold')
    
    names = [r[0].split('(')[0].strip() for r in results]
    Hs = [r[1] for r in results]
    Ss = [r[2] for r in results]
    
    y = np.arange(len(results))
    axes[0].barh(y, Hs, color='#3498db', alpha=0.85, edgecolor='white')
    axes[0].set_yticks(y)
    axes[0].set_yticklabels(names, fontsize=9)
    axes[0].set_xlabel("Shannon Entropy (bits)", fontsize=11)
    axes[0].set_title("Progression Entropy\n(how evenly spread across complexity levels)", fontsize=11)
    axes[0].axvline(np.mean(Hs), color='red', ls='--', alpha=0.5, label='Mean')
    axes[0].legend()
    axes[0].grid(axis='x', alpha=0.3)
    
    # Scatter: entropy vs surprise
    axes[1].scatter(Hs, Ss, s=150, c=range(len(results)), cmap='viridis', 
                   edgecolors='black', lw=1, zorder=5)
    for i, (name, H, S, _) in enumerate(results):
        short = name.split('(')[0].strip()
        axes[1].annotate(short, (H, S), xytext=(H+0.01, S+0.3), fontsize=8)
    axes[1].set_xlabel("Entropy (bits)", fontsize=11)
    axes[1].set_ylabel("Mean Complexity Jump (surprise)", fontsize=11)
    axes[1].set_title("Entropy vs Surprise\n(High-high = complex jazz; Low-low = repetitive)", fontsize=11)
    axes[1].grid(alpha=0.3)
    
    # Quadrant labels
    H_mid, S_mid = np.median(Hs), np.median(Ss)
    axes[1].axvline(H_mid, color='gray', ls='--', alpha=0.3)
    axes[1].axhline(S_mid, color='gray', ls='--', alpha=0.3)
    axes[1].text(H_mid*0.95, S_mid*1.8, 'Predictable\nbut volatile', ha='right', fontsize=8, style='italic', alpha=0.5)
    axes[1].text(H_mid*1.05, S_mid*1.8, 'Unpredictable\n& volatile', ha='left', fontsize=8, style='italic', alpha=0.5)
    axes[1].text(H_mid*0.95, S_mid*0.3, 'Simple\n& stable', ha='right', fontsize=8, style='italic', alpha=0.5)
    axes[1].text(H_mid*1.05, S_mid*0.3, 'Varied\nbut smooth', ha='left', fontsize=8, style='italic', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(OUT/'progression_entropy.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: progression_entropy.png")

# ══════════════════════════════════════════════════════════════════
# 5. BORROWED CHORDS: COLOR EXPLAINED BY LCM PROFILE
# ══════════════════════════════════════════════════════════════════

def analyze_borrowed_chords():
    print("\n=== Borrowed Chords: Color from LCM Profile Shift ===")
    
    # In C major, diatonic chords have specific complexity profiles from tonic C
    # Borrowed chords come from C minor (parallel minor) or other modes
    
    # Root of each chord as a ratio from C=1 (just intonation)
    chord_roots = {
        # Diatonic C major
        'I   (C)':   1,   'ii  (Dm)': 9/8,  'iii (Em)': 5/4,
        'IV  (F)':   4/3, 'V   (G)':  3/2,  'vi  (Am)': 5/3,  
        'vii°(Bdim)': 15/8,
        # Borrowed from C minor / parallel modes
        '♭III (Eb)': 6/5, '♭VI (Ab)': 8/5,  '♭VII (Bb)': 16/9,
        'iv  (Fm)':  4/3,  # Same root as IV but minor quality = borrowed
    }
    
    def root_lcm(ratio):
        f = Fraction(ratio).limit_denominator(64)
        return log2(lcm(f.numerator, f.denominator))
    
    print("\nChord root LCM distance from tonic C:")
    diatonic = ['I   (C)', 'ii  (Dm)', 'iii (Em)', 'IV  (F)', 'V   (G)', 'vi  (Am)', 'vii°(Bdim)']
    borrowed = ['♭III (Eb)', '♭VI (Ab)', '♭VII (Bb)', 'iv  (Fm)']
    
    print("  Diatonic:")
    for name in diatonic:
        d = root_lcm(chord_roots[name])
        print(f"    {name:15s} root LCM complexity: {d:.2f}")
    print("  Borrowed:")
    for name in borrowed:
        d = root_lcm(chord_roots[name])
        equiv = next((dn for dn in diatonic if abs(chord_roots[dn] - chord_roots[name]) < 0.01), None)
        print(f"    {name:15s} root LCM complexity: {d:.2f}" + 
              (f"  (same root as {equiv})" if equiv else "  ← NEW root complexity"))
    
    # The key finding: ♭VII, ♭VI, ♭III all have roots with LCM distance 
    # that doesn't appear in the diatonic scale. They introduce genuinely new 
    # harmonic territory — the "color" is the arrival at an unexpected LCM point.
    
    # Measure "color" = distance from nearest diatonic root LCM
    diatonic_lcms = [root_lcm(chord_roots[n]) for n in diatonic]
    
    print("\nBorrowed chord 'color distance' from nearest diatonic root:")
    for name in borrowed:
        b_lcm = root_lcm(chord_roots[name])
        nearest = min(diatonic_lcms, key=lambda x: abs(x - b_lcm))
        color_dist = abs(b_lcm - nearest)
        print(f"  {name:15s}: LCM={b_lcm:.2f}, nearest diatonic={nearest:.2f}, color={color_dist:.2f}")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Borrowed Chords: Color as LCM Distance from Diatonic Space", 
                 fontsize=14, fontweight='bold')
    
    # Panel 1: LCM positions of all chord roots
    all_names = diatonic + borrowed
    all_lcms = [root_lcm(chord_roots[n]) for n in all_names]
    colors_b = ['#3498db']*len(diatonic) + ['#e74c3c']*len(borrowed)
    
    ax1 = axes[0]
    ax1.scatter(all_lcms, [0]*len(all_names), c=colors_b, s=250, 
               edgecolors='black', lw=1.5, zorder=5)
    for name, x_pos in zip(all_names, all_lcms):
        col = '#3498db' if name in diatonic else '#e74c3c'
        short = name.split('(')[0].strip()
        ax1.annotate(short, (x_pos, 0), xytext=(x_pos, 0.12 if name in diatonic else -0.15),
                    ha='center', fontsize=9, color=col, fontweight='bold',
                    arrowprops=dict(arrowstyle='-', color=col, lw=0.5))
    
    ax1.axhline(0, color='gray', lw=1, alpha=0.3)
    ax1.set_xlim(-0.2, 5.5)
    ax1.set_ylim(-0.4, 0.4)
    ax1.set_xlabel("log₂(LCM) distance from tonic", fontsize=11)
    ax1.set_title("Chord Root Positions in LCM Space\n(Blue=diatonic  Red=borrowed)", fontsize=11)
    ax1.set_yticks([])
    ax1.grid(axis='x', alpha=0.3)
    
    # Panel 2: "Color intensity" bar chart
    ax2 = axes[1]
    b_lcms = [root_lcm(chord_roots[n]) for n in borrowed]
    color_distances = [abs(b - min(diatonic_lcms, key=lambda x: abs(x-b))) for b in b_lcms]
    b_short = [n.split('(')[0].strip() for n in borrowed]
    
    bars = ax2.bar(range(len(borrowed)), color_distances, 
                  color=['#e74c3c','#c0392b','#e67e22','#d35400'], 
                  alpha=0.85, edgecolor='white')
    ax2.set_xticks(range(len(borrowed)))
    ax2.set_xticklabels(b_short, fontsize=11)
    ax2.set_ylabel("Distance from nearest diatonic LCM point")
    ax2.set_title("'Color Intensity' of Borrowed Chords\n(higher = more surprising, more colorful)", fontsize=11)
    ax2.grid(axis='y', alpha=0.3)
    
    # Annotate famous usage
    usage = ['Vs resolution\n(epic moments)', 'Vs picardy third\n(finales)', 'vs V\n(rock anthems)', 'Minor subdominant\n(melancholy)']
    for i,(bar,u) in enumerate(zip(bars, usage)):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.01,
                u, ha='center', fontsize=8, style='italic', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig(OUT/'borrowed_chords.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: borrowed_chords.png")

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Music Theory Session 5 — Modulation, Non-Western Scales, Entropy")
    print("="*60)
    analyze_modulation_paths()
    analyze_non_western_scales()
    analyze_inversions()
    analyze_progression_entropy()
    analyze_borrowed_chords()
    print("\n" + "="*60)
    print("Session 5 complete.")
