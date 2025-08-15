from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv
import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import numpy as np
import csv
import string
import random
from flask_mail import Mail, Message

app = Flask(__name__)
mail = Mail(app)
load_dotenv()

app.secret_key = 'MYSECRETKEY'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT') or 465)
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
mail = Mail(app)
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
  

def create_tables():
    with app.app_context():
        db.create_all()

def generate_random_string(length=10):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def send_mail(subject, recipient, body):
    msg = Message(subject, recipients=[recipient])
    msg.body = body
    mail.send(msg)
    
# Set the path to the directory containing text files
text_files_dir = os.path.join(os.path.dirname(__file__), 'static/prescriptions')

# Set the path to the directory where PDFs will be saved
pdf_output_dir = os.path.join(os.path.dirname(__file__), 'static/pdfs')

# ============================================================ model ============================================================ 


data = pd.read_csv(os.path.join("static","Data", "Training.csv"))
df = pd.DataFrame(data)
cols = df.columns
cols = cols[:-1]
x = df[cols]
y = df['prognosis']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.33, random_state=42)

dt = DecisionTreeClassifier()
clf_dt=dt.fit(x_train,y_train)

indices = [i for i in range(132)]
symptoms = df.columns.values[:-1]

dictionary = dict(zip(symptoms,indices))

def predict(symptom):
    user_input_symptoms = symptom
    user_input_label = [0 for i in range(132)]
    for i in user_input_symptoms:
        idx = dictionary[i]
        user_input_label[idx] = 1

    user_input_label = np.array(user_input_label)
    user_input_label = user_input_label.reshape((-1, 1)).transpose()

    predicted_disease = dt.predict(user_input_label)[0]
    confidence_score = np.max(dt.predict_proba(user_input_label)) * 100  # Assuming decision tree has predict_proba method

    return predicted_disease, confidence_score

with open('static/Data/Testing.csv', newline='') as f:
        reader = csv.reader(f)
        symptoms = next(reader)
        symptoms = symptoms[:len(symptoms)-1]
        
# ============================================================ routes ============================================================ 

@app.route('/', methods=['GET', 'POST'])
def index():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('patient-dashboard.html', username=username)
            
    return render_template('index.html')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        Email = user.email 
        return render_template('patient-profile.html', username=username,Email=Email)
    return render_template('index')

@app.route('/patient-register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        try:
            user = User(username=username, email=email, password=password)
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return redirect(url_for('index'))
        except IntegrityError:
            db.session.rollback()
            flash('Username already exists. Please choose a different username.', 'error')

    return render_template('patient-register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Wrong username or password. Please try again.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/policy')
def policy():
    return render_template('privacy-policy.html')

@app.route('/Transforming_Healthcare')
def Transforming_Healthcare():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Transforming Healthcare.html',username=username)
    return render_template('index.html')

@app.route('/Holistic_Health')
def Holistic_Health():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Holistic Health.html',username=username)
    return render_template('index.html')

@app.route('/Nourishing_Body')
def Nourishing_Body():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Nourishing_Body.html',username=username)
    return render_template('index.html')

@app.route('/Importance_of_Games')
def Importance_of_Games():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('blog_Importance_of_Games.html',username=username)
    return render_template('index.html')

@app.route('/admin')
def admin():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('admin.html',username=username)
    return render_template('index.html')

@app.route('/videocall')
def videocall():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('videocall.html',username=username)
    
    return render_template('index.html')

@app.route('/mentalhealth', methods=['GET', 'POST'])
def mentalhealth():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('mentalhealth.html',username=username)
    else:
        return render_template('index.html')

# ============================================================ scans ============================================================ 
    
@app.route('/braintumor', methods=['GET', 'POST'])
def braintumor():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('brain-tumor.html',username=username)
    else:
        return render_template('index.html')
    

@app.route('/disease_predict', methods=['GET', 'POST'])
def disease_predict():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        chart_data={}
        if request.method == 'POST':
            selected_symptoms = []
            if(request.form['Symptom1']!="") and (request.form['Symptom1'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom1'])
            if(request.form['Symptom2']!="") and (request.form['Symptom2'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom2'])
            if(request.form['Symptom3']!="") and (request.form['Symptom3'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom3'])
            if(request.form['Symptom4']!="") and (request.form['Symptom4'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom4'])
            if(request.form['Symptom5']!="") and (request.form['Symptom5'] not in selected_symptoms):
                selected_symptoms.append(request.form['Symptom5'])
            disease, confidence_score = predict(selected_symptoms)
            
            chart_data = {
            'disease': disease,
            'confidence_score': confidence_score
            }
            return render_template('disease_predict.html',symptoms=symptoms,disease=disease, chart_data=chart_data,confidence_score=confidence_score,username=username)
            
        return render_template('disease_predict.html',symptoms=symptoms,username=username,chart_data=chart_data)
    else:
        return render_template('index.html')

@app.route('/lung', methods=['GET', 'POST'])
def lung():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('lung.html',username=username)
    else:
        return render_template('index.html')

@app.route('/cataract', methods=['GET', 'POST'])
def cataract():
    username = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        username = user.username
        return render_template('cataract.html',username=username)
    else:
        return render_template('index.html')

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)


