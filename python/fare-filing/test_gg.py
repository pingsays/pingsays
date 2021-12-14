import unittest
import gg

class TestGG(unittest.TestCase):

    def setUp(self):
        self.app = gg.FareFiling()
    
    def test_fare_basis(self):
        check_expect_1 = 'YLXSOE'
        check_expect_2 = 'BKWSODE'
        check_expect_3 = 'XHXSE'  

        output_1 = self.app.gen_fare_basis('Y', 'L', 'X', 'O', '')
        output_2 = self.app.gen_fare_basis('B', 'K', 'W', 'O', 'D')
        output_3 = self.app.gen_fare_basis('X', 'H', 'X', '', '')
        
        self.assertEqual(output_1, check_expect_1)
        self.assertEqual(output_2, check_expect_2)
        self.assertEqual(output_3, check_expect_3)

    def test_work_package_record(self):
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

        record_1 = gg.WorkPackageRecord(
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

        record_2 = gg.WorkPackageRecord(
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

    def test_joins(self):
        self.app.import_config()

        print(self.app.df_fare_combination)

if __name__ == '__main__':
    unittest.main()