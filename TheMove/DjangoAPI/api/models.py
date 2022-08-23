from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    vote = models.IntegerField()
    sex = [
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE'),
        ('OTHER', 'OTHER')
    ]
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now=True)

    def CreateID(self):
        id = self.user.username
         
    def GetVote(self):
            return self.vote

    def SetVote(self, val):
            self.vote = val
            self.save()

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-created']



class AllVotes(models.Model):
    defaultVotes = '0 0 0 0 0 0 0 0 0 0 '
    votes = models.CharField(max_length=100, default=defaultVotes)
    id = models.IntegerField(primary_key=True)
    name = 'List of Votes'

    def __str__(self):
        return self.name

    def Update(self, votesArray):
        tmp = ""
        for i in votesArray:
            tmp += str(i) + " "
        self.votes = tmp
        self.save()
