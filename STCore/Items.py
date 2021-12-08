from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from posixpath import basename
from time import struct_time

from astropy.io.fits import header as _header
from numpy import ndarray

CURRENT_VERSION = 2

class TrackState(Enum):
	"ACTIVE", 
	"INACTIVE", 
	"LOST", 
	"RUNNING"

@dataclass
class Item(ABC):
	@property
	@classmethod
	@abstractmethod
	def name(cls):
		raise NotADirectoryError
		
	@property
	@classmethod
	@abstractmethod
	def version(cls):
		raise NotADirectoryError
	
	@abstractmethod
	def printd(self):
		raise NotImplementedError

@dataclass
class File(Item):
	name = "Archivo"
	version = 2
	active = True
	path : str
	data : ndarray
	header : _header
	date : struct_time

	def printd(self):
		pass
	
	def Exists(self):
		from os.path import  isfile
		return isfile(self.path)

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

	
