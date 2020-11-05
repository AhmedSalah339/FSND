import os
import unittest 
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


new_question = {'question':'test question',
                'answer':'test answer',
                'difficulty':1,
                'category':4
                }
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres','123','localhost:5432', self.database_name)
        # self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(len(data['categories']),6)

        

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(len(data['categories']),6)
        self.assertEqual(len(data['currentCategory']),len(data['questions']))
    def test_delete_question(self):
        id = 13
        res = self.client().delete('/questions/'+str(id))
        data = json.loads(res.data)
        deleted_question = Question.query.filter(Question.id==1).all()
        print('deleted_question',deleted_question)
        self.assertEqual(res.status_code,200)
        # question = Question(id=id,question='test',answer='test',category=4,difficulty=1)
        # db.session.add(question)
        self.assertEqual(data['success'],True)
        self.assertEqual(len(deleted_question),0)

    def test_404_delete_question(self):
        res = self.client().delete('/questions/1')
        self.assertEqual(res.status_code,404)
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
    def test_create_question(self):
        res = self.client().post('/questions',json=new_question)
        self.assertEqual(res.status_code,200)
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)
        created_question = Question.query.filter(Question.id==data['created']).all()
        self.assertEqual(len(created_question),1)
        # search test
        res = self.client().post('/questions',json={'searchTerm':'wh'})
        self.assertEqual(res.status_code,200)
        data = json.loads(res.data)
        self.assertEqual(data['success'],True)

    def test_400_create_question(self):
        res = self.client().post('/questions',json={'question':'test question',
                'answer':'test answer',
                'difficulty':1,
                'category':100
                })
        data = json.loads(res.data)
        self.assertEqual(res.status_code,400)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],400)
    def test_get_category_questions(self):
        id = 1
        res = self.client().get('/categories/'+str(id)+'/questions')
        
        self.assertEqual(res.status_code,200)
        data = json.loads(res.data)
        self.assertEqual(len(data['questions']),data['total_questions'])
        for cat in data['current_category']:
            self.assertEqual(cat,id)
    def test_404_get_category_questions(self):
        id = 1000
        res = self.client().get('/categories/'+str(id)+'/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)
    def test_quizzes(self):
        
        res = self.client().post('/quizzes',json={'previous_questions':[12,15]
                                                    ,'quiz_category':{'type':'Science','id':4}})
        self.assertEqual(res.status_code,200)
        data = json.loads(res.data)
        res = self.client().post('/quizzes',json={'previous_questions':[]
                                                    ,'quiz_category':{'type':'click','id':0}})
        self.assertEqual(res.status_code,200)
        data = json.loads(res.data)
        print(data['question'])
    def test_404_quizzes(self):
        res = self.client().post('/quizzes',json={'previous_questions':[12,15]
                                                    ,'quiz_category':{'type':'test','id':1000}})
        self.assertEqual(res.status_code,404)
        data = json.loads(res.data)
        self.assertEqual(data['success'],False)
        self.assertEqual(data['error'],404)


        
        






    


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
