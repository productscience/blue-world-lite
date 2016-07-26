import django_rq
import time
from jobs import count_customers

job = django_rq.enqueue(count_customers)
print(job)
print(job.result)
time.sleep(2)
print(job.result)
