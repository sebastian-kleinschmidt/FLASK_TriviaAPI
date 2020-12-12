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

    def get_all_categories():
        categories = Category.query.all()
        categories = [category.type for category in categories]
        return categories

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after
    completing the TODOs
    '''
    cors = CORS(app, ressources={r"/api/*": {"origins": "*"}})

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    Create an endpoint to handle GET requests
    for all available categories.
    '''

    @app.route('/categories', methods=['GET'])
    def get_categories():
        try:
            categories = jsonify({'categories': get_all_categories()})
            if categories is None:
                assert(404)
            else:
                return categories
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(422)

    @app.route('/categories/<int:category_id>', methods=['GET'])
    def get_category(category_id):
        try:
            category_item = Category.query.filter_by(id=category_id).one_or_none()

            if category_item is None:
                abort(404)
            else:
                return jsonify({'success': True,
                                'id': category_item.id,
                                'type': category_item.type})
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(422)

    '''
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the
    screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions', methods=['GET'])
    def get_question():
        try:
            questions = Question.query.order_by(Question.id).all()
            if questions is None:
                assert(404)
            else:
                formatted_questions = paginate_questions(request, questions)

                return jsonify({'success': True,
                                'questions': formatted_questions,
                                'total_questions': len(questions),
                                'current_category': 0,
                                'categories': get_all_categories()})
        except Exception as error:
            print("\nerror => {}\n".format(error))
            assert(422)

    '''
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will
    be removed. This removal will persist in the database and when you refresh
    the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            if question is None:
                abort(404)

            question.delete()

            questions = Question.query.order_by(Question.id).all()
            formatted_questions = paginate_questions(request, questions)

            return jsonify({'success': True,
                            'questions': formatted_questions,
                            'total_questions': len(questions),
                            'current_category': 0,
                            'categories': get_all_categories()})
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(422)

    '''
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the
    last page of the questions list in the "List" tab.
    '''
    '''
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
                current_selections = paginate_questions(request, questions)

                return jsonify({'success': True,
                                'questions': current_selections,
                                'total_questions': len(current_selections),
                                'current_category': 0,
                                'categories': get_all_categories()})

            else:
                question = Question(question=new_question,
                                    answer=new_answer,
                                    category=new_category,
                                    difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
        except Exception as error:
            print("\nerror => {}\n".format(error))
            abort(422)

    '''
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def get_question_by_category(category_id):
        questions = Question.query.filter(Question.category == category_id+1).order_by(Question.id).all()

        formatted_questions = paginate_questions(request, questions)

        return jsonify({'success': True,
                        'questions': formatted_questions,
                        'total_questions': len(questions),
                        'current_category': category_id,
                        'categories': get_all_categories()})

    '''
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''

    @app.route('/quizzes', methods=['POST'])
    def start_quiz():
        body = request.get_json()
        previous_questions = body.get('previous_questions', None)
        quiz_category = body.get('quiz_category', None)

        if(quiz_category['id'] == 0):
            questions = Question.query.order_by(Question.id).all()
        else:
            questions = Question.query.filter(Question.category == (int(quiz_category['id'])+1)).order_by(Question.id).all()

        # Check if any question exist in category
        if(len(questions) == 0):
            abort(422)

        question_ids = [question.id for question in questions]
        unanswered_question = list(set(question_ids) - set(previous_questions))

        if(len(unanswered_question) != 0):
            question_id = random.choice(unanswered_question)
            question = Question.query.filter(Question.id == question_id).one_or_none()

            return jsonify({'success': True,
                            'question': question.format(),
                            'total_questions': len(questions),
                            'current_category': quiz_category['id'],
                            'categories': get_all_categories()})

    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

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

    @app.errorhandler(500)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
            }), 500

    return app
