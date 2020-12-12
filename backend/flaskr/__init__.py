import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
def paginate_questions(request, selection):
  question_id = request.args.get('page', 1, type=int)
  start_id = (question_id-1)*QUESTIONS_PER_PAGE
  end_id = question_id*QUESTIONS_PER_PAGE
  formatted_questions = [question.format() for question in selection]
  return formatted_questions[start_id:end_id]

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  cors = CORS(app, ressources={r"/api/*": {"origins": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories/<int:category_id>', methods=['GET'])
  def get_categories(category_id):
    category_item = Category.query.filter_by(id=category_id).one_or_none()

    if category_item == None:
      abort(404)
    else:
      return jsonify({'id': category_item.id,
                      'type': category_item.type})

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
  @app.route('/questions', methods=['GET'])
  def get_question():
    questions = Question.query.order_by(Question.id).all()
    formatted_questions = paginate_questions(request, questions)

    return jsonify({'success': True,
                    'questions': formatted_questions,
                    'total_questions': len(questions),
                    'current category': 0, #Todo
                    'categories': 0}) #Todo

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try: 
      question = Question.query.filter(Question.id == question_id).one_or_none()
      if question is None:
        abort(404)
            
      question.delete()
      print("Delete Success")
      questions = Question.query.order_by(Question.id).all()
      formatted_questions = paginate_questions(request, questions)

      return jsonify({'success': True,
                      'questions': formatted_questions,
                      'total_questions': len(questions),
                      'current category': 0, #Todo
                      'categories': 0}) #Todo
    except Exception as error:
      print("\nerror => {}\n".format(error))
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

  @app.route('/questions', methods=['POST'])
  def create_question():
      body = request.get_json()
      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      new_difficulty = body.get('difficulty', None)

      try: 
          question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
          question.insert()
          
          selection = Question.query.order_by(Question.id).all()
          current_books = paginate_questions(request, selection)
          
          return jsonify({
              'success': True,
              'created': question.id,
              'books': current_books,
              'total_books': len(Question.query.all())
          })
      except Exception as error: 
          print("\nerror => {}\n".format(error)) 
          abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''


  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

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
          "message": "Not found"
          }), 404


  @app.errorhandler(422)
  def not_found(error):
      return jsonify({
          "success": False, 
          "error": 422,
          "message": "Unprocessable Entity"
          }), 422
  
  return app

    