#!/usr/bin/env python3

import socket, sys, os, signal
import szasar

PORT = 6012
PHOTOS_USERS = [[],[]]
#MAX_FILE_SIZE = 10 * 1 << 20 # 10 MiB
#SPACE_MARGIN = 50 * 1 << 20  # 50 MiB
USERS = ("sar", "sza")
PASSWORDS = ("sar", "sza")
IDENTIFICADORES = "00000"
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
	Identification, Main, Downloading, Uploading = range(5)

def sendOK( s, params="" ):
	s.sendall( ("OK{}\r\n".format( params )).encode( "ascii" ) )

def sendER( s, code ):
	s.sendall( ("ER{}\r\n".format( code )).encode( "ascii" ) )

def session( s ):
	state = State.Identification
	global IDENTIFICADORES
	PHOTOS_USERS[2].append
	while True:
		message = szasar.recvline( dialog ).decode( "ascii" )
		if not message:
			return
		if message.startswith( szasar.Command.Autentificar ):
			if( state != State.Identification ):
				sendER( s , "01")
				continue
			lo = message[4:].split('|')
			if len(lo) < 2:
				sendER( s , "04")
			elif len(lo) > 2:
				sendER( s, "03")
			else:
				try:
					user = USERS.index( lo[1])
					contraseña = PASSWORDS.index( lo[2])
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
			if message.find("|"):
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
			if message.find("|"):
				try:
					message = "OK"
					us = USERS.index(message[4:])
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
			lo = message[4:].split('|')
			if len(lo) == 1:
				try:
					message = "OK"
					for p in PHOTOS_USERS[:]:
						for a in p[:]:
							if a.getID() == lo[0]:
								message += "|{}|{}".format(a.getTamano(), a.getID())
					message += "\r\n"
				except:
					sendER( s, 5 )
					continue
				else:
					s.sendall( message.encode( "ascii" ) )

		elif message.startswith( szasar.Command.Upload ):
			if state != State.Main:
				sendER( s , "01")
				continue
			lo = message[4:].split('|')
			if len(lo) < 3:
				sendER( s , "04")
			elif len(lo) > 3:
				sendER( s, "03")
			else:
				descripcion, photosize, photo = message[4:].split('|')
				try:
						newfoto = Photo(IDENTIFICADORES, descripcion, photosize, photo)
						PHOTOS_USERS[user].append(newfoto)
						IDENTIFICADORES += 1
				except:
					sendER( s, "09" )
				else:
					sendOK( s )

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
