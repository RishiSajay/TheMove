from turtle import width
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.metrics import dp
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty
from kivy.graphics.vertex_instructions import Line
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Rectangle, Ellipse

import socket

#global variables
HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

#connect to server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#communicate with server
def sendMessage(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length)) #pad sendLength
    client.send(send_length)
    client.send(message)
    return (client.recv(2048).decode(FORMAT)) #2048 is just large number

class WelcomeScreen(Screen):
    pass

class VotingOrLiveScreen(Screen):
    pass

class VotingScreen(Screen):
    hasVoted = False
    hasVotedText = StringProperty("You have not voted")
    userVote = -1
    oldUserVote = -1
    userVoteName = ""


    def splitTextByLine(self, text):
        textList = text.splitlines()
        return textList

    def concatenateVotes(self, oldVote, newVote):
        finalMessage = str(oldVote) + " " + str(newVote)
        return finalMessage

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
            finalMessage = self.concatenateVotes(self.oldUserVote, self.userVote)
            votesAsString = sendMessage(finalMessage)
            self.oldUserVote = self.userVote #update old vote after message has been sent

            allVotes = self.convertStringToList(votesAsString)
            self.updateVotes(allVotes)
            

    #get votes as list
    def convertStringToList(self, votesAsString):
        myList = votesAsString.split()
        return myList

    #update diplayed votes with server data
    def updateVotes(self, allVotes):
        for location, numVotes in enumerate(allVotes):
            self.updateLocation(location, numVotes)
    
    #update each location's votes
    def updateLocation(self, loc, numVotes):
        button = self.ids[str(loc)]
        text = button.text
        text = self.splitTextByLine(text)
        button.text = text[0] + "\n Number of votes: " + numVotes





class WindowManager(ScreenManager):
    pass


class TheMoveApp(App):
    pass

TheMoveApp().run()
