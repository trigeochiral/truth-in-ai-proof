"""CLI entry point: proofline-verify"""
import sys
from .verify import main as verify_main

def main():
    return verify_main() or 0

if __name__ == "__main__":
    sys.exit(main())
