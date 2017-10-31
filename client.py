import socket
import sys

for message in messages:

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

def main():

	# Create TCP/IP socket
	IP = int( sys.argv[1] )
	port = ( sys.argv[2] )
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_adress = ( IP, port )

	# Stablish connection	
	sock.connect(server_adress)
	
	print >>sys,stderr, 'connected'

if __name__ == '__main__":
	main()
