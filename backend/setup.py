import subprocess
import sys
import os

def install_requirements():
    """Install requirements with proper Python 3.12 compatibility"""
    
    # First, ensure setuptools is installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    
    # Install requirements
    requirements = [
        "flask==2.3.3",
        "flask-cors==4.0.0",
        "numpy==1.26.4",
        "scikit-learn==1.4.0",
        "networkx==3.2.1",
        "svgwrite==1.4.3",
        "Pillow==10.2.0",
        "reportlab==4.0.9",
        "matplotlib==3.8.2",
        "pandas==2.2.0",
        "scipy==1.12.0",
        "pyyaml==6.0.1",
        "cairosvg==2.7.1",
        "gunicorn==21.2.0"
    ]
    
    for package in requirements:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
    print("\n✅ All packages installed successfully!")

if __name__ == "__main__":
    install_requirements()
