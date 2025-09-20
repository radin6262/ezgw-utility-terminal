import sys
import os
import git
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QTextBrowser,
    QPushButton, QVBoxLayout, QWidget, QMessageBox, QHBoxLayout,
    QLineEdit, QLabel
)
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt

REPO_URL = "https://github.com/IamAbolfazlHeydari/Factory-Worker-scripts.git"
LOCAL_REPO = "repo"

# 🟢 PyInstaller support: adjust base directory
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.join(sys._MEIPASS, LOCAL_REPO)
else:
    BASE_DIR = LOCAL_REPO

SCRIPTS_FOLDER = os.path.join(BASE_DIR, "Main-Scripts")  # Correct folder name

def read_text_file(path):
    """Read a file handling UTF-8 or UTF-16 automatically"""
    for enc in ('utf-8', 'utf-16'):
        try:
            with open(path, 'r', encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    # Fallback: ignore errors
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

class EZGW(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EZGW Utility")
        self.setGeometry(200, 200, 1000, 600)

        self.selected_script = None

        # Prepare repo
        self.prepare_repo()

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search scripts...")
        self.search_bar.textChanged.connect(self.filter_scripts)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.clicked.connect(self.show_script)

        # Viewer (Markdown-capable)
        self.viewer = QTextBrowser()
        self.viewer.setOpenExternalLinks(True)
        self.viewer.setFont(QFont("Consolas", 11))

        # Download button
        self.download_btn = QPushButton("Save Script to downloads/")
        self.download_btn.clicked.connect(self.save_script)
        self.download_btn.setEnabled(False)

        # Refresh repo button
        self.refresh_btn = QPushButton("Update Repo")
        self.refresh_btn.clicked.connect(self.refresh_repo)
        self.explorer_btn = QPushButton("Open Main-Scripts Folder")
        self.explorer_btn.clicked.connect(self.show_main_scripts_folder)
        self.explorer_btn.setEnabled(True)

        # Layouts
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Preview / README"))
        right_layout.addWidget(self.viewer)
        right_layout.addWidget(self.download_btn)
        right_layout.addWidget(self.explorer_btn)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 5)

        left_layout.addWidget(QLabel("Scripts"))
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.sidebar)
        left_layout.addWidget(self.refresh_btn)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Apply CSS
        self.setStyleSheet("""
            QMainWindow { background-color: #2b2b2b; }
            QListWidget { background: #1e1e1e; color: #ffffff; border: 1px solid #444; }
            QListWidget::item:selected { background: #007acc; color: #ffffff; }
            QLineEdit { padding: 6px; border-radius: 4px; border: 1px solid #666; background: #252526; color: #ffffff; }
            QPushButton { background: #007acc; color: white; padding: 8px; border-radius: 6px; }
            QPushButton:hover { background: #005f99; }
            QTextBrowser { background: #1e1e1e; color: #dcdcdc; border: 1px solid #444; padding: 10px; }
            QLabel { color: #ffffff; font-weight: bold; }
        """)

        self.populate_scripts()
        self.load_readme()

    def prepare_repo(self):
        """Clone or pull the Git repo"""
        if not os.path.exists(BASE_DIR):
            git.Repo.clone_from(REPO_URL, LOCAL_REPO)
        else:
            repo = git.Repo(LOCAL_REPO)
            repo.remotes.origin.pull()

    def refresh_repo(self):
        """Pull latest changes and refresh scripts"""
        try:
            repo = git.Repo(LOCAL_REPO)
            repo.remotes.origin.pull()
            self.sidebar.clear()
            self.populate_scripts()
            self.load_readme()
            QMessageBox.information(self, "Refreshed", "Repo updated successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh repo:\n{e}")

    def populate_scripts(self):
        self.scripts = []
        self.sidebar.clear()
        # Add a "Guide" item at the top
        self.sidebar.addItem("Guide")
        if os.path.exists(SCRIPTS_FOLDER):
            for root, _, files in os.walk(SCRIPTS_FOLDER):
                for f in files:
                    if f.endswith(".cs"):
                        rel_path = os.path.relpath(os.path.join(root, f), LOCAL_REPO)
                        print("Found script:", rel_path)
                        self.scripts.append(rel_path)
            self.sidebar.addItems(self.scripts)

    def filter_scripts(self, text):
        for i in range(self.sidebar.count()):
            item = self.sidebar.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def show_main_scripts_folder(self):
        """Open the Main-Scripts folder in File Explorer"""
        folder_path = os.path.abspath(SCRIPTS_FOLDER)
        if os.path.exists(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Cannot open folder:\n{e}")
        else:
            QMessageBox.warning(self, "Not Found", "Main-Scripts folder does not exist.")

    def load_readme(self):
        """Load README.md as Markdown"""
        readme_path = os.path.join(LOCAL_REPO, "README.md")
        if os.path.exists(readme_path):
            text = read_text_file(readme_path)
            try:
                self.viewer.setMarkdown(text)
            except Exception:
                self.viewer.setPlainText(text)
        else:
            self.viewer.setPlainText("No README.md found in repo.")

    def show_script(self):
        """Display the selected script or README"""
        item = self.sidebar.currentItem()
        if not item:
            return

        if item.text() == "Guide":
            self.load_readme()
            self.selected_script = None
            self.download_btn.setEnabled(False)
        else:
            self.selected_script = item.text()
            script_path = os.path.join(LOCAL_REPO, self.selected_script)
            if os.path.exists(script_path):
                code = read_text_file(script_path)
                self.viewer.setPlainText(code)
                self.download_btn.setEnabled(True)
            else:
                self.viewer.setPlainText("File not found.")
                self.download_btn.setEnabled(False)

    def save_script(self):
        if not self.selected_script:
            return
        src_path = os.path.join(LOCAL_REPO, self.selected_script)
        os.makedirs("downloads", exist_ok=True)
        dst_path = os.path.join("downloads", os.path.basename(self.selected_script))
        try:
            with open(src_path, "r", encoding="utf-8", errors="ignore") as src, \
                 open(dst_path, "w", encoding="utf-8") as dst:
                dst.write(src.read())
            QMessageBox.information(self, "Saved", f"{self.selected_script} saved to downloads/")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EZGW()
    window.show()
    sys.exit(app.exec())
