from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)
socketio = SocketIO(app, async_mode='threading')

online_users = set()

online_users = set()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    return render_template('index.html', nickname=user.nickname)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')
        user = User(nickname=nickname, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        password = request.form['password']
        user = User.query.filter_by(nickname=nickname).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

@socketio.on('connect')
def handle_connect():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        online_users.add(user.nickname)
        emit('user list', list(online_users), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        online_users.discard(user.nickname)
        emit('user list', list(online_users), broadcast=True)

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
<<<<<<< HEAD
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
=======
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
>>>>>>> dad9887 (Готовый чат с авторизацией и списком онлайн)
