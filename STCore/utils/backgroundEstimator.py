from astropy.stats import SigmaClip
from photutils import Background2D, ModeEstimatorBackground
from numpy import std
import numpy as np

def GetBackground(image):
    sigma_clip = SigmaClip(sigma=3.)
    bkg_estimator = ModeEstimatorBackground()
    bkg = Background2D(image, (20, 30), filter_size=(4, 4),sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    #plt.imshow(bkg.background, origin='lower', cmap='Greys_r')
    background=bkg.bkg_estimator.calc_background(image)
    sig=np.std(image)
    return background,sig
