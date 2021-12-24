import unittest
from modules.fare_filing import FareFiling
from pydantic import BaseModel

class TestGG(unittest.TestCase):

    def setUp(self):
        self.app = FareFiling()
    
    def test_fare_basis(self):
        check_expect_1 = 'YLXOUS'
        check_expect_2 = 'BKWODUS'
        check_expect_3 = 'XHXUS'

        output_1 = self.app.gen_fare_basis('Y', 'L', 'X', 'O', '')
        output_2 = self.app.gen_fare_basis('B', 'K', 'W', 'O', 'D')
        output_3 = self.app.gen_fare_basis('X', 'H', 'X', '', '')
        
        self.assertEqual(output_1, check_expect_1)
        self.assertEqual(output_2, check_expect_2)
        self.assertEqual(output_3, check_expect_3)

    def test_calc_fare(self):
        check_expect_1 = {
            'base_fare': 1000,
            'ow_multiplier': .65,
            'weekend_surcharge': 40,
            'result': 690
        }

        check_expect_2 = {
            'base_fare': 2000,
            'ow_multiplier': .6,
            'weekend_surcharge': 80,
            'result': 1280
        }

        self.assertEqual(
            self.app.calc_fare(
                check_expect_1['base_fare'], 
                check_expect_1['ow_multiplier'], 
                check_expect_1['weekend_surcharge']
            ), check_expect_1['result']
        )

        self.assertEqual(
            self.app.calc_fare(
                check_expect_2['base_fare'], 
                check_expect_2['ow_multiplier'], 
                check_expect_2['weekend_surcharge']
            ), check_expect_2['result']
        )

    def test_work_package_record(self):
        from models.models import WorkPackageRecord

        check_expect_1 = {
            'origin': 'NYC', 
            'destination': 'TPE',
            'fare_basis': 'YLXSOE',
            'booking_class': 'Y',
            'cabin': 'Economy',
            'ow_rt': 'OO',
            'blank1': '',
            'blank2': '',
            'blank3': '',
            'currency': 'USD',
            'fare_price': 1000.0,
            'season': 'L'
        }
        check_expect_2 = {
            'origin': 'NYC', 
            'destination': 'SGN',
            'fare_basis': 'XHXSE',
            'booking_class': 'X',
            'cabin': 'Economy',
            'ow_rt': 'RT',
            'blank1': '',
            'blank2': '',
            'blank3': '',
            'currency': 'USD',
            'fare_price': 1000.0,
            'season': 'L'
        }

        record_1 = WorkPackageRecord(
            destination='TPE',
            fare_basis="YLXSOE",
            booking_class='Y',
            cabin='Economy',
            ow_rt='OO',
            blank1='',
            blank2='',
            blank3='',
            fare_price=1000.0,
            season='L'
        )

        record_2 = WorkPackageRecord(
            destination='SGN',
            fare_basis="XHXSE",
            booking_class='X',
            cabin='Economy',
            ow_rt='RT',
            blank1='',
            blank2='',
            blank3='',
            fare_price=1000.0,
            season='L'
        )

        self.assertEqual(record_1, check_expect_1)
        self.assertEqual(record_2, check_expect_2)
        
    def test_ping(self):
        import pandas as pd
        from models.models import Input, WorkPackage, WorkPackageRecord, FareCombination, CabinMapping, SeasonMapping

        input_file = r'./gg_fare_filing.xlsx'

        df_fare_combination = pd.read_excel(input_file, sheet_name='fare_combination', na_filter=False)
        df_cabin_mapping = pd.read_excel(input_file, sheet_name='cabin_mapping')
        df_season_mapping = pd.read_excel(input_file, sheet_name='season_mapping')
        df_input = pd.read_excel(input_file, sheet_name='input', na_filter=False)
        df_input = df_input.set_index('sort')
        df_input = df_input.sort_index()
        df_input = df_input.reset_index(drop=True)

        df_fare_combination = df_fare_combination.astype({
            'weekend_surcharge': 'int32',
            'oneway_multiplier': 'float64',
        })

        df_input_merged = pd.merge(df_input, df_cabin_mapping, on='booking_class')
        df_input_merged = pd.merge(df_input_merged, df_season_mapping, on='season')

        print(df_input_merged)

        a = Input(**df_input_merged.to_dict())
        print(a.dict())

        # x = FareCombination(**df_fare_combination.to_dict())
        # y = CabinMapping(**df_cabin_mapping.to_dict())
        # z = SeasonMapping(**df_season_mapping.to_dict())
        # print()
        # print(x)
        # print()
        # print(y)
        # print()
        # print(z)

    def test_logging(self):
        import logging

        # create logger
        logger = logging.getLogger(__name__)
        logger.setLevel('DEBUG')

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter  = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
        
        logger.info('Testing info level message')
        logger.debug('Testing debug level message')


if __name__ == '__main__':
    unittest.main()