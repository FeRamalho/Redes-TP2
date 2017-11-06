import select
import socket
import sys
import queue
import struct

## main function ##
def main():
	port = sys.argv[1]

	# Create a TCP/IP socket #
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)

	# Bind the socket to the port #
	server_address = ("", int(port))	
	print('starting up on localhost port', int(port))
	server.bind(server_address)

	# Abertura passiva #
	server.listen(65534)

	# Sockets from which we expect to read #
	inputs = [ server ]

	# Sockets to which we 	expect to write #
	outputs = [ ]
	
	# Client list #
	clients = {}

	# nickname list #
	apelidos = {}

	# next id #
	next_id = 1
 
	# server id #
	#server_id = 65535

	# Outgoing message queues (socket:Queue) #
	message_queues = {}

	while inputs:
		# Wait for at least one of the sockets to be ready for processing #
		# print('\nEsperando algo acontecer')
		readable, writable, exceptional = select.select(inputs, outputs, inputs)
		# Handle inputs #
		for s in readable:
			if s is server:
			# A "readable" server socket is ready to accept a connection #			
				connection, client_address = s.accept()
				print('new connection from', client_address)
				connection.setblocking(0)
				inputs.append(connection)

		        # Give the connection a queue for data we want to send #
				message_queues[connection] = queue.Queue()
			else:
				aux = s.recv(2)
				if aux:	
				
					# add output for response #					
					if s not in outputs:
						outputs.append(s)

					# recieve origem destino sequence number #
					msg_type = struct.unpack('!H', aux)[0]
					aux = s.recv(2)
					origem = struct.unpack('!H', aux)[0]
					aux = s.recv(2)
					destino = struct.unpack('!H', aux)[0]
					aux = s.recv(2)
					seq_num = struct.unpack('!H', aux)[0]
					
					# 3 = OI #
					if msg_type == 3:
						# ok #						
						ok = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', next_id) + struct.pack('!H', seq_num)
						message_queues[s].put(ok) 
						clients[next_id] = s
						next_id = next_id + 1
						
					elif clients[origem] != s:
						print('CLIENTE: ', clients[origem])
						print('PEERNAMe: ', s.getpeername())
						erro = struct.pack('!H', 2) + struct.pack('!H', 65535) + struct.pack('!H', origem) + struct.pack('!H', seq_num)
						message_queues[s].put(erro)

					# 4 = FLW #
					if msg_type == 4:
						# ok #
						ok = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', origem) + struct.pack('!H', seq_num)
						message_queues[s].put(ok) 

					# 15 = MSGAP #
					if msg_type == 15:
						aux = s.recv(2)
						apelido_size = struct.unpack('!H', aux)[0]
						nickname = s.recv(apelido_size) # string com encode()
						nickname = nickname.decode()
						view = apelidos.values()
						values = list(view)
						for key, nick in apelidos.items():
							if nick == nickname:
								destino = key
						if nickname not in apelidos.values():
							destino = 65550
						msg_type = 5
					
					# 5 = MSG #
					if msg_type == 5:				
						aux = s.recv(2)
						size = struct.unpack('!H', aux)[0]
						payload = s.recv(size) # string com encode()
							
						# se o destino = 0 , SEND broadcast
						if destino == 0:
							print('broadcast')
							message = struct.pack('!H', 5) + struct.pack('!H', origem) + struct.pack('!H', destino) + struct.pack('!H', seq_num) + struct.pack('!H', size) + payload
							# add output for response #					
							for client in clients:
								if client not in outputs:
									outputs.append(clients[client])
									
							for ppl in outputs:
								if ppl != clients[origem]:
									message_queues[ppl].put(message)
									########################### quando arrumar o timeout tem que por aqui tambem	
								else:
									# SEND OK(origem)
									ok = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', origem) + struct.pack('!H', seq_num)
									message_queues[ppl].put(ok) 
								
						# se o destino nao existe, SEND ERRO(origem)
						elif destino not in clients:
							print('erro')
							erro = struct.pack('!H', 2) + struct.pack('!H', 65535) + struct.pack('!H', origem) + struct.pack('!H', seq_num)
							message_queues[s].put(erro)
						# se nao e nada disso, SEND(destino) 
						else:
							print('unicast para:', s)
							message = struct.pack('!H', 5) + struct.pack('!H', origem) + struct.pack('!H', destino) + struct.pack('!H', seq_num) + struct.pack('!H', size) + payload
							# add output for response #					
							if clients[destino] not in outputs:
									outputs.append(clients[destino])
							message_queues[clients[destino]].put(message)
							# SEND OK(origem)
							ok = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', origem) + struct.pack('!H', seq_num)
							message_queues[s].put(ok) 
################################################################################	TIMEOUT BUGADO						
							# RECV OK(destino)
							'''clients[destino].settimeout(5)
							aux = clients[destino].recv(2)
							ok = struct.unpack('!H', aux)
							if ok == 1:
								aux = clients[destino].recv(4)
								aux = clients[destino].recv(2)
								confirmacao = struct.unpack('!H', aux)
							else:
								if s in outputs:
									outputs.remove(clients[destino])
								inputs.remove(clients[destino])
								clients[destino].close()
								# Remove socket #
								del clients[destino]
		            			# Remove message queue #
								del message_queues[s]
							clients[destino].settimeout(None)'''
###############################################################################
								
					# 6 = CREQ #
					if msg_type == 6:
						length = len(clients)
						cl = list(clients.keys())
						print('LISTA:', cl)
						clist = struct.pack('!H', 7) + struct.pack('!H', 65535) + struct.pack('!H', origem) + \
						struct.pack('!H', seq_num) + struct.pack('!H', length) + struct.pack('{}H'.format(length), *cl)
						message_queues[s].put(clist)
						
						# SEND CLIST(origem)

					# 13 = OIAP #
					if msg_type == 13:
						aux = s.recv(2)
						size = struct.unpack('!H', aux)[0]
						nickname = s.recv(size) # string com encode()
						nickname = nickname.decode()
						x = 0
						for key, nick in apelidos.items():
							if nick == nickname:
								x += 1
						if x == 0:
							apelidos[origem] = nickname
							# ok #
							ok = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', origem) + struct.pack('!H', seq_num)
							message_queues[s].put(ok) 
						else:
							print('erro')
							erro = struct.pack('!H', 2) + struct.pack('!H', 65535) + struct.pack('!H', origem) + struct.pack('!H', seq_num)
							message_queues[s].put(erro)
						
						
					# 16 = CREQAP #
					if msg_type == 16:
						lengthtot = len(apelidos)
						apl = list(apelidos.keys())
						ap = list(apelidos.values())
						clistap = struct.pack('!H', 17) + struct.pack('!H', 65535) + struct.pack('!H', origem) + \
						struct.pack('!H', seq_num) + struct.pack('!H', lengthtot) + struct.pack('{}H'.format(lengthtot), *apl)
						x = 0
						while x<lengthtot:
							length = len(ap[x])
							nick = ap[x].encode()
							clistap += struct.pack('!H', length) + nick
							x += 1
						
						message_queues[s].put(clistap)
					
				else:
		        	# Interpret empty result as closed connection #
					print('closing', client_address, 'after reading no data')
		            # Stop listening for input on the connection #
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()
					# Remove socket #
					if origem in apelidos:
						del apelidos[origem]
					del clients[origem]
		            # Remove message queue #
					del message_queues[s]

		# Handle outputs #
		for s in writable:
			try:
				next_msg = message_queues[s].get_nowait()
			except queue.Empty:
		        # No messages waiting so stop checking for writability. #
				print('output queue for', s.getpeername(), 'is empty')
				outputs.remove(s)
			else:
				print('sending to', s.getpeername())  
				s.send(next_msg)

		# Handle "exceptional conditions" #
		for s in exceptional:
			print('handling exceptional condition for', s.getpeername())
		    # Stop listening for input on the connection #
			inputs.remove(s)
			if s in outputs:
				outputs.remove(s)
			s.close()

		    # Remove message queue #
			del message_queues[s]

if __name__ == "__main__":
	main()
