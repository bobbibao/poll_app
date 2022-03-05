from django.contrib import admin
from .models import User, Poll
# Register your models here.
admin.site.register(User)
admin.site.register(Poll)