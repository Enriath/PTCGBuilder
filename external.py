##A place to store external code that I find from third parties.
from tkinter import *
import re


##Credit: Fredrik Lundh
##Date	: 08/09/1998
##URL	: http://effbot.org/zone/tkinter-autoscrollbar.htm
class AutoScrollbar(Scrollbar):
	# A scrollbar that hides itself if it's not needed.
	# Only works if you use the grid geometry manager!
	def set(self, lo, hi):
		if float(lo) <= 0.0 and float(hi) >= 1.0:
			# grid_remove is currently missing from Tkinter!
			self.tk.call("grid", "remove", self)
		else:
			self.grid()
		Scrollbar.set(self, lo, hi)
	def pack(self, **kw):
		raise TclError("cannot use pack with this widget")
	def place(self, **kw):
		raise TclError("cannot use place with this widget")


##Credit: user17918
##Date	: 03/09/09
##URL	: http://stackoverflow.com/a/1374617
##Note	: This is not as-is. Multiple changes have been made for convenience.
class TwoWay:
	def __init__(self):
		self.d = {}
		self.normal = {}
	def add(self, k, v):
		self.d[k] = v
		self.d[v] = k
		self.normal[k] = v
	def remove(self, k):
		self.d.pop(self.d.pop(k))
		self.normal.pop(k)
	def get(self, k):
		return self.d[k]
	def __str__(self):
		return str(self.normal)

