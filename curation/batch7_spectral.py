# Batch7 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (C:\Users\Admin\RAG\2\papers\<id>.pdf) + dataset (D:\Batch7_datasets\<id>_<title>\).
# Only the 31 records that contain spectra are kept; the 19 records without spectra were moved
# to D:\Batch7_no_spectra (see NO_SPECTRA below) and are not part of the batch7 parquet files.
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

# Records removed from Batch7 because the dataset holds no spectra (record id -> reason).
NO_SPECTRA = {
    "18451122": "CALIOP depolarization-ratio retrievals of above-cloud aerosol optical depth at 532 nm (+ 1064/532 colour-ratio Angstrom exponent, lidar ratio) in 395 monthly ASCII tables - derived single-wavelength lidar product, no spectra",
    "18553569": "article PDF only (Sci. Data 2025 battery-interphase IR/Raman/XRD database; the database files themselves were not downloaded)",
    "18743784": "R project with Purency/siMPle ImageLab particle lists (FPA-uFTIR polymer class, size, shape per particle), blanks and DWD precipitation data - classification results only, no spectra",
    "18933272": "article PDF only (biodiesel production from microalgae, IJAR)",
    "18986098": "IODP Exp 392 interstitial-water composite report (wet chemistry)",
    "19210896": "species-level UV/VIS/NIR/total reflectance brightness summaries (band-averaged %, 440 species) + phylogenies and R script - no spectra",
    "19502759": "micro-FTIR library-match tables of hail microplastics (polymer, hit score, morphology) and statistics workbooks - no spectra",
    "19636576": "concept PDF 'Photonide Class: Optical AI Hardware' + AI-generated PNG - no data (paper PDF is an unrelated 2019 BaTiO3-SiN electro-optic device article)",
    "20135728": "olive-mill wastewater nanofiltration results (permeability, rejection of COD/phenols/sugars, cleaning) - no spectra",
    "20208787": "article PDF only (fibroin secondary structure / sericin paper; paper PDF is the 2011 Nature Protocols silk-fibroin protocol)",
    "20323517": "Western Siberian peat-core database (core locations, chronology and proxy-availability flags, shapefiles) - no spectra",
    "20389604": "article PDF only (physicochemical and mineralogical properties of Senegal clays, IJAR)",
    "20483373": "article PDF only (paracetamol 500 mg tablet conformity, IJAR)",
    "20566389": "article PDF only (benzoylation treatment of natural fibres, IJAR/ICSEFT)",
    "20747040": "HYPER-P merged satellite/reanalysis daily precipitation NetCDF for 5 basins - no spectra; 6 of 10 zips are not readable zip files and 4 .part files remain",
    "20759160": "NetCDF of calibrated C/M river-discharge proxies (NIR reflectance ratios, 34 stations x 9,489 days x 4 sensor products) - derived index time series, no spectra",
    "20810863": "compilation of published bone-collagen d13C/d15N stable-isotope data + R code PDFs - no spectra",
    "21282791": "supplementary-material PDF only (CRISM gypsum study; spectra only as figures)",
    "21712712": "DFT (VASP/phonopy/LOBSTER) inputs/outputs for hexagonal diamond: structures, phonon frequencies with irreps and Raman-activity flags - no Raman or IR spectra (no intensities, no measured data)",
}

# ---------------------------------------------------------------------------
# IODP JOIDES Resolution shipboard data (papers = Proceedings volume front matter /
# expedition summaries; methods are standard JRSO shipboard procedures)
# ---------------------------------------------------------------------------
_PAPER = {
    392: "Proc. IODP Vol. 392 front matter (Uenzelmann-Neben, Bohaty, Childress & Exp 392 Scientists 2023; same 10-page PDF for 18943633, 18968203, 18986098)",
    368: "Proc. IODP Vol. 367/368 'Expedition 367/368 summary' (Sun, Jian, Stock et al. 2018) - Exp 368X re-entered Site U1503 later in 2018",
    362: "Proc. IODP Vol. 362 'Expedition 362 summary' (McNeill, Dugan, Petronotis et al. 2017)",
}

R["18943633"] = dict(
    modality="Single-wavelength UV-Vis colorimetric absorbance (Agilent Cary 300) of interstitial water: ammonium 640 nm",
    spectral_range_original_min=640, spectral_range_original_max=640, spectral_range_original_unit="nm",
    num_spectral_channels=1, spectral_resolution=1.5, spectral_resolution_unit="nm (spectral bandwidth, SBW)",
    num_samples=156,
    num_spectral_values=173,  # ammonium concentration results (one absorbance reading per sample run)
    spectral_target_relationship="Absorbance at 640 nm (indophenol blue) vs external standard curve -> pore-water ammonium concentrations (uM) vs depth (0-978.9 m CSF-A) in 6 holes (U1579A/B/D, U1580A, U1581A/B) on the Agulhas Plateau; Beer-Lambert linear calibration",
    source_file=f"18943633.pdf ({_PAPER[392]}, Exp 392); SPEC-README.txt; data_by_hole (6 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (3 Cary Advanced Reads csv, 3 .BAB, 3 .MAB, 3 *.xlsm calibration workbooks)",
    confidence=0.8,
)


def _rsc(rid, exp, vol, nspectra, nfiles, nholes, sites, depth_max, sensor, lo, hi, nbands, values=None, conf=0.85, note=""):
    R[rid] = dict(
        modality=f"VIS diffuse reflectance spectroscopy and colorimetry (RSC) of split-core section halves ({sensor} + integrating sphere on SHMSL)",
        spectral_range_original_min=lo, spectral_range_original_max=hi, spectral_range_original_unit="nm",
        num_spectral_channels=nbands, sampling_interval=2, sampling_interval_unit="nm",
        num_samples=nfiles,  # per-section-half normalised reflectance files
        num_spectra=nspectra,
        num_spectral_values=values if values is not None else nspectra * nbands,
        spectral_target_relationship=f"% reflectance spectra (white/dark-referenced) of sediment/rock core surfaces -> CIE XYZ, L*a*b*, chroma, hue vs depth (0-{depth_max} m CSF-A) in {nholes} hole(s) ({sites}) for lithostratigraphy, cyclostratigraphy and hole-to-hole correlation" + note,
        source_file=f"{rid}.pdf ({_PAPER[vol]}, Exp {exp}); RSC-README.txt; data_by_hole/*-RSC.csv (+ scaled, compiled-scale, splice where present); supplementary_material raw_data_files norm_*/raw_*_rsc.csv + *.RSC; configuration .ini files; standards_measured",
        confidence=conf,
    )


_rsc("18968203", "392", 392, 72388, 1733, 10, "U1579A-D, U1580A/B, U1581A/B, U1582A/B", 993.97,
     "Ocean Insight QE Pro (S/N QEP00732) with Ocean Optics BlueLoop source", 390, 718, 165)
_rsc("19635411", "368X", 368, 7327, 181, 1, "U1503A, South China Sea rifted margin", 1705.57,
     "Ocean Insight QE Pro (S/N QEP00732)", 390, 730, 171, conf=0.8)
_rsc("19867045", "362", 362, 40693, 989, 8, "U1480A-H, U1481A, Sumatra subduction-zone input sites", 1498.71,
     "Ocean Optics USB4000-VIS", 380, 900, 211, values=8999923, conf=0.8,
     note="; 32,419 spectra x 211 bands (380-800 nm) for U1480 holes and 8,274 x 261 bands (380-900 nm) for U1481A")

# ---------------------------------------------------------------------------

R["18632810"] = dict(
    modality="Bidirectional mid-infrared reflectance spectroscopy (Bruker Vertex 70V FTIR, A513 variable-geometry stage, i=20 deg / e=30 deg, LN-MCT) of synthetic planetary-analogue glasses in four grain-size fractions",
    spectral_range_original_min=555.636, spectral_range_original_max=5000.724, spectral_range_original_unit="cm-1",
    num_spectral_channels=2073, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=2.145, sampling_interval_unit="cm-1 (2.0-18.0 um)",
    num_samples=5,  # 674 tholeiitic basalt, 675 Mg-rich komatiite, 676 boninite variation, 677 boninite, 678 komatiite
    num_spectra=20,  # 5 glasses x 4 size fractions (0-25, 25-63, 63-125, 125-250 um)
    num_spectral_values=41460,
    spectral_target_relationship="Christiansen feature, reststrahlen bands (Si-O stretching ~9-11 um) and transparency feature vs glass composition (SiO2, MgO, Na2O from EMPA/SEM tables) and grain size -> laboratory analogues for MERTIS (BepiColombo) mid-IR remote sensing of Mercury and other planetary surfaces",
    source_file="18632810.pdf (Morlok, Klemme, Weber, Stojic, Sohn et al., 'Mid-Infrared Spectroscopy of Planetary Analogs: A Database for Planetary Remote Sensing' - related IRIS/MERTIS method paper on other glasses, not this sample set); 20 txt (header with measurement protocol + wavenumber, wavelength, reflectance), 5 *_SEM.xlsx compositions, 5 BSE jpg",
    confidence=0.75,
)

R["18658130"] = dict(
    modality="Surface-enhanced Raman spectroscopy (WITec alpha300R, 785 nm) of Cy3/Cy5.5-labelled miRNA on MoS2@Au nanocomposites + UV-Vis-NIR absorption (Agilent Cary 7000) + XPS core-level scans",
    spectral_range_original_min=200.501, spectral_range_original_max=1899.32, spectral_range_original_unit="cm-1",
    sampling_interval=1.73, sampling_interval_unit="cm-1 (SERS; Fig 2a Raman 2.85 cm-1; UV-Vis 200-800 nm at 1 nm; XPS 0.1 eV)",
    num_samples=6,  # MoS2, MoS2@Au, synthetic miR-210-3p, synthetic miR-9-3p, cellular miR-210-3p, cellular miR-9-3p
    num_spectra=50,  # 39 Raman/SERS + 2 UV-Vis + 9 XPS region scans
    num_spectral_values=31264,
    spectral_target_relationship="Cy3 (~1127, 1196, 1391, 1587 cm-1) and Cy5.5 (~1199, 1337, 1455 cm-1) SERS band intensities vs labelled miR-210-3p / miR-9-3p concentration (0.0018-1800 nM) -> linear calibration and LoD (pM-nM) for breast-cancer miRNA detection; MoS2 E12g/A1g modes (384/409 cm-1), Au LSPR (~536-589 nm) and XPS Mo 3d/S 2p/Au 4f confirm in-situ Au growth",
    source_file="18658130.pdf (Zablon, Pathiraja, Dellinger & Aravamudhan 2026 Sci. Rep., doi:10.1038/s41598-026-41084-3); 13 xlsx: Fig 2a Raman, Fig 2b UV-Vis, Fig 4a-c XPS, Fig 5a-8a SERS series, SUPP S1a/b XPS, S2 Raman controls, S3 qPCR Ct",
    confidence=0.8,
)

R["18783909"] = dict(
    modality="ATR-FTIR spectroscopy (PerkinElmer Spectrum Two, diamond ATR) of individual environmental microplastic particles from the Arctic marine environment (MICROSCAN database)",
    spectral_range_original_min=450, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3551, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=2010,  # particles
    num_spectra=2010,  # PE 1,453, PP 466, PS 80, PE/PP 11
    num_spectral_values=7137510,
    spectral_target_relationship="Absorbance spectra of weathered, biofouled particles labelled PE/PP/PS by spectral matching (SMI vs PerkinElmer ATR polymer + BASEMAN libraries) and verified with a 1D-CNN classifier (96-97 % accuracy) -> training/validation data for environmental microplastic identification; colour and DSC data support labels",
    source_file="18783909.pdf (Zhdanov, Volgin, Vlasova, Pakhomova, Yakushev & Lyulin 2026 Sci. Data, doi:10.1038/s41597-026-08121-2); MICROSCAN_database.zip (csv/xlsx: file name, colour, polymer, matching score + 3,551 absorbance columns; manual_and_CNN1D_classification.csv); spectra_files_in_csv.zip (2,010 csv); spectra_in_interactive_form.zip (35 html)",
    confidence=0.9,
)

R["18940376"] = dict(
    modality="ATR-FTIR spectroscopy (Agilent Cary 640 + PIKE GladiATR) of charred archaeological barley grains screened for carbonate, nitrate and humic contamination",
    spectral_range_original_min=399.122, spectral_range_original_max=4000.863, spectral_range_original_unit="cm-1",
    num_spectral_channels=1869, sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=13,  # grains from Maharski prekop (MP) and Stare gmajne contexts S6, S7, S8
    num_spectra=13,
    num_spectral_values=24297,
    spectral_target_relationship="Absorbance at carbonate (~1430/875 cm-1), nitrate (~1384 cm-1) and humic (~1580/1250 cm-1) diagnostic bands vs reference thresholds (Vaiglova et al. 2014) -> confirms pretreatment removed contaminants before d13C/d15N analysis of Late Neolithic pile-dwelling barley (manuring and water status)",
    source_file="18940376.pdf (Skrt Kristan, Kuzmic, Tolar & Styring 2026 Veg. Hist. Archaeobot., doi:10.1007/s00334-026-01108-4); Barley_cultivation_Supplementary_data.zip: ESM_3/ESM3_FTIR.csv (wavenumber + 13 grain columns), 16 contamination plots, R script; ESM_2 152 grain TIFF photographs; ESM_5 isotope xlsx",
    confidence=0.8,
)

R["19028454"] = dict(
    modality="Computed TD-DFT electronic absorption (Gaussian 09, B3LYP/6-311G(d,p), SCRF methanol, 30 singlet states) of a Schiff-base Ni(II) complex - modelled stick spectrum, not measured",
    spectral_range_original_min=224.05, spectral_range_original_max=707.92, spectral_range_original_unit="nm",
    num_spectral_channels=30,
    num_samples=1,
    num_spectra=1,
    num_spectral_values=30,  # excitation energies with oscillator strengths
    spectral_target_relationship="Vertical singlet excitation energies and oscillator strengths (strongest f=0.86 at 245.8 nm; weak d-d/LMCT bands 365-422 nm) assign intra-ligand pi-pi*, n-pi* and charge-transfer bands of the measured UV-Vis spectrum; geometry from B3LYP optimisation and SC-XRD (checkCIF)",
    source_file="19028454.pdf (Arumugam & Arockiasamy 2026 Research Square rs-10915037 - mononuclear Cu(II) Schiff-base complex; the deposited logs and CIF are for C24H32N2NiO4, a Ni complex); shlex_UV-Vis.LOG.txt (TD-DFT), SHELX.LOG.txt (geometry optimisation), checkCIF.pdf (P21/c)",
    confidence=0.45,
)

R["19205775"] = dict(
    modality="FTIR transmittance spectroscopy of sewage-sludge ash, fish meal and their mixture after solubilisation by Bacillus megaterium / Pseudomonas putida (single and dual consortia)",
    spectral_range_original_min=399.193, spectral_range_original_max=4000.605, spectral_range_original_unit="cm-1",
    num_spectral_channels=3736, sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=12,  # 3 wastes x 4 inoculation treatments (none, Bm, Pp, Bm+Pp)
    num_spectra=36,  # triplicates (two spectra 2 points short)
    num_spectral_values=134492,
    spectral_target_relationship="Band areas (SAUB) normalised to the C-H region: phosphate solubilisation factor (950-1080 cm-1), protein decomposition (amide I/II), lipid and carbonate indices vs waste type and bacterial consortium -> structural transformation and P release, linked with kinetic models, pH, redox, phosphatase activity and PCA",
    source_file="19205775.pdf (Sojka, Michellin Kiruba, Winiarski & Saeid 2025 Chem. Biol. Technol. Agric. 12:164, doi:10.1186/s40538-025-00878-9); FTIR_MS_Merged.csv (long format: Wavenumber, Transmittance, Waste, Bacteria); MS_Solub.csv (pH, redox, phosphatase, P2O5/Se/Zn over 7 days)",
    confidence=0.75,
)

R["19446323"] = dict(
    modality="ATR-FTIR spectroscopy (Thermo Nicolet iS5, iD7 ZnSe ATR) of crude extracts and solid biomass of pelagic Sargassum during cold transport and sun exposure, plus reference standards",
    spectral_range_original_min=499.955, spectral_range_original_max=4000.122, spectral_range_original_unit="cm-1",
    num_spectral_channels=7261, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=34,  # CE/SB x exposure days (0-56 d) x batches (Ma23, Ma24 NDS)
    num_spectra=102,  # + ~20 standard spectra (csv, jdx, spa) of 14 reference compounds
    num_spectral_values=740622,
    spectral_target_relationship="Absorbance bands of alginate (carboxylate 1600/1410 cm-1), fucoidan sulfate (1220-1250 cm-1), mannitol, organic acids (lactate, acetate, formate, citrate), carbonates and silicates vs storage/sunlight time -> PCA/chemometric tracking of degradation and fermentation of beached Sargassum",
    source_file="19446323.pdf (Peniche-Pavia, Guzman, Tiessen et al. 2024 J. Appl. Phycol. 36:1391); 'ATR-FTIR spectra of CE and SB from Sargassum.zip' (102 csv Ma23/Ma24_<CE|SB>_<day>d_<rep>); 'ATR-FTIR Spectra of Standards.zip' (5 csv, 13 NIST/library jdx, 3 spa, RData)",
    confidence=0.85,
)

R["19467702"] = dict(
    modality="ATR-FTIR spectroscopy (Bruker Tensor 27) of plant parts recovered from rock ptarmigan crops (Iceland), vector-normalised replicate means",
    spectral_range_original_min=399.256, spectral_range_original_max=3996.415, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=300,  # crop samples (species x plant part x bird sex/age x year)
    num_spectra=300,
    num_spectral_values=559800,
    spectral_target_relationship="Lipid (2920/2850, 1745 cm-1), protein (1650/1540), phenolic (1605), oxalate (1620/1315), cellulose (1025/996) and lignin (1515) fingerprints -> PCA and Random-Forest classification of forage plant part (RFp) and taxon+part (RFtp, accuracy 0.855) to infer ptarmigan diet selection",
    source_file="19467702.pdf (Schafer, Zohmann-Neuberger, Nielsen, Nopp-Mayr et al. 2026 J. Chem. Ecol. 52:41); LM_Iceland_crop_samples_FTIR_data.csv (296 x metadata + wavenumbers, CO2 region removed), *_ChemoSpec.csv (1,866 x 300), loadings_PC1/PC2, scores_LM_full.csv, food composition table, R script",
    confidence=0.85,
)

R["19650918"] = dict(
    modality="Fluorescence excitation-emission matrices with polarisation (anisotropy; Edinburgh FS920, VV/VH/unpolarised) + UV-Vis absorbance of flavanol standards and red wines",
    spectral_range_original_min=250, spectral_range_original_max=600, spectral_range_original_unit="nm",
    sampling_interval=2, sampling_interval_unit="nm emission (260-600 nm, 171 pts); excitation 250-450 nm in 5 nm steps (41); UV-Vis 250-600 nm at 1 nm",
    num_samples=15,  # 9 standard solutions (catechin, epicatechin, procyanidin B2/B3/C1, grape seed extract) + 6 wines
    num_spectra=1860,  # 45 EEMs x 41 emission scans + 15 UV-Vis spectra
    num_spectral_values=320760,  # 45 x 171 x 41 EEM cells (34 % NaN outside scatter limits) + 15 x 351 UV-Vis
    spectral_target_relationship="Flavanol fluorescence (ex/em ~280/310 nm) resolved by PARAFAC; quantum-yield decrease and fluorescence polarisation/anisotropy vs degree of polymerisation (monomer -> dimer -> trimer, tannin extract) -> estimate of tannin polymerisation in red wine; UV-Vis 280 nm absorbance for inner-filter correction",
    source_file="19650918.pdf (Halberg, Heide & Rinnan 2026 Food Res. Int. 236:119152, doi:10.1016/j.foodres.2026.119152); EEM_polymerization.mat (X: 45 x 171 x 41 raw EEMs; EEM dataset object), EEM_preprocessed_polymerization.mat (G-factor + IFE corrected, standards 9 / wines 18), UVVIS_polymerization.mat (9 + 6 x 351), EEM_raw.zip (32 Edinburgh txt), ReadMe.txt",
    confidence=0.85,
)

R["19693995"] = dict(
    modality="Nonlinear optical (SHG/THG) and photoluminescence spectra of lanthanide-complex-functionalised LiNbO3 harmonic nanoparticles (LabRAM HR Evolution with 800 nm fs laser) + FTIR (PerkinElmer Spectrum 3) of the conjugates",
    spectral_range_original_min=325.356, spectral_range_original_max=775.573, spectral_range_original_unit="nm",
    sampling_interval=0.2, sampling_interval_unit="nm (SHG spectra; SHG/THG 0.17 nm; PL 0.05-0.52 nm); FTIR 400-4000 cm-1 at 1 cm-1 (%T)",
    num_samples=9,  # LNO@Ln conjugates (Eu, Gd, Tb, Yb; batches SD121/146/150) + reference AS562
    num_spectra=106,  # 97 SHG/THG/PL spectra (incl. polarisation series) + 9 FTIR
    num_spectral_values=89517,
    spectral_target_relationship="SHG at 400 nm and THG at ~267 nm from LiNbO3 cores and Eu3+ 5D0-7F2 emission (~612 nm) vs excitation polarisation angle (polar plots) demonstrate correlative harmonic + luminescence imaging; FTIR triazole/azide bands confirm CuAAC click conjugation of Ln-DOTA-type complexes (with T1/T2 MRI relaxivity for Gd)",
    source_file="19693995.pdf (Dumolard, Multian, Gheata, Spada, Pierzchala, Lanz, Dhouib, Mugnier, Teyssier, Bonacina, Chauvin & Gerber-Lemaire 2026 Nanomaterials 16:591); FTIR.zip (8 PerkinElmer .sp + AS562.txt), 'Nonlinear imaging.zip' (SHG full spectra, polarisation PL/SHG csv, SD121 SHG-THG csv, zattrs, scripts), Photoluminescence.zip (.opju), DLS, NMR (.mnova), MRI (.opju), STEM-EDX (753 MB), Labbook PDFs",
    confidence=0.7,
)

R["20020715"] = dict(
    modality="FTIR (Shimadzu IRTracer-100), Raman (Horiba XploRA PLUS, 532 nm) and UV-Vis diffuse reflectance (Agilent Cary 5000, Spectralon) of hydrothermal Bi2O3, BiOCl and Bi2O3/BiOCl heterojunctions (+ XRD, BET, SEM)",
    spectral_range_original_min=200.597, spectral_range_original_max=4000.364, spectral_range_original_unit="cm-1",
    sampling_interval=1.929, sampling_interval_unit="cm-1 (FTIR, 1,971 pts; Raman 51-1499 cm-1, 861 pts; UV-Vis DRS 200-800 nm at 1 nm)",
    num_samples=6,  # Bi2O3-H, Bi2O3-75/50/25/10-H heterojunctions, BiOCl
    num_spectra=17,  # 6 FTIR + 5 Raman + 6 UV-Vis DRS
    num_spectral_values=19737,
    spectral_target_relationship="Bi-O (476-625 cm-1), Bi-O-Bi (847 cm-1) and Bi-Cl FTIR bands and Raman modes (beta-Bi2O3 vs BiOCl) track BiOCl formation with HCl ratio; Kubelka-Munk/Tauc analysis of DRS gives band gaps (2.4-3.3 eV) explaining UV/visible photocatalytic caffeine degradation",
    source_file="20020715.pdf (Ruiz-Castillo, Hinojosa-Reyes, Camposeco-Solis & Ruiz 2022 Top. Catal. 65:1071); Bi2O3_BiOCl_hydrothermal_characterization_dataset.zip: FTIR_processed.xlsx, Raman/5 txt (XploRA headers), UV-Vis-DRS-processed.xlsx (absorbance, Tauc, band gaps), XRD raw/processed, BET raw/processed, SEM tif, Readme",
    confidence=0.85,
)

R["20061737"] = dict(
    modality="FTIR transmittance spectroscopy (Thermo Nicolet 6700) of PLA and PLA/MWCNT nanocomposites before and after 28-day hydrolytic degradation",
    spectral_range_original_min=599.753, spectral_range_original_max=3999.64, spectral_range_original_unit="cm-1",
    num_spectral_channels=1764, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=6,  # PLA day 0, PLA day 28, PLA/MWCNT 0.1/0.5/1.0/5.0 % day 28
    num_spectra=6,  # 7 columns, 'PLA Day 28' duplicates 'PLA' (week 4)
    num_spectral_values=10584,
    spectral_target_relationship="Ester C=O (1756 cm-1), C-O (1185/1090 cm-1) and CH (2945, 1367-1458 cm-1) band changes after simulated-physiological hydrolysis vs MWCNT content -> MWCNTs slow PLA hydrolysis, consistent with lower mass loss and higher TGA Tmax",
    source_file="20061737.pdf (Diaz Varela, Burciaga Jurado, Olivas Armendariz, Martinez Perez & Chapa Gonzalez 2024 Sci. Rep. 14:8405); single xlsx: 'PLA (semana 4)' (5 %T spectra), 'PLA D0 D28' (2 spectra), 'Thermal Degradation' (mass loss), 'AE' (TGA Tmax)",
    confidence=0.85,
)

R["20089847"] = dict(
    modality="Temperature-dependent polarised near-normal-incidence FTIR reflectivity (Bruker Vertex 80v, in-situ gold evaporation, 60-22,000 cm-1) + THz-TDS of La4Ni3O10 single crystals with Kramers-Kronig optical constants",
    spectral_range_original_min=30.104, spectral_range_original_max=21898.849, spectral_range_original_unit="cm-1",
    sampling_interval=0.643, sampling_interval_unit="cm-1 (far-IR; non-uniform merged grid)",
    num_samples=1,  # La4Ni3O10 crystal (E||ab and E||c*)
    num_spectra=23,  # 11 ab-plane + 12 c-axis temperatures (4-300 K)
    num_spectral_values=164871,  # frequency points, each with R, sigma1, sigma2, n, k, eps1, eps2
    spectral_target_relationship="Reflectivity -> optical conductivity sigma1/sigma2, n, k, epsilon vs temperature through the ~140 K density-wave transition: Drude weight, gap opening and phonon changes show strongly suppressed out-of-plane (c*) charge dynamics -> electronic layer decoupling; Drude fits give rho_c*/rho_ab",
    source_file="20089847.pdf (Guan, TenHuisen, Tepie, Zhao, Day-Roberts, LaBollita, Young, Cui, Chen, Glerean, Guia, Dean, Kim, Mitchell, Botana, Homes & Mitrano, arXiv preprint / PRL); La4Ni3O10_FTIR_PRL_Electronic_Layer_Decoupling_zenodo.zip: ab_plane/ 11 csv, c_axis/ 12 csv (frequency cm-1/THz/meV, reflectivity, sigma1, sigma2, n, k, eps1, eps2), data_dictionary.csv, README",
    confidence=0.9,
)

R["20201294"] = dict(
    modality="Femtosecond transient absorption (Ultrafast Systems Helios, 465 nm pump, white-light probe) + stationary UV-Vis absorption (Jasco V-550) of lutein-5,6-epoxide, sunflower ray-floret extracts and isolated chromoplasts",
    spectral_range_original_min=200, spectral_range_original_max=915.353, spectral_range_original_unit="nm",
    sampling_interval=1.2, sampling_interval_unit="nm (TA probe pixels 305.7-915.4 nm; stationary 1 nm)",
    num_samples=4,  # all-E-lutein-5,6-epoxide, solubilised chromoplasts, isolated chromoplasts, ester-free extract
    num_spectra=1761,  # 1,758 TA delay spectra (4 raw maps) + 3 stationary (+ 64 selected chirp-corrected TA spectra)
    num_spectral_values=782694,  # approx.: 780,921 TA map values + stationary spectra
    spectral_target_relationship="S2->S1 internal conversion and S1 decay lifetimes (ps) and excited-state absorption bands of xanthophylls (lutein epoxide, violaxanthin) in solution vs in chromoplasts -> carotenoid aggregation/environment effects and absence of detectable triplet formation in sunflower chromoplasts; HPLC-MS pigment identification",
    source_file="20201294.pdf (Wiland-Szymanska, Janecki, Szewczyk, Drapikowska, Wybraniec & Burdzinski 2026 Sci. Rep., doi:10.1038/s41598-026-53788-7); 'stationary UV-vis absorption spectra.rar' (3 csv), 'transient absorption spectra.rar' (4 raw dA maps, not chirp-corrected; 8 selected-spectra csv); ReadMeFile_v1.txt",
    confidence=0.8,
)

R["20210776"] = dict(
    modality="FTIR spectroscopy of laboratory-pyrolysed reference charcoal (reflectance via Bruker HYPERION 2000 microscope; KBr-pellet transmission via Bruker VERTEX 70v) and ancient lake-sediment charcoal particles",
    spectral_range_original_min=950.7, spectral_range_original_max=3499.9, spectral_range_original_unit="cm-1",
    num_spectral_channels=1323, spectral_resolution=8, spectral_resolution_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1 (zero-filled)",
    num_samples=1335,  # 516 pyrolysed reference samples (temperature x species x tissue x atmosphere x replicate) + 819 ancient charcoal particles (number x depth)
    num_spectra=60873,  # 32,733 reflectance + 16,515 transmission reference + 11,625 ancient ('cut' files)
    num_spectral_values=80534979,
    spectral_target_relationship="C-H (3068-2800 cm-1), C=O/C=C (1780-1510) and C-C (1160-1030) regions vs pyrolysis temperature (300-800 C), species, tissue and O2/N2 atmosphere -> deep-learning classifier (98.7 % temperature, 96.2 % species) outperforms k-NN modern analogues; applied to Valles Caldera sediment charcoal to reconstruct past fire temperatures",
    source_file="20210776.pdf (Kraklow et al. 2026 Fire Ecology 22:74, doi:10.1186/s42408-026-00500-9); reflectance_reference_cut/zstandard.csv, transmission_reference_cut.csv, ancient_cut/zstandard.csv (metadata + 1,323 wavenumber columns), AllSPConf.csv / AllTempConf.csv (confusion matrices)",
    confidence=0.85,
)

R["20261425"] = dict(
    modality="Synchrotron micro-XANES at the S and P K-edges (ESRF ID21) of modern carbonate microbialites from Lake Alchichica, with S-XANES hyperspectral mapping and SR-uXRF elemental maps",
    spectral_range_original_min=2140.21, spectral_range_original_max=2530.0, spectral_range_original_unit="eV",
    sampling_interval=0.25, sampling_interval_unit="eV (point spectra; map 0.5 eV at the edge, 2 eV pre-edge)",
    num_samples=3,  # microbialites from 10, 30 and 40 m depth
    num_spectra=6098,  # 98 point XANES (89 S K-edge, 9 P K-edge) + 6,000 pixel spectra of the S-XANES map
    num_spectral_values=385163,  # 25,163 point-spectrum values + 6,000 x 60 map energies
    spectral_target_relationship="S K-edge white-line positions (sulfide ~2.471 keV, organic S, sulfoxide, sulfonate, sulfate ~2.482 keV) fitted with ID21 organic/inorganic reference spectra -> depth-dependent sulfur speciation in microbialites; P XANES and uXRF/SEM-EDXS maps relate S/P phases to hydromagnesite/aragonite mineralogy and microbial metabolisms",
    source_file="20261425.pdf (Caumartin, Benzerara, Havas, Thomazo, Mehta et al., 'Depth-dependent sulfur speciation in modern carbonate microbialites from a monomictic lake' - Supplementary Material only); XANES.zip (S_XANES_10m/30m/40m, P_XANES_10m .dat; hyperspectral_map_40m csv + h5; microXRF h5), XRF_laboratory.zip (tif maps), SEM-EDXS.zip (tif), Bulk_chemistry.zip, 3 xlsx (data content, water chemistry, taxonomic groups)",
    confidence=0.75,
)

R["20408285"] = dict(
    modality="Laboratory transmission FTIR absorbance spectra of interstellar ice analogues (CH3OH at 10 K; NH4+OCN- at 10 K and 120 K) recorded with the ISEAge UHV setup",
    spectral_range_original_min=630.016, spectral_range_original_max=4000.765, spectral_range_original_unit="cm-1",
    sampling_interval=0.1205, sampling_interval_unit="cm-1",
    num_samples=3,
    num_spectra=3,
    num_spectral_values=80397,
    spectral_target_relationship="Laboratory band profiles of CH3OH and NH4+ (6.85 um) / OCN- (4.62 um) used, with LIDA and Cosmic Ice Lab spectra, to fit JWST NIRSpec + MIRI MRS (4.3-8.1 um) absorption toward six Class 0 protostars in Orion A -> pixel-by-pixel column-density maps of 13CO2, OCN-, CO, H2O, NH4+ and H2CO",
    source_file="20408285.pdf (Petrashkevich, Pavlyuchenkov, Punanova, Ozhiganov, Nakibov, Kartashova et al. 2026, AASTeX draft arXiv:2606.09776); Metanol_10K.txt, NH4OCN_10K.txt, NH4OCN_120K.txt (wavenumber, absorbance)",
    confidence=0.85,
)

R["20411426"] = dict(
    modality="Computed IR spectra of the hydrated proton (Zundel/Eigen cations H5O2+, H9O4+, H13O6+) from full-dimensional MCTDH quantum dynamics on machine-learned PES/DMS, plus digitised experimental reference spectra - modelled, not measured",
    spectral_range_original_min=0, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    sampling_interval=0.667, sampling_interval_unit="cm-1 (computed spectra; 4 cm-1 for some scans)",
    num_samples=4,  # H5O2+ (Zundel), H9O4+ (Eigen), H13O6+ and water/proton clusters
    num_spectra=238,  # 224 computed spectral traces (spec, scan1/2, states, eigen, zundel) + 14 experimental reference traces
    num_spectral_values=1339394,  # 1,324,208 computed + 15,186 experimental values
    spectral_target_relationship="Autocorrelation-based IR spectra from MCTDH wavepacket propagation resolve the proton-transfer, Zundel-like shuttling and Fermi-resonance features (~1000-1800 cm-1 and OH stretches up to 3700 cm-1) and compare with gas-phase predissociation and condensed-phase 2D-IR spectra -> assignment of the hydrated-proton continuum",
    source_file="20411426.pdf (Mendive-Tapia, Schran, Das, Gatti, Schroder, Marx & Vendrell 2026 Nat. Chem., doi:10.1038/s41557-026-02209-3); plots.zip (spectra_raw/ .pl and .txt spectra, exp/ literature spectra, figure scripts), wkflow_fig3.zip / wkflow_fig4.zip (MCTDH .inp/.op inputs), wkflow_efig1.zip, *.txt READMEs",
    confidence=0.7,
)

R["20413514"] = dict(
    modality="ATR-FTIR spectroscopy of biochars from pyrolysed solid wastes of used edible oils (300-600 C) before/after washing out alkaline salts (+ XRD, TGA); includes the pine-bark biochar FTIR/XRD of the related Upcycling 2026 study",
    spectral_range_original_min=400.157, spectral_range_original_max=4000.123, spectral_range_original_unit="cm-1",
    num_spectral_channels=7468, sampling_interval=0.482, sampling_interval_unit="cm-1 (Upcycling Fig 2: 599.8-4000.6 cm-1 at 0.964 cm-1)",
    num_samples=10,  # 7 pyrolysis temperatures + 3 washing states
    num_spectra=13,  # 10 Spectroscopy-J ATR spectra + 3 pine-bark biochar spectra (Upcycling-2026-Fig-2)
    num_spectral_values=85264,
    spectral_target_relationship="Aromatic C=C (~1580 cm-1), C-H out-of-plane (700-900 cm-1) and oxygenated-group bands vs pyrolysis temperature -> degree of condensation (DOC) of polyaromatic hydrocarbons; alkaline (K/Na) salts retain oxygenated surface compounds, removed by washing",
    source_file="20413514.pdf (Romero-Sarria, Real, Cordoba, Hidalgo & Alcala 2023 Spectrosc. J. 1:98); Spectroscopy-J-Fig-2 (TGA), Fig-3/Fig-7 (XRD), Fig-5 (7 ATR spectra), Fig-6 (DOC), Fig-8 (3 ATR spectra); Upcycling-2026-Fig-1/Fig-2.csv byte-identical to record 20423503",
    confidence=0.75,
)

R["20423503"] = dict(
    modality="ATR-FTIR spectroscopy of pine-bark biochars (450 C pyrolysis; CO2- and H2O-activated at 800 C) used as tetracycline adsorbents (+ XRD, SEM images)",
    spectral_range_original_min=599.753, spectral_range_original_max=4000.605, spectral_range_original_unit="cm-1",
    num_spectral_channels=3528, sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=3,  # PINO 450 C, PINO-CO2 800 C, PINO-H2O 800 C
    num_spectra=3,
    num_spectral_values=10584,
    spectral_target_relationship="Loss of O-H, aliphatic C-H and C=O bands and growth of aromatic C=C with activation (CO2, steam) -> more condensed, hydrophobic carbon surfaces that adsorb tetracycline from aquaculture effluent and support persulfate/AOP regeneration",
    source_file="20423503.pdf (Moles, Mosteo, Romero-Sarria, Garcia-Munoz & Rodriguez-Chueca 2026 Environ. Sci. Pollut. Res. 33:1237); Upcycling-2026-Fig-1.csv (XRD), Upcycling-2026-Fig-2.csv (3 ATR spectra), Fig-3A-D tif (SEM)",
    confidence=0.7,
)

R["20736558"] = dict(
    modality="In-situ transmission FTIR (PerkinElmer Spectrum Two, Mcell humidity chamber) of 30 um Scots pine earlywood sections during H2O and D2O vapour sorption (0-90 % RH) and H/D exchange",
    spectral_range_original_min=600, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=1701, spectral_resolution=8, spectral_resolution_unit="cm-1",
    sampling_interval=2, sampling_interval_unit="cm-1",
    num_samples=2,  # native wood in H2O vapour, wood deuterated in D2O vapour (+ empty-cell blanks)
    num_spectra=43,  # raw %T: 11 H2O RH steps + 11 blanks, 12 D2O steps (prior/after deuteration, 10-80 %, overnight, final) + 9 blanks
    num_spectral_values=73143,
    spectral_target_relationship="OH (3400 cm-1) vs OD (2500 cm-1) stretching band areas, rubber-band/anchor-point corrected and normalised, vs RH -> accessible hydroxyl content and H/D exchange of wood cell walls; compared with DVS sorption isotherms/kinetics of H2O vs D2O (molecular-weight-based moisture content)",
    source_file="20736558.pdf (Valkonen, Lourencon, Lillqvist, Altgen & Rautkari 2026 Cellulose 33:5695); Fourier-Transform Infrared Spectroscopy/ (raw .sp + csv, truncated .ASC/.csv, absorbance, baselined, rubber-band, anchor-point-corrected and normalised csv; Origin .opju + xlsx analysis); Dynamic Vapor Sorption/ (DVS xlsx, slopes)",
    confidence=0.8,
)

R["20793770"] = dict(
    modality="Real-time UV-Vis-NIR extinction spectroscopy (fibre spectrometer read by PySpecTrace) of Au-Ag nanoparticle plasmonic response over time",
    spectral_range_original_min=176.074, spectral_range_original_max=1328.184, spectral_range_original_unit="nm",
    num_spectral_channels=4094, sampling_interval=0.283, sampling_interval_unit="nm",
    num_samples=1,
    num_spectra=236,  # time frames (~1 h at ~15 s intervals)
    num_spectral_values=966184,
    spectral_target_relationship="Lorentzian tracking of the LSPR peak (~518 nm, red flank masked by a laser notch filter), interband absorbance (400-410 nm) and 500 nm extinction vs time -> sensorgram demonstrating PySpecTrace peak/non-peak tracking for kinetics of AuAg nanostructures",
    source_file="20793770.pdf (Anam, Leonardy, Suwardi, Baldi, Nugroho & Darmadi 2026 F1000Research 15:1187, software tool article); Case-study.zip: AuAg_spectra/Converted_Spectrum.npz (frame, wavelengths 4,094, intensities 236 x 4,094, time, deltatime), processed_spectra/ 236 txt; __MACOSX junk",
    confidence=0.7,
)

R["20794243"] = dict(
    modality="Computed harmonic IR spectra (Gaussian DFT frequency + IR intensity) of polyoxometalate anions (Lindqvist, Keggin, Wells-Dawson, deca-/hepta-/octa-metalates) - modelled stick spectra, not measured",
    spectral_range_original_min=0, spectral_range_original_max=1047.357, spectral_range_original_unit="cm-1",
    num_samples=22,  # POM structures with OPT_IR jobs
    num_spectra=22,
    num_spectral_values=3120,  # normal modes with frequency + IR intensity (one small imaginary mode, -10 cm-1)
    spectral_target_relationship="M=O terminal (~950-1050 cm-1), M-O-M bridging and X-O (central heteroatom) stretching frequencies/intensities vs metal (W, Mo, V, Nb, Ta) and heteroatom (Al, Si, P) -> validation of optimised geometries and QM-derived force-field parameters (charges Q-models CHELPG/MDC) for MD simulations of POMs",
    source_file="20794243.pdf (Segado-Centellas, Masip-Sanchez & Bo 2026 Research Square data descriptor 'POMsDB'); POMsDB_dataset.zip: 88 ioChem-BD calculation folders (output.cml, input .in, mets/metadata xml, thumbnails) incl. 22 *_OPT_IR jobs with cc:frequency/cc:irintensity arrays; 264 force-field zips (GROMACS itp/gro/pdb)",
    confidence=0.6,
)

R["21245297"] = dict(
    modality="FTIR absorbance spectroscopy (Thermo Nicolet 5700, DTGS/KBr) of recycled PVC/PVAc waste, extruded filament and 3D-printed specimens during accelerated xenon-arc weathering (0-995 h) (+ DHC, GPC, DSC, TGA, mechanical tests)",
    spectral_range_original_min=399.199, spectral_range_original_max=4000.442, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.928, sampling_interval_unit="cm-1 (1,869 pts; crushed-waste colour fractions 0.482 cm-1, 7,468 pts)",
    num_samples=13,  # crushed waste, filament, 7 weathering times, 4 waste colour fractions
    num_spectra=13,  # 9 SPA/xlsx spectra + 4 crushed-waste colour csv
    num_spectral_values=46693,
    spectral_target_relationship="Band-area ratio of C=O/C=C (1849-1500 cm-1) to C-H (3049-2750 cm-1) vs weathering time -> photo-oxidation and dehydrochlorination of PVC/PVAc printed parts, consistent with dehydrochlorination (DHC) stability time, GPC molar mass, Tg and tensile changes for PCB-substrate use",
    source_file="21245297.pdf (Chodounska, Kaderabkova, Fros, Kalouskova, Cadek, Zdrahal, Reinsteinova, Brozek, Hrdlicka & Uricar 2026 Polym. Bull. 83:590); 002_Data_repository.zip: FTIR/ 9 .SPA + 001_FTIR.xlsx (spectra + band-area ratios), Crushed_waste/FTIR 4 csv, DHC, GPC (.arw/.afe8/csv), DSC, TGA, tensile, compression, sheet-resistance, 3D-print profiles",
    confidence=0.85,
)

R["21245871"] = dict(
    modality="Liquid ATR-FTIR absorbance spectroscopy (Thermo Nicolet iS10, single-bounce diamond ATR) of neat hydrocarbons/alcohols, aviation and automotive fuels and their blends (OSU and LBNL)",
    spectral_range_original_min=399.922, spectral_range_original_max=4000.188, spectral_range_original_unit="cm-1",
    spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.241, sampling_interval_unit="cm-1 (211 spectra 650-4000 cm-1, 13,898 pts; 37 spectra 400-4000 cm-1, 14,936 pts)",
    num_samples=236,  # neat compounds, fuels and blends (12 extra -REP# replicate files)
    num_spectra=248,
    num_spectral_values=3485110,
    spectral_target_relationship="Functional-group absorbance (CH3/CH2 stretches 2850-2960, aromatic C-H and ring modes, O-H of alcohols) of neat components and blends -> statistical model (Lasso/PLS-type regression on IR absorbance) predicting research octane number (RON) of gasoline-range fuels without CFR engine tests",
    source_file="21245871.pdf (Daly, Niemeyer, Cannella & Hagen, 'Predicting fuel research octane number using Fourier-transform infrared absorption spectra of neat hydrocarbons', Fuel / arXiv preprint); FTIR-ATR-spectra-OSU-LBNL.zip: 248 CSV (wavenumber, absorbance), README.txt, complete-description.pdf; __MACOSX duplicates",
    confidence=0.85,
)

R["21246732"] = dict(
    modality="VIS-NIR diffuse reflectance spectroscopy (Foss NIRSystems 6500) of arctic heath soil samples from a long-term field experiment at Abisko, Sweden",
    spectral_range_original_min=400, spectral_range_original_max=2498, spectral_range_original_unit="nm",
    num_spectral_channels=1050, sampling_interval=2, sampling_interval_unit="nm",
    num_samples=108,  # 36 plots x (2 surface subsamples 0-5 cm + 1 at 5-10 cm)
    num_spectra=108,
    num_spectral_values=113400,
    spectral_target_relationship="NIR spectra (log 1/R) vs soil organic matter (loss on ignition) and ergosterol (fungal biomass, HPLC) -> PLS regression calibrations; fertilisation/warming treatments dominate spectral variation; NIR and fluorescence relate to microbial and chemical soil properties",
    source_file="21246732.pdf (Rinnan & Rinnan 2007 Soil Biol. Biochem. 39:1664, doi:10.1016/j.soilbio.2007.01.022); nir_arctic_soil_abisko_sweden.zip: NIRsoil.mat (PLS_Toolbox dataset objects soil 108 x 1,050 and soilref SOM, Ergogdw), README.md",
    confidence=0.9,
)

R["21502969"] = dict(
    modality="Computed anharmonic IR spectra (VQDPT, B3LYP-D3/6-31++G(d,p) 3MR-QFF/hybrid PES) of Ace-Ala-O-Bzl peptide conformers - modelled stick spectra, not measured",
    spectral_range_original_min=442.704, spectral_range_original_max=3467.129, spectral_range_original_unit="cm-1",
    num_samples=11,  # conformers (5-5_t, 5-5_g+/-, 5-5_IV, 5-5_V, 5-5_prime_I/II, pi-7a, pi-7a_II, pi-7e, pi-7e_II)
    num_spectra=22,  # 2 VQDPT band files per conformer
    num_spectral_values=1786,  # transitions (frequency, IR intensity, configuration)
    spectral_target_relationship="Anharmonic NH/CO stretch and fingerprint transitions of REMD-sampled conformers compared with IR-UV double-resonance spectra via spectral similarity scores -> unbiased assignment of gas-phase peptide conformer structures (consistent with Gloaguen et al. 2010)",
    source_file="21502969.pdf (Otaki, Sugita & Yagi, 'Unbiased structure assignment of peptide conformers: application of similarity scores to Ace-AA-O-Bzl vibrational spectra'); 5_anharmonic_vibrational_analysis.tar.gz (QFF .pot/.dipole, VQDPT *.data band lists per conformer), 3_build_conformer, 4_common_and_unique_structures (pdb); 00_README.md, 1_MM-REMD (2.3 GB), 2_QM-REMD (2.3 GB) and 6_single-point_energy are zero-filled downloads with leftover .part files",
    confidence=0.55,
)
