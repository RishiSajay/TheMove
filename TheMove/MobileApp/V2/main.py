from asyncio.windows_events import NULL
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
userID = ""
isVerified = False
###########################################################################

###########################################################################
#connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
##########################################################################

###########################################################################
#communicate with server
def sendMessage(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length)) #pad sendLength
    client.send(send_length)
    client.send(message)
    return (client.recv(2048).decode(FORMAT)) #2048 is just large number
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

class LoginScreen(Screen):
    newLoginText = StringProperty("")
    def requestIDPressed(self):
        msg = PLACEHOLDER + " " + NEW_ID_MESSAGE
        #print(userID)
        newID = sendMessage(msg)
        self.ids["newLoginDisplay"].text = "You're daily code: " + newID

    def submitLoginPressed(self):
        #send login to server
        potentialID = self.ids["idInputBox"].text
        if potentialID == "":
            potentialID = PLACEHOLDER
        msg = potentialID + " " + VERIFY_ID_MESSAGE
        result = sendMessage(msg)
        
        global isVerified #access global variable
        if result == VERIFIED_MESSAGE:
            isVerified = True
        else:
            isVerified = False
            self.ids["newLoginDisplay"].text = "invalid code! If you forgot your daily code, please request a new one"
        
        global userID #access global variable
        if isVerified:
            kv.current = "voting_or_live"
            kv.transition.direction = "left"
            userID = potentialID
    
            #client gets refreshed after client is verified
            global voteScreen, votesAsString
            votesAsString = client.recv(2048).decode(FORMAT)
            #voteScreen.Update(votesAsString)

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
        global votesAsString
        self.Update(votesAsString)

    #split button text to get the lines you want
    def splitTextByLine(self, text):
        textList = text.splitlines()
        return textList

    #combine ID and vote into one to send to server
    def concatenateIDandVote(self, id, newVote):
        finalMessage = id + " " + str(newVote)
        return finalMessage

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
        #print("Hello")
        global userID
        if self.hasVoted:
            finalMessage = self.concatenateIDandVote(userID, self.userVote)
            #print(finalMessage)
            global votesAsString
            votesAsString = sendMessage(finalMessage) 
            self.Update(votesAsString)
            
    #refresh client
    def refreshPressed(self):
        global userID, votesAsString
        finalMessage = self.concatenateIDandVote(userID, REFRESH_MESSAGE)
        votesAsString = sendMessage(finalMessage) 
        self.Update(votesAsString)

    #methods for diplaying server data in client
    #this happens after user presses submit or refresh

    #overall update method
    def Update(self, votesAsString):
            allVotes, userVote = self.convertStringToList(votesAsString)
            self.updateVotes(allVotes, userVote)

    #get votes as list
    def convertStringToList(self, votesAsString):
        myList = votesAsString.split()
        lastItem = myList.pop() #return just the total votes from server
        return myList, lastItem

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
