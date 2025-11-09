#!/usr/bin/env python3
"""
Unit tests for the equalizer GUI module.

Tests the GUI components and functionality.
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent / 'python-equalizer'))

# Import Qt and set platform to offscreen for testing
import os
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from equalizer_gui import EqualizerGUI, EqualizerBandControl, FrequencyVisualization


# Create QApplication instance once for all tests
app = QApplication(sys.argv)


class TestFrequencyVisualization(unittest.TestCase):
    """Test cases for FrequencyVisualization widget."""
    
    def test_initialization(self):
        """Test FrequencyVisualization initialization."""
        viz = FrequencyVisualization()
        
        self.assertIsNotNone(viz.figure)
        self.assertIsNotNone(viz.axes)
        self.assertIsNotNone(viz.line)
        
    def test_update_plot(self):
        """Test updating the plot with data."""
        import numpy as np
        
        viz = FrequencyVisualization()
        
        freqs = np.logspace(1, 4, 100)
        mag_db = np.zeros_like(freqs)
        
        # Should not raise an error
        viz.update_plot(freqs, mag_db)
        
        # Check that line data was updated
        x_data, y_data = viz.line.get_data()
        self.assertEqual(len(x_data), len(freqs))
        self.assertEqual(len(y_data), len(mag_db))


class TestEqualizerBandControl(unittest.TestCase):
    """Test cases for EqualizerBandControl widget."""
    
    def test_initialization(self):
        """Test EqualizerBandControl initialization."""
        control = EqualizerBandControl(0, 100.0, "Bass")
        
        self.assertEqual(control.band_index, 0)
        self.assertEqual(control.frequency, 100.0)
        self.assertEqual(control.slider.value(), 0)
        
    def test_set_gain(self):
        """Test setting gain value."""
        control = EqualizerBandControl(0, 100.0, "Bass")
        
        control.set_gain(5.0)
        self.assertEqual(control.get_gain(), 5.0)
        
        control.set_gain(-3.5)
        self.assertEqual(control.get_gain(), -3.5)
        
    def test_slider_range(self):
        """Test slider range limits."""
        control = EqualizerBandControl(0, 100.0, "Bass")
        
        # Test maximum
        control.set_gain(12.0)
        self.assertEqual(control.get_gain(), 12.0)
        
        # Test minimum
        control.set_gain(-12.0)
        self.assertEqual(control.get_gain(), -12.0)
        
    def test_value_label_update(self):
        """Test that value label updates with slider."""
        control = EqualizerBandControl(0, 100.0, "Bass")
        
        control.set_gain(6.5)
        self.assertIn("6.5", control.value_label.text())
        self.assertIn("dB", control.value_label.text())


class TestEqualizerGUI(unittest.TestCase):
    """Test cases for EqualizerGUI main window."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.gui = EqualizerGUI()
        
    def tearDown(self):
        """Clean up test fixtures."""
        self.gui.close()
        
    def test_initialization(self):
        """Test GUI initialization."""
        self.assertIsNotNone(self.gui.equalizer)
        self.assertIsNotNone(self.gui.config)
        self.assertFalse(self.gui.enabled)
        
    def test_band_controls_created(self):
        """Test that all band controls are created."""
        expected_bands = len(self.gui.config['bands'])
        self.assertEqual(len(self.gui.band_controls), expected_bands)
        
    def test_preset_combo_populated(self):
        """Test that preset combo box is populated."""
        # Should have "Select Preset" plus all presets
        expected_count = 1 + len(self.gui.config['presets'])
        self.assertEqual(self.gui.preset_combo.count(), expected_count)
        
    def test_reset_all_bands(self):
        """Test resetting all bands to 0."""
        # Set some bands to non-zero values
        self.gui.band_controls[0].set_gain(5.0)
        self.gui.band_controls[1].set_gain(-3.0)
        
        # Reset
        self.gui._reset_all_bands()
        
        # Check all bands are at 0
        for control in self.gui.band_controls:
            self.assertEqual(control.get_gain(), 0.0)
            
    def test_apply_preset(self):
        """Test applying a preset."""
        # Select the bass_boost preset
        preset_index = None
        for i in range(self.gui.preset_combo.count()):
            if self.gui.preset_combo.itemData(i) == 'bass_boost':
                preset_index = i
                break
                
        self.assertIsNotNone(preset_index)
        
        # Apply preset
        self.gui.preset_combo.setCurrentIndex(preset_index)
        
        # Check that first band has positive gain (bass boost)
        first_band_gain = self.gui.band_controls[0].get_gain()
        self.assertGreater(first_band_gain, 0)
        
    def test_save_load_custom_preset(self):
        """Test saving and loading a custom preset."""
        # Set some custom gains
        test_gains = [3.0, -2.0, 1.5, 0.0, -1.0, 2.5, 0.5, -0.5, 1.0, -1.5]
        for i, gain in enumerate(test_gains):
            if i < len(self.gui.band_controls):
                self.gui.band_controls[i].set_gain(gain)
                
        # Create temporary file for preset
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            preset_file = f.name
            
        try:
            # Collect current gains
            gains = [control.get_gain() for control in self.gui.band_controls]
            
            # Create preset data
            preset_data = {
                "description": "Test preset",
                "gains": gains,
                "bands": self.gui.config['bands']
            }
            
            # Save
            with open(preset_file, 'w') as f:
                json.dump(preset_data, f, indent=2)
                
            # Reset bands
            self.gui._reset_all_bands()
            
            # Load the preset
            with open(preset_file, 'r') as f:
                loaded_preset = json.load(f)
                
            # Apply loaded gains
            for i, gain in enumerate(loaded_preset['gains']):
                self.gui.band_controls[i].set_gain(gain)
                
            # Verify gains match
            for i, expected_gain in enumerate(test_gains):
                if i < len(self.gui.band_controls):
                    actual_gain = self.gui.band_controls[i].get_gain()
                    self.assertAlmostEqual(actual_gain, expected_gain, places=1)
                    
        finally:
            # Clean up
            Path(preset_file).unlink(missing_ok=True)
            
    def test_enable_disable(self):
        """Test enable/disable functionality."""
        # Initially disabled
        self.assertFalse(self.gui.enabled)
        
        # Enable
        self.gui.enable_checkbox.setChecked(True)
        self.assertTrue(self.gui.enabled)
        
        # Disable
        self.gui.enable_checkbox.setChecked(False)
        self.assertFalse(self.gui.enabled)
        
    def test_visualization_updates(self):
        """Test that visualization can be updated."""
        # Set some gains
        self.gui.band_controls[0].set_gain(5.0)
        self.gui.band_controls[5].set_gain(-3.0)
        
        # Update visualization (should not raise error)
        self.gui._update_visualization()
        
        # Check that plot has data
        x_data, y_data = self.gui.freq_viz.line.get_data()
        self.assertGreater(len(x_data), 0)
        self.assertGreater(len(y_data), 0)


class TestGUIIntegration(unittest.TestCase):
    """Integration tests for GUI components."""
    
    def test_band_change_updates_visualization(self):
        """Test that changing a band updates the visualization."""
        gui = EqualizerGUI()
        
        try:
            # Get initial visualization data
            initial_x, initial_y = gui.freq_viz.line.get_data()
            
            # Change a band
            gui.band_controls[0].set_gain(8.0)
            
            # Trigger visualization update
            gui._update_visualization()
            
            # Get updated visualization data
            updated_x, updated_y = gui.freq_viz.line.get_data()
            
            # Data should have changed
            self.assertFalse(all(initial_y == updated_y))
            
        finally:
            gui.close()
            
    def test_preset_changes_all_bands(self):
        """Test that applying preset changes all bands."""
        gui = EqualizerGUI()
        
        try:
            # Apply flat preset first
            for i in range(gui.preset_combo.count()):
                if gui.preset_combo.itemData(i) == 'flat':
                    gui.preset_combo.setCurrentIndex(i)
                    break
                    
            # All bands should be at 0
            for control in gui.band_controls:
                self.assertEqual(control.get_gain(), 0.0)
                
            # Apply bass_boost preset
            for i in range(gui.preset_combo.count()):
                if gui.preset_combo.itemData(i) == 'bass_boost':
                    gui.preset_combo.setCurrentIndex(i)
                    break
                    
            # First bands should have positive gain
            self.assertGreater(gui.band_controls[0].get_gain(), 0.0)
            
        finally:
            gui.close()


if __name__ == '__main__':
    unittest.main()
