# WriteSong Windows 安装和使用指南

## 系统要求

- Windows 10/11
- Python 3.8 或更高版本
- 至少 2GB 可用内存
- 至少 500MB 可用磁盘空间

## 快速开始

### 方法一：使用简单启动脚本（推荐新手）

1. 双击运行 `start.bat`
2. 脚本会自动：
   - 检查Python环境
   - 创建虚拟环境
   - 安装依赖
   - 运行数据库迁移
   - 启动应用（端口3027）

3. 打开浏览器访问：http://localhost:3027

### 方法二：使用高级启动脚本

1. 双击运行 `start_advanced.bat` 使用默认设置
2. 或者命令行运行：
   ```cmd
   start_advanced.bat 8080 127.0.0.1
   ```
   这将启动应用在端口8080，只允许本地访问

## 手动安装步骤

如果自动脚本出现问题，可以手动执行以下步骤：

### 1. 安装Python

1. 访问 https://www.python.org/downloads/
2. 下载并安装Python 3.8+
3. 确保勾选"Add Python to PATH"

### 2. 创建虚拟环境

```cmd
python -m venv venv
```

### 3. 激活虚拟环境

```cmd
venv\Scripts\activate
```

### 4. 安装依赖

```cmd
pip install -r requirements.txt
```

### 5. 运行数据库迁移

```cmd
python migrate_db.py
python migrate_music_api.py
```

### 6. 启动应用

```cmd
python app.py
```

## 常见问题

### Q: 提示"python不是内部或外部命令"
A: 请确保Python已正确安装并添加到系统PATH

### Q: 端口被占用
A: 使用高级启动脚本指定其他端口：
```cmd
start_advanced.bat 8080
```

### Q: 虚拟环境创建失败
A: 确保有足够的磁盘空间和权限

### Q: 依赖安装失败
A: 尝试更新pip：
```cmd
python -m pip install --upgrade pip
```

## 功能说明

### 默认配置
- 端口：3027
- 主机：0.0.0.0（允许外部访问）
- 数据库：SQLite（自动创建）

### 管理员账户
- 第一个注册的用户自动成为管理员
- 管理员可以配置LLM和音乐API

### 文件存储
- 音频文件存储在 `song/` 目录
- 数据库文件存储在 `instance/` 目录

## 停止应用

在命令行窗口中按 `Ctrl+C` 停止应用

## 技术支持

如遇到问题，请检查：
1. Python版本是否符合要求
2. 网络连接是否正常
3. 防火墙是否阻止了端口访问
4. 相关服务（如AceStep）是否已启动 