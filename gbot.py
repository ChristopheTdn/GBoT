import discord
from discord.ext import commands,tasks
from discord.utils import get

import os
import logging
from datetime import datetime,timedelta
import time


from colorama import init, Fore, Back
from dotenv import load_dotenv

import asyncio
import sqlite3

import re


# Class specific GBot

from repeattimer import RepeatTimer
from sessionspartiate import SessionSpartiate

# Parametres 
logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s %(message)s", filemode="w")


# Constantes

PLANNING_SPARTIATE =""
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

class GBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.messages = True
        intents.members = True
        super().__init__(command_prefix="!",intents = intents)
        self.connexionSQL = sqlite3.connect("basededonnees.sqlite")
        curseur = self.connexionSQL.cursor()
        curseur.execute('''CREATE TABLE IF NOT EXISTS GBoT(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            planning TEXT,
            streamer TEXT,
            UNIQUE(planning)
            )''')
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("00h00 - 01h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("01h00 - 02h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("02h00 - 03h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("03h00 - 04h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("04h00 - 05h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("05h00 - 06h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("06h00 - 07h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("07h00 - 08h00 :"," "))        
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("08h00 - 09h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("09h00 - 10h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("10h00 - 11h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("11h00 - 12h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("12h00 - 13h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("13h00 - 14h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("14h00 - 15h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("15h00 - 16h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("16h00 - 17h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("17h00 - 18h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("18h00 - 19h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("19h00 - 20h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("20h00 - 21h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("21h00 - 22h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("22h00 - 23h00 :"," "))
        curseur.execute('''INSERT OR REPLACE INTO GBoT (planning, streamer) VALUES (?,?)''', ("23h00 - 00h00 :"," "))
        self.connexionSQL.commit()
        self.connexionSQL.close()


            
    async def on_ready(self):

        self.AfficheMenu()
        self.bg_task_RecupereSpartiate = self.loop.create_task(self.enregistreSpartiate())
        self.bg_task_RecuperePlanning = self.loop.create_task(self.enregistrePlanning())
        self.bg_task_EcrisPresence = self.loop.create_task(self.envoisPresence())
        timer = RepeatTimer(4*60, SessionSpartiate)
        timer.start()
               
        print (RED + "> "+CYAN+"GBoT Process correctement initialisé.")
        
        SessionSpartiate()
         
    def AfficheMenu(self):
        print("\n",BBLACK,"                         "+BBLUE+YELLOW+ "SPARTAN VIEWERSPY"+BBLACK+"\n")
        '''
        print ("  "+YELLOW+"[F1]"+WHITE + " : Affiche Planning.txt",end='')
        print ("  "+YELLOW+"[F2]"+WHITE + " Ouvre DATA Dir",end='')
        print ("  "+YELLOW+"[F5]"+WHITE + " Refresh manuel")
        '''


    async def envoisPresence(self):
        await self.wait_until_ready()
        while not self.is_closed():
            if (datetime.now().hour< 1 or datetime.now().hour >=13) and datetime.now().minute == 59 :
                idChannel = self.recupereIDChannelPresence()
                fichierLocal = open("chatters.txt","r")
                chatters = fichierLocal.read()
                fichierLocal.close
                
                channel = self.get_channel(idChannel) 

                chatters = chatters.split("\n") 
                reponse =  "**"+chatters[0]+"**\n"              
                del chatters[0]
                for chatter in chatters:
                    if chatter !="" :
                        reponse += "`"+chatter+"`\n"
                await channel.send(reponse)    
            await asyncio.sleep(60)

    def recupereIDChannelPresence(self):
        channelID = 0
        jour = (datetime.now().weekday()) # Renvoie le jour de la semaine sous forme d'entier, lundi étant à 0 et dimanche à 6.
        if (datetime.now().hour<2):
            jour-=1  
            if jour<0: jour=6
            
        if jour==0 : # Lundi
            channelID = 1000820139480055938
        elif jour==1 : # Mardi
            channelID = 1000820225589116938
        elif jour==2 : # Mercredi
            channelID = 1000820314432868534
        elif jour==3 : # Jeudi
            channelID = 1000820402106421308
        elif jour==4 : # Vendredi
            channelID = 1000820495605825536
        return channelID

    async def enregistreSpartiate(self):
        await self.wait_until_ready()
        while not self.is_closed():
            members = self.get_all_members()
            with open("spartiates.txt", "w") as fichier:
                for member in members:
                    fichier.write(member.display_name+"\n")
            await asyncio.sleep(30) 

    def recupereIDChannelPlanning(self):
        '''
        renvois l ID du channel en fonction de l heure  local
        '''
        channelID = 0
        jour = (datetime.now().weekday()) # Renvoie le jour de la semaine sous forme d'entier, lundi étant à 0 et dimanche à 6.
        if (datetime.now().hour<2):
            jour-=1  
            if jour<0: jour=6
            
        if jour==0 : # Lundi
            channelID = 979855578144858163
        elif jour==1 : # Mardi
            channelID = 979855690879361035
        elif jour==2 : # Mercredi
            channelID = 979855775193264128
        elif jour==3 : # Jeudi
            channelID = 979855851340857414
        elif jour==4 : # Vendredi
            channelID = 979856098855120916
        return channelID

    async def enregistrePlanning(self):
        await self.wait_until_ready()
        while not self.is_closed():
            _channelID = self.recupereIDChannelPlanning()
            if (_channelID != 0) :
                channel = self.get_channel(_channelID)
                message = await channel.history(limit=1,oldest_first=True).flatten()
                messageTotal = message[0].content
                ligneMessage = messageTotal.split("\n")
                self.connexionSQL = sqlite3.connect("basededonnees.sqlite") 
                curseur = self.connexionSQL.cursor()
                for ligne in  ligneMessage :
                    ligne = re.sub(r' +', ' ', ligne)
                    ligneCut = ligne.split(" ")
                    
                    nom_streamer = ""
                    if len(ligneCut) > 4 :
                        if ("<@" in ligneCut[4]) :
                            identity =ligneCut[4].replace("<@","").replace(">","")
                            user= get(self.get_all_members(),id=(int(identity)))                   
                            ligneCut[4] = user.display_name
                        nom_streamer = ligneCut[4] 

                    curseur.execute("UPDATE GBoT SET streamer = '"+nom_streamer+"' WHERE planning = '"+ligneCut[0]+" "+ligneCut[1]+" "+ligneCut[2]+" "+ligneCut[3]+"'")

                self.connexionSQL.commit()
                self.connexionSQL.close()
            else:
                listeCreneau=["13h00 - 14h00 :",
                        "14h00 - 15h00 :",
                        "15h00 - 16h00 :",
                        "16h00 - 17h00 :",
                        "17h00 - 18h00 :",
                        "18h00 - 19h00 :",
                        "19h00 - 20h00 :",
                        "20h00 - 21h00 :",
                        "21h00 - 22h00 :",                          
                        "22h00 - 23h00 :",
                        "23h00 - 00h00 :",
                        "00h00 - 01h00 :"]
                self.connexionSQL = sqlite3.connect("basededonnees.sqlite") 
                curseur = self.connexionSQL.cursor()
                for creneau in listeCreneau:
                    curseur.execute("UPDATE GBoT SET streamer = 'vide' WHERE planning = '"+creneau+"'")
                self.connexionSQL.commit()
                self.connexionSQL.close()
            self.sauvePlanning()   
            await asyncio.sleep(60)   

    def DetermineCreneau(self):
            
            debut = datetime.now().strftime('%Hh00')
            fin = (datetime.now()+timedelta(hours=1)).strftime('%Hh00')
            return (debut + " - "+ fin +" :") 
      
    def sauvePlanning(self):
        self.connexionSQL = sqlite3.connect("basededonnees.sqlite") 
        creneauActuel = self.DetermineCreneau()
        cur = self.connexionSQL.cursor()
        cur.execute("SELECT * FROM 'GBoT'")
        rows = cur.fetchall()
        planning = ""
        streamer = "vide"
        listeCreneauJour=["13h00 - 14h00 :",
                        "14h00 - 15h00 :",
                        "15h00 - 16h00 :",
                        "16h00 - 17h00 :",
                        "17h00 - 18h00 :",
                        "18h00 - 19h00 :",
                        "19h00 - 20h00 :",
                        "20h00 - 21h00 :",
                        "21h00 - 22h00 :",                          
                        "22h00 - 23h00 :",
                        "23h00 - 00h00 :"]
        listeCreneauNuit=["00h00 - 01h00 :"]
                   
        for creneau in rows :
            if creneau[1] in listeCreneauJour :
                planning += creneau[1]+" "+creneau[2]+"\n"
                if creneau[1] == creneauActuel :
                    streamer = creneau[2]
        for creneau in rows :
            if creneau[1] in listeCreneauNuit :
                planning += creneau[1]+" "+creneau[2]+"\n"
                if creneau[1] == creneauActuel :
                    streamer = creneau[2]
        with open("planning.txt", "w") as fichier:
                fichier.write(planning)
        with open("streamer.txt", "w") as fichier2:
                fichier2.write(streamer)                
                
        return 

    async def on_message(self, message):
           
        self.connexionSQL = sqlite3.connect("basededonnees.sqlite") 
        # Commande !lurk
        if message.content.startswith("!lurk"):            
            fichierLocal = open("chatters.txt","r")
            chatters = fichierLocal.read()
            fichierLocal.close
            await message.channel.send("`"+chatters+"`")
            
        if message.content.startswith("!planning"): 
            fichierLocal = open("planning.txt","r")
            planning = fichierLocal.read()
            fichierLocal.close
            await message.channel.send("`"+planning+"`")

        if message.content.startswith("!streamer"): 
            fichierLocal = open("streamer.txt","r")
            streamer = fichierLocal.read()
            fichierLocal.close
            if streamer != "vide" :
                reponse = "**`"+streamer+"`** (raid > https://www.twitch.tv/"+streamer+" )"
            else:
                reponse = "**`"+streamer+"`**"
            await message.channel.send("Actuellement le nom du Streamer est : "+reponse)
               
        if message.content.startswith("!bubzz"):
            await message.channel.send("**Créateur du serveur** et représente **les Spartiates** au **World Séries Of Warzone**, le plus gros tournois mondial **Warzone** avec un cash price de **600 000 $**")

        if message.content.startswith("!raid"):
            await message.channel.send("**PRO TIP :** Lancer un RAID\n\
`Via l'appli Twitch sur téléphone :`\n\
1. Tu vas sur ton tchat twitch et tu mets la commande: **/raid pseudo** ( exemple: /raid bubzz_tv ), tu envois le message.\n\
2. Tu attends les 10 secondes demandés.\n\
3. Tu appuies sur 'Lancer' pour lancer le raid.\n\
\n\
`Via le gestionnaire du stream (Soit via PC, soit via la page internet de ton téléphone) :`\n\
1. Tu vas dans ton Tableau de bord des créateurs, puis Gestionnaire de stream.\n\
2. Tout à droite, c'est écrit « Lancer un raid sur une chaîne », tu appuies dessus.\n\
3. Ça t'ouvre un page, tu notes le pseudo de la personne que tu dois raid et tu appuis sur « Lancer un raid » qui se trouve en bas à droite.\n\
4. Tu attends les 10 secondes demandées.\n\
5. Tu appuies sur « Lancer un raid maintenant ».\n")

        print (message.author,":",message.content)

        
    
            
if __name__ == "__main__":
    
    load_dotenv(dotenv_path="config")
    bot = GBot()
    bot.run(os.getenv("TOKEN"))
    





