#!/usr/bin/env python3
"""
Entry point for the Jewelry Auction System API
This file provides easy access to run the application from the root directory.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import and run the main application
from src.run import main

if __name__ == '__main__':
    main()
