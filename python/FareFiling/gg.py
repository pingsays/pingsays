# import modules
import pandas as pd

# declare variables
input_file = r'.\gg_fare_filing.xlsx'
orig = 'NYC'
currency = 'USD'
sheet_name = 'copy_this'

# import configuration
df_input = pd.read_excel(input_file, sheet_name='input', na_filter=False)
df_cabin_mapping = pd.read_excel(input_file, sheet_name='cabin_mapping')
df_season_mapping = pd.read_excel(input_file, sheet_name='season_mapping')
df_fare_combination = pd.read_excel(input_file, sheet_name='fare_combination', na_filter=False)

# join configuration with input file
df_input = pd.merge(df_input, df_cabin_mapping, on='booking_class')
df_input = pd.merge(df_input, df_season_mapping, on='season')

def gen_fares():
    output = []

    # loop through each input row
    for i, row_input in df_input.iterrows():
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
                'fare': fare
            }

            output.append(row_output)
    return output


if __name__ == '__main__':
    output = gen_fares()

    columns = [
        'orig', 'dest', 'fare_basis', 'booking_class', 'cabin',
        'ow/rt', 'blank1', 'blank2', 'blank3', 'currency', 'fare'
    ]

    df_output = pd.DataFrame(columns=columns, data=output)

    with pd.ExcelWriter(input_file, engine="openpyxl", mode='a') as writer:
        workbook = writer.book
        try:
            workbook.remove(workbook[sheet_name])
        except:
            print('Worksheet does not exist')
        finally:
            df_output.to_excel(writer, sheet_name=sheet_name, index=False)
