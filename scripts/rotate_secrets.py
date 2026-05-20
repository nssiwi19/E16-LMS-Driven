import secrets
import os
import re

def generate_secret(length=32):
    return secrets.token_hex(length)

def rotate_env_file(env_path='.env'):
    if not os.path.exists(env_path):
        print(f"Error: {env_path} not found.")
        return

    with open(env_path, 'r') as f:
        content = f.read()

    # Generate new keys
    new_secret_key = generate_secret(32)
    new_seed_pw = generate_secret(16)

    # Replace keys using regex
    content = re.sub(r'SECRET_KEY=.*', f'SECRET_KEY={new_secret_key}', content)
    content = re.sub(r'E16_SEED_PASSWORD=.*', f'E16_SEED_PASSWORD={new_seed_pw}', content)

    with open(env_path, 'w') as f:
        f.write(content)
    
    print(f"Successfully rotated local secrets in {env_path}")
    print("NOTE: You MUST rotate GOOGLE_CLIENT_SECRET and SUPABASE_KEY in their respective dashboards manually.")

if __name__ == "__main__":
    rotate_env_file()
