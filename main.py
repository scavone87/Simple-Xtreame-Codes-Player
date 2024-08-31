# main.py
import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication)

from XtreamModel import XtreamModel
from XtreamController import XtreamController
from XtreamView import XtreamView


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon("./logo.webp"))

    model = XtreamModel()
    controller = XtreamController(model)
    view = XtreamView(controller)

    controller.authentication_complete.connect(view.update_auth_status)
    controller.categories_loaded.connect(view.populate_category_table)
    controller.channels_loaded.connect(view.populate_channels_table)
    controller.series_loaded.connect(view.populate_series_table)
    controller.error_occurred.connect(view.show_error)

    view.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()