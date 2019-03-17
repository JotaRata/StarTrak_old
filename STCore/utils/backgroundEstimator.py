#from photutils import Background2D, ModeEstimatorBackground
from numpy import std, mean
from scipy.stats import mode
#from time import time
def GetBackground(image):
    #sigma_clip = SigmaClip(sigma=3.)
    #startTime = time()
    #bkg_estimator = ModeEstimatorBackground()
    # bkg = Background2D(image, (20, 30), filter_size=(4, 4),sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    background = mean(mode(image)[0])
    #print "Tiempo: ", time() - startTime
    #plt.imshow(bkg.background, origin='lower', cmap='Greys_r')
    #background=bkg.bkg_estimator.calc_background(image)
    sig= std(image)
    #print "background = ", background, " sig = ", sig
    return background,sig
