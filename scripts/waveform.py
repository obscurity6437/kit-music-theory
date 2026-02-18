#!/usr/bin/env python3
"""
Waveform generation and interference analysis.
Pure mathematical modeling of sound waves.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_sine_wave(frequency, duration=1.0, sample_rate=44100, amplitude=1.0):
    """Generate a pure sine wave at given frequency."""
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return t, wave

def combine_waves(waves):
    """Sum multiple waveforms (interference)."""
    return np.sum(waves, axis=0)

def analyze_interference(freq1, freq2, base_name, duration=0.05):
    """
    Analyze interference pattern between two frequencies.
    Returns period, amplitude variation, and saves visualization.
    """
    t, wave1 = generate_sine_wave(freq1, duration=duration)
    _, wave2 = generate_sine_wave(freq2, duration=duration)
    combined = wave1 + wave2
    
    # Calculate beat frequency (for dissonant intervals)
    beat_freq = abs(freq1 - freq2)
    
    # Measure amplitude envelope variation
    envelope_std = np.std(combined)
    
    # Create visualization
    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    
    axes[0].plot(t, wave1, 'b-', alpha=0.7, label=f'{freq1:.1f} Hz')
    axes[0].set_ylabel('Amplitude')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    axes[1].plot(t, wave2, 'r-', alpha=0.7, label=f'{freq2:.1f} Hz')
    axes[1].set_ylabel('Amplitude')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(t, combined, 'k-', linewidth=1.5, label='Combined')
    axes[2].set_ylabel('Amplitude')
    axes[2].set_xlabel('Time (seconds)')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    ratio = freq2 / freq1
    fig.suptitle(f'Interference Pattern: {ratio:.4f} ratio ({base_name})')
    
    output_path = Path(__file__).parent.parent / 'visualizations' / f'{base_name}.png'
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    
    return {
        'ratio': ratio,
        'beat_frequency': beat_freq,
        'envelope_variation': envelope_std,
        'visualization': str(output_path)
    }

def harmonic_series(fundamental, num_harmonics=16):
    """Generate harmonic series from fundamental frequency."""
    return [fundamental * n for n in range(1, num_harmonics + 1)]

if __name__ == '__main__':
    print("Waveform analysis tools initialized.")
    print("Example: analyze_interference(440, 880, 'octave')")
