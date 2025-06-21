import os
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import openai
from models import db, User, Lyrics, LLMConfig
from functools import wraps
import logging
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('需要管理员权限')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_active_llm_config():
    # 优先用session中选中的LLM
    llm_id = session.get('llm_id')
    if llm_id:
        config = LLMConfig.query.filter_by(id=llm_id).first()
        if config:
            return config
    return LLMConfig.query.filter_by(is_active=True).first()


def generate_suno_lyrics(text):
    llm_config = get_active_llm_config()
    if not llm_config:
        return '未配置LLM服务'

    # 统一OpenAI格式prompt
    prompt = text

    try:
        if llm_config.provider == 'openai':
            openai.api_key = llm_config.api_key
            resp = openai.ChatCompletion.create(
                model=llm_config.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            result = resp['choices'][0]['message']['content']
        elif llm_config.provider == 'ollama':
            base_url = llm_config.base_url.rstrip('/') if llm_config.base_url else 'http://localhost:11434/v1'
            payload = {
                "model": llm_config.model_name,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer ollama"
            }
            response = requests.post(f'{base_url}/chat/completions', json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                result = data['choices'][0]['message']['content']
            else:
                return 'Ollama未返回歌词内容'
        elif llm_config.provider == 'gemini':
            # 实现Gemini API调用
            pass
        else:
            return '不支持的LLM提供商'
        
        # 处理<think>标签，只保留</think>后的内容
        if '<think>' in result and '</think>' in result:
            think_end = result.find('</think>')
            if think_end != -1:
                result = result[think_end + 8:].strip()  # 8是'</think>'的长度
        
        return result
    except Exception as e:
        return f"生成歌词时出错: {e}"


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
            flash('用户名已存在')
            return redirect(url_for('signup'))
        hashed = generate_password_hash(password)
        # 第一个注册的用户自动成为管理员
        is_admin = User.query.count() == 0
        user = User(username=username, password=hashed, is_admin=is_admin)
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


@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@app.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user.id != current_user.id:  # 不能修改自己的管理员状态
        user.is_admin = not user.is_admin
        db.session.commit()
    return redirect(url_for('admin_users'))


@app.route('/admin/llm_config', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_llm_config():
    if request.method == 'POST':
        provider = request.form['provider']
        api_key = request.form.get('api_key')
        base_url = request.form.get('base_url')
        model_name = request.form['model_name']
        
        # 停用所有现有配置
        LLMConfig.query.update({'is_active': False})
        
        config = LLMConfig(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            is_active=True
        )
        db.session.add(config)
        db.session.commit()
        flash('LLM配置已更新')
        return redirect(url_for('admin_llm_config'))
    
    configs = LLMConfig.query.all()
    return render_template('admin/llm_config.html', configs=configs)


@app.route('/admin/llm_config/<int:config_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_llm_config(config_id):
    config = LLMConfig.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()
    return redirect(url_for('admin_llm_config'))


@app.route('/generate_lyric', methods=['POST'])
@login_required
def generate_lyric_api():
    prompt = request.form.get('prompt')
    logger.info(f"[generate_lyric] user={current_user.username}, prompt={prompt}")
    if not prompt:
        logger.warning("[generate_lyric] 缺少提示词")
        return jsonify(success=False, error='缺少提示词')
    system_prompt = f"Generate suno-style lyric based on the following description:{prompt}"
    lyric = generate_suno_lyrics(system_prompt)
    logger.info(f"[generate_lyric] result={lyric}")
    if lyric:
        return jsonify(success=True, lyric=lyric)
    else:
        return jsonify(success=False, error='歌词生成失败')


@app.route('/generate_music', methods=['POST'])
@login_required
def generate_music_api():
    lyric = request.form.get('lyric')
    logger.info(f"[generate_music] user={current_user.username}, lyric={lyric}")
    if not lyric:
        logger.warning("[generate_music] 缺少歌词内容")
        return jsonify(success=False, error='缺少歌词内容')
    song_url = generate_song(lyric)
    logger.info(f"[generate_music] song_url={song_url}")
    if song_url:
        return jsonify(success=True, song_url=song_url)
    else:
        return jsonify(success=False, error='音乐生成失败')


@app.route('/save_song', methods=['POST'])
@login_required
def save_song_api():
    lyric_name = request.form.get('lyric_name', '未命名歌词')
    lyric = request.form.get('lyric')
    song_url = request.form.get('song_url')
    logger.info(f"[save_song] user={current_user.username}, lyric_name={lyric_name}, lyric={lyric}, song_url={song_url}")
    if not lyric:
        logger.warning("[save_song] 缺少歌词内容")
        return jsonify(success=False, error='缺少歌词内容')
    new_lyric = Lyrics(
        user_id=current_user.id, 
        name=lyric_name,
        original_text=lyric, 
        suno_lyrics=lyric, 
        song_url=song_url
    )
    db.session.add(new_lyric)
    db.session.commit()
    logger.info(f"[save_song] 保存成功 user_id={current_user.id}")
    return jsonify(success=True)


@app.route('/llm_status')
@login_required
def llm_status():
    from models import LLMConfig
    configs = LLMConfig.query.all()
    current_id = session.get('llm_id')
    active = None
    if current_id:
        active = LLMConfig.query.filter_by(id=current_id).first()
    if not active:
        active = LLMConfig.query.filter_by(is_active=True).first()
    logger.info(f"[llm_status] user={current_user.username}, active={active}")
    return jsonify(success=True,
                   provider=active.provider if active else None,
                   model_name=active.model_name if active else None,
                   llms=[{'id':c.id,'provider':c.provider,'model_name':c.model_name} for c in configs],
                   current_id=active.id if active else None)


@app.route('/set_llm', methods=['POST'])
@login_required
def set_llm():
    llm_id = request.form.get('llm_id')
    from models import LLMConfig
    config = LLMConfig.query.filter_by(id=llm_id).first()
    logger.info(f"[set_llm] user={current_user.username}, llm_id={llm_id}, config={config}")
    if config:
        session['llm_id'] = config.id
        return jsonify(success=True)
    else:
        logger.warning(f"[set_llm] 无效的LLM配置 llm_id={llm_id}")
        return jsonify(success=False, error='无效的LLM配置')


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
