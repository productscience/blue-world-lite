import requests

def count_customers():
    from join import models
    return len(models.Customer.objects.all())
