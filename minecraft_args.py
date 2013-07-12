#! /usr/bin/python
import minecraft_client as mc
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=['start', 'stop', 'update', 'restart', 'backup', 'check_players', 'status', 'switch', 'ramdisk_saverun', 'command', 'config_test', 'shutdown'])
parser.add_argument("command", nargs='?')
args=parser.parse_args()
if args.action=='start':
    mc.start()
if args.action=="stop":
    if (args.command == None):
        mc.stop(0)
    else:
        mc.stop(int(args.command))
if args.action=="shutdown":
    if (args.command == None):
        mc.shutdown(0)
    else:
        mc.shutdown(int(args.command))
if args.action=="update":
    mc.update()
if args.action=="restart":
    mc.restart()
if args.action=="backup":
    mc.backup("regular")
if args.action=="check_players":
    mc.check_players()
if args.action=="status":
    mc.status()
if args.action=="switch":
    if args.command==None:
        print ("Please enter a minecraft variant!")
    else:
        mc.switch(args.command)
if args.action=="ramdisk_saverun":
    mc.ramdisk_saverun()
if args.action=="command":
    if args.command==None:
        print ("Please enter a command!")
    elif args.command=="stop":
        print ("Please use the stop method provided by this script!")
    else:
        mc.command(args.command)
if args.action=="config_test":
    mc.config_test()
