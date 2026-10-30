#!/usr/bin/env python3
"""
Helper script to start debug server on port 443 with automatic sudo elevation
"""
import os
import sys
import subprocess

def main():
    if os.getuid() != 0:
        print("Requesting sudo to run on port 443...")
        # Re-run self with sudo
        os.execvp("sudo", ["sudo", sys.executable, __file__])

    # If we get here, we have root
    print("Running with root privileges")

    # Import and run the actual server
    sys.path.insert(0, os.path.dirname(__file__))
    from debug_server_fixed import main as server_main

    server_main()

if __name__ == '__main__':
    main()
