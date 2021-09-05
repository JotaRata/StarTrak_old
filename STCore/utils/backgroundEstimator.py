#from photutils import Background2D, ModeEstimatorBackground
from numpy import std, mean
import numpy
from scipy.stats import mode
#from time import time
def GetBackground(image):
    #sigma_clip = SigmaClip(sigma=3.)
    #startTime = time()
    #bkg_estimator = ModeEstimatorBackground()
    # bkg = Background2D(image, (20, 30), filter_size=(4, 4),sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    background = int(mean(mode(image)[0]))
    #print "Tiempo: ", time() - startTime
    #plt.imshow(bkg.background, origin='lower', cmap='Greys_r')
    #background=bkg.bkg_estimator.calc_background(image)
    sig= std(image)
    #print "background = ", background, " sig = ", sig
    return background, sig

def GetBackgroundMean(image):
    return numpy.median(image)
	#return getmode(getmode(image))[0]

def getmode(ndarray, axis=0):
    # Check inputs
    ndarray = numpy.asarray(ndarray)
    ndim = ndarray.ndim
    if ndarray.size == 1:
        return (ndarray[0], 1)
    elif ndarray.size == 0:
        raise Exception('Cannot compute mode on empty array')
    try:
        axis = range(ndarray.ndim)[axis]
    except:
        raise Exception('Axis "{}" incompatible with the {}-dimension array'.format(axis, ndim))

    # If array is 1-D and numpy version is > 1.9 numpy.unique will suffice
    #if all([ndim == 1,
    #        int(numpy.__version__.split('.')[0]) >= 1,
    #        int(numpy.__version__.split('.')[1]) >= 9]):
    #    modals, counts = numpy.unique(ndarray, return_counts=True)
    #    index = numpy.argmax(counts)
    #    return modals[index], counts[index]

    # Sort array
    sort = numpy.sort(ndarray, axis=axis)
    # Create array to transpose along the axis and get padding shape
    transpose = numpy.roll(numpy.arange(ndim)[::-1], axis)
    shape = list(sort.shape)
    shape[axis] = 1
    # Create a boolean array along strides of unique values
    strides = numpy.concatenate([numpy.zeros(shape=shape, dtype='bool'),
                                 numpy.diff(sort, axis=axis) == 0,
                                 numpy.zeros(shape=shape, dtype='bool')],
                                axis=axis).transpose(transpose).ravel()
    # Count the stride lengths
    counts = numpy.cumsum(strides)
    counts[~strides] = numpy.concatenate([[0], numpy.diff(counts[~strides])])
    counts[strides] = 0
    # Get shape of padded counts and slice to return to the original shape
    shape = numpy.array(sort.shape)
    shape[axis] += 1
    shape = shape[transpose]
    slices = [slice(None)] * ndim
    slices[axis] = slice(1, None)
    # Reshape and compute final counts
    counts = counts.reshape(shape).transpose(transpose)[slices] + 1

    # Find maximum counts and return modals/counts
    slices = [slice(None, i) for i in sort.shape]
    del slices[axis]
    index = numpy.ogrid[slices]
    index.insert(axis, numpy.argmax(counts, axis=axis))
    return sort[tuple(index)]#, counts[index]