from PySide2.QtWidgets import QApplication
from launch_panel.panel import LaunchPanelClass
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.lastWindowClosed.connect(app.quit)
    window = LaunchPanelClass()
    window.show_panel()
    sys.exit(app.exec_())
