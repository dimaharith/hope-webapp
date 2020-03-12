from flask import render_template
from app import app
from flask import Flask
from flask import Flask, jsonify, request
from flask_pymongo import pymongo
from flask_restful import Resource, Api
from flask_cors import CORS
import requests


app.config['JSON_SORT_KEYS'] = False
CONNECTION_STRING = "mongodb+srv://dima:berryjuice09@hope-db-nqwaw.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('hope-db')

class loginForm(FlaskForm):


@app.route('/')
@app.route('/index')
def index():
    pageType = 'index'
    return render_template('index.html', pageType = pageType )


@app.route('/login')
def login():
    pageType = 'login'
    return render_template('login.html', pageType = pageType )

@app.route('/dashboard')
def dashboard():
    pageType = 'dashboard'
    r = requests.get('http://127.0.0.1:5000/users/dima@gmail.com').json()
    fullname = {'firstname': r.get('result').get('firstname'), 'lastname' : r.get('result').get('lastname')}
    return render_template('dashboard.html', pageType = pageType)

@app.route('/add')
def addquestion():
    pageType = 'addquestion'
    return render_template('addquestion.html', pageType = pageType)

@app.route('/update')
def editquestion():
    pageType = 'editquestion'
    return render_template('editquestion.html', pageType = pageType)

@app.route('/questions')
def questions():
    pageType = 'questions'
    return render_template('questions.html', pageType = pageType)

@app.route('/diagnosis')
def diagnosis():
    pageType = 'diagnosis'
    return render_template('diagnosis.html', pageType = pageType)

@app.route('/assessment')
def assessment():
    pageType = 'assessment'
    return render_template('assessment.html', pageType = pageType)

#==== API CODE ====
@app.route('/admins/<email>', methods=['GET'])
def get_a_user(email):
    admins = db.admins

    q = admins.find_one({'email': email})

    if q:
        output = {'email': q['email'], 'password': q['password']}
    else:
        output = 'No results found'

    return jsonify({'result': output})

#GET all assessments
@app.route('/getassessments', methods=['GET'])
def get_all_assessments():
    assessments = db.assessments

    output = []

    for q in assessments.find():
        output.append({'fullname': q['fullname'], 'govID': q['govID'],
                       'diagnosis': q['diagnosis'], 'conf': q['conf']})

    return jsonify({'result': output})

#POST a new assessment
@app.route('/postassessments', methods=['POST'])
def add_assessment():
    assessments = db.assessments

    fullname = request.json['fullname']
    govID = request.json['govID']
    diagnosis = request.json['diagnosis']
    conf = request.json['conf']

    a_id = assessments.insert({'fullname': fullname, 'govID': govID,
                            'diagnosis': diagnosis, 'conf': conf})
    new_a = assessments.find_one({'_id': a_id})

    output = {'fullname': new_a['fullname'], 'govID': new_a['govID'],
              'diagnosis': new_a['diagnosis'], 'conf': new_a['conf']}

    return jsonify({'result': output})

#GET all questions
@app.route('/getquestions', methods=['GET'])
def get_all_questions():
    questions = db.questions

    output = []

    for q in questions.find():
        output.append({'question': q['question'], 'subtext': q['subtext'],
                       'symptomOf': q['symptomOf'], 'refImg': q['refImg']})

    return jsonify({'result': output})

#POST a new question
@app.route('/postquestions', methods=['POST'])
def add_question():
    questions = db.questions

    question = request.json['question']
    subtext = request.json['subtext']
    symptomOf = request.json['symptomOf']
    refImg = request.json['refImg']

    q_id = questions.insert({'question': question, 'subtext': subtext,
                            'symptomOf': symptomOf, 'refImg': refImg})
    new_q = questions.find_one({'_id': q_id})

    output = {'question': new_q['question'], 'subtext': new_q['subtext'],
              'symptomOf': new_q['symptomOf'], 'refImg': new_q['refImg']}

    return jsonify({'result': output})

#DELETE a question
@app.route('/deletequestions', methods=['DELETE'])
def delete_question():
    questions = db.questions
    question = request.json['question']
    toDelete = { "question": question }

    questions.delete_one(toDelete) 

    return jsonify({'result': 'success'})

#PUT/UPDATE a question
@app.route('/updatequestions', methods=['PUT'])
def update_question():
    questions = db.questions
    question = request.json['question']
    toUpdate = { "question": question }
    
    newQuestion = request.json['newQuestion']
    newSubtext = request.json['subtext']
    newSymptomOf = request.json['symptomOf']
    newRefImg = request.json['refImg']
    newValues = { "$set": {'question': newQuestion, 'subtext': newSubtext,
                            'symptomOf': newSymptomOf, 'refImg': newRefImg} }
    
    questions.update_one(toUpdate, newValues)
    return jsonify({'result': 'success'})

