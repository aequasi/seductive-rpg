import es
import popuplib


class menu:
	"""
	@core: srpgCore
	"""

	core = None

	menus = {}

	def __init__( self, core ):
		self.core = core

		self.buildMainMenu()
		self.buildXpMenu()

	def buildMainMenu( self ):
		name = "main_menu"
		main = popuplib.create( name )
		main.addline( "Seductive RPG" )
		main.addline( " " )

		# Lines
		main.addline( "->1. My Experience" )
		main.addline( "->2. Select a Class" )
		main.addline( "->0. Close this Menu" )

		# Submenus
		main.submenu( 1, 'srpg_xp_menu' )
		main.submenu( 1, 'srpg_class_menu' )

		main.menuselect = self.mainMenuHandle

		self.menus[ name ] = main

	def mainMenuHandle( self, user_id, choice, popup_name ):
		main = self.menus[ popup_name ]

		if choice == 10:
			main.close()

	def buildXpMenu( self ):
		"""
		
		"""