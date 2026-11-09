import pandas as pd
import numpy as np
from app.services.data import MyDataFrame

class InfoNumericColumn :
    def __init__(self, type, name, count, mean, std, min, Q1, Q2, Q3, max, distribution):
        self.type = type
        self.name = name
        self.count = count
        self.mean = mean 
        self.std = std
        self.min = min
        self.Q1  = Q1
        self.Q2  = Q2
        self.Q3  = Q3
        self.max = max
        self.distribution = distribution

class InfoCathColumn :
    def __init__(self, type, name, count, unique, top,freq, distribution):
        self.type = type
        self.name = name
        self.count = count
        self.unique = unique
        self.top = top
        self.freq = freq
        self.distribution = distribution

def get_infos_columns():
    df = MyDataFrame().getMyDataFrame()
    columns = []
    for column in df.columns.to_list() :
        infos = df[column].describe() 
        if pd.api.types.is_numeric_dtype(df[column]) :
            serie = df[column].dropna()
            # Calcul de l'histogramme
            frequencies, bins = np.histogram(serie, bins=10)
            distribution = {
                "labels": [
                    f"{bins[i]:.2f} - {bins[i+1]:.2f}"
                    for i in range(len(frequencies))
                ],
                "values": frequencies.tolist()
            }
            
            columns.append(InfoNumericColumn(str(df[column].dtype), column, infos['count'],
                                              infos['mean'], infos['std'], infos['min'], infos['25%'],
                                                infos['50%'], infos['75%'], infos['max'], distribution))

        else : 
            series = df[column].dropna()

            # Distribution des valeurs
            distribution = series.value_counts()

            total = len(series)

            distribution_data = []

            for value, frequency in distribution.items():

                percentage = (frequency / total) * 100 if total > 0 else 0

                distribution_data.append({
                    "value": str(value),
                    "frequency": int(frequency),
                    "percentage": round(percentage, 2)
                })
            columns.append(InfoCathColumn(str(df[column].dtype), column, infos['count'], infos['unique'], infos['top'],infos['freq'], distribution_data))
    return columns