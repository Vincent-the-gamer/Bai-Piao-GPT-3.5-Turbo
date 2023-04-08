"""
Author: Vincent-the-gamer
备用计划：由于老接口用不了了，现在只能找个还没有寄掉的接口了。
"""
import time
import requests
# 使用轻量级框架flask实现后端服务
from flask import Flask
from flask import request as req
# 用于解决前端跨域问题
from flask_cors import CORS
# 生成sign
from getSign import get_sign

app = Flask(__name__)
# 解决前端跨域问题
CORS(app, resources=r'/*')

messages = []

"""
编写请求函数
"""
def send_message(content: str):
    global messages
    messages.append(
        {"role": "user", "content": content}
    )

    url = "https://supremes.pro/api/generate"

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Access-Control-Allow-Origin": "*",
        "Connection": "keep-alive",
        "Content-Type": "text/plain;charset=UTF-8",
        "Origin": "https://supremes.pro",
        "Referer": "https://supremes.pro/",
        "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }

    # 生成sign哈希值


    json = {
        "messages": messages,
        "pass": None,
        "time": int(time.time()*1000),   # 13位时间戳
        "sign": get_sign( messages[len(messages) - 1]["content"] )   # 逆向出来的算法哈希值
    }


    try:
        # 发起请求
        response = requests.post(
            url,
            headers=headers,
            json=json
        )

        """
        请求错误
        """
        try:
            return response.json()["error"]["message"]
        except:
            pass

        """
        请求成功，则把最新的message推入数组
        """
        # 这个接口返回的是纯文本
        messages.append(
            {"role": "assistant", "content": response.text}
        )
        return response.text

    # 运行出错则返回错误信息
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

"""
重新生成答案
"""
@app.route("/regenerate", methods=["GET"])
def regenerate():
    global messages
    if len(messages) < 1:
        return "消息为空"
    else:
        # 提取最后一次的用户问题
        last_content = messages[len(messages) - 2]["content"]
        messages = messages[0:-2] # 删除最后两条问答

        # 重新发请求
        return send_message(last_content)

"""
清空上下文
"""
@app.route("/clearContext", methods=["GET"])
def clear_context():
    global messages
    messages = []
    return "已成功清空上下文，目前上下文条数: {}".format( len(messages) )

"""
查看现在有多少条上下文
"""
@app.route("/showContextCount", methods=["GET"])
def show_context_count():
    global messages
    return "当前上下文条数：" + str(len(messages))


if __name__== "__main__":
    app.run(
        host="0.0.0.0",
        port=2333,
        debug=False
    )