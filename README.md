# TcpRawSocket
Handmade ip + tcp headers

Tcp protocol implementation on raw socket.
Connects to server, send syn, wait for syn-ack, sends ack, (sometimes wait for response), send query, wait for response.

Could be used for this CTF task: https://ctftime.org/task/8902

You should be root to use raw sockets.

By default system sends RST for all tcp connections it doesn't know, so you need to disable sending RST:
```
iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP
```

The source code is based on this aricles: http://www.campergat.com/tcp-raw-sockets-in-python/

## Examples: 
Sending `help me` message to ya.ru:
```
$ sudo python my_tcp.py --dest-ip 87.250.250.242 --dest-port 80 --query 'help me' 
use source ip:  192.168.1.35  and source port  7462
send SYN with seqno =  413100552
got some response, src_port =  80 , dst_port =  7462 , seqno =  4037794324 , ack =  413100553
flags: SYN =  1 , ACK =  1  PSH =  0  FIN =  0
('bytes: ', 'E\x00\x00,\x03\xcd\x00\x00;\x06gGW\xfa\xfa\xf2\xc0\xa8\x01#\x00P\x1d&\xf0\xab\xda\x14\x18\x9fj\t`\x12n(\xaa\x88\x00\x00\x02\x04\x05\x82')
got syn ack, sending ack
sleeping for one second...
send PSH + ACK, with user_query =  help me
, expected ack =  413100561
got some response, src_port =  80 , dst_port =  7462 , seqno =  4037794325 , ack =  413100561
flags: SYN =  0 , ACK =  1  PSH =  0  FIN =  0
('bytes: ', 'E\x00\x00(\x04\xbc\x00\x00;\x06f\\W\xfa\xfa\xf2\xc0\xa8\x01#\x00P\x1d&\xf0\xab\xda\x15\x18\x9fj\x11P\x10n(\xc2\x0b\x00\x00')
got ack for  413100561
got some response, src_port =  80 , dst_port =  7462 , seqno =  4037794325 , ack =  413100561
flags: SYN =  0 , ACK =  1  PSH =  1  FIN =  0
('bytes: ', 'E\x00\x00j\x04\xbd\x00\x00;\x06f\x19W\xfa\xfa\xf2\xc0\xa8\x01#\x00P\x1d&\xf0\xab\xda\x15\x18\x9fj\x11P\x18n(\x17\xa5\x00\x00HTTP/1.1 400 Bad request\r\nContent-Length: 0\r\nConnection: Close\r\n\r\n')
got some response, src_port =  80 , dst_port =  7462 , seqno =  4037794391 , ack =  413100561
flags: SYN =  0 , ACK =  1  PSH =  0  FIN =  1
('bytes: ', 'E\x00\x00(\x04\xbe\x00\x00;\x06fZW\xfa\xfa\xf2\xc0\xa8\x01#\x00P\x1d&\xf0\xab\xdaW\x18\x9fj\x11P\x11n(\xc1\xc8\x00\x00')
got FIN, exititng...
```

Solving CTF task above:
```
$ sudo python my_tcp.py --dest-ip 209.250.241.50 --dest-port 65226 --query GET_FLAG --wait-for-response --change-byte-order --no-end-of-line
use source ip:  192.168.1.35  and source port  7226
send SYN with seqno =  998721491
got some response, src_port =  65226 , dst_port =  7226 , seqno =  0 , ack =  998721492
flags: SYN =  1 , ACK =  1  PSH =  0  FIN =  0
('bytes: ', 'E\x00\x00(\x00\x01\x00\x005\x06\x00\xd7\xd1\xfa\xf12\xc0\xa8\x01#\xfe\xca\x1c:\x00\x00\x00\x00\xd4G\x87;P\x12 \x00\x94Q\x00\x00')
got syn ack, sending ack
got some response, src_port =  65226 , dst_port =  7226 , seqno =  1 , ack =  998721492
flags: SYN =  0 , ACK =  1  PSH =  1  FIN =  0
('bytes: ', "E\x00\x00O\x00\x01\x00\x005\x06\x00\xb0\xd1\xfa\xf12\xc0\xa8\x01#\xfe\xca\x1c:\x01\x00\x00\x00\xd4G\x87;P\x18 \x00k\xcc\x00\x00Send me 'GET_FLAG' and I give your flag")
send PSH + ACK, with user_query =  GET_FLAG , expected ack =  998721500
got some response, src_port =  65226 , dst_port =  7226 , seqno =  40 , ack =  998721500
flags: SYN =  0 , ACK =  1  PSH =  0  FIN =  0
('bytes: ', 'E\x00\x00(\x00\x01\x00\x005\x06\x00\xd7\xd1\xfa\xf12\xc0\xa8\x01#\xfe\xca\x1c:(\x00\x00\x00\xdcG\x87;P\x10 \x00dS\x00\x00')
got ack for  998721500
got some response, src_port =  65226 , dst_port =  7226 , seqno =  40 , ack =  998721500
flags: SYN =  0 , ACK =  1  PSH =  1  FIN =  0
('bytes: ', 'E\x00\x00J\x00\x01\x00\x005\x06\x00\xb5\xd1\xfa\xf12\xc0\xa8\x01#\xfe\xca\x1c:(\x00\x00\x00\xdcG\x87;P\x18 \x00\xaf\xa2\x00\x00cybrics{n0w_I_kn0w_how_cr@ft_tcp}\n')
send PSH + ACK, with user_query =  GET_FLAG , expected ack =  998721508
got some response, src_port =  65226 , dst_port =  7226 , seqno =  74 , ack =  998721500
flags: SYN =  0 , ACK =  0  PSH =  0  FIN =  0
('bytes: ', 'E\x00\x00(\x00\x01\x00\x005\x06\x00\xd7\xd1\xfa\xf12\xc0\xa8\x01#\xfe\xca\x1c:J\x00\x00\x00\xdcG\x87;P\x04 \x00B_\x00\x00')
got FIN, exititng...

```
