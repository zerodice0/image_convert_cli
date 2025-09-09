# Contributing to NanoBanana

Thank you for your interest in contributing to NanoBanana! 🍌

## Ways to Contribute

### 🐛 Report Bugs
- Use the [issue template](.github/ISSUE_TEMPLATE.md)
- Include system information and steps to reproduce
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first

### ✨ Suggest Features
- Open an issue with the feature request template
- Describe the use case and expected behavior
- Consider if it fits the project scope

### 📝 Improve Documentation
- Fix typos or unclear instructions
- Add examples and use cases
- Translate documentation (especially Korean ↔ English)

### 🔧 Code Contributions
- Fix bugs or implement features
- Follow the coding standards below
- Add tests for new functionality

## Development Setup

### Prerequisites
- Python 3.8+
- Git
- Google Gemini API key (for testing)

### Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/nanobanana.git
cd nanobanana

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements_cli.txt

# Install development dependencies
pip install pytest black flake8 mypy
```

### Testing
```bash
# Run tests
pytest

# Test both GUI and CLI versions
python batch_nanobanana_gui.py
python batch_nanobanana_cli.py --help

# Test workflows
python workflows/personal_photos.py --help
```

## Coding Standards

### Python Code Style
- Follow PEP 8
- Use Black for formatting: `black *.py`
- Use type hints where possible
- Write docstrings for functions and classes

### Code Organization
- Keep GUI and CLI logic separate
- Use `batch_nanobanana_core.py` for shared functionality
- Add new workflows to `workflows/` directory

### Documentation
- Update relevant `.md` files when changing functionality
- Add docstrings to new functions
- Include usage examples

## Submission Process

### Pull Requests
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### Commit Messages
```
feat: add new image format support
fix: resolve API timeout issues
docs: update installation guide
style: apply black formatting
refactor: extract common validation logic
test: add CLI argument validation tests
```

### Pull Request Template
- [ ] I have tested the changes locally
- [ ] I have updated relevant documentation
- [ ] I have added tests (if applicable)
- [ ] I have followed the coding standards
- [ ] I have checked that no sensitive information is included

## Code Review Process

1. **Automated checks** must pass (linting, tests)
2. **Manual review** by maintainers
3. **Testing** with different configurations
4. **Merge** after approval

## Security Guidelines

### API Keys and Secrets
- **Never** commit API keys or secrets
- Use environment variables or config files
- Add sensitive patterns to `.gitignore`

### User Data
- **Never** log sensitive user data
- Respect user privacy in error reporting
- Handle file permissions securely

## Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Celebrate contributions of all sizes

### Communication
- Use clear, descriptive issue titles
- Provide context and examples
- Be patient with responses
- Ask questions if unclear

## Recognition

All contributors will be acknowledged in:
- GitHub contributors list
- Project documentation
- Release notes (for significant contributions)

## Questions?

- 📚 Check existing [documentation](README.md)
- 🐛 Search [existing issues](../../issues)
- 💬 Start a [discussion](../../discussions)
- 📧 Contact maintainers

Thank you for making NanoBanana better! 🚀