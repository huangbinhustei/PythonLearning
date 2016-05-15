import requests

url = "http://127.0.0.1:5000/add"
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4,zh-TW;q=0.2',
    'Connection': 'keep-alive',
    'Host': 'www.binbin.com',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
    'Referer': 'https://www.binbin.com/',
}
l_url = "http://127.0.0.1:5000/login"
l_data = {"username": "admin", "password": "admin"}

s = requests.session()

if __name__ == '__main__':
    while 1:
        cmd = input("1 = 登录，2 = 发布页 \n")
        if cmd == "    ":
            break
        if cmd == "1":
            s.post(l_url, headers=headers, data=l_data)
        else:
            s.get(url, headers=headers)