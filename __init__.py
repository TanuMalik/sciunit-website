import os
from flask import Flask, render_template, request, url_for, redirect


app = Flask(__name__)
@app.route('/')
def reroute_path():
    return redirect('/cb', code=301)

@app.route('/cb')
def default_home():
    """ Render the authorization code for user"""
    code = request.args.get('code')
    return render_template('index.html', code = code)



if __name__ == '__main__':
    PORT = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=PORT)


