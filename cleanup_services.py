import os
try:
    path = r"c:\Users\Admin\OneDrive - Hanoi University of Science and Technology\Desktop\E16\E16\e16_app\services.py"
    if os.path.exists(path):
        os.remove(path)
        print(f"Successfully removed {path}")
    else:
        print(f"File {path} does not exist.")
except Exception as e:
    print(f"Error: {str(e)}")
