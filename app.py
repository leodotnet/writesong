import os
from flask import Flask, render_template, redirect, url_for, request, session, flash, jsonify, send_from_directory
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import openai
from models import db, User, Lyrics, LLMConfig, MusicAPIConfig
from functools import wraps
import logging
import requests
import google.generativeai as genai
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 添加静态文件目录
app.static_folder = 'static'

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


def get_active_music_api_config():
    """获取激活的音乐API配置"""
    return MusicAPIConfig.query.filter_by(is_active=True).first()


def generate_suno_lyrics(text):
    llm_config = get_active_llm_config()
    if not llm_config:
        return '未配置LLM服务'

    # 使用配置的系统提示词，如果未配置则使用默认值
    system_prompt_template = llm_config.system_prompt or 'Generate suno-style lyric based on the following description: {prompt}'
    prompt = system_prompt_template.format(prompt=text)
    result = None

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
            genai.configure(api_key=llm_config.api_key)
            model = genai.GenerativeModel(llm_config.model_name)
            # Gemini支持chat和text两种方式
            try:
                chat = model.start_chat()
                response = chat.send_message(prompt)
                result = response.text
            except Exception:
                # fallback to text-only
                response = model.generate_content(prompt)
                result = response.text
        else:
            return '不支持的LLM提供商'
        
        if result is None:
            return 'LLM未返回有效内容'
        
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
        config_id = request.form.get('config_id')
        provider = request.form['provider']
        api_key = request.form.get('api_key')
        base_url = request.form.get('base_url')
        model_name = request.form['model_name']
        system_prompt = request.form.get('system_prompt', 'Generate suno-style lyric based on the following description: {prompt}')
        is_active = bool(request.form.get('is_active'))
        
        if config_id:  # 编辑
            config = LLMConfig.query.get(int(config_id))
            if config:
                config.provider = provider
                if api_key:
                    config.api_key = api_key  # 只有填写才更新
                config.base_url = base_url
                config.model_name = model_name
                config.system_prompt = system_prompt
                config.is_active = is_active
                if is_active:
                    # 只允许一个激活
                    LLMConfig.query.filter(LLMConfig.id != config.id).update({'is_active': False})
                db.session.commit()
                flash('LLM配置已更新')
        else:  # 新增
            if is_active:
                LLMConfig.query.update({'is_active': False})
            config = LLMConfig(
                provider=provider,
                api_key=api_key,
                base_url=base_url,
                model_name=model_name,
                system_prompt=system_prompt,
                is_active=is_active
            )
            db.session.add(config)
            db.session.commit()
            flash('LLM配置已添加')
        return redirect(url_for('admin_llm_config'))
    
    configs = LLMConfig.query.all()
    # 将配置对象转换为字典格式以便JSON序列化
    configs_dict = []
    for config in configs:
        configs_dict.append({
            'id': config.id,
            'provider': config.provider,
            'model_name': config.model_name,
            'base_url': config.base_url,
            'system_prompt': config.system_prompt,
            'is_active': config.is_active
        })
    return render_template('admin/llm_config.html', configs=configs, configs_dict=configs_dict)


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
    lyric = generate_suno_lyrics(prompt)
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
    song_url = request.form.get('song_url')  # 可选参数
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


@app.route('/update_lyric/<int:lyric_id>', methods=['POST'])
@login_required
def update_lyric(lyric_id):
    lyric = Lyrics.query.filter_by(id=lyric_id, user_id=current_user.id).first_or_404()
    
    name = request.form.get('name')
    original_text = request.form.get('original_text')
    suno_lyrics = request.form.get('suno_lyrics')
    
    logger.info(f"[update_lyric] user={current_user.username}, lyric_id={lyric_id}, name={name}")
    
    if not name or not suno_lyrics:
        return jsonify(success=False, error='歌词名称和内容不能为空')
    
    try:
        lyric.name = name
        lyric.original_text = original_text
        lyric.suno_lyrics = suno_lyrics
        db.session.commit()
        logger.info(f"[update_lyric] 更新成功 lyric_id={lyric_id}")
        return jsonify(success=True)
    except Exception as e:
        logger.error(f"[update_lyric] 更新失败: {e}")
        db.session.rollback()
        return jsonify(success=False, error='保存失败，请重试')


@app.route('/generate_song_with_acestep/<int:lyric_id>', methods=['POST'])
@login_required
def generate_song_with_acestep(lyric_id):
    lyric = Lyrics.query.filter_by(id=lyric_id, user_id=current_user.id).first_or_404()
    lyrics_text = request.form.get('lyrics')
    format_type = request.form.get('format', 'mp3')
    prompt = request.form.get('prompt', 'baby, pop, melodic, guitar, drums, bass, keyboard, percussion, 105 BPM, upbeat, groovy, cozy')
    
    logger.info(f"[generate_song_with_acestep] user={current_user.username}, lyric_id={lyric_id}, format={format_type}, prompt={prompt}")
    
    if not lyrics_text:
        return jsonify(success=False, error='缺少歌词内容')
    
    if not prompt:
        return jsonify(success=False, error='缺少音乐风格提示词')
    
    # 获取激活的音乐API配置
    music_config = get_active_music_api_config()
    if not music_config:
        logger.error("[generate_song_with_acestep] 未配置音乐API服务")
        return jsonify(success=False, error='未配置音乐API服务')
    
    logger.info(f"[generate_song_with_acestep] 使用音乐API: {music_config.provider} - {music_config.name} ({music_config.api_url})")
    
    # 处理参考音频文件
    ref_audio_input = None
    if 'ref_audio' in request.files:
        ref_audio_file = request.files['ref_audio']
        if ref_audio_file and ref_audio_file.filename:
            logger.info(f"[generate_song_with_acestep] 收到参考音频文件: {ref_audio_file.filename}")
            
            # 确保uploads目录存在
            uploads_dir = os.path.join(os.getcwd(), 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            
            # 生成唯一的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = os.path.splitext(ref_audio_file.filename)[1]
            ref_filename = f"ref_audio_{lyric_id}_{timestamp}{file_extension}"
            ref_audio_path = os.path.join(uploads_dir, ref_filename)
            
            # 保存上传的文件
            ref_audio_file.save(ref_audio_path)
            ref_audio_input = ref_audio_path
            logger.info(f"[generate_song_with_acestep] 参考音频已保存到: {ref_audio_path}")
    
    try:
        from gradio_client import Client
        import shutil
        
        # 连接到配置的音乐API服务
        client = Client(music_config.api_url)
        
        # 调用AceStep API生成歌曲
        # 处理ref_audio_input参数
        if ref_audio_input and os.path.exists(ref_audio_input):
            # 如果参考音频文件存在，使用handle_file处理
            from gradio_client import handle_file
            ref_audio_param = handle_file(ref_audio_input)
            logger.info(f"[generate_song_with_acestep] 使用参考音频文件: {ref_audio_input}")
        else:
            ref_audio_param = None
            logger.info(f"[generate_song_with_acestep] 未使用参考音频文件")
        
        result = client.predict(
            format=format_type,
            audio_duration=-1,
            prompt=prompt,
            lyrics=lyrics_text,
            infer_step=60,
            guidance_scale=15,
            scheduler_type="euler",
            cfg_type="apg",
            omega_scale=10,
            manual_seeds=None,
            guidance_interval=0.5,
            guidance_interval_decay=0,
            min_guidance_scale=3,
            use_erg_tag=True,
            use_erg_lyric=False,
            use_erg_diffusion=True,
            oss_steps=None,
            guidance_scale_text=0,
            guidance_scale_lyric=0,
            audio2audio_enable=False,
            ref_audio_strength=0.5,
            ref_audio_input=ref_audio_param,
            lora_name_or_path="none",
            lora_weight=1,
            api_name="/__call__"
        )
        
        # 获取生成的音频文件路径
        if result and isinstance(result, (list, tuple)) and len(result) > 0:
            original_song_path = result[0]  # 第一个元素是音频文件路径
            logger.info(f"[generate_song_with_acestep] 生成成功 original_song_path={original_song_path}")
            
            # 确保song目录存在
            song_dir = os.path.join(os.getcwd(), 'song')
            os.makedirs(song_dir, exist_ok=True)
            
            # 生成新的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_extension = format_type.lower()
            filename = f"song_{lyric_id}_{timestamp}.{file_extension}"
            new_song_path = os.path.join(song_dir, filename)
            
            # 复制文件到song目录
            shutil.copy2(original_song_path, new_song_path)
            
            # 设置文件权限为可读
            os.chmod(new_song_path, 0o644)
            
            # 返回相对于web根目录的URL
            song_url = f"/song/{filename}"
            
            logger.info(f"[generate_song_with_acestep] 文件已保存到 {new_song_path}, URL={song_url}")
            return jsonify(success=True, song_url=song_url)
        else:
            logger.error(f"[generate_song_with_acestep] 生成失败，返回结果异常: {result}")
            return jsonify(success=False, error='歌曲生成失败')
            
    except Exception as e:
        logger.error(f"[generate_song_with_acestep] 生成失败: {e}")
        return jsonify(success=False, error=f'歌曲生成失败: {str(e)}')


@app.route('/song/<filename>')
def serve_song(filename):
    """提供song目录下的音频文件访问"""
    import os
    from flask import send_from_directory
    
    song_dir = os.path.join(os.getcwd(), 'song')
    return send_from_directory(song_dir, filename)


@app.route('/uploads/<filename>')
def serve_upload(filename):
    """提供uploads目录下的文件访问"""
    import os
    from flask import send_from_directory
    
    uploads_dir = os.path.join(os.getcwd(), 'uploads')
    return send_from_directory(uploads_dir, filename)

@app.route('/network-status')
def network_status():
    """网络状态检测页面"""
    return render_template('network_status.html')


@app.route('/delete_lyric/<int:lyric_id>', methods=['POST'])
@login_required
def delete_lyric(lyric_id):
    lyric = Lyrics.query.filter_by(id=lyric_id, user_id=current_user.id).first_or_404()
    
    logger.info(f"[delete_lyric] user={current_user.username}, lyric_id={lyric_id}")
    
    try:
        # 如果有关联的音频文件，也删除它
        if lyric.song_url and lyric.song_url.startswith('/song/'):
            import os
            song_filename = lyric.song_url.split('/')[-1]
            song_path = os.path.join(os.getcwd(), 'song', song_filename)
            if os.path.exists(song_path):
                os.remove(song_path)
                logger.info(f"[delete_lyric] 删除音频文件: {song_path}")
        
        # 清理可能存在的参考音频文件
        import os
        import glob
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        if os.path.exists(uploads_dir):
            # 查找与该歌词ID相关的参考音频文件
            pattern = os.path.join(uploads_dir, f"ref_audio_{lyric_id}_*")
            ref_files = glob.glob(pattern)
            for ref_file in ref_files:
                try:
                    os.remove(ref_file)
                    logger.info(f"[delete_lyric] 删除参考音频文件: {ref_file}")
                except Exception as e:
                    logger.warning(f"[delete_lyric] 删除参考音频文件失败: {e}")
        
        # 删除数据库记录
        db.session.delete(lyric)
        db.session.commit()
        
        logger.info(f"[delete_lyric] 删除成功 lyric_id={lyric_id}")
        return jsonify(success=True)
        
    except Exception as e:
        logger.error(f"[delete_lyric] 删除失败: {e}")
        db.session.rollback()
        return jsonify(success=False, error='删除失败，请重试')


@app.route('/admin/music_api_config', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_music_api_config():
    if request.method == 'POST':
        config_id = request.form.get('config_id')
        provider = request.form['provider']
        name = request.form['name']
        api_url = request.form['api_url']
        api_key = request.form.get('api_key')
        is_active = bool(request.form.get('is_active'))
        
        if config_id:  # 编辑
            config = MusicAPIConfig.query.get(int(config_id))
            if config:
                config.provider = provider
                config.name = name
                config.api_url = api_url
                if api_key:
                    config.api_key = api_key  # 只有填写才更新
                config.is_active = is_active
                if is_active:
                    # 只允许一个激活
                    MusicAPIConfig.query.filter(MusicAPIConfig.id != config.id).update({'is_active': False})
                db.session.commit()
                flash('音乐API配置已更新')
        else:  # 新增
            if is_active:
                MusicAPIConfig.query.update({'is_active': False})
            config = MusicAPIConfig(
                provider=provider,
                name=name,
                api_url=api_url,
                api_key=api_key,
                is_active=is_active
            )
            db.session.add(config)
            db.session.commit()
            flash('音乐API配置已添加')
        return redirect(url_for('admin_music_api_config'))
    
    configs = MusicAPIConfig.query.all()
    # 将配置对象转换为字典格式以便JSON序列化
    configs_dict = []
    for config in configs:
        configs_dict.append({
            'id': config.id,
            'provider': config.provider,
            'name': config.name,
            'api_url': config.api_url,
            'is_active': config.is_active
        })
    return render_template('admin/music_api_config.html', configs=configs, configs_dict=configs_dict)


@app.route('/admin/music_api_config/<int:config_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_music_api_config(config_id):
    config = MusicAPIConfig.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()
    return redirect(url_for('admin_music_api_config'))


@app.route('/update_song_url/<int:lyric_id>', methods=['POST'])
@login_required
def update_song_url(lyric_id):
    lyric = Lyrics.query.filter_by(id=lyric_id, user_id=current_user.id).first_or_404()
    song_url = request.form.get('song_url')
    
    logger.info(f"[update_song_url] user={current_user.username}, lyric_id={lyric_id}, song_url={song_url}")
    
    if not song_url:
        return jsonify(success=False, error='缺少歌曲URL')
    
    try:
        lyric.song_url = song_url
        db.session.commit()
        logger.info(f"[update_song_url] 更新成功 lyric_id={lyric_id}")
        return jsonify(success=True)
    except Exception as e:
        logger.error(f"[update_song_url] 更新失败: {e}")
        db.session.rollback()
        return jsonify(success=False, error='保存失败，请重试')


if __name__ == '__main__':
    import argparse
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description='WriteSong - AI歌词与音乐创作平台')
    parser.add_argument('-p', '--port', type=int, default=3027, 
                       help='应用运行端口 (默认: 3027)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='应用运行主机 (默认: 0.0.0.0)')
    parser.add_argument('--debug', action='store_true', default=True,
                       help='启用调试模式 (默认: True)')
    
    # 解析命令行参数
    args = parser.parse_args()
    
    print(f"启动WriteSong应用")
    print(f"主机: {args.host}")
    print(f"端口: {args.port}")
    print(f"调试模式: {args.debug}")
    print("-" * 40)
    
    create_tables()
    app.run(debug=args.debug, host=args.host, port=args.port)
