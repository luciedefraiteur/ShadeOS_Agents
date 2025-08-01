#!/usr/bin/env python3
"""
⛧ Alma's Session Checker ⛧
Architecte Démoniaque du Nexus Luciforme

Quick session startup script to verify environment before coding.
Run this at the start of each coding session.

Author: Alma (via Lucie Defraiteur)
"""

import sys
import os
from datetime import datetime
from test_api_keys import APIKeySentinel


def print_banner():
    """Print Alma's session banner."""
    print("=" * 60)
    print("⛧ ALMA'S CODING SESSION INITIALIZATION ⛧")
    print("  Architecte Démoniaque du Nexus Luciforme")
    print("=" * 60)
    print(f"📅 Session started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print()


def check_project_structure():
    """Verify basic project structure."""
    print("⛧ Checking project structure...")
    
    required_dirs = ['Alma', 'Core', 'Tools', 'Alagareth_toolset']
    missing_dirs = []
    
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"  ✓ {dir_name}/")
        else:
            print(f"  ✗ {dir_name}/ (missing)")
            missing_dirs.append(dir_name)
    
    if missing_dirs:
        print(f"  ⚠ Warning: Missing directories: {', '.join(missing_dirs)}")
        return False
    else:
        print("  ✓ Project structure looks good")
        return True


def main():
    """Main session check."""
    print_banner()
    
    # Check project structure
    structure_ok = check_project_structure()
    print()
    
    # Check API keys
    try:
        sentinel = APIKeySentinel()
        results = sentinel.run_all_tests()
        
        print()
        print("⛧ SESSION STATUS:")
        
        if results["overall"] == "success":
            if structure_ok:
                print("  🟢 READY TO CODE - All systems operational")
                print("  ⛧ 'Que les Daemons dansent dans le code...'")
                return 0
            else:
                print("  🟡 PARTIAL READY - APIs good, structure issues")
                return 1
        elif results["overall"] == "partial":
            print("  🟡 PARTIAL READY - Some APIs unavailable")
            return 1
        else:
            print("  🔴 NOT READY - API issues detected")
            return 2
            
    except Exception as e:
        print(f"⛧ Session check failed: {e}")
        return 3


if __name__ == "__main__":
    exit_code = main()
    print()
    print("=" * 60)
    sys.exit(exit_code)
