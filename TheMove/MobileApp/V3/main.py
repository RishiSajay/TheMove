from asyncio.windows_events import NULL
from cgitb import reset
from turtle import update, width
from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.lang import Builder
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDRectangleFlatButton, MDFillRoundFlatButton, MDRoundFlatButton, MDFlatButton
from kivy.properties import StringProperty, BooleanProperty
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Ellipse
from kivy.utils import get_color_from_hex, rgba
from kivy.uix.behaviors import ToggleButtonBehavior

import socket

from matplotlib.style import use
import requests
import json

###########################################################################
#global variables
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
DISCONNECT_MESSAGE = "!DISCONNECT"
REFRESH_MESSAGE = "!REFRESH"
VERIFY_ID_MESSAGE = "!VERIFY_ID"
NEW_ID_MESSAGE = "!NEW_ID_REQUEST"
VERIFIED_MESSAGE = "!VERIFIED"
NOT_VERIFIED_MESSAGE = "!NOT_VERIFIED"
PLACEHOLDER = "tmp"
votesAsString = ""
username = ""
password = ""
isVerified = False
###########################################################################

###########################################################################
#toggle buttons
#Orange
class MyToggleButton1(MDRoundFlatButton, ToggleButtonBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.md_bg_color = get_color_from_hex("C73E09")
        self.line_color = get_color_from_hex("C73E09")
        self.text_color = get_color_from_hex("C73E09")
    def on_state(self, widget, value):
        if (value == 'down'):
            self.md_bg_color = get_color_from_hex("FF9C76")
            self.text_color = get_color_from_hex("C73E09")
        else:
            self.line_color = get_color_from_hex("C73E09")
            self.text_color = get_color_from_hex("C73E09")
            self.md_bg_color = (0, 0, 0, 0)

#Blue
class MyToggleButton2(MDRoundFlatButton, ToggleButtonBehavior):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        #self.md_bg_color = get_color_from_hex("102B70")
        self.line_color = get_color_from_hex("087CDF")
        self.text_color = get_color_from_hex("087CDF")
    def on_state(self, widget, value):
        if (value == 'down'):
            self.md_bg_color = get_color_from_hex("A5C3FF")
            self.text_color = get_color_from_hex("087CDF")
        else:
            self.line_color = get_color_from_hex("087CDF")
            self.text_color = get_color_from_hex("087CDF")
            self.md_bg_color = (0, 0, 0, 0)
        
        

class MyToggleButton2(MDFillRoundFlatButton, MDToggleButton):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_down = self.theme_cls.primary_light

###########################################################################


#kivy screens
class WindowManager(ScreenManager):
    pass

class WelcomeScreen(Screen):
    pass
###################################################################################
class CreateUserScreen(Screen):
    createUserText = StringProperty("")

    def createPressed(self):
        newUsername = self.ids["newUsernameInput"].text
        newPassword = self.ids["newPasswordInput"].text

        self.createUser()
        
        if isVerified:
            kv.current = "voting_or_live"
            kv.transition.direction = "left"
        else:
            self.ids["newLoginDisplay"].text = "Invalid username or password! If you forgot your username or password I really can't help you."
    

#Communicate with Django API
    apiURL = 'http://127.0.0.1:8000'
    
    def createUser(self, newUsername, newPassword):
        response = requests.post(self.apiURL + '/users/authenticate', json={
            'username': newUsername,
            'password': newPassword,
            'email': ''
        }).json()

        isAuthenticated = response['authenticated']


###################################################################################


###################################################################################
class LoginScreen(Screen):
    newLoginText = StringProperty("")

    def submitLoginPressed(self):
        global isVerified, username, password
        username = self.ids["usernameInput"].text
        password = self.ids["passwordInput"].text

        self.authenticateUser()
        
        if isVerified:
            kv.current = "voting_or_live"
            kv.transition.direction = "left"
        else:
            self.ids["newLoginDisplay"].text = "Invalid username or password! If you forgot your username or password I really can't help you."
    

#Communicate with Django API
    apiURL = 'http://127.0.0.1:8000'
    
    def authenticateUser(self):
        global isVerified, username, password
        response = requests.post(self.apiURL + '/users/authenticate', json={
            "username": username,
            "password": password,
        }).json()
        print(response)
        isAuthenticated = response['authenticated']
        if isAuthenticated == 'true':
            username = response['username']
            username = '/' + username + '/'
            isVerified = True
        else:
            isVerified = False

###################################################################################


class VotingOrLiveScreen(Screen):
    pass

###########################################################################
#bulk of code to communicate votes with server
class VotingScreen(Screen):
    hasVoted = False
    hasVotedText = StringProperty("You have not voted")
    userVote = -1
    userVoteName = ""

    #refresh when screen loads
    def on_pre_enter(self, *args):
        self.Update()

    #split button text to get the lines you want
    def splitTextByLine(self, text):
        textList = text.splitlines()
        return textList

    #when a toggle button is pressed
    def togglePressed(self, widget):
        textByLine = self.splitTextByLine(str(widget.text))
        if (widget.state == "down"):
            self.hasVoted = True
            self.userVote = int(widget.name)
            self.userVoteName = textByLine[0]
        else:
            self.hasVoted = False
            self.userVote = 0

        if (self.hasVoted):
            self.hasVotedText = "You have selected " + textByLine[0]
        else:
            self.hasVotedText = "You have not voted"

    #submit vote
    def submitPressed(self):
        if self.hasVoted:
            self.sendUserVote()
            self.Update()
            
    #refresh client
    def refreshPressed(self):
        self.Update()

    ###################################################################################
    #Communicate with Django API
    apiURL = 'http://127.0.0.1:8000'
    def getVotes(self):
        response = requests.get(self.apiURL + '/votes/').json()
        votesAsString = response['votes']
        return votesAsString
        
    def getUserVote(self):
        global username
        response = requests.get(self.apiURL + '/users' + username).json()
        userVote = response['vote']
        return userVote

    def sendUserVote(self):
        global username
        response = requests.put(self.apiURL + '/users/update' + username, json={
            "vote": self.userVote
        })

    ###################################################################################

    #methods for diplaying server data in client
    #this happens after user presses submit or refresh

    #overall update method
    def Update(self):
            votesAsString = self.getVotes()
            userVote = self.getUserVote()
            userVote = str(userVote)
            allVotes = self.convertStringToList(votesAsString)
            self.updateVotes(allVotes, userVote)

    #get votes as list
    def convertStringToList(self, votesAsString):
        myList = votesAsString.split()
        lastItem = myList.pop() #return just the total votes from server
        return myList

    #update diplayed votes with server data
    def updateVotes(self, allVotes, userVote):
        for location, numVotes in enumerate(allVotes):
            self.updateLocation(location, numVotes)
        self.updateUserVoteInClient(userVote) #update client vote button last
    
    #update each location's votes
    def updateLocation(self, loc, numVotes):
        button = self.ids[str(loc)]
        text = button.text
        text = self.splitTextByLine(text)
        button.text = text[0] + "\n Number of votes: " + numVotes
        button.state = "normal"
    
    #update client to show users current vote. ie if user votes the social, the social is selected in clients view
    def updateUserVoteInClient(self, vote):
        if vote != "-1":
            button = self.ids[vote]
            text = button.text
            text = self.splitTextByLine(text)
            button.state = "down"
            label = self.ids["hasVoted"]
            label.text = "You have voted for " + text[0]

###########################################################################


###########################################################################
#run app
#designate kv file

kv = """ """
class TheMoveApp(MDApp):
    def build(self):
        global kv
        kv = Builder.load_file('TheMove.kv')
        #self.theme_cls.primary_palette = "Orange"
        #Window.clearcolor = (1,1,1,1)
        return kv


TheMoveApp().run()
###########################################################################
