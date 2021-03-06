# import modules
import pandas as pd

# declare variables
input_file = r'.\gg_fare_filing.xlsx'
backup_file = r'.\fare_input_backup.xlsx'
orig = 'NYC'
currency = 'USD'
sheet_name = 'copy_this'
seasons = ('L', 'K', 'K1', 'K2', 'H', 'H1', 'H2', 'P')

# import configuration
df_input = pd.read_excel(input_file, sheet_name='input', na_filter=False)
df_cabin_mapping = pd.read_excel(input_file, sheet_name='cabin_mapping')
df_season_mapping = pd.read_excel(input_file, sheet_name='season_mapping')
df_fare_combination = pd.read_excel(input_file, sheet_name='fare_combination', na_filter=False)

df_input = df_input.set_index('sort')
df_input = df_input.sort_index()
df_input = df_input.reset_index(drop=True)

# join configuration with input file
df_input_merged = pd.merge(df_input, df_cabin_mapping, on='booking_class')
df_input_merged = pd.merge(df_input_merged, df_season_mapping, on='season')

def gen_fares():
    output = []

    # loop through each input row
    for i, row_input in df_input_merged.iterrows():
        dest = row_input['dest']
        booking_class = row_input['booking_class']
        season = row_input['season']
        season_code = row_input['season_code']
        base_fare = row_input['base_fare']
        direct = row_input['direct']
        cabin = row_input['cabin']

        # create different weekend and oneway combinations
        for j, row_fare_combination in df_fare_combination.iterrows():
            weekend = row_fare_combination['weekend']
            oneway = row_fare_combination['oneway']
            weekend_surcharge = row_fare_combination['weekend_surcharge']
            oneway_multiplier = row_fare_combination['oneway_multiplier']
            oneway_mapping = row_fare_combination['oneway_mapping']

            fare_basis = booking_class + season_code + weekend + 'S' + oneway + direct + 'E'
            fare = (base_fare + weekend_surcharge) * oneway_multiplier

            row_output = {
                'orig': orig,
                'dest': dest,
                'fare_basis': fare_basis,
                'booking_class': booking_class,
                'cabin': cabin,
                'ow/rt': oneway_mapping,
                'blank1': '',
                'blank2': '',
                'blank3': '',
                'currency': currency,
                'fare': fare,
                'season': season
            }

            output.append(row_output)
    return output

def create_output(output):
    dict_df = {}
    columns = [
        'orig', 'dest', 'fare_basis', 'booking_class',
        'cabin', 'ow/rt', 'blank1', 'blank2', 'blank3',
        'currency', 'fare', 'season'
    ]
    df_output = pd.DataFrame(columns=columns, data=output)

    for season in seasons:
        df = df_output[df_output['season'] == season]
        df = df.drop(columns='season')

        if not df.empty:
            df.reset_index(inplace=True, drop=True)
            dict_df[season] = df

    with pd.ExcelWriter(input_file, engine="openpyxl", mode='a') as writer:
        workbook = writer.book
        for key, dataframe in dict_df.items():
            try:
                workbook.remove(workbook[key])
            except:
                print(f'Worksheet [{key}] does not exist')
            finally:
                dataframe.to_excel(writer, sheet_name=key, index=False)

def backup_input(df_input):
    dict_df = {}

    for season in seasons:
        df = df_input[df_input['season'] == season]

        if not df.empty:
            df.reset_index(inplace=True, drop=True)
            dict_df[season] = df

    with pd.ExcelWriter(backup_file, engine="openpyxl", mode='a') as writer:
        workbook = writer.book
        for key, dataframe in dict_df.items():
            try:
                workbook.remove(workbook[key])
            except:
                print(f'Worksheet [{key}] does not exist')
            finally:
                dataframe.to_excel(writer, sheet_name=key, index=False)
    return dict_df


if __name__ == '__main__':
    backup_input(df_input)
    output = gen_fares()
    # print(output)
    create_output(output)


    # print(df_input)
    # print()
    # print(df_input_merged)

    # x = backup_input(df_input)

    # for k, v in x.items():
    #     print(v)
