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
        self.database_path = "postgres://jean:mypassword@{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_all_categories(self):
        res = self.client().get('/api/categories')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_all_questions(self):
        res = self.client().get('/api/questions')
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])

    def test_delete_question_successfully(self):
        new_question = Question(question='Who won Balon Dor?', answer='Ronaldo', category=6, difficulty=3)
        new_question.insert()
        url = f'/api/questions/{new_question.id}/delete'
        res = self.client().delete(url)
        data = json.loads(res.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['deleted question'])

    def test_delete_question_out_of_bounds(self):
        question_id = 10000
        url = f'/api/questions/{question_id}/delete'
        res = self.client().delete(url)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)

    def test_get_question_by_category(self):
        url = '/api/categories/2/questions'
        res = self.client().get(url)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)

    def test_get_question_by_search_term(self):
        new_question = Question(question='Who won Balon Dor?', answer='Ronaldo', category=6, difficulty=3)
        new_question.insert()

        url = '/api/questions/search?search=Balon'
        res = self.client().post(url, data=json.dumps({"searchTerm": "Balon"}), content_type='application/json')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_post_a_new_question(self):
        data ={
            'question': 'Who won the Euro in 2000?',
            'answer': 'France',
            'category': 5,
            'difficulty': 3
        }
        data = json.dumps(data)
        url = '/api/questions'

        req = self.client().post(url, data=data, content_type='application/json')
        response_data = json.loads(req.data)

        self.assertEqual(req.status_code, 200)
        self.assertEqual(response_data['success'], True)

    def test_fail_to_process_post(self):
        data ={
            'question': 'Who won the Euro in 2000?',
            'answer': 'France',
            'category': 6,
            'difficulty': 3
        }
        data = json.dumps(data)
        url = '/api/questions/1000'

        req = self.client().post(url, data=data, content_type='application/json')
        response_data = json.loads(req.data)

        self.assertEqual(response_data['success'], False)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
