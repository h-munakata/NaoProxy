# -*- coding: utf-8 -*-
from naoqi import ALProxy
import socket 
import utils
import json
import sys

class NAOProxy:
    def __init__(self, path_json_behavior, ip_server, port_server, ip_NAO, port_NAO, send_message=True):
        self.send_message = send_message
        self.path_json_behavior = path_json_behavior
        self.init_NAO(ip_NAO, port_NAO)
        print "waiting client"
        self.init_server(ip_server, port_server)


    def init_NAO(self, ip_NAO, port_NAO):
        connection_success = False
        num_retry = 5
        for i in range(num_retry):
            try:
                self.say = NAO_Say(ip_NAO, port_NAO)
                self.motion = NAO_Motion(ip_NAO, port_NAO, self.path_json_behavior)
                connection_success = True
                break
            except:
                print "[!] Some type of error has occured. Retrying to connect"
                continue
        
        if connection_success:
            print "Success to connect to NAO"
        else:
            raise RuntimeError("Can't connect to NAO. exit this program")
        


    def init_server(self, ip_server, port_server):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((ip_server, port_server))
        self.sock.listen(1)
        self.sock.settimeout(100)
        try:
            self.client, self.address_server = self.sock.accept()
            print('success to connect to client. IP:{}, port:{}'.format(self.address_server[0], self.address_server[1]))
        except:
            self.disconnect()


    def wait_message(self,buffer_size=1024):
        try:
            json_message = self.client.recv(buffer_size)
        except:
            print "vital error has occured"
            self.disconnect()
        try:
            message = json.loads(json_message)
            return message
        except:
            self.send('{"result":"message has some wrong"}')
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

                result_value = "something is wrong"
                try:
                    if message_type=='playmotion':
                        result_value = self.motion.play(value)

                    elif message_type=='say':
                        result_value = self.say.say(value)

                    self.send('{"result":"xxx"}'.replace("xxx",result_value))

                except:
                    self.send('{"result":"xxx"}'.replace("xxx",result_value))
                


    def send(self,message):
        if self.send_message:
            self.client.send(message)
        else:
            pass



class NAO_Say:
    def __init__(self, ip_NAO, port_NAO):
        self.audioProxy = ALProxy("ALTextToSpeech", ip_NAO, port_NAO)

    def say(self, message):
        self.audioProxy.post.say(message.encode("UTF-8"))
        return "succeed-end"


class NAO_Motion:
    def __init__(self, ip_NAO, port_NAO, path_json_behavior):
        json_behavior = open(path_json_behavior,'r')
        behavior = json.load(json_behavior)
        self.playmotion = behavior["playmotion"]

        self.proxy = ALProxy("ALMotion", ip_NAO, port_NAO)
        self.proxy.stiffnessInterpolation("Body", 0.9, 1.0)

        # Refer to ALFrameManager.py
        self.frame = ALProxy("ALFrameManager", ip_NAO, port_NAO)


    def play(self, key_motion):
        if key_motion in self.playmotion.keys():
            print "playing..."
            path_xar = self.playmotion[key_motion]
            id = self.frame.newBehaviorFromFile(path_xar.encode("UTF-8"), "")
            self.frame.playBehavior(id)

            return "succeed-end"
        else:
            return "can't handle the message"

    def exit(self):
        self.frame.cleanBehaviors()


if __name__ == "__main__":
    ip_NAO = sys.argv[1]
    port_NAO = int(sys.argv[2])
    ip_server = sys.argv[3]
    port_server = int(sys.argv[4])
    send_message = bool(sys.argv[5])
    path_json_behavior = "./behavior.json"

    nao_proxy = NAOProxy(path_json_behavior, 
                        ip_server, port_server,
                        ip_NAO, port_NAO,
                        send_message=True)
    
    nao_proxy.process_message()