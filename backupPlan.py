"""
Author: Vincent-the-gamer
备用计划：由于老接口用不了了，现在只能找个还没有寄掉的接口了。
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
    messages.append(
        {"role": "user", "content": content}
    )

    url = "https://chatgpt-api.shn.hk/v1"

    headers = {
        "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0",
        "Cache-Control": "no-cache",
        "content-type": "application/json",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }

    json = {
        "model": "gpt-3.5-turbo",
        "messages": messages
    }

    # 发起请求
    response = requests.post(
        url,
        headers=headers,
        json=json
    )

    try:
        """
        请求成功，则把最新的message推入数组
        """
        res_message_obj = response.json()["choices"][0]["message"]
        messages.append(res_message_obj)
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
        port=2334,
        debug=False
    )