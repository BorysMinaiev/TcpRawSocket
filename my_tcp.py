# SHOULD BE RUN AS ROOT TO WORK WITH RAW SOCKETS!
# Almost whole code is copied from http://www.campergat.com/tcp-raw-sockets-in-python/
# Some fixes were add
# Before using program you NEED to do disable sending RST packets by system:
# iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
# reason for that could be found in article above


import socket

import tcppacket as rs
import random
import time
import argparse

def get_my_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))  # connect() for UDP doesn't send packets
    return s.getsockname()[0]

def calc_ack(ip_header, tcp_header):
    data_len = ip_header.total_len - ip_header.ihl * 4 - tcp_header.header_len
    ack_packet_id = tcp_header.seq_no + data_len
    if tcp_header.syn or tcp_header.fin:
        ack_packet_id = ack_packet_id + 1
    return ack_packet_id

def send_ack(s, ip_header, tcp_header):
    ack_packet_id = calc_ack(ip_header, tcp_header)
    iphead = rs.construct_ip_header(srcip, destip)
    tcphead = rs.construct_tcp_header(srcip, destip, tcp_header.dst_port, destport, tcp_header.ack_no,
                                      ack_packet_id,
                                      [0, 0, 0, 0, 1, 0, 0, 0, 0])
    tcppacket = rs.construct_tcp_packet(iphead, tcphead)
    s.sendto(tcppacket, (destip, destport))

def send_user_query(s, ip_header, tcp_header):
    ack_packet_id = calc_ack(ip_header, tcp_header)
    user_data = ''
    if user_query is not None:
        user_data = user_query
        if add_end_of_line:
            user_data = user_data + '\n'

    iphead = rs.construct_ip_header(srcip, destip)
    tcphead = rs.construct_tcp_header(srcip, destip, tcp_header.dst_port, destport, tcp_header.ack_no,
                                      ack_packet_id,
                                      [0, 0, 0, 0, 1, 1, 0, 0, 0], user_data)
    tcppacket = rs.construct_tcp_packet(iphead, tcphead, user_data)
    s.sendto(tcppacket, (destip, destport))
    print 'send PSH + ACK, with user_query = ', user_data, ', expected ack = ', len(user_data) + tcp_header.ack_no

def try_read_from_socket(s):
    raw_buffer = s.recv(4096)
    ip_header = rs.IP(raw_buffer[0:20])
    tcp_header = rs.TCP(raw_buffer[20:40])
    if tcp_header.src_port == destport and tcp_header.dst_port == srcport:
        print 'got some response, src_port = ', tcp_header.src_port, ', dst_port = ', tcp_header.dst_port, \
            ', seqno = ', tcp_header.seq_no, ', ack = ', tcp_header.ack_no
        print 'flags: SYN = ', tcp_header.syn, ', ACK = ', tcp_header.ack, ' PSH = ', tcp_header.psh, ' FIN = ', \
            tcp_header.fin
        print ('bytes: ', raw_buffer[0:4000])
        if tcp_header.syn and tcp_header.ack:
            print 'got syn ack, sending ack'
            send_ack(s, ip_header, tcp_header)

            if not wait_for_response:
                print 'sleeping for one second...'
                time.sleep(1)
                send_user_query(s, ip_header, tcp_header)

        elif wait_for_response and tcp_header.psh:
            send_user_query(s, ip_header, tcp_header)
        elif tcp_header.syn or tcp_header.fin or (ip_header.total_len - ip_header.ihl * 4 - tcp_header.header_len > 0):
            send_ack(s, ip_header, tcp_header)
        elif tcp_header.ack:
            print 'got ack for ', tcp_header.ack_no
        if tcp_header.fin or tcp_header.rst:
            print 'got FIN, exititng...'
            exit(0)

def send_syn(s, destip):
    iphead = rs.construct_ip_header(srcip, destip)
    seqno = random.randint(1, 10 ** 9)
    print 'send SYN with seqno = ', seqno
    tcphead = rs.construct_tcp_header(srcip, destip, srcport, destport, seqno, 0, [0, 0, 0, 0, 0, 0, 0, 1, 0])
    tcppacket = rs.construct_tcp_packet(iphead, tcphead)
    s.sendto(tcppacket, (destip, destport))


def create_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    s.bind((srcip, srcport))
    return s

parser = argparse.ArgumentParser(description='Connects to server (do three-way handshake), sends one command, receives result')
parser.add_argument('--dest-ip', dest='destip', action='store', help='destination ip')
parser.add_argument('--dest-port', dest='destport', action='store', help='destination port', type=int)
parser.add_argument('--query', dest='query', action='store', help='user query to send')
parser.add_argument('--wait-for-response', dest='wait_for_response', action='store_true', help='waits server to send hello')
parser.add_argument('--change-byte-order', dest='change_byte_order', action='store_true', help='do strange stuff for https://ctftime.org/task/8902')
parser.add_argument('--no-end-of-line', dest='no_end_of_line', action='store_true', help='do not end user data with \n')


args = parser.parse_args()

destip = args.destip
destport = args.destport
user_query = args.query
wait_for_response = args.wait_for_response
if args.change_byte_order:
    rs.change_byte_order = True
add_end_of_line = True
if args.no_end_of_line:
    add_end_of_line = False

if destip is None or destport is None:
    print("You should specify destination ip and port")
    exit(1)

srcip = get_my_ip()
srcport = random.randint(1, 10000)
print 'use source ip: ', srcip, ' and source port ', srcport

conn_socket = create_socket()

send_syn(conn_socket, destip)

while True:
    try_read_from_socket(conn_socket)