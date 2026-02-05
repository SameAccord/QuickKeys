import sys


def main():
    try:
        from src.app import QuickKeysApp

        app = QuickKeysApp()
        app.run()

    except ImportError as e:
        print(f"Import error: {e}")
        print("\nPlease install required dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)

    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
