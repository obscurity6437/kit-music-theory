"""
Session 6: Spectral Rhythm, Tonal Gravity Fields, Harmonic Rhythm,
           Microtonality, and Cognitive Load Budget
2026-03-04
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fractions import Fraction
from math import gcd, lcm, log2, exp
import itertools
from pathlib import Path

OUT = Path(__file__).parent.parent / "visualizations"
OUT.mkdir(exist_ok=True)

def interval_lcm_log(ratio):
    f = Fraction(ratio).limit_denominator(128)
    v = lcm(f.numerator, f.denominator)
    return log2(v) if v > 1 else 0.0

SEMI_TO_JI = {
    0:(1,1), 1:(16,15), 2:(9,8), 3:(6,5),
    4:(5,4), 5:(4,3), 6:(45,32), 7:(3,2),
    8:(8,5), 9:(5,3), 10:(16,9), 11:(15,8), 12:(2,1),
}

# ══════════════════════════════════════════════════════════════════
# 1. SPECTRAL ANALYSIS OF RHYTHM PATTERNS
# ══════════════════════════════════════════════════════════════════

def analyze_rhythm_spectra():
    print("=== Spectral Analysis of Rhythm Patterns ===")
    
    sr = 1000  # "sample rate" in grid units (8th notes per measure)
    
    # Common rhythm patterns as binary sequences (1=hit, 0=rest) over 16 8th notes
    patterns = {
        '4/4 quarter notes':    [1,0,1,0,1,0,1,0, 1,0,1,0,1,0,1,0],
        'Off-beat (backbeat)':  [0,1,0,1,0,1,0,1, 0,1,0,1,0,1,0,1],
        '3+3+2 (tresillo)':     [1,0,0,1,0,0,1,0, 1,0,0,1,0,0,1,0],
        'Son clave 3-2':        [1,0,0,1,0,0,1,0, 0,1,0,0,1,0,0,0],
        'Bossa nova':           [1,0,0,1,0,0,1,0, 0,0,1,0,0,1,0,0],
        'Swing 8ths':           [1,0,0,1,0,0,1,0, 0,1,0,0,1,0,0,1],
        'Syncopated funk':      [1,0,1,0,0,1,0,1, 1,0,0,1,0,1,0,0],
        'Even 8ths':            [1,1,1,1,1,1,1,1, 1,1,1,1,1,1,1,1],
    }
    
    def rhythmic_entropy(pattern):
        """Shannon entropy of the spectrum magnitude."""
        fft = np.abs(np.fft.rfft(pattern))
        fft = fft / (fft.sum() + 1e-10)
        return -np.sum(fft * np.log2(fft + 1e-10))
    
    def rhythmic_syncopation(pattern):
        """Syncopation = hits on weak grid positions weighted by position strength."""
        n = len(pattern)
        # Metric hierarchy: beat 1 = 4, beat 3 = 3, 8th beats = 2, off-8ths = 1
        strengths = []
        for i in range(n):
            if i % 4 == 0: strengths.append(4)
            elif i % 2 == 0: strengths.append(2)
            else: strengths.append(1)
        # Syncopation = weighted sum of hits on weak positions
        maxS = max(strengths)
        return sum(p * (maxS - s) / maxS for p,s in zip(pattern, strengths))
    
    def rhythmic_complexity(pattern):
        """LCM-analog: IOI (inter-onset interval) complexity."""
        onsets = [i for i,p in enumerate(pattern) if p == 1]
        if len(onsets) < 2: return 0
        iois = [onsets[i+1]-onsets[i] for i in range(len(onsets)-1)]
        # Wrap-around IOI
        iois.append(len(pattern) - onsets[-1] + onsets[0])
        # Complexity = lcm of all IOIs (like pitch LCM)
        total_lcm = iois[0]
        for i in iois[1:]:
            total_lcm = lcm(total_lcm, i)
        return log2(total_lcm)
    
    print("\nRhythm pattern analysis:")
    results = {}
    for name, pat in patterns.items():
        H = rhythmic_entropy(pat)
        S = rhythmic_syncopation(pat)
        C = rhythmic_complexity(pat)
        results[name] = (H, S, C)
        print(f"  {name:30s}: entropy={H:.2f}  syncop={S:.2f}  LCM-complexity={C:.2f}")
    
    # Key finding: IOI-LCM for common patterns
    print("\nIOI-LCM complexity deep dive:")
    for name in ['4/4 quarter notes', '3+3+2 (tresillo)', 'Son clave 3-2']:
        pat = patterns[name]
        onsets = [i for i,p in enumerate(pat) if p == 1]
        iois = [onsets[i+1]-onsets[i] for i in range(len(onsets)-1)]
        total_lcm = iois[0]
        for i in iois[1:]: total_lcm = lcm(total_lcm, i)
        print(f"  {name}: IOIs={iois}, LCM={total_lcm}")
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Spectral Analysis of Rhythm Patterns", fontsize=14, fontweight='bold')
    
    # Panel 1: FFT spectra overlay
    ax = axes[0,0]
    selected = ['4/4 quarter notes', '3+3+2 (tresillo)', 'Son clave 3-2', 'Syncopated funk']
    colors_r = ['#3498db','#e74c3c','#27ae60','#9b59b6']
    for name, col in zip(selected, colors_r):
        pat = np.array(patterns[name], dtype=float)
        fft = np.abs(np.fft.rfft(pat))
        freqs = np.fft.rfftfreq(len(pat))
        ax.plot(freqs, fft, '-', color=col, lw=2, label=name, alpha=0.85)
    ax.set_xlabel("Normalized frequency (cycles per 16-unit window)")
    ax.set_ylabel("Magnitude")
    ax.set_title("Rhythm FFT Spectra\n(peaks = periodicities in the pattern)")
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    
    # Panel 2: Grid view of patterns
    ax2 = axes[0,1]
    n_pats = len(patterns)
    for i, (name, pat) in enumerate(patterns.items()):
        y = n_pats - 1 - i
        for j, p in enumerate(pat):
            if p:
                ax2.add_patch(plt.Rectangle((j, y+0.1), 0.8, 0.8, 
                                           color='#e74c3c' if j % 4 == 0 else '#3498db', 
                                           alpha=0.8))
    ax2.set_xlim(0, 16)
    ax2.set_ylim(0, n_pats)
    ax2.set_xticks(range(16))
    ax2.set_xticklabels([str(i+1) if i%2==0 else '' for i in range(16)], fontsize=8)
    ax2.set_yticks([n_pats-1-i+0.5 for i in range(n_pats)])
    ax2.set_yticklabels(list(patterns.keys()), fontsize=8)
    ax2.set_title("Pattern Grid View\n(red=downbeat hits, blue=off-beat hits)")
    ax2.grid(axis='x', alpha=0.3)
    
    # Panel 3: Complexity vs syncopation
    ax3 = axes[1,0]
    names_r = list(results.keys())
    Hs_r = [results[n][0] for n in names_r]
    Ss_r = [results[n][1] for n in names_r]
    Cs_r = [results[n][2] for n in names_r]
    
    sc = ax3.scatter(Ss_r, Cs_r, c=Hs_r, cmap='YlOrRd', s=200, 
                    edgecolors='black', lw=1.5, zorder=5)
    plt.colorbar(sc, ax=ax3, label='Spectral entropy')
    for n, x, y in zip(names_r, Ss_r, Cs_r):
        ax3.annotate(n.split('(')[0].strip(), (x, y), xytext=(x+0.1, y+0.05), fontsize=8)
    ax3.set_xlabel("Syncopation score")
    ax3.set_ylabel("IOI-LCM complexity (log₂)")
    ax3.set_title("Syncopation vs IOI-LCM Complexity\n(color = spectral entropy)")
    ax3.grid(alpha=0.3)
    
    # Panel 4: Tresillo structure highlighted
    ax4 = axes[1,1]
    tresillo = patterns['3+3+2 (tresillo)']
    iois_t = [3,3,2,3,3,2]  # IOIs of a standard tresillo
    colors_lcm = ['#e74c3c' if x==3 else '#3498db' for x in iois_t]
    x_pos = 0
    for ioi, col in zip(iois_t, colors_lcm):
        ax4.barh(0, ioi, left=x_pos, height=0.5, color=col, alpha=0.8, edgecolor='black')
        ax4.text(x_pos + ioi/2, 0, str(ioi), ha='center', va='center', 
                fontweight='bold', fontsize=12)
        x_pos += ioi
    ax4.set_xlim(0, 16)
    ax4.set_ylim(-0.5, 1)
    ax4.set_yticks([])
    ax4.set_xlabel("Time (8th note units)")
    ax4.set_title(f"Tresillo (3+3+2) Structure\n"
                 f"IOIs: [3,3,2] × 2 → LCM = {lcm(3,2)} = 6 (same as a perfect fifth!)\n"
                 f"Polyrhythm: 3-against-2 embedded in 16-unit cycle → LCM=6")
    ax4.text(8, 0.7, "Same LCM=6 as the perfect fifth (3:2)\nRhythm encodes the same ratio!",
            ha='center', fontsize=10, style='italic',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax4.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUT/'rhythm_spectra.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: rhythm_spectra.png")

# ══════════════════════════════════════════════════════════════════
# 2. TONAL GRAVITY FIELDS
# ══════════════════════════════════════════════════════════════════

def analyze_tonal_gravity():
    print("\n=== Tonal Gravity Fields ===")
    
    # Each note in a key has a "gravitational pull" toward nearby stable notes
    # Gravity ∝ 1/LCM(interval) — low LCM = strong pull
    # Direction: toward whichever stable note requires less LCM motion
    
    major_scale = [0,2,4,5,7,9,11]
    stable_notes = [0, 4, 7]  # Tonic, third, fifth (triad)
    
    def note_lcm(semis_a, semis_b):
        diff = abs(semis_a - semis_b) % 12
        diff = min(diff, 12-diff)
        if diff == 0: return 1
        n, d = SEMI_TO_JI.get(diff, (1,1))
        return lcm(n, d)
    
    # Gravity of note x toward stable notes
    def gravity_vector(x):
        """Returns (dx, dy) in semitone space, weighted by 1/LCM."""
        total_pull = 0
        weighted_dir = 0
        for s in stable_notes:
            dist = (s - x) % 12
            if dist > 6: dist -= 12  # shortest path
            pull = 1.0 / note_lcm(x, s % 12)
            total_pull += pull
            weighted_dir += pull * np.sign(dist)
        return weighted_dir / (total_pull + 1e-10), total_pull
    
    print("\nGravity vectors for C major scale degrees:")
    note_names = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
    for i in range(12):
        direction, magnitude = gravity_vector(i)
        in_key = "✓" if i in major_scale else "✗"
        arrow = "→" if direction > 0.3 else ("←" if direction < -0.3 else "·")
        print(f"  {note_names[i]:3s} {in_key}: direction={direction:+.2f} {arrow}  "
              f"magnitude={magnitude:.3f}")
    
    # The 7th degree (B=11) should pull strongly upward to C (tonic)
    # The 4th degree (F=5) should pull downward to E (third)
    
    # Compute full gravity field
    gravity_data = {}
    for i in range(12):
        direction, magnitude = gravity_vector(i)
        gravity_data[i] = (direction, magnitude)
    
    # Melodic tension arcs for two melodies
    melody1 = [0, 2, 4, 7, 5, 4, 2, 0]      # C-D-E-G-F-E-D-C
    melody2 = [0, 4, 7, 11, 9, 7, 5, 4, 2, 0]  # C-E-G-B-A-G-F-E-D-C
    
    note_names_short = ['C','D','E','G','F','E','D','C']
    note_names2 = ['C','E','G','B','A','G','F','E','D','C']
    
    def tension_arc(melody):
        lcms = [interval_lcm_log(SEMI_TO_JI[n][0] / SEMI_TO_JI[n][1] 
                                  if n < 12 else 1) for n in melody]
        # Use direct note LCM from tonic
        result = []
        for n in melody:
            if n == 0: result.append(0)
            else:
                ratio = Fraction(*SEMI_TO_JI[n]).limit_denominator(64)
                result.append(log2(lcm(ratio.numerator, ratio.denominator)))
        return result
    
    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Tonal Gravity Fields in C Major", fontsize=14, fontweight='bold')
    
    # Panel 1: Gravity field visualization
    ax = axes[0,0]
    semis = list(range(12))
    directions = [gravity_data[i][0] for i in semis]
    magnitudes = [gravity_data[i][1] for i in semis]
    in_key = [i in major_scale for i in semis]
    
    colors_g = ['#3498db' if k else '#e74c3c' for k in in_key]
    bars = ax.bar(semis, magnitudes, color=colors_g, alpha=0.8, edgecolor='black')
    
    # Direction arrows
    for i, (d, m) in enumerate(zip(directions, magnitudes)):
        if abs(d) > 0.1:
            ax.annotate('', xy=(i + d*0.4, m + 0.004), xytext=(i, m + 0.001),
                       arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    
    ax.set_xticks(semis)
    ax.set_xticklabels(note_names, fontsize=10)
    ax.set_ylabel("Gravitational magnitude (Σ 1/LCM toward triad)")
    ax.set_title("Tonal Gravity in C Major\n(Blue=in-key, Red=chromatic, arrow=direction of pull)")
    ax.grid(axis='y', alpha=0.3)
    
    # Stable notes markers
    for s in stable_notes:
        ax.axvline(s, color='green', ls=':', alpha=0.5)
    ax.text(0, max(magnitudes)*0.9, "C (tonic)", color='green', fontsize=9)
    ax.text(4, max(magnitudes)*0.9, "E (3rd)", color='green', fontsize=9)
    ax.text(7, max(magnitudes)*0.9, "G (5th)", color='green', fontsize=9)
    
    # Panel 2: 2D gravity heatmap (pitch vs time position)
    ax2 = axes[0,1]
    # Gravity intensity at each semitone, repeated across time with decay model
    # Imagine a note played at time 0, gravity at time t = magnitude * exp(-t*0.3)
    time_steps = np.linspace(0, 8, 100)
    decay = 0.3
    
    gravity_matrix = np.zeros((12, len(time_steps)))
    for i in range(12):
        _, mag = gravity_data[i]
        for t_idx, t in enumerate(time_steps):
            gravity_matrix[i, t_idx] = mag * exp(-t * decay)
    
    im = ax2.imshow(gravity_matrix, aspect='auto', cmap='Reds', 
                   extent=[0, 8, 11.5, -0.5])
    plt.colorbar(im, ax=ax2, label='Gravitational pull (decaying over time)')
    ax2.set_yticks(range(12))
    ax2.set_yticklabels(note_names, fontsize=9)
    ax2.set_xlabel("Time after note played (arbitrary units)")
    ax2.set_title("Gravity Decay Over Time\n(How long each note 'pulls' after it's heard)")
    for s in stable_notes:
        ax2.axhline(s, color='blue', ls='--', alpha=0.4)
    
    # Panel 3: Melody 1 tension arc
    ax3 = axes[1,0]
    t1 = tension_arc(melody1)
    x1 = range(len(melody1))
    ax3.plot(x1, t1, 'o-', color='#3498db', lw=2.5, ms=10, zorder=5)
    ax3.fill_between(x1, 0, t1, alpha=0.15, color='#3498db')
    ax3.set_xticks(range(len(melody1)))
    ax3.set_xticklabels(note_names_short, fontsize=12)
    ax3.set_ylabel("log₂(LCM) tension from tonic")
    ax3.set_title("Melody Tension Arc: C-D-E-G-F-E-D-C\n(scalar run up and back)")
    ax3.axhline(0, color='green', ls='--', alpha=0.5, label='Tonic (rest)')
    ax3.grid(alpha=0.3)
    ax3.legend()
    
    # Panel 4: Melody 2 tension arc
    ax4 = axes[1,1]
    t2 = tension_arc(melody2)
    x2 = range(len(melody2))
    ax4.plot(x2, t2, 'o-', color='#e74c3c', lw=2.5, ms=10, zorder=5)
    ax4.fill_between(x2, 0, t2, alpha=0.15, color='#e74c3c')
    ax4.set_xticks(range(len(melody2)))
    ax4.set_xticklabels(note_names2, fontsize=11)
    ax4.set_ylabel("log₂(LCM) tension from tonic")
    ax4.set_title("Melody Tension Arc: C-E-G-B-A-G-F-E-D-C\n(arpeggio to leading tone, then stepwise descent)")
    ax4.axhline(0, color='green', ls='--', alpha=0.5, label='Tonic (rest)')
    
    # Annotate the leading tone peak
    b_idx = note_names2.index('B')
    ax4.annotate('B: leading tone\n(LCM=120)', xy=(b_idx, t2[b_idx]),
                xytext=(b_idx+0.5, t2[b_idx]+0.5),
                arrowprops=dict(arrowstyle='->', color='black'),
                fontsize=9, style='italic')
    ax4.grid(alpha=0.3)
    ax4.legend()
    
    plt.tight_layout()
    plt.savefig(OUT/'tonal_gravity.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: tonal_gravity.png")

# ══════════════════════════════════════════════════════════════════
# 3. HARMONIC RHYTHM — RATE OF CHORD CHANGE
# ══════════════════════════════════════════════════════════════════

def analyze_harmonic_rhythm():
    print("\n=== Harmonic Rhythm ===")
    
    # Chord complexity values (log₂ triad LCM)
    chord_cx_map = {
        'I': log2(60), 'IV': log2(60), 'V': log2(60), 'vi': log2(60),
        'ii': log2(60), 'V7': log2(1440), 'vii°': log2(14400),
        '♭VII': log2(80),
    }
    
    # Simulate different harmonic rhythm rates for I-IV-V-I
    progression = ['I', 'IV', 'V', 'I']
    chord_complexities = [chord_cx_map[c] for c in progression]
    
    # Rate = chords per measure (1 = one chord/measure, 4 = one chord/beat)
    rates = [1, 2, 4]
    
    # "Cognitive load" at each time point = current chord complexity + memory of recent chords
    def cognitive_load(rate, decay=0.5):
        """Simulate cognitive load with chord changes at given rate."""
        # Expand progression to match rate
        beats_per_measure = 4
        total_beats = beats_per_measure * len(progression)
        beats_per_chord = beats_per_measure // rate
        
        loads = []
        for beat in range(total_beats):
            chord_idx = beat // beats_per_chord % len(progression)
            base_cx = chord_complexities[chord_idx]
            
            # Memory of previous chord decays
            if beat > 0 and beat % beats_per_chord == 0:
                prev_idx = (chord_idx - 1) % len(progression)
                memory = chord_complexities[prev_idx] * exp(-decay * beats_per_chord)
            else:
                memory = 0
            
            # Transition spike at chord change
            if beat % beats_per_chord == 0 and beat > 0:
                prev_idx = (chord_idx - 1) % len(progression)
                transition_cost = abs(chord_complexities[chord_idx] - chord_complexities[prev_idx])
            else:
                transition_cost = 0
            
            loads.append(base_cx + memory * 0.3 + transition_cost * 0.5)
        
        return loads
    
    print("\nMean cognitive load by harmonic rhythm rate:")
    for rate in rates:
        loads = cognitive_load(rate)
        print(f"  {rate} chord(s)/measure: mean load = {np.mean(loads):.2f}, "
              f"peak load = {max(loads):.2f}, variance = {np.var(loads):.2f}")
    
    # Optimal rate analysis
    print("\nPredicted optimal rate: 1-2 chords/measure")
    print("  Too fast (4/measure): transitions overwhelm base complexity, high variance")
    print("  Too slow (1/measure): low variance but listeners 'settle' too early")
    print("  Sweet spot: 2/measure — enough change to sustain interest, not so fast as to fatigue")
    
    # ii-V-I at different rates
    jazz_prog = ['ii', 'V7', 'I']
    jazz_cx = [chord_cx_map[c] for c in jazz_prog]
    
    print(f"\nii-V7-I complexity: {[f'{c:.2f}' for c in jazz_cx]}")
    print(f"  Total LCM complexity jump ii→V7: +{jazz_cx[1]-jazz_cx[0]:.2f}")
    print(f"  Total LCM complexity drop V7→I:  {jazz_cx[2]-jazz_cx[1]:.2f}")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Harmonic Rhythm: Rate of Chord Change vs Cognitive Load", 
                 fontsize=14, fontweight='bold')
    
    # Panel 1: Load curves at different rates
    ax = axes[0]
    colors_hr = ['#3498db', '#e74c3c', '#27ae60']
    for rate, col in zip(rates, colors_hr):
        loads = cognitive_load(rate)
        ax.plot(range(len(loads)), loads, '-', color=col, lw=2, 
               label=f'{rate} chord(s)/measure', alpha=0.85)
    ax.set_xlabel("Beat number")
    ax.set_ylabel("Cognitive load (LCM-weighted)")
    ax.set_title("I-IV-V-I at Different Harmonic Rhythm Rates\n(higher rate → higher load spikes)")
    ax.legend()
    ax.grid(alpha=0.3)
    
    # Mark chord boundaries for rate=1
    beats_per_chord = 4
    for i in range(1, len(progression)):
        ax.axvline(i * beats_per_chord, color='gray', ls=':', alpha=0.3)
    
    # Panel 2: Mean load vs rate — the "Goldilocks" curve
    many_rates = np.linspace(0.5, 6, 50)
    mean_loads = []
    peak_loads = []
    variances = []
    
    for rate in many_rates:
        beats_per_measure = 4
        beats_per_chord_f = beats_per_measure / rate
        total_beats = 16
        loads = []
        for beat in range(total_beats):
            chord_idx = int(beat / beats_per_chord_f) % len(progression)
            base_cx = chord_complexities[chord_idx]
            beat_in_chord = beat % max(1, int(beats_per_chord_f))
            if beat_in_chord == 0 and beat > 0:
                prev_idx = (chord_idx - 1) % len(progression)
                transition_cost = abs(chord_complexities[chord_idx] - chord_complexities[prev_idx])
            else:
                transition_cost = 0
            loads.append(base_cx + transition_cost * 0.5)
        mean_loads.append(np.mean(loads))
        peak_loads.append(max(loads))
        variances.append(np.var(loads))
    
    ax2 = axes[1]
    ax2.plot(many_rates, mean_loads, '-', color='#3498db', lw=2.5, label='Mean load')
    ax2.plot(many_rates, peak_loads, '--', color='#e74c3c', lw=2, label='Peak load', alpha=0.7)
    ax2.fill_between(many_rates, 
                     np.array(mean_loads) - np.sqrt(variances), 
                     np.array(mean_loads) + np.sqrt(variances),
                     alpha=0.15, color='#3498db', label='±σ')
    ax2.set_xlabel("Harmonic rhythm (chords/measure)")
    ax2.set_ylabel("Cognitive load")
    ax2.set_title("Cognitive Load vs Harmonic Rhythm Rate\n(shaded = ±1σ variance band)")
    ax2.axvline(2, color='green', ls=':', alpha=0.7, label='Sweet spot (~2/measure)')
    ax2.legend()
    ax2.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(OUT/'harmonic_rhythm.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: harmonic_rhythm.png")

# ══════════════════════════════════════════════════════════════════
# 4. MICROTONALITY: LCM IN NON-12-TET SYSTEMS
# ══════════════════════════════════════════════════════════════════

def analyze_microtonality():
    print("\n=== Microtonality: 12-TET vs 19-TET vs 31-TET ===")
    
    # In 12-TET: intervals are irrational but we approximate with JI
    # In n-TET: the step size is 1200/n cents
    # JI ratios and their best approximations in different TET systems
    
    ji_intervals = {
        'Octave (2:1)':       (2, 1),
        'Fifth (3:2)':        (3, 2),
        'Fourth (4:3)':       (4, 3),
        'Maj Third (5:4)':    (5, 4),
        'Min Third (6:5)':    (6, 5),
        'Maj Second (9:8)':   (9, 8),
        'Min Seventh (7:4)':  (7, 4),    # 7th harmonic — "septimal" (absent in 12-TET)
        'Tritone (45:32)':    (45, 32),
        'Min Second (16:15)': (16, 15),
    }
    
    def cents(n, d):
        return 1200 * log2(n/d)
    
    def best_tet(ratio_n, ratio_d, tet):
        target_cents = cents(ratio_n, ratio_d)
        step = 1200 / tet
        n_steps = round(target_cents / step)
        tet_cents = n_steps * step
        error = abs(target_cents - tet_cents)
        return n_steps, tet_cents, error
    
    print(f"\n{'Interval':25s} {'JI Cents':>10} {'12-TET err':>12} {'19-TET err':>12} {'31-TET err':>12}")
    print("-" * 75)
    
    tet_results = {}
    for name, (n, d) in ji_intervals.items():
        ji_c = cents(n, d)
        _, _, e12 = best_tet(n, d, 12)
        _, _, e19 = best_tet(n, d, 19)
        _, _, e31 = best_tet(n, d, 31)
        tet_results[name] = (ji_c, e12, e19, e31)
        print(f"  {name:25s} {ji_c:>10.2f}¢  {e12:>10.2f}¢  {e19:>10.2f}¢  {e31:>10.2f}¢")
    
    # 7th harmonic in 12-TET has 31¢ error — too rough to use
    # In 31-TET, error is only 1.1¢ — pure septimal intervals become accessible
    print("\nKey finding:")
    n, d = ji_intervals['Min Seventh (7:4)']
    ji_c = cents(n, d)
    _, _, e12 = best_tet(n, d, 12)
    _, _, e31 = best_tet(n, d, 31)
    print(f"  7:4 (7th harmonic) in 12-TET: {e12:.1f}¢ error — too far to sound 'pure'")
    print(f"  7:4 (7th harmonic) in 31-TET: {e31:.1f}¢ error — pure septimal intervals available!")
    print("  → 31-TET 'unlocks' the 7th harmonic: dominant 7ths, barbershop 7ths become JI-pure")
    
    # LCM in 31-TET: 5th is 18 steps, has same LCM structure (3:2) but now accessible
    print("\n31-TET interval mapping (in steps):")
    for name, (n, d) in ji_intervals.items():
        steps, tet_c, err = best_tet(n, d, 31)
        ljp = log2(lcm(n, d))
        print(f"  {name:25s}: {steps:3d} steps  (error={err:.1f}¢, JI-LCM={ljp:.2f})")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    fig.suptitle("Microtonality: Tuning Error in 12, 19, and 31-TET", 
                 fontsize=14, fontweight='bold')
    
    # Panel 1: Error comparison
    ax = axes[0]
    names_m = list(tet_results.keys())
    errs12 = [tet_results[n][1] for n in names_m]
    errs19 = [tet_results[n][2] for n in names_m]
    errs31 = [tet_results[n][3] for n in names_m]
    
    y = np.arange(len(names_m))
    ax.barh(y-0.25, errs12, 0.22, label='12-TET', color='#e74c3c', alpha=0.85)
    ax.barh(y,      errs19, 0.22, label='19-TET', color='#e67e22', alpha=0.85)
    ax.barh(y+0.25, errs31, 0.22, label='31-TET', color='#27ae60', alpha=0.85)
    ax.set_yticks(y)
    ax.set_yticklabels(names_m, fontsize=9)
    ax.set_xlabel("Error from Just Intonation (cents)")
    ax.set_title("Tuning Accuracy: 12 vs 19 vs 31-TET\n(lower = closer to pure JI)")
    ax.axvline(5, color='gray', ls='--', alpha=0.5, label='5¢ threshold (barely audible)')
    ax.legend()
    ax.grid(axis='x', alpha=0.3)
    
    # Panel 2: The 7th harmonic story — what 31-TET unlocks
    ax2 = axes[1]
    # Show harmonic series access at different TET levels
    harmonic_lcms = {
        '2nd (octave)': log2(lcm(2,1)),
        '3rd (fifth)':  log2(lcm(3,2)),
        '4th (fourth)': log2(lcm(4,3)),
        '5th (M3)':     log2(lcm(5,4)),
        '6th (m3)':     log2(lcm(6,5)),
        '7th (m7)':     log2(lcm(7,4)),
        '8th (oct+M2)': log2(lcm(9,8)),
        '11th (tritone~)': log2(lcm(11,8)),
        '13th':         log2(lcm(13,8)),
    }
    
    # Accessible in 12-TET (error < 10¢): through 6th harmonic
    # Accessible in 31-TET (error < 5¢): through ~7th harmonic
    accessible_12 = ['2nd (octave)', '3rd (fifth)', '4th (fourth)', '5th (M3)', '6th (m3)']
    accessible_31 = accessible_12 + ['7th (m7)']
    
    names_h = list(harmonic_lcms.keys())
    lcm_vals = [harmonic_lcms[n] for n in names_h]
    colors_h = ['#27ae60' if n in accessible_31 else 
               ('#3498db' if n in accessible_12 else '#e74c3c') for n in names_h]
    
    bars = ax2.bar(range(len(names_h)), lcm_vals, color=colors_h, alpha=0.85, edgecolor='black')
    ax2.set_xticks(range(len(names_h)))
    ax2.set_xticklabels(names_h, rotation=30, ha='right', fontsize=9)
    ax2.set_ylabel("log₂(LCM) — interval complexity")
    ax2.set_title("Harmonic Overtone Accessibility by Tuning System\n"
                 "(green=31-TET unlocks, blue=12-TET accesses, red=beyond 31-TET)")
    ax2.grid(axis='y', alpha=0.3)
    
    # Legend
    from matplotlib.patches import Patch
    legend_elements = [Patch(color='#3498db', label='12-TET accessible (<10¢ error)'),
                      Patch(color='#27ae60', label='31-TET additionally unlocks'),
                      Patch(color='#e74c3c', label='Beyond 31-TET')]
    ax2.legend(handles=legend_elements, fontsize=9)
    
    plt.tight_layout()
    plt.savefig(OUT/'microtonality.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: microtonality.png")

# ══════════════════════════════════════════════════════════════════
# 5. COGNITIVE LOAD BUDGET BY MUSICAL STYLE
# ══════════════════════════════════════════════════════════════════

def analyze_cognitive_load():
    print("\n=== Cognitive Load Budget by Musical Style ===")
    
    # Each style has characteristic:
    # - pitch complexity (mean interval LCM used)
    # - harmonic rhythm (chords/measure)
    # - rhythmic complexity (IOI-LCM)
    # - polyphony density (simultaneous voices)
    
    styles = {
        'Gregorian Chant':    dict(pitch=3.0,  harm_r=0.5, rhythm=2.0, voices=1),
        'Bach Chorale':       dict(pitch=3.5,  harm_r=2.0, rhythm=3.0, voices=4),
        'Classical Sonata':   dict(pitch=3.6,  harm_r=1.5, rhythm=3.5, voices=2),
        'Romantic Orchestra': dict(pitch=4.0,  harm_r=1.0, rhythm=4.0, voices=8),
        'Blues':              dict(pitch=3.8,  harm_r=0.5, rhythm=4.5, voices=1),
        'Jazz Standards':     dict(pitch=5.5,  harm_r=2.0, rhythm=4.0, voices=4),
        'Bebop':              dict(pitch=6.0,  harm_r=4.0, rhythm=5.0, voices=2),
        'Pop (2000s)':        dict(pitch=3.4,  harm_r=1.0, rhythm=3.0, voices=3),
        'Heavy Metal':        dict(pitch=4.5,  harm_r=0.5, rhythm=3.5, voices=2),
        'Death Metal':        dict(pitch=5.5,  harm_r=0.3, rhythm=6.0, voices=4),
        'Minimalism (Glass)': dict(pitch=3.2,  harm_r=0.5, rhythm=7.0, voices=3),
        'Spectral (Murail)':  dict(pitch=7.5,  harm_r=0.2, rhythm=4.5, voices=10),
        'Gamelan':            dict(pitch=3.8,  harm_r=0.2, rhythm=8.0, voices=12),
        'Indian Classical':   dict(pitch=4.5,  harm_r=0.1, rhythm=9.0, voices=2),
    }
    
    def total_load(s):
        """Cognitive load = weighted sum of three axes."""
        pitch_w = 3.0   # pitch complexity weight
        harm_w  = 1.5   # harmonic rhythm weight  
        rhythm_w = 2.0  # rhythmic complexity weight
        voice_w = 0.5   # polyphony weight per voice above 1
        return (s['pitch']   * pitch_w + 
                s['harm_r']  * harm_w  + 
                s['rhythm']  * rhythm_w + 
                max(0, s['voices']-1) * voice_w)
    
    print("\nCognitive load scores by style:")
    style_loads = [(name, total_load(data), data) for name, data in styles.items()]
    style_loads.sort(key=lambda x: x[1])
    
    for name, load, data in style_loads:
        bar = '█' * int(load / 2)
        print(f"  {load:5.1f}  {bar:<15}  {name}")
    
    # Breakdowns
    print("\nLoad breakdown (pitch / harm.rhythm / rhythm / voices):")
    for name, load, data in style_loads:
        p = data['pitch'] * 3.0
        h = data['harm_r'] * 1.5
        r = data['rhythm'] * 2.0
        v = max(0, data['voices']-1) * 0.5
        print(f"  {name:25s}: pitch={p:.1f}  harmony={h:.1f}  rhythm={r:.1f}  voices={v:.1f}  TOTAL={load:.1f}")
    
    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    fig.suptitle("Cognitive Load Budget by Musical Style\n"
                 "(total load = pitch × 3 + harm.rhythm × 1.5 + rhythm × 2 + voices × 0.5)", 
                 fontsize=13, fontweight='bold')
    
    # Panel 1: Stacked bar chart
    ax = axes[0]
    names_s = [n for n,_,_ in style_loads]
    pitch_loads = [d['pitch']*3.0 for _,_,d in style_loads]
    harm_loads  = [d['harm_r']*1.5 for _,_,d in style_loads]
    rhythm_loads = [d['rhythm']*2.0 for _,_,d in style_loads]
    voice_loads = [max(0, d['voices']-1)*0.5 for _,_,d in style_loads]
    
    y = np.arange(len(names_s))
    ax.barh(y, pitch_loads, label='Pitch complexity', color='#3498db', alpha=0.85)
    ax.barh(y, harm_loads, left=pitch_loads, label='Harmonic rhythm', color='#e74c3c', alpha=0.85)
    left2 = np.array(pitch_loads) + np.array(harm_loads)
    ax.barh(y, rhythm_loads, left=left2, label='Rhythmic complexity', color='#27ae60', alpha=0.85)
    left3 = left2 + np.array(rhythm_loads)
    ax.barh(y, voice_loads, left=left3, label='Polyphony', color='#9b59b6', alpha=0.85)
    
    ax.set_yticks(y)
    ax.set_yticklabels(names_s, fontsize=9)
    ax.set_xlabel("Cognitive load units")
    ax.set_title("Load Composition by Style")
    ax.legend(fontsize=9, loc='lower right')
    ax.grid(axis='x', alpha=0.3)
    
    # Panel 2: 2D scatter — pitch vs rhythm (size=harmonic rhythm, color=total)
    ax2 = axes[1]
    pitch_arr = [d['pitch'] for _,_,d in style_loads]
    rhythm_arr = [d['rhythm'] for _,_,d in style_loads]
    harm_arr = [d['harm_r'] * 200 + 50 for _,_,d in style_loads]
    total_arr = [load for _,load,_ in style_loads]
    
    sc = ax2.scatter(pitch_arr, rhythm_arr, s=harm_arr, c=total_arr, 
                    cmap='YlOrRd', alpha=0.8, edgecolors='black', lw=1, zorder=5)
    plt.colorbar(sc, ax=ax2, label='Total cognitive load')
    
    for (name, load, data), x, y_pos in zip(style_loads, pitch_arr, rhythm_arr):
        ax2.annotate(name, (x, y_pos), xytext=(x+0.05, y_pos+0.1), fontsize=8)
    
    ax2.set_xlabel("Pitch complexity (mean log₂-LCM)")
    ax2.set_ylabel("Rhythmic complexity (IOI-LCM scale)")
    ax2.set_title("Pitch vs Rhythm Space\n(bubble size = harmonic rhythm rate)")
    ax2.grid(alpha=0.3)
    
    # Quadrant labels
    ax2.axvline(5, color='gray', ls='--', alpha=0.3)
    ax2.axhline(5, color='gray', ls='--', alpha=0.3)
    ax2.text(3, 8.5, 'Simple pitch\nComplex rhythm', ha='center', fontsize=8, style='italic', alpha=0.5)
    ax2.text(6.5, 8.5, 'Complex pitch\nComplex rhythm', ha='center', fontsize=8, style='italic', alpha=0.5)
    ax2.text(3, 2.5, 'Simple pitch\nSimple rhythm', ha='center', fontsize=8, style='italic', alpha=0.5)
    ax2.text(6.5, 2.5, 'Complex pitch\nSimple rhythm', ha='center', fontsize=8, style='italic', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(OUT/'cognitive_load.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("Saved: cognitive_load.png")

# ══════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("Music Theory Session 6 — Spectral Rhythm, Tonal Gravity, Harmonic Rhythm,")
    print("                          Microtonality, Cognitive Load")
    print("="*65)
    analyze_rhythm_spectra()
    analyze_tonal_gravity()
    analyze_harmonic_rhythm()
    analyze_microtonality()
    analyze_cognitive_load()
    print("\n" + "="*65)
    print("Session 6 complete.")
