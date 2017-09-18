import os

bind = ['0.0.0.0:5000']
worker_class = 'gevent'
workers = 2
pidfile = os.path.join(os.path.dirname(os.getcwd()), "oauth.pid")