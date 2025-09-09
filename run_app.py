#!/usr/bin/env python3
"""
Simple runner script that checks dependencies and runs the GUI app
"""

def check_dependencies():
    """Check if required packages are available"""
    missing_packages = []
    
    try:
        import tkinter
    except ImportError:
        missing_packages.append("tkinter (usually comes with Python)")
    
    try:
        from google import genai
    except ImportError:
        missing_packages.append("google-genai")
    
    try:
        from PIL import Image
    except ImportError:
        missing_packages.append("Pillow")
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install with: pip install google-genai Pillow")
        return False
    
    print("✅ All dependencies available!")
    return True

def main():
    print("🍌 Batch NanoBanana Image Generator")
    print("=" * 40)
    
    if not check_dependencies():
        return
    
    print("🚀 Starting GUI application...")
    
    try:
        from batch_nanobanana_gui import main as gui_main
        gui_main()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("💡 Try running directly: python batch_nanobanana_gui.py")

if __name__ == "__main__":
    main()