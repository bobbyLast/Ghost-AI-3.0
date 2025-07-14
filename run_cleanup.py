#!/usr/bin/env python3
"""
Standalone Cleanup Script
Runs Ghost AI auto cleanup independently.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Running Ghost AI auto cleanup...")
    try:
        from system.auto_cleanup import cleanup_main
        cleanup_main()
        print("Cleanup completed.")
    except Exception as e:
        print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    main() 