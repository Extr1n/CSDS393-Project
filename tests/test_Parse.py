import sys
import os
import json
import unittest
import importlib
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestParse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.file_path = os.path.join(os.getcwd(), 'allcourse.json')
        # Create dummy data to write to allcourse.json.
        dummy_data = {
            "title": ["CSDS101.    TestName    .3 Units."],
            "desc": ["Course description. Prereq: CS101. "]
        }
        with open(cls.file_path, 'w', encoding='utf-8') as f:
            json.dump(dummy_data, f)

        from scrape import parse as parse_module
        importlib.reload(parse_module)
        cls.module = parse_module

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.file_path):
            os.remove(cls.file_path)

    def test_df_loaded(self):
        # Check that the module loaded a DataFrame from our dummy file.
        df = self.module.df  # assuming your module assigns the DataFrame to a global name 'df'
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIn('title', df.columns)
        self.assertIn('desc', df.columns)
        # Optionally, verify the contents:
        self.assertEqual(df.iloc[0]['title'], "CSDS101.    TestName    .3 Units.")
        self.assertEqual(df.iloc[0]['desc'], "Course description. Prereq: CS101. ")

    def test_extract_prereqs(self):
        #Test extract_prereqs when a prerequisite is present.
        text_with_prereq = "Course description. Prereq: CS101."
        result = self.module.extract_prereqs(text_with_prereq)
        self.assertEqual(result, "CS101.")
        #Test extract_prereqs when no prerequisite is present (should return an empty list).
        text_without_prereq = "This course is self-contained."
        result_empty = self.module.extract_prereqs(text_without_prereq)
        self.assertEqual(result_empty, [])

    def test_add_info(self):
        # Create a new DataFrame to test add_info independently.
        sample_title = "CSDS101.    TestName    .3 Units."
        sample_desc = "Course description. Prereq: CS101. "
        df_test = pd.DataFrame({
            'title': [sample_title],
            'desc': [sample_desc]
        })
        # Call add_info to add new columns.
        self.module.add_info(df_test)
        
        # Define expected new columns added by add_info.
        expected_columns = [
            'subject', 'code', 'name', 'credits',
            'cas_global_and_cultural_diversity', 'cas_quanitative_reasoning',
            'sages_departmental_seminar', 'sages_senior_capstone',
            'captsone_project', 'communication_intensive', 'disciplinary_intensive',
            'human_diversity_and_commonality', 'local_and_global_engagement',
            'moral_and_ethical_reasoning', 'quantitative_reasoning',
            'understanding_global_perspectives', 'full_semester_wellness_movement',
            'half_semester_wellnessmovement', 'full_semester_wellness_no_movement',
            'half_semester_wellness_no_movement', 'prereq'
        ]
        for col in expected_columns:
            self.assertIn(col, df_test.columns, f"Missing column: {col}")

        # Verify computed values
        self.assertEqual(df_test.loc[0, 'subject'], sample_title[:4])
        self.assertEqual(df_test.loc[0, 'code'], sample_title[:8])
        expected_name = sample_title[11:-11]
        self.assertEqual(df_test.loc[0, 'name'], expected_name)
        expected_credits = sample_title[-8:-7]
        self.assertEqual(df_test.loc[0, 'credits'], expected_credits)
        self.assertEqual(df_test.loc[0, 'prereq'], "CS101.")

if __name__ == '__main__':
    unittest.main()
