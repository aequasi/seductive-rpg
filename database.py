
import sys
import MySQLdb as mysql
from MySQLdb import OperationalError

class database(object):

	connected = False
	retry = 0
	config = {}

	def __init__( self, config ):
		self.config = config[ 'Database' ]
		self._connect()
		# Value Sizes
		# TINYINT 255
		# SMALLINT 65535
		# MEDIUMINT 16777215
		# INT 4294967295

		# Advertisement Tables

		# Max Length for events is 32 chars according to modevents.res
		self._execute("""
			CREATE TABLE IF NOT EXISTS `client` (
			  `id` bigint(32) unsigned NOT NULL AUTO_INCREMENT,
			  `steam_id` varchar(32) NOT NULL,
			  `class_name` varchar(64) NOT NULL,
			  `level` int(8) unsigned NOT NULL DEFAULT '1',
			  `experience` bigint(32) unsigned NOT NULL DEFAULT '0',
			  PRIMARY KEY (`id`),
			  UNIQUE KEY `steam_id` (`steam_id`,`class_name`),
			  KEY `steam_id_2` (`steam_id`),
			  KEY `class_name` (`class_name`)
			) ENGINE=MyISAM AUTO_INCREMENT=1 DEFAULT CHARSET=utf8
		""" )

	def _connect(self):
		try:
			self.con = mysql.connect(
				host=self.config['host'],
				user=self.config['user'],
				passwd=self.config['pass'],
				db=self.config['name']
			)
		#PY 2.6: except OperationalError as error
		except OperationalError:
			# Handling for failure to connect to MySQL server
			error = sys.exc_info()[1]
			if error[0] == 2003:
				print error[1]
				self.connected = False
				if not self.retry >= 3:
					self.retry += 1
					self._connect()
			else:
				raise OperationalError(error[0],error[1])
		else:
			self.retry = 0
			self.connected = True
			self.cur = self.con.cursor()
			self._execute("SET CHARACTER SET 'utf8'")
	def _execute(self, command):
		try:
			return self.cur.execute(command)
		except OperationalError:
			# Fix for "MySQL Server has gone away"
			error = sys.exc_info()[1]
			if error[0] == 2006:
				print(error[1])
				self._connect()
				self._execute(command)
			else:
				raise OperationalError(error[0],error[1])
	def Disconnect(self):
		if self.connected:
			self.cur.close()
			self.con.close()