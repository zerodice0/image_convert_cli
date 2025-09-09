# 🍌 NanoBanana AI Image Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://aistudio.google.com/)

Transform your images with AI! NanoBanana is a powerful yet easy-to-use tool that leverages Google's Gemini AI to convert images based on natural language prompts.

![NanoBanana Demo](docs/demo.gif)

## ✨ Features

### 🖥️ **Dual Interface**
- **GUI Version**: Beginner-friendly with drag-and-drop interface
- **CLI Version**: Advanced command-line tool for automation and batch processing

### 🎨 **AI-Powered Transformation**
- Transform images with natural language prompts
- Support for multiple artistic styles (vintage, artistic, cinematic, etc.)
- Batch processing for handling multiple images at once

### 🔧 **Professional Tools**
- **Multi-style tester**: Compare different styles on the same image
- **Business batch processor**: Professional workflows with preset styles
- **Personal photo processor**: Simplified interface for casual use

### 🛡️ **Secure & Reliable**
- Multiple secure API key management options
- Comprehensive error handling and logging
- Cross-platform support (Windows, macOS, Linux)

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/nanobanana.git
cd nanobanana

# Install dependencies
pip install -r requirements.txt
```

### Get Your API Key
1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Create an API key
4. Set it as environment variable:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

### Run the Application

**GUI Version (Recommended for beginners):**
```bash
python batch_nanobanana_gui.py
```

**CLI Version (For advanced users):**
```bash
python batch_nanobanana_cli.py \
  --input-dir ./photos \
  --output-dir ./results \
  --prompt "Transform this photo into a beautiful painting"
```

## 📖 Documentation

- 📋 **[Installation Guide](INSTALL_GUIDE.md)** - Detailed setup instructions
- 📚 **[Usage Guide](USAGE_GUIDE.md)** - Complete user manual with examples  
- ⚡ **[Quick Reference](QUICK_REFERENCE.md)** - Command cheat sheet
- 🚨 **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions
- 💻 **[CLI Documentation](README_CLI.md)** - Advanced command-line usage

## 🎯 Use Cases

### Personal Photography
```bash
# Transform vacation photos to artistic style
python batch_nanobanana_cli.py \
  -i vacation_photos \
  -o vacation_artistic \
  -p "Transform into a dreamy, artistic masterpiece"
```

### Business Marketing
```bash
# Professional product image enhancement
./workflows/business_batch.sh \
  product_photos \
  marketing_images \
  luxury
```

### Creative Experimentation
```bash
# Test multiple styles on one image
python workflows/creator_multistyle.py \
  photo.jpg \
  --preset artistic \
  --output style_comparisons
```

## 🛠️ Advanced Features

### Workflow Scripts
Located in the `workflows/` directory:

- **`personal_photos.py`** - GUI bridge for personal use
- **`business_batch.sh`** - Professional batch processing
- **`creator_multistyle.py`** - Multi-style comparison tool

### Supported Formats
- **Input**: PNG, JPG, JPEG, WebP, BMP, TIFF
- **Output**: PNG, JPG, JPEG, WebP

### API Key Management
Multiple secure options:
1. **Environment variables** (recommended)
2. **Configuration files** with proper permissions
3. **Interactive input** with hidden prompt
4. **Command-line arguments** (with security warnings)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute
- 🐛 Report bugs and suggest features
- 📝 Improve documentation
- 🔧 Submit code improvements
- 🌏 Help with translations

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini AI for the amazing image generation capabilities
- The Python community for excellent libraries
- All contributors who help improve NanoBanana

## ⭐ Star History

If you find NanoBanana useful, please consider giving it a star! ⭐

---

**Made with ❤️ for the AI art community**