"""
Author: Vincent-the-gamer
备用计划2：由于老接口用不了了，现在只能找个还没有寄掉的接口了。

PS: 这个接口的免费版不支持上下文对话
"""
import requests
# 使用轻量级框架flask实现后端服务
from flask import Flask
from flask import request as req
# 用于解决前端跨域问题
from flask_cors import CORS

app = Flask(__name__)
# 解决前端跨域问题
CORS(app, resources=r'/*')

messages = []

"""
编写请求函数
"""
def send_message(content: str):
    global messages
    messages = [
        {"role": "user", "content": content}
    ]

    url = "https://chatapi.javaex.cn/chat/789"

    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Host": "chatapi.javaex.cn",
        "Origin": "https://chat.javaex.cn",
        "Referer": "https://chat.javaex.cn/",
        "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    json = {
        "pkey": None,
        "questions": messages
    }


    try:
        # 发起请求
        response = requests.post(
            url,
            headers=headers,
            json=json
        )

        """
        请求成功
        """
        res_message_obj = response.json()["data"]["choices"][0]["message"]
        return res_message_obj["content"]

    # 出错则返回错误信息
    except Exception as err:
        # 清空上下文
        messages = []
        return str(err)

'''
聊天请求接口
'''
@app.route("/", methods=["POST"])
def bai_piao_chatGPT():
    content = req.json.get("content")
    return send_message(content)


if __name__== "__main__":
    app.run(
        host="0.0.0.0",
        port=2334,
        debug=False
    )