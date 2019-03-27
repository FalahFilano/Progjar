import socket 
from threading import Thread 
import glob
from time import sleep
import os
from copy import copy
filelist = []

class SendtoClient() :
    def __init__(self, sock, filetosend, addr):
        self.sock = sock
        self.file = filetosend
        self.target = addr
    
    def sendFile(self, filename):
        print "[.] sending "+ filename +" to " + str(self.target)
        self.sock.send("#start".ljust(1024))
        self.sock.send(filename.ljust(1024))
        fp = open(filename, 'rb')
        while (True):
            payload = fp.read(1024)
            self.sock.send(payload.ljust(1024))
            if not payload:
                break
        self.sock.send("##EOF".ljust(1024))
    
    def directoryCrawler(self, directory):
        self.sock.send("#directoryName".ljust(1024))
        self.sock.send(directory.ljust(1024))
        os.chdir(directory)
        filelist = glob.glob("*")
        for files in filelist:
            
            if os.path.isdir(files):
                self.directoryCrawler( files)
                continue
            self.sendFile(files)
            
        os.chdir("..")
        self.sock.send("#directoryDone".ljust(1024))
            
    
    def run (self):
        print "[.] begin sending "+ self.file +" to " + str(self.target)
        isdir = os.path.isdir(self.file)
        if (isdir):
            self.sock.send("#directoryStart".ljust(1024))
            self.directoryCrawler(self.file)
            self.sock.send("#directoryEnd".ljust(1024))
        else :
            self.sock.send("#sendingFile".ljust(1024))
            self.sendFile(self.file)
        
        print "[-] finish sending "+ self.file +" to " + str(self.target)
        

class ReadFiles(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.selffile = "server.py"
        self.daemon = True
        self.setDaemon(True)
        self.timer = 5
    def run(self):
        while True:
            currentdir = "./"
            global filelist
            files = list(glob.glob('*'))
            files.remove(self.selffile)
            newfiles = copy(files)
            for x in files:
                if os.path.isdir(x):
                    newfiles+=(self.getaFolder( currentdir+x))
            files = newfiles
            filelist = copy(files)
            sleep(1)
            
    def stop(self):
        self.do_run = False
        
    def getaFolder(self, directory):
        globing = directory+"/*"
        files = list(glob.glob(globing))
        newfiles = copy(files)
        for x in files:
            if x == None:
                break
            if os.path.isdir(x):
                newfiles+=(self.getaFolder(x))
        return newfiles
        
    def runProto(self):
        files = glob.glob('*')
        files.remove(self.selffile)
        global filelist
        filelist = list( files)
        
        
class ServerforOne(Thread):
    def __init__(self, connection, addr):
        self.connection= connection
        Thread.__init__(self)
        print "[+] server created for "+ str(addr)
        self.target = addr

    def run(self):
        first = True
        while (True):
            data = self.connection.recv(1024)
            if "#askFiles" in data:
                lists = list(filelist)
                self.connection.sendall(str(lists))
                print("directory Given to Client")
            
            elif data == "#ask":  
                data = self.connection.recv(1024)
                askedfile = list(filelist)[int(data)]
                print ("[.]client asked " + askedfile)
                send = SendtoClient(self.connection, askedfile,self.target)
                send.run()
                #self.count +=1
            elif "#close" in data:
                print("[-] connection from "+ str(self.target) + "closed")
                break

            elif "#sendingFile" in data:
                data = self.connection.recv(1024)
                if ("#start" in data):
                    data= self.connection.recv(1024)
                    filename = data.strip()
                    data = filename.split('/')
                    data = data[len(data)-1]
                    filename = data
                    print ("[+] receiving " + str(filename))
                    print filename
                    fp = open(filename, "wb+")
                    while True:
                        data = self.connection.recv(1024)        
                        
                        if "##EOF" in data:
                            print(data)
                            print ("[-] received " + filename )
                            fp.close()
                            break
                        fp.write(data)

            elif "#directoryStart" in data:
                while True:
                    
                    data = self.connection.recv(1024)
                    
                    if ("#directoryEnd" in data):
                        print "[-] all files done"
                        break
                    
                    elif ("#directoryName" in data):
                        
                        data = self.connection.recv(1024)
                        data = data.strip()
                        if(first):
                            data = data.split('/')
                            data = data[len(data)-1]
                        print "[+] receiving directory" +data
                        if (not os.path.exists(data)):
                            os.mkdir(data)
                        os.chdir(data)
                        
                    elif ("#directoryDone" in data):
                        print "[-] current directory done"
                        os.chdir('..')
                        
                    elif("#start" in data):
                        data= self.connection.recv(1024)
                        filename = data.strip()
                        print ("[+] receiving " + str(filename))
                        print filename
                        fp = open(filename, "wb+")
                        while True:
                            data = self.connection.recv(1024)        
                            
                            if "##EOF" in data:
                                fp.close()
                                break
                            fp.write(data)


class Server():
    def __init__(self):
        socketbind = 9000
        ip = "127.0.0.1"
        self.socketbind = (ip, socketbind)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.socketbind)
        

    def loop (self): 
        while (True):
            self.sock.listen(1)
            connection, source = self.sock.accept()
            print connection
            print source
            newthread = ServerforOne(connection, source)
            newthread.start()
            

if __name__ == "__main__":
    main = Server()
    try:
        filefinder = ReadFiles()
        filefinder.start()

        main.loop()
    except KeyboardInterrupt :
        filefinder.stop()
        main.sock.close()
    