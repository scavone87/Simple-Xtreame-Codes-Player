from PyQt6.QtCore import QThread, pyqtSignal

class XtreamController(QThread):
    authentication_complete = pyqtSignal(dict)
    categories_loaded = pyqtSignal()
    channels_loaded = pyqtSignal()
    series_loaded = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, model):
        super().__init__()
        self.model = model
        self.timeout = 10

    def run(self):
        try:
            self.model.get_categories()
            self.categories_loaded.emit()
        except requests.Timeout:
            self.error_occurred.emit("Timeout: La richiesta ha impiegato troppo tempo.")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def authenticate(self, server, username, password):
        try:
            data = self.model.authenticate(server, username, password)
            self.authentication_complete.emit(data)
        except requests.Timeout:
            self.error_occurred.emit("Timeout: L'autenticazione ha impiegato troppo tempo.")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def load_channels(self, category_id):
        try:
            self.model.get_streams_by_category(category_id)
            self.channels_loaded.emit()
        except requests.Timeout:
            self.error_occurred.emit("Timeout: Il caricamento dei canali ha impiegato troppo tempo.")
        except Exception as e:
            self.error_occurred.emit(str(e))

    def load_series(self, series_id):
        try:
            self.model.get_series_info(series_id)
            self.series_loaded.emit()
        except requests.Timeout:
            self.error_occurred.emit("Timeout: Il caricamento della serie ha impiegato troppo tempo.")
        except Exception as e:
            self.error_occurred.emit(str(e))