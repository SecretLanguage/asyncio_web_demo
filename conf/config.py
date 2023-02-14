#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time : 2023/2/14 22:46
# @Author : SecretLanguage
from conf import config_default, config_override

configs = config_default.configs

try:
    import config_override
    configs = merge(configs, config_override.configs)
except ImportError:
    pass