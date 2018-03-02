
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
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


class Clock:
    def __init__(self):
        self.ping = -1
        self.date_time = datetime.datetime.now()
        self.date = self.date_time.date()
        self.time = self.date_time.time()
        self.today_events = ""
        self.tomorrow_events = ""

    def get_events(self):
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

        today_events_result = service.events().list(
            calendarId='primary', timeMin=day1utc, timeMax=night1utc, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        self.today_events = today_events_result.get('items', [])

        tomorrow_events_result = service.events().list(
            calendarId='primary', timeMin=day2utc, timeMax=night2utc, maxResults=10, singleEvents=True,
            orderBy='startTime').execute()
        self.tomorrow_events = tomorrow_events_result.get('items', [])

    def get_ping(self):
        if platform.system() == "Windows":
            ping_buffer = subprocess.check_output(["ping", "google.com"])
            ping_str = ping_buffer.decode()
            ave_str = "Average = "
            ping_loc = ping_str.find(ave_str)
            self.ping = ping_str[ping_loc + len(ave_str):len(ping_str) - 4]
        else:
            ping_buffer = subprocess.check_output(["ping", "-c", "4", "-q", "google.com"])
            ping_str = ping_buffer.decode()
            split_str = ping_str.split("/")
            self.ping = split_str[4]

    def update_time(self):
        self.date_time = datetime.datetime.now()
        self.date = self.date_time.date()
        self.time = self.date_time.time()


def print_events(event_list, day):
    if (day == "today") | (day == "tomorrow"):
        print("Getting " + day + "'s events")
        if not event_list:
            print('No events scheduled '+day)
        for event in event_list:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])


'''def show_ping(disp):
    clock.get_ping()
    disp.pingvar.set(clock.ping)


def show_time(disp):
    clock.'''


class Display:
    def __init__(self):
        root = Tk()
        root.title("Clock")

        mainframe = ttk.Frame(root, padding="3 3 12 12")
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(0, weight=1)
        # self.pingframe = ttk.Frame(mainframe, padding="3 3 12 12")
        self.pingframe = ttk.Frame(mainframe)
        self.dateframe = ttk.Frame(mainframe)
        self.timeframe = ttk.Frame(mainframe)
        ttk.Button(mainframe, text='Change Function', command=self.change_function).grid(column=1, row=2, sticky=N)

        '''self.dateframe.grid(column=1, row=1, sticky=S)
        self.timeframe.grid(column=1, row=1, sticky=S)
        self.pingframe.grid(column=1, row=1, sticky=S)'''
        # self.dateframe.grid_forget()
        # self.timeframe.grid_forget()

        self.pingvar = StringVar()
        self.update_ping()
        self.timevar = StringVar()
        self.update_time()
        self.datevar = StringVar()
        self.update_date()

        ttk.Label(self.pingframe, textvariable=self.pingvar).grid(column=1, row=1, sticky=E)
        ttk.Button(self.pingframe, text="Refresh", command=self.update_ping).grid(column=2, row=1, sticky=W)

        ttk.Label(self.timeframe, textvariable=self.timevar).grid(column=1, row=1, sticky=E)
        ttk.Button(self.timeframe, text="Refresh", command=self.update_time).grid(column=2, row=1, sticky=W)

        ttk.Label(self.dateframe, textvariable=self.datevar).grid(column=1, row=1, sticky=E)
        ttk.Button(self.dateframe, text="Refresh", command = self.update_ping).grid(column=2, row=1, sticky=W)

        self.currentFrame = self.pingframe
        self.change_function()

        for child in mainframe.winfo_children():
            child.grid_configure(padx=15, pady=15)

        root.bind('<Return>', self.update_ping)
        '''self.pingframe.bind('<Return>', self.update_ping)
        self.dateframe.bind('<Return>', self.update_date)
        self.timeframe.bind('<Return>', self.update_time)'''

        root.mainloop()

    def update_time(self):
        clock.update_time()
        self.timevar.set(clock.time)

    def update_ping(self):
        clock.get_ping()
        self.pingvar.set(clock.ping)

    def update_date(self):
        clock.update_time()
        self.datevar.set(clock.date)

    def change_function(self):
        if self.currentFrame == self.pingframe:
            self.pingframe.grid_forget()
            self.timeframe.grid(column=1, row=1, sticky=S)
            self.currentFrame = self.timeframe
        elif self.currentFrame == self.timeframe:
            self.timeframe.grid_forget()
            self.dateframe.grid(column=1, row=1, sticky=S)
            self.currentFrame = self.dateframe
        elif self.currentFrame == self.dateframe:
            self.dateframe.grid_forget()
            self.pingframe.grid(column=1, row=1, sticky=S)
            self.currentFrame = self.pingframe
        else:
            self.currentFrame.grid_forget()
            self.pingframe.grid(column=1, row=1, sticky=S)
            self.currentFrame = self.pingframe


clock = Clock()
'''clock.get_ping()
clock.update_time()
clock.get_events()
print("ping = ", clock.ping, "datetime = ", clock.date_time)
print_events(clock.today_events, "today")
print_events(clock.tomorrow_events, "tomorrow")'''

display = Display()

