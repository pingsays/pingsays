# import modules
import pandas as pd
from pydantic import BaseModel
from typing import List


class WorkPackageRecord(BaseModel):
    """Class for keeping track of all information needed for work package"""
    # declare constants
    origin: str = 'NYC'
    destination: str
    fare_basis: str
    booking_class: str
    cabin: str
    ow_rt: str
    blank1: str
    blank2: str
    blank3: str
    currency: str = 'USD'
    fare_price: float
    season: str


class WorkPackage(BaseModel):
    data: List[WorkPackageRecord]


class FareFiling:
    def __init__(self) -> None:
        # declare variables
        self.input_file = r'./gg_fare_filing.xlsx'
        self.backup_file = r'./fare_input_backup.xlsx'
        self.seasons = ('L', 'K', 'K1', 'K2', 'H', 'H1', 'H2', 'P')

    def import_config(self) -> None:
        # import configuration
        df_cabin_mapping = pd.read_excel(self.input_file, sheet_name='cabin_mapping')
        df_season_mapping = pd.read_excel(self.input_file, sheet_name='season_mapping')
        df_input = pd.read_excel(self.input_file, sheet_name='input', na_filter=False)
        df_input = df_input.set_index('sort')
        df_input = df_input.sort_index()
        df_input = df_input.reset_index(drop=True)
        self.df_fare_combination = pd.read_excel(self.input_file, sheet_name='fare_combination', na_filter=False)

        # join configuration with input file
        self.df_input_merged = pd.merge(df_input, df_cabin_mapping, on='booking_class')
        self.df_input_merged = pd.merge(self.df_input_merged, df_season_mapping, on='season')

    def gen_fare_basis(self, booking_class, season_code, weekend, oneway, direct):
        return f"{booking_class}{season_code}{weekend}S{oneway}{direct}E"

    def gen_fares(self) -> WorkPackage:
        output = []

        # loop through each input row
        for i, row_input in self.df_input_merged.iterrows():
            dest = row_input['dest']
            booking_class = row_input['booking_class']
            season = row_input['season']
            season_code = row_input['season_code']
            base_fare = row_input['base_fare']
            direct = row_input['direct']
            cabin = row_input['cabin']

            # create different weekend and oneway combinations
            for j, row_fare_combination in self.df_fare_combination.iterrows():
                weekend = row_fare_combination['weekend']
                oneway = row_fare_combination['oneway']
                weekend_surcharge = row_fare_combination['weekend_surcharge']
                oneway_multiplier = row_fare_combination['oneway_multiplier']
                oneway_mapping = row_fare_combination['oneway_mapping']

                fare_basis = self.gen_fare_basis(booking_class, season, weekend, oneway, direct)
                fare = (base_fare + weekend_surcharge) * oneway_multiplier

                row_output = WorkPackageRecord(
                    destination=dest,
                    fare_basis=fare_basis,
                    booking_class=booking_class,
                    cabin=cabin,
                    ow_rt=oneway_mapping,
                    blank1='',
                    blank2='',
                    blank3='',
                    fare_price=fare,
                    season=season
                )

                output.append(row_output.dict())
        return WorkPackage(data=output)

    def create_output(self, output):
        dict_df = {}
        columns = [
            'orig', 'dest', 'fare_basis', 'booking_class',
            'cabin', 'ow/rt', 'blank1', 'blank2', 'blank3',
            'currency', 'fare', 'season'
        ]
        df_output = pd.DataFrame(columns=columns, data=output.data)

        for season in self.seasons:
            df = df_output[df_output['season'] == season]
            df = df.drop(columns='season')

            if not df.empty:
                df.reset_index(inplace=True, drop=True)
                dict_df[season] = df

        with pd.ExcelWriter(self.input_file, engine="openpyxl", mode='a') as writer:
            workbook = writer.book
            for key, dataframe in dict_df.items():
                try:
                    workbook.remove(workbook[key])
                except:
                    print(f'Worksheet [{key}] does not exist')
                finally:
                    dataframe.to_excel(writer, sheet_name=key, index=False)

    def backup_input(self, df_input):
        dict_df = {}

        for season in self.seasons:
            df = df_input[df_input['season'] == season]

            if not df.empty:
                df.reset_index(inplace=True, drop=True)
                dict_df[season] = df

        with pd.ExcelWriter(self.backup_file, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            workbook = writer.book
            for key, dataframe in dict_df.items():
                # try:
                #     workbook.remove(workbook[key])
                # except:
                #     print(f'Worksheet [{key}] does not exist')
                # finally:
                dataframe.to_excel(writer, sheet_name=key, index=False)
        return dict_df


if __name__ == '__main__':
    gg = FareFiling()
    gg.import_config()
    # backup_input(df_input)
    output = gg.gen_fares()
    gg.create_output(output)

    # x = WorkPackageRecord(
    #     destination='TPE',
    #     fare_basis='XYLC',
    #     booking_class='B',
    #     cabin='Y',
    #     ow_rt='OW',
    #     blank1='',
    #     blank2='',
    #     blank3='',
    #     fare_price=1000.0,
    #     season='L',
    # )

    # y = WorkPackageRecord(
    #     destination='SGN',
    #     fare_basis='CLC',
    #     booking_class='C',
    #     cabin='C',
    #     ow_rt='RT',
    #     blank1='',
    #     blank2='',
    #     blank3='',
    #     fare_price=2000.0,
    #     season='L',
    # )

    # data = [x, y]

    # z = WorkPackage(data=data)

    # # print(x.dict())
    # # print(f"{y=}")
    # print(z.data)

    # print(df_input)
    # print()
    # print(self.df_input_merged)

    # x = backup_input(df_input)

    # for k, v in x.items():
    #     print(v)
