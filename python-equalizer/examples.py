#!/usr/bin/env python3
"""
Example usage of the Sound Equalizer

This script demonstrates different ways to use the equalizer:
1. Test mode - no audio processing
2. Preset application
3. Custom band configuration
"""

import sys
from pathlib import Path

# Add parent directory to path to import equalizer module
sys.path.insert(0, str(Path(__file__).parent))

from audio_processor import AudioProcessor, EqualizerBand
import numpy as np


def example1_test_frequency_response():
    """Example 1: Calculate and display frequency response"""
    print("=" * 60)
    print("Example 1: Frequency Response Calculation")
    print("=" * 60)
    
    # Create processor with sample rate
    processor = AudioProcessor(sample_rate=44100)
    
    # Add bass boost configuration
    processor.add_band(60, gain_db=6.0, q_factor=1.0)
    processor.add_band(170, gain_db=4.0, q_factor=1.0)
    processor.add_band(310, gain_db=2.0, q_factor=1.0)
    
    # Calculate frequency response
    freqs, mag_db, phase = processor.get_frequency_response()
    
    print(f"\nProcessor configured with {len(processor.bands)} bands")
    print(f"Sample rate: {processor.sample_rate} Hz")
    print(f"\nFrequency response at key points:")
    
    # Display response at specific frequencies
    test_frequencies = [60, 170, 310, 1000, 5000, 10000]
    for freq in test_frequencies:
        # Find closest frequency in response
        idx = np.argmin(np.abs(freqs - freq))
        print(f"  {freq:5d} Hz: {mag_db[idx]:+6.2f} dB")
    
    print()


def example2_process_audio_block():
    """Example 2: Process a synthetic audio signal"""
    print("=" * 60)
    print("Example 2: Process Audio Block")
    print("=" * 60)
    
    # Create processor
    processor = AudioProcessor(sample_rate=44100)
    
    # Add treble boost
    processor.add_band(3000, gain_db=3.0, q_factor=1.0)
    processor.add_band(6000, gain_db=4.0, q_factor=1.0)
    processor.add_band(12000, gain_db=5.0, q_factor=1.0)
    
    # Generate test signal (1 second of noise)
    duration = 1.0  # seconds
    num_samples = int(processor.sample_rate * duration)
    
    # Create white noise
    audio_signal = np.random.randn(num_samples).astype(np.float32) * 0.1
    
    print(f"\nGenerated test signal: {num_samples} samples")
    print(f"Input RMS level: {np.sqrt(np.mean(audio_signal**2)):.4f}")
    
    # Process through equalizer
    processed = processor.process_block(audio_signal)
    
    print(f"Output RMS level: {np.sqrt(np.mean(processed**2)):.4f}")
    print(f"Peak level: {np.max(np.abs(processed)):.4f}")
    print()


def example3_band_manipulation():
    """Example 3: Dynamically modify equalizer bands"""
    print("=" * 60)
    print("Example 3: Dynamic Band Manipulation")
    print("=" * 60)
    
    # Create processor
    processor = AudioProcessor(sample_rate=44100)
    
    # Add initial bands
    print("\nAdding bands...")
    bands_config = [
        (100, 0.0, 1.0),
        (1000, 0.0, 1.0),
        (10000, 0.0, 1.0),
    ]
    
    for freq, gain, q in bands_config:
        processor.add_band(freq, gain, q)
        print(f"  Added: {freq} Hz, {gain:+.1f} dB, Q={q}")
    
    # Clear and reconfigure
    print("\nClearing all bands...")
    processor.clear_bands()
    print(f"  Bands remaining: {len(processor.bands)}")
    
    # Add new configuration
    print("\nAdding new configuration (vocal preset)...")
    vocal_config = [
        (100, -2.0, 1.0),
        (200, -1.0, 1.0),
        (500, 0.0, 1.0),
        (1000, 3.0, 1.5),
        (2000, 4.0, 1.5),
        (4000, 2.0, 1.0),
    ]
    
    for freq, gain, q in vocal_config:
        processor.add_band(freq, gain, q)
        print(f"  Added: {freq} Hz, {gain:+.1f} dB, Q={q}")
    
    print()


def example4_filter_coefficients():
    """Example 4: Calculate and display filter coefficients"""
    print("=" * 60)
    print("Example 4: Filter Coefficients")
    print("=" * 60)
    
    # Create a single band
    band = EqualizerBand(frequency=1000, gain_db=6.0, q_factor=1.0)
    
    print(f"\nBand configuration:")
    print(f"  Frequency: {band.frequency} Hz")
    print(f"  Gain: {band.gain_db:+.1f} dB")
    print(f"  Q Factor: {band.q_factor}")
    
    # Calculate coefficients for different sample rates
    sample_rates = [44100, 48000, 96000]
    
    for sr in sample_rates:
        b, a = band.get_filter_coefficients(sr)
        print(f"\nSample Rate: {sr} Hz")
        print(f"  Numerator (b):   [{b[0]:+.6f}, {b[1]:+.6f}, {b[2]:+.6f}]")
        print(f"  Denominator (a): [{a[0]:+.6f}, {a[1]:+.6f}, {a[2]:+.6f}]")
    
    print()


def example5_preset_comparison():
    """Example 5: Compare different presets"""
    print("=" * 60)
    print("Example 5: Preset Comparison")
    print("=" * 60)
    
    # Define presets
    presets = {
        'Flat': [0, 0, 0, 0, 0, 0, 0, 0],
        'Bass Boost': [6, 4, 2, 0, 0, 0, 0, 0],
        'Treble Boost': [0, 0, 0, 0, 0, 3, 4, 5],
        'V-Shape': [5, 3, 0, -2, -2, 0, 3, 5],
    }
    
    # Band frequencies
    frequencies = [60, 170, 310, 600, 1000, 3000, 6000, 12000]
    
    print("\nPreset Comparison:")
    print(f"{'Preset':<15} {'60Hz':>6} {'170Hz':>6} {'310Hz':>6} {'600Hz':>6} "
          f"{'1kHz':>6} {'3kHz':>6} {'6kHz':>6} {'12kHz':>6}")
    print("-" * 75)
    
    for preset_name, gains in presets.items():
        gain_str = ' '.join([f'{g:+5.0f}' for g in gains])
        print(f"{preset_name:<15} {gain_str}")
    
    print()


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print(" Sound Equalizer - Example Usage")
    print("=" * 60 + "\n")
    
    try:
        example1_test_frequency_response()
        example2_process_audio_block()
        example3_band_manipulation()
        example4_filter_coefficients()
        example5_preset_comparison()
        
        print("=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        print("\nTo run the actual equalizer, use:")
        print("  python3 equalizer.py --test           # Test mode")
        print("  python3 equalizer.py --list-presets   # List presets")
        print("  python3 equalizer.py --preset rock    # Run with preset")
        print()
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
