import os
import re

template_dir = r"c:\Users\Admin\OneDrive - Hanoi University of Science and Technology\Desktop\E16\E16\templates"

for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find forms with method="post" that don't have csrf_token yet
            new_content = re.sub(
                r'(<form[^>]*method=["\']post["\'][^>]*>)',
                r'\1\n    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">',
                content,
                flags=re.IGNORECASE
            )
            
            if new_content != content:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Updated {file}")
