import socket
import os
import glob

class UploadtoServer() :
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
        

class Client:
    def __init__(self):
        socketbind = 9000
        ip = "127.0.0.1"
        self.server = (ip, socketbind)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(self.server)
    
    def close(self):
        self.sock.send("#close")
    
    def menu(self):
        while(True):
            print("\n---- MENU ----\n1. Download from Servers\n2. upload to Servers\n3. List Directory")
            select = raw_input()
            select = int(select)
            if select == 1:
                self.sendMessage()
            elif select == 2:
                self.upload()
            elif select == 3:
                self.listDirectory()

    def listDirectory(self):
        listfile = os.listdir(".")

        print "--- Directory ---"
        for a in range(len(listfile)):
            print "%s. %s"%(a,listfile[a])
        return listfile

    def upload(self):
        selectedfile = self.listDirectory();
        select = raw_input()
        select = int(select)
        print selectedfile[select]
        send = UploadtoServer(self.sock, selectedfile[select],self.server)
        send.run()
    
    def sendMessage(self):
            
        self.sock.send("#askFiles")
        datas = (self.sock.recv(1024))
        datas = datas.strip()
        datas = datas.replace(' ','')
        datas = datas.replace('[','')
        datas = datas.replace(']','')
        datas = datas.replace('\'','')
        datas = datas.split(',')
        
        ranged = []
        for a in range(len(datas)):
            print ("%s. %s"%(a, datas[a]))
            ranged.append(a)   
        print("select by its number")
        fileask = raw_input()
        fileask = int(fileask)
        if not fileask in ranged:
            return self.sendMessage()
        
        first = True
        fileask = str(fileask)
        self.sock.sendall("#ask")
        self.sock.send(fileask)
        data = self.sock.recv(1024)

        
        if ("#sendingFile" in data):
            data = self.sock.recv(1024)
            if ("#start" in data):
                data= self.sock.recv(1024)
                filename = data.strip()
                data = filename.split('/')
                data = data[len(data)-1]
                filename = data
                print ("[+] receiving " + str(filename))
                print filename
                fp = open(filename, "wb+")
                while True:
                    data = self.sock.recv(1024)        
                    
                    if "##EOF" in data:
                        print(data)
                        print ("[-] received " + filename )
                        fp.close()
                        break
                    fp.write(data)
        else:
            
            while True:
                
                data = self.sock.recv(1024)
                
                if ("#directoryEnd" in data):
                    print "[-] all files done"
                    break
                
                elif ("#directoryName" in data):
                    
                    data = self.sock.recv(1024)
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
                    data= self.sock.recv(1024)
                    filename = data.strip()
                    print ("[+] receiving " + str(filename))
                    print filename
                    fp = open(filename, "wb+")
                    while True:
                        data = self.sock.recv(1024)        
                        
                        if "##EOF" in data:
                            fp.close()
                            break
                        fp.write(data)

if __name__ == "__main__":
    try:
        main = Client()
        main.menu()
    except KeyboardInterrupt:
        main.close()
        print("done")