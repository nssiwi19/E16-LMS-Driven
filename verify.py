import sys
from e16_app import create_app

def verify():
    print("Verifying E16 LMS Application Load...")
    try:
        app = create_app()
        with app.app_context():
            # Check if blueprints are registered
            print(f"Blueprints registered: {list(app.blueprints.keys())}")
            if len(app.blueprints) < 5:
                print("Error: Not all blueprints were registered.")
                sys.exit(1)
        print("Application loaded successfully!")
    except Exception as e:
        print(f"Failed to load application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    verify()
