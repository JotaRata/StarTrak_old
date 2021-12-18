from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from posixpath import basename
from sys import path
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

	def __getitem__(self, key: str) -> str:
		if key in self.dictionary:
			return self.dictionary[key]
		else:
			return key

	def printd(self):
		print(self.id, self.name, self.version, self.header_end, self.dictionary)

	def validate(self):
		path_complete = False
		id_complete = False
		name_complete = False
		version_complete = False
		header_complete = False
		if self.filepath is not None:
			if len(self.filepath) > 0:
				path_complete = True
		if len(self.id) >= 2:
			id_complete = True
		if len(self.name) >= 3:
			name_complete = True
		if self.version >= 0:
			version_complete = True
		if self.header_end > 0:
			header_complete = True
		return path_complete and id_complete and name_complete and version_complete and header_complete
