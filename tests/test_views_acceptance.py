import os
import unittest
import multiprocessing
import time
from urllib.parse import urlparse

from werkzeug.security import generate_password_hash
from splinter import Browser

# configure your app to use the testing database
os.environ['CONFIG_PATH'] = 'blog.config.TestingConfig'

from blog import app
from blog.database import Base, engine, session, User

class TestViews(unittest.TestCase):
    def setUp(self):
        ''' Test setup '''
        self.browser = Browser('phantomjs')
        
        # set up the tables in the database
        Base.metadata.create_all(engine)
        
        # create an example user
        self.user = User(name = 'Alice', email = 'alice@example.com',
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
        
    def test_login_incorrect(self):
        self.browser.visit('http://127.0.0.1:8080/login')
        self.browser.fill('email', 'bob@example.com')
        self.browser.fill('password', 'test')
        button = self.browser.find_by_css('button[type=submit]')
        button.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/login')
        
    def test_entries_dropdown(self):
        self.browser.visit('http://127.0.0.1:8080')
        dropdown = self.browser.find_by_id('entries').first
        option = dropdown.find_by_text('50')
        option.click()
        self.assertEqual(self.browser.url, 'http://127.0.0.1:8080/page/1?limit=50')

if __name__ == '__main__':
    unittest.main()