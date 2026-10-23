import os
import sys
from dulwich.repo import Repo
from dulwich.porcelain import init, add, commit, status

workspace = r"c:\Users\thevillenskull\promt hackaton"

# 1. Create .gitignore if not present
gitignore_path = os.path.join(workspace, ".gitignore")
gitignore_content = """__pycache__/
*.pyc
*.pyo
.pytest_cache/
.coverage
.env
.DS_Store
Thumbs.db
"""
if not os.path.exists(gitignore_path):
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("Created .gitignore")

# 2. Initialize repo if not initialized
git_dir = os.path.join(workspace, ".git")
if not os.path.exists(git_dir):
    repo = init(workspace)
    print("Initialized git repository in", workspace)
else:
    repo = Repo(workspace)
    print("Existing git repository found")

# 3. Add all files
add(repo, paths=["."])
print("Added all files to staging")

# 4. Commit
try:
    commit_sha = commit(
        repo,
        message=b"Initial commit: AegisOps AI - Autonomous Critical Resilience & Security Intelligence Platform",
        committer=b"atharvashete9 <atharvashete9@users.noreply.github.com>",
        author=b"atharvashete9 <atharvashete9@users.noreply.github.com>"
    )
    print(f"Committed successfully! Commit SHA: {commit_sha.decode('utf-8')}")
except Exception as e:
    print(f"Commit note: {e}")

# Check status
st = status(repo)
print(f"Staged: {len(st.staged['add']) if 'add' in st.staged else 0}")
print("Git setup complete!")
