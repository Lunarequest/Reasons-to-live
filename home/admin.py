from django.contrib import admin
from .models import reason_unapproved, reason_approved

# Register your models here.

admin.site.register(reason_unapproved)
admin.site.register(reason_approved)