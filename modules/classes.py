
import json
# from database import db # Retrieve the already prepped db connection
import random
from os.path import dirname, abspath
import json
import datetime

file_path = f"{dirname(abspath(__file__))}\\txt\\"

class MuddyBootsFW:
    """Hosts common paramaters across classes"""
    functionName = None
    
    def __init__ (self, id) -> None:
        self.id = id
        self.load_data()

    def load_data(self) -> None:
        """Will query SQL to retrieve all details of this match
        Returns object hosting properties to be loaded
        """
        self.data = self.run_query(self.functionName,self.id)
        
    def get_id(self) -> int:
        """ Returns the id of the obj """
        return self.id
    
    def run_query(self, fun, var) -> object:
        """" Provides consistent method for getting data from db class"""
        try:
            sqlQuery = f"select * from {fun}({var})"
            data = json.loads(db.run_query(sqlQuery))
            # Return as a dict if a single item
            if len(data) == 1: data = data[0]
            return data
        except:
            return None
    
    
        
    # Produce a string of the dict on call
    def __str__(self):
        """ Return obj as a string in dict format"""
        return str(self.data)

class Match(MuddyBootsFW):
    """
    Hosts all details of a match. Uses super class for common functions
    """
    
    # Prep for all other params
    functionName = "fn_getMatch"
    
    def load_data(self) -> None:
        """Will query SQL to retrieve all details of this match
        Returns object hosting properties to be loaded
        """
        # Expand on the original load data
        super().load_data()
        
        # Retrieve the team details
        self.homeTeamId = self.data.pop('homeTeamId')
        self.awayTeamId = self.data.pop('awayTeamId')
        self.get_teams()

        #self.data["season"] = str(Season(self.data.pop('SeasonId')))
        #self.data["occasion"] = str(Occasion(self.data.pop('OccasionId')))
        
        # Set up the Person of the Match
        self.data['homePOTM'] = self.data.pop('homePOTMId')
        self.data['awayPOTM'] = self.data.pop('awayPOTMId')
        self.get_potm()
        
        # Retrieve all events
        self.get_events()
        
        # Retrieve the season
        self.seasonId = self.data.pop('seasonId')
        self.get_season()
        
        # Retrieve the occasion
        self.occasionId = self.data.pop('occasionId')
        self.get_occasion()
    
    def get_teams(self) -> None:
        """ Retrieves the teams """
        
        # Retrieve the two teams by removing the ID from the main data
        self.homeTeam = Team(self.homeTeamId)
        self.awayTeam = Team(self.awayTeamId)
        
        # Retrieve all players from the teams
        self.get_players()
    
    def get_players(self) -> None:
        """ Retrieves all the selected players for this match"""
        
        # Get data from the database
        players = self.run_query("fn_getMatchPlayers",self.id)
        
        # Clear the lists prior to adding all members
        self.homeTeam.clear_players()
        self.awayTeam.clear_players()
        
        # Add each player into the relevant team
        for player in players:
            teamId = player.pop("teamid")
            if teamId == self.homeTeam.get_id():
                self.homeTeam.add_player(player)
            else:
                self.awayTeam.add_player(player) 
    
    def get_potm(self) -> None:
        """ Retrieves the POTM for each team"""
        
        # Update the POTM only if one has been specified
        if self.data['homePOTM']: 
            self.data['homePOTM'] = self.homeTeam.get_player(self.data['homePOTM'])
            
        if self.data['awayPOTM']: 
            self.data['awayPOTM'] = self.awayTeam.get_player(self.data['awayPOTM'])  
            
    def get_occasion(self) -> None:
        """" Updates the occasion """
        self.occasion = self.run_query("fn_getOccasion",self.occasionId)
    
    def get_season(self) -> None:
        """ Retrieves the season """
        self.season = self.run_query("fn_getSeason",self.seasonId)
            
    def get_events(self) -> None:
        """ Retrieves all events for this match"""
        self.data["events"] = self.run_query("fn_getMatchEvents",self.id)
        
    def __str__(self):
        """ Modify the string return to update itself """
        self.data["homeTeam"] = str(self.homeTeam)
        self.data["awayTeam"] = str(self.awayTeam)
        self.data["season"] = self.season["description"]
        self.data["occasion"] = self.occasion["description"]
        return str(self.data)
    
class Team (MuddyBootsFW):
    """ Hosts all data on a team, including club"""
    functionName = "fn_getTeam"
    def __init__(self,id):
        super().__init__(id)
        self.clear_players()
        
    def add_player(self,player):
        """ Adds players to the player list"""      
        self.data["players"].append(player)
    
    def clear_players(self):
        """ Removes all players from the list"""
        self.data["players"] = []
    
    def remove_player(self,player):
        """ Removes a player from the list"""
        # Allow for none type to squash bugs
        self.data["players"].pop(player, None)
    
    def get_player(self,playerId):
        """" Retrieves a player based on Id """

        for player in self.data["players"]:
            if player["playerid"] == playerId:
                return player
    
    def get_players(self):
        """ Returns all players """
        return self.data["players"]
    
class Player (MuddyBootsFW):
    """ Hosts all data on a player"""
    functionName = "fn_getPlayer"

class MuddyBootsBluePrint:
    # Gives an object to export data with

    def __init__(self, type) -> None:
        self.SetType(type)
        print(f"{type} created")

    def SetType(self,type) -> None: self.type = type
    
    def GetType(self) -> str: return self.type

    def ToJSON(self, folder) -> None:

        # Export the class object as a dict
        data = self.__dict__.copy()

        # Remove the type
        del data["type"]

        # Output the object with the extracted data and type
        obj = {
            "created" : datetime.datetime.now(datetime.UTC).strftime("%Y%m%dT%H%M%S%fZ"),
            "type" : self.GetType(),
            "data" : data
        }
        fileDate = datetime.datetime.now().strftime("%Y%m%d %H%M%S")
        file = f"{folder}\\{self.type}_{fileDate}.json"
        print(f"outputting file to JSON: {file}")
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self, f, ensure_ascii=False, indent=4, default=lambda o:obj, sort_keys=True)

class Players:
    """ Hosts a temp db of players, will only update once requested"""
      
class MBTool:
    """
        The multitool for Muddy Boots
    """ 

class User(MuddyBootsBluePrint):

    def __init__( self ) -> None:

        # Implicity import the super class init
        super().__init__("User")
        
    # Setters
    def SetForName(self, forname:str) -> None: self.forname = forname
    def SetSurName(self, surname:str) -> None: self.surname = surname
    def SetUserName(self,username:str) -> None: self.username = username
    def SetSquadName(self,squadName:str) -> None: self.squadName = squadName
    def SetKnownAs(self, knownAs:str) -> None: self.knownAs = knownAs
    def SetEmail(self,email:str) -> None: self.email = email
    def SetDOB(self,dob:datetime) -> None: self.dob = dob

    # Getters
    def GetForName(self) -> str: return self.forname
    def GetSurName(self) -> str: return self.surname
    def GetUserName(self) -> str: return self.username
    def GetSquadName(self) -> str: return self.squadName
    def GetKnownAs(self) -> str: return self.knownAs
    def GetEmail(self) -> str: return self.email
    def GetDOB(self) -> str: return self.dob

    # Create a random user (for dev purposes)
    def CreateRandom(self):
        print("creating random")
        self.SetForName(random.choice((open(f'{file_path}\\fornames.txt')).readlines()).replace("\n","")) 
        self.SetSurName(random.choice((open(f'{file_path}\\surnames.txt')).readlines()).replace("\n",""))
        self.SetUserName(f"{self.GetForName()}{self.GetSurName()}")
        self.SetSquadName(self.GetUserName())
        self.SetKnownAs(self.GetSurName())
        self.SetEmail(f"{self.GetUserName()}@muddyboots.co.uk")

        # Create a date of birth
        day = random.choice(range(1,31))
        month = random.choice(range(1,12))
        year = random.choice(range(1930,2020))
        self.SetDOB(f"{day}/{month}/{year}")
        self.Print()

    def ToString(self) -> str:
        out = f"Forname: {self.GetForName()}\n"
        out = f"Surname: {self.GetSurName()}\n" + out
        out = f"Username: {self.GetUserName()}\n" + out
        out = f"SquadName: {self.GetSquadName()}\n" + out
        out = f"KnownAs: {self.GetKnownAs()}\n" + out
        out = f"Email: {self.GetEmail()}\n" + out
        out = f"DOB: {self.GetDOB()}" + out
        
        return out


    # Print details of the user to the screen
    def Print(self) -> None: print(self)

    def GetJSON(self) -> json:
        # Passes the user back as a json object
        
        return json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=True,
            indent=4
        )