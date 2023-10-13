from PyQt5.QtWidgets import *
from PyQt5.QtGui import *  # type: ignore
from typing import Tuple, Dict, List

from common.types import PatientInformation, ExamInformation, ScanQueueEntry
import common.logger as logger

log = logger.get_logger()

app = None
stacked_widget = None
registration_widget = None
examination_widget = None

patient_information = PatientInformation()
exam_information = ExamInformation()

scan_queue_list: List[ScanQueueEntry] = []
editor_sequence_instance = None
editor_active = False


def shutdown():
    """Shutdown the MRI4ALL console."""
    global app

    msg = QMessageBox()
    ret = msg.question(
        None,
        "Shutdown Console?",
        "Do you really want to shutdown the console?",
        msg.Yes | msg.No,
    )

    if ret == msg.Yes:
        registration_widget.clear_form()
        examination_widget.clear_examination_ui()
        if app is not None:
            app.quit()
            app = None


def register_patient():
    global exam_information
    exam_information.initialize()
    examination_widget.prepare_examination_ui()
    stacked_widget.setCurrentIndex(1)
    log.info(f"Registered patient {patient_information.get_full_name()}")
    log.info(f"Started exam {exam_information.id}")


def close_patient():
    msg = QMessageBox()
    ret = msg.question(
        None,
        "End Exam?",
        "Do you really want to close the active exam?",
        msg.Yes | msg.No,
    )

    if ret == msg.Yes:
        registration_widget.clear_form()
        stacked_widget.setCurrentIndex(0)
        examination_widget.clear_examination_ui()
        log.info(f"Closed patient {patient_information.get_full_name()}")
        patient_information.clear()
        exam_information.clear()


def get_screen_size() -> Tuple[int, int]:
    screen = QDesktopWidget().screenGeometry()
    return screen.width(), screen.height()


def update_scan_queue_list() -> bool:
    global scan_queue_list
    scan_queue_list = []

    return True
