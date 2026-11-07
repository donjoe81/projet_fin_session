import pandas as pd
from pandas import DataFrame
from pathlib import Path
root=Path(__file__).resolve().parents[2]
csv_file=root/'dataset'/'train.csv'
df=pd.read_csv(csv_file)

class MyDataFrame:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            print(21212121)
            self._df = pd.read_csv(csv_file)
            self._initialized = True

    def getMyDataFrame(self):
        return self._df

def get_data_frame() -> DataFrame:
    return df
