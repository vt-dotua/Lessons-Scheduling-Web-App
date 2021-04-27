"""
The flask application package.
"""

from flask import Flask, session
from flask_session import Session
from flask_mail import Mail, Message
from blinker import signal

app = Flask(__name__)
SESSION_TYPE = 'redis'
app.config['SECRET_KEY'] = 'you-will-never12-guess'
app.config['CSRF_ENABLED'] = True

app.config['MAIL_SERVER'] = 'smtp.ukr.net'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'testboss@ukr.net'
app.config['MAIL_PASSWORD'] = 'mytestuserapp123'

mail = Mail(app)

import schedule_app.views