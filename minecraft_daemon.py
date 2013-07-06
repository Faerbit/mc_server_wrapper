import time
import socket
import subprocess
import argparse
#import os

parser = argparse.ArgumentParser()
parser.add_argument("action")
parser.add_argument("cwd")
args=parser.parse_args()
arg=args.action
cwd=args.cwd
server=subprocess.Popen(arg, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
#print ("Removing socket!")
subprocess.Popen("rm -f server_socket", shell=True)
time.sleep(1)
sock=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
#if os.path.exists("server_socket"):
#	os.remove("server_socket")
sock.bind("server_socket")
sock.listen(1)
while (server.poll()==None):
	connection, addr = sock.accept()
	data = (connection.recv(4096)).decode('utf-8')
	if data=="status":
		connection.send(("Minecraft Server running.").encode('utf-8'))
	elif data=="stop":
		server.stdin.write(("stop\n").encode('utf-8'))
		server.stdin.flush()
		server.wait()
		connection.send(("Server stopped.").encode('utf-8'))
	elif data=="start saverun":
		server.stdin.write(("save-off\n").encode('utf-8'))
		server.stdin.write(("save-all\n").encode('utf-8'))
		server.stdin.flush()
		connection.send(("saving off").encode('utf-8'))
	elif data=="end saverun":
		server.stdin.write(("save-on\n").encode('utf-8'))
		server.stdin.flush()
		connection.send(("Saving back on. Saverun complete.").encode('utf-8'))
	elif data=="check players":
		server.stdin.write(("list\n").encode('utf-8'))
		server.stdin.flush()
		time.sleep(1)
		tail = subprocess.Popen ("tail --lines=2 server.log", cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
		result, crap= tail.communicate()
		connection.send(result)
	elif data[0:7] == "command":
		data = data[8:len(data)]
		server.stdin.write((data+"\n").encode('utf-8'))
		server.stdin.flush()
		time.sleep(1)
		tail = subprocess.Popen ("tail --lines=10 server.log", cwd = cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, shell=True)
		result, crap= tail.communicate()
		connection.send(result)
	connection.close()

sock.close()
#os.remove("server_socket")
#print ("Removing socket!")
subprocess.Popen("rm -f server_socket", shell=True)
