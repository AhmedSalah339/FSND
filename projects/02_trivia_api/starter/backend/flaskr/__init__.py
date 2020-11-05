import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category,db

QUESTIONS_PER_PAGE = 10
# From Udacity class
def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start =  (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Origin','*')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def categories():
    categories = db.session.query(Category).all()
    if len(categories) == 0:
      print('cat not found')
      abort(404)

    cats = {'categories':{}}
    for category in categories:
      cats['categories'][str(category.id)] = category.type
    print(cats)
    return jsonify(cats)

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 



  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def questions():
    categories = db.session.query(Category).all()
    if len(categories) == 0:
      
      abort(404)

    cats = {}
    for category in categories:
      cats[str(category.id)] = category.type

    questions = db.session.query(Question).all()
    current_questions = paginate_questions(request,questions)

    if len(questions) == 0:
      print('questions not found')
      abort(404)
    current_categories = []
    for question in current_questions:
      current_categories.append(question["category"])
    response = {
                    'categories':cats,
                    'currentCategory':current_categories,
                    'questions':current_questions,
                    'total_questions':len(questions)
                    }
    #print(response)


    return jsonify(response)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:id>',methods=['DELETE'])
  def delete_question(id):
    #print('id is',id)
    question_to_be_deleted = Question.query.filter(Question.id==id).first()
    #print('question_to_be_deleted',question_to_be_deleted)
    if not question_to_be_deleted:
      abort(404)
    try:
      question_to_be_deleted.delete()
    
      return jsonify({
        'success':True,
        'deleted_question_id':question_to_be_deleted.id})
    except:
      abort(422)




  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions',methods=['POST'])
  def create_question():
    body = request.get_json()
    searchTerm = body.get('searchTerm',None)
    if searchTerm:
      questions = Question.query.filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
      if len(questions) ==0:
        return jsonify({
        'success':True,
        'questions':[],
        'total_questions':len(questions),
        'current_categories':[]})

      current_questions = [question.format() for question in questions]
      #current_questions = paginate_questions(request,questions)
      current_categories = []
      for question in current_questions:
        current_categories.append(question["category"])
      
      return jsonify({
        'success':True,
        'questions':current_questions,
        'total_questions':len(questions),
        'current_categories':current_categories})



    new_question = body.get('question',None)
    new_answer = body.get('answer',None)
    category = body.get('category',None)
    difficulty = body.get('difficulty',None)
    categories = db.session.query(Category).all()
    cats = [cat.id for cat in categories]

    if len(categories) == 0:
      abort(404)
    if not (new_question and new_answer and category and difficulty):
      abort(400)
    if category not in cats:
      abort(400)
    try:
      
      question = Question(question=new_question,answer=new_answer,
        category=category,difficulty=difficulty)
      db.session.add(question)
      db.session.commit()
      return jsonify(
      {
      'success':True,
      'created':question.id
      }
      )

    except:
      abort(422)


  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:id>/questions')
  def get_category_questions(id):
    cats = db.session.query(Category).all()
    if len(cats) == 0:
      abort(404)

    cats = [cat.id for cat in cats]
    #print('cats',cats)
    if id not in cats:
      abort(404)
    category_questions = Question.query.filter(Question.category==id).all()
    

    if len(category_questions) == 0:
      return jsonify({'questions':[],
                      'total_questions':0,
                      'current_category':[]})
    category_questions = [question.format() for question in category_questions]
    #print('cat question',category_questions)
    current_categories = []
    for question in category_questions:
      current_categories.append(question["category"])

    return jsonify({'questions':category_questions,
                    'total_questions':len(category_questions),
                    'current_category':current_categories})
    


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a tprevious_questionsime is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def quizzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions',None)
    quiz_category = body.get('quiz_category',None)
    print('previous_questions',previous_questions)
    print('quiz_category',quiz_category)
    if  previous_questions is None:
      abort(400)
    if quiz_category['type']!='click':
      print('here')
      cats = db.session.query(Category).all()
      if len(cats) == 0:
        abort(404)
      cats = [cat.id for cat in cats]
      print(cats)
      print(quiz_category['id'])
      if int(quiz_category['id']) not in cats:
        print('bad cat')
        abort(404)
      questions = Question.query.filter(Question.category==int(quiz_category['id'])).all()
    else: 
      questions = Question.query.all()
    if len(questions) == 0:
      print('No Questions')
      abort(404)
    valid_questions = [q for q in questions if q.id not in previous_questions]
    rand_question = random.choice(valid_questions)
    return jsonify({'question':rand_question.format(),
                    'sucess':True
                    })





  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "resource not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False, 
      "error": 422,
      "message": "unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False, 
      "error": 400,
      "message": "bad request"
      }), 400
  
  return app

    
