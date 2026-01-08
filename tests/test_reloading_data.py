import unittest
from bento.common.utils import get_logger, NODES_CREATED, RELATIONSHIP_CREATED, NODES_DELETED, RELATIONSHIP_DELETED
from data_loader import DataLoader
from icdc_schema import ICDC_Schema
from props import Props
import os
from neo4j import GraphDatabase


class TestLoaderReload(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        uri = 'bolt://localhost:7687'
        user = 'neo4j'
        password = os.environ['NEO_PASSWORD']

        self.driver = GraphDatabase.driver(uri, auth = (user, password))
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
            os.path.join(test_dir, "data", "Dataset", "COTC007B-case.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-cohort.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-cycle.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-demographic.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-diagnostic.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-enrollment.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-extent_of_disease.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-physical_exam.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-principal_investigator.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-prior_surgery.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-study.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-study_arm.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-vital_signs.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-blood_samples.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-case.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-demographic.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-diagnosis.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-enrollment.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-normal_samples.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-tumor_samples.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_20170228-GSL-079A-PE-Breen-NCATS-MEL-Rep1-Lane3.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep1-Lane1.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep1-Lane2.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep2-Lane1.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep3-Lane1.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep2-Lane2.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep2-Lane3.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep3-Lane2.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep3-Lane3.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_cohort_file.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_path_report_file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_study_file.txt")
        ]
        self.file_list_unique = [
            os.path.join(test_dir, "data", "Dataset", "COP-program.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-case.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-cohort.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-cycle.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-demographic.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-diagnostic.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-enrollment.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-extent_of_disease.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-physical_exam.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-principal_investigator.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-prior_surgery.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-study.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-study_arm.txt"),
            os.path.join(test_dir, "data", "Dataset", "COTC007B-vital_signs_unique.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-blood_samples.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-case.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-demographic.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-diagnosis.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-enrollment.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-normal_samples.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01-tumor_samples.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_20170228-GSL-079A-PE-Breen-NCATS-MEL-Rep1-Lane3.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep1-Lane1.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep1-Lane2.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep2-Lane1.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-076A-Breen-NCATS-MEL-Rep3-Lane1.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep2-Lane2.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep2-Lane3.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep3-Lane2.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_GSL-079A-Breen-NCATS-MEL-Rep3-Lane3.tar-file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_cohort_file.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_path_report_file_neo4j.txt"),
            os.path.join(test_dir, "data", "Dataset", "NCATS-COP01_study_file.txt")
        ]


    def test_load_detect_duplicate(self):
        test_dir = os.path.dirname(os.path.abspath(__file__))
        self.assertRaises(Exception, self.loader.load([os.path.join(test_dir, "data", "COTC007B", "COTC007B-vital_signs.txt")], True, False, 'new', True, 1))


    def test_reload_with_new_and_delete_cohorts(self):
        load_result = self.loader.load(self.file_list_unique, True, False, 'new', True, 1)
        self.assertIsInstance(load_result, dict, msg='Load data failed!')
        self.assertEqual(1832, load_result[NODES_CREATED])
        self.assertEqual(1974, load_result[RELATIONSHIP_CREATED])
        test_dir = os.path.dirname(os.path.abspath(__file__))
        result = self.loader.load([os.path.join(test_dir, 'data', 'Dataset', 'COTC007B-cohort.txt')], True, False, 'delete', False, 1)
        self.assertEqual(result[NODES_DELETED], 18)
        self.assertEqual(result[RELATIONSHIP_DELETED], 101)

    def test_reload_with_new_and_delete_study(self):
        load_result = self.loader.load(self.file_list_unique, True, False, 'new', True, 1)
        self.assertIsInstance(load_result, dict, msg='Load data failed!')
        self.assertEqual(1832, load_result[NODES_CREATED])
        self.assertEqual(1974, load_result[RELATIONSHIP_CREATED])
        test_dir = os.path.dirname(os.path.abspath(__file__))
        result = self.loader.load([os.path.join(test_dir, 'data', 'Dataset', 'COTC007B-study.txt')], True, False, 'delete', False, 1)
        self.assertEqual(result[NODES_DELETED], 1118)
        self.assertEqual(result[RELATIONSHIP_DELETED], 1201)

        result = self.loader.load([os.path.join(test_dir, 'data', 'Dataset', 'NCATS-COP01_study_file.txt')], True, False, 'delete', False, 1)
        self.assertEqual(result[NODES_DELETED], 713)
        self.assertEqual(result[RELATIONSHIP_DELETED], 773)

    def test_reload_with_new_and_delete_program(self):
        load_result = self.loader.load(self.file_list_unique, True, False, 'new', True, 1)
        self.assertIsInstance(load_result, dict, msg='Load data failed!')
        self.assertEqual(1832, load_result[NODES_CREATED])
        self.assertEqual(1974, load_result[RELATIONSHIP_CREATED])
        test_dir = os.path.dirname(os.path.abspath(__file__))
        result = self.loader.load([os.path.join(test_dir, 'data', 'Dataset', 'COP-program.txt')], True, False, 'delete', False, 1)
        self.assertEqual(result[NODES_DELETED], 1832)
        self.assertEqual(result[RELATIONSHIP_DELETED], 1974)


    def test_reload_upsert(self):
        load_result = self.loader.load(self.file_list, True, False, 'upsert', True, 1)
        self.assertIsInstance(load_result, dict, msg='Load data failed!')
        self.assertEqual(1832, load_result[NODES_CREATED])
        self.assertEqual(1974, load_result[RELATIONSHIP_CREATED])



if __name__ == '__main__':
    unittest.main()
