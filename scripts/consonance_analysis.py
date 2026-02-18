#!/usr/bin/env python3
"""
Analyze why certain frequency ratios sound consonant.
Focus on simple integer ratios and harmonic overlap.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from waveform import analyze_interference, harmonic_series
import json

# Using A440 as reference
BASE_FREQ = 440.0

# Musical intervals with their frequency ratios
INTERVALS = {
    'unison': 1/1,
    'octave': 2/1,
    'perfect_fifth': 3/2,
    'perfect_fourth': 4/3,
    'major_third': 5/4,
    'minor_third': 6/5,
    'major_sixth': 5/3,
    'minor_sixth': 8/5,
    'major_second': 9/8,
    'minor_second': 16/15,
    'tritone': 45/32,  # Approximation of √2
}

def analyze_harmonic_overlap(freq1, freq2, num_harmonics=8):
    """
    Count how many harmonics overlap between two frequencies.
    Simple integer ratios have more harmonic overlap.
    """
    harmonics1 = set(harmonic_series(freq1, num_harmonics))
    harmonics2 = set(harmonic_series(freq2, num_harmonics))
    
    # Find near-matches (within 1 Hz tolerance)
    matches = 0
    for h1 in harmonics1:
        for h2 in harmonics2:
            if abs(h1 - h2) < 1.0:
                matches += 1
                break
    
    return matches

def analyze_all_intervals():
    """Analyze all standard musical intervals."""
    results = {}
    
    for name, ratio in INTERVALS.items():
        freq2 = BASE_FREQ * ratio
        
        # Interference analysis
        interference = analyze_interference(BASE_FREQ, freq2, name)
        
        # Harmonic overlap
        overlap = analyze_harmonic_overlap(BASE_FREQ, freq2)
        
        # Simplicity score (inverse of denominator when reduced)
        # Simpler ratios = more consonant
        from fractions import Fraction
        frac = Fraction(ratio).limit_denominator(100)
        simplicity = 1 / frac.denominator
        
        results[name] = {
            'ratio': ratio,
            'ratio_fraction': f'{frac.numerator}/{frac.denominator}',
            'frequency': freq2,
            'beat_frequency': interference['beat_frequency'],
            'envelope_variation': interference['envelope_variation'],
            'harmonic_overlap': overlap,
            'simplicity_score': simplicity,
            'visualization': interference['visualization']
        }
        
        print(f"✓ Analyzed {name:20s} ({frac.numerator}/{frac.denominator})")
    
    return results

if __name__ == '__main__':
    print(f"Analyzing consonance patterns using A={BASE_FREQ}Hz as reference\n")
    
    results = analyze_all_intervals()
    
    # Save results
    output_file = Path(__file__).parent.parent / 'analysis' / 'consonance_data.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")
    print("\nConsonance ranking (by simplicity score):")
    
    ranked = sorted(results.items(), key=lambda x: x[1]['simplicity_score'], reverse=True)
    for name, data in ranked[:5]:
        print(f"  {name:20s} {data['ratio_fraction']:10s} — {data['harmonic_overlap']} harmonic overlaps")
