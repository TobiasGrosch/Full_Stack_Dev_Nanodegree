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
        self.database_name = "trivia-test"
        self.database_path = "postgresql://postgres:postgres@localhost:5432/{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

        self.new_question = {
            'question': 'Test-Question',
            'answer': 'Test-Answer',
            'difficulty': 2,
            'category': 5,
            'id': 5
        }

        self.new_wrong_question = {
            'question': 'Test-Question',
            'answer': 'Test-Answer',
            'difficulty': 'wrong data type',
            'category': 5
        }

        self.quizz_request = {
            'previous_questions': [],
            'quiz_category': {'id':1, 'type': 'Science'}
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass
    
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_questions(self):
        res = self.client().get('/questions')
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])
        self.assertEqual(data['current_category'], None)

    def test_404_get_questions_above_limit(self):
        res = self.client().get('/questions?page=1000')
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found, Client error')

    def test_post_questions(self):
        res = self.client().post('/questions', json=self.new_question)
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['question'], 'Test-Question')
        self.assertEqual(data['answer'], 'Test-Answer')
        self.assertEqual(data['category'], 5)
        self.assertEqual(data['difficulty'], 2)

    def test_post_questions_error(self):
        res = self.client().post('/questions', json=self.new_wrong_question)
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request, Client Error')


    def test_delete_questions(self):
        selected = Question.query.order_by(self.db.desc(Question.id)).limit(1)
        selected_id = [id.format() for id in selected]
        dict = selected_id[0]
        delete_id = dict['id'] 
        param = {'id' : delete_id}

        res = self.client().delete('/questions/{id}'.format(**param))
        data  = json.loads(res.data)

        question = Question.query.filter(Question.id == 5).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], delete_id)
        self.assertEqual(question, None)

    def test_404_delete_questions_above_limit(self):
        res = self.client().delete('/questions/1000')
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found, Client error')

    def test_post_search(self):
        res = self.client().post('/questions/search', json={'searchTerm': "test"})
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)

    def test_get_questions_based_on_categories(self):
        res = self.client().get('/categories/1/questions')
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 1)

    def test_404_get_questions_based_on_categories_wrong_category(self):
        res = self.client().get('/categories/10/questions')
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found, Client error')

    def test_405_get_questions_based_on_categories(self):
        res = self.client().post('/categories/1/questions', json=self.new_question)
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_post_quizzes(self):
        res = self.client().post('/quizzes', json=self.quizz_request)
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_post_quizzes(self):
        res = self.client().post('/quizzes')
        data  = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'request unprocessable')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()