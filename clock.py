from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

import time
from rq import Queue
from worker import conn
from jobs import count_customers


q = Queue(connection=conn)


@sched.scheduled_job('interval', seconds=15)
def timed_job():
    print('This job is run every 15 seconds to count customers.')
    job = q.enqueue(count_customers)


sched.start()
