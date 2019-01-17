from astropy.stats import SigmaClip
from photutils import ModeEstimatorBackground

def GetBackground(image):
    sigma_clip = SigmaClip(sigma=3.)
    bkg = ModeEstimatorBackground(median_factor=3., mean_factor=2.,sigma_clip=sigma_clip)
    bkg_value = bkg.calc_background(image)
    return(bkg_value)
