# -*- coding: utf-8 -*-
from naoqi import ALProxy
import socket 
import json
import argparse

class NAOSpeechProxy:
    def __init__(self, path_json_behavior, ip_client, port_client, ip_NAO, port_NAO, send_message=True):
        self.send_message = send_message
        self.path_json_behavior = path_json_behavior
        self.init_NAO(ip_NAO, port_NAO)
        print "waiting client"
        self.connect_client(ip_client, port_client)


    def init_NAO(self, ip_NAO, port_NAO):
        connection_success = False
        num_retry = 5
        for i in range(num_retry):
            try:
                self.speech = NAOSpeech(ip_NAO, port_NAO)
                connection_success = True
                break
            except:
                print "[!] Some type of error has occured. Retrying to connect"
                continue
        
        if connection_success:
            print "Success to connect to NAO"
        else:
            raise RuntimeError("Can't connect to NAO.")
        


    def connect_client(self, ip_client, port_client):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip_client, port_client))
        self.sock.listen(1)
        self.sock.settimeout(100)
        try:
            self.client, self.address_client = self.sock.accept()
            print('Success to connect to client. IP:{}, port:{}'.format(self.address_client[0], self.address_client[1]))
        except:
            self.disconnect()


    def wait_message(self,buffer_size=1024):
        try:
            json_message = self.client.recv(buffer_size)
        except:
            print "A vital error has occured."
            self.disconnect()
        try:
            message = json.loads(json_message)
            return message
        except:
            self.send('{"result":"something is wrong"}')
            return None


    def process_message(self):
        while(1):
            print 'waiting message'
            message = self.wait_message()
            if message==None:
                pass
            else:
                print 'recieved message:{}'.format(message)
                message_type, value  = message.items()[0]

                try:
                    self.speech.say(value)
                    self.send('{"result":"succeed-end"}')

                except:
                    self.send('{"result":"something is wrong"}')


    def send(self,message):
        if self.send_message:
            self.client.send(message)
        else:
            pass


class NAOSpeech:
    def __init__(self, ip_NAO, port_NAO):
        self.audioProxy = ALProxy("ALTextToSpeech", ip_NAO, port_NAO)

    def say(self, message):
        self.audioProxy.post.say(message.encode("UTF-8"))
        return "succeed-end"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Motion Proxy for NAO') 

    parser.add_argument('ip_NAO', type=str)
    parser.add_argument('port_NAO', type=int)
    parser.add_argument('ip_client', type=str)
    parser.add_argument('port_client', type=int)
    parser.add_argument('-m', action='store_true', help="Send messages of the result to client")
    args = parser.parse_args()
    path_json_behavior = "./behavior.json"

    nao_proxy = NAOSpeechProxy(path_json_behavior, 
                        args.ip_client, args.port_client,
                        args.ip_NAO, args.port_NAO,
                        send_message=args.m)
    
    nao_proxy.process_message()