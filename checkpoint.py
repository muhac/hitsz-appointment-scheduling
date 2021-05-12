import requests

sess = requests.session()
sess.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 '
                                   '(KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'})
response = sess.get('https://www.bugstop.site/checkpoint/')

print(response.json())
print('data force save')
