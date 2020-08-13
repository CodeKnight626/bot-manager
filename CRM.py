# -*- coding: utf-8 -*-
"""
Created on Sat Aug 10 2020

@author: cesar
"""
import datetime as dt
from db import DB
import sqlite3

class Crm:
    def __init__(self, path):
        self.path = path
        
    def addPendients(self, eventToAdd):
        eventToAdd["start"] = eventToAdd["start"]["dateTime"]
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT _id FROM Pendientes")
        pendiendtNumber = len(self.cur.fetchall())
        self.cur.execute("INSERT INTO Pendientes (_id, pendiente, descripcion, Fecha) VALUES (?, ?, ?, ?)", 
            (pendiendtNumber+1, eventToAdd["summary"], eventToAdd["description"], str(eventToAdd["start"])))
        self.conn.commit()
        self.conn.close()

    def addClients(self, clients):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT _id FROM Clients")
        clientNumber = len(self.cur.fetchall())
        self.cur.execute("INSERT INTO Clients (_id, Nombre, 'E-mail', Telefono, Empresa, Ubicación, 'Formas de contacto', Servicios, 'Marcas Utilizadas') VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
            (clientNumber+1, clients["Nombre"], clients["E-mail"], clients["Telefono"], clients["Empresa"], clients["Ubicacion"], clients["FormaContacto"], clients["Servicios"], clients["MarcasUtilizadas"]))
        self.conn.commit()
        self.conn.close()

    def getClients(self, message):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT Nombre FROM Clients")
        clientList = self.cur.fetchall()
        for client in clientList:
            if(message.find(client[0]) != -1):
                self.cur.execute("SELECT Nombre, Email, Telefono, Empresa, Ubicación, 'Formas de contacto', Servicios, 'Marcas Utilizadas' FROM Clients WHERE Nombre=?", (message,))
                clientList = self.cur.fetchall()
                print(clientList)
                return clientList
        self.conn.close()
        return clientList


    def getPendientes(self):
        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()
        self.cur.execute("SELECT pendiente, descripcion, Fecha FROM Pendientes")
        pendientList = self.cur.fetchall()
        self.conn.close()
        return pendientList