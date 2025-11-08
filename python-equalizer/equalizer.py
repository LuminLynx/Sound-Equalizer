#!/usr/bin/env python3
"""
Sound Equalizer for Linux (Debian)

A real-time audio equalizer implementation using PyAudio and NumPy.
This script processes audio input through a configurable multi-band equalizer.
"""

import sys
import json
import argparse
import numpy as np
from pathlib import Path

# Import PyAudio only if not in test mode
pyaudio = None

from audio_processor import AudioProcessor, normalize_audio


class SoundEqualizer:
    """Real-time sound equalizer using PyAudio."""
    
    def __init__(self, config_file='config.json'):
        """
        Initialize the sound equalizer.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config = self._load_config(config_file)
        self.sample_rate = self.config.get('sample_rate', 44100)
        self.buffer_size = self.config.get('buffer_size', 1024)
        
        # Initialize audio processor
        self.processor = AudioProcessor(sample_rate=self.sample_rate)
        
        # Load default bands
        self._load_bands_from_config()
        
        # PyAudio objects (initialized on demand)
        self.audio = None
        self.stream = None
        self.running = False
        
    def _load_config(self, config_file):
        """Load configuration from JSON file."""
        config_path = Path(__file__).parent / config_file
        
        if not config_path.exists():
            print(f"Warning: Config file {config_file} not found, using defaults.")
            return self._default_config()
            
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._default_config()
            
    def _default_config(self):
        """Return default configuration."""
        return {
            'sample_rate': 44100,
            'buffer_size': 1024,
            'bands': []
        }
        
    def _load_bands_from_config(self):
        """Load equalizer bands from configuration."""
        bands = self.config.get('bands', [])
        for band in bands:
            self.processor.add_band(
                frequency=band['frequency'],
                gain_db=band['gain_db'],
                q_factor=band.get('q_factor', 1.0)
            )
            
    def apply_preset(self, preset_name):
        """
        Apply a preset configuration.
        
        Args:
            preset_name (str): Name of the preset to apply
        """
        presets = self.config.get('presets', {})
        
        if preset_name not in presets:
            print(f"Error: Preset '{preset_name}' not found.")
            self.list_presets()
            return False
            
        preset = presets[preset_name]
        gains = preset['gains']
        bands = self.config.get('bands', [])
        
        if len(gains) != len(bands):
            print(f"Error: Preset has {len(gains)} gains but {len(bands)} bands configured.")
            return False
            
        # Clear and reload bands with new gains
        self.processor.clear_bands()
        for band, gain in zip(bands, gains):
            self.processor.add_band(
                frequency=band['frequency'],
                gain_db=gain,
                q_factor=band.get('q_factor', 1.0)
            )
            
        print(f"Applied preset: {preset_name} - {preset['description']}")
        return True
        
    def list_presets(self):
        """List available presets."""
        presets = self.config.get('presets', {})
        
        if not presets:
            print("No presets available.")
            return
            
        print("\nAvailable presets:")
        for name, preset in presets.items():
            print(f"  - {name}: {preset['description']}")
            
    def list_bands(self):
        """Display current equalizer band configuration."""
        bands = self.processor.bands
        
        if not bands:
            print("No equalizer bands configured.")
            return
            
        print("\nCurrent equalizer configuration:")
        print(f"{'Band':<4} {'Frequency':<12} {'Gain':<10} {'Q Factor':<10}")
        print("-" * 40)
        
        config_bands = self.config.get('bands', [])
        for i, (band, config_band) in enumerate(zip(bands, config_bands)):
            desc = config_band.get('description', '')
            print(f"{i+1:<4} {band.frequency:<12.1f} {band.gain_db:>+6.1f} dB  {band.q_factor:<10.2f}  {desc}")
            
    def audio_callback(self, in_data, frame_count, time_info, status):
        """
        Callback function for PyAudio stream processing.
        
        Args:
            in_data: Input audio data
            frame_count: Number of frames
            time_info: Timing information
            status: Status flags
            
        Returns:
            tuple: (output_data, continue_flag)
        """
        if status:
            print(f"Status: {status}")
            
        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        
        # Process through equalizer
        processed = self.processor.process_block(audio_data.astype(np.float32))
        
        # Normalize to prevent clipping
        processed = normalize_audio(processed, target_level=-1.0)
        
        # Convert back to int16
        output = np.clip(processed, -32768, 32767).astype(np.int16)
        
        return (output.tobytes(), pyaudio.paContinue)
        
    def start(self):
        """Start the equalizer in real-time mode."""
        # Import PyAudio here for real-time mode
        global pyaudio
        try:
            import pyaudio as pa
            pyaudio = pa
        except ImportError:
            print("Error: PyAudio is not installed.")
            print("Install it with: pip install pyaudio")
            print("On Debian/Ubuntu, you may also need: sudo apt-get install portaudio19-dev python3-pyaudio")
            return
            
        if self.stream is not None:
            print("Equalizer is already running.")
            return
        
        # Initialize PyAudio
        if self.audio is None:
            self.audio = pyaudio.PyAudio()
            
        print(f"\nStarting Sound Equalizer...")
        print(f"Sample rate: {self.sample_rate} Hz")
        print(f"Buffer size: {self.buffer_size} samples")
        
        self.list_bands()
        
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                output=True,
                frames_per_buffer=self.buffer_size,
                stream_callback=self.audio_callback
            )
            
            self.stream.start_stream()
            self.running = True
            
            print("\nEqualizer is running. Press Ctrl+C to stop.")
            
            # Keep running until interrupted
            while self.stream.is_active():
                pass
                
        except KeyboardInterrupt:
            print("\n\nStopping equalizer...")
        except Exception as e:
            print(f"\nError: {e}")
        finally:
            self.stop()
            
    def stop(self):
        """Stop the equalizer."""
        if self.stream is not None:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
        self.running = False
        print("Equalizer stopped.")
        
    def cleanup(self):
        """Clean up resources."""
        self.stop()
        if self.audio is not None:
            self.audio.terminate()
            self.audio = None
            
    def test_mode(self):
        """Run in test mode (show configuration without processing audio)."""
        print("\n=== Sound Equalizer Test Mode ===")
        print(f"Sample rate: {self.sample_rate} Hz")
        print(f"Buffer size: {self.buffer_size} samples")
        
        self.list_bands()
        self.list_presets()
        
        # Display frequency response
        print("\nFrequency response calculation:")
        freqs, mag_db, _ = self.processor.get_frequency_response()
        
        print(f"Response calculated for {len(freqs)} frequency points")
        print(f"Frequency range: {freqs[0]:.1f} Hz to {freqs[-1]:.1f} Hz")
        
        print("\nTest mode completed successfully!")
        return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Sound Equalizer for Linux (Debian)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test                    # Test mode (no audio processing)
  %(prog)s --preset bass_boost       # Start with bass boost preset
  %(prog)s --list-presets           # List available presets
  %(prog)s                          # Start with default configuration
        """
    )
    
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file (default: config.json)'
    )
    
    parser.add_argument(
        '--preset',
        help='Apply a preset configuration'
    )
    
    parser.add_argument(
        '--list-presets',
        action='store_true',
        help='List available presets and exit'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (no audio processing)'
    )
    
    args = parser.parse_args()
    
    # Create equalizer instance
    try:
        equalizer = SoundEqualizer(config_file=args.config)
    except Exception as e:
        print(f"Error initializing equalizer: {e}")
        return 1
        
    try:
        # Handle different modes
        if args.list_presets:
            equalizer.list_presets()
            return 0
            
        if args.test:
            success = equalizer.test_mode()
            return 0 if success else 1
            
        # Apply preset if specified
        if args.preset:
            if not equalizer.apply_preset(args.preset):
                return 1
                
        # Start real-time processing
        equalizer.start()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        equalizer.cleanup()
        
    return 0


if __name__ == '__main__':
    sys.exit(main())
