import pandas as pd
from pandas import DataFrame

def excel_loader(excel_file: str) -> dict[str, DataFrame]:
    dfs = pd.read_excel(excel_file, sheet_name=None)
    return dfs
