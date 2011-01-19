#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# V0.1, 2009-03-18, birlinn@gmail.com
# V0.2, 2009-04-03, birlinn@gmail.com
#
########################################################################
# preliminaries
########################################################################

import random, curses, locale, sys, string, traceback

# we need this to be able to print the non-ascii suit symbols...
locale.setlocale(locale.LC_ALL,"")

# dictionaries for manipulating the 'cards'
cvals  = {1: 'A', 10: 'X', 11: 'J', 12: 'Q', 13: 'K'}
cclrs  = {u'\u2660': 'black',
          u'\u2661': 'red',
          u'\u2663': 'black',
          u'\u2662': 'red'}
# dictionary for mapping player input codes to base list numbers
bdict = {'w': 0, 'x': 1, 'y': 2, 'z': 3}

########################################################################
# game functions
########################################################################

def make_deck():
    """
    Build the deck of cards in the cdeck dictionary
    """
    global cdeck
    cdeck  = {}
    cfaces = range(1, 14)
    # suits are represented by the unicode string of the suit symbols
    # u2660 = spades, u2661 = hearts, u2663 = clubs, u2662 = diamonds
    csuits = [u'\u2660', u'\u2661', u'\u2663', u'\u2662']
    cnt = 0
    for xs in cfaces:
        for zs in csuits:
            cdeck[cnt] = (xs, zs)
            cnt += 1

def make_play_stacks():
    """
    Make a list of 7 lists to represent each of the 'play stacks'
    """
    global stack
    stack = []
    for xs in range(7):
        stack.append([[]])

def make_base_stacks():
    """
    Make a list of 4 lists, one for each of the 'base stacks'
    """
    global base
    base = []
    for xs in range(4):
        base.append([])

def shuffle_deck():
    """
    The random.shuffle() function implements a Fisher-Yates shuffle i think
    """
    global shufks
    shufks = []
    unshufks = cdeck.keys()
    random.shuffle(unshufks)
    for xs in unshufks:
        shufks.append(xs)
    # a few extra shuffles... superstition?
    for xs in range(7):
        random.shuffle(shufks)

def _deal_deck(val):
    """
    This function is used by map() in deal_deck()
    """
    stack[val].append(cdeck.pop(shufks.pop()))

def deal_deck():
    """
    Deal the shuffled cards to the stacks [0] - [6]
    """
    stacktot = 0
    while stacktot < 7:
        map(_deal_deck, range(stacktot, 7, 1))
        stacktot += 1

def do_turn():
    """
    Turn over the top card of a stack if it doesn't have any visible cards
    """
    for xs in stack:
        if xs[0] == []:
            if xs == [[]]:
                pass
            else:
                xs[0].append(xs.pop())

def do_waste():
    """
    Add a new card to the waste heap while there are cards in the deck
    """
    if len(cdeck) > 0:
        waste.append(cdeck.pop(shufks.pop()))    
    else:
        display_error()

def new_game():
    """
    Create a new game
    """
    make_deck()
    make_play_stacks()
    make_base_stacks()
    shuffle_deck()
    deal_deck()
    do_turn()
    # create the waste
    global waste
    waste = []
    do_waste()
    # user moves get appended to the 'inp' list
    global inp
    inp = []

def do_move():
    """
    This is where we test the player input for legality and move the
    cards when it is legal to do so
    """
    global dpos, spos
    if len(inp) > 0:
        if len(inp) % 2 != 0:
            pass
        else:
            dpos = inp[-1:][0]
            spos = inp[-2:-1][0]
            # destination is stack
            if dpos in ('0', '1', '2', '3', '4', '5', '6'):
                # check if dest stack is empty
                if len(stack[int(dpos)][0]) == 0:
                    _w2es()           # waste to empty stack
                    _s2es()           # stack to empty stack
                    _b2es()           # base to empty stack
                # or if dest stack is populated
                elif len(stack[int(dpos)][0]) > 0:
                    _w2ps()           # waste to populated stack
                    _s2ps()           # stack to populated stack
                    _b2ps()           # base to populated stack
            # destination is base
            elif dpos in ('w', 'x', 'y', 'z'):
                # check if dest base is empty
                if len(base[bdict[dpos]]) == 0:
                    _w2eb()           # waste to empty base
                    _s2eb()           # stack to empty base
                    _b2eb()           # base to empty base
                # or if dest base is populated
                elif len(base[bdict[dpos]]) > 0:
                    _w2pb()           # waste to populated base
                    _s2pb()           # stack to populated base
                    _b2pb()           # base to populated base not allowed
            # ignore everything else, e.g. 'a -> a'
            else:
                display_error()
    else:
        pass

def _w2es():
    """
    Waste to empty stack
    """
    if spos == 'a':
        if len(waste) > 0:
            # card must be a king
            if waste[-1][0] == 13:
                stack[int(dpos)][0].append(waste.pop())
            else:
                display_error()
        else:
            display_error()

def _w2ps():
    """
    Waste to populated stack
    """
    if spos == 'a':
        if len(waste) > 0:
            # value of source card = value of dest. card - 1
            if waste[-1][0] == (stack[int(dpos)][0][-1][0] - 1):
                # colour of source card does not match colour of dest card
                if cclrs[waste[-1][1]] != cclrs[stack[int(dpos)][0][-1][1]]:
                    stack[int(dpos)][0].append(waste.pop())
                else:
                    display_error()
            else:
                display_error()
        else:
            display_error()

def _w2eb():
    """
    Waste to empty base
    """
    if spos == 'a':
        if len(waste) > 0:
            # card must be an ace
            if waste[-1][0] == 1:
                base[bdict[dpos]].append(waste.pop())
            else:
                display_error()
        else:
            display_error()

def _w2pb():
    """
    Waste to populated base
    """
    if spos == 'a':
        if len(waste) > 0:
            # value of source card = value of dest. card + 1
            if waste[-1][0] == (base[bdict[dpos]][-1][0] + 1):
                # suit of source card matches suit of dest card
                if waste[-1][1] == base[bdict[dpos]][-1][1]:
                    base[bdict[dpos]].append(waste.pop())
                else:
                    display_error()
            else:
                display_error()
        else:
            display_error()

def _s2es():
    """
    Stack to empty stack
    """
    if spos in ('0', '1', '2', '3', '4', '5', '6'):
        # criminalise 'n -> n'
        if spos != dpos:
            if len(stack[int(spos)][0]) > 0:
                for xs in stack[int(spos)][0]:
                    # card must be a king
                    if xs[0] == 13:
                        stack[int(dpos)][0].extend(stack[int(spos)][0][0:])
                        del stack[int(spos)][0][0:]
                        do_turn()
                    else:
                        display_error()
            else:
                display_error()
        else:
            display_error()

def _s2ps():
    """
    Stack to populated stack
    """
    if spos in ('0', '1', '2', '3', '4', '5', '6'):
        # criminalise 'n -> n'
        if spos != dpos:
            if len(stack[int(spos)][0]) > 0:
                cnt = 0
                matched = None             # don't like this!
                # iterate through the source cards until we find a match
                for xs in stack[int(spos)][0]:
                    if xs[0] == (stack[int(dpos)][0][-1][0] - 1):
                        if cclrs[xs[1]] != cclrs[stack[int(dpos)][0][-1][1]]:
                            stack[int(dpos)][0].extend(stack[int(spos)][0][cnt:])
                            del stack[int(spos)][0][cnt:]
                            do_turn()
                            matched = True # don't like this!
                    cnt += 1
                if matched == True:        # don't like this!
                    pass                   # don't like this!
            else:
                display_error()
        else:
            display_error()

def _s2eb():
    """
    Stack to empty base
    """
    if spos in ('0', '1', '2', '3', '4', '5', '6'):
        if len(stack[int(spos)][0]) > 0:
            # card must be an ace
            if stack[int(spos)][0][-1][0] == 1:
                base[bdict[dpos]].append(stack[int(spos)][0].pop())
                do_turn()
            else:
                display_error()
        else:
            display_error()

def _s2pb():
    """
    Stack to populated base
    """
    if spos in ('0', '1', '2', '3', '4', '5', '6'):
        if len(stack[int(spos)][0]) > 0:
            # value of source card = value of dest. card + 1
            if stack[int(spos)][0][-1][0] == (base[bdict[dpos]][-1][0] + 1):
                # suit of source card matches suit of dest card
                if stack[int(spos)][0][-1][1] == base[bdict[dpos]][-1][1]:
                    base[bdict[dpos]].append(stack[int(spos)][0].pop())
                    do_turn()
                else:
                    display_error()
            else:
                display_error()
        else:
            display_error()

def _b2es():
    """
    Base to empty stack
    """
    if spos in ('w', 'x', 'y', 'z'):
        if len(base[bdict[spos]]) > 0:
            if base[bdict[spos]][-1][0] == 13:
                stack[int(dpos)][0].append(base[bdict[spos]].pop())
            else:
                display_error()
        else:
            display_error()

def _b2ps():
    """
    Base to populated stack
    """
    if spos in ('w', 'x', 'y', 'z'):
        if len(base[bdict[spos]]) > 0:
            if base[bdict[spos]][-1][0] == (stack[int(dpos)][0][-1][0] - 1):
                if cclrs[base[bdict[spos]][-1][1]] \
                        != cclrs[stack[int(dpos)][0][-1][1]]:
                    stack[int(dpos)][0].append(base[bdict[spos]].pop())
                else:
                    display_error()
            else:
                display_error()
        else:
            display_error()

def _b2eb():
    """
    Base to empty base
    """
    if spos in ('w', 'x', 'y', 'z'):
        # criminalise 'x -> x'
        if spos != dpos:
            if len(base[bdict[spos]]) > 0:
                # this _could_ be changed to allow multiple cards to be moved
                # to an empty base
                if base[bdict[spos]][-1][0] == 1:
                    base[bdict[dpos]].append(base[bdict[spos]].pop())
                else:
                    display_error()
            else:
                display_error()
        else:
            display_error()

def _b2pb():
    """
    Base to populated base: not allowed
    """
    if spos in ('w', 'x', 'y', 'z'):
        if dpos in ('w', 'x', 'y', 'z'):
            if spos != dpos:
                display_error()
            else:
                display_error()

########################################################################
# curses functions
########################################################################

#
# untrad visual mode
#

def display_waste():
    """
    Draw the waste
    """
    # start by presenting the state of 'cdeck'
    if len(cdeck) > 0:
        screen.addstr(2, 1, 'd:[??]')
    else:
        screen.addstr(2, 1, 'd:[--]')
    # display the contents of the 'top' item in the waste
    if len(waste) > 0:
        # replace numerical vals with face vals where needed
        if waste[-1][0] in (1, 10, 11, 12, 13):
            av = 'a:[' + cvals[waste[-1][0]] + waste[-1][1] + ']'
        else:
            av = 'a:[' + str(waste[-1][0]) + waste[-1][1] + ']'
        screen.addstr(3, 1, av.encode('utf_8'))
        screen.refresh()
    # empty waste
    else:
        av = 'a:[--]'
        screen.addstr(3, 1, av.encode('utf_8'))
        screen.refresh()

def display_stacks():
    """
    Draw the play stacks (tableau)
    """
    # iterate through the 'stack' list and display its contents
    cnt = 0
    for xs in stack:
        # 'n:[]'
        if xs == [[]]:
            sv = str(cnt) + ':[--][--]' + ' '*screenx
            screen.addstr((5 + cnt), 1, sv)
            screen.refresh()
        elif len(xs) == 1:
            # 'n:[2♠]'
            if len(xs[0]) == 1:
                # replace numerical vals with face vals where needed
                if xs[0][0][0] in (1, 10, 11, 12, 13):
                    sv = str(cnt) + ':[--][' + cvals[xs[0][0][0]] \
                         + xs[0][0][1] + ']' + ' '*screenx
                else:
                    sv = str(cnt) + ':[--][' + str(xs[0][0][0]) \
                         + xs[0][0][1] + ']' + ' '*screenx
                screen.addstr((5 + cnt), 1, sv.encode('utf_8'))
                screen.refresh()
            #'n:[3♡, 2♠]'
            elif len(xs[0]) > 1:
                tl = []
                for ys in xs[0]:
                    # replace numerical vals with face vals where needed
                    if ys[0] in (1, 10, 11, 12, 13):
                        tl.append(cvals[ys[0]] + ys[1])
                    else:
                        tl.append(str(ys[0]) + ys[1])
                sv = str(cnt) + ':[--][' + string.join(tl, ', ') + ']' \
                     + ' '*screenx
                screen.addstr((5 + cnt), 1, sv.encode('utf_8'))
                screen.refresh()
        elif len(xs) > 1:
            #'n:[n'][2♠]'
            if len(xs[0]) == 1:
                # replace numerical vals with face vals where needed
                if xs[0][0][0] in (1, 10, 11, 12, 13):
                    sv = str(cnt) + ':[' + str(len(xs[1:])).rjust(2) + '][' \
                         + cvals[xs[0][0][0]] + xs[0][0][1] + ']' + ' '*screenx
                else:
                    sv = str(cnt) + ':[' + str(len(xs[1:])).rjust(2) + '][' \
                         + str(xs[0][0][0]) + xs[0][0][1] + ']' + ' '*screenx
                screen.addstr((5 + cnt), 1, sv.encode('utf_8'))
                screen.refresh()
            #'n:[n'][3♡, 2♠]'
            elif len(xs[0]) > 1:
                tl = []
                for ys in xs[0]:
                    # replace numerical vals with face vals where needed
                    if ys[0] in (1, 10, 11, 12, 13):
                        tl.append(cvals[ys[0]] + ys[1])
                    else:
                        tl.append(str(ys[0]) + ys[1])
                sv = str(cnt) + ':[' + str(len(xs[1:])).rjust(2) + '][' \
                     + string.join(tl, ', ') + ']' + ' '*screenx
                screen.addstr((5 + cnt), 1, sv.encode('utf_8'))
                screen.refresh()
        else:
            display_error() # ???
        cnt += 1

def display_bases():
    """
    Draw the base stacks (foundations)
    """
    # iterate through the 'base' list and display its contents
    cnts = 0
    ll = ['z', 'y', 'x', 'w']
    for xs in base:
        if len(xs) == 0:
            bv = ll.pop() + ':[--]' + ' '*screenx
            screen.addstr((13 + cnts), 1, bv)
            screen.refresh()
        else:
            tl = []
            for ys in xs:
                if ys[0] in (1, 10, 11, 12, 13):
                    tl.append(cvals[ys[0]] + ys[1])
                else:
                    tl.append(str(ys[0]) + ys[1])
            bv = ll.pop() + ':[' + string.join(tl, ', ') + ']' + ' '*screenx
            screen.addstr((13 + cnts), 1, bv.encode('utf_8'))
            screen.refresh()
        cnts += 1

#
# trad visual mode
#

# standard hspace between stack denominators (a, w, 6 etc.) is 6 cols
csp = ' ' * 5
# waste deck with cards in it
nof = '|???| '
# deck (or any other stack) with no cards in it
noctb = '----- '
nocmb = '+++++ '
# card top/bottom
ctb = '+---+ '

def display_trad_waste():
    """
    Draw the waste and bases
    """
    # draw waste and base headings line
    lh0 = '  ' + 'd' + csp + 'a' + ' ' * 17 + 'w' + csp + 'x' + csp + 'y' \
          + csp + 'z'
    screen.addstr(2, 1, lh0)
    # prepare lines 0, 1 & 2, i.e the deck, the waste and the 4 bases
    if len(cdeck) > 0:
        dpv0 = ctb
        dpv1 = nof
        dpv2 = ctb
    else:
        dpv0 = noctb
        dpv1 = nocmb
        dpv2 = nocmb
    if len(waste) > 0:
        av0 = ctb
        if waste[-1][0] in (1, 10, 11, 12, 13):
            av1 = '|' + cvals[waste[-1][0]] + ' ' + waste[-1][1] + '| '
        else:
            av1 = '|' + str(waste[-1][0]) + ' ' + waste[-1][1] + '| '
        av2 = ctb
    else:
        av0 = noctb
        av1 = nocmb
        av2 = nocmb
    tl = []
    for xs in base:
        if len(xs) > 0:
            tl.append(ctb)
            if xs[-1][0] in (1, 10, 11, 12, 13):
                tl.append('|' + cvals[xs[-1][0]] + ' ' + xs[-1][1] + '| ')
            else:
                tl.append('|' + str(xs[-1][0]) + ' ' + xs[-1][1] + '| ')
            tl.append(ctb)
        else:
            tl.append(noctb)
            tl.append(nocmb)
            tl.append(nocmb)

    l0 = dpv0 + av0 + ' ' * 12 + tl[:1][0] + tl[3:4][0] + tl[6:7][0] + \
         tl[9:10][0]
    l1 = dpv1.encode('utf_8') + av1.encode('utf_8') + ' ' * 12 \
             + tl[1:2][0].encode('utf_8') + tl[4:5][0].encode('utf_8') \
             + tl[7:8][0].encode('utf_8') + tl[10:11][0].encode('utf_8')
    l2 = dpv2 + av2 + ' ' * 12 + tl[2:3][0] + tl[5:6][0] + tl[8:9][0] + \
         tl[11:12][0]
    screen.addstr(3, 1, l0)
    screen.addstr(4, 1, l1)
    screen.addstr(5, 1, l2)
    screen.refresh()

def display_trad_stacks():
    """
    Draw the play stacks (tableau)
    """
    # draw play stack headings line
    lh1 = ' ' * 8 + '0' + csp + '1' + csp + '2' + csp + '3' + csp + '4' + \
          csp + '5' + csp + '6'
    screen.addstr(7, 1, lh1)
    # start mangling stack into output format
    # global numvisc, numinvc
    tl = []
    for xs in stack:
        # calculate max col depth in output format, get val with max(tl)
        numvisc = len(xs[0])
        numinvc = (len(xs) - 1)
        maxcoldepth = (numvisc * 2) + 1 + numinvc
        tl.append(maxcoldepth)
    col = []
    for xs in range(7):
        col.append([])
    cnt = 0
    for xs in stack:
        numvisc = len(xs[0])
        numinvc = len(xs)
        # insert spacers: max col depth minus number of cards in stack
        for ys in range(max(tl) - (numvisc * 2) + 1 + numinvc):
            col[cnt].append(nocmb)
        # number of visible cards in stack
        for ys in reversed(xs[0]):
            if ys[0] in (1, 10, 11, 12, 13):
                col[cnt].append(ctb)
                col[cnt].append('|' + cvals[ys[0]] + ' ' + ys[1] + '| ')
            else:
                col[cnt].append(ctb)
                col[cnt].append('|' + str(ys[0]) + ' ' + ys[1] + '| ')
        # number of invisible/face down cards in stack
        for ys in range(numinvc):
            if numvisc == 0:
                col[cnt].append(noctb)
            else:
                col[cnt].append(ctb)
        cnt += 1
    cntr = 8
    for xs in range(max(tl)):
        row = ' ' * 6 + col[0].pop() + col[1].pop() + col[2].pop() + \
              col[3].pop() + col[4].pop() + col[5].pop() + col[6].pop() 
        screen.addstr(cntr, 1, row.encode('utf_8'))
        screen.refresh()
        cntr += 1

#
# curses functions common to both visual modes
#

vizmode = [0, 1]

def display_game():
    """
    Draw the game to screen
    """
    if vizmode[0] == 0:
        screen.clear()
        display_waste()
        display_stacks()
        display_bases()        
        display_feedback()
        display_menu()
    elif vizmode[0] == 1:
        screen.clear()
        display_trad_waste()
        display_trad_stacks()
        display_feedback()
        display_menu()

def display_menu():
    """
    Display the keyboard commands menu & another bit of text... ;-)
    """
    screen.addstr(0, 1, '(Q)uit  (N)ew  (T)oggle mode  (H)elp', curses.A_BOLD)
    screen.addstr(23, 1, 'Enter command/move: ')

def display_feedback():
    """
    Displays the player's moves to the screen in an echo like way
    """
    if len(inp) > 0:
        if len(inp) % 2 != 0:
            # fwin is created, erased and created to ensure no hanging
            # chars... ugly, but i couldn't find a better solution...
            fwin = screen.subwin(1, 10, 23, 22)
            fwin.erase()
            fwin = screen.subwin(1, 10, 23, 22)
            v = inp[-1:][0]
            fwin.addstr(0, 0, ' [' + v + ' ->  ]')
            fwin.refresh()
        else:
            fwin = screen.subwin(1, 10, 23, 22)
            fwin.erase()
            fwin = screen.subwin(1, 10, 23, 22)
            v = " -> ".join(inp[-2:])
            fwin.addstr(0, 0, ' [' + v + ']')
            fwin.refresh()
    else:
        # this is needed to get rid of any hanging chars...
        fwin = screen.subwin(1, 10, 23, 22)
        fwin.erase()

def display_error():
    """
    Displays an error message when the player inputs an invalid char
    """
    erwin = screen.subwin(1, 25, 23, 31)
    erwin.erase()
    erwin = screen.subwin(1, 25, 23, 31)
    erwin.addstr(0, 0, ' Invalid command/move')
    erwin.refresh()

def display_noerror():
    """
    A hack to wipe the error message when the player inputs a valid char
    """
    nerwin = screen.subwin(1, 25, 23, 31)
    nerwin.erase()
    nerwin = screen.subwin(1, 25, 23, 31)
    nerwin.addstr(0, 0, '')
    nerwin.refresh()

def display_help():
    """
    Display the help text window
    """
    global hwin
    hwin = screen.subwin(15, 35, 1, 24)
    hwin.box()
    hwin.addstr(1, 1,  "To move cards onto stacks, type")
    hwin.addstr(2, 1,  "the name of the source stack,  ")
    hwin.addstr(3, 1,  "e.g. 'a', then the name of the ")
    hwin.addstr(4, 1,  "destination stack.             ")
    hwin.addstr(5, 1,  " " * 31)
    hwin.addstr(6, 1,  "Examples: 'a4', '06', '3y'     ")
    hwin.addstr(7, 1,  " " * 31)
    hwin.addstr(8, 1,  "To deal a new card to the waste")
    hwin.addstr(9, 1,  "type 'd'.                      ")
    hwin.addstr(10, 1, " " * 31)
    hwin.addstr(11, 1, "Type 'h' again to remove this  ")
    hwin.addstr(12, 1, "message.                       ")
    hwin.addstr(13, 1,  " " * 31)
    hwin.refresh()
    hc = hwin.getch()
    if hc:
        hwin.erase()
        display_game()

def process_kbinput():
    """
    All the user keyboard input is managed here
    """
    curses.echo()
    c = screen.getch()
    # quit game
    if c in (ord('Q'), ord('q')):
        sys.exit(0)
    # new game
    elif c in (ord('N'), ord('n')):
        new_game()
        display_game()
#        display_noerror()
        screen.refresh()
    # toggle visual modes
    elif c in (ord('T'), ord('t')):
        vizmode.reverse()
        display_game()
        screen.refresh()
    # display help
    elif c in (ord('H'), ord('h')):
        display_help()
#        display_noerror()
        screen.refresh()
    # deal a new card to the waste
    elif c in (ord('D'), ord('d')):
        display_noerror()
        do_waste()
        display_game()
        screen.refresh()
    # make a move: the numbers 48-54 represent the ascii values of 0-6
    elif c in (ord('A'), ord('a'), ord('W'), ord('w'), ord('X'), ord('x'),\
               ord('Y'), ord('y'), ord('Z'), ord('z'), 48, 49, 50, 51, 52,\
               53, 54):
        inp.append(chr(c))
#        display_noerror()
        do_move()
        display_game()
        screen.refresh()
    else:
        display_error()
        display_menu()
        screen.refresh()

########################################################################
# main functions
########################################################################

def main(stdscr):
    """
    The main() function... it all happens here...
    """
    # create the screen and globals
    global screen
    screen = stdscr.subwin(0, 0)
    screen.clear()
    global screeny, screenx
    screeny, screenx = screen.getmaxyx()
#    global botty
#    botty = screeny - 1
    # make a new game
    new_game()
    # do all the display stuff
    display_game()
#    display_menu()
    # main loop    
    while 1:
        process_kbinput()

if __name__ == '__main__':
    try:
        # initialize curses
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        main(stdscr)
        # set everything back to normal
        curses.echo()
        curses.nocbreak()
        # terminate curses
        curses.endwin()
    except:
        # in the event of an error, restore the terminal to sanity
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        # print the exception: use this for debugging
        traceback.print_exc()
