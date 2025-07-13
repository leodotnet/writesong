# WriteSong - AI歌词与音乐创作平台

WriteSong是一个基于Flask的Web应用，让用户能够创作文本，使用AI将其转换为歌词，并生成音乐。用户可以注册、登录，管理自己的歌词作品。

## 功能特性

- 🎵 **AI歌词生成**：支持OpenAI、Ollama、Gemini等多种LLM服务
- 🎼 **音乐生成**：集成AceStep等音乐生成API
- 👤 **用户系统**：注册、登录、个人歌词管理
- 🎨 **歌词编辑**：在线编辑和重新生成歌词
- 🎧 **音乐播放**：在线播放和下载生成的音乐
- ⚙️ **配置管理**：管理员可配置LLM和音乐API服务
- 📱 **响应式设计**：支持桌面和移动设备

## 系统要求

- Python 3.8 或更高版本
- 至少 2GB 可用内存
- 至少 500MB 可用磁盘空间
- 网络连接（用于AI服务调用）

## 快速安装

### 方法一：使用启动脚本（推荐）

#### Windows用户
```cmd
# 下载项目后，双击运行
start.bat

# 或使用高级启动脚本
start_advanced.bat 8080
```

#### Linux/Mac用户
```bash
# 下载项目后，运行
chmod +x start.sh
./start.sh
```

### 方法二：手动安装

1. **克隆或下载项目**
   ```bash
   git clone https://github.com/your-repo/writesong.git
   cd writesong
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   
   # Windows激活
   venv\Scripts\activate
   
   # Linux/Mac激活
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **运行数据库迁移**
   ```bash
   python migrate_db.py
   python migrate_music_api.py
   ```

5. **启动应用**
   ```bash
   python app.py
   ```

6. **访问应用**
   打开浏览器访问：http://localhost:3027

## 配置说明

### 1. LLM服务配置

管理员登录后，进入"管理" → "LLM配置"：

- **OpenAI**：需要API密钥
- **Ollama**：本地部署，需要基础URL
- **Gemini**：需要API密钥

### 2. 音乐API配置

进入"管理" → "音乐API配置"：

- **AceStep**：默认配置 http://127.0.0.1:7865/
- **Suno**：需要配置API地址
- **其他**：支持自定义音乐生成服务

### 3. 环境变量（可选）

```bash
# 设置密钥（可选，也可在管理界面配置）
export SECRET_KEY=your_secret_key
export OPENAI_API_KEY=your_openai_key
```

## 使用指南

### 1. 首次使用
1. 访问应用首页
2. 点击"注册"创建账户
3. 第一个注册的用户自动成为管理员

### 2. 创建歌词
1. 点击"创建歌词"
2. 输入歌词名称和创作灵感
3. 点击"生成歌词"
4. 编辑生成的歌词（可选）
5. 点击"保存"

### 3. 生成音乐
1. 在歌词详情页面点击"生成歌曲"
2. 选择音频格式（MP3/WAV）
3. 输入音乐风格提示词
4. 等待生成完成

### 4. 管理配置（管理员）
1. 配置LLM服务用于歌词生成
2. 配置音乐API用于歌曲生成
3. 管理用户权限

## 项目结构

```
writesong/
├── app.py                 # 主应用文件
├── models.py              # 数据模型
├── requirements.txt       # 依赖列表
├── start.sh              # Linux/Mac启动脚本
├── start.bat             # Windows启动脚本
├── start_advanced.bat    # Windows高级启动脚本
├── migrate_db.py         # 数据库迁移脚本
├── migrate_music_api.py  # 音乐API迁移脚本
├── stub/                 # 测试脚本
│   ├── test_acestep.py   # AceStep测试
│   └── test_ollama.py    # Ollama测试
├── templates/            # 模板文件
├── song/                 # 音频文件存储
└── instance/             # 数据库文件
```

## 常见问题

### Q: 启动时提示端口被占用
A: 使用自定义端口启动：
```bash
python app.py --port 8080
```

### Q: LLM服务连接失败
A: 检查：
- API密钥是否正确
- 网络连接是否正常
- 服务地址是否正确

### Q: 音乐生成失败
A: 检查：
- AceStep服务是否启动
- 音乐API配置是否正确
- 歌词内容是否有效

### Q: 数据库错误
A: 运行迁移脚本：
```bash
python migrate_db.py
python migrate_music_api.py
```

## 开发说明

### 添加新的LLM提供商
1. 在 `models.py` 中添加配置字段
2. 在 `generate_suno_lyrics()` 函数中添加处理逻辑
3. 更新管理界面模板

### 添加新的音乐API
1. 在 `models.py` 中添加音乐API配置
2. 在 `generate_song_with_acestep()` 函数中添加调用逻辑
3. 更新音乐API配置界面

## 技术支持

- **问题反馈**：请提交Issue
- **功能建议**：欢迎Pull Request
- **文档更新**：持续改进中

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

---

**享受AI创作的乐趣！** 🎵✨
