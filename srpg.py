from srpgCore import srpgCore
import es

import psyco
psyco.full( )

core = srpgCore()
info = core.info

def load( ):
	""" Runs when the addon is loaded. Loads all necessary files into memory """
	print core
	core.load( )

def unload( ):
	core.unload()

def cmdHandler():
	# Get command name
	name = es.getargv(1)
	print "SRPG Called - %s" % name
	core.command.run( es.getcmduserid(), name, es.getargs() )


def player_connect( event ):
	core.events[ 'main' ].event_player_connect( event )

def player_death( event ):
	core.events[ 'main' ].event_player_death( event )