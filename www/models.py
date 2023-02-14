#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2023/2/14 11:23
# @Author : SecretLanguage
from www.orm import Model, String, Integer

class User(Model):
    __table__ = 'users'

    id = Integer(primary_key=True)
    name = String()