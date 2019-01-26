from astropy.stats import SigmaClip
from photutils import Background2D, ModeEstimatorBackground
from numpy import std
def GetBackground(image):
    sigma_clip = SigmaClip(sigma=3.)
    bkg_estimator = ModeEstimatorBackground()
    Bg2D = Background2D(image, (20, 30), filter_size=(4, 4),sigma_clip=sigma_clip, bkg_estimator=bkg_estimator)
    Background=Bg2D.bkg_estimator.calc_background(image)
    Sigma=std(Bg2D.background)
    return Background, Sigma
