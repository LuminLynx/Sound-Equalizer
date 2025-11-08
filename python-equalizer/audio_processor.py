#!/usr/bin/env python3
"""
Audio Processing Module for Sound Equalizer

This module provides core audio processing functions for implementing
a parametric equalizer using digital signal processing techniques.
"""

import numpy as np
from scipy import signal


class EqualizerBand:
    """Represents a single equalizer band with frequency, gain, and Q factor."""
    
    def __init__(self, frequency, gain_db, q_factor=1.0):
        """
        Initialize an equalizer band.
        
        Args:
            frequency (float): Center frequency in Hz
            gain_db (float): Gain in decibels (-20 to +20 typical range)
            q_factor (float): Quality factor (0.1 to 10, default 1.0)
        """
        self.frequency = frequency
        self.gain_db = gain_db
        self.q_factor = q_factor
        
    def get_filter_coefficients(self, sample_rate):
        """
        Calculate biquad filter coefficients for this band.
        
        Args:
            sample_rate (int): Sample rate in Hz
            
        Returns:
            tuple: (b, a) filter coefficients
        """
        # Convert gain from dB to linear
        gain_linear = 10 ** (self.gain_db / 20.0)
        
        # Normalize frequency
        w0 = 2 * np.pi * self.frequency / sample_rate
        
        # Calculate alpha (bandwidth parameter)
        alpha = np.sin(w0) / (2 * self.q_factor)
        
        # Peaking EQ filter coefficients
        cos_w0 = np.cos(w0)
        
        # Numerator coefficients (b)
        b0 = 1 + alpha * gain_linear
        b1 = -2 * cos_w0
        b2 = 1 - alpha * gain_linear
        
        # Denominator coefficients (a)
        a0 = 1 + alpha / gain_linear
        a1 = -2 * cos_w0
        a2 = 1 - alpha / gain_linear
        
        # Normalize by a0
        b = np.array([b0/a0, b1/a0, b2/a0])
        a = np.array([1.0, a1/a0, a2/a0])
        
        return b, a


class AudioProcessor:
    """Process audio data through an equalizer filter chain."""
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the audio processor.
        
        Args:
            sample_rate (int): Sample rate in Hz (default 44100)
        """
        self.sample_rate = sample_rate
        self.bands = []
        self.filter_states = []
        
    def add_band(self, frequency, gain_db, q_factor=1.0):
        """
        Add an equalizer band.
        
        Args:
            frequency (float): Center frequency in Hz
            gain_db (float): Gain in decibels
            q_factor (float): Quality factor (default 1.0)
        """
        band = EqualizerBand(frequency, gain_db, q_factor)
        self.bands.append(band)
        self.filter_states.append(None)
        
    def clear_bands(self):
        """Remove all equalizer bands."""
        self.bands.clear()
        self.filter_states.clear()
        
    def process_block(self, audio_data):
        """
        Process a block of audio data through all equalizer bands.
        
        Args:
            audio_data (numpy.ndarray): Input audio data
            
        Returns:
            numpy.ndarray: Processed audio data
        """
        if len(self.bands) == 0:
            return audio_data
            
        # Convert to float for processing
        processed = audio_data.astype(np.float32)
        
        # Apply each band filter sequentially
        for i, band in enumerate(self.bands):
            b, a = band.get_filter_coefficients(self.sample_rate)
            
            # Apply filter with state preservation for continuity
            if self.filter_states[i] is None:
                # Initialize state
                processed, self.filter_states[i] = signal.lfilter(
                    b, a, processed, zi=signal.lfilter_zi(b, a) * processed[0]
                )
            else:
                # Continue with previous state
                processed, self.filter_states[i] = signal.lfilter(
                    b, a, processed, zi=self.filter_states[i]
                )
        
        return processed
        
    def reset_states(self):
        """Reset all filter states."""
        self.filter_states = [None] * len(self.bands)
        
    def get_frequency_response(self, frequencies=None):
        """
        Calculate the frequency response of the equalizer.
        
        Args:
            frequencies (numpy.ndarray): Frequencies to evaluate (Hz)
            
        Returns:
            tuple: (frequencies, magnitude_db, phase)
        """
        if frequencies is None:
            frequencies = np.logspace(1, np.log10(self.sample_rate/2), 1000)
            
        # Start with flat response
        total_response = np.ones(len(frequencies), dtype=complex)
        
        # Combine all band responses
        for band in self.bands:
            b, a = band.get_filter_coefficients(self.sample_rate)
            w, h = signal.freqz(b, a, worN=frequencies, fs=self.sample_rate)
            total_response *= h
            
        magnitude_db = 20 * np.log10(np.abs(total_response))
        phase = np.angle(total_response)
        
        return frequencies, magnitude_db, phase


def normalize_audio(audio_data, target_level=-3.0):
    """
    Normalize audio data to prevent clipping.
    
    Args:
        audio_data (numpy.ndarray): Input audio data
        target_level (float): Target level in dB (default -3.0)
        
    Returns:
        numpy.ndarray: Normalized audio data
    """
    # Find peak
    peak = np.max(np.abs(audio_data))
    
    if peak == 0:
        return audio_data
        
    # Calculate normalization factor
    target_linear = 10 ** (target_level / 20.0)
    scale = target_linear / peak
    
    # Apply scaling
    return audio_data * scale


def apply_fade(audio_data, fade_samples=1000):
    """
    Apply fade in/out to prevent clicks.
    
    Args:
        audio_data (numpy.ndarray): Input audio data
        fade_samples (int): Number of samples for fade (default 1000)
        
    Returns:
        numpy.ndarray: Audio data with fades applied
    """
    result = audio_data.copy()
    
    # Fade in
    fade_in = np.linspace(0, 1, min(fade_samples, len(result)))
    result[:len(fade_in)] *= fade_in
    
    # Fade out
    fade_out = np.linspace(1, 0, min(fade_samples, len(result)))
    result[-len(fade_out):] *= fade_out
    
    return result
