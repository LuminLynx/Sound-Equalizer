# Tests for Sound Equalizer

This directory contains unit tests for the Sound Equalizer project.

## Running Tests

### Run all tests
```bash
python -m pytest
```

### Run with coverage
```bash
python -m pytest --cov=python-equalizer --cov-report=html
```

### Run specific test file
```bash
python -m pytest tests/test_audio_processor.py
```

### Run specific test class
```bash
python -m pytest tests/test_audio_processor.py::TestAudioProcessor
```

### Run specific test method
```bash
python -m pytest tests/test_audio_processor.py::TestAudioProcessor::test_add_band
```

## Test Structure

- `test_audio_processor.py` - Tests for the audio processing module
  - `TestEqualizerBand` - Tests for the EqualizerBand class
  - `TestAudioProcessor` - Tests for the AudioProcessor class
  - `TestNormalizeAudio` - Tests for audio normalization
  - `TestApplyFade` - Tests for fade in/out functionality

- `test_equalizer.py` - Tests for the main equalizer module
  - `TestSoundEqualizer` - Tests for the SoundEqualizer class
  - `TestEqualizerConfiguration` - Tests for configuration loading

## Writing New Tests

When adding new tests, follow these guidelines:

1. Place test files in this directory with the prefix `test_`
2. Name test classes with the prefix `Test`
3. Name test methods with the prefix `test_`
4. Use descriptive test names that explain what is being tested
5. Include docstrings for test classes and methods
6. Use `setUp()` and `tearDown()` for common initialization and cleanup
7. Aim for high code coverage (>80%)

## Test Dependencies

Tests require:
- pytest
- numpy
- scipy

Install with:
```bash
pip install pytest numpy scipy
```

For development dependencies including coverage:
```bash
pip install -r requirements-dev.txt
```
