import json
import requests
from datetime import datetime,timedelta
from colorama import init, Fore, Back
import os
import sqlite3


# Constantes
BLACK = Fore.BLACK
RED = Fore.LIGHTRED_EX
BLUE = Fore.LIGHTBLUE_EX
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.LIGHTYELLOW_EX
CYAN = Fore.LIGHTCYAN_EX
WHITE = Fore.LIGHTWHITE_EX
RESET = Fore.RESET
BRED = Back.RED
BBLACK = Back.BLACK
BYELLOW = Back.LIGHTYELLOW_EX
BBLUE = Back.BLUE

GBOTPATH, filename = os.path.split(__file__)

class SessionRaiders:

        def __init__(self):
            '''
            
            '''
            if datetime.now().hour< 1 or datetime.now().hour >=9 :
                _creneauHoraire = self.DetermineCreneau()
                _streamer = self.ObtenirStreamer(_creneauHoraire)
            
                if (_streamer) :
                    _listeRaidersDejaPresent = self.ObtenirRaidersDejaPresent(_creneauHoraire)
                    self.ListeChatterEnLigne(_streamer.lower(), _creneauHoraire,_listeRaidersDejaPresent)
                else :
                    print("Absence de streamer dans streamer.txt > Pas de session Raiders valide")
            else :
                print(BYELLOW+BLACK+"Hors créneau :"+BBLACK+WHITE+"Il est "+RED+datetime.now().strftime("%Hh%M") +WHITE+" Les créneaux horaires ne sont pas atteint. patientez...")

        
        def ObtenirRaidersDejaPresent(self,creneauHoraire):
            repertoire = os.path.join(GBOTPATH,"data",datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(repertoire, exist_ok=True) 
            name = os.path.join(repertoire,(creneauHoraire.replace(":","").replace(" ","")+"-chatters.txt"))
            chatters =[]
            if os.path.exists(name):
                fichierLocal = open(name,"r")
                chatters =  fichierLocal.read().split("\n")
                del chatters[0]
                chatters =  [x.lower() for x in chatters]
                fichierLocal.close
            return chatters
                
        def SauvegardeCreneauHoraire (self,creneauHoraire,listeRaiders):
            repertoire = os.path.join(GBOTPATH,"data",datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(repertoire, exist_ok=True) 
            name = os.path.join(repertoire,(creneauHoraire.replace(":","").replace(" ","")+"-chatters.txt"))
            chatters =[]
            fichierLocal = open(name,"w")
            fichierLocal.write(creneauHoraire+'\n')
            for raider in listeRaiders:
                fichierLocal.write(raider+'\n')
            fichierLocal.close
            
            name = os.path.join(GBOTPATH,"chatters.txt")
            chatters =[]
            fichierLocal = open(name,"w")
            fichierLocal.write(creneauHoraire+'\n')
            for raider in listeRaiders:
                fichierLocal.write(raider+'\n')
            fichierLocal.close
            

                
        def DetermineCreneau(self):
            
            debut = datetime.now().strftime('%Hh00')
            fin = (datetime.now()+timedelta(hours=1)).strftime('%Hh00')
            return (debut + " - "+ fin +" :")
                        
        def ListeChatterEnLigne(self, streamer, creneauHoraire, listeRaiderDejaPresent):
            '''
            Renvois la liste des Raiders en lignes
            '''
            # Recupere la liste des Raiders
            
            fichierLocal = open(os.path.join(GBOTPATH,"raiders.txt"),"r")
            listeRaiders =  fichierLocal.read().split("\n")
            listeRaiders =  [x.lower() for x in listeRaiders]
            fichierLocal.close

            # Recupere les chatters du STREAMER

            url = requests.get('https://tmi.twitch.tv/group/user/'+streamer.lower()+'/chatters')
            text = url.text  
            data = json.loads(text) 
            parseData = data['chatters']
            chatters = parseData["broadcaster"]+parseData["vips"]+parseData["moderators"]+parseData["staff"]+parseData["admins"]+parseData["global_mods"]+parseData["viewers"]
            chatters =  [x.lower() for x in chatters]

            # créé une liste pour trouver les Raiders present sur le stream

            raidersEnLigne=[]
            raidersHoraire=[]
            
            if len(chatters)>0 :
                for raider in listeRaiderDejaPresent :      
                    if (raider not in chatters) and (raider != ""):
                        raidersHoraire.append(raider)
                    if (raider in chatters):
                        raidersEnLigne.append(raider)
                for chatter in chatters:
                    if (chatter in listeRaiders) and (chatter not in listeRaiderDejaPresent):
                        raidersEnLigne.append(chatter)


            print (GREEN ,"\n"+creneauHoraire , BLUE , streamer.upper())
            print (YELLOW + str(len(chatters)) + WHITE + " viewers(s) sur le stream.")
            print (RED + str(len(raidersEnLigne)) + WHITE + " raider(s) sur le stream.")
            print (RED + str(len(raidersEnLigne)+len(raidersHoraire)) + WHITE + " raider(s) au total sur le creneau.")
            
            listeRaidersFinale=[]        
            listeRaidersFinale.append(streamer) 
            
            print (WHITE,"\nRaider(s) deconnecté(s) durant le créneau : ",end="")
            for raider in raidersHoraire:
                if raider != 'vide' and raider != streamer :
                    print (YELLOW,raider+" ",end="")
                    listeRaidersFinale.append(raider)
            print("\n")
            
            for raider in raidersEnLigne :
                if (raider != streamer):
                    listeRaidersFinale.append(raider)
                    print (RED + "   > " + WHITE + raider)

            #SAUVEGARDE CRENEAU
            self.SauvegardeCreneauHoraire(creneauHoraire,listeRaidersFinale)

        def ObtenirStreamer(self, creneauHoraire):
            '''
            recupere le nom du streamer en fonction du creneau horaire dans le fichier planning.txt
            '''
            streamer=""
            fichierLocal = open(os.path.join(GBOTPATH,"streamer.txt"),"r")
            streamer = fichierLocal.read()
            fichierLocal.close
            if (streamer=="" or streamer == "vide"):
                print ("\n"+ BRED + WHITE +"ERREUR :"+BBLACK+WHITE+" Impossible d'accéder au streaming du viewer. Veuillez vérifier si un streamer est bien présent sur ce créneau horaire dans le PLANNING. \nLe script continue de fonctionner..." )
                self.SauvegardeCreneauHoraire(creneauHoraire,["vide"])
            else :
                return streamer
                