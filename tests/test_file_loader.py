import unittest
import json
import os
from neo4j import GraphDatabase
from file_loader import FileLoader
from icdc_schema import ICDC_Schema
from props import Props
from config import BentoConfig
from data_loader import DataLoader


@unittest.skipIf('NEO_PASSWORD' not in os.environ, "NEO_PASSWORD environment variable not set")
class TestLambda(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(test_dir, 'data', 'lambda', 'event1.json')) as inf:
            self.event = json.load(inf)
        uri = 'bolt://localhost:7687'
        user = 'neo4j'
        password = os.environ['NEO_PASSWORD']

        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        props = Props(os.path.join(os.path.dirname(test_dir), 'config', 'props-ins.yml'))
        self.schema = ICDC_Schema([
            os.path.join(test_dir, 'data', 'icdc-model.yml'),
            os.path.join(test_dir, 'data', 'icdc-model-props.yml')
        ], props)
        config = BentoConfig(os.path.join(os.path.dirname(test_dir), 'config', 'config.ini'))
        self.processor = FileLoader('', self.driver, self.schema, config, 'ming-icdc-file-loader', 'Final/Data_loader/Manifests')
        self.loader = DataLoader(self.driver, self.schema)
        self.file_list = [
            os.path.join(test_dir, "data", "Dataset", "COP-program.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-case.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-diagnosis.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_cohort_file.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_study_file.txt")
        ]

    def test_join_path(self):
        self.assertEqual(self.processor.join_path(), '')
        self.assertEqual(self.processor.join_path('abc'), 'abc')
        self.assertEqual(self.processor.join_path('/abc'), '/abc')
        self.assertEqual(self.processor.join_path('/abc/'), '/abc')

        self.assertEqual(self.processor.join_path('abd/def', 'ghi.zip'), 'abd/def/ghi.zip')
        self.assertEqual(self.processor.join_path('abd/def/', 'ghi.zip'), 'abd/def/ghi.zip')
        self.assertEqual(self.processor.join_path('abd/def//', '//ghi.zip'), 'abd/def/ghi.zip')
        self.assertEqual(self.processor.join_path('http://abd/def//', '//ghi.zip//'), 'http://abd/def/ghi.zip')

        # Test multiple paths joining
        self.assertEqual(self.processor.join_path('abd/def', 'xy/z', 'ghi.zip'), 'abd/def/xy/z/ghi.zip')
        self.assertEqual(self.processor.join_path('abd/def/', '/xy/z/' , 'ghi.zip'), 'abd/def/xy/z/ghi.zip')
        self.assertEqual(self.processor.join_path('abd/def/', '///xy/z///', '///ghi.zip'), 'abd/def/xy/z/ghi.zip')

    def test_lambda(self):
        load_result = self.loader.load(self.file_list, True, False, 'upsert', False, 1)
        self.assertIsInstance(load_result, dict, msg='Load data failed!')

        self.assertTrue(self.processor.handler(self.event))
