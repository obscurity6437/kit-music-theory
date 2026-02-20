#!/usr/bin/env python3
"""
Visualize tuning system differences
Shows cents deviation from just intonation for equal temperament and Pythagorean
"""

import numpy as np
import matplotlib.pyplot as plt
import json
from pathlib import Path

def load_tuning_data():
    """Load tuning system data from analysis"""
    data_path = Path(__file__).parent.parent / 'analysis' / 'tuning_systems_data.json'
    with open(data_path, 'r') as f:
        return json.load(f)

def plot_tuning_deviations():
    """Plot cents deviation from pure ratios for each system"""
    data = load_tuning_data()
    systems = data['tuning_systems']
    
    # Use just intonation as reference (pure ratios)
    just = systems['just_intonation']
    equal = systems['equal_temperament']
    pyth = systems['pythagorean']
    
    notes = list(just.keys())
    
    # Calculate cents deviation from just intonation
    equal_cents = [1200 * np.log2(equal[note] / just[note]) for note in notes]
    pyth_cents = [1200 * np.log2(pyth[note] / just[note]) for note in notes]
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    x = np.arange(len(notes))
    width = 0.35
    
    # Equal temperament deviations
    colors_et = ['red' if abs(c) > 10 else 'orange' if abs(c) > 5 else 'green' for c in equal_cents]
    bars1 = ax1.bar(x, equal_cents, width, label='Equal Temperament', color=colors_et, alpha=0.7)
    ax1.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax1.axhline(y=5, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.axhline(y=-5, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_ylabel('Cents deviation from Just Intonation')
    ax1.set_title('Equal Temperament: Consistent Compromise (±14 cents max)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(notes)
    ax1.grid(True, alpha=0.3)
    ax1.set_ylim(-25, 25)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars1, equal_cents)):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:+.1f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=8)
    
    # Pythagorean deviations
    colors_py = ['red' if abs(c) > 10 else 'orange' if abs(c) > 5 else 'green' for c in pyth_cents]
    bars2 = ax2.bar(x, pyth_cents, width, label='Pythagorean', color=colors_py, alpha=0.7)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    ax2.axhline(y=5, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.axhline(y=-5, color='gray', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_ylabel('Cents deviation from Just Intonation')
    ax2.set_title('Pythagorean: Perfect Fifths, Terrible Thirds (±21 cents)')
    ax2.set_xlabel('Note')
    ax2.set_xticks(x)
    ax2.set_xticklabels(notes)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-25, 25)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars2, pyth_cents)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:+.1f}',
                ha='center', va='bottom' if height > 0 else 'top',
                fontsize=8)
    
    plt.tight_layout()
    
    output_path = Path(__file__).parent.parent / 'visualizations' / 'tuning_deviations.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

def plot_interval_matrix():
    """Heatmap showing which intervals are pure in which systems"""
    data = load_tuning_data()
    comparisons = data['interval_comparisons']
    
    intervals = list(comparisons.keys())
    systems = ['Just Intonation', 'Equal Temperament', 'Pythagorean']
    
    # Build error matrix
    matrix = np.zeros((len(intervals), len(systems)))
    
    for i, interval_key in enumerate(intervals):
        for j, system in enumerate(systems):
            error = abs(comparisons[interval_key]['systems'][system]['cents_off'])
            matrix[i, j] = error
    
    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=25)
    
    # Set ticks
    ax.set_xticks(np.arange(len(systems)))
    ax.set_yticks(np.arange(len(intervals)))
    ax.set_xticklabels(systems)
    ax.set_yticklabels([comparisons[k]['name'] for k in intervals])
    
    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
    
    # Add text annotations
    for i in range(len(intervals)):
        for j in range(len(systems)):
            text = ax.text(j, i, f'{matrix[i, j]:.1f}',
                          ha="center", va="center", color="black", fontsize=9)
    
    ax.set_title("Interval Purity Matrix (cents deviation from ideal)\nGreen = pure, Red = sour")
    fig.colorbar(im, ax=ax, label='Cents deviation')
    
    plt.tight_layout()
    
    output_path = Path(__file__).parent.parent / 'visualizations' / 'interval_matrix.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

def plot_pythagorean_comma():
    """Visualize the spiral of fifths and the comma gap"""
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    
    # Generate circle of fifths positions
    # Each fifth is 7 semitones = 7/12 * 2π
    notes = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#', 'F']
    
    # Equal temperament: perfect circle
    angles_et = np.array([i * (7/12) * 2 * np.pi for i in range(13)])
    
    # Pythagorean: spiral (each fifth is slightly larger than 7/12 octave)
    fifth_angle = np.log2(3/2) * 2 * np.pi  # True fifth angle
    angles_pyth = np.array([i * fifth_angle for i in range(13)])
    
    # Plot both
    radii_et = np.ones(13)
    radii_pyth = np.ones(13) * 1.2
    
    ax.plot(angles_et, radii_et, 'o-', label='Equal Temperament (closes)', 
            color='blue', markersize=8, linewidth=2)
    ax.plot(angles_pyth, radii_pyth, 'o-', label='Pythagorean Fifths (spiral)', 
            color='red', markersize=8, linewidth=2)
    
    # Highlight the comma gap
    ax.plot([angles_pyth[12], angles_et[12]], [radii_pyth[12], radii_et[12]], 
            'k--', linewidth=2, label=f'Pythagorean Comma\n({23.46:.2f} cents)')
    
    # Label notes on ET circle
    for i, note in enumerate(notes):
        ax.text(angles_et[i], 0.85, note, ha='center', va='center', 
                fontsize=12, fontweight='bold')
    
    ax.set_ylim(0, 1.5)
    ax.set_title('Circle of Fifths: The Pythagorean Comma\n12 perfect fifths ≠ 7 octaves', 
                 fontsize=14, pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    ax.grid(True)
    
    output_path = Path(__file__).parent.parent / 'visualizations' / 'pythagorean_comma.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Saved: {output_path}")
    plt.close()

def main():
    print("Generating tuning system visualizations...\n")
    
    plot_tuning_deviations()
    plot_interval_matrix()
    plot_pythagorean_comma()
    
    print("\nVisualization complete!")
    print("Key findings:")
    print("• Equal temperament deviates ±14 cents consistently")
    print("• Pythagorean has perfect fifths but ±21 cent thirds")
    print("• The Pythagorean comma (23.46 cents) prevents closure")

if __name__ == '__main__':
    main()
