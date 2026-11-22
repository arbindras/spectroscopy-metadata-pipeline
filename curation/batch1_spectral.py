# Batch1 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (C:\Users\Admin\RAG\2\papers\<id>.pdf) + dataset archive (D:\Batch1_datasets).
# Only known keys are given; build_parquet.py fills nulls and derives nm/cm-1 conversions.
R = {}

R["5218787"] = dict(
    modality="FTIR spectroscopy (KBr pellet, transmission) + VIS diffuse reflectance colorimetry (Kubelka-Munk) + XRD",
    spectral_range_original_min=500, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=7,  # untreated + 1/2/5/10/20/30 % NaOH
    spectral_target_relationship="FTIR / K-M reflectance spectra of Moso bamboo surfaces vs NaOH concentration (0-30 %) -> lignin/hemicellulose degradation, colour change, decay susceptibility (descriptive, no prediction model)",
    source_file="5218787.pdf; FTIR_analysis.opj; reflect_spectro.opj; XRD_analysis.opj (Origin projects)",
    confidence=0.6,
)

R["5225156"] = dict(
    modality="None (no spectroscopy): soil chemistry, bulk density and macroinvertebrate survey tables",
    num_samples=90,  # 90 TSBF monoliths (18 sites x 5 points); 453 depth-layer soil-chemistry rows
    spectral_target_relationship="No spectral data; tabular soil fertility (pH, Al, Ca, Mg, K, P, C, ...) and macrofauna density/biomass/morphospecies of Amazonian Dark Earths vs reference soils",
    source_file="5225156.pdf; TPI_dataset_21.07.2021.xlsx",
    confidence=0.9,
)

R["5362675"] = dict(
    modality="Mid-IR FTIR transmission spectroscopy of interstellar ice analogues (+ TPD-QMS)",
    spectral_range_original_min=599.68, spectral_range_original_max=3999.13, spectral_range_original_unit="cm-1",
    num_spectral_channels=7053, sampling_interval=0.48206, sampling_interval_unit="cm-1",
    num_samples=29,  # 29 experiments (CO:NH3, CO:CH4 mixtures, blanks), 10-24 K
    num_spectra=565, num_spectral_values=3829320,
    spectral_target_relationship="IR absorbance spectra of VUV-irradiated CO:NH3 / CO:CH4 ices vs fluence and TPD temperature -> photoproduct (NH2CHO, CH3CHO) column densities and radical conversion yields (band integration)",
    source_file="5362675.pdf; 29 Exp*_*.zip (Exp*_IR*.txt two-column spectra, *_TPD_QMS.asc)",
    confidence=0.9,
)

# ExoMol / MoLLIST / Barton diatomic line lists (paper: Tennyson et al. 2020, ExoMol 2020 release)
_XS = dict(  # ExoMolOP TauREx cross sections, 22 pressures x 27 temperatures, R=15000 on 0.3-50 um
    spectral_range_original_min=0.3, spectral_range_original_max=50, spectral_range_original_unit="um",
    num_spectral_channels=76743, spectral_resolution=15000, spectral_resolution_unit="R (lambda/dlambda), TauREx cross sections; k-tables R=1000",
    num_spectra=594, num_spectral_values=594 * 76743,
)


def _exomol(rid, iso, dsname, nstates, ntrans, numin, numax, tmax, xs, files, extra=""):
    r = dict(
        modality=f"Computed/empirical molecular line list (ExoMol {dsname}) for {iso}: rovibrational(-electronic) transitions" + (" + ExoMolOP opacity cross sections/k-tables" if xs else ""),
        num_samples=1,
        spectral_target_relationship=f"Line list for {iso} ({nstates} states, {ntrans} transitions, {numin}-{numax} cm-1, T up to {tmax} K) -> forward modelling of hot (exo)planet / brown-dwarf / stellar atmosphere spectra; partition function Q(T){extra}",
        source_file=f"5362925.pdf (ExoMol 2020 release paper); {files}",
        confidence=0.9,
    )
    if xs:
        r.update(_XS)
    else:
        # no gridded spectra: range = line positions, values = number of transitions
        r.update(spectral_range_original_min=numin, spectral_range_original_max=numax, spectral_range_original_unit="cm-1",
                 num_spectral_values=ntrans)
    R[rid] = r


_exomol("5362925", "40Ca1H", "MoLLIST", 1771, 19095, 722.37, 21931.76, 3000, True,
        "40Ca-1H__MoLLIST.states.bz2/.trans.bz2/.pf/.def; *.xsec.TauREx.h5; *.ktable.petitRADTRANS.h5/.NEMESIS.kta/.ARCiS.fits.gz", "; X-X, A-X, B-X, E-X band systems")
_exomol("5716977", "39K35Cl", "Barton", 60741, 1326765, 0.12, 2927.25, 3000, True,
        "39K-35Cl__Barton.states.bz2/.trans.bz2/.pf/.def; *.xsec.TauREx.h5; *.ktable.*")
_exomol("5716979", "39K37Cl", "Barton", 60741, 1326765, 0.11, 2887.38, 3000, False,
        "39K-37Cl__Barton.states.bz2/.trans.bz2/.pf/.def")
_exomol("5716981", "41K35Cl", "Barton", 60741, 1326765, 0.11, 2894.99, 3000, False,
        "41K-35Cl__Barton.states.bz2/.trans.bz2/.pf/.def")
_exomol("5716983", "41K37Cl", "Barton", 60741, 1326765, 0.11, 2854.60, 3000, False,
        "41K-37Cl__Barton.states.bz2/.trans.bz2/.pf/.def")
_exomol("5716985", "39K19F", "MoLLIST", 1065, 10572, 0.51, 4007.10, 5000, True,
        "39K-19F__MoLLIST.states.bz2/.trans.bz2/.pf/.def; *.xsec.TauREx.h5; *.ktable.*")
_exomol("5717023", "23Na35Cl", "Barton", 48937, 702271, 0.0008, 2457.77, 3000, True,
        "23Na-35Cl__Barton.states.bz2/.trans.bz2/.pf/.def; *.xsec.TauREx.h5; *.ktable.*")
_exomol("5717025", "23Na37Cl", "Barton", 49550, 711120, 0.0026, 2432.30, 3000, False,
        "23Na-37Cl__Barton.states.bz2/.trans.bz2/.pf/.def")
_exomol("5717027", "23Na19F", "MoLLIST", 839, 7884, 0.79, 4987.67, 5000, True,
        "23Na-19F__MoLLIST.states.bz2/.trans.bz2/.pf/.def; *.xsec.TauREx.h5; *.ktable.*")

R["5484203"] = dict(
    modality="FTIR transmission spectroscopy (KBr) + X-ray Raman scattering (C and O K-edge XRS, energy-loss XANES)",
    spectral_range_original_min=399.675, spectral_range_original_max=4000.12, spectral_range_original_unit="cm-1",
    num_spectral_channels=7469, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=10,  # 10 historical plant exudates (Xanthorrhoea x3, Callitris x3, Eucalyptus x2, Acacia x2)
    num_spectra=10, num_spectral_values=74690,  # FTIR only; + 9 C K-edge and 14 O K-edge XRS spectra (7457 values)
    spectral_target_relationship="FTIR + XRS spectra of Australian plant exudates (resins, kinos, gums) -> functional-group speciation and genus classification (terpenoid/aromatic/phenolic/polysaccharide) via Gaussian decomposition + Fisher LDA with combinatorial significance test",
    source_file="5484203.pdf; FT-IR.zip (FTIR/*.CSV); XRS C K-edge.zip; XRS O K-edge.zip (SLAC, SOLEIL); GC-MS.zip; ICP-MS.zip",
    confidence=0.85,
)

R["5552430"] = dict(
    modality="CW and pulse X-band EPR spectroscopy + UV-Vis absorption spectroscopy (ferric myoglobin)",
    spectral_range_original_min=250, spectral_range_original_max=700, spectral_range_original_unit="nm",  # UV-Vis; EPR 50-500 mT field sweeps
    num_spectral_channels=451, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=21,  # Mb in 5 alkaline buffers (+HEPES pH7) x {none, glycerol, ethylene glycol, sucrose, trehalose}
    num_spectra=26,  # UV-Vis spectra (EPR: ~25 CW spectra of 1024 field points + 8 two-pulse echo decays)
    num_spectral_values=26 * 451,
    spectral_target_relationship="EPR (g values, HS/LS ratio, linewidth, Tm) and UV-Vis (Soret/Q-band positions) of myoglobin vs buffer/cryoprotectant combination -> alkaline transition (OH- ligation, pKa ~8.9) and pH shifts on freezing; EasySpin simulations",
    source_file="5552430.pdf; PARACAT_WP3_20210929.zip (01_CW *.mat + EasySpin *.m; 02_PULSE *.DSC/*.DTA; 03_UV-VIS *.ods/*.mat)",
    confidence=0.85,
)

R["5564539"] = dict(
    modality="Far- and mid-IR FTIR absorption spectroscopy (diamond anvil cell thin films) of pyroxene minerals",
    spectral_range_original_min=80.04, spectral_range_original_max=1200, spectral_range_original_unit="cm-1",
    num_spectral_channels=2323, spectral_resolution=2, spectral_resolution_unit="cm-1 (1-2 cm-1)",
    sampling_interval=0.48, sampling_interval_unit="cm-1 (varies 0.43-0.49 between files)",
    num_samples=18, num_spectra=18, num_spectral_values=41090,
    spectral_target_relationship="IR optical-depth spectra (tau per um) of 17 Mg-Fe-Ca ortho/clinopyroxenes + wollastonite -> peak-position trends vs composition (Wo/En/Fs) and crystal structure for astronomical silicate dust identification (JWST MIRI, SPICA)",
    source_file="5564539.pdf; *tau.dat (18 two-column ASCII); README.txt; orthoplot.pdf; enst-wol.pdf",
    confidence=0.95,
)

R["5572818"] = dict(
    modality="Time-resolved (rapid-scan) FTIR difference spectroscopy + UV-Vis of rhodopsin guanylyl cyclase (light minus dark, NPE-GTP photolysis)",
    spectral_range_original_min=899.675, spectral_range_original_max=1850.32, spectral_range_original_unit="cm-1",
    num_spectral_channels=1635, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.6, sampling_interval_unit="cm-1 (0.55-1.10 between files)",
    num_samples=3,  # CaRGC (full-length/C259S), isolated GC domain, reference compounds (GTP, cGMP, PP)
    num_spectra=9, num_spectral_values=12046,  # 9 spectra; + 5 kinetic traces (marker-band absorbance vs time)
    spectral_target_relationship="FTIR difference spectra and marker-band kinetics -> photocycle intermediates (L, M) and GTP->cGMP + pyrophosphate turnover in light-activated RGC vs GC domain; assignment via global fit / SVD (descriptive)",
    source_file="5572818.pdf; Figure_4D/4F/5A/5B *.dpt spectra; Figure_4E/4G *.dpt kinetic traces; Appendix_5 *.pdb homology models; README.txt",
    confidence=0.85,
)


R["5713544"] = dict(
    modality="UV-Vis absorbance spectroscopy (submersible spectrophotometer) of suspended soil-sediment mixtures",
    spectral_range_original_min=200, spectral_range_original_max=730, spectral_range_original_unit="nm",
    num_spectral_channels=213, sampling_interval=2.5, sampling_interval_unit="nm",
    num_samples=42,  # 17 size-fractionated soil samples + 25 artificial mixtures, each at 10 concentrations (100-1000 mg/L)
    num_spectra=1934,  # rows 4-1937 of worksheet (dimension A1:HF1937); archive incomplete, ~40 % of sheet recoverable
    num_spectral_values=1934 * 213,
    spectral_target_relationship="UV-Vis absorbance (213 wavelengths as tracers) of suspended sediment -> soil source proportions in artificial mixtures (MixSIAR Bayesian un-mixing; MAE 12.9-17.0 %), plus concentration and particle-size effects",
    source_file="5713544.pdf; SPECTRAS_absorbance data_raw.xlsx (archive truncated: only first ~195 KB of 5.78 MB present, rest zero-filled)",
    confidence=0.6,
)

R["5713846"] = dict(
    modality="Continuous-wave spatially resolved NIRS tissue oximetry (2 wavelengths: 760, 850 nm) - derived parameters only",
    spectral_range_original_min=760, spectral_range_original_max=850, spectral_range_original_unit="nm",
    num_spectral_channels=2,
    num_samples=105,  # 32 healthy volunteers + 73 COVID-19 patients
    spectral_target_relationship="NIRS-derived StO2, THC and vascular-occlusion-test slopes (DeO2, ReO2, hyperemia AUC) -> COVID-19 vs healthy and ARDS severity (SpO2/FiO2 ratio); correlation + multiple linear regression; no spectra/time series in dataset",
    source_file="5713846.pdf; dataset_PAPER_CRIT_CARE_zenodo.zip (table_jaume.xlsx, ESICM 2021.xls, table_matlab.mat, plots_paper.m, figure PDFs/PNGs)",
    confidence=0.85,
)

R["5721518"] = dict(
    modality="Long-path in-situ gas-phase FTIR absorption spectroscopy (simulation chamber, White multipass cell)",
    spectral_range_original_min=399.92, spectral_range_original_max=4000.19, spectral_range_original_unit="cm-1",
    num_spectral_channels=14936, spectral_resolution=0.25, spectral_resolution_unit="cm-1",
    sampling_interval=0.2411, sampling_interval_unit="cm-1",
    num_samples=15,  # 15 experiment days (relative-rate runs, 7 target VOCs + 7 reference compounds)
    num_spectra=2207,  # 2194 time-series spectra + 13 reference spectra
    num_spectral_values=2207 * 14936,
    spectral_target_relationship="Time series of chamber FTIR spectra -> VOC concentration-time profiles (ANIR least-squares fitting to reference spectra) -> relative-rate NO3 rate coefficients of furans, furanones and pyrrole",
    source_file="5721518.pdf; ACP_Newland_Furans+NO3_2021.zip (<date>/NNNN.CSV raw spectra; Reference Spectra/*.CSV; README .rtf)",
    confidence=0.9,
)

R["5724967"] = dict(
    modality="Derived from long-path gas-phase FTIR (chamber): VOC response-time profiles and fit residuals (no spectra)",
    spectral_range_original_min=399.92, spectral_range_original_max=4000.19, spectral_range_original_unit="cm-1",  # source spectra; analysis windows e.g. 723-760, 770-785, 939-952 cm-1
    spectral_resolution=0.25, spectral_resolution_unit="cm-1",
    num_samples=15,
    spectral_target_relationship="ANIR-derived concentration-time profiles of target and reference VOCs (fitted in specific IR band windows) -> relative-rate plots ln([VOC]0/[VOC]t) vs ln([ref]0/[ref]t) -> k(NO3)",
    source_file="5724967.pdf (same paper as 5721518); ACP_Newland_Furans+NO3_2021_b.zip (54 <date>/<date>-<compound>.txt profiles; README .rtf)",
    confidence=0.85,
)

R["5733169"] = dict(
    modality="Mid-IR FTIR transmission of PTFE aerosol filters - PLS-predicted concentrations only (no spectra in dataset)",
    spectral_range_original_min=420, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=74892,  # filter samples 2015-2018 (IMPROVE network); 61,462 valid spectra used in paper for 2015-2017
    spectral_target_relationship="FTIR spectra of PM2.5 on PTFE filters -> PLS (multilevel calibration, 21 calibration sites) predictions of OC, EC, HIPS BC, SO4, NO3, Si, Al, Ca, Fe, Ti and PM2.5 mass vs TOR/IC/XRF/gravimetric references (R2 > 0.9 for most species)",
    source_file="5733169.pdf; FTIR_and_IMPROVE_data_for_2015_thru_2017_{carbon,ions,elements_and_mass}.xlsx; ReadMe.docx",
    confidence=0.85,
)

R["5736579"] = dict(
    modality="Time-resolved UV-Vis absorption spectroscopy (diode array) - competition kinetics with fluorescein boronate probe",
    spectral_range_original_min=190, spectral_range_original_max=1100, spectral_range_original_unit="nm",
    num_spectral_channels=911, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=13,  # 13 cyclic C-nucleophiles (each at 0-5 mM, 3 series)
    num_spectra=3685,  # 305 kinetic files x 10-15 time points
    num_spectral_values=3685 * 911,
    spectral_target_relationship="UV-Vis spectra vs time (fluorescein build-up at 490 nm, FlBA decay at 378 nm) at varying scavenger concentration -> initial rates -> (v0/vi)-1 vs [S]/[O2] -> second-order rate constants of HNO with C-nucleophiles (33-20,000 M-1 s-1)",
    source_file="5736579.pdf; 305 Agilent 8453 kinetic exports '<compound> <conc>, 25 uM FLBA, 20 uM Angelis salt, 50 mM PB (pH 7.4), 100 uM dtpa_series N.TXT'; AtomicCoordinatesOfStationaryPoints.txt",
    confidence=0.9,
)

R["5793207"] = dict(
    modality="UV-Vis-NIR absorption cross-section spectroscopy of gaseous ozone (echelle + Fourier transform spectrometers), temperature-dependent",
    spectral_range_original_min=213.33, spectral_range_original_max=1100, spectral_range_original_unit="nm",
    num_spectral_channels=88668, spectral_resolution=0.02, spectral_resolution_unit="nm (0.02-0.06 nm UV-Vis; 0.12-0.24 nm NIR; 1-2 cm-1 FTS regions)",
    sampling_interval=0.01, sampling_interval_unit="nm (interpolated grid)",
    num_samples=11,  # 11 temperatures 193-293 K
    num_spectra=11, num_spectral_values=11 * 88668,
    spectral_target_relationship="Absolute O3 absorption cross-sections (cm2/molecule) at 11 temperatures -> reference data for ozone remote-sensing retrievals (Hartley, Huggins, Chappuis, Wulf bands); temperature dependence",
    source_file="5793207.pdf; SerdyuchenkoGorshelev5digits_latest.dat (45 header lines; wavelength + 11 temperature columns)",
    confidence=0.95,
)

R["5801251"] = dict(
    modality="Hyperspectral reflectance imaging (push-broom VNIR + SWIR) of a lake sediment core",
    spectral_range_original_min=397.33, spectral_range_original_max=2574.07, spectral_range_original_unit="nm",
    num_spectral_channels=242,  # VNIR 98 bands (397-1007 nm) + SWIR 144 bands (969-2574 nm)
    num_samples=1,  # core LDB17_P11Ax (Lake Le Bourget); paper also uses Allos and Geneva cores (not in this record)
    num_images=2, num_pixels=1312 * 20073 + 384 * 5904,
    num_spectral_values=1312 * 20073 * 98 + 384 * 5904 * 144,
    image_height=20073, image_width=1312,  # VNIR cube; SWIR cube 5904 x 384
    spatial_resolution=60, spatial_resolution_unit="um (VNIR 60 um; SWIR 200 um)",
    spectral_target_relationship="Per-pixel VNIR/SWIR reflectance spectra -> supervised classification of event layers (floods) vs continuous sedimentation (LDA, QDA, PLS-DA, ANN, RF, DT; 8 pre-processings), accuracies >0.8-0.9",
    source_file="5801251.pdf; swir_LDB17_P11Ax_2018-10-02_10-22-36.zip; vnir_LDB17_P11Ax_2018-10-04_10-02-02.zip (ENVI *_refl.dat/.hdr reflectance cubes, raw capture + DARKREF/WHITEREF, ROI.txt, Metadata_*.xlsx)",
    confidence=0.9,
)

R["5848870"] = dict(
    modality="ATR-FTIR spectroscopy of microplastics - polymer identification results only (no spectra in dataset)",
    spectral_range_original_min=600, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=54,  # 54 Tara Mediterranean manta-net stations (15,654 particles; statistically drawn subset analysed)
    spectral_target_relationship="ATR-FTIR spectra of individual microplastic particles -> polymer type (PE, PP, PS, EVA, PA, PVC, ...) via POSEIDON machine-learning identification; dataset holds per-station polymer proportions by size class",
    source_file="5848870.pdf; TaraMed plastic characteristics.xlsx (readme, METADATA_TARA_MED_VLFR, polymer proportions)",
    confidence=0.85,
)

R["5853516"] = dict(
    modality="Satellite multispectral surface reflectance (Landsat 8 OLI, 7 VNIR-SWIR bands) at field points",
    spectral_range_original_min=433, spectral_range_original_max=2294, spectral_range_original_unit="nm",  # OLI band 1 (433-453) to band 7 (2107-2294)
    num_spectral_channels=7,
    num_samples=49,  # 41 field salinity points (Nguyen et al. 2020) + 8 random pond pixels; + 20 freshwater pond pixels in grids
    num_spectra=49, num_spectral_values=49 * 7,
    spatial_resolution=30, spatial_resolution_unit="m (Landsat pixel)",
    spectral_target_relationship="Landsat 8 NIR (band 5) reflectance and VSSI of mixed water/land pixels -> water percentage cover (significant linear correlation) vs soil EC1:5 salinity (no significant correlation); comment on Nguyen et al. 2020",
    source_file="5853516.pdf; Stats_analyses_Comment_Silvestri-et-al.xlsx (Salinity-data, L8-Collect2-L2, water-land-mix sheets); Grids-and-points_KMLformat.zip (60 KML grids/points)",
    confidence=0.8,
)

R["5963908"] = dict(
    modality="Micro-FTIR transmission imaging (FPA/MCT array) of microplastics on stainless-steel mesh filters",
    spectral_range_original_min=713.56, spectral_range_original_max=3999.81, spectral_range_original_unit="cm-1",
    num_spectral_channels=853, spectral_resolution=8, spectral_resolution_unit="cm-1",
    sampling_interval=3.857, sampling_interval_unit="cm-1",
    num_samples=3,  # VMPS25 PE-bead standard + 2 Las Vegas Wash filters (LVW04, LVW05)
    num_spectra=145, num_spectral_values=145 * 853,  # 139 particle-pixel spectra + 6 PE-bead spectra
    spatial_resolution=25, spatial_resolution_unit="um (aperture and step)",
    spectral_target_relationship="Per-pixel micro-FTIR absorbance spectra of particles -> polymer type (siMPle library matching), particle dimensions; validation of peristaltic-pump/filter microplastic sampling method",
    source_file="5963908 dataset (paper PDF in papers folder is a different article); LVW04_results.xlsx; LVW05_results.xlsx; VMPS_output.xls; README_Harrold.txt",
    confidence=0.7,
)

R["6092729"] = dict(
    modality="UV-Vis absorbance of filtered river water (CDOM) - derived absorption coefficients only (a254, a412)",
    spectral_range_original_min=239, spectral_range_original_max=800, spectral_range_original_unit="nm",  # measured range; dataset holds 254 and 412 nm coefficients
    num_spectral_channels=2, sampling_interval=3, sampling_interval_unit="nm (instrument scan increment)",
    num_samples=156,  # 149 Connecticut River mainstem samples (5 sites, bi-weekly 2018-2020) + 7 tributary sites (Aug 2019)
    spectral_target_relationship="Decadic absorption coefficients a254/a412 and SUVA254 of size-fractionated DOM (<0.22, <0.02, 0.02-0.22 um) vs Fe(III) and DOC -> Fe(III) contribution to UV-Vis absorbance (multiple linear regression; overestimation up to 53 %)",
    source_file="6092729.pdf; lauralogozzo/bgc-2022-data-v1.zip (CRW-Fe3-CDOM-Data.xlsx: Metadata, Site Information, CT River Mainstem Data, CT Watershed Tributary Data; README.md)",
    confidence=0.85,
)

R["6265716"] = dict(
    modality="Unpolarized micro-FTIR absorption spectroscopy (OH stretching) of wadsleyite single crystals (+ NanoSIMS depth profiles)",
    spectral_range_original_min=1000.9, spectral_range_original_max=5000.5, spectral_range_original_unit="cm-1",
    num_spectral_channels=2075, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=21,  # recovered diffusion-run samples (run numbers 1514-1906)
    num_spectra=55, num_spectral_values=86671,
    spectral_target_relationship="FTIR OH-band absorbance (3000-4000 cm-1 integrated, Beer-Lambert, eps=69,000 L mol-1 cm-2) -> H2O content (10-5300 wt ppm) of wadsleyite -> H2O-content exponent (0.8) of Si self-diffusion from NanoSIMS 29Si profiles",
    source_file="6265716.pdf; FTIR data.zip (55 *.txt spectra + thickness.xlsx); SIMS data.zip (52 *_Si28/_Si29.csv depth profiles + crater depth.xlsx)",
    confidence=0.9,
)

R["6323475"] = dict(
    modality="UV-Vis absorption + photoluminescence spectroscopy (solution), with 1H/13C/31P NMR (JCAMP-DX), cyclic voltammetry and DFT outputs",
    spectral_range_original_min=199.99, spectral_range_original_max=1000, spectral_range_original_unit="nm",
    num_spectral_channels=1301, sampling_interval=0.5, sampling_interval_unit="nm (UV-Vis; PL 1 nm)",
    num_samples=4,  # PCT, O-PCT, S-PCT macrocycles + quinine reference (+ synthesis intermediates for NMR)
    num_spectra=9, num_spectral_values=7393,  # 4 UV-Vis + 5 PL spectra; + 16 NMR .dx spectra, 12 CV curves
    spectral_target_relationship="UV-Vis/PL spectra of methoxy-/methylthio-substituted [2.2.2.2]paracyclophanetetraenes -> absorption/emission maxima, Stokes shift (>1.5 eV), relative PL quantum yield vs quinine; combined with CV redox potentials and VIST/NICS (anti)aromaticity calculations (descriptive)",
    source_file="6323475.pdf; Research data_v2.zip (<compound>/Experimental/*_UV-vis absorption.csv, *_Photoluminescence.csv, *-NMR_*.dx, *_Cyclic voltammetry_*.csv, *_HRMS.pdf; Computational/ Q-Chem/Gaussian outputs)",
    confidence=0.85,
)

R["6417982"] = dict(
    modality="FTIR micro-spectroscopic imaging (focal plane array) of human brain tissue sections - pre-processed absorbance",
    spectral_range_original_min=950.78, spectral_range_original_max=3049.06, spectral_range_original_unit="cm-1",
    num_spectral_channels=1089, sampling_interval=1.9286, sampling_interval_unit="cm-1",
    num_samples=6,  # 3 control + 3 multiple-sclerosis case areas (MS352 L1/L2, MS425)
    num_spectra=90112, num_images=6, num_pixels=90112, num_spectral_values=90112 * 1089,
    spectral_target_relationship="Spatially resolved FTIR pixel spectra of MS vs control brain sections -> PCA, UMAP + Leiden clustering, band integration (lipid/protein, secondary structure estimates) and biochemical mapping with Photizo library (example/reference dataset)",
    source_file="6417982.pdf; 6 *_pre-processed_{nobinning,4x4}.txt (col 1 wavenumber, other columns pixel spectra); Clin_data.csv",
    confidence=0.8,
)

R["6430605"] = dict(
    modality="FTIR transmission spectroscopy (KBr IR cards) of asphalt binders, with rheology/chemistry tables",
    spectral_range_original_min=400.17, spectral_range_original_max=3999.81, spectral_range_original_unit="cm-1",
    num_spectral_channels=7467, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=30,  # 2 sources x 3 PG grades (64-22, 70-22, 76-22) x 5 (control + 4 WMA additives)
    num_spectra=30, num_spectral_values=30 * 7467,
    spectral_target_relationship="FTIR absorbance of unaged PG binders with/without warm-mix additives (Sasobit, Advera, Evotherm, Rediset) -> qualitative functional-group changes (C-O, O-H, C-H), alongside SARA, DSR/MSCR/BBR rheology and moisture-susceptibility tests",
    source_file="6430605.pdf; 20BASU24_Data sheet v2.xlsx (sheets Penetration, RV data, Unaged_DSR, PAV aged_DSR, MSCR, BBR, SARA, FTIR, Optical Contact Angle, Texas Boiling Test)",
    confidence=0.85,
)

R["6484941"] = dict(
    modality="Spectrofluorimetry (fluorescence quenching of S,N-co-doped carbon quantum dots) - calibration data only",
    spectral_range_original_min=360, spectral_range_original_max=430, spectral_range_original_unit="nm",  # lambda_ex 360 nm / lambda_em 430 nm (paper); dataset: single-wavelength responses
    num_spectral_channels=1,
    num_samples=2,  # saxagliptin and gliclazide calibration series (~8 concentrations each)
    spectral_target_relationship="SN-CQD fluorescence response (quenching at 430 nm) vs drug concentration (uM) -> linear calibration, found/% recovery for saxagliptin (SXG) and gliclazide (GLZ)",
    source_file="6484941.pdf (sibling paper on rifampicin/nitroimidazoles by same group); Calibration_data_SXG.xlsx; Calibration_data_GLZ.xlsx; README_File.docx",
    confidence=0.55,
)

R["6511882"] = dict(
    modality="None (no spectra): shipboard interstitial-water chemistry (ICP-AES emission-line concentrations, ion chromatography, alkalinity)",
    num_samples=85,  # IW samples, Holes U1517B (2) and U1517C (83)
    spectral_target_relationship="No spectral data; IW element/ion concentrations (Ba 493.408 nm, B 249.678 nm ICP-AES lines, Br, Ca, Cl, SO4, NH4, alkalinity, ...) vs depth at IODP Site U1517 (gas hydrate / Tuaheni landslide)",
    source_file="6511882.pdf (Expedition 372A summary); IWREPORT.zip (data_by_hole/372-U1517B-IWREPORT.csv, 372-U1517C-IWREPORT.csv); IWREPORT-README.txt",
    confidence=0.85,
)

R["6512070"] = dict(
    modality="VIS diffuse reflectance spectroscopy and colorimetry of split sediment cores (SHMSL, integrating sphere)",
    spectral_range_original_min=390, spectral_range_original_max=730, spectral_range_original_unit="nm",
    num_spectral_channels=171, sampling_interval=2, sampling_interval_unit="nm",
    num_samples=1,  # Hole U1517C core (36 cores, ~188 m)
    num_spectra=15750, num_spectral_values=15750 * 171,
    spatial_resolution=1, spatial_resolution_unit="cm (downcore measurement spacing)",
    spectral_target_relationship="Percent reflectance spectra -> CIE L*a*b*, XYZ tristimulus colour vs depth -> lithostratigraphic characterisation of Site U1517 sediments (Tuaheni Landslide Complex)",
    source_file="6512070.pdf (Expedition 372A summary); RSC.zip (data_by_hole/372-U1517C-RSC.csv; supplementary_material/raw_data_files/*-norm_*_rsc.csv percent-reflectance spectra; configuration .ini; standards); RSC-README.txt",
    confidence=0.85,
)

R["6534038"] = dict(
    modality="Synchrotron infrared nano-spectroscopy (SINS, s-SNOM + FTIR) of lunar soil grain lift-outs - near-field amplitude and phase spectra",
    spectral_range_original_min=700, spectral_range_original_max=5000, spectral_range_original_unit="cm-1",  # raw; analysis 700-1500 (processed files 700-2000)
    num_spectral_channels=8920, spectral_resolution=8, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=5,  # 3 sections of Apollo 17 soil 79221, 1 of Apollo 11 soil 10084, terrestrial anorthite standard
    num_spectra=385,  # line-scan points (16 line scans); each with raw, referenced amplitude, phase and fit spectra
    num_spectral_values=385 * 2 * 2697,  # processed amplitude + phase (700-2000 cm-1)
    spatial_resolution=25, spatial_resolution_unit="nm (AFM tip radius; 20-100 nm point spacing)",
    spectral_target_relationship="Depth-resolved near-field phase/amplitude spectra across space-weathered rims -> shifts of Si-O bands and Christiansen feature vs depth (0-500 nm) linking npFe / amorphization to mid-IR space-weathering effects; peak fitting",
    source_file="6534038.pdf; DataSetS1.zip (raw CSV), DataSetS2.zip (referenced Amp/Phase CSV), DataSetS3.zip (fit initial conditions/results), DataSetS4/S5 (GIF/PNG), DataSetS6.zip (fits); readme .txt",
    confidence=0.85,
)

R["6554718"] = dict(
    modality="UV-Vis transmission spectroscopy of WO3 electrochromic devices (+ cyclic voltammetry, chronoamperometry)",
    spectral_range_original_min=199.94, spectral_range_original_max=899.56, spectral_range_original_unit="nm",
    num_spectral_channels=1198, sampling_interval=0.6, sampling_interval_unit="nm",
    num_samples=2,  # solid (PMMA gel) vs liquid polymer electrolyte ECDs
    num_spectra=6, num_spectral_values=6 * 1198,  # original / coloured / bleached x 2 devices
    spectral_target_relationship="Transmittance spectra in original, coloured (-3 V) and bleached (+3 V) states -> optical modulation (16 % SECD vs 21 % LECD at 633 nm) and colouration efficiency; with CV-derived Li+ diffusion coefficients",
    source_file="6554718.pdf; F1000_SECD_Transmittance.xlsx; F1000_LECD_Transmittance.xlsx; F1000_CV_SECD.xlsx; F1000_CV_LECD.xlsx; README_file.txt",
    confidence=0.85,
)

R["6616006"] = dict(
    modality="Hyperspectral SWIR/NIR reflectance imaging (push-broom) of brown-rot decayed Scots pine sapwood",
    spectral_range_original_min=930, spectral_range_original_max=2550, spectral_range_original_unit="nm",
    num_spectral_channels=288, spectral_resolution=12, spectral_resolution_unit="nm (FWHM)",
    sampling_interval=5.6, sampling_interval_unit="nm (approx. band spacing)",
    num_samples=70,  # 2 fungi x 5 tubes x 7 stacked positions
    num_images=70, num_pixels=70 * 384 * 551, num_spectral_values=70 * 384 * 551 * 288,
    image_height=551, image_width=384,
    spatial_resolution=26, spatial_resolution_unit="um (nominal pixel 26 x 26 um)",
    spectral_target_relationship="Pixel NIR spectra of wood at successive decay stages -> mass loss (-3.9 to 57 %) and chemical changes (cellulose degradation, lignin aromatic/carbonyl increase) via ASCA, PCA and k-means clustering; earlywood vs latewood degradation patterns",
    source_file="6616006.pdf; C puteana.mat; R placenta.mat (MATLAB v7.3/HDF5, 35 cubes each of 551 x 384 x 288); Samples IDs and mass losses.csv",
    confidence=0.9,
)

R["6641623"] = dict(
    modality="High-resolution near-IR echelle spectroscopy (astronomical, VLT/CRIRES) of reddened supergiants - telluric-corrected DIB spectra",
    spectral_range_original_min=10672.66, spectral_range_original_max=12838.50, spectral_range_original_unit="Angstrom",  # recoverable segments only (YJ band ~0.95-1.35 um observed)
    wavelength_min_nm=1067.27, wavelength_max_nm=1283.85,
    num_spectral_channels=1023, spectral_resolution=100000, spectral_resolution_unit="R (lambda/dlambda)",
    sampling_interval=0.05, sampling_interval_unit="Angstrom",
    num_samples=5,  # 4 reddened supergiants + unreddened HD 87737 (only HD 111613 partially recoverable)
    num_spectra=8, num_spectral_values=8 * 1023,  # recovered segments; archive truncated
    spectral_target_relationship="Telluric-corrected normalised flux of 4 reddened BA supergiants (+ comparison star) -> identification/measurement of 17 known and 12 new NIR diffuse interstellar bands (EW, FWHM, profile shapes) vs reddening E(B-V); non-LTE stellar modelling",
    source_file="6641623.pdf; CRIRES_DIBs_data.zip (<star>/<central wavelength>.asc: wave [A, vacuum, barycentric], flux, tell_trans, noise) - archive truncated, only 8 HD111613 files recoverable",
    confidence=0.6,
)

R["6780907"] = dict(
    modality="UV-Vis absorption spectroscopy of FAD photoreduction in purified L-Cryptochrome (+ underwater spectroradiometry of sun/moon light)",
    spectral_range_original_min=300, spectral_range_original_max=700, spectral_range_original_unit="nm",
    num_samples=1,  # purified Platynereis dumerilii L-Cry (dark, blue-, sun-, moonlight states)
    spectral_target_relationship="UV-Vis spectra of L-Cry after naturalistic sun-/moonlight exposures and during dark recovery -> FADox vs FAD radical (FAD.-) state kinetics (450 nm decay, 370/404 nm rise; dark-recovery time constants) distinguishing sunlight vs moonlight states",
    source_file="6780907.pdf (bioRxiv 2021.04.16.439809); 25 Origin .opju (Fig 5b-i, S5, S6 UV-Vis); Fig_5a.xlsx (SEC-MALS); Suppl.Fig.1.xlsx (light spectra 350-800 nm); spawning xlsx; README.txt",
    confidence=0.55,
)

R["6958560"] = dict(
    modality="None (no spectra): monthly-mean ozone vertical profile records retrieved from satellite limb/occultation/nadir UV-VIS-IR-microwave spectrometry, ground-based lidar/microwave/FTIR/Umkehr/ozonesondes and CCMI model output",
    num_samples=14,  # 7 merged satellite records + MEGRIDOP + ground-based record types (lidar, microwave, FTIR, Umkehr, sondes) + CCMI-1 REF-C2
    spectral_target_relationship="No spectral data; ozone number density / mixing-ratio profiles (monthly zonal means, 60S-60N) -> LOTUS multiple-linear-regression trends 2000-2020 (% per decade vs pressure/altitude)",
    source_file="6958560.pdf; Satellites_Models_Ground-based_MonthlyMeans_Records.zip (DataAvailability/<record>/ *.nc, *.nc4, *.dat, *.h5)",
    confidence=0.85,
)

R["7005320"] = dict(
    modality="Mid-IR FTIR transmission spectroscopy of aerosol particles collected on ZnSe crystals by electrostatic precipitation",
    spectral_range_original_min=700.12, spectral_range_original_max=3996.3, spectral_range_original_unit="cm-1",
    num_spectral_channels=1710, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.9287, sampling_interval_unit="cm-1",
    num_samples=11, num_spectra=11, num_spectral_values=11 * 1710,
    spectral_target_relationship="Baseline-corrected IR absorbance of ammonium sulfate deposits on ZnSe -> collected mass (linear response R2 > 0.94 vs particle-count reference), collection efficiency (82 +/- 8 %) and radial deposition profile (variable-aperture IR)",
    source_file="7005320.pdf; absorbance_table.csv (wavenumber + 11 sample spectra; effective deposition thicknesses in header); baseline_correct_and_cut.m; DATASET_README.txt",
    confidence=0.9,
)

R["7024765"] = dict(
    modality="In-situ time-resolved DRIFT spectroscopy (modulation excitation) of CO oxidation on Au/TiO2 (+ in-situ UV-Vis reflectance, DR UV-Vis Kubelka-Munk, XPS, XRD)",
    spectral_range_original_min=599.17, spectral_range_original_max=3998.76, spectral_range_original_unit="cm-1",
    num_spectral_channels=1323, spectral_resolution=8, spectral_resolution_unit="cm-1",
    sampling_interval=2.571, sampling_interval_unit="cm-1",
    num_samples=2,  # 1 % Au/TiO2 (P25) catalyst and bare TiO2 reference
    num_spectra=1098,  # 18 unique DRIFTS series x 61 time-resolved spectra (modulation period 100 s); + 2 KM UV-Vis, 6 UV-Vis time traces
    num_spectral_values=1098 * 1323,
    spectral_target_relationship="Time-resolved DRIFTS (CO-Au ~2100-2131 cm-1, CO2 2343 cm-1) under CO/O2 gas switching at 20-250 C -> transient inactivation of CO oxidation, Au charge state (CO band shift); in-situ UV-Vis (750-950 nm) -> Au nanoparticle restructuring",
    source_file="7024765.pdf; Original data.rar (figure 1-4 and Supplementary figure 1-15 folders: DRIFTS *.txt matrices [wavenumber + 61 spectra], JASCO KM spectra, UV-Vis time traces, XPS Au 4f/Ti 2p, XRD, activity)",
    confidence=0.85,
)

R["7064870"] = dict(
    modality="Computed (quantum-dynamical, MCTDH) IR absorption spectra of protonated water clusters (Eigen H9O4+ / Zundel H5O2+)",
    spectral_range_original_min=0, spectral_range_original_max=4200, spectral_range_original_unit="cm-1",
    num_spectral_channels=5001, spectral_resolution=30, spectral_resolution_unit="cm-1 (limited by 1 ps autocorrelation)",
    sampling_interval=0.84, sampling_interval_unit="cm-1",
    num_samples=2,  # Eigen cation (full 33D and reduced models) and Zundel-like subunit
    num_spectra=8,  # Fig 1 (full spectrum), Fig 2a-e (frozen-mode models), Fig 4a, 4b; each with 3 filter variants
    spectral_target_relationship="Full-dimensional (33D) ML-MCTDH simulated IR spectra with frozen subsets of coordinates -> assignment of shared-proton / core O-H stretch bands and anharmonic coupling of the hydrated proton to its first solvation shell (vs D2-tagged experiments)",
    source_file="7064870.pdf; fig_1.tgz, fig_2a-e.tgz, fig_4a.tgz, fig_4b.tgz (MCTDH inputs, operators, CPD PES/DMS fits, spectrum_raw / spectrum.pl); README_fig_1/2/4.txt",
    confidence=0.75,
)

R["7072765"] = dict(
    modality="None (no spectra): shipboard interstitial-water chemistry (ICP-AES emission-line concentrations, ion chromatography, alkalinity, pH, salinity)",
    num_samples=66,  # IW samples, Site U1438 Holes B (26), D (36), E (4)
    spectral_target_relationship="No spectral data; pore-water element/ion concentrations (Al 309.3 nm, Ba 455.4/493.4 nm, B 249.7/249.8 nm ICP-AES lines, Ca, Mg, K, Na, Li, Sr, Si, SO4, Cl, ...) vs depth at IODP Site U1438 (Amami Sankaku Basin, Izu-Bonin-Mariana arc origins)",
    source_file="7072765.pdf (IODP Proc. Vol. 351 front matter); IWREPORT.zip (data_by_hole/IWREPORT-351-U1438{B,D,E}.csv); IWREPORT-README.txt",
    confidence=0.85,
)

R["7086623"] = dict(
    modality="Steady-state and time-resolved UV-Vis and FTIR difference spectroscopy (FMN, amide, nitrile CNF probe regions) of the LOV photoreceptor EL222",
    spectral_range_original_min=1500.33, spectral_range_original_max=2269.78, spectral_range_original_unit="cm-1",  # IR (amide 1500-1749, CNF 2200-2270); UV-Vis 320-550 nm
    spectral_resolution=None, sampling_interval=1.928, sampling_interval_unit="cm-1 (IR); 1 nm (UV-Vis)",
    num_spectral_channels=130,
    num_samples=10,  # WT (H2O, D2O), LOV domain (H2O, D2O), 6 CNF mutants (W31, L35, N53, Y136, M151, L216)
    num_spectra=1165,  # time-resolved spectra in 26 *_DATA.csv files (+ steady-state dark/lit/difference, LDA maps)
    num_spectral_values=158942,
    spectral_target_relationship="Lit-to-dark recovery kinetics in UV-Vis (FMN adduct 390 -> 450 nm), amide I/II and CNF nitrile IR bands -> asynchronous relaxation events (lifetime distribution analysis), CNF31/CNF35 reporters of oligomer/caging equilibria",
    source_file="7086623.pdf (bioRxiv preprint); 61 CSV: 1.1-1.3 steady-state CNF/AMIDE/UVVIS DARK/LIT/DIFFERENCE; 2.x.<variant>_{UVVIS,AMIDE,CNF}_DATA.csv time series; *_LDA.csv lifetime distribution maps",
    confidence=0.8,
)

R["7188057"] = dict(
    modality="Optical emission spectroscopy of transmitted high-power laser pulses (VIS grating spectrometer images + NIR fibre spectrometer) after laser wakefield acceleration; electron spectrometer images",
    spectral_range_original_min=350, spectral_range_original_max=1720.27, spectral_range_original_unit="nm",  # Andor Shamrock 350-840 nm + Ocean Optics NIRQuest 899-1720 nm
    num_spectral_channels=512,  # NIRQuest pixels
    num_samples=8,  # experimental runs (density and length scans, 2017-07-28 and 2017-08-03)
    num_spectra=157,  # NIRQuest shot spectra (r004: 112, r007: 45); + ~314 Shamrock / electron-spectrometer TIF images
    num_spectral_values=157 * 512,
    spectral_target_relationship="Laser photon redshift/depletion spectra (800 -> up to 1600 nm) and electron energy spectra vs plasma density and length -> laser-to-wake energy transfer and extraction efficiency (max 19 +/- 3 %); comparison with PIC simulations",
    source_file="7188057.pdf; EfficiencyPaperShare.zip (expt_data/<date>/<run>/*_NIRQuest.txt SpectraSuite files, *.tif spectrometer/espec images, F40focus tiffs; pkg_data calibrations; Simulations/*.mat/*.pkl; Jupyter notebooks + python modules)",
    confidence=0.75,
)

R["7199948"] = dict(
    modality="Ground-based solar absorption FTIR (high resolution) -> retrieved NH3 total columns (no spectra in dataset)",
    spectral_range_original_min=929.1, spectral_range_original_max=970.0, spectral_range_original_unit="cm-1",  # retrieval microwindows 929.1-931.8 and 963.7-970.0 cm-1
    spectral_resolution=0.005, spectral_resolution_unit="cm-1 (Altzomoni); 0.075-0.1 cm-1 (UNAM)",
    num_samples=2,  # 2 stations: UNAM (urban, 2012-2019) and Altzomoni (remote, 2012-2020)
    spectral_target_relationship="Solar absorption spectra (NH3 nu2 band microwindows) -> optimal-estimation retrieval of NH3 total columns with errors and DOF (12,023 retrievals) -> diurnal/seasonal cycles, trends, comparison with IASI satellite NH3",
    source_file="7199948.pdf; UNAM_FTIRdata.csv (7992 rows); ALTZ_FTIRdata.csv (4031 rows): time, total_column, error_total/systematic/random, dof",
    confidence=0.85,
)

R["7272338"] = dict(
    modality="UV-Vis absorption (AuNP plasmon-shift titrations, enzyme assays) + 1D/2D (SOFAST-HMQC) NMR binding kinetics + DLS",
    spectral_range_original_min=400, spectral_range_original_max=700, spectral_range_original_unit="nm",
    num_spectral_channels=3001, sampling_interval=0.1, sampling_interval_unit="nm",
    num_samples=6,  # GB3 variants (WT, K13G, K13A, K13E, K13Y) + enzymes (proteinase K, carbonic anhydrase)
    num_spectra=150,  # UV-Vis titration spectra (12 TPS workbooks); + CA/PK assay UV kinetics, NMR SOFAST series
    num_spectral_values=150 * 3001,
    spectral_target_relationship="AuNP surface-plasmon peak red-shift (~517.6 nm) vs GB3 variant concentration -> Langmuir binding constants; competitive SOFAST-HMQC NMR intensities -> residue-based AuNP affinity scale; UV-Vis enzyme assays -> activity/orientation of AuNP-bound proteinase K and carbonic anhydrase",
    source_file="7272338.pdf (bioRxiv 2022.03.29.486298); uv-vis_titration.zip (*_TPS.xlsx 'Original Absorbance', *_MTVL.xlsx, Origin fits); sofast_kinetics.zip; pk_and_hca_assay.zip; surface_calculations.zip (PDB/PyMOL/python)",
    confidence=0.8,
)

R["7306475"] = dict(
    modality="Functional near-infrared spectroscopy (CW fNIRS hyperscanning, 3 wavelengths) - haemoglobin concentration time series + OpenFace facial tracking",
    spectral_range_original_min=780, spectral_range_original_max=830, spectral_range_original_unit="nm",
    num_spectral_channels=3,  # 780, 805, 830 nm
    num_samples=40,  # 20 analysed dyads (22 pair folders P01-P22) x 2 participants
    spatial_resolution=None,
    spectral_target_relationship="fNIRS OxyHb/deOxyHb/HbDiff signals (58-60 channels per participant, 30 Hz) during live face-watching -> GLM neural correlates of emotional contagion (partner affect ratings) and facial mimicry (OpenFace action units) in dyads",
    source_file="7306475.pdf; facereading.tgz (P01-P22: FaceReadingPXX_*.csv NIRS exports, optode 3D location csv, facevideo/processed OpenFace csv, results/ logs + ratings); FilesIncluded.csv; README.md",
    confidence=0.8,
)

R["7351744"] = dict(
    modality="FTIR (KBr) + UV-Vis absorption characterisation of green-synthesised ZnO nanoparticles (+ XRD, EDX, SEM)",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3601, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=2,  # ZnO NPs and Cocos nucifera leaf extract
    num_spectra=2, num_spectral_values=3601 + 30,  # leaf-extract FTIR (3601 pts) + digitised ZnO FTIR (30 pts); UV-Vis 20-pt tables
    spectral_target_relationship="FTIR functional groups of leaf extract / capped ZnO, UV-Vis absorption max 370 nm and Tauc band gap 3.37 eV, XRD wurtzite crystallite size 16.6 nm -> confirmation of ZnO NP synthesis; UV-Vis of methylene blue degradation -> photocatalytic activity",
    source_file="7351744.pdf (bioRxiv preprint); 8 figure-data .txt (Fig 3 UV-Vis, Fig 4 XRD, Fig 5 FTIR, Fig 9 MB degradation, Fig 10 DPPH); README.txt",
    confidence=0.8,
)

R["7415554"] = dict(
    modality="FTIR spectroscopy of functionalised polymer resin catalysts (+ solid-state 13C NMR, elemental analysis, catalytic kinetics)",
    spectral_range_original_min=399.21, spectral_range_original_max=3997.85, spectral_range_original_unit="cm-1",
    num_spectral_channels=1867, sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=4,  # PEGMA, PEGMA-Cl, PEGMA-AMP-Boc, PEGMA-AMP
    num_spectra=4, num_spectral_values=4 * 1867,
    spectral_target_relationship="FTIR spectra after each synthesis step (support, chlorination, Boc-pyrrolidine substitution, deprotection) -> confirmation of functionalisation (C-Cl 660/740 cm-1 etc.); combined with amine loading and aldol-condensation kinetics (TOF 3.0e-3 s-1 in acetone/water)",
    source_file="7415554.pdf; Experimental data Biesemans et al. Catalysts 2022.xlsx (sheets Description, Figure 2 FTIR, weight percentages, amine loadings, Table 2, kinetics experiments, Figure A.5)",
    confidence=0.85,
)
