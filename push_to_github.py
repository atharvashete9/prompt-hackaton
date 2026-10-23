import sys
import os
from dulwich.repo import Repo
from dulwich import porcelain

repo_path = r"c:\Users\thevillenskull\promt hackaton"
remote_url = "https://github.com/atharvashete9/prompt-hackaton.git"

token = os.getenv("GITHUB_TOKEN", "").strip()
if len(sys.argv) > 1:
    token = sys.argv[1].strip()

target_url = remote_url
if token:
    # Authenticated URL
    target_url = f"https://{token}@github.com/atharvashete9/prompt-hackaton.git"
    print("Using provided GitHub Token for authentication...")
else:
    print("No GitHub Token provided. Attempting push to public endpoint...")

try:
    repo = Repo(repo_path)
    # Configure remote
    config = repo.get_config()
    config.set((b'remote', b'origin'), b'url', remote_url.encode('utf-8'))
    config.write_to_path()
    
    # Push to main / master
    print(f"Pushing to {remote_url}...")
    porcelain.push(repo, target_url, "refs/heads/main:refs/heads/main")
    print("SUCCESS: Pushed to GitHub repository!")
except Exception as e:
    print(f"Push response: {e}")
