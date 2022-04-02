import random
from tabulate import tabulate
import socket
import json
import logging
import time
import threading

# CONSTANT
JUMLAHREQUEST = 420
JUMLAHTHREAD = [1, 5, 10, 20]
SERVERADDRESS = ('172.16.16.101', 6969)

def make_socket(destination_address='localhost',port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def deserialize(s):
    logging.warning(f"Deserialize {s.strip()}")
    return json.loads(s)

def send_command(command_str):
    alamat_server = SERVERADDRESS[0]
    port_server = SERVERADDRESS[1]
    sock = make_socket(alamat_server,port_server)

    try:
        logging.warning(f"Sending message")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received=""

        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = deserialize(data_received)
        logging.warning("Data received from server:")
        return hasil
    except Exception as ee:
        logging.warning(f"Error during data receiving {str(ee)}")
        return False

def getdatapemain(nomor=0):
    cmd=f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd)
    return hasil

def getdatapemain(nomor=0):
    cmd=f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd)
    return hasil

def ambildata(index,latency):

    starting_request_time = time.perf_counter()

    hasil = getdatapemain(random.randint(1,20))

    if (hasil):
        latency[index] = time.perf_counter() - starting_request_time

    else:
        print("Failed to get player data")
        latency[index] = -1

def lihatversi():
    cmd=f"versi \r\n\r\n"
    hasil = send_command(cmd)
    return hasil

if __name__=='__main__':
    h = lihatversi()
    if (h):
        print(h)

    data = []

    for worker in JUMLAHTHREAD:
        jumlahresponse = 0
        jumlahlatency = 0
        
        tasks = {}
        hasiltask = {}

        startingexecutiontime = time.perf_counter()

        count = JUMLAHREQUEST

        while(count):
            currentcount = worker if worker < count else count
            count -= currentcount

            for i in range(currentcount):
                tasks[count - i] = threading.Thread(target=ambildata, args=(count - i, hasiltask))
                tasks[count - i].start()

            for i in range(currentcount):
                tasks[count - i].join()
                hasil = hasiltask[count - i]
                if (hasil != -1):
                    jumlahresponse += 1
                    jumlahlatency += hasil
            

        executiontime = time.perf_counter() - startingexecutiontime
        averagelatency = jumlahlatency / jumlahresponse

        data.append([worker, JUMLAHREQUEST, jumlahresponse, f"{executiontime * 1000:.3f} ms", f"{averagelatency * 1000:.3f} ms"])

    print()
    header = ["Jumlah thread", "Jumlah request", "Jumlah response", "Execution Time", "Average Latency"]
    print(tabulate(data, headers=header,numalign='left',tablefmt='orgtbl'))

print("DONE")