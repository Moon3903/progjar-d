import socket
import logging
import json
import ssl
import threading
import os
import ssl

alldata = dict()

alldata['1']=dict(nomor=1, nama="N0tail")
alldata['2']=dict(nomor=2, nama="JerAx")
alldata['3']=dict(nomor=3, nama="ana")
alldata['4']=dict(nomor=4, nama="Ceb")
alldata['5']=dict(nomor=5, nama="Topson")
alldata['6']=dict(nomor=6, nama="Kuroky")
alldata['7']=dict(nomor=7, nama="Miracle-")
alldata['8']=dict(nomor=8, nama="MinD_ContRoL")
alldata['9']=dict(nomor=9, nama="Matumbaman")
alldata['10']=dict(nomor=10, nama="GH")
alldata['11']=dict(nomor=11, nama="Miposhka")
alldata['12']=dict(nomor=12, nama="Sumail")
alldata['13']=dict(nomor=13, nama="TORONTOTOKYO")
alldata['14']=dict(nomor=14, nama="Collapse")
alldata['15']=dict(nomor=15, nama="Yatoro")
alldata['16']=dict(nomor=16, nama="Mira")
alldata['17']=dict(nomor=17, nama="Puppey")
alldata['18']=dict(nomor=18, nama="Ame")
alldata['19']=dict(nomor=19, nama="y`")
alldata['20']=dict(nomor=20, nama="Zai")

def versi():
    return "versi 0.0.1"

def proses_request(request_string):
    #format request
    # NAMACOMMAND spasi PARAMETER
    cstring = request_string.split(" ")
    hasil = None
    try:
        command = cstring[0].strip()
        if (command == 'getdatapemain'):
            # getdata spasi parameter1
            # parameter1 harus berupa nomor pemain
            logging.warning("getdata")
            nomorpemain = cstring[1].strip()
            try:
                logging.warning(f"data {nomorpemain} ketemu")
                hasil = alldata[nomorpemain]
            except:
                hasil = None
        elif (command == 'versi'):
            hasil = versi()
    except:
        hasil = None
    return hasil


def serialisasi(a):
    #print(a)
    #serialized = str(dicttoxml.dicttoxml(a))
    serialized =  json.dumps(a)
    logging.warning("serialized data")
    logging.warning(serialized)
    return serialized

def server_thread(koneksi,client_address,socket_context):
    try:
        connection = socket_context.wrap_socket(koneksi, server_side=True)
        selesai=False
        data_received=""
        while True:
            data = connection.recv(32)
            logging.warning(f"Received {data}.")
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    selesai=True

                if (selesai==True):
                    hasil = proses_request(data_received)
                    logging.warning(f"Result: {hasil}")

                    #hasil bisa berupa tipe dictionary
                    #harus diserialisasi dulu sebelum dikirim via network
                    # Send data
                    # some data structure may have complex structure
                    # how to send such data structure through the network ?
                    # use serialization
                    #  example : json, xml

                    # complex structure, nested dict
                    # all data that will be sent through network has to be encoded into bytes type"
                    # in this case, the message (type: string) will be encoded to bytes by calling encode

                    hasil = serialisasi(hasil)
                    hasil += "\r\n\r\n"
                    connection.sendall(hasil.encode())
                    selesai = False
                    data_received = ""  # string
                    break
            
            else:
                logging.warning(f"No more data from {client_address}.")
                break
    # Clean up the connection
    except ssl.SSLError as error_ssl:
        logging.warning(f"SSL error: {str(error_ssl)}.")

def run_server(server_address):
    # ------------------------------ SECURE SOCKET INITIALIZATION ----
    cert_location = os.getcwd() + '/certs/'
    socket_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    socket_context.load_cert_chain(
        certfile = cert_location + 'domain.crt',
        keyfile = cert_location + 'domain.key'
    )
    #--- INISIALISATION ---
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # Bind the socket to the port
    logging.warning(f"starting up on {server_address}")
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1000)

    while True:
         # Wait for a connection
        logging.warning("waiting for a connection")
        koneksi, client_address = sock.accept()
        logging.warning(f"Incoming connection from {client_address} creating thread")
        # Receive the data in small chunks and retransmit it

        task = threading.Thread(target=server_thread,args=(koneksi,client_address,socket_context))
        task.start()


if __name__=='__main__':
    try:
        run_server(('0.0.0.0', 6969))
    except KeyboardInterrupt:
        logging.warning("Control-C: Program berhenti")
        exit(0)
    finally:
        logging.warning("selesai")
