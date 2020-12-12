import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432',
                                                       self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'Who is the president elect?',
            'answer': 'Joe Biden',
            'category': 1,
            'difficulty': 1
        }

        self.new_invalid_question = {
            'question': 'Who is the president elect?',
            'category': 1,
            'difficulty': 1
        }

        self.start_quiz = {
            'previous_questions': [],
            'quiz_category': {'id': 1,
                              'type': 'science'}
        }

        self.invalid_start_quiz = {
            'previous_questions': []
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for
    successful operation and for expected errors.
    """
    # test retrive categories
    def test_get_existing_category_details(self):
        res = self.client().get('/categories/1')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['id'])
        self.assertTrue(data['type'])

    def test_get_non_existing_category_details(self):
        res = self.client().get('/categories/99999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # test question endpoint
    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))

    # test question endpoint
    def test_get_invalid_questions_page(self):
        res = self.client().get('/questions?page=999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)

    # Test delete existing question endpoint
    def test_delete_existing_question(self):
        res = self.client().delete('/questions/2')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 2).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(question, None)

    # Test delete existing question endpoint
    def test_delete_non_existing_question(self):
        res = self.client().delete('/questions/99999')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # Test post question endpoint
    def test_post_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['created'])

    def test_post_invalid_question(self):
        res = self.client().post('/questions', json=self.new_invalid_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

    # test categories question endpoint
    def test_get_questions_for_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))

    # test categories question endpoint for non existing category
    def test_get_questions_for_nonexisting_category(self):
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # test quiz
    def test_get_questions_for_quiz(self):
        res = self.client().post('/quizzes', json=self.start_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['question']))
        self.assertTrue(data['total_questions'])

    def test_invalid_get_questions_for_quiz(self):
        res = self.client().post('/quizzes', json=self.invalid_start_quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
