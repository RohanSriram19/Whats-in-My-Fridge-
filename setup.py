#!/usr/bin/env python3
"""
Setup script for What's In My Fridge
"""

import subprocess
import sys
import os
import shutil

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_pip():
    """Check if pip is available"""
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      check=True, capture_output=True)
        print("✅ pip is available")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        return False

def create_virtual_environment():
    """Create virtual environment"""
    print("🔧 Creating virtual environment...")
    
    if os.path.exists(".venv"):
        print("   Virtual environment already exists")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def install_requirements():
    """Install required packages"""
    print("📦 Installing requirements...")
    
    python_path = os.path.join(".venv", "bin", "python")
    if not os.path.exists(python_path):
        print("❌ Virtual environment not found")
        return False
    
    try:
        subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        subprocess.run([python_path, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Requirements installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def download_spacy_model():
    """Download spaCy language model"""
    print("🧠 Downloading spaCy language model...")
    
    python_path = os.path.join(".venv", "bin", "python")
    
    try:
        subprocess.run([python_path, "-m", "spacy", "download", "en_core_web_sm"], 
                      check=True)
        print("✅ spaCy model downloaded")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to download spaCy model: {e}")
        print("   You can try downloading it manually later")
        return False

def setup_env_file():
    """Setup environment file"""
    print("⚙️  Setting up environment file...")
    
    if os.path.exists(".env"):
        print("   .env file already exists")
        return True
    
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("✅ .env file created from template")
        print("   ⚠️  Remember to add your Spoonacular API key to .env")
        return True
    else:
        print("❌ .env.example not found")
        return False

def run_test():
    """Run application test"""
    print("🧪 Running application test...")
    
    python_path = os.path.join(".venv", "bin", "python")
    
    try:
        result = subprocess.run([python_path, "test_app.py"], 
                              check=True, capture_output=True, text=True)
        print("✅ Application test passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Application test failed: {e}")
        print("   Check the error output above")
        return False

def main():
    """Main setup function"""
    print("🍳 What's In My Fridge - Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_pip():
        return False
    
    # Setup steps
    steps = [
        ("Create virtual environment", create_virtual_environment),
        ("Install requirements", install_requirements),
        ("Download spaCy model", download_spacy_model),
        ("Setup environment file", setup_env_file),
        ("Run application test", run_test)
    ]
    
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print()
    print("📝 Next steps:")
    print("   1. Get a free API key from: https://spoonacular.com/food-api")
    print("   2. Add your API key to the .env file")
    print("   3. Run: python start.py")
    print("   4. Open http://localhost:8501 in your browser")
    print()
    print("📖 For more help, check the README.md file")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
