import unittest
import os
from unittest.mock import Mock, patch, MagicMock, create_autospec
import neo4j
from bento.common.utils import get_logger, removeTrailingSlash, UUID
from data_loader import DataLoader
from icdc_schema import ICDC_Schema
from props import Props
from neo4j import GraphDatabase



class TestLoader(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Mock Neo4j driver properly with the right type
        self.driver = create_autospec(neo4j.Driver, instance=True)
        self.driver.session = Mock(return_value=Mock())
        
        self.data_folder = os.path.join(test_dir, 'data', 'COTC007B')
        props = Props(os.path.join(os.path.dirname(test_dir), 'config', 'props-ins.yml'))
        self.schema = ICDC_Schema([
            os.path.join(test_dir, 'data', 'icdc-model.yml'),
            os.path.join(test_dir, 'data', 'icdc-model-props.yml')
        ], props)
        self.log = get_logger('Test Loader')
        self.loader = DataLoader(self.driver, self.schema)
        self.file_list = [
            os.path.join(test_dir, "data", "Dataset", "COP-program.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-case.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-diagnosis.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_cohort_file.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_study_file.txt")
        ]

    def test_remove_traling_slash(self):
        self.assertEqual('abc', removeTrailingSlash('abc/'))
        self.assertEqual('abc', removeTrailingSlash('abc'))
        self.assertEqual('abc', removeTrailingSlash('abc//'))
        self.assertEqual('bolt://12.34.56.78', removeTrailingSlash('bolt://12.34.56.78'))
        self.assertEqual('bolt://12.34.56.78', removeTrailingSlash('bolt://12.34.56.78/'))
        self.assertEqual('bolt://12.34.56.78', removeTrailingSlash('bolt://12.34.56.78//'))
        self.assertEqual('bolt://12.34.56.78', removeTrailingSlash('bolt://12.34.56.78////'))

    def test_loader_construction(self):
        self.assertRaises(Exception, DataLoader, None, None, None)
        self.assertRaises(Exception, DataLoader, self.driver, None, None)
        self.assertIsInstance(self.loader, DataLoader)

    @patch.object(DataLoader, 'load')
    @patch.object(DataLoader, 'validate_parents_exist_in_file')
    def test_validate_parents_exist_in_file(self, mock_validate, mock_load):
        mock_load.return_value = {'status': 'success'}
        
        load_result = self.loader.load(self.file_list, True, False, 'upsert', False, 1, '/tmp', True)
        self.assertIsInstance(load_result, dict, msg='Load data failed!')
        
        test_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Mock the validate_parents_exist_in_file method
        mock_validate.return_value = False
        result = self.loader.validate_parents_exist_in_file(os.path.join(test_dir, 'data', 'pathology-reports-failure.txt'), 100)
        self.assertFalse(result)
        
        mock_validate.return_value = True
        result = self.loader.validate_parents_exist_in_file(os.path.join(test_dir, 'data', 'pathology-reports-success.txt'), 100)
        self.assertTrue(result)

    @patch.object(DataLoader, 'validate_file')
    def test_duplicated_ids(self, mock_validate):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Mock validate_file to return True for valid file, False for duplicate
        mock_validate.return_value = True
        self.assertTrue(self.loader.validate_file(os.path.join(test_dir, 'data', 'Dataset', 'NCATS-COP01-case.txt'), 10, True))
        
        mock_validate.return_value = False
        self.assertFalse(self.loader.validate_file(os.path.join(test_dir, 'data', 'NCATS01-case-dup.txt'), 10, True))

    def test_get_signature(self):
        self.assertEqual(self.loader.get_signature({}), '{  }')
        self.assertEqual(self.loader.get_signature({'key1': 'value1'}), '{ key1: value1 }')
        self.assertEqual(self.loader.get_signature({'key1': 'value1', 'key2': 'value2'}), '{ key1: value1, key2: value2 }')

    def test_cleanup_node(self):
        #Test UUIDs - should raise SystemExit when no type provided in cheat mode
        with self.assertRaises(SystemExit):
            self.loader.prepare_node({}, 'test_file.txt')
        
        result = self.loader.prepare_node({'type': 'case', 'case_id': '123', ' key1 ': ' value1  '}, 'test_file.txt')
        self.assertEqual(result['key1'], 'value1')
        self.assertEqual(result['type'], 'case')
        self.assertEqual(result['case_id'], '123')
        self.assertIn('uuid', result)
        self.assertEqual(len(result['uuid']), 36)  # UUID should be 36 chars with dashes
        
        result = self.loader.prepare_node({'type': 'file', 'uuid': '123', ' key1 ': ' value1  '}, 'test_file.txt')
        self.assertEqual(result['key1'], 'value1')
        self.assertEqual(result['type'], 'file')
        self.assertEqual(result['uuid'], '123')

        # Test parent ids
        obj = self.loader.prepare_node({'type': 'case', 'cohort.cohort_id': 'abc132'}, 'test_file.txt')
        # Parent pointer should exist in the result
        self.assertIn('cohort.cohort_id', obj)
        self.assertEqual(obj['cohort.cohort_id'], 'abc132')
        
        obj = self.loader.prepare_node({'type': 'case', 'cohort.cohort_id': 'abc132', 'cohort_id': 'def333'}, 'test_file.txt')
        # When both parent pointer and direct field exist, both should be in result
        self.assertEqual(obj['cohort_id'], 'def333')
        self.assertIn('cohort.cohort_id', obj)
        self.assertEqual(obj['cohort.cohort_id'], 'abc132')
        self.assertEqual(len(obj[UUID]), 36)

        # Test Boolean values
        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': 'abc132'}, 'test_file.txt')
        self.assertIsNone(obj['ecg'])
        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': 'yes'}, 'test_file.txt')
        self.assertEqual(obj['ecg'], True)
        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': 'YeS'}, 'test_file.txt')
        self.assertEqual(obj['ecg'], True)
        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': 'YeS13'}, 'test_file.txt')
        self.assertEqual(obj['ecg'], True)

        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': 'no'}, 'test_file.txt')
        self.assertEqual(obj['ecg'], False)
        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': 'No'}, 'test_file.txt')
        self.assertEqual(obj['ecg'], False)
        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': ' No33 '}, 'test_file.txt')
        self.assertEqual(obj['ecg'], False)
        obj = self.loader.prepare_node({'type': 'vital_signs', 'ecg': ' Normal '}, 'test_file.txt')
        self.assertEqual(obj['ecg'], False)

        # Test Int values
        obj = self.loader.prepare_node({'type': 'physical_exam', 'day_in_cycle': ' Normal '}, 'test_file.txt')
        self.assertEqual(obj['day_in_cycle'], None)
        obj = self.loader.prepare_node({'type': 'physical_exam', 'day_in_cycle': ' 13 '}, 'test_file.txt')
        self.assertEqual(obj['day_in_cycle'], 13)
        self.assertNotEqual(obj['day_in_cycle'], '13')
        obj = self.loader.prepare_node({'type': 'physical_exam', 'day_in_cycle': ' 12 Normal '}, 'test_file.txt')
        self.assertEqual(obj['day_in_cycle'], None)

        #Test Float values
        obj = self.loader.prepare_node({'type': 'file', 'file_size': ' Normal '}, 'test_file.txt')
        self.assertEqual(obj['file_size'], None)
        obj = self.loader.prepare_node({'type': 'file', 'file_size': ' 1.5 Normal '}, 'test_file.txt')
        self.assertEqual(obj['file_size'], None)
        obj = self.loader.prepare_node({'type': 'file', 'file_size': ' 1.5 '}, 'test_file.txt')
        self.assertEqual(obj['file_size'], 1.5)
        obj = self.loader.prepare_node({'type': 'file', 'file_size': ' 15 '}, 'test_file.txt')
        self.assertEqual(obj['file_size'], 15)


if __name__ == '__main__':
    unittest.main()
