import modules.utilities

input_file = r'gg_fare_filing.xlsx'

def main():
    dfs = modules.utilities.excel_loader(input_file)
    print(dfs.keys())


if __name__ == '__main__':
    main()