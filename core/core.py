import es
import playerlib
import gamethread
import popuplib
import modevents
import cPickle
import os
import time
import random
import langlib
import keyvalues
import difflib
import effectlib
import vecmath
import math


class core:

	info = {}

	colors = {
		'red': [ '255', '0', '0' ],
		'blue': [ '0', '0', '255' ],
		'green': [ '0', '255', '0' ],
		'magenta': [ '139', '0', '139' ],
		'brown': [ '128', '42', '42' ],
		'grey': [ '128', '128', '128' ],
		'cyan': [ '0', '204', '204' ],
		'yellow': [ '255', '255', '0' ],
		'orange': [ '255', '127', '0' ],
		'white': [ '255', '255', '255' ],
		'pink': [ '255', '0', '204' ]
	}

	defaults = {
	'srpg_debug': [ 0, "The debug Level" ],
	'srpg_start_your_engines': [ 300, "The amount of xp required to level up to level 2" ],
	'srpg_levelinterval': [ 100, "The amount of xp increment after level 2" ],
	'srpg_killxp': [ 40, "The amount of xp gained from a kill" ],
	'srpg_headshotxp': [ 25, "The amount of xp gained from a headshot" ],
	'srpg_winroundxp': [ 15, "The amount of xp gained from winning the round" ],
	'srpg_levelxp': [ 4, "The amount of extra xp gained multiplied by the amount of levels the victim is above the attacker" ],
	'srpg_announcexp': [ 1, "Announce xp on start?" ],
	'srpg_freelevels': [ 10, "The amount of free levels a player gains from joining the server for the first time." ],
	'srpg_inactivity_counter': [ 7, "After this many days, the user will be deleted from the dictionary" ],
	'srpg_savetimer': [ 3, "The amount of minutes that the database will save" ],
	'srpg_admins': [ "", "The admins allowed to use the srpgadmin" ],
	'srpg_new_race_increments_level': [ 1, "Will unlocking a new race increment the players total level" ]
	}

	dir = None
	text = None
	_dict_SRPGPlayers = None
	race_folder = None
	language_keygroup = None
	isModEvents = False

	def __init__( self ):
		# Addon information
		self.info = es.AddonInfo( )
		self.info.name = "Seductive RPG"
		self.info.version = "0.1.0"
		self.info.url = "www.seductiveturtle.com"
		self.info.basename = "srpg"
		self.info.author = "Aaron Scherer (aequasi)"

		# Make public variable
		es.ServerVar( 'srpg', self.info.version, self.info.name + " - Made by " + self.info.author ).makepublic( )

		popuplib.langdata[ 'default' ] = { "prev": "Back", "next": "Next", "quit": "Cancel", "pending": "Pending" }

		self.text = lambda x, y = { }, lang = "en": "strings.ini not found in the ../srpg/ directory!"
		self.isModEvents = os.path.isfile(es.getAddonPath('srpg').replace('\\','/').replace('/srpg','/modevents/__init__.py'))

	def load( self ):
		info = self.info
		self.showLoadMessages()


	def showLoadMessages(self ):
		self.debug( 0, '\n************', writeTime = False )
		self.debug( 0, '%s Version: %s' % ( self.info.name, self.info.version ), writeTime = False )
		self.debug( 0, 'Created by %s' % self.info.author, writeTime = False )
		self.debug( 0, 'Log file started at %s' % time.strftime( "%A %d %B %Y - %H:%M:%S" ), writeTime = False )
		self.debug( 0, '\nSystem Info:', writeTime = False )
		self.debug( 0, '\tCorelib Version: %s' % es.ServerVar( 'es_corelib_ver' ), writeTime = False )
		self.debug( 0, '\tEventscripts Noisy: %s' % es.ServerVar( 'eventscripts_noisy' ), writeTime = False )
		self.debug( 0, '\tPopuplib version: %s' % popuplib.info.version, writeTime = False )
		self.debug( 0, '\tModEvents: %s' % self.isModEvents, writeTime = False )
		self.debug( 0, '************\n', writeTime = False )
		es.keygroupcreate( 'SRPGuserdata' );



	def debug(level, text, addToFile=True, writeTime=True):
		""" This method prints text to the console, and if addToFile is true, it will open a log file and append the log and time to it. """
		if level <= int(es.ServerVar('srpg_debug')):
			tempText = text
			while len(tempText) > 200:
				index    = tempText[:200].rfind(' ')
				es.dbgmsg(0, tempText[:index])
				tempText = tempText[index:]
			es.dbgmsg(0, tempText)
			if addToFile:
				strfile = es.getAddonPath('srpg') + '/debuglog.txt'
				if not os.path.isfile(strfile):
					myfile = open(strfile, 'w')
				else:
					myfile = open(strfile, 'a')
				if writeTime:
					myfile.writelines(time.strftime('%A %m %Y - %H:%M:%S') + " - " + text + "\n")
				else:
					myfile.writelines(text + "\n")
				myfile.close()