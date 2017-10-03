from flask import Flask, url_for, request, render_template, abort
from flask_mail import Mail, Message
import os


app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '93eb3942ae0e1f'
app.config['MAIL_PASSWORD'] = '65e58901acaab7'
mail = Mail(app)


@app.route("/")
def homepage():
    return app.send_static_file('index.html')


@app.route('/download/')
def downloadpage():
    return app.send_static_file('download.html')


@app.route('/docs/')
def docspage():
    return app.send_static_file('docs.html')


@app.route('/papers/')
def paperspage():
    return app.send_static_file('papers.html')


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
    return app.send_static_file('support.html')


@app.route('/cb')
def default_home():
    """ Render the authorization code for user"""
    code = request.args.get('code')
    return render_template('oauth.html', code=code)
