import os
import sys
import time
import shutil
import hashlib
import random
from subprocess import Popen, STDOUT
import sqlite3
if sys.version_info[0] == 3:
    import _thread
    try:
        from queue import PriorityQueue as Queue
    except ImportError:
        from queue import Queue

else:
    import thread as _thread
    try:
        from Queue import PriorityQueue as Queue
    except ImportError:
        from Queue import Queue

import smtplib
import re
from string import Template
# try:
#     from queue import PriorityQueue as Queue
# except ImportError:
#     from queue import Queue

POOL_PATH = 'upload'
DATABASE = 'mzpool.db'
KEEP_TIME = 48


def mkdir_p(path):
    try:
        path = os.path.expanduser(path)
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


class Job(object):
    def __init__(self, cmd, email=None):
        self.cmd = cmd
        self.email = email if email else ''
        self.id = md5('%s-%s' % (cmd, random.random()))
        self.path = pathof(self.id)
        if os.path.exists(self.path):
            raise Error("Job collision")
        mkdir_p(self.path)
        self.fsizes = []

    def __hash__(self):
        return self.id

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, *excinfo):
        self.close()

    def run(self):
        # enforce line buffer
        self.log = open(self.pathof('output.log'), 'w', 1)
        self.proc = Popen(self.cmd, cwd=self.path,
                          stdout=self.log, stderr=None)
        self.stime = time.time()
        return self.proc

    def close(self):
        if self.started:
            self.proc.wait()
            self.ftime = time.time()
            self.log.close()
        else:
            pathclean(self.path)

    @property
    def started(self):
        return hasattr(self, 'proc')

    @property
    def priority(self):
        # TODO: it should match the computaional time
        return sum(self.fsizes) * len(self.fsizes) ** 0.5

    def __cmp__(self, other):
        return cmp(self.priority, other.priority)

    def pathof(self, *subdir):
        return pathof(self.id, *subdir)


class Pool(object):
    __shared_state = {}

    def __sql(self, sql, *args):
        return self.__db.execute(sql, args)

    def __init__(self):
        self.__dict__ = self.__shared_state
        self.__pool = {}
        self.__sync = set()

    # shared by multiply threads
    def checkin(self, job):
        if job.id in self.__pool:
            raise Error("ID collision")
        self.__pool[job.id] = job

    # single _thread, interruptible, lock-free
    def sync(self):
        for k, mj in self.__pool.items():
            if mj.started \
                    and mj.proc.returncode is not None \
                    and mj.id not in self.__sync:
                self.__sql('''insert or replace into Job values
                              (?, ?, ?, ?, ?, ?)''',
                           mj.id, mj.path, sum(mj.fsizes),
                           mj.stime, mj.ftime, mj.proc.returncode)
                self.__sync.add(mj.id)
        for k, path, status in self.__sql(
                '''select id, path, status from Job
                   where now() - ftime >= ? and status >= 0''',
                KEEP_TIME * 3600):
            pathclean(path)
            self.__sync.discard(k)
            if status == 0:
                # status = -1 means succeed and expired
                self.__sql('''update Job set status = -1 where id = ?''', k)
            else:
                self.__sql('''delete from Job where id = ?''', k)
            if k in self.__pool:
                del self.__pool[k]
        self.__conn.commit()

    # run every %interval hours
    def start(self, interval=1.0):
        self.__conn = sqlite3.connect(DATABASE, check_same_thread=0)
        self.__conn.create_function('now', 0, time.time)
        self.__db = self.__conn.cursor()
        self.__sql('''
        create table if not exists Job (
                id TEXT PRIMARY KEY,
              path TEXT NOT NULL,
             dsize INTEGER NOT NULL,
             stime REAL NOT NULL,
             ftime REAL NOT NULL,
            status INTEGER
        )''')

        def _run():
            while 1:
                time.sleep(interval * 3600)
                self.sync()
        return _thread.start_new_thread(_run, ())

    def __len__(self):
        return len(self.__pool)

    def __getitem__(self, jid):
        return self.__pool[jid]

    def __contains__(self, item):
        if type(item) == str:
            return item in self.__pool
        else:
            return item.id in self.__pool

    def __iter__(self):
        return self.__pool.itervalues()

    def close(self):
        self.sync()
        self.__conn.commit()
        self.__conn.close()


class Error(Exception):
    pass


class Mailer(object):
    def __init__(self, host='localhost', port=0,
                 user='', password=None, encrypt='no'):
        if not user:
            raise smtplib.SMTPException('SMTP user not specified')
        self.__starttls = encrypt.lower() == 'starttls'
        use_ssl = encrypt.lower() == 'ssl'
        self.__host = host
        self.__port = port or (465 if use_ssl else 25)
        self.__user = user
        self.__pass = password
        try:
            smtplib.SMTP_SSL
        except AttributeError:
            if use_ssl:
                raise SystemError(
                        'SMTP_SSL is not available; try STARTTLS instead.')
            self.__smtp = smtplib.SMTP()
        else:
            self.__smtp = (smtplib.SMTP_SSL if use_ssl
                           else smtplib.SMTP)(timeout=60)

    def connect(self):
        self.__smtp.connect(self.__host, self.__port)
        if self.__starttls:
            self.__smtp.ehlo()
            self.__smtp.starttls()
        self.__smtp.ehlo()
        if not self.__smtp.does_esmtp:
            self.__smtp.helo()
        # empty password still causes login
        if self.__pass is not None:
            self.__smtp.login(self.__user, self.__pass)

    def sendmail(self, mail):
        # it was said that smtplib is not _thread-safe
        with _thread.allocate_lock():
            try:
                # check and reconnect
                self.__smtp.noop()
            except smtplib.SMTPServerDisconnected:
                self.connect()
            self.__smtp.sendmail(mail['From'], mail['To'], str(mail))

    def close(self):
        try:
            if hasattr(self.__smtp, 'sock'):
                self.__smtp.quit()
        except smtplib.SMTPServerDisconnected:
            pass


def md5(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()


def pathof(*subdir):
    return os.path.join(POOL_PATH, *subdir)


def pathclean(path):
    try:
        shutil.rmtree(path)
    except OSError as e:
        if e.errno != os.errno.ENOENT:
            raise


def fsizeof(*subdir):
    return os.stat(pathof(*subdir)).st_size
