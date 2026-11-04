
# Questions for radioglaciology experts
- How is the offset on top determined and what value is used during preprocessing? (L1B -> L2)
- Is the "ice surface" the surface of the lower, compacted ice or the surface of the firn (surface pick coincides with strongest signal but not upper signal)
- low gain/ high gain

# Known issues
2016: 156 radargrams
ER2HI1B_2017023_ICP8_JKB2r_F07T08a_000 (no match at all)
ER2HI1B_2017027_KNX_JKB2r_Y27a_001 (one missing)

# Environment

# Vocabulary
- subtrate
- trace

# xOPR
- some of the UTIG data does not contain bed picks (which I need)

# Normalisation
- Potentially only shift the data to be mean zero to keep relative differences in db inside the data, while decoupling from ice thickness/attenuation
- 
- 

# HiCARS Earthdata

https://gitlab.com/openpolarradar/opr/-/wikis/Processing-Notes

# Contrast
- deformation velocity
- Calculate the driving stress
- τ_d = ρ · g · H · tan(α)
- u_surface = u_deformation + u_basal
- https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/jgrf.20125 
- https://agupubs.onlinelibrary.wiley.com/doi/full/10.1002/2014GL059976

ML:
- Rank-N-contrast

## Questions:
- What code does xOPR use to determine bed picks? 
- Assign IDs to tiles? 
- Spacing? 
- What additional data do I need? (Specularity)
- Use ratio of bed (peak power) to top

# Encoding: 

Pre-trained computer vision encoder maps an image to an embedding (fixed-length vector).
(SeisCLIP)
OCT (optical coherence tomography)
RETFound

DINOv2 (224 or 364)


# Variables:
Calculate from radar tile:
- average amplitude in "above boundry" layer
- specularity?!
