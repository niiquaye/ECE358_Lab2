import socket

# Use a dictionary for DNS lookup

# String -> Tuple"

HOST = "127.0.0.1"
PORT = 10002

DNS_table = {
    "google.com": ["A", "IN", 260, ["192.165.1.1", "192.165.1.10"]],
    "youtube.com": ["A", "IN", 160, ["192.165.1.2"]],
    "uwaterloo.org": ["A", "IN", 160, ["192.165.1.3"]],
    "wikipedia.org": ["A", "IN", 160, ["192.165.1.4"]],
    "amazon.ca": ["A", "IN", 160, ["192.165.1.5"]]
}



def get_url(QNAME: bytearray):
    # parse the octal request to get a string
    
    index = 0
    url_name = ""
    while True:
        # get the byte
        label_length = QNAME[index]
        index += 1
        if(label_length == 0):
            break
        for i in range(label_length):
            # get the byte
            char = QNAME[index]
            # use the integer as the ascii value of the char
            url_name += chr(char)
            index += 1
        # if the next character is a null label then break
        if(QNAME[index] == 0):
            return url_name
        # otherwise add a dot
        else:
            url_name += "."
    return url_name

def getDNSHeader(request_message: bytearray, url):
    # id is first 16 bits
    request_id = request_message[0:2]
    DNS_response_header = request_id
    # hardcode the flags since these are all given beforehand
    FLAGS = 0b1000010000000000
    DNS_response_header.extend((FLAGS).to_bytes(2, 'big'))
    
    #QDCOUNT

    DNS_response_header.extend((0x0001).to_bytes(2, 'big'))
    
    #ANCOUNT
    # this changes based on how many resources
    
    DNS_response_header.extend((len(DNS_table[url][3])).to_bytes(2, 'big'))
    
    #NSCOUNT
    
    DNS_response_header.extend((0x0000).to_bytes(2, 'big'))
    
    #ARCOUNT
    
    DNS_response_header.extend((0x0000).to_bytes(2, 'big'))
    return DNS_response_header

def getDNSAnswers(request_message):
    # Create a DNS answer
    DNS_response_answers = []
   
    # unpack question
    request_payload = request_message[12:]

    # remove the QType and QClass or the last 4 bytes
    request_payload_name = request_payload[:-4]
    url = get_url(request_payload_name)
    DNS_records = DNS_table[url.lower()]

    # generate response body         
    DNS_response_answer = bytearray()
    
    # NAME
    DNS_response_answer.extend((0xc00c).to_bytes(2, 'big'))
    
    # TYPE
    DNS_response_answer.extend((0x0001).to_bytes(2, 'big'))
    
    # CLASS
    DNS_response_answer.extend((0x0001).to_bytes(2, 'big'))
    
    # TTL
    DNS_response_answer.extend((DNS_records[2]).to_bytes(4, 'big'))

    # RDLENGTH
    # we know the rdlength as 4 
    DNS_response_answer.extend((0x0004).to_bytes(2, 'big'))
    
    for i in range(len(DNS_records[3])):
        DNS_response_answers.append(DNS_response_answer.copy())
    
    for i in range(len(DNS_records[3])):
        byte_ip_address = bytearray()
        # RDATA
        ip_address_array = DNS_records[3][i].split('.')
       
        for string in ip_address_array:
            #add each portion of the ip address as a byte
            byte_ip_address.extend((int(string)).to_bytes(1, 'big'))
       
    
        DNS_response_answers[i].extend(byte_ip_address)

    return DNS_response_answers, url
    
# main body 
if __name__ == "__main__":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            
            request_message = bytearray()
            print("waiting to receive data from client")
            data, client = s.recvfrom(1024)
            
            
            request_message.extend(data)
            # received message and parse the request message
            print("parsing message data")
            
            DNS_response_answers, url = getDNSAnswers(request_message)
            DNS_response_header = getDNSHeader(request_message, url)
        
        
            print("\n request message: \n", " ".join(hex(b) for b in request_message))
            # header
            response_message = DNS_response_header
            # question
            DNS_request_question =  request_message[12:]
            response_message += DNS_request_question
            # answer(s)
            for DNS_response_answer in DNS_response_answers:
                response_message += DNS_response_answer
            
            print("\n response message: \n", " ".join(hex(b) for b in response_message))
            # send back response
        
            s.sendto(response_message, client)
            print("done sending message to client")
        
    