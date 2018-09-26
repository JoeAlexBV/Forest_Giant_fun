import socket
import argparse
import time
import ipaddress
import zlib

class CliInput():
    pass

c = CliInput()

command_line_parser = argparse.ArgumentParser(
    description='This script will send a packet to the specified ip and port by the user every two seconds...')

command_line_parser.add_argument('-p', '--port',
                                 type=int,
                                 action='store',
                                 default=5005,
                                 help='The desired port to send the packets.')

command_line_parser.add_argument('-hp', '--hostport',
                                 type=int,
                                 action='store',
                                 default=5005,
                                 help='The desired host port to send the packets.')

args = command_line_parser.parse_args(namespace=c)

udp_host_port = c.hostport
udp_port = c.port


"""
Create a UDP client & server in either Go, Node.js, or Python

It should have a command line flag that specifies the port and another flag to specify what host:port it should connect and send data to

This can be one application, that can act as either server/client, or two separate applications

Send one IPv4 UDP packet every two seconds with a payload of data

In the payload, byte encode the string `"It always seems impossible until it's done" - Nelson Mandela` along with a timestamp and the IPv4 address and port the sender is listening on

The payload of data should not exceed the default UDP MTU size (64k) and should be structured like this:

checksum (Adler32) - 4 bytes  

unix timestamp - 8 bytes  

ipv4 - 4 bytes  

port - 2 bytes  

Nelson Mandela quote

When the packet is received 

Print the quote

Print the time elapsed since the message was sent

Print the source IPv4 address

Print how many times that source IP sent a message
"""
# Time stuff
unix_ts = time.time()
unix_ts_int = int(unix_ts)

UDP_IP = "127.0.0.1"
ip_int = int(ipaddress.IPv4Address(UDP_IP))
# UDP_PORT = 5005  #  We are using the command line flags now.

# Starting up the Server:
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((UDP_IP, udp_host_port))

# Could give a stop condition of loop forever until Ctrl+C
ip_count = 0
while True:

    string = "\"It always seems impossible until it\'s done\" - Nelson Mandela"
    encoded_string = string.encode("utf-8")

    unix_ts_in_bytes = unix_ts_int.to_bytes(8, byteorder='big')
    # print('TS in bytes: ', unix_ts_in_bytes)

    ipv4_in_bytes = ip_int.to_bytes(4, byteorder='big')
    # print('IP in bytes: ', ipv4_in_bytes)

    port_in_bytes = udp_port.to_bytes(2, byteorder='big')
    # print('PORT in bytes: ', port_in_bytes)


    # NOTE: Disclaimer I do not know what a check sum is really, but with a little googling I thought that this was
    # the purpose that it serves...
    checksum = zlib.adler32((unix_ts_in_bytes + ipv4_in_bytes + port_in_bytes + encoded_string))
    # print(checksum)

    checksum_in_bytes = checksum.to_bytes(4, byteorder='big')
    # print('CS in bytes: ', checksum_in_bytes)

    payload = checksum_in_bytes + unix_ts_in_bytes + ipv4_in_bytes + port_in_bytes + encoded_string


    # Sending the message from Client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(3.0)
    start = time.time() # Start the timer
    client_socket.sendto(payload, (UDP_IP, udp_port))
    """
    When the packet is received 
    
    Print the quote
    
    Print the time elapsed since the message was sent
    
    Print the source IPv4 address
    
    Print how many times that source IP sent a message
    """
    try:
        data, server = server_socket.recvfrom(1024)  # buffer size is 1024 bytes
        end = time.time() # End the timer
        elapsed = end - start

        # print("message:", data)

        # Check sum
        cs = data[0:4]
        # print(cs)
        decoded_check_sum = int.from_bytes(cs, byteorder='big')
        # print(decoded_check_sum)

        #unix ts
        ts = data[4:12]
        # print(ts)
        decoded_time_stamp = int.from_bytes(ts, byteorder='big')
        # print(decoded_time_stamp)

        #ip
        ip = data[12:16]
        # print(ip)
        int_decoded_ip = int.from_bytes(ip, byteorder='big')
        decoded_ip = str(ipaddress.IPv4Address(int_decoded_ip))
        # There are some more intelligent ways to do this like storing the ips in a db or even a list, but the script
        # will be killed to input a new IP so a simple counter will do the trick.  Would consider something else if
        # there was a need...
        if decoded_ip == UDP_IP:
            ip_count += 1

        #port
        port = data[16:18]
        # print(port)
        decoded_port = int.from_bytes(port, byteorder='big')
        # print(decoded_port)

        #quote
        quote = data[18:]
        # print(quote)
        decoded_quote = quote.decode('utf-8', 'strict')
        print(decoded_quote)
        print(elapsed)
        print(decoded_ip)
        print(ip_count)

    except socket.timeout:
        print('Request timed out')

    time.sleep(2.0) #Send one IPv4 UDP packet every two seconds with a payload of data