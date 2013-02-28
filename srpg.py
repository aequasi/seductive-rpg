import es
import core
import psyco
psyco.full( )

es.load( 'srpg/core' )

core = core()

info = core[ 'info' ]

def load( ):
	""" Runs when the addon is loaded. Loads all necessary files into memory """
	core.load()