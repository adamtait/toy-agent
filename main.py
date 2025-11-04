import sys
from agent import main

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py <task>")
        sys.exit(1)
    task = " ".join(sys.argv[1:])
    main(task)
