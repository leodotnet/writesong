import os
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import openai
from models import db, User, Lyrics

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def generate_suno_lyrics(text):
    prompt = f"Convert the following text to suno-style song lyrics:\n{text}"
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        return 'OPENAI_API_KEY not configured.'
    openai.api_key = api_key
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return resp['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating lyrics: {e}"


def generate_song(lyrics):
    # Placeholder for API call to convert lyrics to a song
    # Replace with real API call to Suno or other service
    return f"Generated song for lyrics: {lyrics[:30]}..."


def create_tables():
    with app.app_context():
        db.create_all()


@app.route('/')
@login_required
def index():
    lyrics_list = Lyrics.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', lyrics_list=lyrics_list)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('signup'))
        hashed = generate_password_hash(password)
        user = User(username=username, password=hashed)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        text = request.form['text']
        suno = generate_suno_lyrics(text)
        song = generate_song(suno)
        lyric = Lyrics(user_id=current_user.id, original_text=text, suno_lyrics=suno, song_url=song)
        db.session.add(lyric)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create.html')


@app.route('/lyrics/<int:lyric_id>')
@login_required
def lyrics_detail(lyric_id):
    lyric = Lyrics.query.filter_by(id=lyric_id, user_id=current_user.id).first_or_404()
    return render_template('lyrics.html', lyric=lyric)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
