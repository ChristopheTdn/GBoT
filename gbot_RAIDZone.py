
import discord
from discord.ext import commands
from discord.utils import get
from discord import app_commands
from discord import Embed,Colour,SelectOption
from discord.ui import Select,View
import os
import logging
from datetime import datetime,timedelta
from session_RAIDZone import SessionRAIDZone

from colorama import Fore, Back
from dotenv import load_dotenv
import re 
import asyncio
import sqlite3

description = '''Le GBoT pour le serveur RAIDZone  .
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
    
PROD_GUILD = discord.Object(1037338719780339752)
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
        
    async def setup_hook(self) -> None:
        await self.tree.sync(guild=GUILD)
        # create the background task and run it in the background
        self.bg_task_EnregistreMembres = self.loop.create_task(self.EnchaineProcedure(60))
        self.bg_task_SessionMembres = self.loop.create_task(self.appelSessionMembres(240))

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

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def appelSessionMembres(self,timing_sessionMembres):
        await self.wait_until_ready()
        while not self.is_closed():
            print("\n"+datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ': session Membres START')
            SessionRAIDZone()
            print(datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ': session Membres FIN\n')
            await asyncio.sleep(timing_sessionMembres) 

    def enregistreMembres(self):
        with open(os.path.join(GBOTPATH,"Membres.txt"), "w") as fichier:
            for member in self.get_all_members():
                if not member.bot :
                        fichier.write(member.display_name.lower()+"\n")

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
        listeCreneauJour=["09h00 - 10h00 :",
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
        channelID = 0
        jour = (datetime.now().weekday()) # Renvoie le jour de la semaine sous forme d'entier, lundi étant à 0 et dimanche à 6.
        if (datetime.now().hour<1):
            jour-=1  
            if jour<0: jour=6
            
        if jour==0 : # Lundi
            channelID = 1037341064018796604
        elif jour==1 : # Mardi
            channelID = 1037341103747256361
        elif jour==2 : # Mercredi
            channelID = 1037341153466536037
        elif jour==3 : # Jeudi
            channelID = 1037341185569730561
        elif jour==4 : # Vendredi
            channelID = 1037341222341202020
        elif jour==5 : # Samedi
            channelID = 1037341259657920512

            
        return channelID

    def recupereIDChannelPresence(self):
        channelID = 1037347680965365791 #presence     
        return channelID

    async def recuperePlanning(self):
        _channelID = self.recupereIDChannelPlanning()
        if (_channelID != 0) :
            channel = self.get_channel(_channelID)
            messages = [messageAEffacer async for messageAEffacer in channel.history(limit=1,oldest_first=True)]
            message = messages[0].content
            ligneMessage = message.split("\n")
            
            self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite")) 
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
                sqlreq ="UPDATE GBoT SET streamer = '"+nom_streamer.lower()+"' WHERE planning = '"+ligneCut[0]+" "+ligneCut[1]+" "+ligneCut[2]+" "+ligneCut[3]+"'"
                curseur.execute(sqlreq)

            self.connexionSQL.commit()
            self.connexionSQL.close()            
        else:
            listeCreneau=["09h00 - 10h00 :",
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
                    "23h00 - 00h00 :",
                    "00h00 - 01h00 :"]
            self.connexionSQL =  sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
            curseur = self.connexionSQL.cursor()
            for creneau in listeCreneau:
                curseur.execute("UPDATE GBoT SET streamer = 'vide' WHERE planning = '"+creneau+"'")
            self.connexionSQL.commit()
            self.connexionSQL.close()
               
    async def envoisMessage(self):
        # minute 1    
        #Envois message horaire Streamer en ligne Membres  
        if datetime.now().minute == 1 : 
            with open(os.path.join(GBOTPATH,"streamer.txt"),"r") as fichier :
                streamer = fichier.read()

            idChannel = 1037340918937833543
            channel = self.get_channel(idChannel)
            messages = [messageAEffacer async for messageAEffacer in channel.history(limit=10)]
            for messageAEffacer in messages :
                await messageAEffacer.delete()

            if streamer != "" and streamer != "vide":
                reponse = "**`"+streamer+"`** (raid > https://www.twitch.tv/"+streamer+" )"
                await channel.send("Donnez de la force à "+reponse)
            else :
                reponse = "**`Il n y a pas de Raid Actuellement**"
                await channel.send(reponse)
                    
            # minute 58
            #Envois message horaire presence Membres
        if (datetime.now().hour< 1 or datetime.now().hour >=9) and datetime.now().minute == 59 :

            with open(os.path.join(GBOTPATH,"chatters.txt"),"r") as fichier:
                chatters = fichier.read()
                
                
            idChannel = self.recupereIDChannelPresence()                
            channel = self.get_channel(idChannel) 
                
            self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
            cur = self.connexionSQL.cursor()
            cur.execute("SELECT * FROM 'Membre'")
            rows = cur.fetchall()                
            chatters = chatters.split("\n") 
            reponse =  "**"+chatters[0]+"**\n"              
            del chatters[0]
            for chatter in chatters:
                if chatter !="" :
                    reponse += "`"+chatter+"`\n"
                    flagTrouve = False
                    for Membre in rows :
                        if Membre[1] == chatter :
                            score = Membre[2] + 1
                            if Membre[3] != None :
                                scoreTotal = Membre[3] + 1
                            else:
                                scoreTotal = score
                            flagTrouve = True
                            cur.execute("UPDATE Membre SET score = "+str(score)+", total = "+str(scoreTotal)+ " WHERE pseudo  = '"+chatter+"'")
                                
                        if flagTrouve == False :
                            if chatter != "vide" :
                                cur.execute('''INSERT OR REPLACE INTO Membre(pseudo, score,total) VALUES (?,?,?)''', (chatter,1,1))  

            await channel.send(reponse)
                
            self.connexionSQL.commit()
            self.connexionSQL.close() 

            if datetime.now().hour < 1: 
                # Affiche score
                idChannel = self.recupereIDChannelPresence()                
                await self.afficheScore(self.get_channel(idChannel))                
                # Remet les score de la journée a 0
                self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
                cur = self.connexionSQL.cursor()
                cur.execute("SELECT pseudo,score,total FROM 'Membre' WHERE score>0 ORDER BY total DESC, pseudo ASC")
                rows = cur.fetchall()
                for data in rows :
                    (Membre,score,total) = data
                    cur.execute("UPDATE Membre SET score = 0 WHERE pseudo  = '"+Membre+"'")        
                self.connexionSQL.commit()
                self.connexionSQL.close()
                        
            if datetime.now().hour < 1 and datetime.now().weekday()==6 : 
                await self.distributionRole(self.get_channel(1037341418722705468)) #annonce
    
    def recupereScore(self):
        # Recupere les scores pour les afficher une derniere fois
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()  
        cur.execute("SELECT pseudo,score,total FROM 'Membre' WHERE total>0 ORDER BY total DESC, score DESC, pseudo ASC")
        rows = cur.fetchall()
        self.connexionSQL.close()
        
        reponse = ""
        
        for data in rows :
            (Membre,score,scoreTotal) = data
            if scoreTotal == None :
                scoreTotal=score
            reponse += "• `"+Membre+"`" + " : **"+ str(score) +"** --> **"+ str(scoreTotal)+"**\n"

        if len(reponse)>1980 :
            messageTotal= reponse
            reponse1 = messageTotal[slice(0,1980)]
            reponse2 = messageTotal[slice(1980, len(messageTotal))]
        else :
            reponse1= reponse
            reponse2 = ""

        return (reponse1,reponse2)

    def resa_verifjour(self,jour):
        listeJour = ["lundi","mardi","mercredi","jeudi","vendredi","samedi"]
        if jour in listeJour :
            return jour
        else:
            return "False"
    
    async def recupereScoreMembres(self,ctx):
        # Recupere les scores pour les afficher une derniere fois
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()  
        cur.execute("SELECT pseudo,score,total FROM 'Membre' WHERE total>0 ORDER BY total DESC, score DESC, pseudo ASC")
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
        resultatMax=10
        for data in rows :
            (membre,score,total) = data
            if membre == auteur.display_name.lower()   :
                embed.add_field(name="votre score **"+ str(score)+"/"+str(total)+" pts**",value="\u200b",  inline = False)
        reponse = "\u200b"
        for data in rows :
            (membre,score,total) = data
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
    
    
    async def afficheScore(self,channel):
        
        reponse1,reponse2 = self.recupereScore()

        await channel.send('\n:medal: __**Score des Membres présent sur la journée :**__ *(Score journée --> Total de la semaine)*\n')
        await channel.send(reponse1)
        if reponse2 != "":
            await channel.send(reponse2)
        await channel.send("\n*Chaque présence sur un creneau ajoute 1 pt. Le Cumul de point sur la semaine vous permettra d'acceder au Grade de **VIP** pour la semaine suivante.*\n\n")

    def recupereVIP(self):
        users = self.get_all_members()
        listeRole= self.get_guild(1037338719780339752).roles
        listeVIP=[]
        message = "\n:medal: __**V.I.P**__\n"
        for membre in users:
                if get(listeRole, name="VIP") in membre.roles:
                    listeVIP.append(membre.display_name)
        for VIP in listeVIP:
            message +="> • `"+VIP+"`\n"
        return message
                    
    async def afficheVIP(self,channel):
        await channel.send(self.recupereVIP())
        
    async def on_message(self, message):

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

    async def distributionRole (self,channel):
        # Supprime le role des sparts supremes actuels et attribut en fonction du score 
        # channel = self.get_channel(979857092603162695) # channel annonce
        users = self.get_all_members()
        listeRole= self.get_guild(1037338719780339752).roles
        self.connexionSQL = sqlite3.connect(os.path.join(GBOTPATH,"RAIDZone.BDD.sqlite"))
        cur = self.connexionSQL.cursor()
        cur.execute("SELECT pseudo,score,total FROM 'Membre' WHERE total>=35 ORDER BY total DESC, pseudo ASC")
        rows = cur.fetchall()
        classementMembres ={}
        for data in rows :
            (membre,score,total) = data
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
        listeRole= self.get_guild(1037338719780339752).roles
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
        cur.execute("SELECT pseudo,score,total FROM 'Membre' WHERE total>=35 ORDER BY total DESC, pseudo ASC")
        rows = cur.fetchall()
        place = 1
        scoreTotal = 0
        for data in rows :
            (membre,score,total) = data
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
        message += "Les <@&951980979327762492> obtiennent la prérogative de pouvoir reserver des créneaux en avance par rapport aux autres Membres.\n" 
        await channel.send(message) 

    def initTableSql(self):
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
        curseur.execute('''INSERT OR REPLACE INTO Membre (pseudo, score,total) VALUES (?,?,?)''', ("none",0,0))
        self.connexionSQL.commit()
        self.connexionSQL.close()

if __name__ == "__main__":

    GBoT = GBoT()

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

    @GBoT.hybrid_command(name = "scoregeneral", description = "Obtenir les scores des Membres pour la journée en cours.")
    @app_commands.guilds(GUILD)
    async def scoregeneral(ctx:commands.Context):
        # Commande !score
        reponse1, reponse2 = GBoT.recupereScore()
        await ctx.send('\n:medal: __**Score des Membres présent sur la journée :**__ *(Score journée --> Total de la semaine)*\n')
        if reponse1 != "":
            await ctx.send(reponse1)
        if reponse2 != "":
            await ctx.send(reponse2)
        await ctx.send("\n*Chaque présence sur un creneau ajoute 1 pt. Le Cumul de point sur la semaine vous permettra d'acceder au Grade de **VIP** pour la semaine suivante.*\n\n")

    @GBoT.hybrid_command(name = "score", description = "Obtenir les scores des Membres pour la journée en cours.")
    @app_commands.guilds(GUILD)
    async def score(ctx:commands.Context): 
        # Commande !score
        await ctx.defer(ephemeral=True)
        await GBoT.recupereScoreMembres(ctx)

    @GBoT.hybrid_command(name = "discord", description = "Obtenir le lien à diffuser pour rejoindre le discord RAIDZone.")
    @app_commands.guilds(GUILD)
    async def discord(ctx:commands.Context):  
        # Commande !discord
        await ctx.send("Bonjour à toi jeune streamer/streameuse,\
    tu débutes dans le stream et tu galères à avoir ton affiliation ou à te créer une communauté ? Ne t'en fais pas le serveur Discord __**\"RAIDZone\"**__ est là pour te donner un coup de pouce.\n\
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
    @GBoT.hybrid_command(name = "resa", description = "reserve un creneau.")
    @app_commands.guilds(GUILD)
    async def resa(ctx:commands.Context,jour:str): 
        await ctx.defer(ephemeral=True)
        jour=jour.lower()
        listeJour = ["lundi","mardi","mercredi","jeudi","vendredi","samedi"]
        if GBoT.resa_verifjour(jour) == 'False' :
            embed = Embed(title="ERREUR :",colour= Colour.red())
            embed.set_thumbnail(url="https://www.su66.fr/raidzone/error.png")
            embed.add_field(name="La syntaxe du __jour__ n est pas valable",value="Les seuls jours acceptables sont `lundi`, `mardi`, `mercredi`, `jeudi`, `vendredi` et `samedi`.",  inline = False)
            embed.set_footer(text = 'Généré par GBoT')
            await ctx.send(embed=embed)
            
        else:
            
            listeCreneau=["09h00 - 10h00 :",
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
                        "23h00 - 00h00 :",
                        "00h00 - 01h00 :"]
            listeOption =[]
            for creneau in listeCreneau :
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
                await interaction.followup.send(f"prise en compte des creneaux : {select.values}")

                
            select.callback= my_callback   
            view = View()
            view.add_item(select)
            
            await ctx.send("Choisis une réponse :", view=view)

    GBoT.run(TOKEN)



    
