from flask import Flask, render_template, url_for, request, session, redirect, flash
from app import app
from flask import Flask
from flask import Flask, jsonify, request
from flask_pymongo import pymongo
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, FileField, BooleanField
from wtforms.validators import InputRequired
import requests


app.config['JSON_SORT_KEYS'] = False
CONNECTION_STRING = "mongodb+srv://dima:berryjuice09@hope-db-nqwaw.mongodb.net/test?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('hope-db')

class addForm(FlaskForm):
    question = StringField('Question', validators=[InputRequired()])
    subtext = TextAreaField('Subtext', validators=[InputRequired()])
    mcc = BooleanField('Merkel Cell Carcinoma')
    scc = BooleanField('Squamous Cell Carcinoma')
    bcc = BooleanField('Basal Cell Carcinoma')
    mel = BooleanField('Melanoma')
    imgFile = FileField('Upload a reference image so patients know what to look for (.jpg, .png, .jpeg)')

class AssessForm(FlaskForm):
    fullname = StringField('Full Name', validators=[InputRequired()])
    govID = StringField('Government ID', validators=[InputRequired()])

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

@app.route('/')
@app.route('/index', methods=['GET','POST'])
def index():
    pageType = 'index'

    if request.method == 'POST':
        session['userGovID'] = request.form['govID']
        session['user'] = request.form['fullname']

        return redirect(url_for('assessment'))

    form = AssessForm()
    return render_template('index.html', pageType = pageType, form=form)


@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    pageType = 'login'

    if request.method == 'POST':
        admins = db.admins
        login_user = admins.find_one({'email': request.form['email']})

        if login_user:
            if request.form['password'] == login_user['password']:
                session['admin'] = request.form['email']
                return redirect(url_for('dashboard'))
            else:
                flash('Incorrect email/password')
                return redirect(url_for('login'))

    return render_template('login.html', pageType = pageType, form=form)
    

@app.route('/dashboard')
def dashboard():
    pageType = 'dashboard'
    if 'admin' in session:
        return render_template('dashboard.html', pageType = pageType, loggedEmail = session['admin'])
    return 'You are not logged in!'

@app.route('/assessment', methods=['GET','POST'])
def assessment():
    pageType = 'assessment'
    if 'user' in session:
        return render_template('assessment.html', pageType = pageType, loggedUser = session['user'])
    return 'You are not logged in!'


@app.route('/addquestion', methods=['GET','POST'])
def addquestion():
    form = addForm()
    pageType = 'addquestion'
    url = 'http://127.0.0.1:5000/postquestions'

    if request.method == 'POST':
        questions = db.questions

        newQuestion = {'question': request.form['question'], 'subtext': request.form['subtext'],
                           'symptomOf': request.form.getlist('symptom'), 'refImg': request.form['imgFile']}

        resp = requests.post(url, json = newQuestion)
        flash('Successfully added question to database')
    
    return render_template('addquestion.html', pageType = pageType, form=form)


@app.route('/updatequestions')
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

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('admin', None)
   return redirect(url_for('login'))

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

