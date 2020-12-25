from django.db import models

# Create your models here.
class reason_unapproved(models.Model):
    reason = models.TextField(max_length=1000)
    email = models.EmailField()
    display_name = models.TextField(max_length=11)


class reason_approved(models.Model):
    reason = models.TextField(max_length=1000)
    email = models.EmailField()
    display_name = models.TextField(max_length=11)
