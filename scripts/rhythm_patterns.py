#!/usr/bin/env python3
"""
Explore polyrhythms as frequency ratio analogs.
If 3:2 creates consonant harmony, does 3:2 polyrhythm create consonant rhythm?
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_pulse_train(bpm, duration=4.0, beats_per_measure=4):
    """
    Generate a pulse train (rhythm) at given tempo.
    Returns time points where pulses occur.
    """
    beat_duration = 60.0 / bpm  # seconds per beat
    num_beats = int(duration / beat_duration)
    pulses = [i * beat_duration for i in range(num_beats)]
    return np.array(pulses)

def polyrhythm_alignment(ratio, duration=4.0):
    """
    Analyze when two pulse trains align for a given ratio.
    E.g., 3:2 means 3 pulses in voice 1 for every 2 in voice 2.
    """
    # Base the timing on the slower rhythm
    slower = max(ratio)
    faster = min(ratio)
    
    # Calculate BPMs that give us the desired ratio
    base_bpm = 60  # arbitrary base
    bpm1 = base_bpm * ratio[0]
    bpm2 = base_bpm * ratio[1]
    
    pulses1 = generate_pulse_train(bpm1, duration)
    pulses2 = generate_pulse_train(bpm2, duration)
    
    # Find alignments (within 0.01 second tolerance)
    alignments = []
    for p1 in pulses1:
        for p2 in pulses2:
            if abs(p1 - p2) < 0.01:
                alignments.append(p1)
                break
    
    # Calculate repetition period
    if len(alignments) > 1:
        repeat_period = alignments[1] - alignments[0]
    else:
        repeat_period = duration
    
    return {
        'pulses1': pulses1,
        'pulses2': pulses2,
        'alignments': alignments,
        'repeat_period': repeat_period,
        'alignment_frequency': len(alignments) / duration
    }

def visualize_polyrhythm(ratio, name, duration=4.0):
    """Create visualization of polyrhythm pattern."""
    analysis = polyrhythm_alignment(ratio, duration)
    
    fig, ax = plt.subplots(figsize=(14, 4))
    
    # Plot pulse trains
    ax.scatter(analysis['pulses1'], [1] * len(analysis['pulses1']), 
               s=100, c='blue', marker='|', linewidths=3, label=f'{ratio[0]} pulses')
    ax.scatter(analysis['pulses2'], [0.5] * len(analysis['pulses2']), 
               s=100, c='red', marker='|', linewidths=3, label=f'{ratio[1]} pulses')
    
    # Mark alignments
    for align in analysis['alignments']:
        ax.axvline(x=align, color='green', alpha=0.3, linestyle='--', linewidth=2)
    
    ax.set_ylim([0, 1.5])
    ax.set_xlim([0, duration])
    ax.set_xlabel('Time (seconds)')
    ax.set_yticks([0.5, 1])
    ax.set_yticklabels([f'{ratio[1]} rhythm', f'{ratio[0]} rhythm'])
    ax.legend()
    ax.grid(True, alpha=0.2)
    
    title = f'{ratio[0]}:{ratio[1]} Polyrhythm — '
    title += f'Repeats every {analysis["repeat_period"]:.2f}s, '
    title += f'{len(analysis["alignments"])} alignments'
    ax.set_title(title)
    
    output_path = Path(__file__).parent.parent / 'visualizations' / f'rhythm_{name}.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    return analysis

if __name__ == '__main__':
    # Analyze the same ratios we used for harmony
    rhythms = {
        'unison': (1, 1),
        'octave': (2, 1),
        'fifth': (3, 2),
        'fourth': (4, 3),
        'complex': (9, 8),
        'very_complex': (45, 32)
    }
    
    print("Polyrhythm analysis:\n")
    
    for name, ratio in rhythms.items():
        result = visualize_polyrhythm(ratio, name)
        print(f"{name:15s} {ratio[0]}:{ratio[1]:2d} — "
              f"repeats every {result['repeat_period']:.3f}s, "
              f"{len(result['alignments'])} alignments in 4s")
    
    print("\n✓ Visualizations saved to visualizations/")
    print("\nPattern: Simple ratios align more frequently, creating predictable structure.")
    print("Just like consonance in harmony, simple polyrhythms have short repeat periods.")
