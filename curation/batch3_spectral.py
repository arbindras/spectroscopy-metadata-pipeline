# Batch3 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (C:\Users\Admin\RAG\2\papers\<id>.pdf) + dataset folder (D:\Batch3_datasets\<id>_<title>).
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

# ---------------------------------------------------------------------------
# IODP JOIDES Resolution shipboard data (papers = Proceedings volume front matter /
# expedition summary chapters; methods are standard JRSO shipboard procedures)
# ---------------------------------------------------------------------------
_PAPER = {
    360: "Expedition 360 summary",
    363: "volume front matter (Univ. Birmingham repository copy)",
    371: "Expedition 371 summary",
    378: "volume front matter",
    379: "Expedition 379 summary",
    383: "Expedition 383 summary",
    "390393": "Vol. 390/393 front matter (covers Exp 390C, 395E, 390, 393)",
    391: "Vol. 391 front matter (covers Exp 391 and 397T)",
}


def _iw(rid, exp, vol, nrows, nholes, sites, depth_max, nparams, spec):
    R[rid] = dict(
        modality="None (no spectra): IODP interstitial-water geochemistry composite report (ICP-AES emission lines, ion chromatography, titration, refractometry" + (", colorimetric UV-Vis" if spec else "") + ")",
        num_samples=nrows,
        spectral_target_relationship=f"No spectral data; {nparams} pore-water parameters (alkalinity, pH, salinity, major/minor ions and elements" + (", NH4+/PO4 by UV-Vis colorimetry" if spec else "") + f") vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}) -> diagenesis, organic-matter remineralisation, fluid-rock/basement exchange",
        source_file=f"{rid}.pdf ({_PAPER[vol]}, Exp {exp}); IWREPORT-README.txt; data_by_hole.zip per-hole IWREPORT csv",
        confidence=0.85,
    )


_iw("10206405", "391", 391, 115, 4, "U1575-U1578", 371.5, 23, True)
_iw("10520455", "363", 363, 383, 11, "U1482-U1490", 533.85, 21, True)
_iw("10642260", "390C", "390393", 155, 4, "U1556-U1559", 554.2, 25, False)
_iw("10652149", "395E", "390393", 28, 2, "U1560-U1561", 116.86, 25, True)
_iw("10668214", "390", "390393", 86, 3, "U1556, U1559", 274.76, 24, True)
_iw("10672701", "393", "390393", 227, 6, "U1558, U1560, U1583", 173.86, 29, True)
_iw("10809947", "378", 378, 193, 3, "U1553", 420.18, 24, True)

_SPEC_WL = {"ammonium": 640, "phosphate": 885, "silica": 812}


def _spec(rid, exp, vol, counts, nsamples, nholes, sites, depth_max, files, cary, conf=0.85, note=""):
    analytes = list(counts)
    wl = [_SPEC_WL[a] for a in analytes]
    R[rid] = dict(
        modality=f"Single-wavelength UV-Vis colorimetric absorbance (Agilent {cary}) of interstitial water: " + ", ".join(f"{a} {w} nm" for a, w in zip(analytes, wl)),
        spectral_range_original_min=min(wl), spectral_range_original_max=max(wl), spectral_range_original_unit="nm",
        num_spectral_channels=len(wl), spectral_resolution=1.5, spectral_resolution_unit="nm (spectral bandwidth, SBW)",
        num_samples=nsamples,
        num_spectral_values=sum(counts.values()),  # concentration results (one absorbance reading per analyte per sample)
        spectral_target_relationship=f"Absorbance at fixed analytical wavelengths vs external standard curve -> pore-water {'/'.join(analytes)} concentrations (uM) vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}); Beer-Lambert linear calibration" + note,
        source_file=f"{rid}.pdf ({_PAPER[vol]}, Exp {exp}); SPEC-README.txt; {files}",
        confidence=conf,
    )


_spec("10206445", "391", 391, {"ammonium": 114, "phosphate": 114}, 114, 4, "U1575-U1578", 371.5,
      "data_by_hole.zip (4 *-SPEC.csv); supplementary_material.zip raw_data_files (9 Cary Advanced Reads csv + 8 *.xlsm calibration workbooks)", "Cary 300")
_spec("10406792", "383", 383, {"ammonium": 299, "phosphate": 300, "silica": 162}, 300, 12, "U1539-U1544", 337.58,
      "data_by_hole (12 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (22 Cary csv, 22 .BAB, 22 *_RESULTS.xlsm)", "Cary 300")
_spec("10520357", "363", 363, {"ammonium": 345, "phosphate": 349}, 350, 10, "U1482-U1490", 489.25,
      "data_by_hole (10 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (16 Cary csv, 41 .BAB, 23 xlsx workbooks)", "Cary 100")
_spec("10672845", "393", "390393", {"ammonium": 93, "phosphate": 102}, 90, 5, "U1558, U1560, U1583", 173.86,
      "data_by_hole (5 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files per site (6 xlsm, 3 csv, 3 .MAB, 3 .BAB)", "Cary 300")
_spec("11238497", "371", 371, {"ammonium": 378, "phosphate": 311, "silica": 321}, 327, 11, "U1506-U1511", 497.36,
      "data_by_hole (11 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (48 Cary csv / run lists, 36 RESULTS xlsx, 41 .BAB)", "Cary 300",
      note="; squeezed IW and Rhizon samples")


def _rsc(rid, exp, vol, nspectra, nfiles, nholes, sites, depth_max, sensor, bands, lo, hi):
    R[rid] = dict(
        modality=f"VIS diffuse reflectance spectroscopy and colorimetry (RSC) of split-core section halves ({sensor} + integrating sphere on SHMSL)",
        spectral_range_original_min=lo, spectral_range_original_max=hi, spectral_range_original_unit="nm",
        num_spectral_channels=bands, sampling_interval=2, sampling_interval_unit="nm",
        num_samples=nfiles,  # per-section-half normalised reflectance files
        num_spectra=nspectra, num_spectral_values=nspectra * bands,
        spectral_target_relationship=f"% reflectance spectra (white/dark-referenced) of sediment/rock core surfaces -> CIE XYZ, L*a*b*, chroma, hue vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}) for lithostratigraphy, cyclostratigraphy and hole-to-hole correlation",
        source_file=f"{rid}.pdf ({_PAPER[vol]}, Exp {exp}); RSC-README.txt; data_by_hole/*-RSC.csv; supplementary raw_data_files norm_*/raw_*_rsc.csv + *.RSC; configuration files",
        confidence=0.85,
    )


_QEP = "Ocean Insight QE Pro"
_USB = "Ocean Optics USB4000-VIS"
_rsc("10206437", "391", 391, 22135, 816, 5, "U1575-U1578", 483.71, f"{_QEP} QEP00732", 165, 390, 718)
_rsc("10210964", "397T", 391, 5196, 229, 2, "U1584-U1585", 494.82, f"{_QEP} QEP00732", 165, 390, 718)
_rsc("10406782", "383", 383, 128407, 2191, 19, "U1539-U1544", 339.52, f"{_QEP} QEP02181", 171, 390, 730)
_rsc("10520345", "363", 363, 262072, 5733, 30, "U1482-U1490", 534.975, _USB, 261, 380, 900)
_rsc("10642303", "390C", "390393", 35614, 711, 5, "U1556-U1559", 574.015, f"{_QEP} QEP00674/QEP00732", 165, 390, 718)
_rsc("10652177", "395E", "390393", 7332, 163, 4, "U1560-U1561", 121.35, f"{_QEP} QEP00674/QEP00732", 165, 390, 718)
_rsc("10668427", "390", "390393", 23139, 606, 7, "U1556, U1557, U1559", 682.615, f"{_QEP} QEP00732", 165, 390, 718)
_rsc("10672833", "393", "390393", 28789, 694, 12, "U1558, U1559, U1560, U1583", 368.4, f"{_QEP} QEP00732", 165, 390, 718)
_rsc("10810008", "378", 378, 33626, 790, 5, "U1553", 581.025, f"{_QEP} QEP00674", 171, 390, 730)
_rsc("11200444", "379", 379, 52839, 915, 9, "U1532-U1533", 787.39, f"{_QEP} QEP00732", 171, 390, 730)
_rsc("11238485", "371", 371, 118658, 1946, 11, "U1506-U1511", 855.62, f"{_QEP} QEP00732", 171, 390, 730)
_rsc("11984398", "360", 360, 39202, 407, 1, "U1473", 789.52, f"{_USB} RF52054", 261, 380, 900)

# ---------------------------------------------------------------------------

R["10083991"] = dict(
    modality="Time-resolved UV-Vis absorption: anaerobic stopped-flow rapid-scan diode-array spectra and single-wavelength (A427) kinetics + steady-state diode-array spectra of heme/FAD redox reactions in STEAP1/STEAP2 (+ bio-layer interferometry)",
    spectral_range_original_min=190, spectral_range_original_max=1100, spectral_range_original_unit="nm",
    num_spectral_channels=911,  # HP 8453 spectra 190-1100 nm @1 nm; stopped-flow rapid-scan spectra 182-192 points @2.2 nm (~295-708 nm)
    sampling_interval=1, sampling_interval_unit="nm (HP 8453); 2.2 nm (stopped-flow rapid scan)",
    num_samples=8,  # 8 spectral-kinetic reactions (STEAP1/2, L230G mutant, +FADH2 / NADPH / NADH+b5R)
    num_spectra=2217,  # 313 HP8453 spectra (911 pts) + 1904 rapid-scan spectra (182-192 pts)
    num_spectral_values=640886,
    spectral_target_relationship="Soret shift 413 -> 427 nm and alpha/beta bands (532/560 nm) vs time -> heme reduction/oxidation state of STEAP1/STEAP2; global deconvolution (Pro-Kineticist) into spectral species and rate constants (e.g. 177.9 and 0.13 s-1 for STEAP1+b5R+NADH); A427 traces vs [Fe3+-NTA] or [FADH2] -> kobs, KM",
    source_file="10083991.pdf (Chen et al. 2023 eLife 88299); README.md; 7 figure workbooks Figure2/3/4/5(-FigureSupplement).xlsx (sheet = panel/reaction)",
    confidence=0.85,
)

R["10182614"] = dict(
    modality="Airborne limb-scanning NIR differential optical absorption spectroscopy (mini-DOAS, scattered sunlight) - derived products only (+ VLIDORT-QS radiative-transfer simulations)",
    spectral_range_original_min=900, spectral_range_original_max=1700, spectral_range_original_unit="nm",  # NIRQuest512, 512 px; ice fit 1338-1631 nm
    num_spectral_channels=512, spectral_resolution=17, spectral_resolution_unit="nm FWHM",
    num_samples=2,  # Global Hawk flights 16 and 17 Feb 2014 (Guam)
    spectral_target_relationship="DOAS fits of ice and liquid-water absorption (1338-1631 nm), O2 (1160-1293 nm) and CO2 (1508-1678 nm) slant column densities -> slant ice water path (SIWP) of tropical-tropopause-layer cirrus; VLIDORT simulated ice absorbance vs IWC, solar zenith/azimuth, albedo and cloud geometry -> IWC retrieval compared with in-situ FCDP and NOAA water probes",
    source_file="10182614.pdf (Colosimo et al. 2024 AMT 17:2367); 7 ASCII figure files Results_Fig2_Feb-16/17-2014.dat, Results_Fig3-6.dat (VLIDORT tables), Results_Fig8.dat",
    confidence=0.8,
)

R["10184946"] = dict(
    modality="None (derived product): satellite UV-Vis nadir ozone retrieval (GOME-1 / SCIAMACHY / OMI) - gridded lower-tropospheric column ozone",
    spectral_range_original_min=266, spectral_range_original_max=335, spectral_range_original_unit="nm",  # Hartley (266-307) + Huggins (323-335) fit windows of the RAL scheme
    num_samples=22,  # annual means 1996-2017
    spectral_target_relationship="Sun-normalised UV radiances in Hartley/Huggins bands -> optimal-estimation ozone profile -> lower tropospheric column ozone (surface-450 hPa, DU) on a 5 x 5 deg grid (72 lon x 24 lat, 57.5S-57.5N) per year; spatial/temporal LTCO3 variability and trends",
    source_file="10184946.pdf (Miles et al. 2015 AMT 8:385, GOME-2 RAL ozone retrieval - method paper; dataset paper Pope et al. 2023 not supplied); ral_space_merged_ltco3_record_1996_2017.nc",
    confidence=0.7,
)

R["10257363"] = dict(
    modality="None (no spectra): DFT training data and machine-learned tensorial neuroevolution potential (TNEP) models for dipole, polarizability and susceptibility used to simulate IR/Raman spectra",
    num_samples=12,  # 12 TNEP model/training-set combinations
    spectral_target_relationship="Atomic structures with reference dipole moments / polarizability / susceptibility tensors (water monomer, dimer, Zundel, bulk water, QM7B molecules, iron oxide, BaZrO3) -> TNEP models in GPUMD -> IR (dipole autocorrelation) and Raman (polarizability autocorrelation) spectra of liquid water, PTAF- and BaZrO3",
    source_file="10257363.pdf (Xu et al. 2024 J. Chem. Theory Comput., doi:10.1021/acs.jctc.3c01343); 13 nep_*.txt models + 13 ZIPs (nep.in, nep.txt, train.xyz, test.xyz extended-XYZ; reference-data.db for BaZrO3)",
    confidence=0.85,
)

R["10278196"] = dict(
    modality="None (no spectroscopy): visual microscopy (dissection microscope) and hot-needle testing of suspected microplastic particles",
    num_samples=30,  # 30 fish IDs (29 fish + blank sample entries)
    spectral_target_relationship="No spectral data; particle counts by type (fibre, film, fragment incl. tyre-wear-like) and colour in fish muscle and gastrointestinal tract per gram tissue",
    source_file="10278196.pdf (Hart et al. 2022 Front. Mar. Sci., dolphin gastric microplastics - related study, same Sarasota Bay group); Fish_Microplastics_Data_Repository.xlsx + README.md",
    confidence=0.6,
)

R["10409160"] = dict(
    modality="ATR-FTIR (diamond, N2 glovebox) and Raman (488/633 nm) spectroscopy + powder XRD reference database of battery solid-electrolyte interphase compounds",
    spectral_range_original_min=370.339, spectral_range_original_max=4000.433, spectral_range_original_unit="cm-1",  # ATR-FTIR; Raman 103-3203 cm-1 (LiH to 4004)
    num_spectral_channels=3765, spectral_resolution=2, spectral_resolution_unit="cm-1 (FTIR)",
    sampling_interval=0.964, sampling_interval_unit="cm-1 (FTIR); Raman ~1.66 raw / 1.36 interpolated",
    num_samples=10,  # CH3COOLi, Li2CO3, 6LiF, 7LiF, LiH, LiPF6, Li2O, MnF2, NiF2, PEO
    num_spectra=20,  # 10 FTIR + 10 Raman raw spectra (each with background and processed versions) + 10 XRD patterns
    num_spectral_values=61195,  # FTIR 37,645 + Raman 23,550 raw values
    spectral_target_relationship="Reference vibrational fingerprints (peak positions + assignments) of SEI/CEI components for identifying interphase chemistry in Li-ion/Li-metal batteries; raw, background and FFT-filtered normalised spectra",
    source_file="10409160.pdf (Karapin-Springorum et al. 2025 Sci. Data 12:33); ATR-FTIR.xlsx, Raman.xlsx, XRD.xlsx (one sheet per compound: Raw / Background / Final) + README.md",
    confidence=0.9,
)

R["10426284"] = dict(
    modality="Hyperspectral VIS absorption/attenuation (WET Labs ac-s, filter-pad integrating-sphere spectrophotometry) + multispectral backscattering and LISST size spectra of phytoplankton cultures",
    spectral_range_original_min=300, spectral_range_original_max=800, spectral_range_original_unit="nm",  # filter-pad 300-800 @0.2 nm; ac-s 400-730 @2.5 nm
    num_spectral_channels=2501, sampling_interval=0.2, sampling_interval_unit="nm (filter pad); 2.5 nm (ac-s)",
    num_samples=92,  # culture/dilution experiments with ac-s; 191 filter-pad samples; ~62 strains, 9 classes
    num_spectra=757,  # 3 x 191 filter-pad mean spectra (ap, ad, aph; uncertainty sheets not counted) + 2 x 92 ac-s (ap, cp)
    num_spectral_values=573 * 2501 + 184 * 133,
    spectral_target_relationship="Particulate (ap), de-pigmented (ad) and phytoplankton (aph) absorption, beam attenuation (cp) and backscattering (bb) spectra of 50+ CCMP strains, mixtures and climate-change growth conditions -> optical fingerprint library linking spectral shape to taxonomic class, HPLC pigments, POC, Chl a and cell size for PACE ocean-colour phytoplankton community algorithms",
    source_file="10426284.pdf (Lomas et al. 2024 Sci. Data 11:168); PLOPS_Data_27Sept2023_Final.xlsx (12 sheets: ap_ACS, cp_ACS, backscatter, LISST, POC_chla, HPLC, ap/ad/aph_spec + _unc) + README.md",
    confidence=0.85,
)

R["10428759"] = dict(
    modality="Transmission micro-FTIR (Nicolet iN10 MX imaging microscope, MCT detector) of charcoal fragments",
    spectral_range_original_min=949.81, spectral_range_original_max=3500.32, spectral_range_original_unit="cm-1",
    num_spectral_channels=2646, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=137,  # 70 reference (10 species x 7 temperatures) + 67 combustion-facility samples
    num_spectra=4034,  # 2100 reference (30 per species-temperature) + 1934 combustion-facility spectra
    num_spectral_values=4034 * 2646,
    spectral_target_relationship="FTIR spectra of laboratory charcoal (200-800 C, 10 western-North-American tree/shrub species) and combustion-facility burn charcoal (PIPO, QUKE, POTR, ABCO) -> maximum pyrolysis temperature and fuel/species identity by modern-analogue matching (paper method: 57 % exact, 93 % within +/-100 C)",
    source_file="10428759.pdf (Maezumi et al. 2021 Palaeogeogr. Palaeoclimatol. Palaeoecol. 578:110580 - method paper); Minatre_reference_spectra.csv, Minatre_combustionfacility_spectra.csv + README.md",
    confidence=0.8,
)

R["10478661"] = dict(
    modality="Unpolarized micro-FTIR transmission spectroscopy (OH stretching region) of hydrous Al-free stishovite single crystals (+ XRD)",
    spectral_range_original_min=895.8, spectral_range_original_max=8000.3, spectral_range_original_unit="cm-1",  # most spectra 1500-4000 cm-1
    num_spectral_channels=2594, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.964, sampling_interval_unit="cm-1 (1.93 cm-1 for H5312/H5376)",
    num_samples=6,  # runs H5630 (1300 C), H5326 (1500), H5486 (1700), H5312 (1800), H5376 (1900), H5592 (2100) at 22 GPa
    num_spectra=6, num_spectral_values=18007,
    spectral_target_relationship="Integrated OH absorbance (2669, 3112, 3237, 3311 cm-1 bands) with Paterson (1982) calibration and thickness 80-100 um -> H2O content of stishovite vs synthesis temperature at 22 GPa (max 521(47) wt ppm at 1700 C, 145(26) at 2100 C)",
    source_file="10478661.pdf (Purevjav et al. 2024 GRL 51:e2023GL104029); 6 FTIR-<run>x<crystal>.pdf + 2 XRD-<run>.pdf (numeric two-column tables printed in PDF)",
    confidence=0.8,
)

R["10684347"] = dict(
    modality="VNIR-SWIR (and some MIR/TIR) reflectance spectral library of Mars-relevant minerals compiled from RELAB-type laboratory libraries + ExoMars PanCam geology filter definitions",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",  # 351/400-2500 nm for most; ASTER/USGS files extend to 15.9-25.9 um
    spectral_resolution=2, spectral_resolution_unit="nm @350 to 7 nm @2500 (UWinnipeg ASD); ~1.5-6 cm-1 for FTIR entries",
    sampling_interval=1, sampling_interval_unit="nm (most UWinnipeg spectra)",
    num_samples=426,  # spectra/sample files: montmorillonite 144, hematite 83, basalt 71, saponite 102, vermiculite 26
    num_spectra=426, num_spectral_values=846916,
    spectral_target_relationship="Laboratory reflectance spectra of hematite, Fe/Mg-smectites (montmorillonite, saponite), vermiculite and basalt (incl. heated/mixed samples) convolved to 12 PanCam filters (440-1000 nm) -> spectral parameters (band depths, ratios, slopes) optimised to discriminate hematite and clays for ExoMars rover multispectral imaging",
    source_file="10684347.pdf (Kokaly et al. 2017 USGS Spectral Library Version 7, Data Series 1035 - source-library documentation, not the SPTK paper); exm_pc_geol.csv (filter cwl/FWHM); stabbins2024_exmpc_hematite_spectral_library.zip (426 per-sample CSV with metadata header + Wavelength,Response)",
    confidence=0.7,
)

R["10689754"] = dict(
    modality="FTIR transmittance spectroscopy (Varian 670-IR) of Haematococcus pluvialis microalgal bio-oil and its FAME (+ TGA, DSC thermal analysis)",
    spectral_range_original_min=599.753, spectral_range_original_max=4001.57, spectral_range_original_unit="cm-1",
    num_spectral_channels=1765, sampling_interval=1.9285, sampling_interval_unit="cm-1",
    num_samples=2,  # microalgae bio-oil (MBO) and biodiesel (FAME)
    num_spectra=2, num_spectral_values=3530,
    spectral_target_relationship="FTIR %T of bio-oil vs transesterified FAME -> confirmation of conversion (1435 cm-1 -CH3 of methyl ester, 1730-1750 C=O ester, reduced 3000-3700 O-H/water); RSM-optimised transesterification (oil:methanol 1:4.17, 80 C, CH3ONa 1.5 %) evaluated by GC-FID FAME yield; TGA thermal stability 211-290 C",
    source_file="10689754.pdf (Sanjurjo et al. 2024 BioEnergy Res. 17:2374-2383); Dataset Thermal characterization.xlsx (FTIR MBO, FTIR Biodiesel, TGA x2, DSC x3 sheets)",
    confidence=0.85,
)

R["10690480"] = dict(
    modality="FT-IR (KBr) and UV-Vis absorption spectra of isolated sea-cucumber compounds - figures/peak lists only (+ TLC, VLC, HPLC, GC-MS, MTT cytotoxicity)",
    spectral_range_original_min=221, spectral_range_original_max=274, spectral_range_original_unit="nm",  # reported UV maxima; IR peaks 1036-3441 cm-1
    num_samples=2,  # isolates F4 and F7.8 from Paracaudina australis ethyl acetate / n-hexane fractions
    num_spectra=4,  # 2 FT-IR + 2 UV-Vis spectra shown as images
    spectral_target_relationship="IR functional-group bands (O-H/N-H 3363-3441, C-H 2864-2953, C=O 1701/1746, C=C 1629/1649, C-O 1036-1078 cm-1) and UV maxima (221, 230, 274 nm) -> tentative identification of steroid (dihydrocholesterol / cholestan-3-ol by GC-MS) and flavonoid-type isolates; isolates F4 and F7.8 cytotoxic to T47D cells (IC50 25.3 and 13.76 ug/mL)",
    source_file="10690480.pdf (Sukmiwati et al. F1000Research 13:340, v2 2025); 'Research Datas.pdf' (19-page report with embedded spectra images and tables)",
    confidence=0.6,
)

R["10776084"] = dict(
    modality="ATR-FTIR absorbance spectroscopy of powdered whole Drosophila simulans males, yellow mutants and melanin (+ RNA-seq, locomotor/startle behaviour data)",
    spectral_range_original_min=399.191, spectral_range_original_max=4001.552, spectral_range_original_unit="cm-1",
    num_spectral_channels=1869, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=28,  # 16 evolved/ancestral replicate populations (fl_sim_*), 9 melanin spike-in, yellow mutant, pure melanin (+ duplicates)
    num_spectra=43,  # 32 duplicate spectra (16 populations x a/b) + 9 melanin spike-in + 1 yellow mutant + 1 pure melanin (19 single-spectrum CSV exports duplicate these)
    num_spectral_values=43 * 1869,
    spectral_target_relationship="Absorbance at melanin-specific wavenumbers (melanin absorption index MAI>1: 2925, 2853, 1743, 1153, 1077, 1023 cm-1, derived from melanin spike-in and yellow-mutant contrast) -> relative whole-body melanin content of hot- vs cold-evolved vs ancestral populations (mixed models); main study links dopamine signalling to thermal adaptation",
    source_file="10776084.pdf (Jaksic et al. bioRxiv 585422); README.md; fl_sim_*_males.csv, melanin_pure_as_obtained.csv, yellow_mutant*.csv, males_all_duplicate_spectra.txt, males_2_1_melanin_spikein_spectra.txt, yellow_mutant_spectra.txt; mai.r",
    confidence=0.8,
)

R["10779480"] = dict(
    modality="UV-Vis absorption (Tauc), steady-state and time-resolved photoluminescence, XPS and XRD of perovskite films with triarylamine interlayers + J-V/stability device data (Origin project files)",
    num_samples=3,  # control, TAAT-modified, spiro-covered variants (labels inside .opju)
    spectral_target_relationship="UV-Vis absorbance / Tauc plots -> perovskite bandgap; PL quenching and TRPL decay (ns) -> hole extraction at perovskite/HTM interface with triarylamine (TAAT) modulator; XPS/XRD -> surface chemistry and crystallinity; J-V and maximum-power-point stability -> device performance",
    source_file="10779480.pdf (AlSabeh et al. 2024 Nanoscale Adv. 6:3029, helicene interfacial modulation - related paper, same group; NOT the triarylamine study); 9 OriginLab *.opju figure projects (Figure_2 Tauc/UV-vis/XPS/XRD, Figure_3 PV, Figure_4 PL/TRPL, Figure_5 stability) + Figures_SI.zip (4 opju)",
    confidence=0.4,
)

R["10802984"] = dict(
    modality="Transmission FTIR (KBr pellets) and 57Fe Mössbauer spectroscopy of schwertmannite after phosphate sorption (+ XRD, SEM, sorption kinetics/isotherms)",
    spectral_range_original_min=300.874, spectral_range_original_max=4499.611, spectral_range_original_unit="cm-1",
    num_spectral_channels=2178, spectral_resolution=1, spectral_resolution_unit="cm-1 (32 scans)",
    sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=10,  # synthetic schwertmannite + equilibrations at pH 3/6/8 with 0-high P loads
    num_spectra=48,  # ~39 FTIR spectra in figure CSVs (raw, normalised, subtracted) + 9 Mossbauer spectra (6 at 77 K, 3 temperatures)
    num_spectral_values=56810,  # FTIR 2,178- and 467-point traces + 9 x 512 Mossbauer channels
    spectral_target_relationship="FTIR sulfate (nu3 ~1100-1200, nu1 ~980 cm-1) and phosphate (900-1200 cm-1) bands with Gaussian deconvolution of difference spectra -> outer- vs inner-sphere sulfate release and mono/bidentate phosphate coordination; Mossbauer (77/40/30 K) doublets/sextets -> Fe phases and proto-transformation of schwertmannite; sulfate release vs phosphate uptake (ligand exchange) across pH 3-8",
    source_file="10802984.pdf (As et al. 2024 Chem. Geol. 653:122043); Data_Figures_and_Tables.zip (per-figure CSV/XLSX + TIFF, Main_Text Fig1-10, SI1-8); Figures_TIFF_Files.zip",
    confidence=0.8,
)

R["10814421"] = dict(
    modality="UV-Vis total and diffuse transmittance (integrating sphere) for transmittance/haze of leek-replica cellulose acetate films (+ J-V of perovskite cells, light-scattering profiles)",
    spectral_range_original_min=300, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=501, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=9,  # plain CA, replica 2/5/10 % CA, replica + 0.5/1/2/3 % carnauba wax, replica+2 % CW after 10 d solar simulator
    num_spectra=68,  # T1 (reference), T2 x3 (total), T3 (device scatter), T4 x3 (diffuse) per sample type
    num_spectral_values=68 * 501,
    spectral_target_relationship="T1-T4 transmission spectra -> total transmittance (T2/T1) and haze ((T4/T2 - T3/T1) x 100) of bio-inspired anisotropic superhydrophobic CA films (~94 % T, ~54 % haze at 550 nm); light-management coating effect on perovskite solar-cell J-V",
    source_file="10814421.pdf (Vapaavuori, Daghigh Shirazi et al. Research Square preprint rs-3375082, published Commun. Mater. 2024); Read me.txt; 9 'UV-Vis - <sample>.zip' (T*.txt), J-V and light-scattering txt files",
    confidence=0.85,
)

R["10866787"] = dict(
    modality="FTIR spectroscopy (Bruker Alpha II, DLATGS) of SBS polymer-modified bitumen aged by modified thin-film oven test (+ DSR rheology, penetration/softening point)",
    spectral_range_original_min=598.368, spectral_range_original_max=3997.348, spectral_range_original_unit="cm-1",
    num_spectral_channels=1654, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=2.056, sampling_interval_unit="cm-1",
    num_samples=26,  # unaged + 25 ageing conditions (1-5 h x 120-200 C)
    num_spectra=26, num_spectral_values=26 * 1654,
    spectral_target_relationship="Band areas -> ageing indices (aliphatic 1350-1510, aromatic 1535-1625, carbonyl 1678-1725, sulfoxide 1010-1043 cm-1 over sum of areas) and butadiene/styrene index A966/A699 -> oxidation and SBS degradation vs TFOT time/temperature; correlated with DSR complex modulus / phase angle",
    source_file="10866787.pdf (Farid & Król 2023 Roads and Bridges 22:379-386); 'OPUS Spectroscopy files.zip' (26 Bruker OPUS binaries <t>h_<T>C.2 + Unaged.2); 01 - SP Pen.csv; 02.x - DSR Rheology_*.csv",
    confidence=0.8,
)

R["10911316"] = dict(
    modality="UV-Vis-NIR absorption spectroscopy of n-doped P(NDI2OD-T2) thin films (+ XPS, photoelectron yield spectroscopy, GIWAXS)",
    spectral_range_original_min=350, spectral_range_original_max=1600, spectral_range_original_unit="nm",
    num_spectral_channels=1251, sampling_interval=1, sampling_interval_unit="nm (Fig1; Fig4 350-1200 nm, 851 points)",
    num_samples=9,  # pristine, CoCp2, CoCp2 + 5 cation-exchange salts (dMesIMCl, TBACl, TBAPF6, TBATFSI, TPPCl); stability: dMesIM, N-DMBI, RuCpMes, TBA, TPP
    num_spectra=23,  # 7 doping spectra (Fig1) + 16 air-stability spectra (Fig4)
    num_spectral_values=7 * 1251 + 16 * 851,
    spectral_target_relationship="Bleaching of neutral ~700 nm band and rise of polaron bands (~800-1600 nm) -> electron-doping efficiency of CoCp2 and cation exchange with closed-shell cations; absorbance vs time in air (0-70 h) -> ambient stability (dMesIM+ most stable); XPS Co 2p/N 1s/P 2p -> cation exchange confirmation; PYS -> ionisation potential",
    source_file="10911316.pdf (Yamashita et al. Research Square preprint rs-3484432, published Commun. Mater. 2024); Fig1-Fig5.zip (CSV per sample; Fig5 GIWAXS line cuts + JPG)",
    confidence=0.85,
)

R["10912482"] = dict(
    modality="Mid-IR micro-FTIR extinction spectroscopy (transmission, Hyperion microscope) of hBN-encapsulated twisted bilayer graphene devices (+ continuum-model optical conductivity, quantum transport)",
    spectral_range_original_min=108.95, spectral_range_original_max=867.49, spectral_range_original_unit="meV",  # photon energy; ~879-6997 cm-1
    num_spectral_channels=4289, spectral_resolution=4, spectral_resolution_unit="cm-1 (600 scans)",
    sampling_interval=0.1769, sampling_interval_unit="meV (~1.43 cm-1)",
    num_samples=7,  # twist angles 0.94, 0.98, 1.12, 1.16, 1.46, 1.67 deg + Bernal bilayer reference
    num_spectra=7, num_spectral_values=4289 * 6 + 3589,  # main extinction spectra (raw + smoothed columns); further spectra in SI folders (A1, A6, A11, A12)
    spectral_target_relationship="Extinction spectra 1 - T_signal/T_reference (hBN/TBG/hBN/graphite vs hBN/hBN/graphite) -> interband transitions between flat and remote superlattice minibands (peaks ~375-510 meV for 0.94-0.98 deg) -> twist angle, bandgaps and continuum-model parameters (vF ~1.05-1.15e6 m/s, u0 80-100, u1 115-130 meV); validated with transport gaps",
    source_file="10912482.pdf (Li et al. arXiv:2404.05716, ICFO); 'TBG_FTIR_original data' folder: per-figure txt (experimental extinction, continuum-model sigma/extinction, separate bands, low-T FTIR, 2nd derivative, device homogeneity, Hall/transport) + peak positions xlsx; 'data information.txt' per folder",
    confidence=0.85,
)

R["10953819"] = dict(
    modality="FTIR (KBr pellet) of clay/antimicrobial nanofillers + powder XRD, TGA and DSC of polycaprolactone/vermiculite nanocomposite films (+ SEM images)",
    spectral_range_original_min=399.1926, spectral_range_original_max=4001.568, spectral_range_original_unit="cm-1",
    num_spectral_channels=1869, spectral_resolution=4, spectral_resolution_unit="cm-1 (64 scans, Happ-Genzel)",
    sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=15,  # 8 nanofillers (VER, ZnOVER, CH, OCT, VER_CH, VER_OCT, ZnOVER_CH, ZnOVER_OCT) + 7 PCL films
    num_spectra=8, num_spectral_values=8 * 1869,
    spectral_target_relationship="FTIR bands of chlorhexidine / octenidine (C=N, aromatic, N-H) appearing in VER and ZnOVER spectra + XRD basal-spacing shift -> intercalation of antimicrobials into vermiculite interlayers; TGA/DSC of PCL films during 5-45 d in simulated body fluid -> thermal stability, crystallinity and hydrolytic degradation",
    source_file="10953819.pdf (Holesova et al. 2024 Polym. Compos. 45:9280-9298, doi:10.1002/pc.28409; also included in dataset); 8 FTIR *.CSV (semicolon, decimal comma), 16 XRD txt, 7 TGA + 28 DSC csv exports, 26 SEM tif, results xlsx, Readme.txt",
    confidence=0.8,
)

R["11091437"] = dict(
    modality="UV-Vis extinction spectroscopy (fibre-optic spectrometer, 1 mm quartz cuvette) of colloidal silver nanoparticles + SEM size distributions for deep-learning inversion",
    spectral_range_original_min=200.289, spectral_range_original_max=900.453, spectral_range_original_unit="nm",
    num_spectral_channels=1206, spectral_resolution=1.4, spectral_resolution_unit="nm",
    sampling_interval=0.58, sampling_interval_unit="nm (0.555-0.602 nm, non-uniform)",
    num_samples=45,  # colloids A1-E6 (30) + F1-F15 (15)
    num_spectra=45, num_spectral_values=45 * 1206,
    spectral_target_relationship="LSPR extinction spectra E(lambda) of seed-mediated Ag colloids -> tandem deep neural network (trained on Mie / modified Maxwell-Garnett-Mie simulated spectra) predicting particle size distribution and mass concentration; validated against SEM radius histograms and measured mass concentrations (batch F)",
    source_file="11091437.pdf (Klinavicius et al., Deep learning methods for colloidal silver nanoparticle concentration and size distribution determination from UV-Vis extinction spectra, manuscript); 6 extinction CSV (batches A-F), 6 SEM size-distribution CSV, mass concentrations batch F, ReadMe.txt",
    confidence=0.85,
)

R["11137126"] = dict(
    modality="NIR diffuse/bidirectional reflectance spectroscopy (Avantes AvaSpec-NIR512) of coal and coal-measure rocks under varied illumination/detection geometry and granularity",
    spectral_range_original_min=1000, spectral_range_original_max=2499, spectral_range_original_unit="nm",
    num_spectral_channels=1500, sampling_interval=1, sampling_interval_unit="nm (resampled)",
    num_samples=24,  # 12 coal ranks + 12 coal-measure rock types, each with up to 11 granularity sub-samples
    num_spectra=10078,
    num_spectral_values=10078 * 1500,
    spectral_target_relationship="NIR reflectance (%) of 24 coal/rock types at varying light-source zenith (10-80 deg), detection zenith/azimuth and granularity (in-situ block to powder) -> coal vs rock identification and coal-rank classification for intelligent mining; supported by XRD minerals, XRF oxides and proximate analysis (Fcad, Vad, Aad, Mad)",
    source_file="11137126.pdf (Lv et al. 2024 Sci. Data 11:628); 'Spectroscopy dataset.tgz' (Spectrum/24 CSV with 6 geometry/granularity header rows; Documentation/24 txt; Picture/24 jpg; Analysis/ICA.csv, XRD.csv, XRF.csv)",
    confidence=0.9,
)

R["11198391"] = dict(
    modality="Mid-IR (FTIR) food spectrographs of wine distributed as a UCR/UEA time-series classification problem",
    num_spectral_channels=234,
    num_samples=111,  # 57 train + 54 test
    num_spectra=111, num_spectral_values=111 * 234,
    spectral_target_relationship="234-point spectra treated as univariate series -> 2-class wine classification benchmark (UCR archive; 1-NN ED error 0.389 reported in archive paper)",
    source_file="11198391.pdf (Dau et al. 2019 The UCR Time Series Archive, arXiv:1810.07758); Wine_TRAIN.ts, Wine_TEST.ts (sktime .ts format, @seriesLength 234, class labels 1/2)",
    confidence=0.6,
)

R["11202938"] = dict(
    modality="None (mechanical spectroscopy): optimally windowed chirp rheometry (piezo sliding-plate and rotational rheometer) of a curing vinylester resin + time-resolved ATR-FTIR conversion (derived)",
    num_samples=1,  # catalysed vinylester resin (plus fumed-silica putty variants)
    spectral_target_relationship="No optical spectra; G'(omega), G''(omega) linear viscoelastic spectra every ~20 s during cure (OWCh-PZR up to ~1000 rad/s) and FTIR-derived methacrylate/styrene double-bond conversion vs time (1397 points) -> gelation and network formation kinetics",
    source_file="11202938.pdf (Athanasiou, Geri, Roose, McKinley & Petekidis, High-frequency optimally windowed chirp rheometry ... crosslinking thermoset, manuscript); 'Chirp Data deposition.xlsx' (16 figure sheets incl. 'Fig 13 FTIR' band areas/conversion)",
    confidence=0.7,
)

R["11204174"] = dict(
    modality="Vis-NIR (PSR+3500, 350-2500 nm) and NIR (NeoSpectra FT-NIR MEMS, 1350-2550 nm) soil absorbance spectra, in-situ and laboratory, + soil laboratory analyses",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",  # PSR; NeoSpectra 1350-2550 nm @2 nm (601 ch)
    num_spectral_channels=2151, spectral_resolution=2.8, spectral_resolution_unit="nm (2.8-8 nm PSR; 16 nm NeoSpectra)",
    sampling_interval=1, sampling_interval_unit="nm (PSR); 2 nm (NeoSpectra)",
    num_samples=134,  # sampling points in 9 Agroscope field trials
    num_spectra=1667,  # 933 PSR + 734 NeoSpectra (each the mean of 5 replicate scans), 7 scan types
    num_spectral_values=933 * 2151 + 734 * 601,
    spectral_target_relationship="Absorbance log(1/R) spectra under 7 scanning conditions (in-situ auger cut, untreated/cleaned/smoothed surface, dried-sieved, finely ground) -> prediction of SOC/OM, clay/silt/sand, pH, N, CEC, carbonate, P/K/Mg/Ca and moisture (ProbeField in-situ vs lab spectroscopy); spectra also supplied with SNV, MSC and Savitzky-Golay pretreatments",
    source_file="11204174.pdf (Schmidinger et al. 2025 Geoderma 459:117337, LimeSoDa benchmark collection - related, includes Swiss vis-NIR data; not the SSL data paper); 00_metadata_Agroscope_SSL.txt, 01_laboratory_analyses.csv, 02_spectraA_psr.csv, 03_spectraA_neo.csv, 04_psr.rds, 05_neo.rds, 06_fields_and_spectrometers.txt",
    confidence=0.8,
)

R["12570844"] = dict(
    modality="ATR-FTIR spectroscopy (diamond, Shimadzu IRPrestige-21) of acetylated and unmodified Scots pine decayed by brown-rot fungi",
    spectral_range_original_min=399.265, spectral_range_original_max=4000.364, spectral_range_original_unit="cm-1",
    num_spectral_channels=1868, spectral_resolution=4, spectral_resolution_unit="cm-1 (50 accumulations)",
    sampling_interval=1.9288, sampling_interval_unit="cm-1",
    num_samples=90,  # ~30 selected decayed samples per type (reference, 9 % WPG, 18 % WPG) x 2 fungi, 3 spectra each
    num_spectra=269,  # unprocessed (90 + 90 + 89); preprocessed 800-1800 cm-1 versions (519 pts) also given
    num_spectral_values=269 * 1868,
    spectral_target_relationship="Acetyl C=O (~1740) and C-O (~1235) bands and carbohydrate/lignin bands (800-1800 cm-1) -> deacetylation and degradation of acetylated wood; PLSR (3 latent variables) of preprocessed spectra vs mass loss per sample type and fungus (Coniophora puteana, Rhodonia placenta); HPLC acetyl content as reference",
    source_file="12570844.pdf (Belt & Awais 2025 Wood Sci. Technol. 59:13, doi:10.1007/s00226-024-01620-8); Unprocessed/Preprocessed FTIR spectra_<reference|9%|18%>.csv, Mass data and acetyl content.csv",
    confidence=0.9,
)

R["8411799"] = dict(
    modality="Diamond ATR-FTIR (Bruker Vertex 70, DTGS) of freeze-dried ectomycorrhizal fungal mycelia grown at three C:N ratios",
    spectral_range_original_min=349.058, spectral_range_original_max=3999.703, spectral_range_original_unit="cm-1",
    num_spectral_channels=1894, spectral_resolution=4, spectral_resolution_unit="cm-1 (200 scans)",
    sampling_interval=1.9285, sampling_interval_unit="cm-1",
    num_samples=57,  # 19 isolates (16 species) x 3 C:N treatments
    num_spectra=111, num_spectral_values=111 * 1894,
    spectral_target_relationship="ATR-corrected, baseline-corrected absorbance spectra (min-subtracted / mean-normalised for statistics) -> mycelial chemical composition (polysaccharides ~1030-1075, proteins amide I/II ~1640/1545, lipids ~2920/1740 cm-1); PCA-CVA and perMANOVA show species effect (R2 = 0.873) and C:N effect (more polysaccharides, less protein at high C)",
    source_file="8411799.pdf (Fransson, Robertson & Campbell 2023 Mycorrhiza 33:303-319, doi:10.1007/s00572-023-01128-2); Fransson_FTIR_C_availability_raw.xlsx (wavenumber + 111 sample columns) + README.md",
    confidence=0.9,
)

R["8420035"] = dict(
    modality="UV-Vis absorbance scans (Tecan Spark 20M plate reader) of Platynereis cryptochrome FAD photoreduction/dark recovery + inline-absorbance SEC (+ cryo-EM, MD simulations)",
    spectral_range_original_min=300, spectral_range_original_max=700, spectral_range_original_unit="nm",
    num_spectral_channels=201, sampling_interval=2, sampling_interval_unit="nm",
    num_samples=4,  # PdLCry WT, monomeric mutant, Y352A, Y352D (+ dimer-interface/CTT/PBL variants in SEC)
    num_spectra=940,  # 93 scan workbooks x ~10 well columns (illumination time series)
    num_spectral_values=188940,
    spectral_target_relationship="FAD absorbance (FADox 450/370 nm ratio ~1.06; semiquinone/anionic radical changes) vs blue/sunlight illumination time and dark recovery -> photoreduction kinetics of WT vs monomer and Y352 mutants; SEC elution -> light-induced dimer-to-monomer transition (inverse photo-oligomerisation)",
    source_file="8420035.pdf (Vu, Behrmann et al. bioRxiv 2023, A marine cryptochrome with an inverse photo-oligomerization mechanism); Fig7CDEF_Absorbance scan/*.xlsx (SparkControl exports), Fig6/Fig7AB/SupFig6 SEC csv, Fig1 sequence tree, 4 NAMD MD simulation folders (pdb/psf/prm/coor/vel)",
    confidence=0.75,
)
