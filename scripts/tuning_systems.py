#!/usr/bin/env python3
"""
Tuning system analysis: Just Intonation vs Equal Temperament vs Pythagorean
Shows the mathematical impossibility of perfect consonance across all keys
"""

import numpy as np
import json
from pathlib import Path

# Just Intonation - pure simple ratios from C
# Uses ratios that create perfect consonances
JUST_INTONATION = {
    'C': 1.0,        # 1/1
    'C#': 16/15,     # minor second
    'D': 9/8,        # major second (9:8)
    'D#': 6/5,       # minor third
    'E': 5/4,        # major third (5:4) - PURE
    'F': 4/3,        # perfect fourth (4:3) - PURE
    'F#': 45/32,     # tritone
    'G': 3/2,        # perfect fifth (3:2) - PURE
    'G#': 8/5,       # minor sixth
    'A': 5/3,        # major sixth
    'A#': 9/5,       # minor seventh
    'B': 15/8,       # major seventh
}

# Equal Temperament - 12th root of 2 for each semitone
# Compromises ALL intervals slightly for transposability
EQUAL_TEMPERAMENT = {
    note: 2 ** (i/12) for i, note in enumerate([
        'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'
    ])
}

# Pythagorean - pure fifths (3:2), stack them to build scale
# Perfect fifths, but thirds are quite sour
def generate_pythagorean():
    """Build scale from stacked perfect fifths"""
    fifth = 3/2
    
    # Stack fifths: F C G D A E B F# C# G# D# A#
    # Then fold back into one octave
    fifths_sequence = ['F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#', 'G#', 'D#', 'A#']
    
    ratios = {}
    for i, note in enumerate(fifths_sequence):
        # Start from F (which is -1 fifth from C)
        power = i - 1
        ratio = (fifth ** power)
        
        # Fold into one octave [1, 2)
        while ratio < 1:
            ratio *= 2
        while ratio >= 2:
            ratio /= 2
            
        ratios[note] = ratio
    
    # Sort by frequency
    sorted_notes = sorted(ratios.items(), key=lambda x: x[1])
    return {note: ratio for note, ratio in sorted_notes}

PYTHAGOREAN = generate_pythagorean()

def cents_difference(ratio1, ratio2):
    """
    Measure difference in cents (1/100 of a semitone)
    1200 cents = octave, 100 cents = equal-tempered semitone
    """
    return 1200 * np.log2(ratio1 / ratio2)

def analyze_interval(note1, note2, tuning_system):
    """Analyze a specific interval in a tuning system"""
    ratio = tuning_system[note2] / tuning_system[note1]
    return ratio

def compare_systems():
    """Compare how each system handles key intervals"""
    
    # Key consonant intervals to test
    test_intervals = [
        ('C', 'E', 5/4, 'Major Third'),
        ('C', 'F', 4/3, 'Perfect Fourth'),
        ('C', 'G', 3/2, 'Perfect Fifth'),
        ('C', 'A', 5/3, 'Major Sixth'),
        ('D', 'A', 3/2, 'Fifth from D'),
        ('E', 'B', 3/2, 'Fifth from E'),
        ('G', 'D', 3/2, 'Fifth from G'),
    ]
    
    results = {}
    
    for root, target, ideal_ratio, name in test_intervals:
        interval_key = f"{root}-{target}"
        results[interval_key] = {
            'name': name,
            'ideal_ratio': ideal_ratio,
            'systems': {}
        }
        
        for system_name, system in [
            ('Just Intonation', JUST_INTONATION),
            ('Equal Temperament', EQUAL_TEMPERAMENT),
            ('Pythagorean', PYTHAGOREAN)
        ]:
            actual_ratio = analyze_interval(root, target, system)
            cents_off = cents_difference(actual_ratio, ideal_ratio)
            
            results[interval_key]['systems'][system_name] = {
                'ratio': float(actual_ratio),
                'cents_off': float(cents_off),
                'error_magnitude': abs(float(cents_off))
            }
    
    return results

def find_wolf_intervals():
    """
    Wolf intervals: intervals that sound terrible in certain tuning systems
    In Just Intonation from C, transposing to other keys breaks consonance
    """
    
    wolves = []
    
    # Test fifths in all keys for Just Intonation
    notes = list(JUST_INTONATION.keys())
    
    for i, root in enumerate(notes):
        # Find the note a fifth above
        target_idx = (i + 7) % 12  # 7 semitones = fifth
        target = notes[target_idx]
        
        ratio = JUST_INTONATION[target] / JUST_INTONATION[root]
        
        # Normalize to one octave
        while ratio < 1:
            ratio *= 2
        while ratio >= 2:
            ratio /= 2
        
        ideal_fifth = 3/2
        cents_off = cents_difference(ratio, ideal_fifth)
        
        if abs(cents_off) > 10:  # More than 10 cents off
            wolves.append({
                'root': root,
                'target': target,
                'ratio': float(ratio),
                'cents_off': float(cents_off),
                'severity': 'wolf' if abs(cents_off) > 20 else 'sour'
            })
    
    return wolves

def pythagorean_comma():
    """
    The Pythagorean comma: the mathematical impossibility
    
    Stacking 12 perfect fifths (3:2) should equal 7 octaves (2:1)
    But: (3/2)^12 = 531441/4096 = 129.746...
         2^7 = 128
    
    Difference: 531441/524288 ≈ 1.0136 (about 23.46 cents)
    
    This is why you can't have perfect fifths in all keys.
    """
    
    twelve_fifths = (3/2) ** 12
    seven_octaves = 2 ** 7
    
    # Normalize to same octave
    twelve_fifths_normalized = twelve_fifths / (2 ** 7)
    
    comma = twelve_fifths / seven_octaves
    cents = 1200 * np.log2(comma)
    
    return {
        'twelve_fifths': float(twelve_fifths),
        'seven_octaves': float(seven_octaves),
        'comma_ratio': float(comma),
        'cents': float(cents),
        'explanation': 'The mathematical impossibility: 12 perfect fifths ≠ 7 octaves'
    }

def main():
    print("Tuning Systems Analysis\n" + "="*60)
    
    # Compare systems
    print("\n1. Interval Accuracy Comparison")
    print("-" * 60)
    comparisons = compare_systems()
    
    for interval_key, data in comparisons.items():
        print(f"\n{interval_key} ({data['name']}) — ideal: {data['ideal_ratio']:.4f}")
        for system, metrics in data['systems'].items():
            error = metrics['cents_off']
            symbol = "✓" if abs(error) < 2 else "~" if abs(error) < 10 else "✗"
            print(f"  {symbol} {system:20s}: {metrics['ratio']:.6f} ({error:+.2f} cents)")
    
    # Pythagorean comma
    print("\n\n2. The Pythagorean Comma (Why Perfection is Impossible)")
    print("-" * 60)
    comma = pythagorean_comma()
    print(f"12 perfect fifths: {comma['twelve_fifths']:.6f}")
    print(f"7 octaves:         {comma['seven_octaves']:.6f}")
    print(f"Comma ratio:       {comma['comma_ratio']:.6f} ({comma['cents']:+.2f} cents)")
    print(f"\n{comma['explanation']}")
    
    # Wolf intervals
    print("\n\n3. Wolf Intervals in Just Intonation")
    print("-" * 60)
    wolves = find_wolf_intervals()
    if wolves:
        print("Fifths that break when tuned pure to C:")
        for wolf in wolves:
            print(f"  {wolf['root']:2s} → {wolf['target']:2s}: {wolf['ratio']:.6f} ({wolf['cents_off']:+.2f} cents) [{wolf['severity']}]")
    else:
        print("No wolf intervals found in this analysis range")
    
    # Save data
    output = {
        'interval_comparisons': comparisons,
        'pythagorean_comma': comma,
        'wolf_intervals': wolves,
        'tuning_systems': {
            'just_intonation': {k: float(v) for k, v in JUST_INTONATION.items()},
            'equal_temperament': {k: float(v) for k, v in EQUAL_TEMPERAMENT.items()},
            'pythagorean': {k: float(v) for k, v in PYTHAGOREAN.items()},
        }
    }
    
    output_path = Path(__file__).parent.parent / 'analysis' / 'tuning_systems_data.json'
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n\nData saved to: {output_path}")
    print("\nKey Insight:")
    print("• Just Intonation: Perfect consonances in ONE key, breaks everywhere else")
    print("• Pythagorean: Perfect fifths, terrible thirds")
    print("• Equal Temperament: Nothing perfect, everything acceptable")
    print("\nEqual temperament sacrifices purity for democracy.")

if __name__ == '__main__':
    main()
