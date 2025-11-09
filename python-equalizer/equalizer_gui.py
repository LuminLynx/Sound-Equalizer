#!/usr/bin/env python3
"""
GUI for Sound Equalizer

A PyQt5-based graphical user interface for the Sound Equalizer.
Provides real-time frequency visualization, 10-band equalizer controls,
preset management, and custom preset save/load functionality.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSlider, QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from equalizer import SoundEqualizer
from audio_processor import AudioProcessor


class FrequencyVisualization(FigureCanvas):
    """Widget for displaying frequency response visualization."""
    
    def __init__(self, parent=None):
        """Initialize the frequency visualization widget."""
        self.figure = Figure(figsize=(8, 3), facecolor='#f0f0f0')
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.setParent(parent)
        
        # Configure plot
        self.axes.set_xlabel('Frequency (Hz)')
        self.axes.set_ylabel('Gain (dB)')
        self.axes.set_title('Equalizer Frequency Response')
        self.axes.grid(True, alpha=0.3)
        self.axes.set_xscale('log')
        self.axes.set_xlim([20, 20000])
        self.axes.set_ylim([-15, 15])
        
        # Initialize empty line
        self.line, = self.axes.plot([], [], 'b-', linewidth=2)
        self.figure.tight_layout()
        
    def update_plot(self, frequencies: np.ndarray, magnitude_db: np.ndarray):
        """Update the frequency response plot."""
        self.line.set_data(frequencies, magnitude_db)
        self.draw()


class EqualizerBandControl(QWidget):
    """Widget for a single equalizer band control."""
    
    value_changed = pyqtSignal(int, float)  # band_index, gain_db
    
    def __init__(self, band_index: int, frequency: float, description: str, parent=None):
        """
        Initialize a band control widget.
        
        Args:
            band_index: Index of the band
            frequency: Center frequency in Hz
            description: Band description
            parent: Parent widget
        """
        super().__init__(parent)
        self.band_index = band_index
        self.frequency = frequency
        
        layout = QVBoxLayout()
        layout.setSpacing(5)
        
        # Frequency label
        freq_label = QLabel(f"{frequency:.0f} Hz")
        freq_label.setAlignment(Qt.AlignCenter)
        freq_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(freq_label)
        
        # Description label
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 10px; color: #666;")
        layout.addWidget(desc_label)
        
        # Gain value label
        self.value_label = QLabel("0.0 dB")
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setStyleSheet("font-size: 11px;")
        layout.addWidget(self.value_label)
        
        # Slider
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(-120)  # -12 dB * 10
        self.slider.setMaximum(120)   # +12 dB * 10
        self.slider.setValue(0)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(30)  # 3 dB intervals
        self.slider.setMinimumHeight(200)
        self.slider.valueChanged.connect(self._on_slider_changed)
        layout.addWidget(self.slider)
        
        self.setLayout(layout)
        
    def _on_slider_changed(self, value: int):
        """Handle slider value changes."""
        gain_db = value / 10.0
        self.value_label.setText(f"{gain_db:+.1f} dB")
        self.value_changed.emit(self.band_index, gain_db)
        
    def set_gain(self, gain_db: float):
        """Set the gain value programmatically."""
        self.slider.blockSignals(True)
        self.slider.setValue(int(gain_db * 10))
        self.value_label.setText(f"{gain_db:+.1f} dB")
        self.slider.blockSignals(False)
        
    def get_gain(self) -> float:
        """Get the current gain value."""
        return self.slider.value() / 10.0


class EqualizerGUI(QMainWindow):
    """Main GUI window for the Sound Equalizer."""
    
    def __init__(self):
        """Initialize the GUI."""
        super().__init__()
        
        # Load configuration
        config_path = Path(__file__).parent / 'config.json'
        with open(config_path, 'r') as f:
            self.config = json.load(f)
            
        # Initialize equalizer (without starting audio)
        self.equalizer = SoundEqualizer()
        self.enabled = False
        
        # Initialize UI
        self._init_ui()
        
        # Set up visualization update timer
        self.viz_timer = QTimer()
        self.viz_timer.timeout.connect(self._update_visualization)
        self.viz_timer.start(500)  # Update every 500ms
        
        # Initial visualization update
        self._update_visualization()
        
    def _init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Sound Equalizer - MVP')
        self.setMinimumSize(1200, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel('Sound Equalizer')
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont('Arial', 18, QFont.Bold))
        main_layout.addWidget(title)
        
        # Frequency visualization
        viz_group = QGroupBox("Frequency Response")
        viz_layout = QVBoxLayout()
        self.freq_viz = FrequencyVisualization()
        viz_layout.addWidget(self.freq_viz)
        viz_group.setLayout(viz_layout)
        main_layout.addWidget(viz_group)
        
        # Control panel
        control_layout = QHBoxLayout()
        
        # Enable/Disable checkbox
        self.enable_checkbox = QCheckBox("Enable Equalizer")
        self.enable_checkbox.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.enable_checkbox.stateChanged.connect(self._on_enable_changed)
        control_layout.addWidget(self.enable_checkbox)
        
        control_layout.addStretch()
        
        # Preset selector
        preset_label = QLabel("Preset:")
        preset_label.setStyleSheet("font-size: 14px;")
        control_layout.addWidget(preset_label)
        
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(200)
        self.preset_combo.addItem("-- Select Preset --", None)
        for preset_name, preset_data in self.config['presets'].items():
            self.preset_combo.addItem(f"{preset_name} - {preset_data['description']}", preset_name)
        self.preset_combo.currentIndexChanged.connect(self._on_preset_changed)
        control_layout.addWidget(self.preset_combo)
        
        # Save preset button
        save_btn = QPushButton("Save Preset")
        save_btn.clicked.connect(self._save_custom_preset)
        control_layout.addWidget(save_btn)
        
        # Load preset button
        load_btn = QPushButton("Load Preset")
        load_btn.clicked.connect(self._load_custom_preset)
        control_layout.addWidget(load_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset All")
        reset_btn.clicked.connect(self._reset_all_bands)
        control_layout.addWidget(reset_btn)
        
        main_layout.addLayout(control_layout)
        
        # Equalizer bands
        eq_group = QGroupBox("10-Band Equalizer")
        eq_layout = QHBoxLayout()
        eq_layout.setSpacing(15)
        
        self.band_controls: List[EqualizerBandControl] = []
        bands = self.config['bands']
        
        for i, band in enumerate(bands):
            band_control = EqualizerBandControl(
                i,
                band['frequency'],
                band['description']
            )
            band_control.value_changed.connect(self._on_band_changed)
            self.band_controls.append(band_control)
            eq_layout.addWidget(band_control)
            
        eq_group.setLayout(eq_layout)
        main_layout.addWidget(eq_group)
        
        central_widget.setLayout(main_layout)
        
        # Set initial state
        self._update_status_message("Equalizer initialized. Use controls to adjust settings.")
        
    def _on_enable_changed(self, state: int):
        """Handle enable/disable checkbox changes."""
        self.enabled = (state == Qt.Checked)
        
        if self.enabled:
            # Start the equalizer
            try:
                # Apply current settings to equalizer
                self._apply_current_settings()
                # Note: We don't actually start audio processing in this MVP
                # as it requires PyAudio and proper audio setup
                self._update_status_message("Equalizer enabled (audio processing requires PyAudio)")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to enable equalizer: {e}")
                self.enable_checkbox.setChecked(False)
                self.enabled = False
        else:
            self._update_status_message("Equalizer disabled")
            
    def _on_band_changed(self, band_index: int, gain_db: float):
        """Handle band slider changes."""
        if self.enabled:
            # Update the equalizer's band configuration
            bands = self.equalizer.processor.bands
            if band_index < len(bands):
                bands[band_index].gain_db = gain_db
                
        # Update visualization
        self._update_visualization()
        
    def _on_preset_changed(self, index: int):
        """Handle preset selection changes."""
        preset_name = self.preset_combo.itemData(index)
        
        if preset_name is None:
            return
            
        # Apply the preset
        preset = self.config['presets'][preset_name]
        gains = preset['gains']
        
        # Update sliders
        for i, gain in enumerate(gains):
            if i < len(self.band_controls):
                self.band_controls[i].set_gain(gain)
                
        # Apply to equalizer if enabled
        if self.enabled:
            self._apply_current_settings()
            
        self._update_visualization()
        self._update_status_message(f"Applied preset: {preset_name}")
        
    def _reset_all_bands(self):
        """Reset all bands to 0 dB."""
        for control in self.band_controls:
            control.set_gain(0.0)
            
        if self.enabled:
            self._apply_current_settings()
            
        self._update_visualization()
        self._update_status_message("All bands reset to 0 dB")
        
    def _apply_current_settings(self):
        """Apply current slider values to the equalizer."""
        # Clear existing bands
        self.equalizer.processor.clear_bands()
        
        # Add bands with current gains
        bands = self.config['bands']
        for i, band in enumerate(bands):
            if i < len(self.band_controls):
                gain_db = self.band_controls[i].get_gain()
                self.equalizer.processor.add_band(
                    frequency=band['frequency'],
                    gain_db=gain_db,
                    q_factor=band.get('q_factor', 1.0)
                )
                
    def _update_visualization(self):
        """Update the frequency response visualization."""
        # Apply current settings to a temporary processor for visualization
        temp_processor = AudioProcessor(sample_rate=self.equalizer.sample_rate)
        
        bands = self.config['bands']
        for i, band in enumerate(bands):
            if i < len(self.band_controls):
                gain_db = self.band_controls[i].get_gain()
                temp_processor.add_band(
                    frequency=band['frequency'],
                    gain_db=gain_db,
                    q_factor=band.get('q_factor', 1.0)
                )
                
        # Get frequency response
        freqs, mag_db, _ = temp_processor.get_frequency_response()
        
        # Update plot
        self.freq_viz.update_plot(freqs, mag_db)
        
    def _save_custom_preset(self):
        """Save current settings as a custom preset file."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Custom Preset",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not filename:
            return
            
        # Collect current gains
        gains = [control.get_gain() for control in self.band_controls]
        
        # Create preset data
        preset_data = {
            "description": "Custom preset",
            "gains": gains,
            "bands": self.config['bands']
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(preset_data, f, indent=2)
                
            QMessageBox.information(self, "Success", f"Preset saved to {filename}")
            self._update_status_message(f"Preset saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save preset: {e}")
            
    def _load_custom_preset(self):
        """Load a custom preset file."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Custom Preset",
            str(Path.home()),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not filename:
            return
            
        try:
            with open(filename, 'r') as f:
                preset_data = json.load(f)
                
            # Validate preset data
            if 'gains' not in preset_data:
                raise ValueError("Invalid preset file: missing 'gains' field")
                
            gains = preset_data['gains']
            
            if len(gains) != len(self.band_controls):
                raise ValueError(f"Preset has {len(gains)} bands, expected {len(self.band_controls)}")
                
            # Apply gains to sliders
            for i, gain in enumerate(gains):
                self.band_controls[i].set_gain(gain)
                
            # Apply to equalizer if enabled
            if self.enabled:
                self._apply_current_settings()
                
            self._update_visualization()
            
            description = preset_data.get('description', 'Custom preset')
            QMessageBox.information(self, "Success", f"Loaded preset: {description}")
            self._update_status_message(f"Loaded preset from {filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load preset: {e}")
            
    def _update_status_message(self, message: str):
        """Update the status bar message."""
        self.statusBar().showMessage(message, 5000)
        
    def closeEvent(self, event):
        """Handle window close event."""
        # Clean up equalizer resources
        if self.enabled:
            self.equalizer.cleanup()
        event.accept()


def main():
    """Main entry point for the GUI."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = EqualizerGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
