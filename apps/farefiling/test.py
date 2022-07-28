import unittest
import app


def hello_world():
    pass


class TestFareFiling(unittest.TestCase):

    def test_excel_loader(self):
        required_sheets = (
            'input',
            'cabin_mapping',
            'season_mapping',
            'fare_combination',
        )

        dfs = app.modules.utilities.excel_loader(app.input_file)
        keys = tuple(dfs.keys())

        for sheet in required_sheets:
            msg = f"sheet '{sheet}' is missing from Excel workbook"
            with self.subTest(msg):
                self.assertIn(sheet, keys)

    def test_generate_fare_combinations(self):
        pass


if __name__ == '__main__':
    unittest.main()
