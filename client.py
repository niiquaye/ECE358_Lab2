import socket
import os

HOST = "127.0.0.1"
PORT = 10001

def makeDNSHeader():
    DNS_response_header = bytearray
    #ID
    DNS_response_header.append(os.urandom(4))
    #Flags
    DNS_response_header.append(bytes(0b00000100000000000))
    #QDCount
    DNS_response_header.append(bytes(0x0001))
    #ANCOUNT
    DNS_response_header.append(bytes(0x0000))
    #NSCOUNT
    DNS_response_header.append(bytes(0x0000))
    #ARCOUNT
    DNS_response_header.append(bytes(0x0000))
    return DNS_response_header

def makeDNSBody(url):
    DNS_request_body = bytearray
    #QNAME
    qname = bytearray
    # url is split on .
    url_array = url.split('.')
    for label in url_array:
        # a section is www or google or com
        # labe
        qname.append(bytes(int(label.size(), 8)))
        for letter in label:
            qname.append(bytes(int(label, 8)))
    DNS_request_body.append(qname)
    #QTYPE
    DNS_request_body.append(bytes(0x0001))
    #QCLASS  
    DNS_request_body.append(bytes(0x0001))
        
    return DNS_request_body

def parseData(response):
    # parse the data
    # header is first 10 bytes
    response_header = response[0:10]
    # remaining bytes are the answer
    response_body = response[10:]
    # Since it's assumed that name is 2 bytes long
    # type is bytes 2 and 3 in the answer
    TYPE = response[2:4]
    # class is bytes 4 and 5 in the answer
    CLASS = response[4:6]
    # TTL is bytes 6,7, 8 and 9
    TTL = response[6:10]
    # RDLENGTH is bytes 10 and 11
    RDLENGTH = response[10:12]
    # RDATA is bytes 12+
    RDATA = response[12:]
    
    
    

if __name__ == "__main__":
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print("client is waiting for server to open")
        s.connect((HOST, PORT))
        print("connected to server")
        while True:
            DNS_url = input("Enter Domain Name: ")
            if(DNS_url == "end"):
                print("Session Ended")
                break
            
            DNS_request_header = makeDNSHeader()
            DNS_request_body = makeDNSBody(DNS_url)
            
            # construct a DNS message
            
            print("client is sending DNS message")
            s.sendall(DNS_request_header + DNS_request_body)
            print("client is waiting for response")
            response = s.recv(2048)
            TYPE, CLASS, TTL, sizes, addresses = parseData(response)
            
            for i in range(addresses):
                # print multiple if RDlength is long
                print(DNS_url, 
                    "type", TYPE, 
                    "class", CLASS,
                    "TTL", TTL,
                    "addr (", sizes[i], ")", addresses[i]
                    )
    