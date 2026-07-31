# import pandas as pd
# from pathlib import Path

# class DataLoader:
#     """
#     Responsible for loading datasets.
    
#     This class has only one responsibility:
#     Reading datasets from storage.
#     """

#     def __init__(self):

#         self.data_path = Path("data/raw/incident_reports.csv")

#     def load_data(self):

#         df = pd.read_csv(self.data_path, index_col=0)

#         return df    

import pandas as pd
from pathlib import Path

class DataLoader:
    """
    Responsible for loading datasets.

    This class has only one responsibility:
    Reading datasets from storage.
    """

    def __init__(self, filepath: str | Path = "data/raw/incident_reports_1000.csv"):
        self.data_path = Path(filepath)

    def load_data(self):
        df = pd.read_csv(self.data_path, index_col=0)
        return df