#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2023/2/14 22:21
# @Author : SecretLanguage
"""
    Json API definition
"""

import json, logging, inspect, functools


class APIError(Exception):
    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message
        
class APIValueError(APIError):
    def __int__(self, field, message=''):
        super(APIValueError, self).__init__('value:invalid', field, message)
        

class APIResourceNotFoundError(APIError):
    """
        indicate the resource not found
    """
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)
        

class APIPermissionError(APIError):
    """
        api has no permission
    """
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)