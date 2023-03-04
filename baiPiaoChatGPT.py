"""
通过调用公开版网站的API接口，实现和gpt-3.5-turbo模型的上下文关联对话
Author: Vincent-the-gamer

该模块实现了与模型的上下文关联对话，并且在请求失败时自动清空上下文
该模块必须做成后端服务，否则上下文的持久化需要用到数据库等其它持久化工具辅助
而当你使用了后端服务，只要服务不停止，上下文就可以保留
"""
import requests
import unicodedata
# 使用轻量级框架flask实现后端服务
from flask import Flask
from flask import request as req

app = Flask(__name__)

'''
计算总tokenLength, 用于构造请求体
判断字符是全角还是半角，全角返回2，半角返回1
'''
def cal_token_length(content: str):
    count = 0
    for i in content:
        if unicodedata.east_asian_width(i) == "W":
            count += 2
        else:
            count += 1
    return count

messages = []
'''
遍历所有消息的content，计算tokenLength总值
'''
def cal_total_tokenLength(msg_arr: [dict]):
    all_messages = ""

    if len(msg_arr) > 0:
        for message in msg_arr:
            all_messages += message["content"]
    else:
        raise Exception("消息数组为空！")

    return cal_token_length(all_messages)


'''
编写请求函数
传参：http://host:2333/你要问的问题
'''
@app.route("/", methods=["POST"])
def bai_piao_chatGPT():
    content = req.json.get("content")

    global messages
    messages.append(
        {"role": "user", "content": content}
    )

    # 计算消息数组总tokenLength
    token_length = cal_total_tokenLength(messages)

    url = "http://api.aioschat.com/"
    headers = {
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "Referer": "https://www.aigcfun.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "sec-ch-ua": 'Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
        "sec-ch-ua-platform": "Windows",
        "sec-ch-ua-mobile": "?0",
        "Connection": "keep-alive",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Origin": "https://www.aigcfun.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
    }


    json = {
        "messages": messages,
        "model": "gpt-3.5-turbo",
        "tokensLength": token_length
    }

    # 发起请求
    try:
        session = requests.Session()

        response = session.post(
            url,
            headers=headers,
            json=json
        )

        """
        请求成功，则把最新的message推入数组
        """
        res_message_obj = response.json()["choices"][0]["message"]
        """
        转义特殊字符
        """
        res_message_obj["content"] = res_message_obj["content"]

        messages.append(res_message_obj)

        return res_message_obj["content"]

    except Exception as error:
        """ 发生错误，则清空上下文 """
        messages = []
        raise error


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
    messages = []
    return "当前上下文条数：" + str(len(messages))


if __name__== "__main__":
    app.run(
        host="0.0.0.0",
        port=2333
    )