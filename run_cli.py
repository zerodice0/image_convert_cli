#!/usr/bin/env python3
"""
Simple runner script for CLI version that checks dependencies
"""

import sys
import os


def check_dependencies():
    """Check if required packages are available"""
    missing_packages = []
    
    try:
        from google import genai
    except ImportError:
        missing_packages.append("google-genai")
    
    try:
        from PIL import Image
    except ImportError:
        missing_packages.append("Pillow")
    
    try:
        from rich.console import Console
    except ImportError:
        missing_packages.append("rich")
    
    try:
        import tqdm
    except ImportError:
        missing_packages.append("tqdm")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install with: pip install -r requirements_cli.txt")
        print("    or: pip install google-genai Pillow rich tqdm python-dotenv")
        return False
    
    print("✅ All dependencies available!")
    return True


def check_python_version():
    """Check if Python version is adequate"""
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version}")
    return True


def main():
    print("🍌 Batch NanoBanana Image Generator - CLI")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print("🚀 Starting CLI application...")
    print("💡 For help: python batch_nanobanana_cli.py --help\n")
    
    # Import and run CLI
    try:
        from batch_nanobanana_cli import main as cli_main
        
        # Pass through all command line arguments
        sys.argv[0] = "batch_nanobanana_cli.py"  # Update script name for help text
        cli_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try running directly: python batch_nanobanana_cli.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()