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
# 用于解决前端跨域问题
from flask_cors import CORS

app = Flask(__name__)
# 解决前端跨域问题
CORS(app, resources=r'/*')


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

"""
全局消息数组
"""
messages = [
  {"role": "system", "content": "请以markdown的形式返回答案"}
]

"""
全局API_Key
"""
api_key = "FCDECIR0HM1R0B5FO4"


"""
全局请求头
"""
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN",
    "Access-Control-Allow-Origin": "*",
    "Connection": "keep-alive",
    "Content-Type": "application/json",
    "Host": "api.aigcfun.com",
    "sec-ch-ua": '"Not?A_Brand";v="8", "Chromium";v="108"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "cross-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ai-edu/0.0.2 Chrome/108.0.5359.215 Electron/22.3.5 Safari/537.36",
    "x-f-platform": "win32"
}

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
'''
def send_message(content: str):
    global messages
    messages.append(
        {"role": "user", "content": content}
    )

    # 计算消息数组总tokenLength
    token_length = cal_total_tokenLength(messages)

    global api_key
    url = "https://api.aigcfun.com/api/v1/text?key={}".format(api_key)
    print("当前API Key: " + api_key)

    global headers

    json = {
        "messages": messages,
        "model": "gpt-3.5-turbo",
        "tokensLength": token_length
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
        response_json = response.json()

        # 当前的API Key已经到达上限时，重新请求
        if not "message" in response_json["choices"][0]:
            messages = [
                {"role": "system", "content": "请以markdown的形式返回答案"}
            ]
            # 请求新的API Key
            request_api_key()
            return "该API Key达到了使用上限，正在生成新的API Key，请过一会儿重新提问~"


        res_message_obj = response_json["choices"][0]["message"]
        messages.append(res_message_obj)
        return res_message_obj["content"]

    # 出错则返回错误信息
    except Exception as err:
        # 清空上下文
        messages = [
            {"role": "system", "content": "请以markdown的形式返回答案"}
        ]
        return str(err)


"""
请求新的API Key
"""
def request_api_key():
    url = "https://api.aigcfun.com/fc/key"

    global headers

    # 发起请求
    response = requests.get(
        url,
        headers=headers
    )

    """
    请求成功，重新赋值api_key
    """
    global api_key
    api_key = response.json()["data"]
    print("新API Key:" + api_key)
    # 验证api_key
    verify_key(api_key)

"""
验证key
"""
def verify_key(api_key: str):
    url = "https://api.aigcfun.com/fc/verify-key?key={}".format(api_key)
    global headers

    # 发起请求
    requests.get(
        url,
        headers=headers
    )


"""
发送消息
"""
@app.route("/", methods=["POST"])
def bai_piao_chatgpt():
    content = req.json.get("content")
    return send_message(content)


"""
清空上下文
"""
@app.route("/clearContext", methods=["GET"])
def clear_context():
    global messages
    messages = [
        {"role": "system", "content": "请以markdown的形式返回答案"}
    ]
    return "已成功清空上下文，目前上下文条数: {}".format( len(messages) )


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