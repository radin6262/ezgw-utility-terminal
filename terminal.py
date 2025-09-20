import os
import sys
import git
import shutil

REPO_URL = "https://github.com/IamAbolfazlHeydari/Factory-Worker-scripts.git"
LOCAL_REPO = "repo"
SCRIPTS_FOLDER = os.path.join(LOCAL_REPO, "Main-Scripts")

def read_text_file(path):
    for enc in ('utf-8', 'utf-16'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

def prepare_repo():
    if not os.path.exists(LOCAL_REPO):
        print("Cloning repo...")
        git.Repo.clone_from(REPO_URL, LOCAL_REPO)
    else:
        print("Repo exists. Pulling latest changes...")
        repo = git.Repo(LOCAL_REPO)
        repo.remotes.origin.pull()
        print("Repo updated.")

def list_scripts():
    scripts = []
    if os.path.exists(SCRIPTS_FOLDER):
        for root, _, files in os.walk(SCRIPTS_FOLDER):
            for f in files:
                if f.endswith(".cs"):
                    rel_path = os.path.relpath(os.path.join(root, f), LOCAL_REPO)
                    scripts.append(rel_path)
    return scripts

def show_readme():
    readme_path = os.path.join(LOCAL_REPO, "README.md")
    if os.path.exists(readme_path):
        print("\n=== README ===\n")
        print(read_text_file(readme_path))
        print("\n=== END README ===\n")
    else:
        print("No README.md found.")

def view_script(script_path):
    full_path = os.path.join(LOCAL_REPO, script_path)
    if os.path.exists(full_path):
        print("\n--- Script Start ---\n")
        print(read_text_file(full_path))
        print("\n--- Script End ---\n")
    else:
        print("File not found.")

def save_script(script_path):
    full_path = os.path.join(LOCAL_REPO, script_path)
    if os.path.exists(full_path):
        os.makedirs("downloads", exist_ok=True)
        dst_path = os.path.join("downloads", os.path.basename(script_path))
        shutil.copy(full_path, dst_path)
        print(f"Saved {script_path} to downloads/")
    else:
        print("File not found.")

def main():
    prepare_repo()
    while True:
        print("\n=== EZGW Terminal Launcher ===")
        print("Commands: list | view | save | readme | update | exit")
        cmd = input("> ").strip().lower()

        if cmd == "exit":
            break
        elif cmd == "update":
            prepare_repo()
        elif cmd == "readme":
            show_readme()
        elif cmd == "list":
            scripts = list_scripts()
            if not scripts:
                print("No scripts found.")
            else:
                for i, s in enumerate(scripts, 1):
                    print(f"{i}. {s}")
        elif cmd in ("view", "save"):
            scripts = list_scripts()
            if not scripts:
                print("No scripts found.")
                continue
            for i, s in enumerate(scripts, 1):
                print(f"{i}. {s}")
            choice = input("Select script number: ").strip()
            if not choice.isdigit() or not 1 <= int(choice) <= len(scripts):
                print("Invalid selection.")
                continue
            script_path = scripts[int(choice)-1]
            if cmd == "view":
                view_script(script_path)
            else:
                save_script(script_path)
        else:
            print("Unknown command.")

