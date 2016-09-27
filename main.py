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
		self.columnsEntry = Entry(searchFrame, width=3, validate="focus")
		self.columnsEntry.configure(validatecommand=lambda x=self.columnsEntry: self.entryValidate(x, "3"))
		self.columnsEntry.grid(row=0, column=3)
		self.columnsEntry.insert(0, "3")
		rowsLabel = Label(searchFrame, text="Rows: ")
		rowsLabel.grid(row=0, column=4)
		self.rowsEntry = Entry(searchFrame, width=3, validate="focus")
		self.rowsEntry.configure(validatecommand=lambda x=self.rowsEntry: self.entryValidate(x, "2"))
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
			self.root.bind_all("<MouseWheel>",
						  lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
		elif platform.system() == "Darwin":  # OSX
			##UNTESTED!!!
			self.root.bind_all("<MouseWheel>", lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(e.delta, "units"))
		else:  # Linux et al. X11 mainly
			##UNTESTED!!!
			self.root.bind_all("<Button-4>",
						  lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
			self.root.bind_all("<Button-5>",
						  lambda e, canvas=self.scrollbarProxy: canvas.yview_scroll(int(e.delta / 120), "units"))

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
		self.entryValidate(self.columnsEntry, "3")
		self.entryValidate(self.rowsEntry, "2")
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
				c = Card(name, set, num, image, False, True)
			elif name[:2].upper() == "M ":
				c = Card(name, set, num, image, True, False, True)
			elif name[-3:].upper() == " EX":
				c = Card(name, set, num, image, True)
			else:
				c = Card(name, set, num, image)
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

	@staticmethod
	def entryValidate(entry, default):
		"""
		Checks that an entry follows the following criteria:
		Is <= 3 characters
		Is an integer
		Is > 0 numerically

		Range of values, therefore, is between 1 and 999 as strings.

		Args:
		entry 	(tkinter.Entry)	: The Entry widget to validate.
		default (int as String)	: Th default value to reset to if one of the criteria is not met.

		Returns: True
		This is so the Entry Validation doesn't throw a hissy fit.
		"""
		if len(entry.get()) > 3:
			entry.delete(3, END)
		try:
			int(entry.get())
		except ValueError:
			entry.delete(0, END)
			entry.insert(0, default)
			return True
		if int(entry.get()) <= 0:
			entry.delete(0, END)
			entry.insert(0, default)
		return True

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
		self.entryValidate(self.columnsEntry,"3")
		return int(self.columnsEntry.get())


class Card:

	#Default Card image dimensions
	#Used to set up the Scrollbar Proxy Canvas
	ImageDimensions = (245,342)

	#The Pretty Set Names
	sets = {"xy0": "Kalos Starter Set",
			"xy1": "XY",
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
			"g1": "Generations",
			"dc1": "Double Crisis"}

	def __init__(self,name,set,number,imageURL,isEX=False,isBreak=False,isMega=False):
		"""
		Builds a Card object

		Args:
		name 		(String)				: The name of the card
		set 		(String)				: The set code, see Card.sets
		number 		(String)				: The number. Must be a string to support special sets, like Radiant Collections (RC##)
		imageURL 	(String)				: The image URL
		isEX 		(Boolean, default=False): Is the card an EX?
		isBreak 	(Boolean, default=False): Is the card a BREAK Evolution? Used for rendering the card.
		isMega 		(Boolean, default=False): Is the card a Mega Evolution?

		Returns: Nothing
		"""
		self.name = name
		self.set = set
		self.number = number
		self.imageURL = imageURL
		self.isEX = isEX
		self.isBreak = isBreak
		self.isMega = isMega

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

	def formatPretty(self):
		"""
		Makes a descriptive string of all the card details. Used in CardDisplay.display()

		Args: Nothing

		Returns: String
		"""
		return self.name+", "+self.getPrettySet()+" #"+self.number


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
		i = card.getCardImage()
		if card.isBreak:
			i.thumbnail((245,245),Image.ANTIALIAS)
		itk = ImageTk.PhotoImage(i)
		self.root = Frame(self.parent.cardFrame)
		pic = Label(self.root, image=itk)
		pic.image = itk
		pic.pack()
		name = Label(self.root, text=card.formatPretty())
		name.pack()
		self.num = num

	def display(self):
		"""
		Actually draws the widget. This makes all the cards appear at once.

		Args: Nothing

		Returns: Nothing
		"""
		self.root.grid(row=self.num // self.parent.getProvidedCardGridWidth(), column=self.num % self.parent.getProvidedCardGridWidth())


##BASIC TEST CODE

root = Tk()
root.title("PTCGBuilder")

cardSelector = CardSelector()

button = Button(root,text="CLICK ME",width=40,height=40,command=cardSelector.build)
button.pack(fill="both")

root.mainloop()