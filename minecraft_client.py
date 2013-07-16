from lxml import etree
import time
import socket
import subprocess
import shlex

current_mc = str("")
ramdisk_path = str("")
mc_path = str("")
mc_link = str("")
unpack_server = str("")

tree = etree.parse("config.xml")

def read_xpath(xpath):
   return (tree.xpath(xpath)[0].text).strip()

def read_config():
    global current_mc
    global ramdisk_path
    global mc_path
    global mc_link
    global unpack_server
    global world_path
    current_mc = read_xpath('/config/current_mc/value')
    ramdisk_path = read_xpath('/config/ramdisk_path/value')
    mc_path = read_xpath('/config/mc_variants/'+current_mc+'/path')
    mc_link = read_xpath('/config/mc_variants/'+current_mc+'/link')
    unpack_server = read_xpath('/config/mc_variants/'+current_mc+'/unpack_server')

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
        arg= "java -Xmx2048M -jar *server*.jar nogui"
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
        subprocess.call("unzip ./tmp/*Server*.zip -d ./tmp/extracted", shell=True)
        subprocess.call("cp -r ./tmp/extracted/* " + mc_path, shell=True)
    else:
        subprocess.call("cp ./tmp/*server*.jar " + mc_path, shell=True)
    subprocess.call("rm -r ./tmp/", shell=True)
    print(current_mc + " updated.")
    
def stop(time):
    if (status()==True):
        read_config()
        print (communicate("stop " + time))
        subprocess.call("rsync -ucr " + ramdisk_path + "* "+mc_path,shell=True)
        subprocess.call("rm -r " + ramdisk_path + "*", shell=True)
        print ("RAMdisk cleaned.")

def shutdown(time):
    stop(time)
    subprocess.call("sudo /sbin/shutdown -hP now", shell=True)
        
def restart():
    stop(str(0))
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
        backup_paths=[]
        backup_path = read_xpath('/config/backup_path/value')
        new_paths = list(map((lambda x: x.strip()), tree.xpath('/config/backup_paths/*/text()')))
        backup_paths.append(new_paths)
        print("Backing up " + str(new_paths))
                    
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
            stop(str(0))
            subprocess.call("sudo /sbin/shutdown -hP now", shell=True)
    
def status():
    status=communicate("status")
    print (status)
    if status=="Minecraft Server running.":
        return True
    else:
        return False
        
def switch(variant):
    if not tree.xpath('/config/mc_variants/'+variant):
        print("Please check your spelling/settings!")
        return
    tree.xpath('/config/current_mc/value')[0].text = variant
    tree.write("config.xml")
    print("Active minecraft variant changed to " + variant + ".")
    

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
