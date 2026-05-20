import os
import re

template_dir = os.path.join(os.path.dirname(__file__), "..", "templates")

for root, dirs, files in os.walk(template_dir):
    for file in files:
        if file.endswith(".html"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Find forms with method="post"
            # Idempotent: only inject if csrf_token() is NOT already there
            if 'method="post"' in content.lower() and 'csrf_token()' not in content:
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
