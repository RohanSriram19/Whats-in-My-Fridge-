#!/usr/bin/env python3
"""
Startup script for What's In My Fridge application
"""

import subprocess
import sys
import os

def start_app():
    """Start the Streamlit application"""
    
    print("🍳 Starting What's In My Fridge...")
    print("=" * 50)
    
    # Change to the app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    # Get the Python executable path
    python_path = os.path.join(app_dir, ".venv", "bin", "python")
    
    if not os.path.exists(python_path):
        print("❌ Virtual environment not found!")
        print("   Please run the setup first.")
        return
    
    print("✅ Starting Streamlit server...")
    print("🌐 The app will open in your browser at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start Streamlit
        cmd = [python_path, "-m", "streamlit", "run", "app.py", "--server.headless", "true"]
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    start_app()
