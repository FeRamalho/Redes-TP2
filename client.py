import socket
import sys
import struct 
'''for message in messages:

	# Send messages on both sockets
    	for s in socks:
        	print >>sys.stderr, '%s: sending "%s"' % (s.getsockname(), message)
        	s.send(message)

    	# Read responses on both sockets
    	for s in socks:
    	    data = s.recv(1024)
    	    print >>sys.stderr, '%s: received "%s"' % (s.getsockname(), data)
    	    if not data:
    	        print >>sys.stderr, 'closing socket', s.getsockname()
    	        s.close()
'''

# Create TCP/IP socket
#IP = str( sys.argv[1] )
port = int( sys.argv[1] )
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_adress = ( 'localhost', port )

# Stablish connection	
sock.connect(server_adress)

print('connected')	
msg = struct.pack('!H', 3) + struct.pack('!H', 123) + struct.pack('!H', 321) + struct.pack('!H', 1)
sock.send(msg)

