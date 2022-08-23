from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import VotesSerializer, UserSerializer, UserProfileSerializer
from . models import UserProfile, AllVotes, User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate
from django.db import IntegrityError

##########################################################################################
@api_view(['GET']) #user can recieve get this
def GetRoutes(request):
    routes = [
        {
            'username' : '...',
            'email':'...',
            'password':'...'
        },
        {
            'vote' : '...',
        }
    ]
    return Response(routes)
##########################################################################################

##########################################################################################
#display all votes
@api_view(['GET']) #user can recieve this
def GetVotes(request):
    UpdateAllVotes()
    userVotesObject = AllVotes.objects.get(pk=1)
    serializer = VotesSerializer(userVotesObject, many = False)
    
    return Response(serializer.data)

def UpdateAllVotes():
    users = UserProfile.objects.all()
    votesArray = [0] * 10
    for i in users:
        vote = i.GetVote()
        if (i.GetVote() != -1):
            votesArray[vote] += 1
    userVotesObject = AllVotes.objects.get(pk=1)
    userVotesObject.Update(votesArray)
##########################################################################################

##########################################################################################
#display user specific data
@api_view(['GET']) #user can recieve this
def GetUser(request, userString):
    try:
        myUser = User.objects.get(username=userString)
    except ObjectDoesNotExist as e:
        return None
    # if request.user.is_authenticated():
    #     username = request.user.username
    userProfile = UserProfile.objects.get(user=myUser)
    serializer = UserProfileSerializer(userProfile, many = False)
    
    return Response(serializer.data)
##########################################################################################

##########################################################################################
@api_view(['PUT']) #backend recieves this
def UpdateVote(request, userString):
    try:
        myUser = User.objects.get(username=userString)
    except ObjectDoesNotExist as e:
        return None

    userProfile = UserProfile.objects.get(user=myUser)
    #userProfile.SetVote(int(request.data['vote']))

    serializer = UserProfileSerializer(userProfile, data=request.data)
    if serializer.is_valid():
        serializer.save()
    userProfile.SetVote(int(serializer.data['vote']))
    
    return Response(serializer.data)
##########################################################################################

##########################################################################################
#create new user
@api_view(['POST']) #user can recieve this
def CreateNewUser(request):
    isCreated = False
    errorCode = ''
    myUsername = request.data['username']
    myEmail = request.data['email']
    myPassword = request.data['password']
    try:
        myUser = User.objects.create_user(username=myUsername,
                                 email=myEmail,
                                 password=myPassword)
        userProfile = UserProfile.objects.create(user = myUser, vote = -1)
        isCreated = True
    except IntegrityError as e:
        errorCode = 'username already exists'

    display1 = {
            'success' : 'true',
            'username': myUsername
        }
    
    display2 = {
            'success' : 'false',
            'error': errorCode
        }
    
    if isCreated:
        return Response(display1)
    else:
        return Response(display2)

##########################################################################################

##########################################################################################
#authenticate user
@api_view(['POST']) #user can recieve this
def AuthenticateUser(request):
    myUsername = request.data['username']
    myPassword = request.data['password']

    display1 = {
            'authenticated' : 'true',
            'username': myUsername
        }
    
    display2 = {
            'authenticated' : 'false',
        }

    user = authenticate(username=myUsername, password=myPassword)
    if user is not None:
        return Response(display1)

    else:
        return Response(display2)


##########################################################################################