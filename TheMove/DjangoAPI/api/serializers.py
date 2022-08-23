from rest_framework.serializers import ModelSerializer
from . models import AllVotes, UserProfile, User

class VotesSerializer(ModelSerializer):
    class Meta:
        model = AllVotes
        fields = '__all__'


class UserProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        #fields = ['vote']


class UserSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        #fields = ['vote']

