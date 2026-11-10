"""Compatibility entry point for the project quality and security gate."""

try:
    from scripts.verify_project import main
except ModuleNotFoundError:  # Direct execution places scripts/ first on sys.path.
    from verify_project import main


if __name__ == "__main__":
    main()
