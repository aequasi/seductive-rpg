import es
import popuplib

class command( object ):

	core = None

	menus = {}

	def __init__( self, core ):
		"""
		@core: srpgCore
		"""
		self.core = core

	def run( self, user_id, name, arguments ):
		print { 'user': user_id, 'name': name, 'args': arguments }
		if len( name ) == 0:
			self.showMainMenu( user_id )
		if not hasattr( self.__class__, name ):
			return es.tell( user_id, '#multi', "#greenCommand doesn't exist" )
		else:
			return getattr( self.__class__, name )( self, user_id, arguments )

	def xp( self, user_id, arguments = {} ):
		steam_id = es.getplayersteamid( user_id )
		player = self.core.findPlayer( steam_id )

		current_class = self.core.getPlayerClass( user_id )

		totalXp = 0
		totalLevel = 0
		classXp = 0
		classLevel = 0
		for class_name in player:
			if not class_name == "info":
				data = player[ class_name ]
				if class_name == current_class:
					classXp = data[ 'experience' ]
					classLevel = data[ 'level' ]
				totalXp += data[ 'experience' ]
				totalLevel += data[ 'level' ]

		needed_xp = self.core.getLevelExperience( classLevel + 1 )

		self.core.tell( user_id, "#green Total Level: #lightgreen %d" % ( totalLevel ) )
		self.core.tell(
			user_id,
			"#green %s Level: #lightgreen %d #green %s XP: #lightgreen %d/%d"
			% ( current_class, classLevel, current_class, classXp, needed_xp )
		)