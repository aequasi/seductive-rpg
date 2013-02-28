import es
from srpgCore import srpgCore
import psyco
psyco.full( )

core = None 

info = None

def load( ):
	core = srpgCore()
	info = core.info
	print info
	""" Runs when the addon is loaded. Loads all necessary files into memory """
	print core
	core.load( )
