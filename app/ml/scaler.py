import pandas as pd
from sklearn.preprocessing import StandardScaler as SklearnStandardScaler
from sklearn.preprocessing import MinMaxScaler as SklearnMinMaxScaler
import numpy as np

def standard_scaler(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melakukan Standard Scaling (Z-score normalization) pada data numerik.
    Menghasilkan data dengan mean=0 dan variance=1.
    """
    scaler = SklearnStandardScaler()
    scaled_data = scaler.fit_transform(df)
    return pd.DataFrame(scaled_data, columns=df.columns, index=df.index)

def min_max_scaler(df: pd.DataFrame) -> pd.DataFrame:
    """
    Melakukan Min-Max Scaling pada data numerik.
    Menghasilkan data dalam rentang [0, 1].
    """
    scaler = SklearnMinMaxScaler()
    scaled_data = scaler.fit_transform(df)
    return pd.DataFrame(scaled_data, columns=df.columns, index=df.index)
