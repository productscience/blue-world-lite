from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

import time
from rq import Queue
from redis import Redis
from jobs import count_customers


conn = Redis()
q = Queue(connection=conn)


@sched.scheduled_job('interval', seconds=1)
def timed_job():
    print('This job is run every 1500 seconds to count customers.')
    job = q.enqueue(count_customers)


sched.start()
