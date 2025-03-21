__author__ = 'Kugan et Eric Zagre'


import http.server
import threading
import socketserver
import os
import sys
import socket
import json
import re
import sqlite3
from threading import Thread



#database variables
conn = None


#This function open or create the database if it does not exists and initiates the table if it does not exits
def setupDatabase():
    conn =sqlite3.connect("journalist.db")# This will open or create the journalist.db
    print("Database initiated [OK]")

    dbTable = "CREATE TABLE IF NOT EXISTS JOURNALISTDATA (EventID TEXT PRIMARY KEY NOT NULL,Key TEXT, data BLOB )"
    dbTable2 = "CREATE TABLE IF NOT EXISTS MEMBERS (USERID TEXT PRIMARY KEY NOT NULL, CONNECTED TEXT, PASSWORD TEXT )"
    conn.execute(dbTable)
    conn.execute(dbTable2)
    conn.close()


def getAllEntryFromDatabase():
    result = None
    conn =sqlite3.connect("journalist.db")# This will open or create the journalist.db
    query = '''SELECT EventID FROM JOURNALISTDATA'''
    result = conn.execute(query).fetchall()
    conn.close() # close database connection
    return result


def getRequestedItemFromDB(id):

    symbol = id
    t = (symbol,)
    conn =sqlite3.connect("journalist.db")# This will open or create the journalist.db
    query = '''SELECT data FROM JOURNALISTDATA WHERE EventID = ?'''
    result = conn.execute(query, t).fetchone()
    conn.close() # close database connection
    return result
def getPublicKeyOfRequestedItem(id):
    symbol = id
    t = (symbol,)
    conn =sqlite3.connect("journalist.db")# This will open or create the journalist.db
    query = '''SELECT Key FROM JOURNALISTDATA WHERE EventID = ?'''
    result = conn.execute(query, t).fetchone()
    conn.close() # close database connection
    return result

class ThreadedUDPRequestHandler(socketserver.BaseRequestHandler):
    receivedPackets = None
    receivedPacketOrderIndex = 0
    objectID = ""
    totalNbOfPackets = 0

    def handle(self):
        data = ""
		#get port number
        port = self.client_address[1]
		#get the communicate socket
        Socket = self.request[1]
		### get client host ip address
        client_address = (self.client_address[0])
		#proof of multithread
        cur_thread = threading.current_thread()

        data, addr = Socket.recvfrom(1500)
        print("thread %s" % cur_thread.name)
        print("received call from client address :%s" % client_address)
        print("received data from port [%s]: %s" % (port, data))


        print(data.strip(), client_address)

        fileNameStr = str(data.strip())
        print(fileNameStr)
        if not fileNameStr.find("nbPackets") == -1:
            self.totalNbOfPackets = re.search(r'nbPackets:.*', fileNameStr)
            self.totalNbOfPackets = self.totalNbOfPackets.group(0).strip("nbPackets:")
            self.totalNbOfPackets = self.totalNbOfPackets.strip("'")
            self.receivedPackets = ["None"]*int(self.totalNbOfPackets)

        if not fileNameStr.find("Data:") == -1:
            self.objectID = re.search(r'\w*\s', fileNameStr)
            print(self.objectID.group(0))
            self.objectID = self.objectID.group(0)
            self.receivedPacketOrderIndex = re.search('\s\w*:[0-9]*\s', fileNameStr)
            print(self.receivedPacketOrderIndex.group(0).strip(" PacketNum:"))
            self.receivedPacketOrderIndex = self.receivedPacketOrderIndex.group(0).strip(" PacketNum:")
            data = re.search(r'Data:.*', fileNameStr)
            print(data.group(0).strip("Data:"))
            self.receivedPackets[int(self.receivedPacketOrderIndex)] = data.group(0).strip("Data:")

        #server should place the received content in the database
        '''if(receivedPacketOrderIndex+1==totalNbOfPackets):
                conn.execute("INSERT INTO JOURNALISTDATA (EventID,data) \
                                VALUES ("+objectID +","+data+")");

                conn.commit()'''

        # sever should reply to client for received packets
        reply = cur_thread+" Packet Received [OK]"
        Socket.sendto(bytes(reply, "utf-8"), self.client_address)



'''def threadedServer(clientInfo, newSocket):
    global receivedPackets = None
    global receivedPacketOrderIndex = 0
    global objectID = ""
    global totalNbOfPackets = 0

    #print(data.strip(), client_address)

    fileNameStr = str(data.strip())
    print(fileNameStr)
    if not fileNameStr.find("nbPackets") == -1:
        totalNbOfPackets = re.search(r'nbPackets:.*', fileNameStr)
        totalNbOfPackets = totalNbOfPackets.group(0).strip("nbPackets:")
        totalNbOfPackets = totalNbOfPackets.strip("'")
        receivedPackets = ["None"]*int(totalNbOfPackets)

    if not fileNameStr.find("Data:") == -1:
        objectID = re.search(r'\w*\s', fileNameStr)
        print(objectID.group(0))
        objectID = objectID.group(0)
        receivedPacketOrderIndex = re.search('\s\w*:[0-9]*\s', fileNameStr)
        print(receivedPacketOrderIndex.group(0).strip(" PacketNum:"))
        receivedPacketOrderIndex = receivedPacketOrderIndex.group(0).strip(" PacketNum:")
        data = re.search(r'Data:.*', fileNameStr)
        print(data.group(0).strip("Data:"))
        receivedPackets[int(receivedPacketOrderIndex)] = data.group(0).strip("Data:")

        #server should place the received content in the database
        if(receivedPacketOrderIndex+1==totalNbOfPackets):
                conn.execute("INSERT INTO JOURNALISTDATA (EventID,data) \
                                VALUES ("+objectID +","+data+")");

                conn.commit()

        # sever should reply to client for received packets
        #reply = cur_thread+" Packet Received [OK]"
        #Socket.sendto(bytes(reply, "utf-8"), self.client_address)'''

class ThreadedUDPServer(socketserver. ThreadingMixIn, socketserver. UDPServer):
    pass


if __name__ == "__main__":
    receivedPackets = None
    receivedPacketOrderIndex = 0
    objectID = ""
    totalNbOfPackets = 0
    pythonServerPort = 50963
    operType = ""
    packetToSend = None
    publicKey = ""


    test="Alpha,Romeo ,Juliette ,Toshiba,Sony,HP";
    #data = ""

    #call databse function
    setupDatabase()
    #try:
        #creation d'un premier thread serveur qui sera toujours actif
        #Il est le premier qui ecoutera tous ce qui veulent se connecter
        #server=MultiThreadedServer(('192.168.1.100', 8050), MyHandler)


    #Set up UDP server
    UDPSocket=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    listen_addr=('192.168.1.100',pythonServerPort)
    UDPSocket.bind(listen_addr)
    print("Server listening on port "+str(pythonServerPort) + "[OK]")


    while True:
        data, addr = UDPSocket.recvfrom(1500)
        print(data.strip(), addr)

        #print(data)
        fileNameStr = str(data.strip())
        print(fileNameStr)
        if not fileNameStr.find("username") == -1:
            operType = re.search(r'operType:[0-9]*\s', fileNameStr)
            operType = operType.group(0).strip("operType:")

        if not fileNameStr.find("nbPackets") == -1:
            operType = re.search(r'operType:[0-9]*\s', fileNameStr)
            operType = operType.group(0).strip("operType:")
            totalNbOfPackets = re.search(r'nbPackets:[0-9]*\s', fileNameStr)
            totalNbOfPackets = totalNbOfPackets.group(0).strip("nbPackets:")
            #totalNbOfPackets = totalNbOfPackets.strip("'")
            publicKey = re.search(r'encryptionKey:.*', fileNameStr)
            publicKey = publicKey.group(0).strip("'")
            print(publicKey)
            receivedPackets = ["None"]*int(totalNbOfPackets)
            for i in range(0, int(totalNbOfPackets)-1):
                receivedPackets[i] = "None"

            reply = "Packet Received"
            UDPSocket.sendto(bytes(reply, "utf-8"), addr)

        if int(operType) == 3045:
            # we should send the real dat from database
            finalResult = ""
            resulto = getAllEntryFromDatabase()
            for i in range(0, len(resulto)):
                print(resulto[i][0])
                finalResult += (str(resulto[i][0]))
                if i != len(resulto)-1:
                    finalResult += ","
            UDPSocket.sendto(bytes(finalResult, "utf-8"), addr)


        if int(operType) == 4404:
            requestedItem = re.search(r'requestedItem:.*', fileNameStr)
            requestedItem = requestedItem.group(0).strip("requestedItem:").strip("\\")
            requestedItem = requestedItem.strip("\\")
            requestedItem = requestedItem.strip("'")
            key = getPublicKeyOfRequestedItem(requestedItem)
            result = getRequestedItemFromDB(requestedItem)
            UDPSocket.sendto(bytes(str(key), "utf-8"), addr)
            nbPacketToSend = 0
            packet = ""
            if len(result) % 1400 == 0:
                nbPacketToSend = int(len(result)/1400)
            else:
                nbPacketToSend = int(len(result)/1400)
                nbPacketToSend += 1
            packetToSend = ["None"]*nbPacketToSend
            j = 0
            start = 0
            for i in range(0, nbPacketToSend):
                for j in range(i*1400, (i*1400)+1400):
                    packet += result[i]
                    packetToSend[i] = packet
                    packet = ""
            temp=0
            UDPSocket.sendto(bytes(str(nbPacketToSend), "utf-8"), addr)
            while temp != len(packetToSend):
                print(bytearray(packetToSend[temp].encode()))
                UDPSocket.sendto(bytearray(packetToSend[temp].encode()), addr)
                temp += 1


        if not fileNameStr.find("Data:") == -1:
            objectID = re.search(r'\w*\s', fileNameStr)
            print(objectID.group(0))
            objectID = objectID.group(0).strip(" ")
            receivedPacketOrderIndex = re.search('\s\w*:[0-9]*\s', fileNameStr)

            print(receivedPacketOrderIndex.group(0).strip(" PacketNum:"))
            receivedPacketOrderIndex = receivedPacketOrderIndex.group(0).strip(" PacketNum:")
            receivedPacketOrderIndex = int(receivedPacketOrderIndex)

            data2 = re.search(r'Data:.*', fileNameStr)
            print(data2.group(0).strip("Data:"))
            receivedPackets[int(receivedPacketOrderIndex)] = data2.group(0).strip("Data:")

            #server should place the received content in the database
            if receivedPacketOrderIndex+1 == int(totalNbOfPackets):
                temp = ""
                for i in range(0, len(receivedPackets)):
                    temp += receivedPackets[i]
                conn = sqlite3.connect("journalist.db")# This will open or create the journalist.db

                conn.execute('''INSERT OR IGNORE INTO JOURNALISTDATA (EventID,Key,data) VALUES(:id,:key,:donnee)''', {'id': objectID, 'key': publicKey, 'donnee': temp})

                conn.commit()
                conn.close()

            # sever should reply to client for received packets

            print(str(int(receivedPacketOrderIndex)+1) +" " + str(totalNbOfPackets))
            if receivedPacketOrderIndex+1 == int(totalNbOfPackets):
                reply = "Data transfer Completed : 5060"
                UDPSocket.sendto(bytes(reply, "utf-8"), addr)
            else:
                reply = "Data Packet Received"
                UDPSocket.sendto(bytes(reply, "utf-8"), addr)









