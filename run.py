from rq import Queue
from worker import conn
from jobs import count_customers

import time

# q = Queue(connection=conn, async=False)
q = Queue(connection=conn)
job = q.enqueue(count_customers)  # Accepts args
print(job.result)
time.sleep(2)
print(job.result)
