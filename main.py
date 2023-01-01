import logging
import multiprocessing
import platform
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QGuiApplication
from PyQt6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
                             QLineEdit, QMenu, QMenuBar, QMessageBox,
                             QProgressDialog, QPushButton, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

import xtream

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.table1 = QTableWidget()
        self.table2 = QTableWidget()
        self.table3 = QTableWidget()
        self.search_box = QLineEdit()
        self.search_box_channels = QLineEdit()
        self.progressDialog = None
        self.initUI()

    def initUI(self):
        logging.debug("INIT UI")
        # Inizializza la finestra e posizionala al centro
        self.setGeometry(100, 100, 900, 500)
        self.setWindowTitle("Simple Xtreame Codes Player")
        qr=self.frameGeometry()           
        cp= QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Crea il menu bar
        menu_bar = QMenuBar()

        # Crea il menu "Aiuto
        help_menu = QMenu("Aiuto")

        # Crea l'azione "Informazioni su"
        about_action = QAction("Informazioni su", self)
        about_action.setMenuRole(QAction.MenuRole.AboutRole)
        about_action.triggered.connect(self.onAboutTriggered)

        # Aggiungi l'azione "Informazioni su" al menu "Aiuto"
        help_menu.addAction(about_action)

        # Aggiungi il menu "Aiuto" alla barra dei menu
        menu_bar.addMenu(help_menu)

        # Aggiungi la barra dei menu alla finestra principale

        self.df_category = pd.DataFrame()
        self.option_category = xtream.liveType
        self.df_channels = pd.DataFrame()
        self.df_series = pd.DataFrame()
        self.url_channel = None

        # Crea la casella di input e il bottone
        self.input_box = QLineEdit(self)
        self.button = QPushButton("Clicca qui", self)
        # Associa la funzione al bottone
        self.button.clicked.connect(self.onButtonClicked)

        # Crea i tre label
        self.label1 = QLabel("")
        self.label2 = QLabel("")
        self.label3 = QLabel("")

        self.label1.setStyleSheet(
            "color: green; font-weight: bold; font-family: Helvetica; font-size: 14px;")
        self.label2.setStyleSheet(
            "color: red; font-weight: bold; font-family: Helvetica; font-size: 14px;")
        self.label3.setStyleSheet(
            "color: blue; font-weight: bold; font-family: Helvetica; font-size: 14px;")

        # Crea la label per le opzioni
        self.options_label = QLabel("Scegli un'opzione")

        self.combo_box = QComboBox()
        self.combo_box.currentIndexChanged.connect(self.onDropdownChanged)

        # Aggiungi le opzioni alla casella di selezione
        self.combo_box.addItem(xtream.liveType)
        self.combo_box.addItem(xtream.vodType)
        self.combo_box.addItem(xtream.seriesType)

        # Crea la casella di ricerca
        self.search_box = QLineEdit(self)
        self.search_box.textChanged.connect(self.onSearchChanged)

        self.search_box_channels = QLineEdit(self)
        self.search_box_channels.textChanged.connect(
            self.onSearchChannelChanged)

        # Crea i due dataframe
        self.table1 = QTableWidget(5, 1)
        self.table2 = QTableWidget(5, 1)
        self.table3 = QTableWidget(5, 1)

        self.table1.setEnabled(False)
        self.table2.setEnabled(False)
        self.table3.setEnabled(False)

        # Imposta la larghezza delle colonne delle tabelle 1 e 2 sulla larghezza della tabella
        self.table1.setColumnWidth(0, self.table1.width())
        self.table2.setColumnWidth(0, self.table2.width())
        self.table3.setColumnWidth(0, self.table3.width())

        self.table1.cellDoubleClicked.connect(self.onTableCellDoubleClicked)
        self.table2.cellDoubleClicked.connect(self.onTable2CellDoubleClicked)
        self.table3.cellDoubleClicked.connect(self.onTable3CellDoubleClicked)

        # Imposta il layout verticale per i widget
        vbox = QVBoxLayout()
        vbox.addWidget(self.input_box)
        vbox.addWidget(self.button)

        # Imposta il layout orizzontale per i label
        hbox = QHBoxLayout()
        hbox.addWidget(self.label1, stretch=1)
        hbox.setAlignment(self.label1, Qt.AlignmentFlag.AlignLeft)
        hbox.addWidget(self.label2, stretch=1)
        hbox.setAlignment(self.label2, Qt.AlignmentFlag.AlignCenter)
        hbox.addWidget(self.label3, stretch=1)
        hbox.setAlignment(self.label3, Qt.AlignmentFlag.AlignRight)
        vbox.addLayout(hbox)
        vbox.addWidget(self.options_label)
        vbox.addWidget(self.combo_box)
        hbox = QHBoxLayout()
        hbox.addWidget(self.search_box)
        hbox.addWidget(self.search_box_channels)
        vbox.addLayout(hbox)

        # Imposta il layout orizzontale per i dataframe
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.table1)
        self.hbox.addWidget(self.table2)
        vbox.addLayout(self.hbox)

        # Imposta il layout principale della finestra
        self.setLayout(vbox)

    def onAboutTriggered(self):
        message = """Questa è un'app PyQt6. È un player IPTV che sfrutta XTREAM CODES API per accedere alla lista dei canali. \nSfrutta VLC Media Player per la riproduzione (verifica di averlo installato correttamente). \nRicorda che Lo streaming di pay tv tramite IPTV è illegale. Questa applicazione implementa solo le API e non si assume alcuna resposabilità.
        \nRocco Scavone.
        """
        QMessageBox.about(self, "Informazioni sull'app", message)

    def onSearchChanged(self):
        # Ottieni il testo inserito nella casella di ricerca
        search_text = self.search_box.text().lower()
        # Scorri tutte le righe delle tabelle e nascondi quelle che non corrispondono alla ricerca
        for row in range(self.table1.rowCount()):
            # Prendi il primo elemento della riga (puoi scegliere qualsiasi altra colonna se vuoi cercare in un'altra colonna)
            item = self.table1.item(row, 0)
            if item is not None:
                text = item.text().lower()
                if search_text not in text:
                    self.table1.setRowHidden(row, True)
                else:
                    self.table1.setRowHidden(row, False)

    def onSearchChannelChanged(self):
        # Ottieni il testo inserito nella casella di ricerca
        search_text = self.search_box_channels.text().lower()
        # Scorri tutte le righe delle tabelle e nascondi quelle che non corrispondono alla ricerca
        for row in range(self.table2.rowCount()):
            # Prendi il primo elemento della riga (puoi scegliere qualsiasi altra colonna se vuoi cercare in un'altra colonna)
            item = self.table2.item(row, 0)
            if item is not None:
                text = item.text().lower()
                if search_text not in text:
                    self.table2.setRowHidden(row, True)
                else:
                    self.table2.setRowHidden(row, False)

    def onTableCellDoubleClicked(self, row, column):
        # Prendi l'i-esimo elemento del dataframe
        self.progress_dialog.show()  # Mostra la ProgressDialog
        selected_item = self.df_category.iloc[row]
        logging.debug("Categoria Selezionata: ", selected_item)
        category_id = selected_item['category_id']
        r = xtream.streamsByCategory(self.option_category, category_id)
        streams_by_category = r.json()
        self.df_channels = pd.DataFrame(streams_by_category)
        self.populateChannelsTable()
        self.progress_dialog.hide()

    def onTable3CellDoubleClicked(self, row):
        self.progress_dialog.show()
        selected_item = self.df_series.iloc[row]
        logging.debug("Episodio della serie selezionato: ", selected_item)
        self.url_channel = selected_item['url']
        self.playChannel()
        self.progress_dialog.hide()

    def onTable2CellDoubleClicked(self, row, column):
        # Prendi l'i-esimo elemento del dataframe
        self.progress_dialog.show()  # Mostra la ProgressDialog
        selected_item = self.df_channels.iloc[row]
        logging.debug("Canale selezionato: ", selected_item)
        stream_id = selected_item.get("stream_id")
        series_id = selected_item.get("series_id")
        container_extension = selected_item.get("container_extension")
        if container_extension is not None and series_id is None:
            # È un film
            self.url_channel = f"{xtream.server}:8080/movie/{xtream.username}/{xtream.password}/{stream_id}.{container_extension}"
            logging.debug("URL del film: ", self.url_channel)
            self.progress_dialog.hide()
            self.playChannel()

        if stream_id is not None and container_extension is None:
            # È un live
            self.url_channel = f"{xtream.server}:8080/{xtream.username}/{xtream.password}/{stream_id}"
            logging.debug("URL del canale live: ", self.url_channel)
            self.progress_dialog.hide()
            self.playChannel()
        elif series_id is not None:
            self.df_series = pd.DataFrame()
            seriesSeasons = xtream.seriesInfoByID(series_id).json()
            self.df_series = creaDataframeSeries(seriesSeasons)
            self.populateSeriesEpisodeTable()
            self.progress_dialog.hide()
        else:
            self.progress_dialog.hide()
            QMessageBox.warning(self, "Errore", "Qualcosa è andato storto")

    def playChannel(self):
        try:
            if platform.system() == 'Windows':
                logging.info('Il sistema operativo è Windows')
                subprocess.Popen(
                    ["C:/Program Files/VideoLAN/VLC/vlc.exe", self.url_channel])
            elif platform.system() == 'Darwin':
                logging.info('Il sistema operativo è Mac')
                subprocess.Popen(["open", "-a", "vlc", self.url_channel])
            else:
                logging.info('Il sistema operativo non è Windows o Mac')
        except FileNotFoundError:
            QMessageBox.warning(self, "Error", "VLC non è installato.")

    def clearContent(self):
        self.search_box.clear()
        self.search_box_channels.clear()
        self.table2.clear()
        self.table3.clear()

    def onDropdownChanged(self):
        self.clearContent()

        if xtream.username:
            # Ottieni l'indice del valore selezionato
            selected_index = self.combo_box.currentIndex()
            # Seleziona il dataframe da utilizzare in base all'indice selezionato
            if selected_index == 0:
                self.option_category = xtream.liveType
                self.table3.hide()
                self.hbox.removeWidget(self.table3)
            elif selected_index == 1:
                self.option_category = xtream.vodType
                self.table3.hide()
                self.hbox.removeWidget(self.table3)
            else:
                self.option_category = xtream.seriesType
                self.hbox.addWidget(self.table3)
                self.table3.show()
            logging.debug("Dropdown quando è stato inserito il link")
            self.progress_dialog.show()
            catgegory_list = xtream.categories(self.option_category).json()
            self.df_category = pd.DataFrame(catgegory_list)
            self.populateCategoryTable()
            self.progress_dialog.hide()

    def onButtonClicked(self):
        # Ottieni il testo inserito nella casella di input
        logging.debug("Bottone premuto")
        input_text = self.input_box.text()
        # Verifica se è un URL
        if not re.match(r"^https?://", input_text):
            # Mostra un pop-up di errore
            QMessageBox.warning(self, "Errore", "L'input non è un URL")
            return
        login_info = extract_login_info(input_text)
        if login_info[2]:
          server, username, password = login_info
          logging.debug(
              f"Contenuto del login info: {server} - {username} - {password}")
          # Scarica il contenuto dell'URL
          self.progress_dialog = QProgressDialog(
              "Caricamento in corso...", "Annulla", 0, 100, self)
          self.progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
          self.progress_dialog.setMinimumDuration(0)
          self.progress_dialog.show()  # Mostra la ProgressDialog
          logging.debug("Progress Dialog mostrata")
          data = xtream_auth(server, username, password)
          message = data["user_info"]["message"]
          status = data["user_info"]["status"]
          expire_date = data["user_info"]["exp_date"]
          self.label1.setText(message)
          self.label2.setText(status)
          self.label3.setText(expire_date)
          logging.debug(
              f"{message}, - Status: {status} - Data di scadenza: {expire_date}")
          self.option_category = self.combo_box.currentText()
          catgegory_list = xtream.categories(self.option_category).json()
          self.df_category = pd.DataFrame(catgegory_list)
          self.populateCategoryTable()
          self.progress_dialog.hide()
        else:
            QMessageBox.warning(
                self, "Errore", "Il testo inserito non è un URL valido")
            self.progress_dialog.hide()

    def populateCategoryTable(self):
        self.table1.setEnabled(True)
        # Imposta il numero di righe e colonne della tabella
        self.table1.setRowCount(self.df_category.shape[0])
        self.table1.setColumnCount(1)
        # Inserisci i dati del dataframe nella tabella
        for i in range(self.df_category.shape[0]):
            self.table1.setItem(
                i-1, 1, QTableWidgetItem(str(self.df_category.iloc[i, 1])))

    def populateChannelsTable(self):
        # Imposta il numero di righe e colonne della tabella
        self.table2.setEnabled(True)
        self.table2.setRowCount(self.df_channels.shape[0])
        self.table2.setColumnCount(1)
        # Inserisci i dati del dataframe nella tabella
        for i in range(self.df_channels.shape[0]):
            self.table2.setItem(
                i-1, 1, QTableWidgetItem(str(self.df_channels.iloc[i, 1])))

    def populateSeriesEpisodeTable(self):
        # Imposta il numero di righe e colonne della tabella
        self.table3.setEnabled(True)
        self.table3.setRowCount(self.df_series.shape[0])
        self.table3.setColumnCount(1)
        # Inserisci i dati del dataframe nella tabella
        for i in range(self.df_series.shape[0]):
            self.table3.setItem(
                i-1, 1, QTableWidgetItem(str(self.df_series.iloc[i, 0])))


def creaDataframeSeries(series):
    row = []
    with multiprocessing.Pool() as pool:
        for season in series["episodes"]:
            for episode in series["episodes"][season]:
                title = episode["title"]
                url = f"{xtream.server}/series/{xtream.username}/{xtream.password}/{episode['id']}.{episode['container_extension']}"
                row.append((title, url))
    df = pd.DataFrame(row, columns=["title", "url"])
    return df


def extract_login_info(url):
    # Analizziamo l'URL e estraiamo la stringa di query
    parsed_url = urllib.parse.urlparse(url)
    query_string = parsed_url.query

    # Analizziamo la stringa di query e estraiamo le informazioni di login
    query_params = urllib.parse.parse_qs(query_string)
    username = query_params.get("username", [None])[0]
    password = query_params.get("password", [None])[0]

    # Restituiamo le informazioni di login insieme al server
    return (parsed_url.hostname, username, password)


def get_category_type(xtream_type):
    category = xtream.categories(xtream_type)
    return pd.DataFrame(category.json())


def xtream_auth(server_name, username, password):
    xtream.server = f"http://{server_name}"
    xtream.username = username
    xtream.password = password
    r = xtream.authenticate()
    return r.json()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
