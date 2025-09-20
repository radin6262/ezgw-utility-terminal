import os
import sys
import subprocess
import shutil
import time
import stat
from git import Repo, RemoteProgress
import terminal
# ---------------------- REPOS ----------------------
REPOS = {
    "1": ("Factory Worker Scripts", "https://github.com/IamAbolfazlHeydari/Factory-Worker-scripts.git")
}

DOWNLOAD_FOLDER = "repos"
REMOVE_FOLDER = "repos/Factory_Worker_Scripts"
# ---------------------- PROGRESS WITH SPEED ----------------------
class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.last_percent = 0
        self.start_time = time.time()
        self.last_time = self.start_time
        self.last_count = 0

    def update(self, op_code, cur_count, max_count=None, message=''):
        if max_count and max_count > 0:
            percent = int(cur_count / max_count * 100)
            now = time.time()
            elapsed = now - self.last_time

            if elapsed >= 0.5 or percent != self.last_percent:
                delta_count = cur_count - self.last_count
                speed = delta_count / elapsed if elapsed > 0 else 0
                remaining = max_count - cur_count
                eta = remaining / speed if speed > 0 else 0
                speed_mb = speed / 1024 / 1024
                eta_min, eta_sec = divmod(int(eta), 60)
                print(f"\rCloning... {percent}% - {speed_mb:.2f} MB/s - ETA {eta_min}m{eta_sec}s", end="", flush=True)
                self.last_percent = percent
                self.last_time = now
                self.last_count = cur_count
        elif message:
            print(f"\r{message}", end="", flush=True)

# ---------------------- INSTALL FUNCTION ----------------------
def install_repo():
    print("Current Issues: The Ezgw utility fails to get cloned")
    print("Soultion: will be pre copied")
    print("\nAvailable repositories to download:")
    for key, (name, url) in REPOS.items():
        print(f"{key}. {name} ({url})")
    
    choice = input("Select repo to install (1/2) or Q to cancel: ").strip().lower()
    if choice == "q":
        return
    if choice not in REPOS:
        print("Invalid selection!")
        return

    name, url = REPOS[choice]
    local_path = os.path.join(DOWNLOAD_FOLDER, name.replace(" ", "_"))
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    if os.path.exists(local_path):
        print(f"{name} already installed at {local_path}")
        return

    print(f"Installing {name}...")
    try:
        Repo.clone_from(url, local_path, progress=CloneProgress())
        print(f"\n{name} installed successfully at {local_path}")
    except Exception as e:
        print(f"\nFailed to install {name}: {e}")

# ---------------------- SEARCH ----------------------
def find_exe(repo_path):
    exe_files = []
    for root, _, files in os.walk(repo_path):
        for f in files:
            if f.endswith(".exe"):
                exe_files.append(os.path.join(root, f))
    return exe_files

def find_py(repo_path):
    py_files = []
    for root, _, files in os.walk(repo_path):
        for f in files:
            if f == "main.py":
                py_files.append(os.path.join(root, f))
    return py_files

# ---------------------- RUN ----------------------
def run_exe(path):
    # print(f"Running exe: {path}")
    # try:
    #     subprocess.run([path])
    # except Exception as e:
    #     print("Failed to run exe:", e)
    print("This Launch method is no longer usable. Please use the command (gui)")

def run_py(path):
    # print(f"Running python file: {path}")
    # try:
    #     subprocess.run([sys.executable, path])
    # except Exception as e:
    #     print("Failed to run python script:", e)
    print("this launch method is no longer usable. please use (gui)")

def launch_ezgw_gui(repo_path):
    main_py = os.path.join(repo_path, "main.py")
    if os.path.exists(main_py):
        print(f"Launching EZGW GUI: {main_py}")
        subprocess.run([sys.executable, main_py])
    else:
        print("No main.py found to launch GUI.")

# ---------------------- UNINSTALL ----------------------
def remove_readonly(func, path, excinfo):
    """Fix read-only deletion errors on Windows."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def uninstall_all():
    if os.path.exists(REMOVE_FOLDER):
        print("pre-installed repo's are not included")
        confirm = input(f"Are you sure you want to delete ALL repos in {REMOVE_FOLDER}? (y/n): ").strip().lower()
        if confirm == "y":
            try:
                shutil.rmtree(REMOVE_FOLDER, onerror=remove_readonly)
                print("All installed repositories have been deleted.")
            except Exception as e:
                print(f"Failed to uninstall: {e}")
        else:
            print("Uninstall cancelled.")
    else:
        print("No installed repositories to delete.")

# ---------------------- MAIN CONSOLE ----------------------
def main():
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

    while True:
        print("\n=== EZGW Console Launcher ===")
        print("Commands: install | run | gui | uninstall | exit | terminal")
        print("the terminal is the Text based ezgw utility")
        print("To run the gui edition you need to run command gui")
        print("--------------------------------------------------")
        
        command = input("> ").strip().lower()

        if command == "exit":
            print("Exiting console.")
            break
        elif command == "install":
            install_repo()
        elif command == "uninstall":
            uninstall_all()
        elif command == "gui":
            installed_repos = [
                os.path.join(DOWNLOAD_FOLDER, d) 
                for d in os.listdir(DOWNLOAD_FOLDER)
                if os.path.isdir(os.path.join(DOWNLOAD_FOLDER, d))
            ]
            if not installed_repos:
                print("No repos installed. Run 'install' first.")
                continue

            print("Installed repositories:")
            for i, repo_path in enumerate(installed_repos, 1):
                print(f"{i}. {repo_path}")

            choice = input("Select repo or Q to cancel: ").strip().lower()
            if choice == "q":
                continue
            if not (choice.isdigit() and 1 <= int(choice) <= len(installed_repos)):
                print("Invalid selection!")
                continue

            selected_repo = installed_repos[int(choice) - 1]
            launch_ezgw_gui(selected_repo)
        elif command == "terminal": terminal.main()
        elif command == "run": print("This method is no longer usable")
        else:
            print("Unknown command. Available commands: install | run | gui | uninstall | exit | terminal")

if __name__ == "__main__":
    main()
