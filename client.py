# -*- coding: utf-8 -*-

import socket
import sys
import struct
import select


def main():
	# Create TCP/IP socket
	IP = ( sys.argv[1] )
	port = int( sys.argv[2] )
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_adress = ( IP, port )

	# Stablish connection	
	sock.connect(server_adress)
	
	numseq = 1
	print('Conectado com o servidor')
	# manda OI
	oi = struct.pack('!H', 3) + struct.pack('!H', 0) + struct.pack('!H', 65535) + struct.pack('!H', 0)
	sock.send(oi)
	# recebe OK
	ok = sock.recv(2)
	msg_type = struct.unpack('!H', ok)[0]
	print('\nmessage type: ',msg_type)
	if msg_type == 1:
		ok = sock.recv(2)
		idfrom = struct.unpack('!H', ok)[0]
		print('\nrecieved ok from ', idfrom)
		ok = sock.recv(2)
		myid = struct.unpack('!H', ok)[0]
		print('\nmy id is: ',myid)
		ok = sock.recv(2)
		numseq = struct.unpack('!H', ok)[0] # recebe o numero de sequencia

	print('Escolha uma opcao: ')
	print('[1] Enviar uma mensagem\n' + \
		  '[2] Lista de clientes\n' + \
		  '[3] Sair')


	while 1:
		socket_list = [sys.stdin, sock]
		ready_to_read, ready_to_write, error_sock = select.select(socket_list , [], [])

		for i in ready_to_read:
			#print('IIIII ',i)
			if i == sock: # mensagem recebida do servidor
				print('RECEBI DO SERVIDOR')
				msg = i.recv(2)
				msg_type = struct.unpack('!H', msg)[0]
				print('MENSAGEM TIPO ',msg_type)
				#if not msg:
				#	sys.exit()
				if msg_type == 1: # recebeu OK
					print('ENTROU NO OK')
					msg = i.recv(4)
					msg = i.recv(2)
				elif msg_type == 5:
					print('ENTOU NA MSG')
					msg = i.recv(2)
					idfrom = struct.unpack('!H', msg)[0]
					msg = i.recv(2)
					dst = struct.unpack('!H', msg)[0]
					if myid == dst:
						print('ta certo')
					msg = i.recv(2) # recebe o numero de sequencia
					msg = i.recv(2)
					#length = struct.unpack('!H', msg)[0]
					length = msg
					msg = i.recv(length)
					#mensagem = struct.unpack('!H', msg)[0]
					mensagem = msg.decode()
					print('Mensagem de ', idfrom)
					print(mensagem)

			else: # mensagem do teclado
				print('RECEBI DO TECLADO')
				cmd = input()
				if cmd == '1': # envia mensagem
					print('entrou 1')
					dst = int(input('ID do destino: '))
					mensagem = input('Mensagem: ')
					#mandar a msg
					length = len(mensagem)
					mensagem = mensagem.encode()
					msg = struct.pack('!H', 5) + struct.pack('!H', myid) + struct.pack('!H', dst) + \
					struct.pack('!H', numseq) + struct.pack('!H', length) + mensagem
					numseq +=1
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
					struct.pack('!H', 1)
					sock.send(creq)
					# esperar pelo clist e mandar um ok
					# ver se o numero de sequencia tem que mudar aqui

				elif cmd == '3': # sai do sistema
					print('entrou 3')
					flw = struct.pack('!H', 4) + struct.pack('!H', myid) + struct.pack('!H', 65535) + \
					struct.pack('!H', 1)
					# ver se o numero de sequencia tem que mudar aqui
					sock.send(flw)

					'''# esperando OK
					aux = sock.recv(2)
					msg_type = struct.unpack('!H', aux)[0]
					#print(msg_type)
					if msg_type == 1:
						print('OK')
						aux = sock.recv(4)
						sock.close()
						sys.exit()''' #essa parte ta dando erro





if __name__ == "__main__":
    main()
