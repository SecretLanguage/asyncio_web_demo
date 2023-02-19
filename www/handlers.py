#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2023/2/14 22:20
# @Author : SecretLanguage
import re, time, json, logging, hashlib, base64, asyncio

from coroweb import get, post

from models import User, Comment, Blog, next_id


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