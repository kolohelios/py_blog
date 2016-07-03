import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# configure your app to use the testing configuration
if not 'CONFIG_PATH' in os.environ:
    os.environ['CONFIG_PATH'] = 'blog.config.TestingConfig'

from blog import app
from blog.database import Base, engine, session, User

'''adding engine disposition and drop_all before setup in case earlier test suite run was interrupted'''
engine.dispose()
Base.metadata.drop_all(engine)

class TestViews(unittest.TestCase):
    def setUp(self):
        ''' Test setup '''
        
        self.browser = Browser('phantomjs')
        
        # if we don't set the window size, we won't be able to interact with UI that might 
        # be hidden because of our media queries with a smaller emulated window
        self.browser.driver.set_window_size(1120, 550)
        
        # set up the tables in the database
        Base.metadata.create_all(engine)
        
        # create an example user
        self.user = User(name = 'Alice', email = 'alice@example.com',
            password = generate_password_hash('test'))
        session.add(self.user)
        session.commit()
        
        # create a second example user
        self.user = User(name = 'Bob', email = 'bob@example.com',
            password = generate_password_hash('test'))
        session.add(self.user)
        session.commit()
        
        self.process = multiprocessing.Process(target = app.run, kwargs = { 'port': 8080 })
        self.process.start()
        time.sleep(1)
        
    def tearDown(self):
        ''' Test teardown '''
        # remove the tables and their data from the database
        self.process.terminate()
        session.close()
        engine.dispose()
        Base.metadata.drop_all(engine)
        self.browser.quit()
        os.system('pgrep phantomjs | xargs kill')
        
    def test_login_correct(self):
        self.browser.visit('http://127.0.0.1:8080/login')
        self.browser.fill('email', 'alice@example.com')
        self.browser.fill('password', 'test')
        button = self.browser.find_by_css('button[type=submit]')
        button.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/')
        self.assertFalse(self.browser.is_element_present_by_css('[href="/login"]'))
        self.assertTrue(self.browser.is_element_present_by_css('[href="/logout"]'))
        self.assertTrue(self.browser.is_element_present_by_css('[href="/entry/add"]'))
        
    def test_login_incorrect(self):
        self.browser.visit('http://127.0.0.1:8080/login')
        self.browser.fill('email', 'cliff@example.com')
        self.browser.fill('password', 'test')
        button = self.browser.find_by_css('button[type=submit]')
        button.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/login')
        self.assertTrue(self.browser.is_element_present_by_css('[href="/login"]'))
        self.assertFalse(self.browser.is_element_present_by_css('[href="/logout"]'))
        self.assertFalse(self.browser.is_element_present_by_css('[href="/entry/add"]'))
        
    def test_entries_dropdown(self):
        self.browser.visit('http://127.0.0.1:8080')
        dropdown = self.browser.find_by_id('entries').first
        option = dropdown.find_by_text('50')
        option.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/page/1?limit=50')

    def test_not_logged_in_user(self):
        self.browser.visit('http://127.0.0.1:8080')
        self.assertTrue(self.browser.is_element_present_by_css('[href="/login"]'))
        self.assertFalse(self.browser.is_element_present_by_css('[href="/logout"]'))
        self.assertFalse(self.browser.is_element_present_by_css('[href="/entry/add"]'))
        
    def test_add_entry_while_not_logged_in_then_log_in_as_other_user_and_try_delete_and_edit(self):
        test_title = 'A New Blog Post'
        test_content = 'This is a test of a new blog post.'
        self.browser.visit('http://127.0.0.1:8080/entry/add')
        self.browser.fill('email', 'alice@example.com')
        self.browser.fill('password', 'test')
        button = self.browser.find_by_css('button[type=submit]')
        button.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/entry/add')
        self.browser.fill('title', test_title)
        self.browser.fill('content', test_content)
        button = self.browser.find_by_css('button[type=submit]')
        button.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/')
        self.assertTrue(self.browser.is_element_present_by_text(test_title))
        self.assertTrue(self.browser.is_element_present_by_text(test_content))
        logout_link = self.browser.find_by_css('[href="/logout"]').first
        logout_link.click()
        self.browser.visit('http://127.0.0.1:8080/logout')
        login_link = self.browser.find_by_css('[href="/login"]').first
        login_link.click()
        self.browser.fill('email', 'bob@example.com')
        self.browser.fill('password', 'test')
        button = self.browser.find_by_css('button[type=submit]')
        button.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/')
        self.browser.visit('http://127.0.0.1:8080/entry/1/delete')
        self.assertTrue(self.browser.is_element_present_by_text('You are not authorized to delete this record.'))
        self.assertFalse(self.browser.is_element_present_by_css('button[type="submit"]'))        
        self.browser.visit('http://127.0.0.1:8080/entry/1/edit')
        self.assertTrue(self.browser.is_element_present_by_text('You are not authorized to edit this record.'))
        self.assertFalse(self.browser.is_element_present_by_css('button[type="submit"]'))  

if __name__ == '__main__':
    unittest.main()