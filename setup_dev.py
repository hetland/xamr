#!/usr/bin/env python3
"""
Development setup script for xamr
"""

import os
import sys
import subprocess


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Command: {e.cmd}")
        print(f"  Return code: {e.returncode}")
        print(f"  Output: {e.stdout}")
        print(f"  Error: {e.stderr}")
        return None


def main():
    """Main setup function"""
    print("Setting up xamr development environment...")
    
    # Check if we're in the right directory
    if not os.path.exists('xamr') or not os.path.exists('setup.py'):
        print("Error: This script must be run from the xamr project root directory")
        sys.exit(1)
    
    # Install in development mode
    result = run_command("pip install -e '.[dev]'", "Installing xamr in development mode")
    if result is None:
        print("Failed to install xamr. Please check your Python environment.")
        sys.exit(1)
    
    # Run tests to make sure everything is working
    print("\nRunning tests...")
    result = run_command("pytest -v", "Running unit tests")
    if result is None:
        print("Some tests failed. Please check the output above.")
    
    # Run linting
    print("\nRunning linting...")
    run_command("flake8 xamr tests --max-line-length=88", "Running flake8 linting")
    
    # Format code
    print("\nFormatting code...")
    run_command("black xamr tests", "Formatting code with black")
    
    print("\n" + "="*50)
    print("Development environment setup complete!")
    print("\nQuick commands:")
    print("  make test        - Run tests")
    print("  make lint        - Run linting")
    print("  make format      - Format code")
    print("  make build       - Build package")
    print("  make clean       - Clean build artifacts")
    print("\nFor more commands, run: make help")


if __name__ == '__main__':
    main()
