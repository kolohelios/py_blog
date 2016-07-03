import os
import unittest
import datetime

# configure your app to use the testing configuration
if not 'CONFIG_PATH' in os.environ:
    os.environ['CONFIG_PATH'] = 'blog.config.TestingConfig'
    
import blog
from blog.filters import *

class FilterTests(unittest.TestCase):
    
    def test_markdown_format_emptystring(self):
        formatted = markdown('')
        self.assertEqual(formatted, '')    
        
    def test_markdown_format_none(self):
        with self.assertRaises(TypeError):
            formatted = markdown(None)
    
    def test_markdown(self):
        formatted = markdown('# Test Header\n*bolding*\n1. list item one\n2. list item two')
        marked_up = '<h1>Test Header</h1>\n<p><em>bolding</em></p>\n<ol>\n<li>list item one</li>\n<li>list item two</li>\n</ol>\n'
        self.assertEqual(formatted, marked_up)
            
if __name__ == '__main__':
    unittest.main()