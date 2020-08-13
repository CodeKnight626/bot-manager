from __future__ import print_function
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 23 20:43:35 2020

@author: cesar
"""
#Import library to read variable system with the token of the bot
import os.path

# Librerias para usar la api de telegram
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
import logging

# Librerias para trabajar con fechas
import datetime
import pytz

# Libreria para utilizar las funciones de google calendar
from calendarFunctions import Calendars 

# Librerias para utilizar el crm
from CRM import Crm

TELEGRAM_BOT_MANAGER_TOKEN = os.environ["TELEGRAM_BOT_MANAGER_TOKEN"]
DATABASE_PATH = os.environ["DATABASE_PATH"]

# Si se modifican los permisos borrar el archivo token.pickle
calendar = Calendars(['https://www.googleapis.com/auth/calendar'])

# Crea una instancia para utilizar el CRM y la base de datos
crm = Crm(DATABASE_PATH)

# Variable utilizada para seguir la respuestas 
answersDict = {
    "answer": 0,
    "name": "",
    "answerClient": 0,
    "nameC": ""
}
event = {
    "summary": "",
    "description": "",
    "start": {},
    "end": {}
}
client = {
    "Nombre": "",
    "E-mail": "",
    "Telefono": "",
    "Empresa": "",
    "Ubicacion": "",
    "FormaContacto": "",
    "Servicios": "",
    "MarcasUtilizadas": ""
}

#Funcion llamada cada vez que se utiliza el comando /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hola, soy el ayudante privado de BotsIA, estoy en fase de desarrollo, no hago nada por el momento, cada nueva actualización yo la dare a conocer a través del comando '/ayuda'")

def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Lista de comandos;\n /inicio: Introduccion del bot\n /ayuda: Lista de comandos\n /pendientes: Ver los pendientes en el calendario")

#Funcion llamada cada vez que se genera un cambio de status en el grupo
def welcome(update, context):
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING)
    if update.message.new_chat_members:
        for new_member in update.message.new_chat_members:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Holaaaaaa " + new_member.first_name + ", Bienvenido")


def pendientes(update, context):
    message = update.message.text
    events = calendar.getEvents()
    eventsFromDB = crm.getPendientes()
    months = calendar.getListOfMonths(message)

    if eventsFromDB:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Pendientes de la base de datos:")
        for listOfEvents in eventsFromDB:
            sendEvents = f""
            for data in listOfEvents:
                sendEvents = f"{sendEvents} - {str(data)}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=sendEvents)

    if message.find("todos") != -1 and events:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Hola " + update.message.from_user.first_name + " aquí está la lista completa de pendientes : ")
        for event in events:
            time = event['start'].get('dateTime')[11:16]
            date = event['start'].get('dateTime')[0:10]
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"{event['summary']} el dia {date} a las {time}")

    elif months:
        for month, code in months.items():
            monthEvents = calendar.getMonthEvents(code, events)
            if monthEvents:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hola {update.message.from_user.first_name} los pendientes de {month.capitalize()} son: ")
                for event in monthEvents:
                    time = event['start'].get('dateTime')[11:16]
                    date = event['start'].get('dateTime')[0:10]
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{event['summary']} el dia {date} a las {time}")
            else:
                context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hola {update.message.from_user.first_name} No hay pendientes programados para el mes de {month.capitalize()}")

    elif events:
        events = calendar.getNextEvents(events)
        if events:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Hola " + update.message.from_user.first_name + " los proximos pendientes son: ")
            for event in events:
                time = event['start'].get('dateTime')[11:16]
                date = event['start'].get('dateTime')[0:10]
                if(date == str(datetime.datetime.now().date()) and not bool(months)):
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Hoy:")
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{event['summary']} a las {time}")
                if(date == str(datetime.date.today() + datetime.timedelta(days=1)) and not bool(months)):
                    context.bot.send_message(chat_id=update.effective_chat.id, text="Mañana:")
                    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{event['summary']} a las {time}")
        elif not events:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hola {update.message.from_user.first_name} No hay pendientes programados en el calendario")
        
    elif not events:
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Hola {update.message.from_user.first_name} No hay pendientes programados en el calendario")
    

def agregarPendiente(update, context):
    message = update.message.text
    chat_id = update.message.chat_id
    answersDict["answer"] = 0
    event["summary"] = ""
    event["description"] = ""
    event["start"] = {}
    event["end"] = {}
    context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="¿Qué nombre deseas para el proximo pendiente?")
    answersDict["answer"] = 1
    answersDict["name"] = update.message.from_user.first_name


def agregarCliente(update, context):
    message = update.message.text
    chat_id = update.message.chat_id
    answersDict["answerClient"] = 0
    answersDict["nameC"] = ""
    client["Nombre"] = ""
    client["E-mail"] = ""
    client["Telefono"] = ""
    client["Empresa"] = ""
    client["Ubicacion"] = ""
    client["FormaContacto"] = ""
    client["Servicios"] = ""
    client["MarcasUtilizadas"] = ""
    context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    context.bot.send_message(chat_id=chat_id, text="¿Nombre?")
    answersDict["answerClient"] = 1
    answersDict["nameC"] = update.message.from_user.first_name

def verClientes(update, context):
    message = update.message.text
    chat_id = update.message.chat_id
    context.bot.send_chat_action(chat_id=chat_id, action=telegram.ChatAction.TYPING)
    listOfClients = crm.getClients(message[13:])
    if message[13:] == "":
        for client in listOfClients:
            context.bot.send_message(chat_id=chat_id, text=client[0])
    else:
        print(listOfClients)
        for client in listOfClients:
            for data in client:
                context.bot.send_message(chat_id=chat_id, text=data)


def respuestas(update, context):
    message = update.message.text
    chat_id = update.message.chat_id
    if ((answersDict["answer"] == 0 and answersDict["answerClient"] == 0) or message.find("!stop") != -1):
        answersDict["answer"] = 0
        return 0

    elif(answersDict["answer"]==1 and update.message.from_user.first_name==answersDict["name"]):
        event["summary"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Descripcion?:")
        answersDict["answer"] = 2

    elif(answersDict["answer"]==2 and update.message.from_user.first_name==answersDict["name"]):
        event["description"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Fecha? en el formato 'dd-mm-yyyy':")
        answersDict["answer"] = 3

    elif(answersDict["answer"]==3 and update.message.from_user.first_name==answersDict["name"]):
        event["start"]["dateTime"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Deseas agregarlo a Google calendar?:")
        answersDict["answer"] = 4

    elif(answersDict["answer"]==4 and update.message.from_user.first_name==answersDict["name"] and message.lower() == "si"):
        context.bot.send_message(chat_id=chat_id, text="¿Hora de inicio? En el formato 'hh:mm':")
        answersDict["answer"] = 5

    elif(answersDict["answer"]==4 and update.message.from_user.first_name==answersDict["name"] and message.lower() == "no"):
        context.bot.send_message(chat_id=chat_id, text="Agregado a la lista")
        answersDict["answer"] = 0

    elif(answersDict["answer"]==5 and update.message.from_user.first_name==answersDict["name"]):
        event["start"]["dateTime"] = event["start"]["dateTime"] + " " + message
        context.bot.send_message(chat_id=chat_id, text="¿Fecha de cierre? en el formato 'dd-mm-yyyy':")
        answersDict["answer"] = 6

    elif(answersDict["answer"]==6 and update.message.from_user.first_name==answersDict["name"]):
        event["end"]["dateTime"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Hora de cierre? En el formato 'hh:mm':")
        answersDict["answer"] = 7

    elif(answersDict["answer"]==7 and update.message.from_user.first_name==answersDict["name"]):
        event["end"]["dateTime"] = event["end"]["dateTime"] + " " + message
        calendar.createEvents(event)
        context.bot.send_message(chat_id=chat_id, text="Agregado a la lista y al calendario")
        answersDict["answer"] = 0

    elif(answersDict["answerClient"]==1 and update.message.from_user.first_name==answersDict["nameC"]):
        client["Nombre"] = message
        context.bot.send_message(chat_id=chat_id, text="¿E-mail?")
        answersDict["answerClient"] = 2

    elif(answersDict["answerClient"]==2 and update.message.from_user.first_name==answersDict["nameC"]):
        client["E-mail"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Telefono?")
        answersDict["answerClient"] = 3

    elif(answersDict["answerClient"]==3 and update.message.from_user.first_name==answersDict["nameC"]):
        client["Telefono"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Empresa?")
        answersDict["answerClient"] = 4

    elif(answersDict["answerClient"]==4 and update.message.from_user.first_name==answersDict["nameC"]):
        client["Empresa"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Ubicacion?")
        answersDict["answerClient"] = 5

    elif(answersDict["answerClient"]==5 and update.message.from_user.first_name==answersDict["nameC"]):
        client["Ubicacion"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Forma preferida de contacto?")
        answersDict["answerClient"] = 6

    elif(answersDict["answerClient"]==6 and update.message.from_user.first_name==answersDict["nameC"]):
        client["FormaContacto"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Servicios?")
        answersDict["answerClient"] = 7

    elif(answersDict["answerClient"]==7 and update.message.from_user.first_name==answersDict["nameC"]):
        client["Servicios"] = message
        context.bot.send_message(chat_id=chat_id, text="¿Marcas a Utilizar?")
        answersDict["answerClient"] = 8

    elif(answersDict["answerClient"]==8 and update.message.from_user.first_name==answersDict["nameC"]):
        client["MarcasUtilizadas"] = message
        crm.addClients(client)
        crm.addPendients(event)
        context.bot.send_message(chat_id=chat_id, text="Nuevo cliente agregado al CRM")
        answersDict["answerClient"] = 0



def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def main():

    #service = build('calendar', 'v3', credentials=creds)

    # Creamos un objecto "updater" con el token de nuestro bot 
    updater = Updater(token=TELEGRAM_BOT_MANAGER_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    # Objeto de telegram.message
    #messages = telegram.Message()
    
    # Configuraremos un loggin para saber porque no funcionan las cosas
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    
    # Manda a llamar funciones dependiendo del comando
    dispatcher.add_handler(CommandHandler('inicio', start))
    dispatcher.add_handler(CommandHandler('ayuda', help))
    dispatcher.add_handler(CommandHandler('pendientes', pendientes))
    dispatcher.add_handler(CommandHandler('agregarpendiente', agregarPendiente))
    dispatcher.add_handler(CommandHandler('agregarcliente', agregarCliente))
    dispatcher.add_handler(CommandHandler('verclientes', verClientes))
    
    # Manda a llamar la funcion echo cuando se da una opcion sin comando
    #dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))
    
    # Manda a llamar la funcion cuando llega algun mensaje nuevo
    dispatcher.add_handler(MessageHandler(Filters.text , respuestas))
    # Manda a llamar la funcion cuando hay un cambio de status
    dispatcher.add_handler(MessageHandler(Filters.status_update, welcome))
    
    
    #Iniciamos el bot
    updater.start_polling()
    
    #Detener el bot
    #updater.stop()
    
    
if __name__ == "__main__":
    main()