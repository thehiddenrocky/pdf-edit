# Purging Sensitive Files from Git History

If you accidentally commit sensitive files (like passwords, API keys, personal PDFs, or signature images) to a Git repository, simply deleting them and committing the deletion is not enough. The files will still exist in the Git history and can be accessed by looking at old commits.

To permanently erase files from all previous commits across the entire history of the repository, the recommended tool is `git-filter-repo`.

## Prerequisites

You need to install `git-filter-repo`. On macOS, you can install it using Homebrew:

```bash
brew install git-filter-repo
```

## The Purging Process

### 1. Ensure a Clean Working Tree
Before rewriting history, make sure you don't have any uncommitted changes. Commit or stash them, and ensure your `.gitignore` is updated to prevent these files from being tracked again.

```bash
git status
```

### 2. Run `git filter-repo`
Run the tool and specify the paths of the files or directories you want to completely erase from the history. Use the `--invert-paths` flag to say "keep everything *except* these paths".

```bash
git filter-repo --invert-paths \
  --path path/to/sensitive_file.jpg \
  --path folder_with_secrets \
  --path .DS_Store \
  --force
```
*Note: As a safety precaution to prevent accidental pushes of rewritten history, `git filter-repo` automatically removes your configured remotes (like `origin`).*

### 3. Re-add Your Remote
Because the remote was removed in the previous step, you need to add it back. 

```bash
# Check current remotes (will likely be empty)
git remote -v

# Add the remote back (replace with your actual repository URL)
git remote add origin https://github.com/yourusername/your-repo.git
```

### 4. Force Push to the Remote
To update the history on your remote server (e.g., GitHub, GitLab) and delete the files there, you must force push the newly rewritten history.

```bash
git push origin main --force
```
*(If your primary branch is `master` or something else, replace `main` accordingly).*

### 5. Inform Collaborators
Because the Git history has been fundamentally rewritten, anyone else working on this repository will encounter errors if they try to `git pull`. They will need to either:
1. Delete their local repository and re-clone from the remote.
2. Fetch the latest and perform a hard reset to the remote branch (`git fetch origin && git reset --hard origin/main`).
