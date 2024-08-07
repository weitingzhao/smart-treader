import logging
import os
import re
import sys
import json
from zoneinfo import ZoneInfo

import pandas as pd
from pathlib import Path

pip = "pip" if "win" in sys.platform else "pip3"
try:
    import tzlocal
except ModuleNotFoundError:
    exit(f"tzlocal package is required\nRun: {pip} install tzlocal")


class Config:
    """A class to store all configuration

    # Attributes for polt.py
                            plugin configuration.                       (Default {})
    PLOT_DAYS:              Number of days to be plotted with trading_pattern_chart.py.  (Default 160.)
    PLOT_WEEKS:             Number of weeks to be plotted with trading_pattern_chart.py. (Default 140.)
    PLOT_M_RS_LEN_D:        Length used to calculate Mansfield
                            Relative Strength on daily TF.              (Default 60.)
    PLOT_M_RS_LEN_W:        Length used to calculate Mansfield
                            Relative Strength on Weekly TF.             (Default 52.)
    PLOT_RS_INDEX:          Index used to calculate Dorsey Relative
                            strength and Mansfield relative strength.   (Default 'S&P 500')
    MAGNET_MODE:            When True, lines snap to closest High,
                            Low, Close or Open. If False, mouse
                            click coordinates on chart are used.        (Default True)

    PLOT_CHART_STYLE:       Chart theme                                 (Default 'tradingview')
    PLOT_CHART_TYPE:        Chart type. One of: ohlc, candle, line      (Default 'candle')

    PLOT_RS_COLOR:          Dorsey RS line color                        (Default 'darkblue')
    PLOT_M_RS_COLOR:        Mansfield RS line color                     (Default 'darkgreen')
    PLOT_DLV_L1_COLOR:      Delivery mode L1 bar color                  (Default 'red')
    PLOT_DLV_L2_COLOR:      Delivery mode L2 bar color                  (Default 'darkorange')
    PLOT_DLV_L3_COLOR:      Delivery mode L3 bar color                  (Default 'royalblue')
    PLOT_DLV_DEFAULT_COLOR: Delivery mode default color                 (Default 'darkgrey')

    PLOT_AXHLINE_COLOR:     Horizontal line color across the Axes       (Default 'crimson')
    PLOT_TLINE_COLOR:       Trend line color                             (Default 'darkturquoise')
    PLOT_ALINE_COLOR:       Arrow color                                 (Default 'mediumseagreen')
    PLOT_HLINE_COLOR:       Horizontal line color                       (Default 'royalblue')

    """

    PRESET = {}
    WATCH = {"SECTORS": "sectors.csv"}

    TIME_ZONE = "America/New_York"

    Has_Latest_Holidays = False

    # alphavantage.co API Key
    API_KEY_Alphavantage = 'ZLV0FVBBQUBFWEZU'

    # Delivery
    DLV_L1 = 1
    DLV_L2 = 1.5
    DLV_L3 = 2
    DLV_AVG_LEN = 60
    VOL_AVG_LEN = 30

    # PLOT CONFIG
    PLOT_DAYS = 160
    PLOT_WEEKS = 140
    PLOT_M_RS_LEN_D = 60
    PLOT_M_RS_LEN_W = 52
    PLOT_RS_INDEX = "^GSPC"  # S&P 500
    MAGNET_MODE = True

    # PLOT THEMES AND COLORS
    # 'binance', 'binancedark', 'blueskies', 'brasil', 'charles',
    # 'checkers', 'classic', 'default', 'ibd', 'kenan', 'mike',
    # 'nightclouds', 'sas', 'starsandstripes', 'tradingview', 'yahoo'
    PLOT_CHART_STYLE = "tradingview"
    # ohlc, candle, line
    PLOT_CHART_TYPE = "candle"

    # PLOT COLORS
    # https://matplotlib.org/stable/gallery/color/named_colors.html#base-colors
    PLOT_RS_COLOR = "darkblue"
    PLOT_M_RS_COLOR = "darkgreen"
    PLOT_DLV_L1_COLOR = "red"
    PLOT_DLV_L2_COLOR = "darkorange"
    PLOT_DLV_L3_COLOR = "royalblue"
    PLOT_DLV_DEFAULT_COLOR = "darkgrey"
    PLOT_AXHLINE_COLOR = "crimson"
    PLOT_TLINE_COLOR = "darkturquoise"
    PLOT_ALINE_COLOR = "mediumseagreen"
    PLOT_HLINE_COLOR = "royalblue"

    # DO NOT EDIT BELOW
    VERSION = "0.1.0"

    # DB connection
    DB_CONN = {
        "host": "",
        "port": 0,
        "dbname": "",
        "user": "",
        "password": ""
    }

    def __init__(self, name: str = __name__) -> None:
        self.__name__ = name
        self.FILE_user: Path = Path(__file__).parents[1] / "user.json"

        if self.FILE_user.exists():
            dct = json.loads(self.FILE_user.read_bytes())
            if "WATCH" in dct:
                self.WATCH.update(dct["WATCH"])
            if "DB_CONN" in dct:
                self.DB_CONN.update(dct["DB_CONN"])
            self.__dict__.update(dct)

        self.ROOT = Path(self.__dict__.get("ROOT", self.FILE_user.parents[1] / "data"))

        # <editor-fold desc="Declare file & folder">
        # data structure
        self.ROOT_Logs = self.path_exist(self.ROOT / "log")
        self.ROOT_Data = self.path_exist(self.ROOT / "data")
        self.ROOT_Research = self.path_exist(self.ROOT / "research")

        # data sub-folder
        self.FOLDER_Symbols = self.path_exist(self.ROOT_Data / "symbols")
        self.FOLDER_Daily = self.path_exist(self.ROOT_Data / "daily")
        self.FOLDER_Tradings = self.path_exist(self.ROOT_Data / "daily")
        self.FOLDER_Infos = self.path_exist(self.ROOT_Data / "infos")

        # research sub-folder
        self.FOLDER_Watch = self.path_exist(self.ROOT_Research / "watch")
        self.FOLDER_Charts = self.path_exist(self.ROOT_Research / "charts")
        self.FOLDER_Lines = self.path_exist(self.ROOT_Research / "lines")
        self.FOLDER_Images = self.path_exist(self.ROOT_Research / "images")
        self.FOLDER_States = self.path_exist(self.ROOT_Research / "states")

        # Files
        self.FILE_WatchList = self.path_exist(Path(self.__dict__["SYM_LIST"]))
        self.FILE_Infos_Errors = self.path_exist(self.FOLDER_Infos / "errors.json")
        # </editor-fold>

        # <editor-fold desc="Declare Format">
        # Regex
        self.bonusRegex = re.compile(r"(\d+) ?: ?(\d+)")
        self.splitRegex = re.compile(r"(\d+\.?\d*)[/\- a-z.]+(\d+\.?\d*)")
        self.headerText = b"Date,Open,High,Low,Close,Volume,TOTAL_TRADES,QTY_PER_TRADE,DLV_QTY\n"
        # Timezone
        self.TIMEZONE_local = tzlocal.get_localzone()
        self.TIMEZONE_US = ZoneInfo(self.TIME_ZONE)
        # Color
        if "win" in sys.platform:
            # enable color support in Windows
            os.system("color")
        # </editor-fold>

        # <editor-fold desc="Initial Data">
        # PLOT Plugins
        self.PLOT_PLUGINS = {}
        # MyList
        self.LIST_Watch = pd.read_csv(self.FILE_WatchList)["watchlist"].tolist()
        # </editor-fold>

        # <editor-fold desc="API Key">
        self.KEY_Symbol = self.API_KEY_Alphavantage
        # </editor-fold>

        # <editor-fold desc="Setup Tools">
        # Logger
        self.logger = self._log_initial(self.__name__)
        # Exception custom handler (Set the sys.excepthook)
        sys.excepthook = self._log_unhandled_exception
        # </editor-fold>

    def to_list(self):
        return Path(self.FILE_user).read_text().strip("\n").split("\n")

    @staticmethod
    def path_exist(path: Path) -> Path:
        if path.exists():
            return path
        base, ext = os.path.splitext(path)
        if not ext:  # No extension means it's likely a directory
            # Create any necessary parent directories
            path.mkdir(parents=True, exist_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch()
        return path

    def __str__(self):
        txt = f"SPM1 | Version: {self.VERSION}\n"
        for p in self.__dict__:
            txt += f"{p}: {getattr(self, p)}\n"
        return txt

    def _log_unhandled_exception(self, exc_type, exc_value, exc_traceback):
        # Log the unhandled exception
        self.logger.critical(
            "Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    def _log_initial(self, name: str) -> logging.Logger:
        """Return a logger instance by name
        Creates a file handler to log messages with level WARNING and above
        Creates a stream handler to log messages with level INFO and above

        Parameters:
        name (str): Pass __name__ for module level logger
        """
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        stdout_handler = logging.StreamHandler()
        stdout_handler.setLevel(logging.INFO)
        stdout_handler.setFormatter(
            logging.Formatter('[%(asctime)s - %(name)s] %(levelname)s: %(message)s'))

        file_handler = logging.FileHandler(self.ROOT_Logs / "error.log")
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(
            logging.Formatter('[%(asctime)s - %(name)s] %(levelname)s: %(message)s')
        )

        logger.addHandler(stdout_handler)
        logger.addHandler(file_handler)

        return logger
