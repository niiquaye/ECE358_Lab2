import socket

# Use a dictionary for DNS lookup

# String -> Tuple"

HOST = "127.0.0.1"
PORT = 10001

DNS_table = {
    "google.com": ["A", "IN", 260, ["192.165.1.1", "192.165.1.10"]],
    "youtube.com": ["A", "IN", 160, ["192.165.1.2"]],
    "uwaterloo.org": ["A", "IN", 160, ["192.165.1.3"]],
    "wikipedia.org": ["A", "IN", 160, ["192.165.1.4"]],
    "amazon.ca": ["A", "IN", 160, ["192.165.1.5"]]
}



def get_url(request_payload_name):
    # parse the octal request to get a string
    index = 0
    url_name = ""
    while True:
        
        label_length = request_payload_name[index]
        index += 1
        if( int(label_length, 8) == 0):
            break
        for i in range(label_length):
            url_name += chr(int(request_payload_name[index], 8))
            index += 1
        # if the next character is a null label then break
        if(request_payload_name[index] == 0):
            break;
        # otherwise add a dot
        else:
            url_name += "."
    return url_name

def getDNSHeader(request_message):
    # id is first 16 bits
    request_id = request_message[0:2]
    DNS_response_header = request_id
    # hardcode the flags since these are all given beforehand
    FLAGS = 0b1000010000000000
    FLAGS = bytes(FLAGS)
    DNS_response_header.append(FLAGS)
    
    #QDCOUNT

    DNS_response_header.append(bytes(0x0001))
    
    #ANCOUNT
    
    DNS_response_header.append(bytes(0x0001))
    
    #NSCOUNT
    
    DNS_response_header.append(bytes(0x0000))
    
    #ARCOUNT
    
    DNS_response_header.append(bytes(0x0000))
    return DNS_response_header

def getDNSBody(request_message):
           
    # unpack question
    request_payload = request_message[10:]
    
    # remove the QType and QClass or the last 4 bytes
    request_payload_name = request_payload[:-4]
    
    
    url = get_url(request_payload_name)
    
    DNS_records = DNS_table[url]

    # generate response body
                
    DNS_response_body = bytearray()
    
    # NAME
    
    DNS_response_body.append(bytes(0xc00c))
    
    # TYPE
    
    DNS_response_body.append(bytes(0x0001))
    
    # CLASS
    
    DNS_response_body.append(bytes(0x0001))
    
    # TTL
    
    DNS_response_body.append(bytes(DNS_records[2]))
    
    
    # RDLENGTH
    # we know the rdlength as 4 * #of ip_addresses and convert it to oct
    # pad with zfill in case not enough zeroes
    # finally turn it into a byte form so it can be added to the byte array
    
    DNS_response_body.append(bytes(oct((DNS_records[3].size() * 4)).zfill(4)))
    
    for ip_address in DNS_records[3]:
        # RDATA
        ip_address_array = ip_address.split('.')
        
        for string in ip_address_array:
            #add each portion of the ip address as an octal
            DNS_response_body.append(bytes(int(string, 8)))
            
        
        
        
    return DNS_response_body
    

if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
       
        print("server is listening for a connection on", PORT)
        s.listen()
        conn, addr = s.accept()
        print("accepted a connection")
        with conn:
            
            request_message = bytearray()
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                request_message.append(bytearray(data))
            # received message and parse the request message
            print("parsing message data")
            DNS_response_header = getDNSHeader(request_message)
            DNS_response_body = getDNSBody(request_message)
        
           
            print(request_message)
            response_message = DNS_response_header + DNS_response_body
            print(response_message)
            # send back response
         
            conn.sendall(response_message)
            print("done sending message to client")
 