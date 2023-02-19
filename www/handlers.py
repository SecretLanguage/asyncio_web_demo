#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2023/2/14 22:20
# @Author : SecretLanguage
import re, time, json, logging, hashlib, base64, asyncio

from coroweb import get, post
from apis import APIError, APIValueError, APIPermissionError, APIResourceNotFoundError
from aiohttp import web

from models import User, Comment, Blog, next_id
from config_default import configs


COOKIE_NAME = 'awesession'
_COOKIE_KEY = configs['session']['secret']

def check_admin(request):
    if request.__user__ is None or not request.__user__.admin:
        raise APIPermissionError()


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


def user2cookie(user, max_age):
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, _COOKIE_KEY)
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


@asyncio.coroutine
def cookie2user(cookie_str):
    '''
    Parse cookie and load user if cookie is valid.
    '''
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = yield from User.find(uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, _COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


@get('/')
async def index(request):
    users = await User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }


@get('/b')
async def get_b(request):
    return {
        '__template__': 'test_b.html'
    }

@get('/blogs')
def blogs(request):
    summary = 'This is a blogs web system.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time()-120),
        Blog(id='2', name='New Title Demo', summary=summary, created_at=time.time()-360),
        Blog(id='3', name='Learn Python Base', summary=summary, created_at=time.time()-1200),
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

@get('/blog/{id}')
def get_blog(id):
    blog = yield from Blog.find(id)
    comments = yield from Comment.findAll('blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments
    }


@get('/register')
def register():
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }

@get('/signin')
def signin():
    return {
        '__template': 'signin.html'
    }


@get('/signout')
def signout(request):
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    r.set_cookie(COOKIE_NAME, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


@get('/manage/blogs')
def manage_blogs(*args, page='1'):
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }

@get('/manage/blogs/create')
def manage_create_blog():
    return  {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }

# RE 正则表达式  用户注册Regex
_RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1, 4}$')
_RE_SHAI = re.compile(r'^[0-9a-f]{40}')


# API接口
@get('/api/users')
async def api_get_users():
    """
        获取用户数据 API接口
    :return: None
    """
    users = await User.findAll(orderBy='created_at desc')
    for u in users:
        u.passwd = '******'
    return dict(users=users)


@post('/api/users')
def api_register_user(*args, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHAI.match(passwd):
        raise APIValueError('passwd')
    users = yield from User.findAll('email=?', [email])

    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    shai_passwd = '%s:%s' % (uid, passwd)
    # 用户头像
    user = User(
        id=uid,
        name=name.strip(),
        email=email,
        passwd=hashlib.sha1(shai_passwd.encode('utf-8')).hexdigest(),
        image='#'
    )
    yield from user.save()
    # 存储cookie session
    r = web.Response()
    r.set_cookie(COOKIE_NAME, user2cookie(user, 86600), max_age=86600, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r