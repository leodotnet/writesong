#!/bin/bash

# WriteSong 服务启动脚本
# 作者: AI Assistant
# 描述: 自动安装依赖、设置环境变量并启动Flask服务

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python是否安装
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    print_success "Python3 已安装: $(python3 --version)"
}

# 检查pip是否安装
check_pip() {
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 未安装，请先安装pip3"
        exit 1
    fi
    print_success "pip3 已安装: $(pip3 --version)"
}

# 创建虚拟环境
create_venv() {
    if [ ! -d "venv" ]; then
        print_info "创建虚拟环境..."
        python3 -m venv venv
        print_success "虚拟环境创建成功"
    else
        print_info "虚拟环境已存在"
    fi
}

# 激活虚拟环境
activate_venv() {
    print_info "激活虚拟环境..."
    source venv/bin/activate
    print_success "虚拟环境已激活"
}

# 安装依赖
install_dependencies() {
    print_info "安装Python依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "依赖安装完成"
}

# 设置环境变量
setup_env() {
    print_info "设置环境变量..."
    
    # 检查是否已有SECRET_KEY
    if [ -z "$SECRET_KEY" ]; then
        export SECRET_KEY="devsecret_$(date +%s)"
        print_warning "未设置SECRET_KEY，使用临时密钥: $SECRET_KEY"
    else
        print_success "SECRET_KEY 已设置"
    fi
    
    # 检查OpenAI API Key
    if [ -z "$OPENAI_API_KEY" ]; then
        print_warning "未设置OPENAI_API_KEY，某些功能可能无法正常工作"
        print_info "请运行: export OPENAI_API_KEY=your_key_here"
    else
        print_success "OPENAI_API_KEY 已设置"
    fi
    
    # 设置Flask环境
    export FLASK_APP=app.py
    export FLASK_ENV=development
    print_success "Flask环境变量已设置"
}

# 检查端口是否被占用
check_port() {
    local port=${1:-5000}
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        print_warning "端口 $port 已被占用"
        read -p "是否使用其他端口? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            read -p "请输入端口号: " new_port
            export FLASK_RUN_PORT=$new_port
            print_info "将使用端口: $new_port"
        else
            print_error "请先停止占用端口 $port 的服务"
            exit 1
        fi
    else
        print_success "端口 $port 可用"
    fi
}

# 启动服务
start_service() {
    print_info "启动WriteSong服务..."
    print_info "服务将在 http://localhost:${FLASK_RUN_PORT:-5000} 启动"
    print_info "按 Ctrl+C 停止服务"
    echo
    
    # 启动Flask应用
    python app.py
}

# 主函数
main() {
    echo "========================================"
    echo "    WriteSong 服务启动脚本"
    echo "========================================"
    echo
    
    # 检查系统要求
    check_python
    check_pip
    
    # 创建并激活虚拟环境
    create_venv
    activate_venv
    
    # 安装依赖
    install_dependencies
    
    # 设置环境变量
    setup_env
    
    # 检查端口
    check_port
    
    # 启动服务
    start_service
}

# 清理函数
cleanup() {
    print_info "正在停止服务..."
    # 这里可以添加清理代码
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 运行主函数
main "$@" 