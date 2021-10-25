#!/usr/bin/env python3

import socket, sys, os, signal
import szasar

PORT = 6012
PHOTOS_USERS = [[],[]]
USERS = ('sar', 'sza')
PASSWORDS = ('sar', 'sza')
IDENTIFICADORES = 10000
class Photo(object):
	def __init__(self, id, descripcion, tamano, foto):
		self.id = id
		self.descripcion = descripcion
		self.tamano = tamano
		self.foto = foto
	def getID(self):
		return self.id
	def getDescripcion(self):
		return self.descripcion
	def getTamano(self):
		return self.descripcion
	def getFoto(self):
		return self.foto

class State:
	Identification, Main = range(2)

def sendOK( s, params="" ):
	s.sendall( ("OK{}\r\n".format( params )).encode( "ascii" ) )

def sendER( s, code ):
	s.sendall( ("ER{}\r\n".format( code )).encode( "ascii" ) )

def session( s ):
	state = State.Identification
	global IDENTIFICADORES
	#foto usada para probar el funcionamiento
	#np = Photo(10004, "hola", 1000, 1010100101)
	#PHOTOS_USERS[1].append(np)

	while True:
		message = szasar.recvline( dialog ).decode( "ascii" )
		if not message:
			return
		if message.startswith( szasar.Command.Autentificar ):
			if( state != State.Identification ):
				sendER( s , "01")
				continue
			lo = message[5:].split('|')
			if len(lo) < 2:
				sendER( s , "04")
			elif len(lo) > 2:
				sendER( s, "03")
			else:
				try:
					user = USERS.index( lo[0])
					contraseña = PASSWORDS.index( lo[1])
				except:
					sendER( s , "06")
				else:
					if user == contraseña:
						sendOK( s )
						state = State.Main
					else:
						sendER( s , "06")

		elif message.startswith( szasar.Command.List ):
			if state != State.Main:
				sendER( s , "01" )
				continue
			if message.find("|")!=-1:
				sendER( s , "03")
			else:
				try:
					message = "OK"
					for usuario in USERS[:]:
						message += "|{}".format( usuario )
					message += "\r\n"
				except:
					sendER( s, "07" )
				else:
					s.sendall( message.encode( "ascii" ) )

		elif message.startswith( szasar.Command.ListaFotos ):
			if state != State.Main:
				sendER( s , "01" )
				continue
			lo = message[5:].split('|')
			if len(lo) > 1:
				sendER( s , "03" )
			elif message.find("|") != -1:
				try:
					us = USERS.index(message[5:])
					message = "OK"
					for p in PHOTOS_USERS[us]:
						i=p.getID()
						d=p.getDescripcion()
						message += "|{}{}".format( i, d )
					message += "\r\n"
				except:
					sendER( s, "07" )
				else:
					s.sendall( message.encode( "ascii" ) )
			else:
				try:
					message = "OK"
					for p in PHOTOS_USERS[user]:
						i=p.getID()
						d=p.getDescripcion()
						message += "|{}{}".format( i, d )
					message += "\r\n"
				except:
					sendER( s, "07" )
				else:
					s.sendall( message.encode( "ascii" ) )
			
		elif message.startswith( szasar.Command.Download ):
			if state != State.Main:
				sendER( s )
				continue
			lo = message[5:].split('|')
			if len(lo) == 1:
				try:
					if len(lo[0])!=5:
						sendER( s, "05")
						continue
					iden = int(lo[0])
				except:
					sendER( s, "05")
				else:
					try:
						message = "OK"
						for p in PHOTOS_USERS[:]:
							for a in p[:]:
								if iden == a.getID():
									message += "|{}|{}".format(a.getTamano(), a.getFoto())
									encontrado = True
						message += "\r\n"
					except:
						sendER( s, "11" )
					else:
						if encontrado == True:
							s.sendall( message.encode( "ascii" ) )
						else:
							sendER( s, "10" )
			elif len(lo) > 1:
				sendER( s , "03")
			else:
				sendER( s , "04")

		elif message.startswith( szasar.Command.Upload ):
			if state != State.Main:
				sendER( s , "01")
				continue
			lo = message[5:].split('|')
			if len(lo) < 3:
				sendER( s , "04")
			elif len(lo) > 3:
				sendER( s, "03")
			else:
				try:
						newfoto = Photo(IDENTIFICADORES, lo[0], lo[1], lo[2])
						PHOTOS_USERS[user].append(newfoto)
						IDENTIFICADORES += 1
				except:
					sendER( s, "09" )
				else:
					message = "OK|" + str(newfoto.getID()) + "\r\n"
					s.sendall( message.encode( "ascii" ) )


		elif message.startswith( szasar.Command.Quit ):
			sendOK( s )
			return

		else:
			sendER( s , "02")



if __name__ == "__main__":
	s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )

	s.bind( ('', PORT) )
	s.listen( 5 )

	signal.signal(signal.SIGCHLD, signal.SIG_IGN)

	while True:
		dialog, address = s.accept()
		print( "Conexión aceptada del socket {0[0]}:{0[1]}.".format( address ) )
		if( os.fork() ):
			dialog.close()
		else:
			s.close()
			session( dialog )
			dialog.close()
exit( 0 )