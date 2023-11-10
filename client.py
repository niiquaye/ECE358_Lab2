import socket
import os

SERVER_IP = "127.0.0.1"
PORT = 10002

def makeDNSHeader():
    DNS_response_header = bytearray()
    #ID
    random_bytes = os.urandom(2)
    DNS_response_header.extend(random_bytes)
    #Flags
    DNS_response_header.extend((0b0000010000000000).to_bytes(2, 'big'))
    #QDCount
    DNS_response_header.extend((0x0001).to_bytes(2, 'big'))
    #ANCOUNT
    DNS_response_header.extend((0x0000).to_bytes(2, 'big'))
    #NSCOUNT
    DNS_response_header.extend((0x0000).to_bytes(2, 'big'))
    #ARCOUNT
    DNS_response_header.extend((0x0000).to_bytes(2, 'big'))
    return DNS_response_header

def makeDNSBody(url):
    DNS_request_body = bytearray()
    #QNAME
    qname = bytearray()
    # url is split on .
    url_array = url.split('.')
    for label in url_array:
        # a section is www or google or com
       
        qname.extend(len(label).to_bytes(1, 'big'))
        for letter in label:
            qname.extend(ord(letter).to_bytes(1, 'big'))
    qname.extend((0x00).to_bytes(1, 'big'))
    DNS_request_body.extend(qname)
    #QTYPE
    DNS_request_body.extend((0x0001).to_bytes(2, 'big'))
    #QCLASS  
    DNS_request_body.extend((0x0001).to_bytes(2, 'big'))
        
    return DNS_request_body

def parseData(request: bytearray, response: bytearray) -> list:
    
    # parse the data
    # header is first 12 bytes
    response_header = response[0:12]
    # question is the same size as the request question
    size_of_question = len(request[12:])
    # starts from byte 12 to (12 + size of question) 
    response_question = response[12: (12 + size_of_question)]
    response_answers = response[(12 + size_of_question):]
  
    # Find number of answers from header from ANCOUNT
    number_of_answers = response_header[6:8]
    number_of_answers = int.from_bytes(number_of_answers, 'big')
    
    return parseAnswers(number_of_answers, response_answers)
    
        
#input answer output RData
def parseAnswers(number_of_answers : int, response_answers : bytearray):
    results = []
    index = 0
    for i in range(number_of_answers):
        result = {} 
        # Skip over the first two bytes since it's the name
        # Since it's assumed that name is 2 bytes long and constant
        index += 2
     
        # type is bytes 2 and 3 in the answer
        TYPE = response_answers[index: index + 2]
        index += 2
        
        TYPE = int.from_bytes(TYPE, 'big')
        if(TYPE == 1):
            result.update({"TYPE" : "A"})
        # class is bytes 4 and 5 in the answer
        CLASS = response_answers[index: index + 2]
        CLASS = int.from_bytes(CLASS, 'big')
        if(CLASS == 1):
            result.update({"CLASS" : "IN"})
        index += 2
        # TTL is bytes 6,7, 8 and 9
        TTL = response_answers[index: index + 4]
        TTL = int.from_bytes(TTL, 'big')
        result.update({"TTL" : TTL})
        index += 4
        
        # RDLENGTH is bytes 10 and 11
        RDLENGTH = response_answers[index: index + 2]
        RDLENGTH = int.from_bytes(RDLENGTH, 'big')
        
        result.update({"LENGTH": RDLENGTH})
        index += 2
        # RDATA is bytes 12 - 12 + RDLENGTH
        RDATA = response_answers[index: index + RDLENGTH]
        ip_string = ""
        for byte in RDATA:
            ip_string += str(byte)
            ip_string += '.'
            
        # remove the extra . from the string
        ip_string = ip_string[:-1]
        
        result.update({"ADDRESS": ip_string})
        index += RDLENGTH
        results.append(result)
    return results

if __name__ == "__main__":
    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            DNS_url = input("Enter Domain Name: ")
            if(DNS_url == "end"):
                s.close()
                print("Session Ended")
                break
            
            DNS_request_header = makeDNSHeader()
            DNS_request_body = makeDNSBody(DNS_url)
            
            # construct a DNS message
            
            print("client is sending DNS message")
            DNS_request_header.extend(DNS_request_body)
            request = DNS_request_header
            s.sendto(request, (SERVER_IP, PORT))
            print("client is waiting for response")
            response, server = s.recvfrom(2048)
            results = parseData(request, response)
            print(results)
            for result in results:
                print(DNS_url, 
                    "type ", result["TYPE"], ",", 
                    "class ", result["CLASS"], ",",
                    "TTL ", result["TTL"], ",",
                    "addr (", result["LENGTH"], ") ", result["ADDRESS"]
                    )
            
    