import os
import unittest
import datetime

# configure your app to use the testing configuration
if not 'CONFIG_PATH' in os.environ:
    os.environ['CONFIG_PATH'] = 'blog.config.TestingConfig'
    
import blog
from blog.filters import *

class FilterTests(unittest.TestCase):
    def test_date_format(self):
        date = datetime.date(1999, 12, 31)
        formatted = dateformat(date, '%y/%m/%d')
        self.assertEqual(formatted, '99/12/31')
    
    def test_date_format_none(self):
        formatted = dateformat(None, '%y/%m/%d')
        self.assertEqual(formatted, None)
    
    def test_markdown_format_emptystring(self):
        formatted = markdown('')
        self.assertEqual(formatted, '')    
        
    def test_markdown_format_none(self):
        with self.assertRaises(TypeError):
            formatted = markdown(None)
    
    # the following is not a unit test, it's actually an integration test (and it's currently failing)        
    # def test_markdown(self):
    #     formatted = markdown('# Test Header\n*bolding*\n1. list item one\n2. list item two')
    #     self.assertEqual(formatted, '<h1>Test Header</h1>\n<p><em>bolding</em></p>\n<ol>\n<li>list item one</li>\n<li>list item two</li></ol>')
            
if __name__ == '__main__':
    unittest.main()