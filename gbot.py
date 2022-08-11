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
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(message)s", filemode="w")


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

class GBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.messages = True
        intents.members = True
        super().__init__(command_prefix="!",intents = intents)
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"basededonnees.sqlite"))
        curseur = self.connexionSQL.cursor()
        curseur.execute('''CREATE TABLE IF NOT EXISTS GBoT(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            planning TEXT,
            streamer TEXT,
            UNIQUE(planning)
            )''')
        curseur.execute('''CREATE TABLE IF NOT EXISTS Spartiate(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            pseudo TEXT UNIQUE,
            score INTEGER,
            total INTEGER
            )''')
        #curseur.execute('''ALTER TABLE IF NOT EXISTS Spartiate ADD COLUMN total INTEGER''')
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
        curseur.execute('''INSERT OR REPLACE INTO Spartiate (pseudo, score,total) VALUES (?,?,?)''', ("none",0,0))
        self.connexionSQL.commit()
        self.connexionSQL.close()


            
    async def on_ready(self):

        self.AfficheMenu()
        self.bg_task_RecupereSpartiate = self.loop.create_task(self.enregistreSpartiate())
        self.bg_task_RecuperePlanning = self.loop.create_task(self.enregistrePlanning())
        self.bg_task_EcrisPresence = self.loop.create_task(self.envoisMessage())
        self.bg_task_SessionSpartiate = self.loop.create_task(self.appelSessionSpartiate())

        await self.wait_until_ready()
        
        print (RED + "> "+CYAN+"GBoT Process correctement initialisé.")
        

    def AfficheMenu(self):
        print("\n",BBLACK,"                         "+BBLUE+YELLOW+ "SPARTAN VIEWERSPY"+BBLACK+"\n")
        '''
        print ("  "+YELLOW+"[F1]"+WHITE + " : Affiche Planning.txt",end='')
        print ("  "+YELLOW+"[F2]"+WHITE + " Ouvre DATA Dir",end='')
        print ("  "+YELLOW+"[F5]"+WHITE + " Refresh manuel")
        '''
    async def appelSessionSpartiate(self):
        await self.wait_until_ready()
        while not self.is_closed():
            SessionSpartiate()
            await asyncio.sleep(240)
            
    async def envoisMessage(self):
        await self.wait_until_ready()
        while not self.is_closed():
            # minute 1    
            #Envois message horaire Streamer en ligne Spartiate  
            if (datetime.now().hour < 1 or datetime.now().hour >=13) and datetime.now().minute == 1 : 
                fichierLocal2 = open(os.path.join(GBOTPATH,"streamer.txt"),"r")
                streamer = fichierLocal2.read()
                fichierLocal2.close
                idChannel = 979853240642437171
                channel = self.get_channel(idChannel)
                messages = await channel.history(limit=10).flatten()
                for message in messages :
                    await message.delete()
                if streamer != "" :
                    reponse = "**`"+streamer+"`** (raid > https://www.twitch.tv/"+streamer+" )"
                    await channel.send("Donnez de la force à "+reponse)
                    
            # minute 58
            #Envois message horaire presence Spartiate
            if (datetime.now().hour< 1 or datetime.now().hour >=13) and datetime.now().minute == 58 :
                idChannel = self.recupereIDChannelPresence()
                fichierLocal = open(os.path.join(GBOTPATH,"chatters.txt"),"r")
                chatters = fichierLocal.read()
                fichierLocal.close
                
                channel = self.get_channel(idChannel) 

                self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"basededonnees.sqlite"))
                cur = self.connexionSQL.cursor()
                cur.execute("SELECT * FROM 'Spartiate'")
                rows = cur.fetchall()                
                chatters = chatters.split("\n") 
                reponse =  "**"+chatters[0]+"**\n"              
                del chatters[0]
                for chatter in chatters:
                    if chatter !="" :
                        reponse += "`"+chatter+"`\n"
                        flagTrouve = False
                        for spartiate in rows :
                            if spartiate[1] == chatter :
                                score = spartiate[2] + 1
                                if spartiate[3] != None :
                                    scoreTotal = spartiate[3] + 1
                                else:
                                    scoreTotal = score
                                flagTrouve = True
                                cur.execute("UPDATE Spartiate SET score = "+str(score)+", total = "+str(scoreTotal)+ " WHERE pseudo  = '"+chatter+"'")
                                
                            if flagTrouve == False :
                                cur.execute('''INSERT OR REPLACE INTO Spartiate (pseudo, score,total) VALUES (?,?,?)''', (chatter,1,1))  
                reponse2 =""                
                if datetime.now().hour < 1: 
                    # Recupere les scores pour les afficher une derniere fois
                    cur.execute("SELECT pseudo,score,total FROM 'Spartiate' WHERE total>0 ORDER BY total DESC, score DESC, pseudo ASC")
                    rows = cur.fetchall()
                    reponse2 +=':medal: __**Score des SPARTIATES présent sur la journée :**__ *(Score journée / Total de la semaine)*\n'
                    for data in rows :
                        (spartiate,score,scoreTotal) = data
                        if scoreTotal == None :
                            scoreTotal=score
                        reponse2 += "`"+spartiate+"`" + " : **"+ str(score) +"** / "+ str(scoreTotal) +"\n"
                    # Remet les score a 0
                    cur.execute("SELECT pseudo,score,total FROM 'Spartiate' WHERE score>0 ORDER BY total DESC, pseudo ASC")
                    rows = cur.fetchall()
                    for data in rows :
                        (spartiate,score,total) = data
                        cur.execute("UPDATE Spartiate SET score = 0 WHERE pseudo  = '"+spartiate+"'")        
                self.connexionSQL.commit()
                self.connexionSQL.close()    
                        
                await channel.send(reponse)
                if reponse2 != "": 
                    await channel.send(reponse2)
                
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
            channelID = 1005910080031559680 
        elif jour==4 : # Vendredi
            channelID = 1005912896011784275
        return channelID

    async def enregistreSpartiate(self):
        await self.wait_until_ready()
        while not self.is_closed():
            members = self.get_all_members()
            with open(os.path.join(GBOTPATH,"spartiates.txt"), "w") as fichier:
                for member in members:
                    fichier.write(member.display_name.lower()+"\n")
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
                self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"basededonnees.sqlite")) 
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

                    curseur.execute("UPDATE GBoT SET streamer = '"+nom_streamer.lower()+"' WHERE planning = '"+ligneCut[0]+" "+ligneCut[1]+" "+ligneCut[2]+" "+ligneCut[3]+"'")

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
                self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"basededonnees.sqlite"))
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
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"basededonnees.sqlite")) 
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

            
        with open(os.path.join(GBOTPATH,"planning.txt"), "w") as fichier:
                fichier.write(planning)
        with open(os.path.join(GBOTPATH,"streamer.txt"), "w") as fichier2:
                fichier2.write(streamer)                
        if streamer == "vide" :
            with open(os.path.join(GBOTPATH,"chatters.txt"), "w") as fichier3:
                fichier3.write("vide")          
        return 

    async def on_message(self, message):
           
 
        # Commande !lurk
        if message.content.startswith("!lurk"):            
            fichierLocal = open(os.path.join(GBOTPATH,"chatters.txt"),"r")
            chatters = fichierLocal.read()
            fichierLocal.close
            await message.channel.send("`"+chatters+"`")
            
        if message.content.startswith("!planning"): 
            fichierLocal = open(os.path.join(GBOTPATH,"planning.txt"),"r")
            planning = fichierLocal.read()
            fichierLocal.close
            await message.channel.send("`"+planning+"`")

        if message.content.startswith("!streamer"): 
            fichierLocal = open(os.path.join(GBOTPATH,"streamer.txt"),"r")
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

        if message.content.startswith("!pub"):
            await message.channel.send("Bonjour à toi jeune streamer/streameuse,\
tu débutes dans le stream et tu galères à avoir ton affiliation ou à te créer une communauté ? Ne t'en fais pas le serveur Discord __**\"Spartiates Entraide Twitch\"**__ est là pour te donner un coup de pouce.\n\
\nLe principe est simple, il y a plusieurs horaires sous forme de créneaux disponibles du lundi au vendredi, il suffit simplement de t'inscrire à l'un d'entre eux pour recevoir un raid et voir ton nombre de viewers grimper en flèche et ton tchat se déchaîner.\n\
\nÉvidemment, l'entraide est le mot d'ordre, alors on compte également sur toi pour faire parti(e) de la chaîne des raids et être présent(e) sur les streams des autres personnes qui adhèrent à ce projet.\n\
\nAllez n'attend pas plus longtemps et deviens toi aussi un Spartiate en rejoignant ce serveur ici : https://discord.gg/SzDnhgEWrn )\n")
            
        if message.content.startswith("!score"):
            if (datetime.now().hour< 1 or datetime.now().hour >=13) : 
                self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"basededonnees.sqlite")) 
                cur = self.connexionSQL.cursor()
                cur.execute("SELECT pseudo,score,total FROM 'Spartiate' WHERE total>0 ORDER BY total DESC, score DESC, pseudo ASC")
                rows = cur.fetchall()
                sortieFlux =':medal: __**Score des SPARTIATES présent sur la journée :**__ *(Score journée / Total de la semaine)*\n'
                for data in rows :
                    (spartiate,score,scoreTotal) = data
                    sortieFlux += "`"+spartiate+"`" + " : **"+ str(score) +"** / "+ str(scoreTotal) +"\n"
            else :
                sortieFlux = ':medal: __**Score des SPARTIATES présents sur la journée :**__:medal:\n Absence de resultat en dehors des creneaux horaires de stream.'         
            await message.channel.send(sortieFlux)
            
        if message.content.startswith("!aide") or message.content.startswith("!gbot"):
            await message.channel.send("**Commande GBoT :**\n\
• `!planning` : renvois le planning de la journée.\n\
• `!streamer` : renvois le streamer actuel du créneau horaire.\n\
• `!lurk` : renvois la liste des spartiates qui visualisent le stream en cours.\n\
• `!bubzz` : Créateur du channel Discord 'Les Spartiates'.\n\
• `!raid` : tuto pour réaliser un raid.\n\
• `!pub` : Obtenir le lien à diffuser pour rejoindre le discord SPARTIATES.\n\
• `!score` : Obtient les scores des spartiates pour la journée en cours.\n\
• `!aide` ou `!gbot` : cette aide.\n\
")



        print (message.author,":",message.content)

if __name__ == "__main__":
    
    load_dotenv(dotenv_path=os.path.join(GBOTPATH,"config"))
    bot = GBot()
    bot.run(os.getenv("TOKEN"))
    





