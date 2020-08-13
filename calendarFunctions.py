# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 20:43:35 2020

@author: cesar
"""

#Librerias necesarias para trabaja con la api de google
import os.path
import datetime as dt
from datetime import datetime
import pytz
import pickle

#Librerias especificas de google
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


class Calendars:

    def __init__(self, SCOPES):
        self.scope = SCOPES
        self.generateCredentials(self.scope)
        # Dictionary to help to localize the months in spanish
        self.getMonth = {
            "enero": "01",
            "febrero": "02",
            "marzo" : "03",
            "abril": "04",
            "mayo": "05",
            "junio": "06",
            "julio": "07",
            "agosto": "08",
            "septiembre": "09",
            "octubre": "10",
            "noviembre": "11",
            "diciembre": "12"
        }

    def generateCredentials(self, SCOPES):
        # Genera los permisos para entrar a la cuenta de google
        self.creds = None
        
        # EL archivo token.pickle guarda el acceso y actualiza los tockens, es creado automaticamente cuando
        # cuando se ejecuta el programa por primera vez
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        # Si no hay credenciales validas, deja al usuario hacer loggin
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Guarda las credenciales par el siguiente uso
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def getListOfMonths(self, message):
        months = {}
        for month, code in self.getMonth.items():
            if message.lower().find(month) != -1:
                months[month] = code
        return months

    def getEvents(self):
        # Manda a llamar a la API de Calendar
        service = build('calendar', 'v3', credentials=self.creds)
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events

    def getMonthEvents(self, code, events):
        eventsReply = []
        for event in events:
            date = event['start'].get('dateTime')[5:7]
            if(date == code):
                eventsReply.append(event)
        return eventsReply

    def getNextEvents(self, events):
        eventsReply = []
        for event in events:
            time = event['start'].get('dateTime')[11:16]
            date = event['start'].get('dateTime')[0:10]
            if(date == str(datetime.now().date())):
                eventsReply.append(event)
            if(date == str(dt.date.today() + dt.timedelta(days=1))):
                eventsReply.append(event)
        return eventsReply

    def createEvents(self, eventToCreate):
        eventToCreate["start"]["dateTime"] = datetime.strptime(eventToCreate["start"]["dateTime"], '%d-%m-%Y %H:%M')
        eventToCreate["end"]["dateTime"] = datetime.strptime(eventToCreate["end"]["dateTime"], '%d-%m-%Y %H:%M')
        eventToCreate["start"]["dateTime"] = eventToCreate["start"]["dateTime"].isoformat()
        eventToCreate["start"]["timeZone"] = "America/Chihuahua"
        eventToCreate["end"]["dateTime"] = eventToCreate["end"]["dateTime"].isoformat()
        eventToCreate["end"]["timeZone"] = "America/Chihuahua"

        # Manda a llamar a la API de Calendar
        service = build('calendar', 'v3', credentials=self.creds)
        event = service.events().insert(calendarId='primary', body=eventToCreate).execute()
                
