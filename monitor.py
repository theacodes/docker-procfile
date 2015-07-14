#   Copyright 2015, Google, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys

import psutil
from flask import Flask


# The app checks this file for the PID of the process to monitor.
PID_FILE = None


def get_pid():
    """Reads the process id from the PID file."""
    if not os.path.exists(PID_FILE):
        return False

    with open(PID_FILE, 'r') as pidfile:
        pid = pidfile.read()

    return int(pid)


app = Flask(__name__)


# The health check will see if the worker process is running and report 200
# if it is and 503 otherwise.
@app.route('/_ah/health')
def health():
    pid = get_pid()

    if not pid:
        return 'Worker pid not found', 503

    try:
        proc = psutil.Process(pid)

        if not proc.is_running():
            return 'Worker process exists, but is not running.', 503

    except psutil.NoSuchProcess:
        return 'Worker not running.', 503

    return 'healthy', 200


# The stop handler is called by Google App Engine whenever an instance is going
# to be shut down. This allows this app to signal the worker to attempt to shut
# down gracefully.
@app.route('/_ah/stop')
def stop():
    pid = get_pid()

    if not pid:
        return 'Worker pid not found.', 200

    try:
        proc = psutil.Process(pid)
        proc.terminate()

    except psutil.NoSuchProcess:
        return 'Worker not running.', 503

    return 'ok', 200


@app.route('/')
def index():
    return health()


if __name__ == '__main__':
    PID_FILE = sys.argv[1]
    app.run('0.0.0.0', 8080)
