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
                    _listeSpartiateDejaPresent = self.ObtenirSpartiateDejaPresent(_creneauHoraire)
                    self.ListeChatterEnLigne(_streamer.lower(), _creneauHoraire,_listeSpartiateDejaPresent)
                else :
                    print("Absence de streamer dans streamer.txt > Pas de session Raiders valide")
            else :
                print(BYELLOW+BLACK+"Hors créneau :"+BBLACK+WHITE+"Il est "+RED+datetime.now().strftime("%Hh%M") +WHITE+" Les créneaux horaires ne sont pas atteint. patientez...")

        
        def ObtenirSpartiateDejaPresent(self,creneauHoraire):
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
                
        def SauvegardeCreneauHoraire (self,creneauHoraire,listeSpartiate):
            repertoire = os.path.join(GBOTPATH,"data",datetime.now().strftime("%Y-%m-%d"))
            os.makedirs(repertoire, exist_ok=True) 
            name = os.path.join(repertoire,(creneauHoraire.replace(":","").replace(" ","")+"-chatters.txt"))
            chatters =[]
            fichierLocal = open(name,"w")
            fichierLocal.write(creneauHoraire+'\n')
            for spartiate in listeSpartiate:
                fichierLocal.write(spartiate+'\n')
            fichierLocal.close
            
            name = os.path.join(GBOTPATH,"chatters.txt")
            chatters =[]
            fichierLocal = open(name,"w")
            fichierLocal.write(creneauHoraire+'\n')
            for spartiate in listeSpartiate:
                fichierLocal.write(spartiate+'\n')
            fichierLocal.close
            

                
        def DetermineCreneau(self):
            
            debut = datetime.now().strftime('%Hh00')
            fin = (datetime.now()+timedelta(hours=1)).strftime('%Hh00')
            return (debut + " - "+ fin +" :")
                        
        def ListeChatterEnLigne(self, streamer, creneauHoraire, listeSpartiateDejaPresent):
            '''
            Renvois la liste des Spartiates en lignes
            '''
            # Recupere la liste des SPARTIATES
            fichierLocal = open(os.path.join(GBOTPATH,"raiders.txt"),"r")
            listeSpartiate =  fichierLocal.read().split("\n")
            listeSpartiate =  [x.lower() for x in listeSpartiate]
            fichierLocal.close

            # Recupere les chatters du STREAMER

            url = requests.get('https://tmi.twitch.tv/group/user/'+streamer.lower()+'/chatters')
            text = url.text  
            data = json.loads(text) 
            parseData = data['chatters']
            chatters = parseData["broadcaster"]+parseData["vips"]+parseData["moderators"]+parseData["staff"]+parseData["admins"]+parseData["global_mods"]+parseData["viewers"]
            chatters =  [x.lower() for x in chatters]

            # créé une liste pour trouver les Spartiates present sur le stream

            spartiateEnLigne=[]
            spartiateHoraire=[]
            
            if len(chatters)>0 :
                for spartiate in listeSpartiateDejaPresent :      
                    if (spartiate not in chatters) and (spartiate != ""):
                        spartiateHoraire.append(spartiate)
                    if (spartiate in chatters):
                        spartiateEnLigne.append(spartiate)
                for chatter in chatters:
                    if (chatter in listeSpartiate) and (chatter not in listeSpartiateDejaPresent):
                        spartiateEnLigne.append(chatter)


                
          
            print (GREEN ,"\n"+creneauHoraire , BLUE , streamer.upper())
            print (YELLOW + str(len(chatters)) + WHITE + " viewers(s) sur le stream.")
            print (RED + str(len(spartiateEnLigne)) + WHITE + " spartiate(s) sur le stream.")
            print (RED + str(len(spartiateEnLigne)+len(spartiateHoraire)) + WHITE + " spartiate(s) au total sur le creneau.")
            
            listeSpartiateFinale=[]        
            listeSpartiateFinale.append(streamer) 
            
            print (WHITE,"\nSpartiate(s) deconnecté(s) durant le créneau : ",end="")
            for spartiate in spartiateHoraire:
                if spartiate != 'vide' and spartiate != streamer :
                    print (YELLOW,spartiate+" ",end="")
                    listeSpartiateFinale.append(spartiate)
            print("\n")
            
            for spartiate in spartiateEnLigne :
                if (spartiate != streamer):
                    listeSpartiateFinale.append(spartiate)
                    print (RED + "   > " + WHITE + spartiate)
            
             
            #SAUVEGARDE CRENEAU
            self.SauvegardeCreneauHoraire(creneauHoraire,listeSpartiateFinale)

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
                