from CYPHER_PROTOCOL.CYPHER_SERVER.cypher_server import CYPHER_SERVER
from CYPHER_PROTOCOL.CYPHER_SERVER.FTP.ftp_server import FTP_SERVER
import os
import threading
import sys
# MAX BYTES THAT WOULD BE RECIEVED IN ONE SINGLE recv() CALL
# MAX LIMIT DEPENDS ON SYSTEM SPECS
RECV_BUFFER = 1024*1024*8

# MAX BYTES THAT WOULD BE TRANSMITTED IN ONE SINGLE send() CALL
# MAX LIMIT OF BYTES DEPENDS ON SYSTEM/PYTHON
TRANSMISSION_BUFFER = 1024*1024*1

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

# CAN CHANGE THE STRING SIZE AND SEE
# HOW IT AFFECTS THE PING AND OVERALL RECIEVING TIME
DATA = "~"*1024*1024*1

# PATH OF DIRECTORY OF WHICH CONTENT IS TO BE HOSTED
PATH = "."

# HANDLING RESPONCES
def HANDLE_REQUEST(request: dict, ip_port: tuple) -> dict :
    #global DATA
    #request["DATA"] = DATA
    #return request
    try :
        if request["OPERATION"] == "START" :
            global computing_thread
            print("##", request["DATA"], "##")
            computing_thread = threading.Thread(target=os.system, args=(request["DATA"],))
            computing_thread.start()
    except Exception as e :
        print(e)

SERVER_FTP = FTP_SERVER(path=PATH,
                        recv_chunk_size=RECV_CHUNK_SIZE,
                        transmission_chunk_size=TRANSMISSION_CHUNK_SIZE,
                        host="127.0.0.2",
                        port=11112,
                        encryption_key=ENCRYPTION_KEY,
                        decryption_key=DECRYPTION_KEY,
                        recv_buffer=RECV_BUFFER,
                        transmission_buffer=TRANSMISSION_BUFFER,
                        timeout=TIMEOUT,
                        debug1=True,
                        debug2=True
                        )

SERVER = CYPHER_SERVER(host="127.0.0.2",
                       port=11111,
                       recv_buffer=RECV_BUFFER,
                       transmission_buffer=TRANSMISSION_BUFFER,
                       encryption_key=ENCRYPTION_KEY,
                       decryption_key=DECRYPTION_KEY,
                       request_handler=HANDLE_REQUEST,
                       timeout=TIMEOUT,
                       debug1=True,
                       debug2=True
                       )

if __name__ == "__main__" :
    try :
        SERVER.start_server()
        SERVER_FTP.start_server()
        input()
        SERVER.stop_server()
        SERVER_FTP.stop_server()
    except :
        try :
            SERVER.stop_server()
            SERVER_FTP.stop_server()
        except : sys.exit(0)

