import pandas as pd
from pandas import DataFrame


def excel_loader(excel_file: str) -> dict[str, DataFrame]:
    dfs = pd.read_excel(excel_file, sheet_name=None)
    # {df[sheet].reset_index(drop=True) for sheet, df in dfs.items()}
    # dfs = dfs.reset_index(drop=True)
    return dfs

def gen_fare_combinations(base_df: DataFrame, fare_combination_df: DataFrame) -> DataFrame:
    print(base_df)
    for _, base_row in base_df.iterrows():
        rbd = base_row['booking_class']
        season = base_row['season_code']

        for _, combination_row in fare_combination_df.iterrows():
            weekday = combination_row['weekday']
            ow = combination_row['oneway']

            if base_row['rt_only'] and combination_row['oneway']:
                continue

            if base_row['no_weekday_weekend'] and combination_row['weekday']:
                continue

            if base_row['no_weekday_weekend']:
                weekday = None

            fare_basis = gen_fare_basis(
                rbd=rbd,
                season=season,
                weekday =weekday,
                ow =ow
            )
            print(fare_basis)

def merge_dfs(input_df: DataFrame, cabin_df: DataFrame, season_df: DataFrame):
    df = input_df.merge(cabin_df, on='booking_class')
    df = df.merge(season_df, on='season')
    return df

def gen_fare_basis(rbd: str, season: str, weekday: bool, ow: bool, country: str='US') -> str:
    if weekday is None:
        weekday_code = ''
    elif weekday:
        weekday_code = 'X'
    else:
        weekday_code = 'W'

    if ow:
        ow_code = 'O'
    else:
        ow_code = ''

    fare_basis = f"{rbd}{season}{weekday_code}{ow_code}{country}"
    return fare_basis

# def set_dtypes(df: DataFrame, dtype_mapping: dict) -> DataFrame:
#     df = df.astype(dtype_mapping)
#     return df
