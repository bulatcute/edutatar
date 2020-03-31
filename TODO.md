## отправка комментария учителю

#### копии запроса и ответа

> request

```
POST /facultative/index/21119 HTTP/1.1
Host: edu.tatar.ru
Connection: keep-alive
Content-Length: 156
Cache-Control: max-age=0
Origin: https://edu.tatar.ru
Upgrade-Insecure-Requests: 1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundarynGEbXf7NeG42wtaU
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69
Sec-Fetch-Dest: document
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Referer: https://edu.tatar.ru/facultative/index/21119
Accept-Encoding: gzip, deflate, br
Accept-Language: ru
Cookie: DNSID=3ac0cbde41b01b0dfd1905ae2a31399f98c8e293; HLP=5945503%7C%242y%2410%24FdxStqjvSXwEH85KQ52rB.th%2Fzo31zUhyRtvTHBoudZ27L%2FbPyT8.

------WebKitFormBoundary8YQ9Ps8yr6jIa9pN
Content-Disposition: form-data; name="facultative_comment[text]"

комментарий
------WebKitFormBoundary8YQ9Ps8yr6jIa9pN--
```

> response

```
HTTP/1.1 200 OK
Server: nginx
Date: Sat, 28 Mar 2020 10:46:01 GMT
Content-Type: text/html; charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
Expires: Mon, 26 Jul 1997 05:00:00 GMT
Last-Modified: Sat, 28 Mar 2020 10:46:01 GMT
Cache-Control: no-store, no-cache, must-revalidate
Cache-Control: post-check=0, pre-check=0
Pragma: no-cache
Set-Cookie: DNSID=3ac0cbde41b01b0dfd1905ae2a31399f98c8e293; path=/; samesite=Lax; domain=.edu.tatar.ru; secure; httponly
Content-Encoding: gzip
```

## система входа в edu.tatar

1. вход преводится на странице /login

1. логин и пароль проверяются на валидность

1. логин и пароль проверяются через edu.tatar
    - если пользователь в первый раз заходит под этими данными,
    выполняется его регистрация в базе данных

1. выполняется вход и редирект на главную страницу

[пример системы входа](https://github.com/PrettyPrinted/building_user_login_system/blob/master/finish/app.py)