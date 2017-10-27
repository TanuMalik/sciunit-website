from flask import Flask, url_for, request, render_template, abort,make_response
from flask_mail import Mail, Message
from zlib import adler32
import os
import json


app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '93eb3942ae0e1f'
app.config['MAIL_PASSWORD'] = '65e58901acaab7'
mail = Mail(app)
pages = []

for filename in os.listdir("./templates"):
    if filename != 'base.html':
        pages.append(filename)
    
    print(pages)


def addEtagCaching(resp, filename):
    resp.set_etag(etag_for(os.path.join('templates', filename)))
    resp.headers['Expires'] = 'Thu, 14 Jan 2018 00:00:00 GMT'
    return resp

def etag_for(filename):
    st = os.stat(filename)
    return 'flask-%s-%s-%s' % (st.st_mtime, st.st_size, 
            adler32(os.path.abspath(filename)) & 0xffffffff)

@app.route("/")
def homepage():
    filename="index.html"
    with open('./json/team.json') as team_data:
        json_team = json.load(team_data)
    response = make_response(render_template(filename,team=json_team))
    return addEtagCaching(response, filename)




@app.route('/install/')
def downloadpage():
    filename="install.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response, filename)


@app.route('/docs/')
def docspage():
    filename="docs.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response, filename)


@app.route('/papers/')
def paperspage():
    filename="papers.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response, filename)


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
    filename="support.html"
    response = make_response(render_template(filename))
    return addEtagCaching(response, filename)
    


@app.route('/cb')
def default_home():
    """ Render the authorization code for user"""
    filename="cb.html"
    response = make_response(render_template(filename,code=request.args.get('code')))
    return addEtagCaching(response, filename)