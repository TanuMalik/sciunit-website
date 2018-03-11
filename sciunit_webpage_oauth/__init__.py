from __future__ import absolute_import

from flask import Flask
from flask import request, render_template, make_response, send_from_directory
from flask_mail import Mail, Message
from werkzeug.exceptions import HTTPException
import hashlib
import os
from . import team


app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '93eb3942ae0e1f'
app.config['MAIL_PASSWORD'] = '65e58901acaab7'
mail = Mail(app)
pages = []


def addEtagCaching(resp):
    if not resp.is_streamed:
        etag = etag_for(resp.data)
        if (etag in request.if_none_match):
            raise NotModified
        resp.set_etag(etag)
    return resp


def etag_for(data):
    return hashlib.sha1(data).hexdigest()


class NotModified(HTTPException):
    code = 304


@app.route("/")
def homepage():
    filename = "index.html"
    response = make_response(render_template(filename, team=team.data))
    return addEtagCaching(response)


@app.route('/install/')
def downloadpage():
    filename = "install.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response)


@app.route('/docs/')
def docspage():
    filename = "docs.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response)


@app.route('/papers/')
def paperspage():
    filename = "papers.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response)


@app.route('/papers/<fn>')
def papershosting(fn):
    uploads = os.path.join(os.path.dirname(__file__), 'uploads')
    return send_from_directory(uploads, fn)


@app.route('/support/', methods=['GET', 'POST'])
def supportpage():
    if request.method == 'POST':
        name = request.form['name']
        user_email = request.form['email']
        subject = request.form['subject']
        message = 'A message from %s\nMessage: %s' % (
            name, request.form['message'])
        email_msg = Message(
            subject=subject, sender=user_email,
            recipients=['jack.m.gman@gmail.com'],
            body=message,
            reply_to=user_email)
        mail.send(email_msg)
    filename = "support.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response)


@app.route('/cb')
def default_home():
    """ Render the authorization code for user"""
    filename = "cb.html"
    response = make_response(render_template(filename,
                                             code=request.args.get('code')))
    return addEtagCaching(response)
