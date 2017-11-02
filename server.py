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
	server_address = ('localhost', int(port))	
	print('starting up on %s port %s', server_address)
	server.bind(server_address)

	# Abertura passiva #
	server.listen(6534)

	# Sockets from which we expect to read #
	inputs = [ server ]

	# Sockets to which we 	expect to write #
	outputs = [ ]
	
	# Client list #
	clients = [ ]

	# Outgoing message queues (socket:Queue) #
	message_queues = {}

	while inputs:
		# Wait for at least one of the sockets to be ready for processing #
		print('\nEsperando algo acontecer')
		readable, writable, exceptional = select.select(inputs, outputs, inputs)
		#Handle inputs
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
					msg_type = struct.unpack('!H', aux)[0]
					aux = s.recv(2)
					origem = struct.unpack('!H', aux)[0]
					aux = s.recv(2)
					destino = struct.unpack('!H', aux)[0]
					aux = s.recv(2)
					seq_num = struct.unpack('!H', aux)[0]
					# 3 = OI
					if msg_type == 3:						
						print('OI de ', origem, 'para', destino)
						# msg = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', new.client_num() )
						# send(OK) com origem (servidor) e destino(NUM destinado ao que enviou)

					# 4 = FLW
					if msg_type == 4:
						print('FLW')
						# send(OK), fechar a conexao com aquele cliente, liberar o NUm dele 					
					
					# 5 = MSG
					if msg_type == 5:
						msg = [ ] 						
						size = s.recv(2)
						msg.append( s.recv(size) )
						# se o destino nao existe, SEND ERRO(origem)
						# se o destino = 0 , SEND broadcast
						# se nao e nada disso, SEND(destino) 
						# SEND OK(origem)
					
					# 6 = CREQ
					if msg_type == 6:
						print('CREQ')
						# SEND CLIST(origem)

					# A readable client socket has data #
					#print >>sys.stderr, 'received "%s" from %s' % (data, s.getpeername())
					#message_queues[s].put(data)
		            # Add output channel for response #
					
					if s not in outputs:
						outputs.append(s)
				else:
		        	# Interpret empty result as closed connection #
					print('closing', client_address, 'after reading no data')
		            # Stop listening for input on the connection #
					if s in outputs:
						outputs.remove(s)
					inputs.remove(s)
					s.close()

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
				print('sending "', next_msg, '" to', s.getpeername())  
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
