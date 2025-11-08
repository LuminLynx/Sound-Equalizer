# Contributing to Sound Equalizer

Thank you for your interest in contributing to the Sound Equalizer project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment Setup](#development-environment-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation Guidelines](#documentation-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Community](#community)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. We pledge to:

- Be respectful of differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Our Standards

Examples of behavior that contributes to a positive environment:

- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards others

Examples of unacceptable behavior:

- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Sound-Equalizer.git
   cd Sound-Equalizer
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/LuminLynx/Sound-Equalizer.git
   ```
4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment Setup

### System Requirements

- Linux (Debian/Ubuntu recommended, but any distribution works)
- Python 3.8 or higher
- Git

### Installing Dependencies

#### Ubuntu/Debian

```bash
# System packages for audio development
sudo apt-get update
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    pulseaudio \
    ladspa-sdk \
    swh-plugins

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt  # When available
```

#### Fedora/RHEL

```bash
sudo dnf install -y \
    python3 \
    python3-pip \
    portaudio-devel \
    pulseaudio \
    ladspa \
    swh-plugins

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Arch Linux

```bash
sudo pacman -S \
    python \
    python-pip \
    portaudio \
    pulseaudio \
    ladspa \
    swh-plugins

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Verifying Installation

```bash
# Test the equalizer in test mode
cd python-equalizer
python3 equalizer.py --test

# Run examples
python3 examples.py
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Code contributions**
   - Bug fixes
   - New features
   - Performance improvements
   - Code refactoring

2. **Documentation**
   - Fixing typos or clarifying existing docs
   - Adding new guides or tutorials
   - Creating examples
   - Translating documentation

3. **Testing**
   - Writing unit tests
   - Writing integration tests
   - Manual testing and bug reports
   - Performance testing

4. **Design**
   - UI/UX improvements
   - Logo and branding
   - Website design
   - Documentation layout

5. **Community support**
   - Answering questions in issues
   - Helping others in discussions
   - Creating tutorials or blog posts
   - Organizing events

### Finding Something to Work On

- Check the [issue tracker](https://github.com/LuminLynx/Sound-Equalizer/issues) for open issues
- Look for issues labeled `good first issue` for beginner-friendly tasks
- Look for issues labeled `help wanted` for areas where we need assistance
- Check the [ROADMAP.md](ROADMAP.md) for planned features
- Suggest your own ideas by opening an issue first

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- **Line length**: Maximum 100 characters (not 79)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Use single quotes for strings unless double quotes avoid escaping
- **Imports**: Group imports in this order:
  1. Standard library imports
  2. Third-party library imports
  3. Local application imports

### Code Quality Tools

We use the following tools (will be enforced via CI):

```bash
# Code formatting
black python-equalizer/

# Linting
pylint python-equalizer/

# Type checking
mypy python-equalizer/

# Import sorting
isort python-equalizer/
```

### Naming Conventions

- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private attributes**: `_leading_underscore`
- **File names**: `snake_case.py`

### Documentation in Code

- All public functions, classes, and modules must have docstrings
- Use Google style docstrings:

```python
def process_audio(audio_data, sample_rate):
    """
    Process audio data through the equalizer.
    
    Args:
        audio_data (numpy.ndarray): Input audio samples
        sample_rate (int): Sample rate in Hz
        
    Returns:
        numpy.ndarray: Processed audio samples
        
    Raises:
        ValueError: If sample_rate is invalid
        
    Example:
        >>> processor = AudioProcessor(sample_rate=44100)
        >>> output = processor.process_audio(input_data, 44100)
    """
    pass
```

### Best Practices

1. **Keep functions small and focused** - Each function should do one thing well
2. **Use meaningful variable names** - Avoid abbreviations unless obvious
3. **Don't repeat yourself (DRY)** - Extract common code into functions
4. **Handle errors gracefully** - Use try/except blocks appropriately
5. **Write self-documenting code** - Code should be readable without comments
6. **Add comments for complex logic** - Explain why, not what
7. **Use type hints** - Help with IDE support and catch errors early

## Testing Guidelines

### Writing Tests

- Place tests in a `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use `unittest` or `pytest` framework
- Aim for at least 80% code coverage

### Test Structure

```python
import unittest
from audio_processor import AudioProcessor

class TestAudioProcessor(unittest.TestCase):
    """Test cases for AudioProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = AudioProcessor(sample_rate=44100)
        
    def test_add_band(self):
        """Test adding an equalizer band."""
        self.processor.add_band(1000, 6.0, 1.0)
        self.assertEqual(len(self.processor.bands), 1)
        
    def test_frequency_response(self):
        """Test frequency response calculation."""
        self.processor.add_band(1000, 6.0, 1.0)
        freqs, mag, phase = self.processor.get_frequency_response()
        self.assertIsNotNone(freqs)
        self.assertGreater(len(freqs), 0)
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=python-equalizer --cov-report=html

# Run specific test file
python -m pytest tests/test_audio_processor.py

# Run specific test function
python -m pytest tests/test_audio_processor.py::TestAudioProcessor::test_add_band
```

## Documentation Guidelines

### README Updates

- Keep README.md concise and focused on overview
- Move detailed guides to separate files in `docs/`
- Include code examples where appropriate
- Use clear headings and formatting

### Documentation Files

- Use Markdown for all documentation
- Include a table of contents for long documents
- Use code blocks with syntax highlighting
- Include screenshots where helpful
- Keep language clear and concise

### Inline Documentation

- Document all public APIs
- Include examples in docstrings
- Explain parameters and return values
- Document exceptions that may be raised

## Pull Request Process

### Before Submitting

1. **Update your branch** with the latest from upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests** to ensure nothing is broken:
   ```bash
   python -m pytest
   ```

3. **Run linters** to check code quality:
   ```bash
   black --check python-equalizer/
   pylint python-equalizer/
   ```

4. **Update documentation** if needed

5. **Test your changes** manually

### Submitting a Pull Request

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request** on GitHub

3. **Fill out the PR template** with:
   - Clear description of changes
   - Motivation and context
   - How to test the changes
   - Screenshots (if UI changes)
   - Related issues

4. **Respond to feedback** from reviewers

5. **Update your PR** as needed:
   ```bash
   git add .
   git commit -m "Address review comments"
   git push origin feature/your-feature-name
   ```

### PR Title Format

Use conventional commit format:

- `feat: Add GUI for equalizer control`
- `fix: Correct frequency response calculation`
- `docs: Update installation instructions`
- `test: Add unit tests for AudioProcessor`
- `refactor: Simplify filter coefficient calculation`
- `perf: Optimize real-time processing`
- `style: Format code with black`
- `chore: Update dependencies`

### Review Process

1. At least one maintainer will review your PR
2. Automated CI checks must pass
3. Code coverage should not decrease
4. All discussions must be resolved
5. Maintainer will merge when approved

## Issue Reporting

### Bug Reports

When reporting a bug, include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Exact steps to trigger the bug
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Environment**:
  - OS and version
  - Python version
  - Package versions
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

### Feature Requests

When requesting a feature, include:

- **Description**: Clear description of the feature
- **Use case**: Why is this feature needed?
- **Examples**: How would it be used?
- **Alternatives**: Any alternatives considered?
- **Additional context**: Any other relevant information

### Issue Labels

- `bug`: Something isn't working
- `feature`: New feature or request
- `documentation`: Improvements or additions to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on
- `duplicate`: This issue already exists

## Community

### Communication Channels

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Pull Requests**: For code review and contribution

### Getting Help

If you need help:

1. Check the [README.md](README.md) and documentation in `docs/`
2. Search existing issues for similar problems
3. Ask in GitHub Discussions
4. Open a new issue with the `question` label

### Recognition

Contributors will be recognized in:

- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graph

## License

By contributing to Sound Equalizer, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Sound Equalizer! Your efforts help make this project better for everyone.
