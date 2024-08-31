import pandas as pd
import xtream

class XtreamModel:
    def __init__(self):
        self.df_category = pd.DataFrame()
        self.df_channels = pd.DataFrame()
        self.df_series = pd.DataFrame()
        self.url_channel = None
        self.expired = False
        self.option_category = xtream.liveType

    def authenticate(self, server, username, password):
        xtream.server = f"http://{server}"
        xtream.username = username
        xtream.password = password
        r = xtream.authenticate()
        return r.json()

    def get_categories(self):
        category_list = xtream.categories(self.option_category).json()
        self.df_category = pd.DataFrame(category_list)

    def get_streams_by_category(self, category_id):
        r = xtream.streamsByCategory(self.option_category, category_id)
        streams_by_category = r.json()
        self.df_channels = pd.DataFrame(streams_by_category)

    def get_series_info(self, series_id):
        series_seasons = xtream.seriesInfoByID(series_id).json()
        self.df_series = self.create_dataframe_series(series_seasons)

    @staticmethod
    def create_dataframe_series(series):
        rows = []
        for season in series["episodes"]:
            for episode in series["episodes"][season]:
                title = episode["title"]
                url = f"{xtream.server}/series/{xtream.username}/{xtream.password}/{episode['id']}.{episode['container_extension']}"
                rows.append((title, url))
        return pd.DataFrame(rows, columns=["title", "url"])