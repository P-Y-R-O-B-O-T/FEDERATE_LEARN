from CYPHER_PROTOCOL.CYPHER_CLIENT.FTP.ftp_client import FTP_CLIENT
from CYPHER_PROTOCOL.CYPHER_CLIENT.cypher_client import CYPHER_CLIENT
import time
import os

# FILE SIZE THAT WILL BE RECIEVED FOR ONE REQUEST
# CHUNK_SIZE CAN BE OF ANY SIZE; JUST KEEP IN MIND :
# "APPROPRIATE TIMEOUT MUST ALSO BE SET TO CLIENT AND SERVER TOO"
# OPTIMUM CHUNK_SIZE DEPENDS ON SYSTEM SPECS; STILL 2MB IS OPTIMUM
# RECV_CHUNK_SIZE AND TRANSMISSION_CHUNK_SIZE MUST BE OF SAME SIZE
RECV_CHUNK_SIZE = 1024*1024*2

# FILE SIZE THAT WILL BE TRANSMITTED FOR ONE REQUEST
# CHUNK_SIZE CAN BE OF ANY SIZE; JUST KEEP IN MIND :
# "APPROPRIATE TIMEOUT MUST ALSO BE SET TO CLIENT AND SERVER TOO"
# OPTIMUM CHUNK_SIZE DEPENDS ON SYSTEM SPECS; STILL 2MB IN OPTIMUM
# RECV_CHUNK_SIZE AND TRANSMISSION_CHUNK_SIZE MUST BE OF SAME SIZE
TRANSMISSION_CHUNK_SIZE = 1024*1024*2

# MAX BYTES THAT WOULD BE RECIEVED IN ONE SINGLE recv() CALL
# MAX LIMIT DEPENDS ON SYSTEM SPECS
RECV_BUFFER = 1024*1024*8

# MAX BYTES THAT WOULD BE TRANSMITTED IN ONE SINGLE send() CALL
# MAX LIMIT OF BYTES DEPENDS ON SYSTEM/PYTHON
TRANSMISSION_BUFFER = 1024*1024*1

# ENCRYPTION_KEY and DECRYPTION_KEY CAN BE SAME OR DIFFERENT                                     
# JUST KEEP IN MIND :                                                                            
# ENCRYPTION_KEY OF SERVER IS DECRYPTION_KEY OF CLIENT                                           
# DECRYPTION_KEY OF SERVER IS ENCRYPTION_KEY OF CLIENT                                           
#                                                                                                
# WE ARE KEEPING BOTH SAME FOR SOME SIMPLICITY
ENCRYPTION_KEY = "2ZpK1CdQfm0s1EZ1SIhYfV7MHdJf8X3U"
DECRYPTION_KEY = "2ZpK1CdQfm0s1EZ1SIhYfV7MHdJf8X3U"

# SERVER TIMEOUT PERIOD; CLIENT IS DISCONNECTED IF
# CLIENT DOES NOT SEND ANY REQUEST IN THIS PERIOD
TIMEOUT = 60*1

# FUNCTION TO LET US KNOW WHEN WE ARE ONLINE
def ONLINE_SIGNAL_PROCESSOR() -> None :
    print("You are online")

# FUNCTION TO LET US KNOW WHEN WE ARE OFFLINE
def OFFLINE_SIGNAL_PROCESSOR() -> None :
    print("You are offline")

# FUNCTION TO LET US KNOW WHAT WE RECIEVED FROM SERVER
def FILE_RESP_HANDLER(responce: dict) -> None :
    #print(responce["PATH"])
    pass

def HANDLE_RESPONCE(responce: dict) -> None :
    print("\t[ # ] STARTED")

ips = [["127.0.0.1", 11111], ["127.0.0.2", 11111], ["127.0.0.3", 11111]]
ftp_ips = [["127.0.0.1", 11112], ["127.0.0.2", 11112], ["127.0.0.3", 11112]]

COMPUTING_SERVERS = []
SERVERS_FTP = []

for _ in range(len(ips)) :
    SERVERS_FTP.append(FTP_CLIENT(file_responce_trigger=FILE_RESP_HANDLER,
                                        recv_chunk_size=RECV_CHUNK_SIZE,
                                        transmission_chunk_size=TRANSMISSION_CHUNK_SIZE,
                                        ip=ftp_ips[_][0], port=ftp_ips[_][1],
                                        encryption_key=ENCRYPTION_KEY,
                                        decryption_key=DECRYPTION_KEY,
                                        offline_signal_processor=OFFLINE_SIGNAL_PROCESSOR,
                                        online_signal_processor=ONLINE_SIGNAL_PROCESSOR,
                                        recv_buffer=RECV_BUFFER,
                                        transmission_buffer=TRANSMISSION_BUFFER
                                        )
                            )

for _ in range(len(ftp_ips)) :
    COMPUTING_SERVERS.append(CYPHER_CLIENT(ip=ips[_][0],
                                     port=ips[_][1],
                                     recv_buffer=RECV_BUFFER,
                                     transmission_buffer=TRANSMISSION_BUFFER,
                                     encryption_key=ENCRYPTION_KEY,
                                     decryption_key=DECRYPTION_KEY,
                                     responce_handler=HANDLE_RESPONCE,
                                     timeout=TIMEOUT
                                     )
                       )

if __name__ == "__main__" :
    for _ in range(len(SERVERS_FTP)) :
        print("[ ! ] 1")
        SERVERS_FTP[_].upload_file_s("PREPROCESSED_DATA_2", "")
        SERVERS_FTP[_].upload_file_s("model_1_1_"+str(_+1)+".py", "")
        SERVERS_FTP[_].upload_file_s("locations.txt", "")
    
    for _ in range(len(COMPUTING_SERVERS)) :
        print("[ # ]", _)
        COMPUTING_SERVERS[_].make_request(operation="START", data="python3 model_1_1_"+str(_+1)+".py " + str(_+1) + " " + str(len(COMPUTING_SERVERS)))

    for _ in range(len(SERVERS_FTP)) :
        while "TIME_" + str(_) not in os.listdir() :
            time.sleep(1)
            print("[ $ ]", _)
            SERVERS_FTP[_].fetch_file_s("TIME.txt", "TIME_"+str(_))

        while "ACCURACY_" + str(_) not in os.listdir() :
            time.sleep(1)
            print("[ ^ ]", _)
            SERVERS_FTP[_].fetch_file_s("ACCURACY_OP.txt", "ACCURACY_"+str(_))

        while "TIME_REQ_" + str(_) not in os.listdir() :
            time.sleep(1)
            print("[ & ]", _)
            SERVERS_FTP[_].fetch_file_s("TIME_REQ.txt", "TIME_REQ_"+str(_))

    # concatening the files

    # getting average time for training all models
    times = []
    for  _ in range(2) :
        read_file = open("TIME_"+str(_)+"/TIME.txt", "r")
        times.append(eval(read_file.read()))
        read_file.close()
    avg_time = sum(times)/len(times)
    write_file = open("AVG_TIME.txt", "w")
    write_file.write(str(avg_time))
    write_file.close()

    ## need to be modifies for the other version
    # concat the trimes req file which stores all the files that store time required for all coins
    time_req = []
    times_req = {}
    for _ in range(2) :
        read_file = open("TIME_REQ_"+str(_)+"/TIME_REQ.txt", "r")
        time_req.append(eval(read_file.read()))
        times_req = times_req | time_req[-1]#eval(read_file.read())
        read_file.close()
    write_file = open("TIME_REQ.txt", "w")
    write_file.write(str(times_req))
    write_file.close()

    ## need to be modified for the other version
    # storing the accuracies of the models
    #storing_accuracies
    accuracies = []
    accuracy = {}
    for _ in range(2) :
        read_file = open("ACCURACY_"+str(_)+"/ACCURACY_OP.txt", "r")
        accuracies.append(eval(read_file.read()))
        accuracy = accuracy | accuracies[-1]
        read_file.close()
    write_file = open("ACCURACY.txt", "w")
    write_file.write(str(accuracy))
    write_file.close()
