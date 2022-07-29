import src.modules.utilities
import src.datatype_mapping

input_file = r'gg_fare_filing.xlsx'

config_sheets = {
    'input',
    'cabin_mapping',
    'season_mapping',
    'fare_combination'
}

def main():
    excel_sheets = src.modules.utilities.excel_loader(input_file)

    # filter for config sheets only
    dfs = dict()
    for key, df in excel_sheets.items():
        if key in config_sheets:
            dfs[key] = df

    sheet_names = tuple(dfs.keys())

    # apply dtypes to dataframes
    for sheet_name, dtypes in src.datatype_mapping.dtype_mapping.items():
        dfs[sheet_name] = dfs[sheet_name].astype(dtypes)

    # print dfs for troubleshooting
    for sheet_name, df in dfs.items():
        print(sheet_name)
        print(df)
        print(df.dtypes)

    x = src.modules.utilities.merge_dfs(
        input_df=dfs['input'],
        cabin_df=dfs['cabin_mapping'],
        season_df=dfs['season_mapping'],
    )

    print(x)




if __name__ == '__main__':
    main()