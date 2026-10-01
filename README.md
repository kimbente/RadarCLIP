# RadarCLIP

Contrastive learning for ice-penetrating radar (IPR) data.

![IBIZ logo](assets/IBIZ_logo.png)

# Data

Blankenship, D.D., Roberts, J.L., Greenbaum, J.S., Young, D.A., Van Ommen, T., Le Meur, E. and Beem, L.H. (2018) EAGLE/ICECAP II RADARGRAMS, Ver. 1, Australian Antarctic Data Centre - doi:10.26179/5bcff4afc287d, Accessed: 2026-07-14
[link to AADC](https://data.aad.gov.au/metadata/AAS_4346_EAGLE_ICECAP_LEVEL2_RADAR_DATA)

Roberts, J.L., Blankenship, D.D., Greenbaum, J.S., Beem, L.H., Kempf, S.D., Young, D.A., Richter, T.G., Van Ommen, T. and Le Meur, E. (2025) EAGLE/ICECAP II - geophysical observations (surface and bed elevation, ice thickness, gravity disturbance and magnetic anomalies) - 2015-2018, Ver. 3, Australian Antarctic Data Centre - doi:10.26179/11md-a816, Accessed: 2026-07-14 
[link to AADC](https://data.aad.gov.au/metadata/AAS_4346_EAGLE_ICECAP_LEVEL2_AEROGEOPHYSICS)

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
IceBridge HiCARS 2 L1B Time-Tagged Echo Strength Profiles V001
- Spatial filter

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