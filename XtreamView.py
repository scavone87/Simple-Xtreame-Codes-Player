# XtreamView.py
from datetime import datetime
import re
import urllib.parse
import platform
import subprocess

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QGuiApplication, QColor, QPalette
from PyQt6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QMessageBox,
                             QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget, QStyleFactory)
import xtream

class XtreamView(QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Xtream Codes Player")
        self.setGeometry(100, 100, 1000, 600)
        self.center_on_screen()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Input and authentication
        input_layout = QHBoxLayout()
        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Enter Xtream Codes URL")
        self.auth_button = QPushButton("Authenticate")
        self.auth_button.clicked.connect(self.on_auth_button_clicked)
        input_layout.addWidget(self.input_box)
        input_layout.addWidget(self.auth_button)
        main_layout.addLayout(input_layout)

        # Status labels
        status_layout = QHBoxLayout()
        self.status_label = QLabel()
        self.expiry_label = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.expiry_label)
        main_layout.addLayout(status_layout)

        # Category selection
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.addItems([xtream.liveType, xtream.vodType, xtream.seriesType])
        self.category_combo.currentIndexChanged.connect(self.on_category_changed)
        category_layout.addWidget(QLabel("Category:"))
        category_layout.addWidget(self.category_combo)
        main_layout.addLayout(category_layout)

        # Search boxes
        search_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search categories")
        self.search_box.textChanged.connect(self.on_search_changed)
        self.search_box_channels = QLineEdit()
        self.search_box_channels.setPlaceholderText("Search channels")
        self.search_box_channels.textChanged.connect(self.on_search_channels_changed)
        search_layout.addWidget(self.search_box)
        search_layout.addWidget(self.search_box_channels)
        main_layout.addLayout(search_layout)

        # Tables
        tables_layout = QHBoxLayout()
        self.table_category = QTableWidget()
        self.table_channels = QTableWidget()
        self.table_series = QTableWidget()
        self.table_category.cellDoubleClicked.connect(self.on_category_selected)
        self.table_channels.cellDoubleClicked.connect(self.on_channel_selected)
        self.table_series.cellDoubleClicked.connect(self.on_episode_selected)
        tables_layout.addWidget(self.table_category)
        tables_layout.addWidget(self.table_channels)
        tables_layout.addWidget(self.table_series)
        main_layout.addLayout(tables_layout)

        self.create_menu_bar()
        self.setup_style()

    def center_on_screen(self):
        frame_geometry = self.frameGeometry()
        screen_center = QGuiApplication.primaryScreen().availableGeometry().center()
        frame_geometry.moveCenter(screen_center)
        self.move(frame_geometry.topLeft())

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        help_menu = menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def setup_style(self):
            qapp = QApplication.instance()
            qapp.setStyle(QStyleFactory.create("Fusion"))
            
            # Imposta una palette di colori moderna e accattivante
            palette = QPalette()
            palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
            qapp.setPalette(palette)

            # Imposta lo stile dei widget
            qapp.setStyleSheet("""
                QMainWindow {
                    background-color: #353535;
                }
                QLabel {
                    font-size: 14px;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #2a82da;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 3px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #3a92ea;
                }
                QLineEdit, QComboBox {
                    padding: 5px;
                    border: 1px solid #555555;
                    border-radius: 3px;
                    background-color: #252525;
                    color: white;
                    font-size: 14px;
                }
                QTableWidget {
                    border: 1px solid #555555;
                    background-color: #252525;
                    color: white;
                    gridline-color: #555555;
                }
                QTableWidget::item:selected {
                    background-color: #2a82da;
                }
                QHeaderView::section {
                    background-color: #353535;
                    color: white;
                    padding: 5px;
                    border: 1px solid #555555;
                }
            """)

    def show_about_dialog(self):
        QMessageBox.about(self, "About Xtream Codes Player",
                          "This is an IPTV player using Xtream Codes API.\n"
                          "Remember that streaming pay TV via IPTV might be illegal in your country.\n"
                          "This application only implements the API and assumes no responsibility.\n\n"
                          "Created by Rocco Scavone")

    def on_auth_button_clicked(self):
        url = self.input_box.text()
        if not re.match(r"^https?://", url):
            self.show_error("Invalid URL", "The input is not a valid URL")
            return

        server, username, password = self.extract_login_info(url)
        if not all([server, username, password]):
            self.show_error("Invalid URL", "Unable to extract login information from the URL")
            return

        self.controller.authenticate(server, username, password)

    def on_category_changed(self):
        self.controller.model.option_category = self.category_combo.currentText()
        self.controller.start()

    def on_search_changed(self):
        self.filter_table(self.table_category, self.search_box.text())

    def on_search_channels_changed(self):
        self.filter_table(self.table_channels, self.search_box_channels.text())

    def on_category_selected(self, row, column):
        category_id = self.controller.model.df_category.iloc[row]['category_id']
        self.controller.load_channels(category_id)

    def on_channel_selected(self, row, column):
        selected_item = self.controller.model.df_channels.iloc[row]
        stream_id = selected_item.get("stream_id")
        series_id = selected_item.get("series_id")
        container_extension = selected_item.get("container_extension")
        stream_type = selected_item.get("stream_type")

        if stream_type == "movie":
            url = f"{xtream.server}:8080/movie/{xtream.username}/{xtream.password}/{stream_id}.{container_extension}"
            self.play_channel(url)
        elif stream_type == "live":
            url = f"{xtream.server}:8080/{xtream.username}/{xtream.password}/{stream_id}"
            self.play_channel(url)
        elif series_id is not None:
            self.controller.load_series(series_id)
        else:
            self.show_error("Error", "Unable to play this content")

    def on_episode_selected(self, row, column):
        url = self.controller.model.df_series.iloc[row]['url']
        self.play_channel(url)

    def play_channel(self, url):
        try:
            if platform.system() == 'Windows':
                subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe", url])
            elif platform.system() == 'Darwin':
                subprocess.Popen(["open", "-a", "vlc", url])
            else:
                subprocess.Popen(["vlc", url])
        except FileNotFoundError:
            self.show_error("Error", "VLC is not installed or not found in the default location")

    def update_auth_status(self, data):
        user_info = data.get("user_info", {})
        message = user_info.get("message", "Unknown status")
        status = user_info.get("status", "Unknown")
        exp_date = user_info.get("exp_date")

        self.status_label.setText(f"Status: {status} - {message}")
        if exp_date:
            expiry_date = datetime.fromtimestamp(int(exp_date)).strftime("%d-%m-%Y %H:%M:%S")
            self.expiry_label.setText(f"Expiry: {expiry_date}")
        else:
            self.expiry_label.setText("Expiry: Unknown")

        if status == "Expired":
            self.controller.model.expired = True
            self.show_error("Account Expired", "Your account has expired.")
        else:
            self.controller.start()

    def populate_category_table(self):
        self.populate_table(self.table_category, self.controller.model.df_category, ['category_name'])

    def populate_channels_table(self):
        self.populate_table(self.table_channels, self.controller.model.df_channels, ['name'])

    def populate_series_table(self):
        self.populate_table(self.table_series, self.controller.model.df_series, ['title'])

    def populate_table(self, table, df, columns):
        table.setRowCount(df.shape[0])
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        for i, row in df.iterrows():
            for j, col in enumerate(columns):
                item = QTableWidgetItem(str(row[col]))
                table.setItem(i, j, item)

        table.resizeColumnsToContents()

    def filter_table(self, table, search_text):
        search_text = search_text.lower()
        for row in range(table.rowCount()):
            item = table.item(row, 0)
            if item:
                table.setRowHidden(row, search_text not in item.text().lower())

    def show_error(self, title, message):
        QMessageBox.warning(self, title, message)

    @staticmethod
    def extract_login_info(url):
        parsed_url = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        username = query_params.get("username", [None])[0]
        password = query_params.get("password", [None])[0]
        return parsed_url.hostname, username, password