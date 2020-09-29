import discord, pycurl, re, wget, certifi, html
from io import BytesIO

buffer = BytesIO()
c = pycurl.Curl()
client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name="$r help"))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    commande = '$r '
    if message.content == "$r help":
    	helping = "Use \" $r \" followed with your search query to use RemyWiki's search engine directly on discord. \n **Example** : $r THE SAFARI"
    	await message.channel.send(helping)

    elif message.content.startswith(commande):
    	#On prépare la requête curl
    	msg = '' + message.content
    	argument = msg.replace(commande, '').replace("\"", "\'").replace('\'', '%27')
    	requete = "https://remywiki.com/api.php?action=query&list=search&srsearch=" + argument + "&format=json"
    	c.setopt(c.CAINFO, certifi.where())
    	c.setopt(c.URL, requete)
    	c.setopt(c.WRITEDATA, buffer)
    	c.perform()
    	json = buffer.getvalue().decode('utf-8')
    	buffer.truncate(0)
    	#On récupère les titres ainsi obtenus et on en garde pas plus de 9
    	titles = re.findall(r"\"title\":\".+?\"", json)
    	titles = [title.replace("\"" , "").replace("title:", "") for title in titles]
    	#On affiche une erreur si le résultat ne donne aucun résultat
    	if len(titles) == 0:
    		url_afficher = "No result found !"
    	else:
    		miniature =  "https://remywiki.com/wiki.png"
	    	links = re.findall(r"\"pageid\":.+?,", json)
	    	links = [link.replace("\"" , "").replace("pageid:", "").replace(",", "") for link in links]
	    	if titles[0].lower() == argument.lower() :
	    		titre_embed = titles[0]
	    		#Si le titre d'une page correspond à notre recherche, on la joint en url directement
	    		requete = "https://remywiki.com/?curid=" + links[0]
	    		c.setopt(c.URL, requete)
	    		c.setopt(c.WRITEDATA, buffer)
	    		c.perform()
	    		json = buffer.getvalue().decode('utf-8')
	    		url_afficher = requete.replace(" ", "%20")
	    		#S'il y a des images sur la page, on les affichera en miniature
	    		if len(re.findall(r"thumb tright.+?src.+?png.+?png" ,json)) !=0:
	    			image = re.sub(r"thumb tright.+?src=", "https://remywiki.com" ,re.findall(r"thumb tright.+?src.+?png.+?png" ,json)[0]).replace("\"", "")
	    		elif len(re.findall(r"thumb tright.+?src.+?jpg.+?jpg" ,json)) !=0:
	    			image = re.sub(r"thumb tright.+?src=", "https://remywiki.com" ,re.findall(r"thumb tright.+?src.+?jpg.+?jpg" ,json)[0]).replace("\"", "")
	    		else:
	    			image = "https://remywiki.com/wiki.png"
	    		#Si c'est une chanson qui a été trouvée, on prépare la prévisualisation en conséquence
	    		if len(re.findall(r"Song Information", json)) !=0 :
	    			if len(re.findall(r"Artist:.*<br", json)) != 0:
	    				artist = re.findall(r"Artist:.*<br", json)[0].replace("Artist:", "").replace("<br", "")
	    			else:
	    				artist = ""
	    			if len(re.findall(r"Composition\/Arrangement:.*<br", json)) != 0:
	    				compo =  re.sub("<a.*?>", "", re.findall(r"Composition\/Arrangement:.*<br", json)[0]).replace("Composition/Arrangement:", "").replace("</a><br", "")
	    			else:
	    				compo = ""
	    			if len(re.findall(r"BPM:.*<br", json)) != 0:
	    				bpm = 	re.findall(r"BPM:.*<br", json)[0].replace("BPM:", "").replace("<br", "")
	    			else:
	    				bpm = ""
	    			if len(re.findall(r"Length:.*<br", json)) != 0:
	    				length = 	re.findall(r"Length:.*<br", json)[0].replace("Length:", "").replace("<br", "")
	    			else:
	    				length = ""
	    			if len(re.findall(r"Genre:.*<br", json)) != 0:
	    				genre = re.findall(r"Genre:.*<br", json)[0].replace("Genre:", "").replace("<br", "")
	    			else:
	    				genre = "" 
	    			description = "**Artis**t : " + artist + "\n" + "**Composition/Arrangemen**t : " +  compo + "\n" + "**BPM** : " + bpm + "\n" + "**Length** : " + length + "\n" + "**Genre** : " + genre
	    			#Idem mais version artiste
	    		elif len(re.findall(r"Artist Information", json)) !=0 :
	    			if len(re.findall(r"Name:.*</li", json)) != 0:
	    				artist = name = re.findall(r"Name:.*</li", json)[0].replace("Name:", "").replace("</li", "")
	    			else:
	    				artist = name = ""
	    			if len(re.findall(r"Birthdate:.*</li", json)) != 0:
	    				birthdate =  re.findall(r"Birthdate:.*</li", json)[0].replace("Birthdate:", "").replace("</li", "")
	    			else:
	    				birthdate = ""
	    			if len(re.findall(r"<p>.+?\.", json)) != 0:
	    				desc = re.sub("<..*?>", "", re.findall(r"<.>.+?\.", json)[0]).replace("</a>", "").replace("<p>", "")
	    				if len(desc) > 325:
	    					desc = desc[0:321] + "..." 
	    			else:
	    				desc = ""
	    			description = "**Name** : " + name + "\n" + "**Birthdate** : " +  birthdate + "\n" + "**Profile** : " +  desc
	    			#On ajoute les informations à l'embed
	    		embed = discord.Embed(title=titre_embed, description=description.replace("#8594;", "→"),colour=discord.Colour.blue())
	    		embed.set_image(url=image)
	    		embed.set_thumbnail(url=miniature)
	    		embed.set_author(name=artist)
	    		embed.add_field(name="Link", value="[" + url_afficher +"]" + "(" + url_afficher + ")", inline=False)
	    		await message.channel.send(embed=embed)
	    	else:
	    		#Si nous sommes sur la page de recherche
	    		i = 0
	    		description = ""
	    		if len(links) > 9:
	    			boucle = 9
	    		else:
	    			boucle = len(links)
	    		while (i < boucle) :
	    			description = description + str(i+1) + ". " + "[" + titles[i] +"]" + "(" + "https://remywiki.com/?curid=" + links[i] + ")" + "\n"
	    			i = i + 1;
	    		if len(links) > 9:
	    			description = description + "..."
	    		#Embed pour la page de recherche
	    		embed = discord.Embed(title="Search Results", description=description.replace("&#8594;", "→"),colour=discord.Colour.blue())
	    		image = "https://remywiki.com/wiki.png"
	    		embed.set_thumbnail(url=miniature)
	    		url_afficher = "https://remywiki.com/index.php?search=" + argument.replace(" ", "%20")
	    		embed.add_field(name="Search Page", value="[" + url_afficher +"]" + "(" + url_afficher + ")", inline=False)
	    		await message.channel.send(embed=embed)

client.run('TOKEN')
