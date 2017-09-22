import os

bind = ['127.0.0.1:5000']
worker_class = 'gevent'
workers = 2
pidfile = os.path.join(os.path.dirname(os.getcwd()), "oauth.pid")