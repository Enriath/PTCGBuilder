import urllib.request
from tkinter import *
from PIL import Image, ImageTk
from io import BytesIO
import re
import time
import platform

import external

class CardSelector:

	#The base search URL, with .format() substitution strings in the right places.
	baseurl = "http://www.pokemon.com/uk/pokemon-tcg/pokemon-cards/{pagenum}?cardName={name}&format=modified-legal"
	#Add these on to the base URL to search for EX, Mega, and BREAK Pokemon
	isEX = "&ex-pokemon=on"
	isMega = "&mega-ex=on"
	isBreak = "&break=on"

	def __init__(self):
		self.title = "PTCGBuilder Card Search"
		self.rowAndColEntryValidate = (root.register(self.rowAndColEntryValidate),"%d","%i","%s","%S")#Tkinter Wizardry!

	def build(self):
		"""
		Actually creates and shows the Card Selector window.
		This means one instance can be re-used by the Deck Builder

		Args: Nothing

		Returns: Nothing
		"""
		self.root = Toplevel()
		self.root.title(self.title)
		self.root.protocol("WM_DELETE_WINDOW", self.root.destroy)

		self.opener = urllib.request.build_opener()
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]

		searchFrame = Frame(self.root)
		searchFrame.pack(fill="x")
		searchEntry = Entry(searchFrame)
		searchEntry.grid(row=0, column=0, sticky="ew")
		searchEntry.focus_set()
		searchButton = Button(searchFrame, text="Search Card",
							  command=lambda searchEntry=searchEntry: self.searchForCardsByName(searchEntry.get()))
		searchButton.grid(row=0, column=1)
		self.root.bind("<Return>", lambda x, searchButton=searchButton: searchButton.invoke())
		searchEntry.bind("<Control-BackSpace>", lambda x, searchEntry=searchEntry: self.deleteOneWord(searchEntry))
		columnsLabel = Label(searchFrame, text="Columns: ")
		columnsLabel.grid(row=0, column=2)
		self.columnsEntry = Entry(searchFrame, width=3, validate="key")
		self.columnsEntry.configure(validatecommand=self.rowAndColEntryValidate)
		self.columnsEntry.grid(row=0, column=3)
		self.columnsEntry.insert(0, "3")
		rowsLabel = Label(searchFrame, text="Rows: ")
		rowsLabel.grid(row=0, column=4)
		self.rowsEntry = Entry(searchFrame, width=3, validate="key")
		self.rowsEntry.configure(validatecommand=self.rowAndColEntryValidate)
		self.rowsEntry.grid(row=0, column=5)
		self.rowsEntry.insert(0, "2")

		self.cardRoot = Frame(self.root)
		self.cardRoot.pack(fill="both")
		scrollbar = external.AutoScrollbar(self.cardRoot)
		scrollbar.grid(row=0, column=1, sticky=N + S)
		self.scrollbarProxy = Canvas(self.cardRoot, yscrollcommand=scrollbar.set)
		self.scrollbarProxy.configure(height=int(self.rowsEntry.get()) * (Card.ImageDimensions[1] + 30))
		self.scrollbarProxy.configure(width=int(self.columnsEntry.get()) * (Card.ImageDimensions[0] + 4))
		self.scrollbarProxy.grid(row=0, column=0, sticky=N + S + E + W)
		scrollbar.config(command=self.scrollbarProxy.yview)
		self.cardRoot.grid_rowconfigure(0, weight=1)
		self.cardRoot.grid_columnconfigure(0, weight=1)
		self.cardFrame = Frame(self.scrollbarProxy)
		self.cardFrame.pack(fill="both")

		self.scrollbarProxy.create_window(0, 0, anchor=NW, window=self.cardFrame)
		self.cardFrame.update_idletasks()
		self.scrollbarProxy.config(scrollregion=self.scrollbarProxy.bbox("all"))

		if platform.system() == "Windows":
			self.root.bind_all("<MouseWheel>", lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
		elif platform.system() == "Darwin":  # OSX
			##UNTESTED!!!
			self.root.bind_all("<MouseWheel>", lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(e.delta, "units"))
		else:  # Linux et al. X11 mainly
			##UNTESTED!!!
			self.root.bind_all("<Button-4>", lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
			self.root.bind_all("<Button-5>", lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(int(e.delta / 120), "units"))

	def searchForCardsByName(self,n):
		"""
		Searches for a card by a given name, including EX, BREAK, and Mega pokemon.
		Function also displays the Cards in the Card Frame

		Args:
		n (String): Part of or whole name of a Card.

		Returns:Nothing
		"""
		self.root.title(self.title+" - Searching")
		self.cardFrame.destroy()
		self.scrollbarProxy.configure(height=int(self.rowsEntry.get()) * (Card.ImageDimensions[1] + 30))
		self.scrollbarProxy.configure(width=int(self.columnsEntry.get()) * (Card.ImageDimensions[0] + 4))
		self.cardFrame = Frame(self.scrollbarProxy)
		self.cardFrame.pack(fill="both")
		n = n.strip()
		extra = ""
		if n[-6:].upper() == " BREAK" or n.upper() == "BREAK":
			extra += CardSelector.isBreak
			n = n[:-6]
		if n[:5].lower() == "mega " or n.lower() == "mega":
			extra += CardSelector.isMega
			n = n[5:]
		if n[-3:].upper() == " EX" or n.upper() == "EX":
			extra += CardSelector.isEX
			n = n[:-3]
		try:
			r = self.opener.open(CardSelector.baseurl.format(name=n, pagenum=1) + extra).read().decode()
		except urllib.error.URLError:
			eFrame = Frame(self.cardFrame)
			eL = Label(eFrame, text="No Internet/Pokemon.com is blocked")
			eL.pack()
			eFrame.pack()
			self.root.title(self.title)
			return

		if '<title>503' in r:
			eFrame = Frame(self.cardFrame)
			eL = Label(eFrame, text="503 Error")
			eL.pack()
			eL2 = Label(eFrame, text="Try again later maybe?")
			eL2.pack()
			eFrame.pack()
			self.root.title(self.title)
			return
		if '<div class="no-results' in r:
			eFrame = Frame(self.cardFrame)
			eL = Label(eFrame, text="No Pokemon found")
			eL.pack()
			eL2 = Label(eFrame, text="Check for spelling mistakes")
			eL2.pack()
			eFrame.pack()
			self.root.title(self.title)
			return

		if '<div id="cards-load-more">' in r:
			pages = r.split('<div id="cards-load-more">')[1].split("</div>")[0]
			match = re.search('[0-9]+ of [0-9]+', pages)
			pages = int(pages[match.start():match.end()].split(" ")[-1])
		else:
			pages = 1
		r = r.split('<ul class="cards-grid clear" id="cardResults">')[1].split("</ul>")[0]
		rawCardList = r.split("<li>")[1:]
		found = []
		found.extend(self.parseCardPage(rawCardList))
		if pages > 1:
			if pages > 20:
				pages = 20
			for i in range(2, pages + 1):
				retries = 10
				while True:
					try:
						r = self.opener.open(CardSelector.baseurl.format(name=n, pagenum=i) + extra).read().decode()
						if '<title>503' in r:
							retries -= 1
							if retries == 0:
								break
							time.sleep(10)
						else:
							r = r.split('<ul class="cards-grid clear" id="cardResults">')[1].split("</ul>")[0]
							rawCardList = r.split("<li>")[1:]
							found.extend(self.parseCardPage(rawCardList, i - 1))
							break
					except urllib.error.URLError:
						retries -= 1
						if retries == 0:
							break
						time.sleep(10)
				if retries == 0:
					eFrame = Frame(self.cardFrame)
					eL = Label(eFrame, text="Error getting data for page " + str(i))
					eL.pack()
					eL2 = Label(eFrame, text="Try again later maybe?")
					eL2.pack()
					eFrame.pack()
					self.root.title(self.title)
					return

		for card in found:
			card.display()

		self.setUpCardFrame()
		self.root.title(self.title)

	def parseCardPage(self, rawCardList, pagenum=0):
		"""
		Parses a page's worth of cards, getting the data needed for a Card object.

		Args:
		rawCardList (String[])		: A list of strings, each containing the HTML that displays the card.
		pagenum 	(int, default=0): The current page number, minus 1 to ake maths easier. This is used in CardDislay.

		Returns: CardDisplay[]
		A list of all the display objects for each card on this page.
		"""
		found = []
		for i, data in enumerate(rawCardList):
			page = data.split('<a href="')[1].split('">')[0].split("/")
			set = page[-3]
			num = page[-2]
			name = data.split('alt="')[1].split('">')[0].replace("-", " ")
			image = "http:" + data.split('<img src="')[1].split('"')[0]
			if name[-6:].upper() == " BREAK":
				c = Card(name, set, num, image, "Pokemon", False, True)
			elif name[:2].upper() == "M ":
				c = Card(name, set, num, image, "Pokemon", True, False, True)
			elif name[-3:].upper() == " EX":
				c = Card(name, set, num, image, "Pokemon", True)
			else:
				c = Card(name, set, num, image, "Pokemon")
			found.append(CardDisplay(self, c,i + (pagenum * 12)))
		return found

	@staticmethod
	def deleteOneWord(entry):
		"""
		Deletes a single word from an entry box. Used for Ctrl+Backspace binds.

		Args:
		entry (tkinter.Entry): The Entry widget to delete a word from.

		Returns: Nothing
		"""
		contents = entry.get()
		try:
			index = contents.rindex(" ")
			entry.delete(index + 1, END)
		except ValueError:
			entry.delete(0, END)

	def setUpCardFrame(self):
		"""
		Forces the Scrollbar Proxy Canvas to render the new Card Frame, plus forces the required updates.
		May not be necessary, but it's good to be sure.

		Args: Nothing

		Returns: Nothing
		"""
		self.scrollbarProxy.create_window(0, 0, anchor=NW, window=self.cardFrame)
		self.cardFrame.update_idletasks()
		self.scrollbarProxy.config(scrollregion=self.scrollbarProxy.bbox("all"))

	def getProvidedCardGridWidth(self):
		"""
		Allows CardDisplay.display() to get the columns to display. This is crucial.

		Args: None

		Returns: int
		The columns to display
		"""
		return int(self.columnsEntry.get())


	@staticmethod
	def rowAndColEntryValidate(d, i, s, S):
		"""
		Called every time a key is pressed when the row and column entry boxes are focused
		Uses Tkinter wizardry to get the parameters.
		Big thanks to Bryan Oakley for this answer: http://stackoverflow.com/a/4140988

		Args:
		d (String): Type of action (1=insert, 0=delete, -1 for others)
		i (String): Index of char string to be inserted/deleted, or -1
		s (String): Value of entry prior to editing
		S (String): The text string being inserted or deleted, if any

		Returns: Boolean
		True if the change passes validation, False if not
		"""
		#Clamp the length to 3 characters
		if len(s) >= 3 and d == "1":
			return False
		v = ord(S)
		#Clamp the value between 0 and 9
		if v < 48 or v > 57:
			return False
		#Don't allow the last character to be deleted
		if len(s) == 1 and d == "0":
			return False
		#Don't allow a lone 0 to be input
		if v == 48 and s == " ":
			return False
		#Don't allow a lone 0 to be left
		if d == "1":
			value = s+S
		else:
			value = s
		if int(i)+1 == len(value):
			result = int(value)
		else:
			result = int(value[int(i)+1:])
		if result == 0:
			return False
		#Otherwise, it's fine
		return True


class Card:

	#Default Card image dimensions
	#Used to set up the Scrollbar Proxy Canvas
	ImageDimensions = (245,342)

	#The Pretty Set Names
	sets = {"xy0":	"Kalos Starter Set",
			"xy1":	"XY",
			"xy2":	"Flashfire",
			"xy3":	"Furious Fists",
			"xy4":	"Phantom Forces",
			"xy5":	"Primal Clash",
			"xy6":	"Roaring Skies",
			"xy7":	"Ancient Origins",
			"xy8":	"BREAKthrough",
			"xy9":	"BREAKpoint",
			"xy10":	"Fates Collide",
			"xy11":	"Steam Siege",
			"xy12":	"Evolutions",
			"xyp":	"Promo",
			"g1":	"Generations",
			"dc1":	"Double Crisis"}

	def __init__(self,name,set,number,imageURL,cardType,isEX=False,isBreak=False,isMega=False):
		"""
		Builds a Card object

		Args:
		name 		(String)				: The name of the card
		set 		(String)				: The set code, see Card.sets
		number 		(String)				: The number. Must be a string to support special sets, like Radiant Collections (RC##)
		imageURL 	(String)				: The image URL
		cardType	(String)				: What type the card is (Pokemon, Item, Tool, Supporter, Stadium, Special Energy, Energy)
		isEX 		(Boolean, default=False): Is the card an EX?
		isBreak 	(Boolean, default=False): Is the card a BREAK Evolution? Used for rendering the card.
		isMega 		(Boolean, default=False): Is the card a Mega Evolution?

		Returns: Nothing
		"""
		self.name = name
		self.set = set
		self.number = number
		self.imageURL = imageURL
		self.type = cardType
		self.isEX = isEX
		self.isBreak = isBreak
		self.isMega = isMega
		self.image = None
		self.cacheImage()

	def getCardImage(self):
		"""
		Fetches the card image

		Args: Nothing

		Returns: PIL.Image
		The image at the card's stored imageURL, downloaded straight to RAM. Should be PNG.
		"""
		img = BytesIO(urllib.request.urlopen(self.imageURL).read())
		i = Image.open(img)
		return i

	def cacheImage(self):
		"""
		Cache's the image. Used so the deck can have a pretty display on the side

		Args: Nothing

		Returns: Nothing
		"""
		i = self.getCardImage()
		if self.isBreak:
			i.thumbnail((245, 245), Image.ANTIALIAS)
		self.image = i

	def getPrettySet(self):
		"""
		Takes the raw, ugly set code, and uses Card.sets to get the pretty set name
		If the code doesn't exist, return the raw ugly set code

		Args: Nothing

		Returns: String
		Either the pretty set name or the ugly set code.
		"""
		try:
			return Card.sets[self.set]
		except KeyError:
			return self.set

	def getPrettySetAndCardNum(self):
		"""
		Returns the pretty set and the card number, for use in the deck builder

		Args: Nothing

		Returns: String
		"""
		return self.getPrettySet()+" #"+self.number

	def formatPretty(self):
		"""
		Makes a descriptive string of all the card details. Used in CardDisplay.display()

		Args: Nothing

		Returns: String
		"""
		return self.name+", "+self.getPrettySetAndCardNum()


class CardDisplay:

	def __init__(self,parent,card,num):
		"""
		Builds a display widget from a card object and a locating number

		Args:
		parent 	(CardSelector)	: Required to access the desired column ammount in display()
		card 	(Card)			: The Card object to use as data
		num 	(int)			: The locating number, used to correctly place the card in the grid.

		Returns: Nothing
		"""
		self.card = card
		self.parent = parent
		itk = ImageTk.PhotoImage(card.image)
		self.root = Frame(self.parent.cardFrame)
		pic = Label(self.root, image=itk)
		pic.image = itk
		pic.pack()
		name = Label(self.root, text=card.formatPretty())
		name.pack()
		self.num = num

		pic.bind("<Double-Button-1>",lambda e,c=self.card: requestCardCount(c))
		name.bind("<Double-Button-1>", lambda e, c=self.card: requestCardCount(c))

	def display(self):
		"""
		Actually draws the widget. This makes all the cards appear at once.

		Args: Nothing

		Returns: Nothing
		"""
		self.root.grid(row=self.num // self.parent.getProvidedCardGridWidth(), column=self.num % self.parent.getProvidedCardGridWidth())


##BASIC TEST CODE

from tkinter.ttk import Treeview
from collections import OrderedDict


def requestDeleteCardFromDeck(deck):
	"""
	A dialogue to ask if the user is sure they want to delete a card/s
	Also displays an error if the user selects nothing and hits delete

	Args:
	deck (tkinter.ttk.Treeview): The deck Treeview. So I don't have to work with globals, and can use multiple decks

	Returns: Nothing
	"""
	root = Toplevel()
	sel = deck.selection()
	print(repr(sel))
	l = Label(root)
	b1 = Button(root,height=2)
	if sel == "":
		l.configure(text="Please select a card first.")
		b1.configure(text="Ok",width=4,command=root.destroy)
		l.pack()
		b1.pack(fill="x")
	else:
		sel = sel[0]
		try:
			card = deckItems[sel]
			l.configure(text="Are you sure you want to delete {card}?".format(card=card.formatPretty()))
			b1.configure(text="Yes",command=lambda:deleteCardFromDeckById(root,sel))
			Button(root,text="No",height=2,command=root.destroy).grid(row=1,column=1,sticky="ew")
			l.grid(row=0,column=0,columnspan=2)
			b1.grid(row=1,column=0,sticky="ew")
		except KeyError:
			print(roots)
			l.configure(text="Are you sure you want to delete all {section} cards?".format(section=roots.get(sel)))
			b1.configure(text="Yes", command=lambda: deleteAllCardsFromSection(root, sel))
			Button(root,text="No",height=2, command=root.destroy).grid(row=1, column=1,sticky="ew")
			l.grid(row=0, column=0, columnspan=2)
			b1.grid(row=1, column=0,sticky="ew")


root = Tk()
root.title("PTCGBuilder")

cardSelector = CardSelector()

deckRoot = Frame(root)
deckRoot.pack()

toolbarRoot = Frame(deckRoot)
toolbarRoot.pack(fill="x")

addCardB = Button(toolbarRoot,text="Add Card",width=10,height=2,command = lambda c=cardSelector:c.build())
addCardB.pack(anchor="w",side=LEFT)

Label(toolbarRoot,text="  # of Cards:").pack(anchor="w",side=LEFT)

totalCards = IntVar()
totalCards.set(0)

Label(toolbarRoot,textvariable=totalCards).pack(anchor="w",side=LEFT,padx=20)

remCardB = Button(toolbarRoot,text="Remove Card",width=10,height=2)
remCardB.pack(anchor="w",side=LEFT)

headers = OrderedDict()
headers["name"]		= "Name"
headers["count"]	= "Count"
headers["setnum"]	= "Set/Number"

deck = Treeview(deckRoot,height=25,columns=tuple(headers.keys()),show="tree headings")
remCardB.configure(command = lambda d=deck: requestDeleteCardFromDeck(d))
for k,v in headers.items():
	deck.heading(k,text=v)

deck.column("#0",width=90)
deck.heading("#0",text="Type")

roots = external.TwoWay()

roots.add("Pokemon", deck.insert("",END,text="Pokemon",open=True,values=["",0]))
roots.add("Items", deck.insert("",END,text="Items",open=True,values=["",0]))
roots.add("Tools", deck.insert("",END,text="Tools",open=True,values=["",0]))
roots.add("Supporter", deck.insert("",END,text="Supporters",open=True,values=["",0]))
roots.add("Stadium", deck.insert("",END,text="Stadiums",open=True,values=["",0]))
roots.add("Energy", deck.insert("",END,text="Energy",open=True,values=["",0]))

deckItems = {}

def cardCountEntryValidate(d, s, S):
	"""
	Called every time a key is pressed when the Card Count Dialogue box is open
	Allows for values between 1 and 4 to be in the Entry at any one time.

	Uses Tkinter wizardry to get the parameters.
	Big thanks to Bryan Oakley for this answer: http://stackoverflow.com/a/4140988

	Args:
	d (String): Type of action (1=insert, 0=delete, -1 for others)
	s (String): Value of entry prior to editing
	S (String): The text string being inserted or deleted, if any

	Returns: Boolean
	True if the change passes validation, False if not
	"""
	#Clamp the length to 1 character
	if len(s) >= 1 and d == "1":
		return False
	v = ord(S)
	#Clamp the input between 1 and 4
	if v < 49 or v > 52:
		return False
	return True

def cardCountEntryValidateIfEnergy(d, s, S):
	"""
	Called every time a key is pressed when the Card Count Dialogue box is open
	Allows for values between 0 and 99 to be in the Entry at any one time.

	Uses Tkinter wizardry to get the parameters.
	Big thanks to Bryan Oakley for this answer: http://stackoverflow.com/a/4140988

	Args:
	d (String): Type of action (1=insert, 0=delete, -1 for others)
	s (String): Value of entry prior to editing
	S (String): The text string being inserted or deleted, if any

	Returns: Boolean
	True if the change passes validation, False if not
	"""
	#Clamp the length to 2 characters
	if len(s) >= 2 and d == "1":
		return False
	v = ord(S)
	#Clamp the input between 0 and 9
	if v < 48 or v > 57:
		return False
	return True

#More Tkinter Wizardry!
cardCountEntryValidate = (root.register(cardCountEntryValidate), '%d', '%s', '%S')
cardCountEntryValidateIfEnergy = (root.register(cardCountEntryValidateIfEnergy), '%d', '%s', '%S')

def requestCardCount(card):
	"""
	Builds and displays a dialogue asking for the number of cards. Is called when a card is added,
	but can also be called by double clicking a card in the Treeview

	Args:
	card (Card): The Card object containing the selected card's information.

	Returns: Nothing
	"""
	global cardCountEntry
	root = Toplevel()
	Label(root,text="How many of {card} do you want?".format(card=card.name)).pack()
	cardCountEntry = Entry(root,width=2,validate="key")
	if card.type == "Energy":
		cardCountEntry.configure(validatecommand=cardCountEntryValidateIfEnergy)
	else:
		cardCountEntry.configure(validatecommand=cardCountEntryValidate)
	cardCountEntry.focus_set()
	cardCountEntry.pack(fill="x")
	b = Button(root,text="Submit")
	b.configure(command = lambda e=cardCountEntry,top=root: addCardToDeck(top,card,e.get()))
	b.pack(fill="x")


def addCardToDeck(top,card,count):
	"""
	Adds a card to the deck. Also updates the counters.

	Args:
	top		(tkinter.Toplevel)	: The Toplevel of the Card Count dialogue, so it can be destroyed
	card	(Card)				: The Card object containing all of the card's information
	count	(String)			: The amount of said card to add to the deck. If empty, will stop the function instantly

	Returns: Nothing
	"""
	global deckItems
	if count != "":
		top.destroy()
		cardSelector.root.destroy()
		#card = Card("Pikachu","g1","RC29","example.com")
		id = deck.insert(roots.get(card.type),END,values=[card.name,count,card.getPrettySetAndCardNum()])
		deckItems[id] = card
		updateCardCounters(roots.get(card.type))

def deleteCardFromDeckById(top,id):
	"""
	Deletes a card, then updates the counters

	Args:
	top	(tkinter.Toplevel)	: The Toplevel from the confirmation dialogue, so it can be destroyed
	id	(String)			: The ID of the Treeview item to be destroyed

	Returns: Nothing
	"""
	top.destroy()
	parent = deck.parent(id)
	deck.delete(id)
	updateCardCounters(parent)

def deleteAllCardsFromSection(top,id):
	"""
	Deletes all the cards in an entire section, then updates the counters

	Args:
	top	(tkinter.Toplevel)	: The Toplevel from the confirmation dialogue, so it can be destroyed
	id	(String)			: The ID of a root Treeview item to be destroyed

	Returns: Nothing
	"""
	top.destroy()
	items = deck.get_children(id)
	for i in items:
		deck.delete(i)
	updateCardCounters(id)

def updateCardCounters(root):
	"""
	Updates the total card counter and section card counters

	Args:
	root (String): Either a Treeview ID or all. If an ID is provided, only that section will be updated.

	Returns: Nothing
	"""
	if root.lower() == "all":
		total = 0
		for k,v in roots.normal.items():
			rootTotal = 0
			items = deck.get_children(v)
			for i in items:
				c = int(deck.item(i,"values")[1])
				total += c
				rootTotal += c
			deck.item(v,values=["",rootTotal])
		totalCards.set(total)
	else:
		current = int(deck.item(root,"values")[1])
		new = 0
		items = deck.get_children(root)
		for i in items:
			c = int(deck.item(i, "values")[1])
			new += c
		deck.item(root, values=["", new])
		delta = current - new
		totalCards.set(totalCards.get()-delta)


deck.pack()

root.mainloop()
