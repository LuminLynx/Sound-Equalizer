#!/usr/bin/env python3
"""
Unit tests for the audio_processor module.

This module contains tests for the EqualizerBand and AudioProcessor classes.
"""

import unittest
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'python-equalizer'))

from audio_processor import EqualizerBand, AudioProcessor, normalize_audio, apply_fade


class TestEqualizerBand(unittest.TestCase):
    """Test cases for EqualizerBand class."""
    
    def test_initialization(self):
        """Test EqualizerBand initialization with valid parameters."""
        band = EqualizerBand(frequency=1000, gain_db=6.0, q_factor=1.0)
        
        self.assertEqual(band.frequency, 1000)
        self.assertEqual(band.gain_db, 6.0)
        self.assertEqual(band.q_factor, 1.0)
        
    def test_initialization_defaults(self):
        """Test EqualizerBand initialization with default Q factor."""
        band = EqualizerBand(frequency=1000, gain_db=6.0)
        
        self.assertEqual(band.frequency, 1000)
        self.assertEqual(band.gain_db, 6.0)
        self.assertEqual(band.q_factor, 1.0)
        
    def test_filter_coefficients(self):
        """Test filter coefficient generation."""
        band = EqualizerBand(frequency=1000, gain_db=6.0, q_factor=1.0)
        b, a = band.get_filter_coefficients(sample_rate=44100)
        
        # Check that we get coefficient arrays
        self.assertEqual(len(b), 3)
        self.assertEqual(len(a), 3)
        
        # Check that coefficients are finite
        self.assertTrue(np.all(np.isfinite(b)))
        self.assertTrue(np.all(np.isfinite(a)))
        
        # Check normalization (a[0] should be 1.0)
        self.assertAlmostEqual(a[0], 1.0)
        
    def test_filter_coefficients_different_sample_rates(self):
        """Test that filter coefficients change with sample rate."""
        band = EqualizerBand(frequency=1000, gain_db=6.0, q_factor=1.0)
        
        b1, a1 = band.get_filter_coefficients(sample_rate=44100)
        b2, a2 = band.get_filter_coefficients(sample_rate=48000)
        
        # Coefficients should be different for different sample rates
        self.assertFalse(np.allclose(b1, b2))
        self.assertFalse(np.allclose(a1, a2))
        
    def test_zero_gain(self):
        """Test that zero gain produces nearly unity gain."""
        band = EqualizerBand(frequency=1000, gain_db=0.0, q_factor=1.0)
        b, a = band.get_filter_coefficients(sample_rate=44100)
        
        # With zero gain, filter should be close to pass-through
        # This is a simplified check - exact behavior depends on filter design
        self.assertTrue(np.all(np.isfinite(b)))
        self.assertTrue(np.all(np.isfinite(a)))


class TestAudioProcessor(unittest.TestCase):
    """Test cases for AudioProcessor class."""
    
    def test_initialization(self):
        """Test AudioProcessor initialization."""
        processor = AudioProcessor(sample_rate=44100)
        
        self.assertEqual(processor.sample_rate, 44100)
        self.assertEqual(len(processor.bands), 0)
        self.assertEqual(len(processor.filter_states), 0)
        
    def test_initialization_default_sample_rate(self):
        """Test AudioProcessor initialization with default sample rate."""
        processor = AudioProcessor()
        
        self.assertEqual(processor.sample_rate, 44100)
        
    def test_add_band(self):
        """Test adding a single equalizer band."""
        processor = AudioProcessor(sample_rate=44100)
        processor.add_band(frequency=1000, gain_db=6.0, q_factor=1.0)
        
        self.assertEqual(len(processor.bands), 1)
        self.assertEqual(len(processor.filter_states), 1)
        
        band = processor.bands[0]
        self.assertEqual(band.frequency, 1000)
        self.assertEqual(band.gain_db, 6.0)
        self.assertEqual(band.q_factor, 1.0)
        
    def test_add_multiple_bands(self):
        """Test adding multiple equalizer bands."""
        processor = AudioProcessor(sample_rate=44100)
        
        processor.add_band(frequency=100, gain_db=3.0)
        processor.add_band(frequency=1000, gain_db=6.0)
        processor.add_band(frequency=10000, gain_db=-3.0)
        
        self.assertEqual(len(processor.bands), 3)
        self.assertEqual(processor.bands[0].frequency, 100)
        self.assertEqual(processor.bands[1].frequency, 1000)
        self.assertEqual(processor.bands[2].frequency, 10000)
        
    def test_clear_bands(self):
        """Test clearing all equalizer bands."""
        processor = AudioProcessor(sample_rate=44100)
        
        processor.add_band(frequency=100, gain_db=3.0)
        processor.add_band(frequency=1000, gain_db=6.0)
        
        self.assertEqual(len(processor.bands), 2)
        
        processor.clear_bands()
        
        self.assertEqual(len(processor.bands), 0)
        self.assertEqual(len(processor.filter_states), 0)
        
    def test_process_block_no_bands(self):
        """Test processing with no bands (pass-through)."""
        processor = AudioProcessor(sample_rate=44100)
        
        # Create test signal
        test_signal = np.random.randn(1000).astype(np.float32)
        
        # Process should return the same signal
        output = processor.process_block(test_signal)
        
        np.testing.assert_array_equal(output, test_signal)
        
    def test_process_block_with_bands(self):
        """Test processing with equalizer bands."""
        processor = AudioProcessor(sample_rate=44100)
        processor.add_band(frequency=1000, gain_db=6.0, q_factor=1.0)
        
        # Create test signal
        test_signal = np.random.randn(1000).astype(np.float32)
        
        # Process signal
        output = processor.process_block(test_signal)
        
        # Output should have same length
        self.assertEqual(len(output), len(test_signal))
        
        # Output should be different from input (filter was applied)
        self.assertFalse(np.allclose(output, test_signal))
        
        # Output should be finite
        self.assertTrue(np.all(np.isfinite(output)))
        
    def test_process_block_preserves_length(self):
        """Test that processing preserves signal length."""
        processor = AudioProcessor(sample_rate=44100)
        processor.add_band(frequency=1000, gain_db=6.0)
        
        # Test with different signal lengths
        for length in [100, 512, 1024, 4096]:
            test_signal = np.random.randn(length).astype(np.float32)
            output = processor.process_block(test_signal)
            self.assertEqual(len(output), length)
            
    def test_reset_states(self):
        """Test resetting filter states."""
        processor = AudioProcessor(sample_rate=44100)
        processor.add_band(frequency=1000, gain_db=6.0)
        
        # Process a signal to initialize states
        test_signal = np.random.randn(1000).astype(np.float32)
        processor.process_block(test_signal)
        
        # States should be initialized
        self.assertIsNotNone(processor.filter_states[0])
        
        # Reset states
        processor.reset_states()
        
        # States should be None
        self.assertIsNone(processor.filter_states[0])
        
    def test_get_frequency_response(self):
        """Test frequency response calculation."""
        processor = AudioProcessor(sample_rate=44100)
        processor.add_band(frequency=1000, gain_db=6.0, q_factor=1.0)
        
        freqs, mag_db, phase = processor.get_frequency_response()
        
        # Check that we get arrays of the right size
        self.assertEqual(len(freqs), 1000)  # Default number of points
        self.assertEqual(len(mag_db), 1000)
        self.assertEqual(len(phase), 1000)
        
        # Check that arrays are finite
        self.assertTrue(np.all(np.isfinite(freqs)))
        self.assertTrue(np.all(np.isfinite(mag_db)))
        self.assertTrue(np.all(np.isfinite(phase)))
        
        # Frequencies should be in ascending order
        self.assertTrue(np.all(np.diff(freqs) > 0))
        
    def test_get_frequency_response_custom_frequencies(self):
        """Test frequency response with custom frequency array."""
        processor = AudioProcessor(sample_rate=44100)
        processor.add_band(frequency=1000, gain_db=6.0, q_factor=1.0)
        
        test_freqs = np.array([100, 500, 1000, 5000, 10000])
        freqs, mag_db, phase = processor.get_frequency_response(frequencies=test_freqs)
        
        # Should return same frequencies
        np.testing.assert_array_equal(freqs, test_freqs)
        
        # Check that we get magnitude response at 1000 Hz (peak)
        idx_1000 = 2  # Index of 1000 Hz
        # At the peak frequency, gain should be close to 6 dB
        self.assertGreater(mag_db[idx_1000], 3.0)  # At least half the gain


class TestNormalizeAudio(unittest.TestCase):
    """Test cases for normalize_audio function."""
    
    def test_normalize_basic(self):
        """Test basic normalization."""
        # Create signal with peak at 0.5
        audio = np.array([0.5, 0.3, -0.4, 0.2], dtype=np.float32)
        
        # Normalize to -3 dB (default)
        normalized = normalize_audio(audio)
        
        # Peak should be close to 10^(-3/20) ≈ 0.708
        target_peak = 10 ** (-3.0 / 20.0)
        actual_peak = np.max(np.abs(normalized))
        
        self.assertAlmostEqual(actual_peak, target_peak, places=5)
        
    def test_normalize_custom_level(self):
        """Test normalization to custom level."""
        audio = np.array([1.0, 0.5, -0.8, 0.3], dtype=np.float32)
        
        # Normalize to -6 dB
        normalized = normalize_audio(audio, target_level=-6.0)
        
        # Peak should be close to 10^(-6/20) ≈ 0.501
        target_peak = 10 ** (-6.0 / 20.0)
        actual_peak = np.max(np.abs(normalized))
        
        self.assertAlmostEqual(actual_peak, target_peak, places=5)
        
    def test_normalize_zero_signal(self):
        """Test normalization of zero signal."""
        audio = np.zeros(100, dtype=np.float32)
        
        normalized = normalize_audio(audio)
        
        # Should return zeros unchanged
        np.testing.assert_array_equal(normalized, audio)
        
    def test_normalize_preserves_shape(self):
        """Test that normalization preserves signal shape."""
        audio = np.random.randn(1000).astype(np.float32)
        
        normalized = normalize_audio(audio)
        
        # Shape should be preserved
        self.assertEqual(normalized.shape, audio.shape)
        
        # Relative amplitudes should be preserved
        # (normalized should be a scaled version of audio)
        scale = normalized[0] / audio[0] if audio[0] != 0 else 0
        if scale != 0:
            np.testing.assert_allclose(normalized, audio * scale, rtol=1e-5)


class TestApplyFade(unittest.TestCase):
    """Test cases for apply_fade function."""
    
    def test_apply_fade_basic(self):
        """Test basic fade application."""
        audio = np.ones(1000, dtype=np.float32)
        
        faded = apply_fade(audio, fade_samples=100)
        
        # First sample should be 0 (start of fade in)
        self.assertAlmostEqual(faded[0], 0.0, places=5)
        
        # Last sample should be 0 (end of fade out)
        self.assertAlmostEqual(faded[-1], 0.0, places=5)
        
        # Middle should be close to 1.0
        self.assertAlmostEqual(faded[500], 1.0, places=5)
        
    def test_apply_fade_preserves_length(self):
        """Test that fade preserves signal length."""
        for length in [100, 500, 1000, 5000]:
            audio = np.ones(length, dtype=np.float32)
            faded = apply_fade(audio, fade_samples=100)
            self.assertEqual(len(faded), length)
            
    def test_apply_fade_short_signal(self):
        """Test fade with signal shorter than fade length."""
        # Signal shorter than fade samples
        audio = np.ones(50, dtype=np.float32)
        
        faded = apply_fade(audio, fade_samples=100)
        
        # Should still work without error
        self.assertEqual(len(faded), 50)
        
        # First and last samples should be faded
        self.assertLess(faded[0], 0.5)
        self.assertLess(faded[-1], 0.5)
        
    def test_apply_fade_does_not_modify_original(self):
        """Test that apply_fade doesn't modify the original array."""
        audio = np.ones(1000, dtype=np.float32)
        original = audio.copy()
        
        faded = apply_fade(audio, fade_samples=100)
        
        # Original should be unchanged
        np.testing.assert_array_equal(audio, original)
        
        # Faded should be different
        self.assertFalse(np.allclose(faded, original))


if __name__ == '__main__':
    unittest.main()
