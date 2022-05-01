from flask import Flask, render_template, request, redirect

from base62 import base62_decode, base62_encode
import json
import urllib.parse
import mysql.connector


host = 'http://127.0.0.1:5000/'
# host = 'https://alinjiong.ml:8080/'


class db_control():

    def __init__(self) -> None:
        self.db = None
        self.cursor = None

    @classmethod
    def get_db(self):
        # self.db = pymysql.connect(host='db',
        #                           port=3306,
        #                           user='root',
        #                           password='mysql824.',
        #                           db='test',
        #                           )
        # self.cursor = self.db.cursor()
        # return self.db, self.cursor
        config = {
            'user': 'root',
            'password': 'mysql824.',
            'host': 'db',
            'port': '3306',
            'database': 'test'
        }
        self.db = mysql.connector.connect(**config, buffered=True)
        self.cursor = self.db.cursor()
        return self.db, self.cursor

    @classmethod
    def close_db(self):
        self.cursor.close()
        self.db.close()


app = Flask('__name__')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/l2s', methods=['GET'])
def gen_short_url_api():
    long_url = request.args.get('long')
    # 将长链接存入数据库

    try:
        db, cursor = db_control.get_db()
        cursor.execute('insert into urls (url) values ("{}")'.format(long_url))
        db.commit()
    except pymysql.Error:
        raise
    finally:
        db_control.close_db()
    # 获取id
    last_id = cursor.lastrowid
    # 将 id 转化为 62 进制
    encode = base62_encode(last_id)
    short_url = host + encode

    ret = {}
    ret['short'] = short_url
    return json.dumps(ret)


@app.route('/gen_short_url', methods=['POST'])
def gen_short_url():
    long_url = request.form.get('long_url')
    # 将长链接存入数据库

    if len(long_url) == 0:
        return render_template('index.html', short_url=None)

    if long_url.startswith('https://s.weibo.com/weibo?'):
        long_url = urllib.parse.unquote(long_url, encoding='utf-8')

    try:
        db, cursor = db_control.get_db()
        cursor.execute('insert into urls (url) values ("{}")'.format(long_url))
        db.commit()
    except pymysql.Error:
        raise
    finally:
        db_control.close_db()
    # 获取id
    last_id = cursor.lastrowid
    # 将 id 转化为 62 进制
    encode = base62_encode(last_id)
    short_url = host + encode
    return render_template('index.html', short_url=short_url)


@app.route('/<encode_id>')
def redirect_url(encode_id):
    id = base62_decode(encode_id)
    db, cursor = db_control.get_db()
    try:
        cursor.execute('select url from urls where id = {}'.format(id))
        db.commit()
        url = cursor.fetchone()

        res = str(url[0])
        # 微博url含有中文，存入数据库的时候有变化
        if res.startswith('https://s.weibo.com/weibo?'):
            res = urllib.parse.quote(res, safe=";/?:@&=+$,", encoding='utf-8')
        return redirect(res)
    except pymysql.Error:
        raise

    finally:
        db_control.close_db()


if __name__ == '__main__':
    # createapp.run(host='0.0.0.0', port=80)
    app.run(host='0.0.0.0', port=5000, debug=True)
