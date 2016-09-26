import urllib.request
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
import sys
import re
import time
import platform

import external

root = Tk()
root.title("PTCGBuilder")
#root.geometry("758x800")



class Card:

	ImageDimensions = (245,342)

	def __init__(self,name,set,number,imageURL,isEX=False,isBreak=False,isMega=False):
		self.name = name
		self.set = set
		self.number = number
		self.imageURL = imageURL
		self.isEX = isEX
		self.isBreak = isBreak
		self.isMega = isMega

	def getCardImage(self):
		img = BytesIO(urllib.request.urlopen(self.imageURL).read())
		i = Image.open(img)
		return i

	def getPrettySet(self):
		try:
			return sets[self.set]
		except KeyError:
			return self.set

	def formatPretty(self):
		return self.name+", "+self.getPrettySet()+" #"+self.number


class CardDisplay:

	def __init__(self,card,num):
		self.card = card
		i = card.getCardImage()
		if card.isBreak:
			i.thumbnail((245,245),Image.ANTIALIAS)
		itk = ImageTk.PhotoImage(i)
		self.root = Frame(cardFrame)
		pic = Label(self.root, image=itk)
		pic.image = itk
		pic.pack()
		name = Label(self.root, text=card.formatPretty())
		name.pack()
		self.num = num
	def display(self):
		self.root.grid(row=self.num // int(columnsEntry.get()), column=self.num % int(columnsEntry.get()))

baseurl = "http://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/{pagenum}?cardName={name}&format=modified-legal"
isEX = "&ex-pokemon=on"
isMega = "&mega-ex=on"
isBreak = "&break=on"

sets = {"xy0" : "Kalos Starter Set",
		"xy1" : "XY",
		"xy2" : "Flashfire",
		"xy3" : "Furious Fists",
		"xy4" : "Phantom Forces",
		"xy5" : "Primal Clash",
		"xy6" : "Roaring Skies",
		"xy7" : "Ancient Origins",
		"xy8" : "BREAKthrough",
		"xy9" : "BREAKpoint",
		"xy10": "Fates Collide",
		"xy11": "Steam Siege",
		"xy12": "Evolutions",
		"xyp" : "Promo",
		"g1"  : "Generations",
		"dc1" : "Double Crisis"}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]


def searchForCardsByName(n):
	global cardFrame
	root.title("PTCGBuilder - Searching")
	cardFrame.destroy()
	entryValidate(columnsEntry,"3")
	entryValidate(rowsEntry,"2")
	scrollbarProxy.configure(height=int(rowsEntry.get())*(Card.ImageDimensions[1]+30))
	scrollbarProxy.configure(width=int(columnsEntry.get())*(Card.ImageDimensions[0]+4))
	cardFrame = Frame(scrollbarProxy)
	cardFrame.pack(fill="both")
	n = n.strip()
	extra = ""
	if n[-6:].upper() == " BREAK" or n.upper() == "BREAK":
		extra += isBreak
		n = n[:-6]
	if n[:5].lower() == "mega " or n.lower() == "mega":
		extra += isMega
		n = n[5:]
	if n[-3:].upper() == " EX" or n.upper() == "EX":
		extra += isEX
		n = n[:-3]
	try:
		r = opener.open(baseurl.format(name=n,pagenum=1)+extra).read().decode()
	except urllib.error.URLError:
		eFrame = Frame(cardFrame)
		eL = Label(eFrame,text="No Internet/Pokemon.com is blocked")
		eL.pack()
		eFrame.pack()
		return

	if '<title>503' in r:
		eFrame = Frame(cardFrame)
		eL = Label(eFrame,text="503 Error")
		eL.pack()
		eL2 = Label(eFrame,text="Try again later maybe?")
		eL2.pack()
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
	#fl = open("lastPage.html","w")
	#fl.write(r)
	#fl.close()
	if '<div id="cards-load-more">' in r:
		pages = r.split('<div id="cards-load-more">')[1].split("</div>")[0]
		match = re.search('[0-9]+ of [0-9]+',pages)
		pages = int(pages[match.start():match.end()].split(" ")[-1])
	else:
		pages = 1
	r = r.split('<ul class="cards-grid clear" id="cardResults">')[1].split("</ul>")[0]
	rawCardList = r.split("<li>")[1:]
	found = []
	found.extend(parseCardPage(rawCardList))
	if pages > 1:
		if pages > 20:
			pages = 20
		for i in range(2,pages+1):
			retries = 10
			while True:
				try:
					r = opener.open(baseurl.format(name=n, pagenum=i) + extra).read().decode()
					if '<title>503' in r:
						retries -= 1
						if retries == 0:
							break
						time.sleep(10)
					else:
						r = r.split('<ul class="cards-grid clear" id="cardResults">')[1].split("</ul>")[0]
						rawCardList = r.split("<li>")[1:]
						found.extend(parseCardPage(rawCardList,i-1))
						break
				except urllib.error.URLError:
					retries -= 1
					if retries == 0:
						break
					time.sleep(10)
			if retries == 0:
				eFrame = Frame(cardFrame)
				eL = Label(eFrame, text="Error getting data for page "+str(i))
				eL.pack()
				eL2 = Label(eFrame, text="Try again later maybe?")
				eL2.pack()
				eFrame.pack()
				return

	#print(len(found))
	for card in found:
		card.display()
		#print(card.card.formatPretty())

	setUpCardFrame()
	root.title("PTCGBuilder")




def parseCardPage(rawCardList,pagenum=0):
	found = []
	for i, data in enumerate(rawCardList):
		page = data.split('<a href="')[1].split('">')[0].split("/")
		set = page[-3]
		num = page[-2]
		name = data.split('alt="')[1].split('">')[0].replace("-", " ")
		image = "http:" + data.split('<img src="')[1].split('"')[0]
		if name[-6:].upper() == " BREAK":
			c = Card(name, set, num, image,False,True)
		elif name[:2].upper() == "M ":
			c = Card(name, set, num, image,False,False,True)
		elif name[-3:].upper() == " EX":
			c = Card(name, set, num, image,True)
		else:
			c = Card(name, set, num, image)
		found.append(CardDisplay(c,i+(pagenum*12)))
	return found


def deleteOneWord(entry):
	contents = entry.get()
	try:
		index = contents.rindex(" ")
		entry.delete(index+1,END)
	except ValueError:
		entry.delete(0,END)

def entryValidate(entry,default):
	if len(entry.get()) > 3:
		entry.delete(3,END)
	try:
		int(entry.get())
	except ValueError:
		entry.delete(0,END)
		entry.insert(0, default)
		return True
	if int(entry.get()) <= 0:
		entry.delete(0, END)
		entry.insert(0,default)
	return True



searchFrame = Frame(root)
searchFrame.pack(fill="x")
searchEntry = Entry(searchFrame)
searchEntry.grid(row=0,column=0,sticky="ew")
searchEntry.focus_set()
searchButton = Button(searchFrame,text="Search Card",command=lambda searchEntry=searchEntry:searchForCardsByName(searchEntry.get()))
searchButton.grid(row=0,column=1)
root.bind("<Return>",lambda x,searchButton=searchButton:searchButton.invoke())
searchEntry.bind("<Control-BackSpace>", lambda x,searchEntry=searchEntry:deleteOneWord(searchEntry))
columnsLabel = Label(searchFrame,text="Columns: ")
columnsLabel.grid(row=0,column=2)
columnsEntry = Entry(searchFrame,width=3,validate="focus")
columnsEntry.configure(validatecommand=lambda x=columnsEntry:entryValidate(x,"3"))
columnsEntry.grid(row=0,column=3)
columnsEntry.insert(0,"3")
rowsLabel = Label(searchFrame,text="Rows: ")
rowsLabel.grid(row=0,column=4)
rowsEntry = Entry(searchFrame,width=3,validate="focus")
rowsEntry.configure(validatecommand=lambda x=rowsEntry:entryValidate(x,"2"))
rowsEntry.grid(row=0,column=5)
rowsEntry.insert(0,"2")


cardRoot = Frame(root)
cardRoot.pack(fill="both")
scrollbar = external.AutoScrollbar(cardRoot)
scrollbar.grid(row=0, column=1, sticky=N+S)
scrollbarProxy = Canvas(cardRoot, yscrollcommand=scrollbar.set)
scrollbarProxy.configure(height=int(rowsEntry.get())*(Card.ImageDimensions[1]+30))
scrollbarProxy.configure(width=int(columnsEntry.get())*(Card.ImageDimensions[0]+4))
scrollbarProxy.grid(row=0, column=0, sticky=N+S+E+W)
scrollbar.config(command=scrollbarProxy.yview)
cardRoot.grid_rowconfigure(0, weight=1)
cardRoot.grid_columnconfigure(0, weight=1)
cardFrame = Frame(scrollbarProxy)
cardFrame.pack(fill="both")

scrollbarProxy.create_window(0, 0, anchor=NW, window=cardFrame)
cardFrame.update_idletasks()
scrollbarProxy.config(scrollregion=scrollbarProxy.bbox("all"))

def setUpCardFrame():
	scrollbarProxy.create_window(0, 0, anchor=NW, window=cardFrame)
	cardFrame.update_idletasks()
	scrollbarProxy.config(scrollregion=scrollbarProxy.bbox("all"))


if platform.system() == "Windows":

	root.bind_all("<MouseWheel>", lambda e,canvas=scrollbarProxy:canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
elif platform.system() == "Darwin":#OSX
	##UNTESTED!!!
	root.bind_all("<MouseWheel>", lambda e, canvas=scrollbarProxy: canvas.yview_scroll(e.delta, "units"))
else:#Linux et al. X11 mainly
	##UNTESTED!!!
	root.bind_all("<Button-4>", lambda e, canvas=scrollbarProxy: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
	root.bind_all("<Button-5>", lambda e, canvas=scrollbarProxy: canvas.yview_scroll(int(e.delta / 120), "units"))


root.mainloop()