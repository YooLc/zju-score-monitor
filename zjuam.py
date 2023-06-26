import requests
import re


def printhtml(content, n):
    with open(f"temp{n}.html", mode="w") as f:
        f.write(content)

# https://www.cc98.org/topic/5339540
def rsa_encrypt(password, modulus, exponent):
    password_int = int.from_bytes(bytes(password, 'ascii'), 'big')
    exp = int(exponent, 16)
    mod = int(modulus, 16)
    result = pow(password_int, exp, mod)
    return hex(result)[2:]

class login:
    def __init__(self, username, password):
        url = 'https://zjuam.zju.edu.cn/cas/login?service=http%3A%2F%2Fappservice.zju.edu.cn%2F'
        get_pubkey_url = 'https://zjuam.zju.edu.cn/cas/v2/getPubKey'

        self.session = requests.session()
        res1 = self.session.get(url)
        pubkey = self.session.get(get_pubkey_url)

        execution = re.search('name="execution" value="(.*?)"', res1.text).group(1)
        modulus = pubkey.json()["modulus"]
        exponent = pubkey.json()["exponent"]
        encrypted_password = rsa_encrypt(password, modulus, exponent)

        # https://blog.csdn.net/yang_wen_wu/article/details/108040216
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58',
        }
        data = {
            'username': username,
            'password': encrypted_password,
            '_eventId': 'submit',
            'execution': execution,
            'authcode': '',
        }
        res_login = self.session.post(url, data = data, headers = headers)
        self.content = res_login.text
        self.logger()

    def logger(self):
        if "用户名或密码错误" in self.content:
            print("用户名或密码错误")