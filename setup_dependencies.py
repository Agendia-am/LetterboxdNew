#!/usr/bin/env python3
"""
Setup script to ensure all dependencies are properly installed and configured
"""
import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Running: {' '.join(cmd)}\n")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed")
        print(f"Error: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False

def check_python_version():
    """Check Python version"""
    print(f"\nPython version: {sys.version}")
    version_info = sys.version_info
    if version_info.major < 3 or (version_info.major == 3 and version_info.minor < 8):
        print("⚠ Warning: Python 3.8 or higher is recommended")
        return False
    print("✓ Python version is compatible")
    return True

def main():
    print("="*60)
    print("LETTERBOXD SCRAPER - DEPENDENCY SETUP")
    print("="*60)
    
    # Check Python version
    check_python_version()
    
    # Install Python packages
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Installing Python dependencies"
    ):
        print("\n⚠ Warning: Some pip packages may have failed to install")
    
    # Install Playwright browsers
    print("\n" + "="*60)
    print("Installing Playwright browsers (this may take a few minutes)")
    print("="*60)
    
    # Try to install all Playwright browsers
    if run_command(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        "Installing Playwright Chromium browser"
    ):
        print("\n✓ Playwright Chromium installed successfully")
    
    # Optional: Install other browsers
    print("\nOptional: Installing additional Playwright browsers...")
    run_command(
        [sys.executable, "-m", "playwright", "install", "firefox"],
        "Installing Playwright Firefox browser"
    )
    
    # Install system dependencies for Playwright (Linux/macOS)
    if sys.platform in ['linux', 'darwin']:
        print("\nInstalling Playwright system dependencies...")
        run_command(
            [sys.executable, "-m", "playwright", "install-deps"],
            "Installing Playwright system dependencies"
        )
    
    # Verify installations
    print("\n" + "="*60)
    print("VERIFYING INSTALLATIONS")
    print("="*60)
    
    # Check Selenium
    try:
        import selenium
        print(f"✓ Selenium version: {selenium.__version__}")
    except ImportError:
        print("✗ Selenium not installed")
    
    # Check Playwright
    try:
        import playwright
        print(f"✓ Playwright installed")
    except ImportError:
        print("✗ Playwright not installed")
    
    # Check webdriver-manager
    try:
        import webdriver_manager
        print(f"✓ webdriver-manager installed")
    except ImportError:
        print("✗ webdriver-manager not installed")
    
    # Check other dependencies
    deps = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('tqdm', 'tqdm'),
        ('pandas', 'pandas'),
        ('numpy', 'numpy'),
        ('plotly', 'plotly'),
        ('flask', 'flask')
    ]
    print("\nOther dependencies:")
    for dep_name, import_name in deps:
        try:
            __import__(import_name)
            print(f"  ✓ {dep_name}")
        except ImportError:
            print(f"  ✗ {dep_name}")
    
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nYou can now run the scraper with:")
    print("  python LetterboxdNew.py")
    print("\nOr test the enhanced features with:")
    print("  python test_enhanced_scraping.py")
    print("\n")

if __name__ == "__main__":
    main()
