#!/usr/bin/env python3
"""
Test instructor evaluation system
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts/instructor'))

from task_generator import TaskGenerator, encode_to_data_uri


class TestTaskGenerator(unittest.TestCase):
    
    def setUp(self):
        templates_path = os.path.join(os.path.dirname(__file__), 
                                     '../../config/task_templates.json')
        self.generator = TaskGenerator(templates_path)
    
    def test_get_available_templates(self):
        templates = self.generator.get_available_templates()
        self.assertIsInstance(templates, list)
        self.assertGreater(len(templates), 0)
        self.assertIn('sum-of-sales', templates)
    
    def test_generate_task_round1(self):
        task = self.generator.generate_task('sum-of-sales', 'test@example.com', round_num=1)
        
        self.assertIn('task_id', task)
        self.assertIn('brief', task)
        self.assertIn('checks', task)
        self.assertIsInstance(task['checks'], list)
        self.assertGreater(len(task['checks']), 0)
    
    def test_generate_task_round2(self):
        task = self.generator.generate_task('sum-of-sales', 'test@example.com', round_num=2)
        
        self.assertIn('task_id', task)
        self.assertIn('brief', task)
        # Round 2 should have different brief
        self.assertIsInstance(task['brief'], str)
    
    def test_generate_seed(self):
        seed1 = self.generator._generate_seed('test@example.com')
        seed2 = self.generator._generate_seed('test@example.com')
        
        # Same email in same hour should generate same seed
        self.assertEqual(seed1, seed2)
        self.assertEqual(len(seed1), 8)
    
    def test_encode_to_data_uri(self):
        content = "Hello, World!"
        uri = encode_to_data_uri(content, 'text/plain')
        
        self.assertTrue(uri.startswith('data:text/plain;base64,'))


class TestStaticChecks(unittest.TestCase):
    
    def test_check_license_format(self):
        from static_checks import check_license
        
        # This would need a real repo URL to test properly
        # For unit testing, we'd mock the requests
        pass


if __name__ == '__main__':
    unittest.main()
