import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from collections import OrderedDict
from sqlalchemy.orm import joinedload
import sqlalchemy

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)

  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app)

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  def after_request(func):
    def exec(*args, **kwargs):
      r = func(*args, **kwargs)
      r.headers['Access-Control-Allow'] = '*'
      return r
    return exec

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories/', methods=('GET', 'POST'))
  @after_request
  def categories():
    if request.method == 'POST':
      data = request.form
      t = data.get('type', None)
      if t:
        q = Category(type=t)
        q.insert()
        return jsonify({'result': q.format()})
      abort(404, 'data not correct')
    page = request.args.get('page', '1')
    page = int(page) if page.isdigit() else 1
    queryset = Category.query.paginate(page, QUESTIONS_PER_PAGE, error_out=True)
    results = [category.format() for category in queryset.items]
    return jsonify({'categories': results})

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
  @app.route('/questions/', methods=('GET', ))
  def questions():
    page = request.args.get('page', '1')

    if page.isdigit():
      page = int(page)
    else:
      page = 1
    questions = Question.query.filter().paginate(
        page, QUESTIONS_PER_PAGE, error_out=True)
    categories = [category.format() for category in Category.query.paginate(1, QUESTIONS_PER_PAGE, error_out=True).items]  # noqa

    results = []
    for question in questions.items:
      q = question.format()
      # q['category'] = categories[q['category']-1]['type']
      results.append(q)
    return jsonify(OrderedDict({'count': Question.query.count(),
                                'questions': results,
                                'categories': categories}))

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:pk>', methods=('DELETE',))
  def delete_question(pk):
    q = Question.query.get_or_404(pk)
    if q:
      q.delete()
    return jsonify({'result': 'success'})

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions/', methods=('POST',))
  def add_question():
    data = request.form
    q = data.get('question', None)
    a = data.get('answer', None)
    c = data.get('category', None)
    d = data.get('difficulty', None)
    if all([a, q, c,d]) and (c.isdigit() and d.isdigit()):
      q = Question(question=q, answer=a, category=int(c), difficulty=int(d))
      try:
        q.insert()
        q = q.format()
      except sqlalchemy.exc.IntegrityError:
        q = f'category id {c} doesn\'t exists'
      return jsonify({'result': q})
    return abort(404,'Data is not correct')

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=('GET',))
  def search_question():
    q = request.args.get('searchTerm', None)
    page = request.args.get('page', '1')
    page = int(page) if page.isdigit() else 1
    if not q:
      return jsonify({'results': 'no questions found'})
    qs = Question.query.filter(Question.question.contains(q)).paginate(
        page, QUESTIONS_PER_PAGE, error_out=True)
    results = [question.format() for question in qs.items]
    return jsonify({'questions': results})

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:pk>/questions',  methods=('GET',))
  def cat_questions(pk):
    page = request.args.get('page', '1')
    page = int(page) if page.isdigit() else 1
    qs = Question.query.filter(Question.category== str(pk))
    # qs = Question.query.join(Category, Category.id==Question.category).filter(Category.id == str(pk))
    if qs.count()>0:
      qs = qs.paginate(page, QUESTIONS_PER_PAGE, error_out=True)
    else:
      abort(404)
    results = [question.format() for question in qs.items]
    return jsonify({'categories': results})

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
  @app.route('/quizzes/', methods=('GET', ))
  def game():
    category = request.args.get('quiz_category', None)
    previous = request.args.get('previous_questions', None)
    if not category and not previous:
      msg = {'message': 'category and previous are required parameters'}
      response = jsonify(msg)
      response.status_code = 400
      return response
    if category and category.isdigit():
      qs = Question.query.filter(Question.category == category)
    else:
      qs = Question.query
    if previous:
      previous = list(map(int, previous.split(',')))
      qs = qs.filter(Question.id.notin_(previous))
    count = qs.count()
    if not count:
      abort(404, 'no questions found for the above arguments')
    qidx = random.randint(1, count)-1
    question = qs.all()[qidx].format()
    return jsonify(question)

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def page_not_found(error):
    app.logger.error('Page not found: %s', (request.path))
    response = jsonify({'error': error.description, 'status_code': error.code})
    response.status_code = error.code
    return response

  @app.errorhandler(422)
  def unprocessable_entity(error):
    app.logger.error('Unprocessable Entity: %s', (request.path))
    response = jsonify({'error': error.description, 'status_code': error.code})
    response.status_code = 422
    return response

  return app
