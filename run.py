#!/usr/bin/env python3
"""
Asteroid Impact Tool - Main Runner
Run this file to start the application
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main import main

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting Asteroid Impact Tool...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Please check your inputs and try again.")
