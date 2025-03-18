import time
import os
import json
import urllib3
import sys
from pathlib import Path
from threading import Thread
from datetime import datetime
from subprocess import run, check_output, Popen, PIPE, STDOUT
import pandas as pd
from io import StringIO
import psutil
import timeit
import argparse
import platform
import re
import json

# command to get LEDA card information
ledagssh    =   "ledag-ssh -o localhost"

def get_leda_info(check_boards=None, get_clock_rate=True, verbose=False, raise_exc=True):
    '''Get LedaG card info and optionally check boards availability.'''

    if verbose: print("%s: Getting LEDA info..." % sys.argv[0])

    slotx = re.compile("slot(\d+)@localhost")
    freqx = re.compile(".*freq\s*(\d+)")
    slots = [] # will populate with slot(s) summary info
    clock_rate = {} # will populate with clock rate
    slot_history = {} #tracks select prompting history
    slot_prompting = False # help us track the nested prompting
    slot_selected = -1 # track current slot prompt
    def _next_slot_cmd(p, num_slots):
        #print("_next_slot:", num_slots, clock_rate.keys(), range(num_slots))

        clocks = list( clock_rate.keys() )
        history = list( slot_history.keys() )
        if len( clocks ) == len( range(num_slots) ):
            return ("done",)

        elif len( clocks ) < len( history ):
            # figure out which slot is next
            cmd = "fwp\n"
            p.stdin.write( bytes(cmd,'utf-8'))
            p.stdin.flush()
            remaining = sorted( list( set(range(num_slots)) - set(clock_rate) ) )[0]
            clock_rate[remaining]=None
            return ("clock", remaining)

        elif len( history ) < len( range(num_slots) ):
            remaining = sorted( list( set(range(num_slots)) - set(slot_history) ) )[0]
            cmd = "select %d\n" % remaining
            p.stdin.write( bytes(cmd,'utf-8'))
            p.stdin.flush()
            slot_history[remaining]=None
            return ("slot",remaining)
        else:   
            raise Exception("Unhandled state")

    #
    # This is gnarly code to invoke the ledagssh command,
    # async capture the output, detect the ledagssh prompt,
    # and send it the quit command, and capture any error
    # code when the process exits.
    #
    cmd = ledagssh.split()
    if verbose: print("%s: Running leda command" % sys.argv[0], cmd)
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.poll()!=None:
            if verbose: print("%s: leda command terminated." % sys.argv[0])
            if p.returncode!=0:
                print("%s: ERROR: Leda command returned error code %d" % ( sys.argv[0], p.returncode))
                return False
            else: break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        if verbose: print("%s: leda output: %s" % ( sys.argv[0], bs), end="")

        if not slot_prompting:
            # within the top-level prompt mode
            if bs.find("slot")>=0:
                slots.append( bs )
            if bs.startswith("localhost >"):
                if verbose: print()
                retv = _next_slot_cmd( p, len(slots) )
                if retv[0]=="slot": slot_selected = retv[1]
                slot_prompting=True
        else:
            # within theselected board prompting mode

            # check its a board prompt and get selected board id
            matches =slotx.match(bs)
            if matches and matches.groups():
                brd = int(matches.groups()[0])
                if verbose: print("got slot prompt", brd)
                retv = _next_slot_cmd( p, len(slots) )
                if retv[0]=="slot": 
                    slot_selected = retv[1]
                elif retv[0]=="done":
                    p.communicate( str.encode("quit") ) # this will terminate the ssh connection
                    break
            elif bs.find("freq")>=0: # else its the output of a board command
                freq = int( freqx.match(bs).groups()[0] )
                clock_rate[slot_selected]=freq

    if verbose: print("%s: ledag slot info:" % sys.argv[0], slots)

    if check_boards!=None: # check we have min available boards
        if verbose: print("%s: Checking boards availability..." % sys.argv[0])
        if len(slots) < check_boards:
            print("%s: ERROR: Only found %d slots and requesting %d" % ( sys.argv[0], len(slots), check_boards) )
            raise Exception("Board(s) check failed.")

    # here we check that enumerated boards are working/available as best we can
    str_int_sort = [ int(j) for j in sorted([ str(i) for i in range( len(slots)) ]) ]
    for idx, i in enumerate(str_int_sort):
        slot = slots[idx]
        decoded = eval( slot.replace("\x1b[1m\x1b[33mslot%d\x1b[0m" % i,"").strip() )
        if verbose: print("%s: " % sys.argv[0], decoded)
        if decoded["FW Status"] != "background":
            if raise_exc:
                raise Exception("There is a problem with FW with board at slot %d" % i)
            else:
                print("WARNING: There is a problem with FW with board at slot %d" % i)

    # return number of boards and the board slot details array
    return len(slots), slots, clock_rate


def get_leda_power(check_boards=None, get_board_power=True, continuous=True, verbose=False):
    '''Get LedaG card info and calculated power.'''

    if verbose: print("%s: Getting LEDA info..." % sys.argv[0])

    slotx = re.compile("slot(\d+)@localhost")
    freqx = re.compile(".*freq\s*(\d+)")
    slots = [] # will populate with slot(s) summary info
    board_power = {} # will populate with board power
    slot_history = {} #tracks select prompting history
    slot_prompting = False # help us track the nested prompting
    slot_selected = -1 # track current slot prompt
    def _next_slot_cmd(p, num_slots):
        if verbose: print("_next_slot:", num_slots, board_power.keys(), range(num_slots))

        bps = list( board_power.keys() )
        history = list( slot_history.keys() )
        if len( bps ) == len( range(num_slots) ):
            return ("done",)

        elif len( bps ) < len( history ):
            # figure out which slot is next
            cmd = "calc_pwr\n"
            if verbose: print("sending cmd", cmd)
            p.stdin.write( bytes(cmd,'utf-8'))
            p.stdin.flush()
            remaining = sorted( list( set(range(num_slots)) - set(board_power) ) )[0]
            board_power[remaining]=None
            return ("bp", remaining)

        elif len( history ) < len( range(num_slots) ):
            remaining = sorted( list( set(range(num_slots)) - set(slot_history) ) )[0]
            cmd = "select %d\n" % remaining
            if verbose: print("sending cmd", cmd)
            p.stdin.write( bytes(cmd,'utf-8'))
            p.stdin.flush()
            slot_history[remaining]=None
            return ("slot",remaining)

        else:
            raise Exception("Unhandled state")

    #
    # This is gnarly code to invoke the ledagssh command,
    # async capture the output, detect the ledagssh prompt,
    # and send it the quit command, and capture any error
    # code when the process exits.
    #
    cmd = ledagssh.split()
    if verbose: print("%s: Running leda command" % sys.argv[0], cmd)
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    os.set_blocking(p.stdout.fileno(), False)
    while True:
        if p.poll()!=None:
            if verbose: print("%s: leda command terminated." % sys.argv[0])
            if p.returncode!=0:
                print("%s: ERROR: Leda command returned error code %d" % ( sys.argv[0], p.returncode))
                return False
            else: break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        if verbose: print("%s: leda output: %s" % ( sys.argv[0], bs), end="")

        if not slot_prompting:
            # within the top-level prompt mode
            if bs.find("slot")>=0:
                slots.append( bs )
            if bs.startswith("localhost >"):
                if verbose: print()
                retv = _next_slot_cmd( p, len(slots) )
                if retv[0]=="slot": slot_selected = retv[1]
                slot_prompting=True
        else:
            # within theselected board prompting mode

            # check its a board prompt and get selected board id
            matches =slotx.match(bs)
            if matches and matches.groups():
                brd = int(matches.groups()[0])
                if verbose: print("got slot prompt", brd)
                retv = _next_slot_cmd( p, len(slots) )
                if retv[0]=="slot":
                    slot_selected = retv[1]
                elif retv[0]=="done":
                    if continuous:
                        board_power = {} 
                        slot_history = {} 
                        if verbose: print("looping...")
                        retv = _next_slot_cmd( p, len(slots) )
                        if retv[0]=="slot": slot_selected = retv[1]
                        slot_prompting=True
                    else:
                        if verbose: print("quitting...")
                        p.communicate( str.encode("quit") ) # this will terminate the ssh connection
                        break
            elif bs.find("Board Power")>=0: # else its the output of a board command
                #freq = int( freqx.match(bs).groups()[0] )
                board_power[slot_selected]=bs.strip()
                if verbose: print("got power", bs.strip())

    if verbose: print("%s: ledag slot info:" % sys.argv[0], slots)

    if check_boards!=None: # check we have min available boards
        if verbose: print("%s: Checking boards availability..." % sys.argv[0])
        if len(slots) < check_boards:
            print("%s: ERROR: Only found %d slots and requesting %d" % ( sys.argv[0], len(slots), check_boards) )
            raise Exception("Board(s) check failed.")

    # here we check that enumerated boards are working/available as best we can
    str_int_sort = [ int(j) for j in sorted([ str(i) for i in range( len(slots)) ]) ]
    for idx, i in enumerate(str_int_sort):
        slot = slots[idx]
        decoded = eval( slot.replace("\x1b[1m\x1b[33mslot%d\x1b[0m" % i,"").strip() )
        if verbose: print("%s: " % sys.argv[0], decoded)
        if decoded["FW Status"] != "background":
            raise Exception("There is a problem with the board at slot %d" % i)

    # return number of boards and the board slot details array
    return len(slots), slots, board_power

def get_leda_board(verbose=False):
    '''Get LedaG card board type.'''

    if verbose: print("%s: Getting LEDA info..." % sys.argv[0])

    slotx = re.compile("slot(\d+)@localhost")
    slots = [] # will populate with slot(s) summary info
    slot_history = {} #tracks select prompting history
    slot_prompting = False # help us track the nested prompting
    slot_selected = -1 # track current slot prompt
    waiting = 0 # flag that signals when wating on a response
    waitCount = 0 # timeout for waiting on slot response 
    def _next_slot_cmd(p, num_slots, waiting):
        #print("_next_slot:", num_slots, clock_rate.keys(), range(num_slots))

        history = list( slot_history.keys() )
        if waiting:
            return ("done",)

        elif len( history ) < len( range(num_slots) ):
            remaining = sorted( list( set(range(num_slots)) - set(slot_history) ) )[0]
            cmd = "select %d\n" % remaining
            p.stdin.write( bytes(cmd,'utf-8'))
            p.stdin.write( bytes("brd_type\n",'utf-8'))
            p.stdin.flush()
            slot_history[remaining]=None
            return ("slot",remaining)
        elif len( history ) == len( range(num_slots) ):
            print("No responsive slots. Could not retrieve card type.")
            return None
        else:   
            raise Exception("Unhandled state")

    #
    # This is gnarly code to invoke the ledagssh command,
    # async capture the output, detect the ledagssh prompt,
    # and send it the quit command, and capture any error
    # code when the process exits.
    #
    cmd = ledagssh.split()
    if verbose: print("%s: Running leda command" % sys.argv[0], cmd)
    p = Popen( cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
    os.set_blocking(p.stdout.fileno(), False)
    
    while True:
        if p.poll()!=None:
            if verbose: print("%s: leda command terminated." % sys.argv[0])
            if p.returncode!=0:
                print("%s: ERROR: Leda command returned error code %d" % ( sys.argv[0], p.returncode))
                return None
            else: break
        b = p.stdout.readline()
        if b==b'':
            time.sleep(0.01)
            continue
        bs = b.decode('utf-8')
        checkString = str(bs).split()
        if(checkString[0] == "board_type:"):
            return checkString[1]
        if verbose: print("%s: leda output: %s" % ( sys.argv[0], bs), end="")

        if not slot_prompting:
            # within the top-level prompt mode
            if bs.find("slot")>=0:
                slots.append( bs )
            if bs.startswith("localhost >"):
                if verbose: print()
                retv = _next_slot_cmd( p, len(slots), waiting )
                if retv[0]=="slot": slot_selected = retv[1]
                waiting = 1
                slot_prompting=True
        else:
            # within theselected board prompting mode

            # check its a board prompt and get selected board id
            matches =slotx.match(bs)
            if matches and matches.groups():
                brd = int(matches.groups()[0])
                if verbose: print("got slot prompt", brd)
                retv = _next_slot_cmd( p, len(slots), waiting)
                if retv[0]=="slot": 
                    slot_selected = retv[1]
                    waiting = 1
                elif retv[0]=="done":
                    if verbose: print("waiting")
                    #keeping waiting for a response
                    #then try another slot
                    if waitCount > 10:
                        waiting = 0
                        waitCount = 0
                    waitCount += 1
                elif retv[0] == None:
                    return None



if __name__ == "__main__":
    
    print("%s: Unit tests: Starting..." % sys.argv[0])
    print()
    print("%s: Calling 'get_leda_power'..." % sys.argv[0])
    retv = get_leda_info(verbose=False)
    print("%s: Got leda info..." % sys.argv[0])
    print(retv)
    print()
    print("%s: Calling 'get_leda_power'..." % sys.argv[0])

    retv = get_leda_power(continuous=False, verbose=False)
    print("%s: Got leda info..." % sys.argv[0])
    print(retv)
    print()
    print("%s: Unit tests: Done." % sys.argv[0])

    

