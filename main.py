import urllib.request
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO

root = Tk()
root.title("PTCGBuilder")
#root.geometry("758x800")

class Card:

	def __init__(self,name,set,number,image):
		self.name = name
		self.set = set
		self.number = number
		self.image = image

	def getPrettySet(self):
		return sets[self.set]

	def formatPretty(self):
		return self.name+", "+self.getPrettySet()+" #"+self.number

baseurl = "http://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/?cardName={name}&format=modified-legal"
isEX = "&ex-pokemon=on"
isMega = "&mega-ex=on"
isBreak = "&break=on"

sets = {"xy1": "XY",
		"xy2": "Flashfire",
		"xy3": "Furious Fists",
		"xy4": "Phantom Forces",
		"xy5": "Primal Clash",
		"xy6": "Roaring Skies",
		"xy7": "Ancient Origins",
		"xy8": "BREAKthrough",
		"xy9": "BREAKpoint",
		"xy10": "Fates Collide",
		"xy11": "Steam Siege",
		"xy12": "Evolutions",
		"xyp": "Promo",
		"g1": "Generations"}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]


def searchForCardsByName(n):
	global cardFrame
	cardFrame.destroy()
	cardFrame = Frame(root)
	cardFrame.pack(fill="both")
	n = n.strip()
	extra = ""
	if n[-6:].upper() == " BREAK":
		extra += isBreak
		n = n[:-6]
	elif n[:5].lower() == "mega ":
		extra += isMega
		n = n[5:]
	elif n[-3:].upper() == " EX":
		extra += isEX
		n = n[:-3]
	try:
		r = opener.open(baseurl.format(name=n)+extra).read().decode()
	except urllib.error.URLError:
		eFrame = Frame(cardFrame)
		eL = Label(eFrame,text="No Internet/Pokemon.com is blocked")
		eL.pack()
		eFrame.pack()
		return

	if '<div class="no-results' in r:
		eFrame = Frame(cardFrame)
		eL = Label(eFrame,text="No Pokemon found")
		eL.pack()
		eL2 = Label(eFrame,text="Check for spelling mistakes")
		eL2.pack()
		eFrame.pack()
		return
	r = r.split('<ul class="cards-grid clear" id="cardResults">')[1].split("</ul>")[0]
	u = r.split("<li>")[1:]

	# if len(u) > 6:

	searched = []
	for i, data in enumerate(u):
		page = data.split('<a href="')[1].split('">')[0].split("/")
		set = page[-3]
		num = page[-2]
		name = data.split('alt="')[1].split('">')[0].replace("-", " ")
		image = "http:" + data.split('<img src="')[1].split('"')[0]
		c = Card(name, set, num, image)
		buildCardDisplay(c).grid(row=i//6,column=i%6)
		#searched.append(Card(name, set, num, image))
	#for c in searched:print(c.formatPretty())




def buildCardDisplay(c):
	r = Frame(cardFrame)
	img = BytesIO(urllib.request.urlopen(c.image).read())
	i = Image.open(img)
	itk = ImageTk.PhotoImage(i)
	pic = Label(r, image=itk)
	pic.image = itk
	pic.pack()
	name = Label(r,text=c.formatPretty())
	name.pack()
	return r


searchFrame = Frame(root)
searchFrame.pack(fill="x")
searchEntry = Entry(searchFrame)
searchEntry.grid(row=0,column=0,sticky="ew")
searchEntry.focus_set()
searchButton = Button(searchFrame,text="Search Card",command=lambda searchEntry=searchEntry:searchForCardsByName(searchEntry.get()))
searchButton.grid(row=0,column=1)
root.bind("<Return>",lambda x,searchButton=searchButton:searchButton.invoke())

cardFrame = Frame(root)
cardFrame.pack(fill="both")




root.mainloop()