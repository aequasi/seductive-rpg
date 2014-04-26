import os
import time

import es
import playerlib
import gamethread
import popuplib
import keyvalues
from database import database
import events.mainEvent as mainEvent
import command.command as command
import menu.menu as menu


class srpgCore(object):
    info = {}

    colors = {
        'red': ['255', '0', '0'],
        'blue': ['0', '0', '255'],
        'green': ['0', '255', '0'],
        'magenta': ['139', '0', '139'],
        'brown': ['128', '42', '42'],
        'grey': ['128', '128', '128'],
        'cyan': ['0', '204', '204'],
        'yellow': ['255', '255', '0'],
        'orange': ['255', '127', '0'],
        'white': ['255', '255', '255'],
        'pink': ['255', '0', '204']
    }

    db = None
    events = {}
    command = None
    menu = None

    config = None
    dir = None
    text = None
    players = None
    race_folder = None
    language_keygroup = {}
    tf_class_names = {1: "Scout", 2: "Sniper", 3: "Soldier", 4: "Demoman", 5: "Medic", 6: "Heavy", 7: "Pyro", 8: "Spy",
                      9: "Engineer"}

    def __init__(self):
        self.setDefaults()
        self.setInfo()

        self.db = database()
        self.events['main'] = mainEvent.mainEvent(self)
        self.command = command.command(self)
        self.menu = menu.menu(self)

        # Make public variable
        es.ServerVar('srpg_version', self.info.version, self.info.name + " - Made by " + self.info.author).makepublic()

        popuplib.langdata['default'] = {"prev": "Back", "next": "Next", "quit": "Cancel", "pending": "Pending"}

        self.text = lambda x, y={}, lang="en": "strings.ini not found in the ../srpg/ directory!"
        strFile = es.getAddonPath('srpg') + '/language_db.txt'
        if os.path.isfile(strFile):
            self.language_keygroup = keyvalues.KeyValues(filename=strFile)

        self.initializeUserDictionary()

    def setDefaults(self):
        defaults = {
            'srpg_debug': [0, "The debug Level"],
            'srpg_levelinterval': [500, "The amount of xp increment after level 2"],
            'srpg_killxp': [40, "The amount of xp gained from a kill"],
            'srpg_headshotxp': [25, "The amount of xp gained from a headshot"],
            'srpg_winroundxp': [15, "The amount of xp gained from winning the round"],
            'srpg_levelxp': [4,
                             "The amount of extra xp gained multiplied by the amount of levels the victim is above the attacker"],
            'srpg_announcexp': [1, "Announce xp on start?"],
            'srpg_freelevels': [10,
                                "The amount of free levels a player gains from joining the server for the first time."],
            'srpg_inactivity_counter': [7, "After this many days, the user will be deleted from the dictionary"],
            'srpg_savetimer': [5, "The amount of minutes that the database will save"],
            'srpg_admins': ["", "The admins allowed to use the srpgadmin"],
            'srpg_new_race_increments_level': [1, "Will unlocking a new race increment the players total level"]
        }

        for x in defaults:
            es.ServerVar(x, defaults[x][0], defaults[x][1])

    def setInfo(self):
        # Addon information
        self.info = es.AddonInfo()
        self.info.name = "Seductive RPG"
        self.info.version = "0.1.0"
        self.info.url = "www.st-gc.org"
        self.info.basename = "srpg"
        self.info.author = "Aaron Scherer (aequasi)"

    def initializeUserDictionary(self, error=False):
        c = self.db.getCursor()
        result = c.execute("SELECT * FROM client").fetchall()
        players = {}
        for player in result:
            sid = player[1]
            cid = player[2]
            if not players.has_key(sid):
                players[sid] = {}
            if not players[sid].has_key(cid):
                players[sid][cid] = {}
            players[sid][cid] = {'level': int(player[3]), 'experience': int(player[4])}
        self.players = players
        c.close()

    def load(self):
        self.debug(0, "Calling `load()`")
        self.showLoadMessages()

        if not es.exists('command', 'srpg'):
            es.regcmd('srpg', 'srpg/cmdHandler')
            es.regsaycmd('!srpg', 'srpg/cmdHandler')

        self.debug(0, "Registering Save Timer")
        gamethread.delayed(60 * es.ServerVar('srpg_savetimer'), self.saveDatabase)

    def unload(self):
        self.db.close()

    def findPlayer(self, steam_id):
        if self.players.has_key(steam_id):
            return self.players[steam_id]
        return False

    def saveDatabase(self):
        self.msg("#green Saving users to database!")
        print( "[Seductive] SAVING USERS" )
        c = self.db.getCursor()

        for steam_id in self.players:
            player = self.players[steam_id]
            if player.has_key('info'):
                self.debug(0, "Saving %s..." % steam_id)
                client_steam_id = player['info']['networkid']
                for class_id in player:
                    data = player[class_id]
                    if class_id != 'info':
                        query = "INSERT OR IGNORE INTO client VALUES( NULL, '%s', '%s', 0, 0)" % \
                                (client_steam_id, class_id)
                        c.execute(query)

                        query = "UPDATE client SET level = %s, experience = %s WHERE steam_id = '%s' AND class_name = '%s'" % \
                                (data['level'], data['experience'], client_steam_id, class_id)
                        c.execute(query)
            else:
                print "%s had no info key" % steam_id

        gamethread.delayed(60 * es.ServerVar('srpg_savetimer'), self.saveDatabase)
        c.close()


    def addExperience(self, client, client_steam_id, xp):

        client_class = self.getPlayerClass(client)
        if not self.players.has_key(client_steam_id):
            self.players[client_steam_id] = {}
        if not self.players[client_steam_id].has_key(client_class):
            self.players[client_steam_id][client_class] = {'level': 1, 'experience': 0}
        self.players[client_steam_id][client_class]['experience'] += xp
        self.checkLevelUp(client_steam_id, client_class)
        self.tell(self.players[client_steam_id]['info']['userid'], "#green You've gained %s experience!" % xp)

    def checkLevelUp(self, client_steam_id, type):
        xp = self.players[client_steam_id][type]['experience']
        level = self.players[client_steam_id][type]['level']

        if int(xp) > self.getLevelExperience(level + 1):
            self.players[client_steam_id][type]['level'] += 1
            self.tell(self.players[client_steam_id]['info']['userid'], "#green Congrats! You've leveled up!")
            return self.checkLevelUp(client_steam_id, type)
        else:
            return False

    def getLevelExperience(self, level):
        xp = 0
        for i in range(0, level):
            xp += es.ServerVar('srpg_levelinterval') * level
        return int(xp)

    def getPlayerClass(self, userid):
        ac_entitylist = es.createentitylist("tf_player_manager")
        for ac_player_manager in ac_entitylist:
            ac_player = playerlib.getPlayer(userid)
            ac_class = es.getindexprop(ac_player_manager,
                                       "CTFPlayerResource.m_iPlayerClass.%03d" % int(ac_player.get('index')))
            if ac_class in self.tf_class_names:
                return self.tf_class_names[ac_class]
            else:
                return 0

    def showLoadMessages(self):
        self.debug(0, '************')
        self.debug(0, '%s Version: %s' % ( self.info.name, self.info.version ))
        self.debug(0, 'Created by %s' % self.info.author)
        self.debug(0, 'Log file started at %s' % time.strftime("%A %d %B %Y - %H:%M:%S"))
        self.debug(0, 'System Info:')
        self.debug(0, '\tCorelib Version: %s' % es.ServerVar('es_corelib_ver'))
        self.debug(0, '\tEventscripts Noisy: %s' % es.ServerVar('eventscripts_noisy'))
        self.debug(0, '\tPopuplib version: %s' % popuplib.info.version)
        self.debug(0, '************\n')
        es.keygroupcreate('SRPGuserdata')

    def msg(self, text):
        es.msg("#multi", "[Seductive RPG] - %s" % text)
        self.debug(0, text, False)

    def tell(self, user_id, msg):
        es.tell(user_id, '#multi', '[Seductive RPG] - %s' % msg)

    def debug(self, level, text, addToFile=True):
        """ This method prints text to the console, and if addToFile is true, it will open a log file and append the log and time to it. """
        if level <= int(es.ServerVar('srpg_debug')):
            tempText = "[SeductiveRPG] - %s" % text
            while len(tempText) > 200:
                index = tempText[:200].rfind(' ')
                es.dbgmsg(0, tempText[:index])
                tempText = tempText[index:]
            es.dbgmsg(0, tempText)
            if addToFile:
                strfile = es.getAddonPath('srpg') + '/debuglog.txt'
                if not os.path.isfile(strfile):
                    myfile = open(strfile, 'w')
                else:
                    myfile = open(strfile, 'a')
                myfile.writelines(text + "\n")
                myfile.close()
