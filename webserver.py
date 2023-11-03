from socket import *
from email.utils import format_datetime, formatdate
from enum import Enum
import datetime
import os 



SERVER_IP = "127.0.0.1"
SERVER_PORT = 10005
SERVER_NAME = "Webserver" #https://piazza.com/class/llomgydu5c3tm/post/247
CR_LF = "\r\n" # needed after the end of each line in header for some reason 

# to do a get request run the following
#http://127.0.0.1:10005/orson/HelloWorld.html

class RequestType(Enum):
    HEAD = 1
    GET = 2

def parse_file(file_name):
    file_contents = []
    with open(file_name) as f:
        file_contents = f.read()
    return file_contents

def get_file_name(request):
    # get file name from http request by looking for the first occurence
    # of a '/' then incrementing string pointer until a ' ' has been found 

    start = request.find('/')
    start += 1
    end = 0

    while end < len(request) and request[start + end] != ' ':
        end += 1

    file_name = request[start: start+end]
    return file_name

def generate_reponse_header(request):
    # Header Contains the following fields:
    # 1. Connection
    # 2. Date
    # 3. Server
    # 4. Last-Modified
    # 5. Content-Length
    # 6. Content-Type
    print('Generating Response Header')

    # use time now for time message request was created as
    # there is virtually no delay of any sorts since client is running from local source
    utc_date = str(formatdate(timeval=None, localtime=False, usegmt=True))
    date = "Date: " + utc_date + CR_LF

    server_name = "Server:" + SERVER_NAME + CR_LF
    connection = "Connection:" + "keep-alive" + CR_LF
    content_type = "Content-Type:" + "text/html" + CR_LF
    content_length = "Content-Length:" + str(0) + CR_LF # if file not found content length will remain 0 - ERROR 404
    last_modified = "Last-Modified:" + utc_date + CR_LF# if file not found date last modified will be trivially set to date of request

    # https://stackoverflow.com/questions/1321878/how-to-prevent-favicon-ico-requests
    # certain browsers send a request for favicon.ico but it does not always exist

    file_name = get_file_name(request)

    if not os.path.isfile(file_name):
        print("ERROR 404")
    else:

        file_name = get_file_name(request)
        content_length = "Content-Length:"  + str(os.stat(file_name).st_size) + CR_LF # file size in bytes 

        # get time file was last modified
        # RFC 1123 format needed for datetime 
        modify_time = os.path.getmtime(file_name)
        modify_date = datetime.datetime.fromtimestamp(modify_time)
        modify_date_utc = modify_date.astimezone(datetime.timezone.utc)
        last_modified = "Last-Modified:" + str(format_datetime(modify_date_utc, usegmt=True)) + CR_LF


    

    # construct header
    header_lines = date + server_name + last_modified + content_length + content_type + connection + CR_LF

    #print("HTTP Header Response: \n{}".format(header_lines))

    return header_lines




def parse_http_request(request, type):
    status_line = ""
    file_contents = ""
    # if file not found send error 404
    if not os.path.isfile(get_file_name(request)):
        status_line = "HTTP/1.1 404 Not Found" + CR_LF
    else:
        status_line = "HTTP/1.1 200 OK" + CR_LF
        file_contents = parse_file(get_file_name(request))
    
    header_lines = generate_reponse_header(request)

    file_contents_to_send = file_contents if type == RequestType.GET else ""

    response = status_line + header_lines + file_contents_to_send

    return response


def server():
    # 1. socket 
    # 2. bind 
    # 3. listen 
    # 4. accept 
    # 5. read 
    # 6. write 
    # 7. close 
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind((SERVER_IP, SERVER_PORT))
    serverSocket.listen(1)
    print ("The server is ready to receive")
    while True:
        connectionSocket, addr = serverSocket.accept()
        http_request = connectionSocket.recv(2048).decode()

        http_response = ""
        if http_request[0:3] == "GET":
            print('GET Request')
            http_response = parse_http_request(http_request, RequestType.GET)
        elif http_request[0:4] == "HEAD":
            print('HEAD Request')
            http_response = parse_http_request(http_request, RequestType.HEAD)


        connectionSocket.send(http_response.encode())
        connectionSocket.close()


if __name__ == "__main__":
    server()