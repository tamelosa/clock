
from __future__ import print_function
import httplib2
import os
import platform

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import subprocess

from tkinter import *
from tkinter import ttk


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Clock'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'clock.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def get_events():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.now()
    day1 = now.replace(hour=0, minute=0, second=0)
    night1 = now.replace(hour=23, minute=59, second=59)
    tomorrow = now + datetime.timedelta(days=1)
    day2 = tomorrow.replace(hour=0, minute=0, second=0)
    night2 = tomorrow.replace(hour=23, minute=59, second=59)

    day1stamp = day1.timestamp()
    night1stamp = night1.timestamp()
    day2stamp = day2.timestamp()
    night2stamp = night2.timestamp()

    day1utc = datetime.datetime.utcfromtimestamp(day1stamp).isoformat() + 'Z'
    night1utc = datetime.datetime.utcfromtimestamp(night1stamp).isoformat() + 'Z'
    day2utc = datetime.datetime.utcfromtimestamp(day2stamp).isoformat() + 'Z'
    night2utc = datetime.datetime.utcfromtimestamp(night2stamp).isoformat() + 'Z'

    print("Getting today's events")
    todayEventsResult = service.events().list(
       calendarId='primary', timeMin=day1utc, timeMax=night1utc, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    todayEvents = todayEventsResult.get('items', [])
    if not todayEvents:
        print('No events scheduled today')
    for event in todayEvents:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

    print("Getting tomorrow's events")
    tomorrowEventsResult = service.events().list(
       calendarId='primary', timeMin=day2utc, timeMax=night2utc, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    tomorrowEvents = tomorrowEventsResult.get('items', [])
    if not tomorrowEvents:
        print('No events scheduled tomorrow')
    for event in tomorrowEvents:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


class Clock:

    def __init__(self):
        self.dateTime = datetime.datetime.now()
        self.date = datetime.datetime.now().date()
        self.time = datetime.datetime.now().time()
        self.ping = -1

    def get_ping(self):
        if platform.system() == "Windows":           
            pingBuffer = subprocess.check_output(["ping", "google.com"])
            pingStr = pingBuffer.decode()
            aveStr = "Average = "
            pingLoc = pingStr.find(aveStr)
            self.ping = pingStr[pingLoc + len(aveStr):len(pingStr) - 4]
        else:
            pingBuffer = subprocess.check_output(["ping",
            "-c", "4", "-q", "google.com"])
            pingStr = pingBuffer.decode()
            splitStr = pingStr.split("/")
            self.ping = splitStr[4]
            
        #print("Your ping is "+self.ping+"ms")

    def update_time(self):
        self.dateTime = datetime.datetime.now()


clock = Clock()
clock.get_ping()
#clock.update_time()
#print(Clock.dateTime())
#get_events()


def show_ping(*args):
    clock.get_ping()
    displayValue.set(clock.ping)


root = Tk()
root.title("Clock")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

displayValue = StringVar()
changeFunc = StringVar()

ttk.Label(mainframe, textvariable=displayValue).grid(column=1, row=1, sticky=E)
updateButton = ttk.Button(mainframe, text='update', command=show_ping).grid(column=2, row=1, sticky=W)
# changeButton = ttk.Button(mainframe, textvariable=changeFunc).grid(column=2, row=2, sticky=(N,W))


'''def show_time(*args):
    clock.update_time()
    displayValue.set(clock.time)


def show_date(*args):
    clock.update_time()
    displayValue.set(clock.date)


def change_function(*args):
    
    functiontext = changeFunc.get()
    if functiontext == "Date":
        changeFunc.set("Ping")
        updateButton.configure(command=show_date)
        show_date()
    elif functiontext == "Ping":
        changeFunc.set("Time")
        updateButton.configure(command=show_ping)
        show_ping()
    else:
        changeFunc.set("Date")
        updateButton.configure(command=show_time)
        show_time()


changeButton.config(command=change_function)
change_function()'''

for child in mainframe.winfo_children(): child.grid_configure(padx=15, pady=15)

root.bind('<Return>', show_ping)

root.mainloop()
