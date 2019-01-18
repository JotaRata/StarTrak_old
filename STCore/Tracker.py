from astropy.io import fits
import numpy
import matplotlib


def Track(data, stars, sigma = 3):
	results = []
	for s in stars:
		ind = numpy.swapaxes(numpy.array(numpy.where(numpy.abs(data - s.value) < sigma)), 0, 1)
		r = numpy.empty((0,2), int)
		i = 0
		while i < ind.shape[0]:
			if abs(ind[i,0] -  s.location[0]) < s.radius and abs(ind[i,1] -  s.location[1]) < s.radius:
				_ind = numpy.atleast_2d(ind[i,:])
				r = numpy.append(r, _ind, axis = 0)
			i += 1
		if len(r) != 0:
			rm = numpy.mean(r, axis = 0)
			results.append(rm)
	print results
	return results