
import discord
from discord.ext import commands
from discord.utils import get
from discord import app_commands
from discord import Embed,Colour,SelectOption
from discord.ui import Select,View
import os
import logging
from datetime import datetime,timedelta
import json
import requests
from colorama import Fore, Back
from dotenv import load_dotenv
import re 
import asyncio
import sqlite3

description = '''Le GBoT pour le serveur RaidZ🅾️ne.
gere les streamers et leurs viewers en ajoutant quelques commandes sympas.'''

# Parametres 
logging.basicConfig(level=logging.ERROR,
                    format="%(asctime)s %(message)s", filename='debug.log',filemode="w")

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

# Gestion Config
GBOTPATH, filename = os.path.split(__file__)
load_dotenv(dotenv_path=os.path.join(GBOTPATH,"config"))
DEBUG = os.getenv("DEBUG")
TOKEN = os.getenv("TOKEN")

#Channel
channelID = {
    "lundi": 1037341064018796604,
    "mardi": 1037341103747256361,
    "mercredi": 1037341153466536037,
    "jeudi": 1037341185569730561,
    "vendredi": 1037341222341202020,
    "samedi": 1037341259657920512,
    "dimanche": 1039082787417903154,
    "presence":1037347680965365791,
    "annonce":1037341418722705468,
    "commandes-log": 1037395917919227985,
    "raid_en_cours": 1037340918937833543,
    "blabla": 1037341465099120672,
    "guild":1037338719780339752,
    }


#Guild    
PROD_GUILD = discord.Object(channelID["guild"])
TEST_GUILD = None
if DEBUG == "True":
    GUILD = TEST_GUILD
else :
    GUILD = PROD_GUILD

    
class GBoT(commands.Bot):
    
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.messages = True
        intents.members = True
        super().__init__(command_prefix ="!",intents=intents)

        # Initialise Table SQL
        self.initTableSql() 

    ##################################
    ##     EVENEMENTS DISCORD.PY    ##
    ##################################
    async def on_ready(self):
        """
        S'affiche quand l'Initialisation Bot est terminé
        """
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        
    async def setup_hook(self) -> None:
        """
        Initialise les taches tournant en tache de fond et appelable régulierement selon un timing en seconde
        """
        await self.tree.sync(guild=GUILD)
        # create the background task and run it in the background
        self.bg_task_ProcedureLancement = self.loop.create_task(self.EnchaineProcedure(60))
        self.bg_task_SessionMembres = self.loop.create_task(self.appelSessionMembres(240))

    async def on_message(self, message):
        """
        Evennement levé à chaque message transmis sur le serveur Discord

        Args:
            message (Discord.message): objet message renvoyé par l API Discord
        """
        admin = False
        # determine si la commande est lancée par un Admin
        if message.author.display_name == 'GToF_':
            admin=True
            
        if admin and message.content.startswith(">nomine"):
                await self.distributionRole(message.channel)
        # Commande >efface
        if admin and message.content.startswith(">efface"):
            channel = self.get_channel(message.channel.id)
            messages = [messageAEffacer async for messageAEffacer in channel.history(limit=10)]
            for messageAEffacer in messages :
                await messageAEffacer.delete()       


    async def EnchaineProcedure(self, timing):
        
        await self.wait_until_ready()
        while not self.is_closed():
            
            # ENREGISTRE Membres
            self.enregistreMembres()

            # RECUPERE PLANNING               
            await self.recuperePlanning()   

            
            # SAUVEGARDE PLANNING SUIR DISQUE                
            self.sauvePlanning() 

            
            # ENVOIS MESSAGE 
            await self.envoisMessage()


            await asyncio.sleep(timing) 

    async def envoisMessage(self):
        # minute 1    
        #Envois message horaire Streamer en ligne Membres  
        if datetime.now().minute == 1 : 
            with open(os.path.join(GBOTPATH,"streamer.txt"),"r") as fichier :
                streamer = fichier.read()
            channel = self.get_channel(channelID["raid_en_cours"])
            messages = [messageAEffacer async for messageAEffacer in channel.history(limit=10)]
            for messageAEffacer in messages :
                await messageAEffacer.delete()

            if streamer.strip() != "" and streamer != "vide" :
                reponse = "**`"+streamer+"`** (raid > https://www.twitch.tv/"+streamer+" )"
                await channel.send("Donnez de la force à "+reponse)
            else :
                reponse = "**`Il n y a pas de Raid Actuellement**"
                await channel.send(reponse)
                    
            # il est minuit ?
            # reinitialise les scores du jours à 0
            if datetime.now().hour == 0 :
                self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
                cur = self.connexionSQL.cursor()
                cur.execute("SELECT * FROM 'Membre'")
                rows = cur.fetchall()
                jour = self.determineJour()
                for Membre in rows :
                    pseudo = Membre[1]
                    score_lundi = Membre[2]
                    score_mardi = Membre[3]
                    score_mercredi = Membre[4]
                    score_jeudi = Membre[5]
                    score_vendredi = Membre[6]
                    score_samedi = Membre[7]
                    score_dimanche = Membre [8]
                    if jour =="lundi" :
                        score_lundi = 0
                    elif jour == "mardi" :
                        score_mardi = 0
                    elif jour == "mercredi" :
                        score_mercredi = 0
                    elif jour == "jeudi" :
                        score_jeudi = 0
                    elif jour == "vendredi" :
                        score_vendredi = 0
                    elif jour == "samedi" :
                        score_samedi = 0
                    elif jour == "dimanche" :
                        score_dimanche = 0
                    scoreTotal = score_lundi+score_mardi+score_mercredi+score_jeudi+score_vendredi+score_samedi+score_dimanche
                    req = "UPDATE Membre SET lundi = "+str(score_lundi)+\
                                ",mardi = "+str(score_mardi)+\
                                ",mercredi = "+str(score_mercredi)+\
                                ",jeudi = "+str(score_jeudi)+\
                                ",vendredi = "+str(score_vendredi)+\
                                ",samedi = "+str(score_samedi)+\
                                ",dimanche = "+str(score_dimanche)+\
                                ",total = "+str(scoreTotal)+ " WHERE pseudo  = '"+pseudo+"'"
                    cur.execute(req)
                
                self.connexionSQL.commit()
                self.connexionSQL.close() 
                print ("Stats Journalière remise a zero")
            
        if datetime.now().minute == 59 :

            with open(os.path.join(GBOTPATH,"chatters.txt"),"r") as fichier:
                chatters = fichier.read()
                                
            channel = self.get_channel(channelID["presence"]) 
            jour = self.determineJour()    
            self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
            cur = self.connexionSQL.cursor()
            cur.execute("SELECT * FROM 'Membre'")
            rows = cur.fetchall()
            score = 0                
            chatters = chatters.split("\n") 
            reponse =  f"**{chatters[0]}** >`{chatters[1]}` (streamer)\n" 
            streamer = chatters[1]
            del chatters[0]
            del chatters[0] #EFFACE LE STREAMER POUR NE PAS LUI COMPTER DE POINT
            for chatter in chatters:
                if chatter !="" :
                    reponse += f"▫️`{chatter}`\n"
                    score += 1
                    flagTrouve = False
                    for Membre in rows :
                        if Membre[1] == chatter :
                            score_lundi = Membre[2]
                            score_mardi = Membre[3]
                            score_mercredi = Membre[4]
                            score_jeudi = Membre[5]
                            score_vendredi = Membre[6]
                            score_samedi = Membre[7]
                            score_dimanche = Membre [8]
                            if jour =="lundi" :
                                score_lundi += 1
                            elif jour == "mardi" :
                                score_mardi += 1
                            elif jour == "mercredi" :
                                score_mercredi += 1
                            elif jour == "jeudi" :
                                score_jeudi +=1
                            elif jour == "vendredi" :
                                score_vendredi += 1
                            elif jour == "samedi" :
                                score_samedi += 1
                            elif jour == "dimanche" :
                                score_dimanche += 1
                            scoreTotal = score_lundi+score_mardi+score_mercredi+score_jeudi+score_vendredi+score_samedi+score_dimanche
                            flagTrouve = True
                            req = "UPDATE Membre SET lundi = "+str(score_lundi)+\
                                ",mardi = "+str(score_mardi)+\
                                ",mercredi = "+str(score_mercredi)+\
                                ",jeudi = "+str(score_jeudi)+\
                                ",vendredi = "+str(score_vendredi)+\
                                ",samedi = "+str(score_samedi)+\
                                ",dimanche = "+str(score_dimanche)+\
                                ",total = "+str(scoreTotal)+ " WHERE pseudo  = '"+chatter+"'"
                            cur.execute(req)

                    if flagTrouve == False :
                        if chatter != "vide" :
                            score_lundi = 0
                            score_mardi = 0
                            score_mercredi = 0
                            score_jeudi = 0
                            score_vendredi = 0
                            score_samedi = 0
                            score_dimanche = 0
                            if jour =="lundi" :
                                score_lundi += 1
                            elif jour == "mardi" :
                                score_mardi += 1
                            elif jour == "mercredi" :
                                score_mercredi += 1
                            elif jour == "jeudi" :
                                score_jeudi += 1
                            elif jour == "vendredi" :
                                score_vendredi += 1
                            elif jour == "samedi" :
                                score_samedi +=1
                            elif jour == "dimanche" :
                                score_dimanche +=1
                            scoreTotal = 1
                            cur.execute("INSERT OR REPLACE INTO Membre(pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total) VALUES (?,?,?,?,?,?,?,?,?)",(chatter,score_lundi,score_mardi,score_mercredi,score_jeudi,score_vendredi,score_samedi,score_dimanche,scoreTotal))
            reponse += f"*{score} streamers présents sur le créneau.*"
            self.connexionSQL.commit()
            self.connexionSQL.close()
            await channel.send(reponse)
            dataHiScore = self.recupereHiScore()
            hiScore=dataHiScore[3]
            if score>hiScore :
                self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
                cur = self.connexionSQL.cursor()
                req = "UPDATE HIScore SET date = '"+datetime.now().strftime("%d-%m-%Y %Hh00")+"',\
                    pseudo = '"+streamer+"',\
                    score = "+str(score)+" WHERE id  = 1"
                cur.execute(req)
                self.connexionSQL.commit()
                self.connexionSQL.close()
                channel = self.get_channel(channelID["blabla"])
                await self.afficheHiScore(channel)
                print("fin")

    async def appelSessionMembres(self,timing_sessionMembres):
        await self.wait_until_ready()
        while not self.is_closed():
            self.sessionMembre()
            await asyncio.sleep(timing_sessionMembres) 

    def enregistreMembres(self):
        with open(os.path.join(GBOTPATH,"Membres.txt"), "w") as fichier:
            for member in self.get_all_members():
                if not member.bot :
                        name = member.display_name.lower()
                        allowed_chars = ['a', 'b', 'c','d',"e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","0","1","2","3","4","5","6","7","8","9","_"]
                        chars = set(allowed_chars)
                        res = ''.join(filter(lambda x: x in chars, name))
                        if res != name :
                            print (f"\n{RED}ATTENTION : {WHITE}l'utilisateur {RED+name+WHITE} renvoit une erreur sur son pseudo.\n")
                        fichier.write(res+"\n")
    def DetermineCreneau(self):
            
        debut = datetime.now().strftime('%Hh00')
        fin = (datetime.now()+timedelta(hours=1)).strftime('%Hh00')
        return (debut + " - "+ fin +" :") 

    def sauvePlanning(self):
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite")) 
        creneauActuel = self.DetermineCreneau()
        cur = self.connexionSQL.cursor()
        cur.execute("SELECT * FROM 'GBoT'")
        rows = cur.fetchall()
        planning = ""
        streamer = "vide"
        listeCreneauJour=["00h00 - 01h00 :",
                    "01h00 - 02h00 :",
                    "02h00 - 03h00 :",
                    "03h00 - 04h00 :",
                    "04h00 - 05h00 :",
                    "05h00 - 06h00 :",
                    "06h00 - 07h00 :",
                    "07h00 - 08h00 :",
                    "08h00 - 09h00 :",
                    "09h00 - 10h00 :",
                    "10h00 - 11h00 :",
                    "11h00 - 12h00 :",
                    "12h00 - 13h00 :",
                    "13h00 - 14h00 :",
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

        for creneau in rows :
            if creneau[1] in listeCreneauJour :
                planning += creneau[1]+" "+creneau[2]+"\n"
                if creneau[1] == creneauActuel :
                    streamer = creneau[2]
        self.connexionSQL.commit()
        self.connexionSQL.close()

        with open(os.path.join(GBOTPATH,"planning.txt"), "w") as fichier:
                fichier.write(planning)
        with open(os.path.join(GBOTPATH,"streamer.txt"), "w") as fichier2:
                fichier2.write(streamer)                
        if streamer == "vide" :
            with open(os.path.join(GBOTPATH,"chatters.txt"), "w") as fichier3:
                fichier3.write("vide")          
        return

    def recupereIDChannelPlanning(self):
        '''
        renvois l ID du channel en fonction de l heure  local
        '''
        jour = (datetime.now().weekday()) # Renvoie le jour de la semaine sous forme d'entier, lundi étant à 0 et dimanche à 6.
        if jour==0 : # Lundi
            channel = channelID["lundi"]
        elif jour==1 : # Mardi
            channel = channelID["mardi"]
        elif jour==2 : # Mercredi
            channel = channelID["mercredi"]
        elif jour==3 : # Jeudi
            channel = channelID["jeudi"]
        elif jour==4 : # Vendredi
            channel = channelID["vendredi"]
        elif jour==5 : # Samedi
            channel = channelID["samedi"]
        elif jour==6 : # Dimanche
            channel = channelID["dimanche"]
            
        return channel

    async def recuperePlanning(self):
        _channel = self.recupereIDChannelPlanning()
        if (_channel != 0) :
            channel = self.get_channel(_channel)
            messages = [messageAEffacer async for messageAEffacer in channel.history(limit=1,oldest_first=True)]
            message = messages[0].content
            ligneMessage = message.split("\n")
            
            self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite")) 
            curseur = self.connexionSQL.cursor()
            
            for ligne in  ligneMessage :
                ligne = re.sub(r' +', ' ', ligne.strip()) #remplace les multiples espaces par un seul
                ligneCut = ligne.split(" ")
                
                nom_streamer = ""
                if len(ligneCut) > 4 :
                    if ("<@" in ligneCut[4]) :
                        identity =ligneCut[4].replace("<@","").replace(">","")
                        user= get(self.get_all_members(),id=(int(identity)))                   
                        ligneCut[4] = user.display_name
                    nom_streamer = ligneCut[4] 
                sqlreq ="UPDATE GBoT SET streamer = '"+nom_streamer.lower()+"' WHERE planning = '"+ligneCut[0]+" "+ligneCut[1]+" "+ligneCut[2]+" "+ligneCut[3]+"'"
                curseur.execute(sqlreq)

            self.connexionSQL.commit()
            self.connexionSQL.close()            
        else:
            listeCreneau=["00h00 - 01h00 :",
                    "01h00 - 02h00 :",
                    "02h00 - 03h00 :",
                    "03h00 - 04h00 :",
                    "04h00 - 05h00 :",
                    "05h00 - 06h00 :",
                    "06h00 - 07h00 :",
                    "07h00 - 08h00 :",
                    "08h00 - 09h00 :",
                    "09h00 - 10h00 :",
                    "10h00 - 11h00 :",
                    "11h00 - 12h00 :",
                    "12h00 - 13h00 :",
                    "13h00 - 14h00 :",
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
            self.connexionSQL =  sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
            curseur = self.connexionSQL.cursor()
            for creneau in listeCreneau:
                curseur.execute("UPDATE GBoT SET streamer = 'vide' WHERE planning = '"+creneau+"'")
            self.connexionSQL.commit()
            self.connexionSQL.close()


    def recupereScoresMembres(self):
        # Recupere les scores pour les afficher une derniere fois
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()  
        cur.execute("SELECT pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total FROM 'Membre' WHERE total>0 ORDER BY total DESC, pseudo ASC")
        rows = cur.fetchall()
        self.connexionSQL.close()
        
        reponse = ""
        
        for data in rows :
            (pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,scoreTotal) = data
            if scoreTotal == None :
                scoreTotal=score
            reponse += "• `"+pseudo+"`" + " : **"+str(scoreTotal)+"**\n"

        if len(reponse)>1980 :
            messageTotal= reponse
            reponse1 = messageTotal[slice(0,1980)]
            reponse2 = messageTotal[slice(1980, len(messageTotal))]
        else :
            reponse1= reponse
            reponse2 = ""

        return (reponse1,reponse2)

    ####################################
    ##   REPONSE APPEL PAR COMMANDE / ##
    ####################################    
    def commande_resa_verifjour(self,jour):
        listeJour = ["lundi","mardi","mercredi","jeudi","vendredi","samedi","dimanche"]
        if jour in listeJour :
            return jour
        else:
            return "False"

    async def commande_resa_renvoisCreneau(self, jour):
        """Renvois la liste des creneau disponible pour un jour donné"""
        channel = self.get_channel(channelID[jour])
        messages = [MessagesChannel async for MessagesChannel in channel.history(limit=1,oldest_first=True)]
        message = messages[0].content
        ligneMessage = message.split("\n")
        listeCreneaux=[]
        
        for ligne in  ligneMessage :
            ligne = re.sub(r' +', ' ', ligne.strip()) #remplace les multiples espaces par un seul
            ligneCut = ligne.split(" ")

            if len(ligneCut) == 4 :
                creneau = ligneCut[0]+" "+ligneCut[1]+" "+ligneCut[2]+" "+ligneCut[3]
                listeCreneaux.append(creneau)
        return listeCreneaux     
    
    async def commande_resa_valideCreneaux(self,membre,jour,listeDemande):
        """Inscrit la liste des creneaux fourni pour un jour donné"""
        channel = self.get_channel(channelID[jour])
        messages = [MessagesChannel async for MessagesChannel in channel.history(limit=1,oldest_first=True)]
        message = messages[0].content
        ligneMessage = message.split("\n")
        listeCreneaux=[]
        messageReponse = ""
        conflitCreneau = False
        for ligne in  ligneMessage :
            if ligne != '':
                ligne = re.sub(r' +', ' ', ligne.strip()) #remplace les multiples espaces par un seul
                ligneCut = ligne.split(" ")
                if ligneCut[0]+" "+ligneCut[1]+" "+ligneCut[2]+" "+ligneCut[3] in listeDemande :
                    if len(ligneCut) >4 :
                         messageReponse += ligne + "\n"
                         conflitCreneau = True
                    else :
                        messageReponse += ligneCut[0]+" "+ligneCut[1]+" "+ligneCut[2]+" "+ligneCut[3]+' <@'+str(membre) +'>\n'            
                else : 
                    messageReponse += ligne + "\n"
        if conflitCreneau:
            channel = self.get_channel(channelID["commandes-log"])
            await channel.send(f'{datetime.now().strftime("%d-%m-%Y %Hh00")} : <@{str(membre)}> à généré un conflit de créneaux ({listeDemande})')  
        else :
            channel = self.get_channel(channelID[jour])
            messages = [messageAEffacer async for messageAEffacer in channel.history(limit=4)]
            for messageAEffacer in messages :
                await messageAEffacer.delete() 
            await channel.send(messageReponse) 
            channel = self.get_channel(channelID["commandes-log"])
            await channel.send(f'`{datetime.now().strftime("%c")}` > Réservation par <@{str(membre)}> pour la journée de __{jour}__ (*{listeDemande}*).') 

                
    def commande_resa_droitMembreNonValide(self,auteur,jourResa):
        auteur = str(auteur)
        auteur = auteur.lower()
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()  
        cur.execute(f"SELECT pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total FROM 'Membre' WHERE pseudo='{auteur}'")
        dataMembre = cur.fetchone()
        if not dataMembre : return True
        pseudo = dataMembre[0]
        score = dataMembre[1] + dataMembre[2] + dataMembre[3] + dataMembre[4] + dataMembre[5] + dataMembre[6] + dataMembre[7]
        self.connexionSQL.close()

        aujourdhui = (datetime.now().weekday())
        jourResaID = {
            "lundi": 0,
            "mardi": 1,
            "mercredi": 2,
            "jeudi": 3,
            "vendredi": 4,
            "samedi": 5,
            "dimanche": 6
            }
        
        jourResa= jourResaID[jourResa]
        dayDelta=aujourdhui

        if score > 30 :
            auteurDroit = 8
        elif score > 20 :
            auteurDroit = 3
        elif score > 10 :
            auteurDroit = 2
        elif score > 5 :
            auteurDroit = 1
        else :
            return True 
            
        for index in range(auteurDroit):
            if dayDelta==jourResa :
                return False          
            dayDelta += 1
            if dayDelta>6:
                dayDelta = 0
        return True

    async def commande_afficheScoreMembre(self,ctx):
        # Recupere les scores pour les afficher une derniere fois
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        jour = self.determineJour()
        cur = self.connexionSQL.cursor()  
        cur.execute("SELECT pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total FROM 'Membre' WHERE total>0 ORDER BY total DESC, pseudo ASC")
        rows = cur.fetchall()
        self.connexionSQL.close()
        
        auteur = ctx.author
        name = auteur.display_name
        pfp = auteur.display_avatar
        embed = Embed(title="Relevé des scores",colour= Colour.random())
        embed.set_author(name=f"{name}",icon_url=auteur.display_icon)
        embed.set_thumbnail(url=f"{pfp}")

        place = 1
        scoreTotal = 0
        resultatMax=15
        for data in rows :
            (membre,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total) = data
            if jour == 'lundi' : score = lundi
            elif jour == 'mardi' : score = mardi
            elif jour == 'mercredi' : score = mercredi
            elif jour == 'jeudi' : score = jeudi
            elif jour == 'vendredi' : score = vendredi
            elif jour == 'samedi' : score = samedi
            elif jour == 'dimanche' : score = dimanche
            total = lundi + mardi + mercredi + jeudi + vendredi + samedi + dimanche 
            if membre == auteur.display_name.lower()   :
                embed.add_field(name="Ton score :",value=f"Tu obtiens le score de **{score} pt** aujourd'hui pour un cumul de **{total} pts** ces 7 derniers jours.",  inline = False)
        reponse = "\u200b"
        for data in rows :
            (membre,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total) = data
            if scoreTotal > total :
                place += 1
            scoreTotal=total
            medaille = " "
            if place == 1:
                medaille = ":first_place:"
            elif place == 2:
                medaille = ":second_place:"
            elif place == 3:
                medaille = ":third_place:"
            reponse += medaille + "  n° "+str(place) +" : `"+membre+"` -➤ "+ str(total)+" pts\n" 
            resultatMax-=1
            if resultatMax==0: break          
        embed.add_field(name=":medal: Le top score de la semaine: :medal:",value = reponse,inline = False) 
    
        await ctx.send(embed=embed)
            

    ####################################
    ##   FONCTIONS  COMMUNES          ##
    ####################################  
    
    def recupereHiScore(self):
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()  
        cur.execute("SELECT id,date,pseudo,score FROM 'HIScore' WHERE id=1")
        dataHiScore = cur.fetchone()
        self.connexionSQL.close()
        return dataHiScore

    def determineJour (self):
        '''
        renvois le jour a prendre sous forme de texte
        '''
        jour = (datetime.now().weekday()) # Renvoie le jour de la semaine sous forme d'entier, lundi étant à 0 et dimanche à 6.
        if jour==0 : # Lundi
            today = "lundi"
        elif jour==1 : # Mardi
            today = "mardi"
        elif jour==2 : # Mercredi
            today = "mercredi"
        elif jour==3 : # Jeudi
            today = "jeudi"
        elif jour==4 : # Vendredi
            today = "vendredi"
        elif jour==5 : # Samedi
            today = "samedi"
        elif jour==6 : # Samedi
            today = "dimanche"
        return today   
    
    async def afficheHiScore(self,channel) :
        # Recupere les scores pour les afficher une derniere fois
        rows=self.recupereHiScore()
        embed = Embed(title="Nouveau Record !!!",colour= Colour.dark_red())
        embed.set_author(name=f"serveur RaidZ🅾️ne",icon_url="https://www.su66.fr/raidzone/logo.png")
        embed.set_thumbnail(url=f"https://www.su66.fr/raidzone/guinness.png")
        embed.add_field(name=f"__Score :__",value=f" **{rows[3]}** viewers le {rows[1]} chez **{rows[2]}**.",  inline = False)
        embed.set_footer(text="Staff RaidZ🅾️ne",icon_url="https://www.su66.fr/raidzone/logo.png")
        await channel.send(embed=embed)

    async def afficheScore(self,channel):
        
        reponse1,reponse2 = self.recupereScoresMembres()

        await channel.send('\n:medal: __**Score des Membres présent sur la journée :**__ *(Score journée --> Total de la semaine)*\n')
        await channel.send(reponse1)
        if reponse2 != "":
            await channel.send(reponse2)
        await channel.send("\n*Chaque présence sur un creneau ajoute 1 pt. Le Cumul de point sur la semaine vous permettra d'acceder au Grade de **VIP** pour la semaine suivante.*\n\n")

    def recupereVIP(self):
        users = self.get_all_members()
        listeRole= self.get_guild(channelID["guild"]).roles
        listeVIP=[]
        message = "\n:medal: __**V.I.P**__\n"
        for membre in users:
                if get(listeRole, name="VIP") in membre.roles:
                    listeVIP.append(membre.display_name)
        for VIP in listeVIP:
            message +="> • `"+VIP+"`\n"
        return message
                    
    async def afficheVIP(self,channel):
        """
        Affiche les titulaires d'un role VIP sur le channel du serveur discord
        passé en paramètre

        Args:
            channel (Discord.channel): Channel du serveur discord sur lequel 
                                       sera renvoyé le message d'information.
        """
        await channel.send(self.recupereVIP())
        
    async def distributionRole (self,channel):
        # Supprime le role des sparts supremes actuels et attribut en fonction du score 
        # channel = self.get_channel(979857092603162695) # channel annonce
        users = self.get_all_members()
        listeRole= self.get_guild(channelID["guild"]).roles
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()
        cur.execute("SELECT pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total FROM 'Membre' WHERE total>=35 ORDER BY total DESC, pseudo ASC")
        rows = cur.fetchall()
        classementMembres ={}
        for data in rows :
            (membre,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total) = data
            classementMembres[membre]=total
        self.connexionSQL.close()
        
        for Membre in users:
                if get(listeRole, name="VIP") in Membre.roles:
                    await Membre.remove_roles(get(listeRole, name="VIP"))
                    print("on retire ",Membre.display_name)
             
                if Membre.display_name.lower() in classementMembres :                    
                        await Membre.add_roles(get(listeRole, name="VIP"))
                        print("on ajoute ",Membre.display_name," comme VIP")    

        # A deplacer vers distribution role apres debug
        users = self.get_all_members()
        listeRole= self.get_guild(channelID["guild"]).roles
        listeVIP=[]
        message = ''
        for Membre in users:
                if get(listeRole, name="VIP") in Membre.roles:
                    listeVIP.append(Membre.id)
                    
        message =  "\nBonjour à tous, voici les résultats d'attribution des rôles pour cette semaine :\n\n"
        message += ":yellow_circle: Les <@&1037343347905409116> sont :\n"
        message +="   >" 
        for VIP in listeVIP:
            message +=" • <@"+str(VIP)+">"
        message += "\n\n"
        
        
        message += ":medal: Le top viewers des Sparts Suprêmes ::medal:\n\n" 
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()
        cur.execute("SELECT pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total FROM 'Membre' WHERE total>=35 ORDER BY total DESC, pseudo ASC")
        rows = cur.fetchall()
        place = 1
        scoreTotal = 0
        for data in rows :
            (membre,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total) = data
            if scoreTotal > total :
                place += 1
            scoreTotal=total
            medaille = " "
            if place == 1:
                medaille = ":first_place:"
            elif place == 2:
                medaille = ":second_place:"
            elif place == 3:
                medaille = ":third_place:"
            message += medaille + "  n° "+str(place) +" - `"+membre+"`" + " : **"+ str(total)+" pts**\n"

        self.connexionSQL.close()
        await channel.send(message)  
        message = "\n\n"
        message += "Les <@&1037343347905409116> obtiennent la prérogative de pouvoir reserver des créneaux en avance par rapport aux autres Membres.\n" 
        await channel.send(message) 

    ####################################################
    ##         SESSION sessionMembre (Acces disk)     ##
    ####################################################
    def sessionMembre(self):
        _creneauHoraire = self.DetermineCreneau()
        _streamer = self.ObtenirStreamer(_creneauHoraire)
        print("\n"+datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ': session RaidZ🅾️ne  START')

        if (_streamer) :
            _listeMembresDejaPresent = self.ObtenirMembresDejaPresent(_creneauHoraire)
            self.ListeChatterEnLigne(_streamer.lower(), _creneauHoraire,_listeMembresDejaPresent)
        else :
            print("Absence de streamer dans streamer.txt > Pas de session Membres valide")
            
        print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ': session RaidZ🅾️ne  FIN\n')
        
    def ObtenirMembresDejaPresent(self,creneauHoraire):
        repertoire = os.path.join(GBOTPATH,"data",datetime.now().strftime("%Y-%m-%d"))
        fichier = creneauHoraire.replace(":","").replace(" ","")+"-chatters.txt"
        os.makedirs(repertoire, exist_ok=True) 
        name = os.path.join(repertoire,fichier)
        chatters =[]
        if os.path.exists(name):
            with open(name,"r") as fichierLocal :
                chatters =  fichierLocal.read().split("\n")
                del chatters[0]
                chatters =  [x.lower() for x in chatters]
        return chatters

    def SauvegardeCreneauHoraire (self,creneauHoraire,listeMembres):
        repertoire = os.path.join(GBOTPATH,"data",datetime.now().strftime("%Y-%m-%d"))
        os.makedirs(repertoire, exist_ok=True) 
        name = os.path.join(repertoire,(creneauHoraire.replace(":","").replace(" ","")+"-chatters.txt"))
        chatters =[]
        with open(name,"w") as fichierLocal :
            fichierLocal.write(creneauHoraire+'\n')
            for Membre in listeMembres:
                fichierLocal.write(Membre+'\n')
                
        name = os.path.join(GBOTPATH,"chatters.txt")
        chatters =[]
        with open(name,"w") as fichierLocal :
            fichierLocal.write(creneauHoraire+'\n')
            for Membre in listeMembres:
                fichierLocal.write(Membre+'\n')

    def ListeChatterEnLigne(self, streamer, creneauHoraire, listeMembreDejaPresent):
        '''
        Renvois la liste des Membres en lignes
        '''
        # Recupere la liste des Membres
        
        with open(os.path.join(GBOTPATH,"Membres.txt"),"r") as fichierLocal : 
            listeMembres =  fichierLocal.read().split("\n")
            listeMembres =  [x.lower() for x in listeMembres]

        # Recupere les chatters du STREAMER

        url = requests.get('https://tmi.twitch.tv/group/user/'+streamer.lower()+'/chatters')
        text = url.text  
        data = json.loads(text) 
        parseData = data['chatters']
        chatters = parseData["broadcaster"]+parseData["vips"]+parseData["moderators"]+parseData["staff"]+parseData["admins"]+parseData["global_mods"]+parseData["viewers"]
        chatters =  [x.lower() for x in chatters]

        # créé une liste pour trouver les Membres present sur le stream

        MembresEnLigne=[]
        MembresHoraire=[]
        
        if len(chatters)>0 :
            for Membre in listeMembreDejaPresent :      
                if (Membre not in chatters) and (Membre != ""):
                    MembresHoraire.append(Membre)
                if (Membre in chatters):
                    MembresEnLigne.append(Membre)
            for chatter in chatters:
                if (chatter in listeMembres) and (chatter not in listeMembreDejaPresent):
                    MembresEnLigne.append(chatter)

        print (GREEN ,"\n"+creneauHoraire , BLUE , streamer.upper())
        print (YELLOW + str(len(chatters)) + WHITE + " viewers(s) sur le stream.")
        print (RED + str(len(MembresEnLigne)) + WHITE + " Membre(s) sur le stream.")
        print (RED + str(len(MembresEnLigne)+len(MembresHoraire)) + WHITE + " Membre(s) au total sur le creneau.")
        
        listeMembresFinale=[]        
        listeMembresFinale.append(streamer) 
        
        print (WHITE,"\nMembre(s) deconnecté(s) durant le créneau : ",end="")
        for Membre in MembresHoraire:
            if Membre != 'vide' and Membre != streamer :
                print (YELLOW,Membre+" ",end="")
                listeMembresFinale.append(Membre)
        print("\n")
        
        for Membre in MembresEnLigne :
            if (Membre != streamer):
                listeMembresFinale.append(Membre)
                print (RED + "   > " + WHITE + Membre)

        #SAUVEGARDE CRENEAU
        self.SauvegardeCreneauHoraire(creneauHoraire,listeMembresFinale)

    def ObtenirStreamer(self, creneauHoraire):
        '''
        recupere le nom du streamer en fonction du creneau horaire dans le fichier planning.txt
        '''
        streamer=""
        try:        
            with open(os.path.join(GBOTPATH,"streamer.txt"),"r") as fichierLocal :
                streamer = fichierLocal.read()
        except IOError:
            streamer=""

        if (streamer=="" or streamer == "vide"):
            print ("\n"+ BRED + WHITE +"ERREUR :"+BBLACK+WHITE+" Impossible d'accéder au streaming du viewer. Veuillez vérifier si un streamer est bien présent sur ce créneau horaire dans le PLANNING. \nLe script continue de fonctionner..." )
            self.SauvegardeCreneauHoraire(creneauHoraire,["vide"])
        else :
            return streamer  

    ######################################
    ##         BASE DE DONNEE           ##
    ######################################
    def initTableSql(self):
        """        Initialise la base de donnée si elle n'existe pas
        """
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        curseur = self.connexionSQL.cursor()
        curseur.execute('''CREATE TABLE IF NOT EXISTS GBoT(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            planning TEXT,
            streamer TEXT,
            UNIQUE(planning)
            )''')
        curseur.execute('''CREATE TABLE IF NOT EXISTS Membre(
            id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            pseudo TEXT UNIQUE,
            lundi INTEGER,
            mardi INTEGER,
            mercredi INTEGER,
            jeudi INTEGER,
            vendredi INTEGER,
            samedi INTEGER,
            dimanche INTEGER,
            score INTEGER,
            total INTEGER
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
        curseur.execute('''INSERT OR REPLACE INTO Membre (pseudo,lundi,mardi,mercredi,jeudi,vendredi,samedi,dimanche,total) VALUES (?,?,?,?,?,?,?,?,?)''', ("none",0,0,0,0,0,0,0,0))
        curseur.execute('''CREATE TABLE IF NOT EXISTS HIScore(
            id INTEGER UNIQUE,
            date TEXT,
            pseudo TEXT,
            score INTEGER
            )''')
        curseur.execute('''INSERT OR IGNORE INTO HIScore (id,date,pseudo,score) VALUES (?,?,?,?)''', (1,"none","none",0))
        self.connexionSQL.commit()
        self.connexionSQL.close()

if __name__ == "__main__":

    GBoT = GBoT()

    ######################################
    ##        GESTION COMMANDE /        ##
    ######################################
    @GBoT.hybrid_command(name = "lurk", description = "Renvois la liste des Membres présents sur le creneau en cours.")
    @app_commands.guilds(GUILD)
    async def lurk(ctx:commands.Context):
        with open(os.path.join(GBOTPATH,"chatters.txt"),"r") as fichier :
            chatters = fichier.read()
        await ctx.defer(ephemeral=True)
        await ctx.send(chatters)

    @GBoT.hybrid_command(name = "planning", description = "renvois le planning de la journée.")
    @app_commands.guilds(GUILD)
    async def planning(ctx:commands.Context):
        # Commande !planning     
        with open(os.path.join(GBOTPATH,"planning.txt"),"r") as fichier :
            planning = fichier.read()
        await ctx.defer(ephemeral=True)
        await ctx.send("`"+planning+"`")

    @GBoT.hybrid_command(name = "streamer", description = "renvois le streamer actuel du créneau horaire.")
    @app_commands.guilds(GUILD)
    async def streamer(ctx:commands.Context):        
        # Commande !streamer
        with open(os.path.join(GBOTPATH,"streamer.txt"),"r") as fichier :
            streamer = fichier.read()
        if streamer != "vide" and streamer != "" :
            reponse = "**`"+streamer+"`** (raid > https://www.twitch.tv/"+streamer+" )"
        else:
            reponse = "**`"+streamer+"`**"
        #await ctx.defer(ephemeral=True)
        await ctx.send("Actuellement le nom du Streamer est : "+reponse)
        
    @GBoT.hybrid_command(name = "vip", description = "renvois la liste des VIPs.")
    @app_commands.guilds(GUILD)
    async def supreme(ctx:commands.Context):        
        # Commande !supreme
        await ctx.defer(ephemeral=True)
        await ctx.send(GBoT.recupereVIP())

    @GBoT.hybrid_command(name = "score", description = "Obtenir les scores des Membres pour la journée en cours.")
    @app_commands.guilds(GUILD)
    async def score(ctx:commands.Context): 
        # Commande !score
        await ctx.defer(ephemeral=True)
        await GBoT.commande_afficheScoreMembre(ctx)

    @GBoT.hybrid_command(name = "discord", description = "Obtenir le lien à diffuser pour rejoindre le discord Raid Z🅾️ne .")
    @app_commands.guilds(GUILD)
    async def discord(ctx:commands.Context):  
        # Commande !discord
        await ctx.send("Bonjour à toi streamer/streameuse,\
    tu débutes dans le stream et tu galères à avoir ton affiliation ou à te créer une communauté ? Ne t'en fais pas le serveur Discord __**\"Raid Z🅾️ne \"**__ est là pour te donner un coup de pouce.\n\
    \nLe principe est simple, il y a plusieurs horaires sous forme de créneaux disponibles du lundi au vendredi, il suffit simplement de t'inscrire à l'un d'entre eux pour recevoir un raid et voir ton nombre de viewers grimper en flèche et ton tchat se déchaîner.\n\
    \nÉvidemment, l'entraide est le mot d'ordre, alors on compte également sur toi pour faire parti(e) de la chaîne des raids et être présent(e) sur les streams des autres personnes qui adhèrent à ce projet.\n\
    \nAllez n'attend pas plus longtemps et deviens toi aussi un Membre en rejoignant ce serveur ici : https://discord.gg/2EzvqkuB9d )\n")

    @GBoT.hybrid_command(name = "raid", description = "tuto pour réaliser un raid.")
    @app_commands.guilds(GUILD)
    async def raid(ctx:commands.Context): 
        # Commande !raid
        await ctx.send("**PRO TIP :** Lancer un RAID\n\
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

    @GBoT.hybrid_command(name = "link", description = "lier son compte twitch a son compte discord.")
    @app_commands.guilds(GUILD)
    async def link(ctx:commands.Context):
        await ctx.send('**PRO TIP :** Lier Twitch et Discord\n\
        __**Via PC :**__\n\
            • Tu vas dans les paramètres de discord\n\
            • Tu vas dans "Connexion"\n\
            • Tu sélectionnes le logo "Twitch" et la liaison se fait.\n\
            • Vérifiez bien que le "Afficher sur mon profil" soit bien coché.\n\
        __**Via Téléphone :**__\n\
            • Tu vas dans les paramètres de discord\n\
            • Tu vas dans "Connexion"\n\
            • Tu cliques en haut à droite sur "Ajouter"\n\
            • Tu sélectionnes le logo "Twitch" et la liaison se fait.\n\
            • Vérifiez bien que le "Afficher sur mon profil" soit bien coché.\n')

    @GBoT.hybrid_command(name = "aide", description = "Afficher les commandes du GBoT.")
    @app_commands.guilds(GUILD)
    async def aide(ctx:commands.Context):
        await ctx.defer(ephemeral=True)
        await ctx.send("**Commande GBoT :**\n\
            • `/aide` : Les commandes du GBoT.\n\
            • `/link` : tuto pour lier son compte twitch et discord.\n\
            • `/lurk` : renvois la liste des Membres qui visualisent le stream en cours.\n\
            • `/planning` : renvois le planning de la journée.\n\
            • `/discord` : Obtenir le lien à diffuser pour rejoindre le discord Membres.\n\
            • `/raid` : tuto pour réaliser un raid.\n\
            • `/score` : Obtenir les scores des Membres pour la journée en cours.\n\
            • `/streamer` : renvois le streamer actuel du créneau horaire.\n\
            • `/VIP` : Obtenir la liste des VIP actuel.\n\
            ")
    
    @GBoT.hybrid_command(name = "hiscore", description = "Obtenir la date et le record de viewers du serveur pour un créneau.")
    @app_commands.guilds(GUILD)
    async def hiscore(ctx:commands.Context): 
        # Commande !score
        await ctx.defer(ephemeral=True)
        rows=GBoT.recupereHiScore()
        embed = Embed(title="Nouveau Record !!!",colour= Colour.dark_red())
        embed.set_author(name=f"serveur RaidZ🅾️ne",icon_url="https://www.su66.fr/raidzone/logo.png")
        embed.set_thumbnail(url=f"https://www.su66.fr/raidzone/guinness.png")
        embed.add_field(name=f"__Score :__",value=f" **{rows[3]}** viewers le {rows[1]} chez **{rows[2]}**.",  inline = False)
        embed.set_footer(text="Staff RaidZ🅾️ne",icon_url="https://www.su66.fr/raidzone/logo.png")
        await ctx.send(embed=embed)     
    
    @GBoT.hybrid_command(name = "avatar", description = "affiche mon avatar.")
    @app_commands.guilds(GUILD)
    async def avatar(ctx:commands.Context): 
        member = ctx.author
        name = member.display_name
        pfp = member.display_avatar
        embed = Embed(title="voici mon encart perso",colour= Colour.random())
        embed.set_author(name=f"{name}",icon_url=member.display_icon)
        embed.set_thumbnail(url=f"{pfp}")
        embed.set_footer(text = 'Généré par GBoT')
        await ctx.send(embed=embed)
            
    #######################################
    @GBoT.hybrid_command(name = "resa", description = "réserve un créneau.")
    @app_commands.guilds(GUILD)
    async def resa(ctx:commands.Context,jour:str): 
        await ctx.defer(ephemeral=True)
        jour=jour.lower()
        if GBoT.commande_resa_verifjour(jour) == 'False' :
            embed = Embed(title="ERREUR :",colour= Colour.red())
            embed.set_thumbnail(url="https://www.su66.fr/raidzone/error.png")
            embed.add_field(name="La syntaxe du __jour__ n est pas valable",value="Les seuls jours acceptables sont `lundi`, `mardi`, `mercredi`, `jeudi`, `vendredi`, `samedi` et `dimanche`.",  inline = False)
            embed.set_footer(text = 'Généré par GBoT')
            await ctx.send(embed=embed) 
        elif GBoT.commande_resa_droitMembreNonValide(ctx.author.display_name,jour) :
            embed = Embed(title="ERREUR :",colour= Colour.red())
            embed.set_thumbnail(url="https://www.su66.fr/raidzone/error.png")
            embed.add_field(name="Tes droits sont restreints",value="Tu n'as pas accés à cette journée de réservation car tu n'as pas cumulé assez de point pour reserver sur cette période.\n\
                            ▫️ **score >5** : accés réservation pour le lendemain.\n\
                            ▫️ **score >10** : accés réservation les 2 jours suivant.\n\
                            ▫️ **score >20** : accés réservation les 3 jours suivant.\n\
                            ▫️ **score >30** : accés réservation les 7 jours suivant.\n\
                            **1 pt** se gagne quand tu es chez un streamer du serveur durant son créneau. __Tu ne marques pas de point__ quand tu es le streamer.\n\
                            Pour connaitre ton score actuel, tape `/score` dans le channel <#1037341465099120672>.",  inline = False)
            embed.set_footer(text = 'Généré par GBoT')
            await ctx.send(embed=embed)         
        else:
            listeCreneaux = await GBoT.commande_resa_renvoisCreneau(jour)
            listeOption = []
            if len(listeCreneaux)==0:
                embed = Embed(title="ERREUR :",colour= Colour.red())
                embed.set_thumbnail(url="https://www.su66.fr/raidzone/error.png")
                embed.add_field(name="Absence de creneau",value=f"Il n y a pas de creneaux disponibles pour la journée de {jour}.",  inline = False)
                embed.set_footer(text = 'Généré par GBoT')
                await ctx.send(embed=embed)  
            else :
                for creneau in listeCreneaux :
                    listeOption.append(SelectOption(label=creneau,emoji="🔹"))
                select = Select(
                    min_values=1,
                    max_values=2,
                    placeholder=f"Choisissez vos creneaux pour {jour} :",
                    options=listeOption,
                )
                async def my_callback(interaction):
                    select.disabled = True
                    await interaction.response.edit_message(view=view)
                    await GBoT.commande_resa_valideCreneaux(ctx.author.id,jour,select.values)


                
            select.callback= my_callback   
            view = View()
            view.add_item(select)
            
            await ctx.send("Choisis une réponse :", view=view)

    @GBoT.hybrid_command(name = "scoregeneral", description = "commande ADMIN : Obtenir les scores des Membres pour la journée en cours.")
    @app_commands.guilds(GUILD)
    async def scoregeneral(ctx:commands.Context):
        # Commande !score
        if ctx.author.display_name == "GToF_" :
            reponse1, reponse2 = GBoT.recupereScoresMembres()
            await ctx.send('\n:medal: __**Score des Membres :**__ *( sur 7 jours )*\n')
            if reponse1 != "":
                await ctx.send(reponse1)
            if reponse2 != "":
                await ctx.send(reponse2)
            await ctx.send("\n*Chaque présence sur un creneau ajoute 1 pt. Le Cumul de point sur 7 jours vous permettra d'acceder au Grade de **VIP**\n\n")
        else:
            await ctx.defer(ephemeral=True)
            embed = Embed(title="ERREUR :",colour= Colour.red())
            embed.set_thumbnail(url="https://www.su66.fr/raidzone/error.png")
            embed.add_field(name="Commande non autorisée",value="Tu n'as pas accés a la commande `/scoregeneral`.\nTu peux consulter ton score actuel en utilisant la commande `/score`.",  inline = False)
            embed.set_footer(text = 'Généré par GBoT')
            await ctx.send(embed=embed) 
     

    GBoT.run(TOKEN)



    
