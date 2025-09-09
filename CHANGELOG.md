# Changelog

All notable changes to NanoBanana will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-09

### Added
- 🎨 **GUI Version**: User-friendly tkinter interface for beginners
- 💻 **CLI Version**: Command-line interface for advanced users and automation
- 🔧 **Core Engine**: Shared processing logic for consistent results
- 🚀 **Installation Scripts**: Automated setup for Windows, Mac, and Linux
- 📚 **Complete Documentation**: Usage guides, troubleshooting, and quick reference
- 🛠️ **Workflow Tools**: Pre-built scripts for common use cases
  - Personal photo processor with GUI bridge
  - Business batch processing with multiple styles  
  - Multi-style tester for creators
- 🔐 **Secure API Management**: Multiple methods for API key handling
  - Environment variables (recommended)
  - Configuration files with proper permissions
  - Interactive secure input
  - Command-line arguments (with warnings)
- 🎯 **Image Format Support**: 
  - Input: PNG, JPG, JPEG, WebP, BMP, TIFF
  - Output: PNG, JPG, JPEG, WebP
- ⚡ **Performance Features**:
  - Concurrent processing support
  - Progress tracking with visual feedback
  - Dry-run mode for testing
  - Comprehensive logging
- 📱 **Cross-Platform Support**: Windows, macOS, Linux
- 🌐 **Internationalization**: Korean and English documentation

### Features

#### GUI Version
- Drag-and-drop folder selection
- Real-time progress tracking
- Built-in log viewer
- Start/stop processing controls
- Settings persistence
- Error handling with user-friendly messages

#### CLI Version  
- Batch processing with parallel execution
- Rich terminal output with colors and progress bars
- Flexible output formats and naming
- Integration with shell scripts and automation
- Comprehensive logging and debugging options
- Signal handling for graceful shutdown

#### Workflow Scripts
- **Personal Photos** (`workflows/personal_photos.py`): Simplified interface bridging GUI and CLI
- **Business Batch** (`workflows/business_batch.sh`): Professional batch processing with 5 style presets
- **Creator Multi-Style** (`workflows/creator_multistyle.py`): Test multiple styles with HTML comparison

### Documentation
- **Installation Guide**: Step-by-step setup for all platforms
- **Usage Guide**: Complete user manual with examples
- **Quick Reference**: Cheat sheet for commands and options  
- **Troubleshooting**: Common issues and solutions
- **CLI Documentation**: Advanced command-line usage

### Security
- API key protection with multiple secure methods
- File permission handling
- Input validation and sanitization
- No sensitive data in logs or output

### Dependencies
- `google-genai>=0.7.0`: Google Gemini API integration
- `Pillow>=10.0.0`: Image processing
- `rich>=13.0.0`: Terminal UI enhancements  
- `tqdm>=4.65.0`: Progress bars
- `python-dotenv>=1.0.0`: Environment configuration

## [Unreleased]

### Planned Features
- [ ] Additional AI model support (OpenAI, Anthropic)
- [ ] Batch size optimization
- [ ] Image preprocessing options
- [ ] Template system for common prompts
- [ ] Web interface option
- [ ] Docker containerization
- [ ] Plugin system for custom workflows

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute to this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.