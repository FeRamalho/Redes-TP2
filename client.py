# -*- coding: utf-8 -*-

import socket
import sys
import struct
import select
#import pickle

def main():
	# Create TCP/IP socket
	IP = ( sys.argv[1] )
	port = int( sys.argv[2] )
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_adress = ( IP, port )

	# Stablish connection	
	sock.connect(server_adress)
	
	numseqprog = 1
	print('Conectado com o servidor')
	# manda OI
	oi = struct.pack('!H', 3) + struct.pack('!H', 0) + struct.pack('!H', 65535) + struct.pack('!H', 0)
	sock.send(oi)
	# recebe OK
	ok = sock.recv(2)
	msg_type = struct.unpack('!H', ok)[0]
	if msg_type == 1:
		ok = sock.recv(2)
		idfrom = struct.unpack('!H', ok)[0]
		print('\nreceived ok from ', idfrom)
		ok = sock.recv(2)
		myid = struct.unpack('!H', ok)[0]
		print('\nMeu ID é:', myid)
		ok = sock.recv(2)
		numseq = struct.unpack('!H', ok)[0] # recebe o numero de sequencia
	else:
		sock.close()
		sys.exit()

	print('Escolha uma opcao: ')
	print('[1] Enviar uma mensagem\n' + \
		  '[2] Lista de clientes\n' + \
		  '[3] Sair')


	while 1:
		socket_list = [sys.stdin, sock]
		ready_to_read, ready_to_write, error_sock = select.select(socket_list , [], [])

		for i in ready_to_read:
			if i == sock: # mensagem recebida do servidor
				msg = sock.recv(2)
				msg_type = struct.unpack('!H', msg)[0]
				if not msg:
					sys.exit()
				elif msg_type == 5:
					msg = sock.recv(2)
					idfrom = struct.unpack('!H', msg)[0]
					msg = sock.recv(2)
					dst = struct.unpack('!H', msg)[0]
					if myid == dst or dst == 0:
						print('ta certo')
						msg = sock.recv(2) # recebe o numero de sequencia
						msg = sock.recv(2)
						length = struct.unpack('!H', msg)[0]
						msg = sock.recv(length)
						mensagem = msg.decode()
						print('Mensagem de', idfrom,':')
						print('>>>', mensagem)
						#manda OK
						ok = struct.pack('!H', 1) + struct.pack('!H', myid) + struct.pack('!H', 65535) + \
						struct.pack('!H', numseqprog)
						sock.send(ok)

			else: # mensagem do teclado
				cmd = input()
				if cmd == '1': # envia mensagem
					print('entrou 1')
					dst = int(input('ID do destino: '))
					while dst == myid:
						print('Nao mande mensagem para você mesmo')
						dst = int(input('ID do destino: '))
					mensagem = input('Mensagem: ')
					#mandar a msg
					length = len(mensagem)
					mensagem = mensagem.encode()
					msg = struct.pack('!H', 5) + struct.pack('!H', myid) + struct.pack('!H', dst) + \
					struct.pack('!H', numseqprog) + struct.pack('!H', length) + mensagem
					numseqprog +=1
					sock.send(msg)

					#esperando OK ou ERRO
					aux = sock.recv(2)
					msg_type = struct.unpack('!H', aux)[0]

					if msg_type == 1: # OK
						print('OK')
						aux = sock.recv(4)
						aux = sock.recv(2) #recebe numero de sequencia

					elif msg_type == 2:
						print('ERRO. NAO EXISTE ESSE CLIENTE')
						aux = sock.recv(4)
						aux = sock.recv(2) #recebe numero de sequencia

				elif cmd == '2': # pede a lista de clientes
					print('entrou 2')
					creq = struct.pack('!H', 6) + struct.pack('!H', myid) + struct.pack('!H', 65535) + \
					struct.pack('!H', numseqprog)
					sock.send(creq)
					# esperar pelo clist e mandar um ok
					aux = sock.recv(2)
					msg_type = struct.unpack('!H', aux)[0]
					if msg_type == 7:
						aux = sock.recv(6)
						aux = sock.recv(2)
						length = struct.unpack('!H', aux)[0]
						aux = sock.recv(length*2)
						#cl = pickle.loads(aux)
						cl = struct.unpack('{}H'.format(length),aux)
						clist = ', '.join([str(x) for x in cl])
						print('Lista de clientes:', clist)
						# manda OK
						ok = struct.pack('!H', 1) + struct.pack('!H', myid) + struct.pack('!H', 65535) + \
						struct.pack('!H', numseqprog)
						sock.send(ok)
						numseqprog += 1
					# ver se o numero de sequencia tem que mudar aqui

				elif cmd == '3': # sai do sistema
					print('entrou 3')
					flw = struct.pack('!H', 4) + struct.pack('!H', myid) + struct.pack('!H', 65535) + \
					struct.pack('!H', numseqprog)
					# ver se o numero de sequencia tem que mudar aqui
					sock.send(flw)
					numseqprog += 1

					# esperando OK
					aux = sock.recv(2)
					msg_type = struct.unpack('!H', aux)[0]
					if msg_type == 1:
						print('OK')
						aux = sock.recv(6)
						sock.close()
						sys.exit() 



if __name__ == "__main__":
    main()
