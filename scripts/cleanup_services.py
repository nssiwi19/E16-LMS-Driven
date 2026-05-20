import os
try:
    path = os.path.join(os.path.dirname(__file__), "..", "e16_app", "services.py")
    if os.path.exists(path):
        os.remove(path)
        print(f"Successfully removed {path}")
    else:
        print(f"File {path} does not exist.")
except Exception as e:
    print(f"Error: {str(e)}")
