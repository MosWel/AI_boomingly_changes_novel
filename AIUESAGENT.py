# AIUESAGENT.py

# 导入所需库
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown
import os

# 环境参数
key="f10f8ab6-dda5-4649-8698-2e214297a34f"
url="https://ark.cn-beijing.volces.com/api/v3"
model="doubao-1-5-pro-32k-character-250715"

# 创建智能体类，实现与OpenAI模型的交互
class AIUESAgent:
    def __init__(self, api_key=key, base_url=url):
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.console = Console()
        self.markdown = Markdown
        self.model = model

    def get_response(self, prompt, system_prompt='', temperature=0.7, max_tokens=2048):
        '''
        输入提示词获取模型回复
        :param prompt: 用户输入的提示词
        :param system_prompt: 系统提示词
        :param temperature: 生成文本的随机性
        :param max_tokens: 最大生成长度
        :return: 模型生成的回复文本
        '''
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content