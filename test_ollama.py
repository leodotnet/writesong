import requests

OLLAMA_BASE_URL = 'http://localhost:11434/v1'
MODEL_NAME = 'qwen3:4b'  # 或 'qwen3:32b'，根据你实际拉取的模型

prompt = '写一首关于春天的中文歌词'

payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "user", "content": prompt}
    ]
}

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer ollama"  # 必须有，但内容无所谓
}

try:
    response = requests.post(f'{OLLAMA_BASE_URL}/chat/completions', json=payload, headers=headers, timeout=120)
    response.raise_for_status()
    data = response.json()
    print('Ollama返回内容:')
    print(data)
    if 'choices' in data and len(data['choices']) > 0:
        print('\n生成的歌词:')
        print(data['choices'][0]['message']['content'])
    else:
        print('未获取到歌词内容')
except Exception as e:
    print(f'调用Ollama失败: {e}') 