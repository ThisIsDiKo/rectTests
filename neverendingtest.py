import socket
import time
import random
addr = ("192.168.0.222", 6454)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
data = b'\x45\x53\x50\x50\x01'

#part1 = 'ESDD'.encode('utf-8')
part1 = b'\x41\x72\x74\x2d\x4e\x65\x74\x00\x00\x50\x00\x0e'
part2 = b'\x00\x00\x00\x00\x02\x00'
l = [0 for i in range(255)]
part3 = bytes(l)

data = part1+part2+part3
sock.sendto(data, addr)
time.sleep(10)

while True:
    randI = random.randint(0, 19)
    print("Set all to:", randI)
    l = [randI for j in range(255)]
    part3 = bytes(l)
    data = part1+part2+part3
    sock.sendto(data, addr)
    time.sleep(10)
#sock.sendto(data, addr)
#d, a = sock.recvfrom(1024)
#print(d)
"""
for i in range(255):
    l = [i for j in range(512)]
    part3 = bytes(l)
    data = part1+part2+part3
    sock.sendto(data, addr)
    time.sleep(0.2)
"""
sock.close()
print("END")
