import socket
import sys
import struct 

# TEST CLIENT #

# Create TCP/IP socket
port = int( sys.argv[1] )
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_adress = ( 'localhost', port )

# Stablish connection	
sock.connect(server_adress)

print('connected')	
# oi 
msg = struct.pack('!H', 3) + struct.pack('!H', 0) + struct.pack('!H', 321) + struct.pack('!H', 1)
sock.send(msg)
#ok
aux = sock.recv(2)
msg_type = struct.unpack('!H', aux)[0]
print('\nmessage type: ',msg_type)
if msg_type == 1:
	aux = sock.recv(2)
	origem = struct.unpack('!H', aux)[0]
	print('\nrecieved ok  from ', origem)
	aux = sock.recv(2)
	myid = struct.unpack('!H', aux)[0]
	print('\nmy id is: ',myid)
#msg
mensagem = 'mensagem'
length = len(mensagem)
mensagem = mensagem.encode()
msg = struct.pack('!H', 5) + struct.pack('!H', myid) + struct.pack('!H', 0) + struct.pack('!H', 1) + struct.pack('!H', length) + mensagem
sock.send(msg)
print('message sent')
aux = sock.recv(2)
msg_type = struct.unpack('!H', aux)[0]
print(msg_type)
# ok
if msg_type == 1:
	print('ok')	
	aux = sock.recv(4)
# erro
if msg_type == 2:
	print('ixi fudeu')
	aux = sock.recv(4)
sock.close()
