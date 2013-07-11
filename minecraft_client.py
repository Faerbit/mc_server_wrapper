import xml.dom.minidom as dom
import time
import socket
import subprocess
import shlex

current_mc = str("")
ramdisk_path = str("")
mc_path = str("")
mc_link = str("")
unpack_server = str("")

def read_config():
    global current_mc
    global ramdisk_path
    global mc_path
    global mc_link
    global unpack_server
    global world_path
    config = dom.parse("config.xml")    
    for config_entry in config.firstChild.childNodes:
        if config_entry.nodeName == "current_mc":
            for data_entry in config_entry.childNodes:
                if data_entry.nodeName == "value":
                    current_mc = data_entry.firstChild.data.strip()
        if config_entry.nodeName == "ramdisk_path":
            for data_entry in config_entry.childNodes:
                if data_entry.nodeName == "value":
                    ramdisk_path = data_entry.firstChild.data.strip()
        if config_entry.nodeName == "mc_variants":
            for data_entry in config_entry.childNodes:
                if data_entry.nodeName == current_mc:
                    for mc_data_entry in data_entry.childNodes:
                        if mc_data_entry.nodeName == "path":
                            mc_path = mc_data_entry.firstChild.data.strip()
                        if mc_data_entry.nodeName == "link":
                            mc_link = mc_data_entry.firstChild.data.strip()
                        if mc_data_entry.nodeName == "unpack_server":
                            unpack_server = mc_data_entry.firstChild.data.strip()
    if mc_path =="" : 
        print ("Reading config file failed! Please check your settings!")
        return False
    return True

def config_test():                        
    if read_config():
        print (current_mc)
        print (ramdisk_path)
        print (mc_path)
        print (mc_link)
        print (unpack_server)

def start():
    if(status()==False):
        read_config()
        subprocess.call("cp -r " + mc_path + "* " + ramdisk_path, shell=True)
        print("Minecraft copied to RAM.")
        arg= "java -Xmx2048M -jar *server*.jar"
        call = "python minecraft_daemon.py \"" + arg + "\" " + ramdisk_path
        call = shlex.split(call)
        subprocess.Popen(call)
        time.sleep(2)
        status()
    else:
        print ("Minecraft Server already running!")

def update():
    read_config()
    if (status()==True):
        stop()
    print ("Making backup prior to update.")
    backup("update")
    subprocess.call("mkdir ./tmp", shell=True)
    download=subprocess.Popen("wget " + mc_link, shell=True, cwd ="./tmp/")
    download.wait()
    if (unpack_server=="true"):
        subprocess.call("unzip ./tmp/*Server.zip -d ./tmp/extracted", shell=True)
        subprocess.call("cp -r ./tmp/extracted/* " + mc_path, shell=True)
    else:
        subprocess.call("cp ./tmp/*server.jar " + mc_path, shell=True)
    subprocess.call("rm -r ./tmp/", shell=True)
    print(current_mc + " updated.")
    
def stop():
    if (status()==True):
        read_config()
        print (communicate("stop"))
        subprocess.call("rsync -ucr " + ramdisk_path + "* "+mc_path,shell=True)
        subprocess.call("rm -r " + ramdisk_path + "*", shell=True)
        print ("RAMdisk cleaned.")
        
def restart():
    stop()
    start()
    
def ramdisk_saverun():
    if (status()==True):
        read_config()
        if (communicate("start saverun")=="saving off"):
            subprocess.call("rsync -ucr " + ramdisk_path + "* " + mc_path,shell=True)
            print ("RAMdisk synced.")
            print (communicate("end saverun"))
        else:
            print ("Saverun failed to turn off saving!")
        
def backup(option):
    if (status()==True):
        config = dom.parse("config.xml")
        backup_paths=[]
        for config_entry in config.firstChild.childNodes:
            if config_entry.nodeName == "backup_path":
                for data_entry in config_entry.childNodes:
                    if data_entry.nodeName == "value":
                        backup_path = data_entry.firstChild.data.strip()
            if config_entry.nodeName == "backup_paths":
                for data_entry in config_entry.childNodes:
                    if (data_entry.firstChild):
                        backup_paths.append(data_entry.firstChild.data.strip())
                        print("Backing up " + data_entry.firstChild.data.strip())
                    
        if (option=="regular" or option=="update"):
            print ("Backing up to "+ backup_path + "backup_" + option + "_1.")
            subprocess.call("rm -r " + backup_path + "backup_"+ option + "_3", shell=True)
            subprocess.call("mv " + backup_path + "backup_" + option + "_2 " + backup_path + "backup_" + option + "_3", shell=True)
            subprocess.call("mv " + backup_path + "backup_" + option + "_1 " + backup_path + "backup_" + option + "_2", shell=True)
            subprocess.call("mkdir " + backup_path + "backup_" + option + "_1", shell=True)
            for path in backup_paths:
                subprocess.call("cp --parents -r " + path + " " + backup_path + "backup_" + option + "_1", shell=True)
                print("Backing up of " + path + " is complete.")                
            
def check_players():
    if (status()==True):
        number=communicate("check players")
        number=number[37]
        print("There are " + number + " players online.")
        if (number=="0"):
            config = dom.parse("config.xml")
            for config_entry in config.firstChild.childNodes:
                if config_entry =="username":
                    for data_entry in config_entry.childNodes:
                        if data_entry.nodeName == "value"
                        username = data_entry.firstChild.data.strip()
            if mc_path =="" : 
                print ("Reading config file failed! Please check your settings!")
                return False

            subprocess.call(" sudo -u " + username + " python3 minecraft_args.py stop", shell=True)
            subprocess.call("sudo shutdown -hP now", shell=True)
    
def status():
    status=communicate("status")
    print (status)
    if status=="Minecraft Server running.":
        return True
    else:
        return False
        
def switch(variant):
    config = dom.parse("config.xml")
    for config_entry in config.firstChild.childNodes:
        if config_entry.nodeName == "mc_variants":
            for data_entry in config_entry.childNodes:
                if data_entry.nodeName == variant:
                    for config_entry_2 in config.firstChild.childNodes:
                        if config_entry_2.nodeName == "current_mc":
                            for data_entry_2 in config_entry_2.childNodes:
                                if data_entry_2.nodeName == "value":
                                    data_entry_2.firstChild.data=variant
                                    config.writexml(open ("config.xml","w+"))
                                    print("Active minecraft variant changed to " + variant + ".")
                                    return()
            else:
                print("Please check your spelling/settings!")
    
def command(cmd):
    print (communicate("command "+cmd))
    
def communicate (command):
    sock=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect("server_socket")
    except socket.error as e:
        if e.errno == 2:
            return ("Minecraft Server not running.")
    try:
        sock.sendall(command.encode('utf_8'))
    except socket.error as e:
        if e.errno == 107:
            print("Removing server_socket")
            subprocess.Popen("rm -f server_socket", shell=True)
            return ("Minecraft Server not running.")
    data=(sock.recv(4096)).decode('utf-8')
    sock.close()
    return data
