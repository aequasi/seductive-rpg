import es


class mainEvent:
    """
    @core: srpgCore
    """
    core = None

    def __init__(self, core):
        """
        @core: srpgCore
        """
        self.core = core

    def event_player_connect(self, event):
        steam_id = event['networkid']
        event = {
            'networkid': event['networkid'],
            'name': event['name'],
            'userid': event['userid'],
            'client': event['index']
        }
        if len(steam_id) < 10:
            return
        self.core.debug(0, "Running Player connect on %s<%s> " % ( event['name'], steam_id ))
        if not self.core.players.has_key(steam_id):
            self.core.players[steam_id] = {}
        self.core.players[steam_id]['info'] = event
        print self.core.players

    def event_player_death(self, event):
        attacker = event['attacker']
        steam_id = es.getplayersteamid(attacker)
        xp = es.ServerVar('srpg_killxp')
        if event['headshot']:
            xp += es.ServerVar('srpg_headshotxp')
        print "Trying to give %s (%s) %d xp" % ( attacker, steam_id, xp )
        if steam_id != None and len(steam_id) > 3:
            self.core.addExperience(attacker, steam_id, xp)

        assister = event['assister']
        steam_id = es.getplayersteamid(assister)
        xp = es.ServerVar('srpg_killxp') / 2
        if steam_id != None and len(steam_id) > 3:
            self.core.addExperience(assister, steam_id, xp)