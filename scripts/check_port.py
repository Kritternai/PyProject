import socket
s=socket.socket()
try:
    s.connect(('127.0.0.1',5004))
    print('connected')
except Exception as e:
    print('connect failed:', e)
finally:
    s.close()