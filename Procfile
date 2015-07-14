worker: rqworker --pid /tmp/rq.pid -u redis://:$REDIS_PASSWORD@$REDIS_HOST:6379
monitor: python monitor.py /tmp/rq.pid
