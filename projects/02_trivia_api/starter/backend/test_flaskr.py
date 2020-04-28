import os
import unittest
import json
import random
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client()
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after each test"""
        pass

    def runTest(self):
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_categories(self):
        # get all the available categories
        url = '/categories/'
        response = self.client.get(url)
        assert response.status_code == 200
        # print(url, response.get_json())

    def test_create_categories(self):
        url = '/categories/'
        dataset = [dict(type=12122)]*10
        # I'm using the same ugly data here and creating copies of the same object # noqa
        # please update this list with something meaningful
        for data in dataset:
            response = self.client.post(url, data=data)
            assert response.status_code == 200
            # print(response.get_json())

    def test_add_question(self):
        url = '/questions/'
        dataset = [dict(question=2, answer=1, category=12,
                        difficulty=12)]*10
        # I'm using the same ugly data here and creating copies of the same object # noqa
        # please update this list with something meaningful
        for data in dataset:
            response = self.client.post(url, data=data)
            assert response.status_code == 200
            # print(url, response.get_json())

    def test_get_query_questions(self, query=random.randint(0, 1)):
        url = f'/questions/search?searchTerm=2&page=2' if query else '/questions/'  # noqa
        response = self.client.get(url)
        assert response.status_code == 200
        # print(url, response.get_json())

    def test_delete_question(self, id=random.randint(1, 10)):
        url = f'/questions/{id}'
        response = self.client.delete(url)
        assert response.status_code in [200, 404]
        # print(url, response.get_json())

    def test_get_categories(self, id=random.randint(1, 10)):
        url = f'/categories/2/questions'
        response = self.client.get(url)
        assert response.status_code == 200
        # print(url, response.get_json())

    def test_game(self):
        url = '/quizzes/?quiz_category=2&previous_questions=2'
        response = self.client.get(url)
        assert response.status_code == 200
        # print(url, response.get_json())


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
