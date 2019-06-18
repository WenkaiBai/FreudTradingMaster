import json
import requests

class WeChat(object):
    def __init__(self, corpid, secret, agentid):
        self.url = "https://qyapi.weixin.qq.com"
        self.corpid = corpid
        self.secret = secret
        self.agentid = agentid

    # get access_token
    def access_token(self):
        url_arg = '/cgi-bin/gettoken?corpid={id}&corpsecret={crt}'.format(
            id=self.corpid, crt=self.secret)
        url = self.url + url_arg
        response = requests.get(url=url)
        text = response.text
        self.token = json.loads(text)['access_token']

    # construct message
    def messages(self, msg):
        values = {
            "touser": '@all',
            "msgtype": 'text',
            "agentid": self.agentid,
            "text": {'content': msg},
            "safe": 0
        }
        # python 3
        # self.msg = (bytes(json.dumps(values), 'utf-8'))
        # python 2
        self.msg = json.dumps(values)

    # sending message
    def send_message(self, msg):
        self.access_token()
        self.messages(msg)

        send_url = '{url}/cgi-bin/message/send?access_token={token}'.format(
            url=self.url, token=self.token)
        response = requests.post(url=send_url, data=self.msg)
        errcode = json.loads(response.text)['errcode']

        if errcode == 0:
            print('Sending Succesfully')
        else:
            print('Sending Failed')

'''
corpid = "ww2baed54bbccc5f0c"
secret = "7K7XwCgZlj01W0jh7gqiJjvVKaSUOgQbm5rKf1MyJRU"
agentid = "1000002"
msg = "python test"
wechat = WeChat(corpid, secret, agentid)
wechat.send_message(msg)
'''