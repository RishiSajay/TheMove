from django.contrib import admin
from . models import AllVotes, UserProfile

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(AllVotes)
