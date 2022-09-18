import os
from urllib import parse
from dotenv import load_dotenv
load_dotenv()  # loading enviromental variable from .env files

# Getting Credentials from Enviromental Variables
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')

username = parse.quote_plus(DB_USERNAME)
password = parse.quote_plus(DB_PASSWORD)

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'abbb40056543548c8943091625840810ed1fb643e80e7422941ccce8aa7abe64'

    # Flask-MongoEngine settings
    MONGODB_SETTINGS = {
        'db': 'the_new_system',
        'host': 'mongodb://{}:{}@cluster0-shard-00-00.xwjgf.mongodb.net:27017,cluster0-shard-00-01.xwjgf.mongodb.net:27017,cluster0-shard-00-02.xwjgf.mongodb.net:27017/the_new_system?ssl=true&replicaSet=atlas-81cn45-shard-0&authSource=admin&retryWrites=true&w=majority'.format(username, password)
    }

    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USE_TLS = False
    MAIL_USERNAME = 'everprint.system@gmail.com'
    MAIL_PASSWORD = 'jgbwslnyzcsbkugi'
    MAIL_DEFAULT_SENDER = '"INVESTORS SYSTEM" <noreply@everprint_new_system.com>'

    # Flask-User settings
    USER_APP_NAME = "INVESTORS SYSTEM"      # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = True      # Enable email authentication
    USER_ENABLE_USERNAME = False    # Disable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True    # Simplify register form if set to False
    USER_ENABLE_INVITE_USER = True
    USER_CORPORATION_NAME = "VINCITORI"
    USER_COPYRIGHT_YEAR = 2022
    USER_REQUIRE_INVITATION  = True # Only invited users may register.
