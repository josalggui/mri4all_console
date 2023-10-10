from PyQt5 import uic
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # type: ignore

from common.version import mri4all_version
import common.runtime as rt


def show_about():
    about_window = AboutWindow()
    about_window.exec_()


class AboutWindow(QDialog):
    def __init__(self):
        super(AboutWindow, self).__init__()
        uic.loadUi(f"{rt.get_console_path()}/services/ui/forms/about.ui", self)
        self.setWindowTitle("About MRI4ALL")
        self.versionLabel.setText(
            f'<html><head/><body><p><span style="font-weight:600;">MRI4ALL Console</span></p><p>The Open-Source MRI Software</p><p>Version {mri4all_version.get_version_string()}</p></body></html>'
        )
        self.closeButton.clicked.connect(self.close_clicked)

    def close_clicked(self):
        self.close()
