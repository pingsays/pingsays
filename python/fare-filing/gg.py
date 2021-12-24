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
        self.df_cabin_mapping = pd.read_excel(self.input_file, sheet_name='cabin_mapping')
        self.df_season_mapping = pd.read_excel(self.input_file, sheet_name='season_mapping')
        self.df_input = pd.read_excel(self.input_file, sheet_name='input', na_filter=False)
        self.df_input = self.df_input.set_index('sort')
        self.df_input = self.df_input.sort_index()
        self.df_input = self.df_input.reset_index(drop=True)
        self.df_fare_combination = pd.read_excel(self.input_file, sheet_name='fare_combination', na_filter=False)

        # update data type
        self.df_fare_combination = self.df_fare_combination.astype({
            'weekend_surcharge': 'int32',
            'oneway_multiplier': 'float64',
        })

        # join configuration with input file
        self.df_input_merged = pd.merge(self.df_input, self.df_cabin_mapping, on='booking_class')
        self.df_input_merged = pd.merge(self.df_input_merged, self.df_season_mapping, on='season')

    def gen_fares(self) -> WorkPackage:
        rt_only_rbd = self.get_rt_only_rbd(self.df_cabin_mapping)
        weekend_only_rbd = self.get_weekend_only_rbd(self.df_cabin_mapping)
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

                # skip if RBD does not have round trip fares
                if booking_class in rt_only_rbd and oneway == 'O':
                    continue

                # skip if RBD does not have weekend or weekday
                if booking_class in weekend_only_rbd:
                    if weekend == 'W':
                        continue
                    elif weekend == 'X':
                        weekend = ''

                fare_basis = self.gen_fare_basis(booking_class, season_code, weekend, oneway, direct)
                fare = self.calc_fare(base_fare, oneway_multiplier, weekend_surcharge)

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

    def calc_fare(self, base_fare, ow_multiplier, weekend_surcharge):
        return (base_fare * ow_multiplier) + weekend_surcharge

    def get_rt_only_rbd(self, df) -> List:
        valid_input = ('Y', 'y')
        rt_only_rbd = df[df['rt_only'].isin(valid_input)]
        rt_only_rbd_list = rt_only_rbd['booking_class'].values
        print(rt_only_rbd_list)
        return rt_only_rbd_list

    def get_weekend_only_rbd(self, df) -> List:
        valid_input = ('Y', 'y')
        weekend_only_rbd = df[df['weekend_only'].isin(valid_input)]
        weekend_only_rbd_list = weekend_only_rbd['booking_class'].values
        print(weekend_only_rbd_list)
        return weekend_only_rbd_list

    def gen_fare_basis(self, booking_class, season_code, weekend, oneway, direct):
        return f"{booking_class}{season_code}{weekend}{oneway}{direct}US"

    def create_output(self, fares):
        dict_df = {}
        df_fares = pd.DataFrame(data=fares.dict()['data'])

        # round fare price then convert to int to remove decimal place
        # df_fares = df_fares.round({'fare_price': 0})
        # df_fares['fare_price'] = df_fares['fare_price'].astype('int')
        print(df_fares)

        for season in self.seasons:
            df = df_fares[df_fares['season'] == season]
            df = df.drop(columns='season')

            if not df.empty:
                df.reset_index(inplace=True, drop=True)
                dict_df[season] = df

        with pd.ExcelWriter(self.input_file, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            for key, dataframe in dict_df.items():
                dataframe.to_excel(writer, sheet_name=key, index=False)

    def backup_input(self, df_input):
        dict_df = {}

        for season in self.seasons:
            df = df_input[df_input['season'] == season]

            if not df.empty:
                df.reset_index(inplace=True, drop=True)
                dict_df[season] = df

        with pd.ExcelWriter(self.backup_file, engine="openpyxl", mode='a', if_sheet_exists='replace') as writer:
            for key, dataframe in dict_df.items():
                dataframe.to_excel(writer, sheet_name=key, index=False)
        return dict_df


if __name__ == '__main__':
    gg = FareFiling()
    gg.import_config()
    gg.backup_input(gg.df_input)
    fares = gg.gen_fares()
    gg.create_output(fares)
