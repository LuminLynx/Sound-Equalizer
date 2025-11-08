#!/usr/bin/env python3
"""
Unit tests for the equalizer module.

This module contains tests for the SoundEqualizer class and main functionality.
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'python-equalizer'))

from equalizer import SoundEqualizer


class TestSoundEqualizer(unittest.TestCase):
    """Test cases for SoundEqualizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_config = {
            "sample_rate": 44100,
            "buffer_size": 1024,
            "bands": [
                {
                    "frequency": 100,
                    "gain_db": 0.0,
                    "q_factor": 1.0,
                    "description": "Bass"
                },
                {
                    "frequency": 1000,
                    "gain_db": 0.0,
                    "q_factor": 1.0,
                    "description": "Mid"
                },
                {
                    "frequency": 10000,
                    "gain_db": 0.0,
                    "q_factor": 1.0,
                    "description": "Treble"
                }
            ],
            "presets": {
                "flat": {
                    "description": "Flat response",
                    "gains": [0, 0, 0]
                },
                "bass_boost": {
                    "description": "Bass boost",
                    "gains": [6, 0, 0]
                },
                "test_preset": {
                    "description": "Test preset",
                    "gains": [3, -2, 4]
                }
            }
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        json.dump(self.temp_config, self.temp_file)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary file
        Path(self.temp_file.name).unlink(missing_ok=True)
        
    def test_initialization_with_config(self):
        """Test SoundEqualizer initialization with config file."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        self.assertEqual(equalizer.sample_rate, 44100)
        self.assertEqual(equalizer.buffer_size, 1024)
        self.assertEqual(len(equalizer.processor.bands), 3)
        
    def test_initialization_default_config(self):
        """Test SoundEqualizer initialization with default config."""
        # Use non-existent config file
        equalizer = SoundEqualizer(config_file='nonexistent.json')
        
        # Should use defaults
        self.assertEqual(equalizer.sample_rate, 44100)
        self.assertEqual(equalizer.buffer_size, 1024)
        
    def test_load_bands_from_config(self):
        """Test loading bands from configuration."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        # Check that bands were loaded
        bands = equalizer.processor.bands
        self.assertEqual(len(bands), 3)
        
        self.assertEqual(bands[0].frequency, 100)
        self.assertEqual(bands[1].frequency, 1000)
        self.assertEqual(bands[2].frequency, 10000)
        
    def test_apply_preset_valid(self):
        """Test applying a valid preset."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        result = equalizer.apply_preset('bass_boost')
        
        self.assertTrue(result)
        
        # Check that gains were applied
        bands = equalizer.processor.bands
        self.assertEqual(bands[0].gain_db, 6.0)
        self.assertEqual(bands[1].gain_db, 0.0)
        self.assertEqual(bands[2].gain_db, 0.0)
        
    def test_apply_preset_invalid(self):
        """Test applying an invalid preset."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        result = equalizer.apply_preset('nonexistent_preset')
        
        self.assertFalse(result)
        
    def test_apply_preset_changes_bands(self):
        """Test that applying preset changes band configuration."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        # Apply first preset
        equalizer.apply_preset('flat')
        flat_gains = [band.gain_db for band in equalizer.processor.bands]
        
        # Apply second preset
        equalizer.apply_preset('test_preset')
        test_gains = [band.gain_db for band in equalizer.processor.bands]
        
        # Gains should be different
        self.assertNotEqual(flat_gains, test_gains)
        
        # Check specific values
        self.assertEqual(test_gains[0], 3.0)
        self.assertEqual(test_gains[1], -2.0)
        self.assertEqual(test_gains[2], 4.0)
        
    def test_list_presets(self):
        """Test listing available presets."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        # This should not raise an error
        equalizer.list_presets()
        
        # Check that presets exist in config
        presets = equalizer.config.get('presets', {})
        self.assertGreater(len(presets), 0)
        self.assertIn('flat', presets)
        self.assertIn('bass_boost', presets)
        
    def test_list_bands(self):
        """Test listing current band configuration."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        # This should not raise an error
        equalizer.list_bands()
        
        # Check that bands exist
        self.assertGreater(len(equalizer.processor.bands), 0)
        
    def test_test_mode(self):
        """Test running in test mode."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        result = equalizer.test_mode()
        
        self.assertTrue(result)
        
    def test_cleanup(self):
        """Test cleanup method."""
        equalizer = SoundEqualizer(config_file=self.temp_file.name)
        
        # Should not raise an error
        equalizer.cleanup()
        
        # Check that resources are cleaned
        self.assertIsNone(equalizer.stream)
        
    def test_config_with_missing_fields(self):
        """Test handling config with missing fields."""
        minimal_config = {
            "sample_rate": 48000
        }
        
        temp_minimal = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        json.dump(minimal_config, temp_minimal)
        temp_minimal.close()
        
        try:
            equalizer = SoundEqualizer(config_file=temp_minimal.name)
            
            # Should use provided sample rate
            self.assertEqual(equalizer.sample_rate, 48000)
            
            # Should use default buffer size
            self.assertEqual(equalizer.buffer_size, 1024)
            
            # Should have no bands
            self.assertEqual(len(equalizer.processor.bands), 0)
        finally:
            Path(temp_minimal.name).unlink(missing_ok=True)
            
    def test_preset_with_wrong_number_of_gains(self):
        """Test applying preset with wrong number of gains."""
        wrong_config = {
            "sample_rate": 44100,
            "buffer_size": 1024,
            "bands": [
                {"frequency": 100, "gain_db": 0.0, "q_factor": 1.0},
                {"frequency": 1000, "gain_db": 0.0, "q_factor": 1.0}
            ],
            "presets": {
                "wrong_preset": {
                    "description": "Wrong number of gains",
                    "gains": [1, 2, 3, 4, 5]  # 5 gains but only 2 bands
                }
            }
        }
        
        temp_wrong = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        )
        json.dump(wrong_config, temp_wrong)
        temp_wrong.close()
        
        try:
            equalizer = SoundEqualizer(config_file=temp_wrong.name)
            result = equalizer.apply_preset('wrong_preset')
            
            # Should fail gracefully
            self.assertFalse(result)
        finally:
            Path(temp_wrong.name).unlink(missing_ok=True)


class TestEqualizerConfiguration(unittest.TestCase):
    """Test cases for configuration loading and validation."""
    
    def test_load_valid_json_config(self):
        """Test loading a valid JSON configuration."""
        config = {
            "sample_rate": 48000,
            "buffer_size": 512,
            "bands": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config, f)
            config_file = f.name
            
        try:
            equalizer = SoundEqualizer(config_file=config_file)
            self.assertEqual(equalizer.sample_rate, 48000)
            self.assertEqual(equalizer.buffer_size, 512)
        finally:
            Path(config_file).unlink(missing_ok=True)
            
    def test_load_invalid_json_config(self):
        """Test loading an invalid JSON configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            config_file = f.name
            
        try:
            # Should fall back to defaults
            equalizer = SoundEqualizer(config_file=config_file)
            self.assertEqual(equalizer.sample_rate, 44100)
            self.assertEqual(equalizer.buffer_size, 1024)
        finally:
            Path(config_file).unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
