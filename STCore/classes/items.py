from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from posixpath import basename
from time import struct_time
from warnings import simplefilter

from astropy.io.fits import header as _header
from numpy import ndarray
from tkinter import Variable

CURRENT_VERSION = 2
#----------------------------------
class TrackState(Enum):
	"ACTIVE", 
	"INACTIVE", 
	"LOST", 
	"RUNNING"
#--------------------------------------------------
@dataclass
class Item(ABC):
	@property
	@abstractmethod
	def name(cls):
		raise NotImplementedError
		
	@property
	@abstractmethod
	def version(cls):
		raise NotImplementedError
	
	@abstractmethod
	def printd(self):
		raise NotImplementedError
#--------------------------------------------------
@dataclass
class File(Item):
	name = "Archivo"
	version = 2
	active = True
	path : str
	data : ndarray		= None
	header : _header	= None
	date : struct_time	= None
	relative_path :bool	= False
	simple	:bool		= False

	def printd(self):
		pass
	
	def exists(self):
		from os.path import  isfile
		return isfile(self.path)
#--------------------------------------------------
@dataclass
class Star(Item):
	name = "Estrella"
	version = 2
	location : tuple
	guide : bool
	sample : ndarray
	size : int
	bounds : int
	bkg_samples : tuple
	bkg_size : int

	def printd(self):
		pass
#--------------------------------------------------
@dataclass
class Track(Item):	
	name = "Rastreador"
	version = 2
	state : TrackState 
	star : Star
	locations : list
	values : list
	losses : int

	def printd(self):
		pass
#--------------------------------------------------
@dataclass
class Setting(object):
	value 	: Variable
	group 	: str
	name 	:	 str
	default : object

	def set(self, value):
		self.value.set(value = value)
	def get(self):
		return self.value.get()
#--------------------------------------------------
@dataclass
class Language(object):
	filepath	: str
	id 			= ""
	name 		= ""
	version 	= -1
	dictionary  = None
	header_end 	= 0