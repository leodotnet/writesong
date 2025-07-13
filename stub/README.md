# Stub 文件夹

这个文件夹包含用于测试和开发的示例脚本。

## 文件说明

### test_acestep.py
- **用途**: 测试AceStep音乐生成API
- **功能**: 演示如何使用gradio_client调用AceStep服务生成音乐
- **依赖**: gradio_client
- **运行**: `python test_acestep.py`

### test_ollama.py
- **用途**: 测试Ollama本地LLM服务
- **功能**: 演示如何调用Ollama API生成歌词
- **依赖**: requests
- **运行**: `python test_ollama.py`

## 使用说明

这些文件主要用于：
1. 开发和调试时测试API连接
2. 验证服务配置是否正确
3. 作为API调用的参考示例

## 注意事项

- 运行前请确保相应的服务已启动
- 根据实际环境修改配置参数
- 这些文件不会影响主应用的运行 