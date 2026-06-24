#!/usr/bin/env python3
import sys
from app import main

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
