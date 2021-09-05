
from tkinter import filedialog
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import figure
from os.path import splitext, isfile
from os import remove
import STCore.ImageView
#import pyfits as fits
from astropy.io import fits
def ExportImage(figure):
	path = filedialog.asksaveasfilename(confirmoverwrite = True, filetypes=[("Portable Network Graphics", "*.png"), ("JPEG Image", "*.jpg")], defaultextension = "*.png")
	figure.savefig(str(path))

def ExportImageExt(data, mode, color, lmin, lmax, imMin, imMax):
	path = filedialog.asksaveasfilename(confirmoverwrite = True, filetypes=[("FiTS Image", "*.fit"), ("Portable Network Graphics", "*.png"), ("JPEG Image", "*.jpg")], defaultextension = "*.fit")
	if splitext(str(path))[1] == ".fit":
		if (isfile(str(path))):
			remove(str(path))		# La funcion PyFITS.HDUList.writeto no permite sobreescritura	
		hdu = fits.PrimaryHDU((data * imMax + imMin).astype(int))
		hdulist = fits.HDUList([hdu])
		hdulist.writeto(path)
	else:
		tableFig = figure.Figure(figsize = (7, 4), dpi= 200)
		tableAx = tableFig.add_subplot(111)
		Img = tableAx.imshow(data)
		canvas = FigureCanvasAgg(tableFig)
		Img.norm.vmax = lmax
		Img.norm.vmin = lmin
		Img.set_cmap(STCore.ImageView.ColorMaps[color])
		Img.set_norm(STCore.ImageView.Modes[mode])
		tableFig.savefig(str(path))

def ExportData(TrackedStars, MagData, TimeLabel):
	path = filedialog.asksaveasfilename(confirmoverwrite = True, filetypes=[("Archivo de texto", "*.txt")], defaultextension = "*.txt")
	with open(path, "wb") as f:
		print ("Magnitudes aparentes de "+str(len(TrackedStars))+" estrellas", file = f)
		print ("Generado por StarTrak", file = f)
		print (" ", file = f)
		names = "Fechas\t"
		for t in TrackedStars:
			names += t.star.name+ "\t"
		print (names, file=f)
		i = 0
		while i < MagData.shape[1]:
			line = TimeLabel[i]+"\t"
			j = 0
			while j < MagData.shape[0]:
				line += ('%.2f' % MagData[j][i])+"\t"
				j += 1
			print (line, file = f)
			i += 1

def ExportPDF(fig, MagData, TrackedStars):
		path = filedialog.asksaveasfilename(confirmoverwrite = True, filetypes=[("Documento PDF", "*.pdf")], defaultextension = "*.pdf")
		collabel = []
		fig.set_size_inches(7, 4)
		for t in TrackedStars:
			collabel.append(t.star.name)
		tableFig = figure.Figure(figsize = (7, 4), dpi= 100)
		tableAx = tableFig.add_subplot(111)
		tableAx.set_axis_off()
		tableAx.table(cellText=MagData.round(decimals = 2),colLabels=collabel,loc='center')
		with PdfPages(str(path)) as pp:
			
			pp.savefig(fig)
			pp.savefig(tableFig)