import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
  
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

  @app.route('/api/categories')
  def get_all_categories():
    all_categories = Category.query.order_by(Category.id).all()
    categories = {category.id : category.type for category in all_categories}

    return jsonify({
      'success': True,
      'categories': categories
    }), 200

  '''
  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/api/questions')
  def get_all_questions():
    '''
    an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions).
    '''
    page = request.args.get('page', 1, int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    selection = Question.query.order_by(Question.id).all()
    questions = [question.format() for question in selection] # making a list using list comprehension
    current_questions = questions[start:end] #list selection

    all_categories = Category.query.order_by(Category.id).all()
    categories = {category.id : category.type for category in all_categories}

    if len(current_questions) == 0:
      abort(404)

    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': categories,
      'current_category': ''
    })

  @app.route('/api/questions/<int:question_id>/delete', methods=['DELETE'])
  def delete_question(question_id):
    '''
    an endpoint to DELETE question using a question ID. 
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      question.delete()

      return jsonify({
          'success': True,
          'deleted question': question.format(),
          'messsage': 'The question has been successfully deleted'

        }), 200
    except:
      abort(404)

  '''
  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/api/questions', methods=['POST'])
  def post_a_new_question():
    '''
    A POST endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.
    '''
    data = request.get_json()
    question = data.get('question', None)
    answer = data.get('answer', None)
    category = data.get('category', None)
    difficulty = data.get('difficulty', None)

    if not(question and answer and category and difficulty):
      abort(400)

    try:
      new_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
      new_question.insert()

      return jsonify({
        'success': True,
        'question': new_question.format(),
        'messsage': 'The new question was successfully created'
      }), 200

    except:
      abort(422)


  '''
  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/api/questions/search', methods=['POST'])
  def get_questions_by_search_term():
    '''
    A POST endpoint to get questions based on a search term. 
    is a substring of the question. 
    '''
    # data = request.get_json()
    # search = data.get('searchTerm')
    search = request.args.get('searchTerm', '', type=str)
    searched_questions = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search))).all()

    searched_results = [result.format() for result in searched_questions]

    return jsonify({
      'success': True,
      'questions': searched_results
    }), 200

  '''
  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/api/categories/<int:category_id>/questions')
  def get_questions_by_category(category_id):
    '''
    a GET endpoint to get questions based on category. 

    '''
    questions_by_category = Question.query.order_by(Question.id).filter(Question.category == category_id).all()

    questions = [question.format() for question in questions_by_category]

    # current_category =  first_question.category

    return jsonify({
      'success': True,
      'questions': questions,
      'total_questions': len(questions),
      'current_category': category_id
    }), 200

  @app.route('/api/questions/quiz', methods=['POST'])
  def play_quiz_questions():
    '''
    a POST endpoint to get random questions to play the quiz. 
    Targs: category and previous question parameters 
    '''
    data = request.get_json()
    previous_questions = data.get("previous_questions")
    category = data.get("quiz_category")
    category_id = int(category["id"])

    question = Question.query.filter(
        Question.id.notin_(previous_questions)
    )

    # if category_id:
    # #so that the question is based on the category
    #     new_question = question.filter_by(category=category_id)

    

    # new_question = question.first().format()

    # return jsonify({
    #   'question': new_question,
    #   'success': True
    # })
    if category_id:
      new_question = question.filter_by(category=category_id)
      new_question_based_on_category = new_question.first().format()

      return jsonify({
        'question': new_question_based_on_category,
        'success': True
      })
    else:
      new_question = question.first().format()

      return jsonify({
      'question': new_question,
      'success': True
    })
  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
      return jsonify({
          'success': False,
          'error': 404,
          'message': "Not found"
      }), 404

  @app.errorhandler(422)
  def unprocessable(error):
      return jsonify({
          'success': False,
          'error': 422,
          'message': "Unprocessable"
      }), 422

  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          'success': False,
          'error': 400,
          'message': "bad request"
      }), 400
  
  return app
