from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
import pika
import sys
from threading import Thread
from time import sleep

PORT = 1234


class RabbitMQ():
    def __init__(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        self.channel = connection.channel()

        self.channel.exchange_declare(exchange='direct_logs',type='direct')

        result = self.channel.queue_declare(exclusive=True)
        self.queue_name = result.method.queue

        self.channel.queue_bind(exchange='direct_logs', queue=self.queue_name, routing_key='info')



class Chat(LineReceiver):

    def __init__(self, users):
        self.users = users
        self.name = None
        self.state = "GETNAME"
        self.rabbitMQ = RabbitMQ()


    def connectionMade(self):
    	self.clients=+1
    	message = "Welcome to connection manager... send me your user id"
        self.sendLine(message)

    def connectionLost(self, reason):
        if self.name in self.users:
            del self.users[self.name]

    def lineReceived(self, line):
        if self.state == "GETNAME":
            self.handle_GETNAME(line)
        else:
            self.handle_CHAT(line)

    def handle_GETNAME(self, name):
        if name in self.users:
            self.sendLine("Name taken, please choose another.")
            return
        self.name = name
        self.users[name] = self
        self.sendLine("User accepted, we have now %s clients" % (len(self.users)))
        self.state = "CHAT"
        
        thread = Thread(target = self.startConsuming)
        thread.start()

    def startConsuming(self):
        print ' [*] Waiting for logs. To exit press CTRL+C'
        self.rabbitMQ.channel.basic_consume(self.callback, queue=self.rabbitMQ.queue_name)
        self.rabbitMQ.channel.start_consuming()

    def callback(self, ch, method, properties, body):
        print self.users
        print " [x] %r:%r" % (method.routing_key, body,)
        for name, protocol in self.users.iteritems():
            protocol.sendLine(body)


    def handle_CHAT(self, message):
        message = "<%s> %s" % (self.name, message)
        for name, protocol in self.users.iteritems():
            if protocol != self:
                protocol.sendLine(message)


class ChatFactory(Factory):

    def __init__(self):
        self.users = {} # maps user names to Chat instances

    def buildProtocol(self, addr):
        return Chat(self.users)

reactor.listenTCP(PORT, ChatFactory())
print "Waiting for connections at -%s- port" %(PORT)
reactor.run()