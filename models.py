from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    lyrics = db.relationship('Lyrics', backref='owner', lazy=True)


class Lyrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, default='未命名歌词')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    original_text = db.Column(db.Text, nullable=False)
    suno_lyrics = db.Column(db.Text)
    song_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class LLMConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(20), nullable=False)  # 'openai', 'ollama', 'gemini'
    api_key = db.Column(db.String(200))  # For OpenAI and Gemini
    base_url = db.Column(db.String(200))  # For Ollama
    model_name = db.Column(db.String(100))  # Model name for each provider
    system_prompt = db.Column(db.Text, default="Generate suno-style lyric based on the following description:")  # System prompt for lyric generation
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())


class MusicAPIConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(20), nullable=False)  # 'acestep', 'suno', etc.
    name = db.Column(db.String(100), nullable=False)  # 配置名称
    api_url = db.Column(db.String(200), nullable=False)  # API服务地址
    api_key = db.Column(db.String(200))  # API密钥（如果需要）
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
