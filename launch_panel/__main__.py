"""
Entry point for app
"""
from PySide2.QtWidgets import QApplication
from launch_panel.panel import LaunchPanelClass
import sys

if __name__ == "__main__":
    # create Qt Aplication
    app = QApplication(sys.argv)
    # exit app when all windows is closed
    app.lastWindowClosed.connect(app.quit)
    # create panel instance
    window = LaunchPanelClass()
    # execute event loop
    sys.exit(app.exec_())
