from flask import Flask, url_for, request, make_response, render_template, abort
from flask_mail import Mail, Message
import os
import sys
import mz
import re
if sys.version_info[0] == 3:
    import _thread
else:
    import thread as _thread
import atexit
import subprocess


app = Flask(__name__)
mail = Mail(app)

app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '93eb3942ae0e1f'
app.config['MAIL_PASSWORD'] = '65e58901acaab7'
mail = Mail(app)

jqueue = mz.Queue()
jpool = mz.Pool()
app = Flask(__name__)


def cleanup():
    jqueue.join()
    jpool.close()


@app.before_first_request
def startup():
    atexit.register(cleanup)

    for i in range(os.sysconf('SC_NPROCESSORS_ONLN')):
        _thread.start_new_thread(run_job, ())
    jpool.start(1 if mz.KEEP_TIME > 2.0 else mz.KEEP_TIME / 2.0)


def run_job():
    while 1:
        try:
            # super safe...
            with jqueue.get() as mj:
                # ensure the existence of log and proc
                jpool.checkin(mj)
        except Exception as e:
            app.logger.error('%s: %s' % (e.__class__.__name__, str(e)))
        finally:
            # log the error, don't hang
            jqueue.task_done()

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
        message = 'A message from ' + name + '\nMessage: ' + request.form['message']
        email_msg = Message(subject = subject, sender=user_email,
        	recipients =['jack.m.gman@gmail.com'],
        	body = message,
        	reply_to = user_email)
        mail.send(email_msg)
    return app.send_static_file('support.html')

@app.route('/cb')
def default_home():
    """ Render the authorization code for user"""
    code = request.args.get('code')
    return render_template('oauth.html', code = code)



# if __name__ == '__main__':
#     PORT = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=PORT)


