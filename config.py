# -*- encoding: utf-8 -*-
# --------------------------------------------------------------------------
# Name:			config
# Description:
# Author:			zgd
# Date:				2019-05-05
# --------------------------------------------------------------------------
class Config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1:3306/project_april?charset=utf8'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
