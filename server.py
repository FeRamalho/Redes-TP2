import select
import socket
import sys
import queue
import struct

def next_free_id(usedlist):
	for i in usedlist:
		if usedlist[i] == 0:
			usedlist[i] == 1			
			return i

## main function ##
def main():
	port = sys.argv[1]

	# Create a TCP/IP socket #
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setblocking(0)

	# Bind the socket to the port #
	server_address = ('localhost', int(port))	
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

	# next id #
	next_id = 1
 
	# server id #
	server_id = 65535

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
						msg = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', next_id) 
						message_queues[s].put(msg) 
						clients[next_id] = s
						next_id = next_id + 1

					# 4 = FLW #
					if msg_type == 4:
						# ok #
						msg = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', next_id) 
						message_queues[s].put(msg) 
						# remove s #						
						inputs.remove(s)
						if s in outputs:
							outputs.remove(s)
						s.close()
					
					# 5 = MSG #
					if msg_type == 5:					
						aux = s.recv(2)
						size = struct.unpack('!H', aux)[0]
						payload = s.recv(size)
							
						print('recebi: ', payload)
						# se o destino = 0 , SEND broadcast
						if destino == 0:
							print('broadcast')
							message = struct.pack('!H', origem) + payload
							for ppl in outputs:
								if ppl != clients[origem]:
									message_queues[ppl].put(message)	
								else:
									# SEND OK(origem)
									msg = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', origem) 
									message_queues[ppl].put(msg) 
								
						# se o destino nao existe, SEND ERRO(origem)
						elif destino not in clients:
							print('erro')
							message = struct.pack('!H', 2) + struct.pack('!H', 65535) + struct.pack('!H', origem) 
							message_queues[s].put(message)
						
						# se nao e nada disso, SEND(destino) 
						else:
							print('unicast')
							message = struct.pack('!H', 5) + struct.pack('!H', origem) + struct.pack('!H', destino) + struct.pack('!H', size) + payload
							message_queues[destino].put(message)
							# SEND OK(origem)
							msg = struct.pack('!H', 1) + struct.pack('!H', 65535) + struct.pack('!H', origem) 
							message_queues[s].put(msg) 
								
					# 6 = CREQ #
					if msg_type == 6:
						print('CREQ')
						# SEND CLIST(origem)
					
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
