# Batch2 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (now C:\Users\Admin\RAG\papers2\<id>.pdf) + dataset folder (now E:\Batch2_datasets\<id>_<title>).
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

R["7482510"] = dict(
    modality="ATR-FTIR spectroscopy (diamond ATR, portable Agilent 4500) of aqueous and dried blood fractions",
    spectral_range_original_min=649.088, spectral_range_original_max=4000.54, spectral_range_original_unit="cm-1",
    num_spectral_channels=1803, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.8599, sampling_interval_unit="cm-1",
    num_samples=32,  # 32 volunteers P1-P32 (paper Table I: 30 retained after 2 noisy outliers) x whole blood/plasma/RBC x aqueous/dry
    num_spectra=575,  # 543 sample spectra (WB/PL/RBC x AQ/D, 2-3 technical replicates) + 19 water + 13 background
    num_spectral_values=575 * 1803,
    spectral_target_relationship="ATR-FTIR absorbance of whole blood, plasma and red blood cells (aqueous and dry) -> G6PD deficiency status (normal / partially / fully deficient); MCR-ALS water correction + SG 2nd derivative + SNV -> PLS-DA (aqueous RBC best: sensitivity 0.80, specificity 0.80, 1450-950 cm-1)",
    source_file="7482510.pdf; 575 *.spc (Galactic SPC, absorbance) + 575 paired *.a2r (Agilent MicroLab raw), named P<n>_<sex>_<class>_<WB|PL|RBC>_<AQ|D>_<rep>_<timestamp>",
    confidence=0.9,
)

# ---------------------------------------------------------------------------
# IODP JOIDES Resolution shipboard data (papers = Proceedings volume front matter /
# expedition summary chapters; methods are standard JRSO shipboard procedures)
# ---------------------------------------------------------------------------


def _iw(rid, exp, nrows, nholes, sites, depth_max, nparams, spec, paper):
    R[rid] = dict(
        modality="None (no spectra): IODP interstitial-water geochemistry composite report (ICP-AES emission lines, ion chromatography, titration, refractometry" + (", colorimetric UV-Vis" if spec else "") + ")",
        num_samples=nrows,
        spectral_target_relationship=f"No spectral data; {nparams} pore-water parameters (alkalinity, pH, salinity, major/minor ions and elements" + (", NH4+/PO4 by UV-Vis colorimetry" if spec else "") + f") vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}) -> diagenesis, sulfate reduction, fluid-rock exchange",
        source_file=f"{paper} (IODP Proceedings Vol. {exp}); IWREPORT-README.txt; per-hole IWREPORT csv",
        confidence=0.85,
    )


_iw("7502431", 350, 69, 3, "U1436-U1437", 693.41, 24, True, "7502431.pdf")
_iw("7504787", 376, 13, 5, "U1528-U1530", 427.0, 31, False, "7504787.pdf")
_iw("7708617", 385, 519, 23, "U1545-U1552", 535.1, 41, True, "7708617.pdf")
_iw("8257104", 382, 117, 7, "U1534-U1538", 670.75, 26, True, "8257104.pdf")


def _spec(rid, exp, analytes, nvals, nsamples, nholes, sites, depth_max, files, paper, conf=0.85, note=""):
    wl = [w for a, w in (("ammonium", 640), ("phosphate", 885), ("sulfide", 670)) if a in analytes]
    R[rid] = dict(
        modality="Single-wavelength UV-Vis colorimetric absorbance (Agilent Cary 100/300) of interstitial water: " + ", ".join(f"{a} {w} nm" for a, w in zip(analytes, wl)),
        spectral_range_original_min=min(wl), spectral_range_original_max=max(wl), spectral_range_original_unit="nm",
        num_spectral_channels=len(wl), spectral_resolution=1.5, spectral_resolution_unit="nm (spectral bandwidth, SBW)",
        num_samples=nsamples,
        num_spectral_values=nvals,  # concentration results (one absorbance reading per analyte per sample)
        spectral_target_relationship=f"Absorbance at fixed analytical wavelengths vs external standard curve -> pore-water {'/'.join(analytes)} concentrations (uM) vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}); Beer-Lambert linear calibration" + note,
        source_file=f"{paper} (IODP Proceedings Vol. {exp}); SPEC-README.txt; {files}",
        confidence=conf,
    )


_spec("8011387", 369, ["ammonium"], 205, 205, 7, "U1512-U1516", 687.35,
      "data_by_hole/*-SPEC.csv (+ scaled/splice variants); supplementary raw_data_files *.BAB + *.xlsx calibration workbooks", "8011387.pdf")
_spec("8264004", 382, ["ammonium", "phosphate"], 232, 116, 7, "U1534-U1538", 670.75,
      "data_by_hole/*-SPEC.csv (+ scaled/splice variants); supplementary raw_data_files (Cary Advanced Reads csv, .MAB/.BAB, xlsm workbooks)", "8264004.pdf")
_spec("7806744", 396, ["ammonium", "phosphate"], 661, 333, 20, "U1565-U1574", 433.74,
      "SPEC.zip: data_by_hole/*-SPEC.csv; supplementary_material raw Cary csv + *_RESULTS.xlsm", "7806744.pdf")
_spec("7708644", 385, ["ammonium", "phosphate", "sulfide"], 1197, 466, 23, "U1545-U1552", 535.1,
      "SPEC/data_by_hole (25 per-hole CSV, 1,197 results); supplementary_material/raw_data_files (100 Cary .BAB, 40 Advanced Reads csv, 44 .xlsm + 1 .xlsx calibration workbooks)", "7708644.pdf",
      note="; sulfide by methylene blue at 670 nm (raw Cary reports)")


def _rsc(rid, exp, nspectra, nsections, nholes, sites, depth_max, sensor, paper):
    R[rid] = dict(
        modality="VIS diffuse reflectance spectroscopy and colorimetry (RSC) of split-core section halves (Ocean Optics QE Pro + integrating sphere on SHMSL)",
        spectral_range_original_min=390, spectral_range_original_max=730, spectral_range_original_unit="nm",
        num_spectral_channels=171, sampling_interval=2, sampling_interval_unit="nm",
        num_samples=nsections,  # core section halves with spectra
        num_spectra=nspectra, num_spectral_values=nspectra * 171,
        spectral_target_relationship=f"% reflectance spectra (white/dark-referenced) of sediment/rock core surfaces -> CIE XYZ, L*a*b*, chroma, hue vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}) for lithostratigraphy, cyclostratigraphy and hole-to-hole correlation",
        source_file=f"{paper} (IODP Proceedings Vol. {exp}); RSC-README.txt; data_by_hole/*-RSC.csv; raw_data_files norm_*/raw_*_rsc.csv + *.RSC; configuration *.ini ({sensor})",
        confidence=0.85,
    )


_rsc("7504139", 376, 10871, 278, 12, "U1527-U1531", 448.66, "QEPRO QEP00732", "7504139.pdf")
_rsc("7708664", 385, 143078, 3569, 26, "U1545-U1552", 540.04, "QEPRO QEP02181", "7708664.pdf")
_rsc("8263963", 382, 129684, 2471, 18, "U1534-U1538", 672.86, "QEPRO QEP02181", "8263963.pdf")

# ---------------------------------------------------------------------------

R["7515083"] = dict(
    modality="FTIR absorbance spectroscopy (amide I/II region) of purified proteins (+ cryo-EM, fluorescence anisotropy, SDS-PAGE gels)",
    spectral_range_original_min=1448.44, spectral_range_original_max=1751.24, spectral_range_original_unit="cm-1",
    num_spectral_channels=158, sampling_interval=1.9287, sampling_interval_unit="cm-1",
    num_samples=4,  # RecF WT, RecF A170W, RecR WT, RecR A147W
    num_spectra=4, num_spectral_values=632,
    spectral_target_relationship="Normalised amide I/II FTIR spectra of Thermus thermophilus RecF/RecR wild type vs Trp interface mutants -> secondary-structure content / structural integrity (OPUS-QUANT2 vs protein reference library); supports cryo-EM-derived RecF-RecR interface mutagenesis",
    source_file="7515083.pdf (Extended Data Fig. 9); FT-IR.zip (4 *_N.dpt two-column spectra); FluorescenceAnisotropyIII.zip; Glycerol gradient.zip (31 gel TIFFs); Pull-downII.zip",
    confidence=0.85,
)

R["7536702"] = dict(
    modality="VIS-NIR hyperspectral imaging reflectance (MoHIS monochromator + VIS CCD/NIR MCT cameras) of sublimating salty ice analogues in SCITEAS-2 vacuum chamber",
    spectral_range_original_min=0.38, spectral_range_original_max=2.45, spectral_range_original_unit="um",
    num_spectral_channels=294,  # 290-294 bands (0.38-2.45 um); SPIPA-B pure water/NaCl series: 84 bands 1.302-1.80 um
    spectral_resolution=6.5, spectral_resolution_unit="nm FWHM (<=1700 nm; 13 nm beyond)",
    sampling_interval=6, sampling_interval_unit="nm (NIR; 15 nm in VIS)",
    num_samples=25,  # NaCl, MgSO4, MgCl2, Na2SO4 x 3 concentrations x {slab, granular} + pure-water control
    num_spectra=2038,  # ROI-mean spectra (507 files x 1-5 ROI columns)
    num_spectral_values=575634,
    spectral_target_relationship="Time series of VIS-NIR reflectance during sublimation of salty ice slabs and granular ices (NaCl, MgSO4, MgCl2, Na2SO4, 3-33 wt%) -> normalised integrated band area (NIBA), band centroid and depth of 1.5/2.0 um hydration bands vs residual water ice and salt hydrate state; comparison with icy-moon (Europa) spectra",
    source_file="7536702.pdf; Cerubini_PSS_2022.zip (22 experiment folders, 507 *_cube_N_spectra_mean.txt: wavelength (um) + ROI reflectance columns)",
    confidence=0.85,
)

R["7537055"] = dict(
    modality="VIS-NIR reflectance spectroscopy (SCITEAS imaging spectro-goniometer, monochromator + VIS/NIR cameras) of CO2/H2O ice and Mars soil simulant mixtures",
    spectral_range_original_min=415, spectral_range_original_max=2398, spectral_range_original_unit="nm",
    num_spectral_channels=279,  # full ("hyperspectral") scans; quick ("multispectral") scans 130 bands 445-2326 nm
    spectral_resolution=6.5, spectral_resolution_unit="nm FWHM (13 nm >1700 nm)",
    num_samples=8,  # 8 experiment sets (ternary mixtures, CO2 frost interlayers, CO2 sizes, CO2+JSC Mars-1 400-800 um, CO2 slab frost)
    num_spectra=108, num_spectral_values=18510,  # 78 x 130 + 30 x 279
    spectral_target_relationship="Reflectance factor (i=5, e=0) of CO2 ice, H2O ice and JSC Mars-1 binary/ternary mixtures and sublimation sequences -> detectability of CO2 ice (1.435/2.28 um bands) vs H2O 1.5/2.0 um bands; spectral parameters and simulated CaSSIS colours to discriminate ices and dust on Mars",
    source_file="7537055.pdf; Yoldi2022_spectral_data.zip (108 SSHADE-style CSV: geometry, reflectance_factor, std, bandpass_central/FWHM, time; multispectral/ and hyperspectral/ per experiment; __MACOSX junk)",
    confidence=0.85,
)
R["7599269"] = dict(
    modality="MIR (FTIR, absorbance) and VIS-NIR (reflectance) soil spectral library (OSSL v1.2, harmonised multi-source) + ensemble ML calibration models",
    spectral_range_original_min=600, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",  # MIR; VisNIR 350-2500 nm @ 2 nm (1076 ch)
    num_spectral_channels=1701, sampling_interval=2, sampling_interval_unit="cm-1 (MIR); VisNIR 2 nm",
    num_samples=135000,  # ~135k site/layer rows (KSSL 86.6k, LUCAS 40.2k, ICRAF-ISRIC 4.1k, AfSIS1 1.9k, CAF 1.6k, others)
    num_spectra=156694,  # 91,631 MIR + 65,063 VisNIR scans (Zenodo description)
    num_spectral_values=91631 * 1701 + 65063 * 1076,
    spectral_target_relationship="MIR/VisNIR soil spectra (compressed to PCs) -> 17 soil properties (OC, N, clay/silt/sand, pH, CEC, exchangeable Ca/Mg/K/Al, CaCO3, gypsum, bulk density, base saturation) via ensemble ML (ranger, xgboost, Cubist, glmnet stacked by lm); 102 models, R2 0.43-0.98 (e.g. log OC 0.97-0.98 MIR)",
    source_file="7599269.pdf (Summerauer et al. 2021, central African SSL = OSSL source CAF.SSL); ossl_all_L0/L1_v1.2.qs, ossl_mir_L0, ossl_visnir_L0, ossl_soillab/soilsite (R qs); v1 *.rds; ossl_models.zip (102 model .rds + resultsFit.txt + accuracy plots, pca.ossl)",
    confidence=0.75,
)

R["7613510"] = dict(
    modality="Solid-state NMR spectroscopy (13C CP-MAS, 13C multiCP-MAS, 13C/15N CP-MAS after 13CO2 dosing) of amine-functionalised covalent organic frameworks",
    num_samples=3,  # three MestReNova documents (each may hold several spectra)
    spectral_target_relationship="13C/15N ssNMR chemical shifts of COF before/after 13CO2 exposure -> identification of chemisorbed CO2 species (carbamate / carbamic acid / bicarbonate) and degree of amine functionalisation (quantitative multiCP)",
    source_file="7613510.pdf (Zhou et al. 2024 Nature, COF-999 - related paper; dataset README cites Lyu et al. 2022 JACS, doi:10.1021/jacs.2c05382); 3 *.mnova (proprietary MestReNova) + README_file.txt",
    confidence=0.5,
)

R["7662738"] = dict(
    modality="FTIR absorption (temperature ramps, titrations), temperature-jump IR (t-HDVE), 2D IR, 1H NMR temperature series and ITC of DNA/RNA dinucleotide-template complexes (+ MD simulations)",
    spectral_range_original_min=1485, spectral_range_original_max=1740, spectral_range_original_unit="cm-1",
    num_spectral_channels=530, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.5, sampling_interval_unit="cm-1 (exported grid)",
    num_samples=12,  # 12 template/complex constructs (TTg, TTgc, TTgd, TTo, UUg, ... with/without AA)
    num_spectra=535,  # FTIR: 12 T-ramps x 37 temperatures (509 pts) + 7 titrations x 13 ratios (530 pts); + 363 2D IR, 252 T-jump time-domain maps, 3 NMR ramps
    num_spectral_values=444 * 509 + 91 * 530,
    spectral_target_relationship="Base-pairing/stacking-sensitive IR bands (1545 G ring, 1605/1625 A ring, 1665-1695 C=O) vs temperature, AA:template ratio and time after T-jump -> AA dinucleotide binding fraction, Kd, dH/dS (two-state SVD fits) and dissociation rates 0.2-40 us (MEM inverse Laplace); validated by 1H NMR and ITC; MD explains coaxial stacking",
    source_file="7662738.pdf (bioRxiv 2023.04.10.536266); Experimental Data.zip (29 nested zips: FTIR, 2D IR, T jump time/rate domain, NMR, ITC CSV); Simulation Data.zip (34.5 GB GROMACS/OPES MD: xtc, tpr, cpt, edr)",
    confidence=0.85,
)
R["7665262"] = dict(
    modality="None (no spectra): confocal / TEM / dark-field microscopy images, flow-cytometry fluorescence intensities, ICP-AES gold quantification, RT-qPCR, western blots",
    num_samples=7,  # cell lines screened for EGFR (A549, A549-EGFR-GFP, ARPE-19, Caco-2, Calu-3, HT-29, HeLa, THP-1); main experiments in A549
    num_images=100,  # 31 TIFF + 68 PNG + 1 JPG figure panels
    spectral_target_relationship="No spectral data; EGF stimulation of A549 lung carcinoma cells -> altered uptake of 59/422 nm silica (BDP FL) and Au-PEG nanoparticles (flow-cytometry MFI, ICP-AES Au mass per cell), endocytosis markers (dextran, transferrin), Rac1/c-myc expression",
    source_file="NO PAPER SUPPLIED (Susnik et al., 'Altered nanoparticle uptake by lung carcinoma cells when stimulated with epidermal growth factor'); README file.txt; 100 figure images; 9 xlsx (MFI, ICP-AES, RT-qPCR, LDH, MTS, DLS)",
    confidence=0.6,
)

R["7671724"] = dict(
    modality="VNIR bidirectional reflectance (ASD FieldSpec 4) + Raman (Bruker BRAVO, 758/852 nm) + MIR FTIR-ATR (Bruker Alpha) + XRD of Mars-analog minerals with amorphous ferric sulfate",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",  # VNIR; Raman 300-3200 cm-1 @2; FTIR-ATR ~360-4000 cm-1
    num_spectral_channels=2151, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=77,  # 5 analogs x 3 grain sizes (15) + 60 desiccated AFS mixtures (R/RN/V/VN x 3 sizes x 5) + AFS, AFS+NaCl; + 6 reference sulfates
    num_spectra=382,  # VNIR 82 + 47 corrected, Raman 72 + 62 corrected, FTIR 76 + 43 corrected (sheet columns)
    num_spectral_values=650228,
    spectral_target_relationship="VNIR, Raman and ATR-FTIR spectra of basaltic glass, hematite, gypsum, nontronite, magnesite (<25, 25-63, 63-180 um) mixed with ferric sulfate (+/-NaCl) brines, desiccated at 11 % RH or vacuum -> detectability/masking of amorphous ferric sulfate and chloride phases on Mars (band positions, continuum-removed features; XRD % amorphous)",
    source_file="7671724.pdf; Hopkins et al. 2023 Data Final2.xlsx (sheets: Uncorrected/Corrected VNIR, Raman, FTIR; XRD data and baselines)",
    confidence=0.9,
)

R["7681840"] = dict(
    modality="Time-resolved step-scan FTIR difference spectroscopy (ns 532 nm laser flashes) of photosystem II membrane particles",
    spectral_range_original_min=929.33, spectral_range_original_max=1858.67, spectral_range_original_unit="cm-1",
    num_spectral_channels=4000, spectral_resolution=10, spectral_resolution_unit="cm-1 (step-scan; rapid-scan 4 cm-1)",
    sampling_interval=0.2324, sampling_interval_unit="cm-1 (heat-artefact spectrum grid)",
    num_samples=1,  # spinach PSII membrane particles (~1800 sample spots per refill, 7 months of averaging)
    num_spectra=1301,  # 10 flashes x 130 log-averaged delays (interferograms, 334 mirror positions) + 1 heat-artefact spectrum
    num_spectral_values=10 * 130 * 334 + 4000,
    spectral_target_relationship="Log-time-averaged step-scan interferograms after each of 10 flashes (-5.6 ms to 129 ms) -> S-state difference spectra (1800-1200 cm-1) and decay-associated spectra for proton removal (340 us) and O2 formation (2.5 ms); carboxylate (Glu65/Glu312) protonation bands 1700-1750 / 1565-1605 cm-1; DFT/MD reaction path",
    source_file="7681840.pdf (Research Square preprint rs-1210297/v1); Log_Averaged_Interferograms.xlsx (10 sheets 'Flash 1-10': time x 334 interferogram points); Heat_Artefact_Spectrum.xlsx (OD vs cm-1)",
    confidence=0.8,
)

R["7696956"] = dict(
    modality="ATR-FTIR polymer identification of microplastic particles (library matching) - spectra not included",
    spectral_range_original_min=500, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1", sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=83,  # 83 sediment samples (11 sites; lower/mid/upper beach, subaqueous, grab)
    num_spectra=931,  # particles identified by FTIR (sum of polymer table)
    spectral_target_relationship="ATR-FTIR spectra of picked particles (>250 um) matched to Shimadzu libraries (>=80 % match) -> polymer type counts per site (HDPE 401, PP 299, PS 157, PVC 27, EVA 23, ...); plus microscope counts of fibers/fragments/films per kg dry sediment",
    source_file="7696956.pdf; FulferandWalsh2023_Microplastic_Counts.xlsx (83 rows x 24 cols); FulferandWalsh2023_PolymerCharacterization.xlsx (13 polymer types x 7 sites)",
    confidence=0.85,
)
R["7706021"] = dict(
    modality="Computed (DFT B3LYP/6-311+G(d,p)) IR spectra of metabolite molecular ions + experimental infrared ion spectroscopy (IRIS / IRMPD with FELIX free-electron laser)",
    spectral_range_original_min=0, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=4001, spectral_resolution=45, spectral_resolution_unit="cm-1 FWHM Gaussian convolution (computed); experimental ~5 cm-1 steps",
    sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=4631,  # HMDB metabolites (MW < 210 Da) with computed ions
    num_spectra=11969,  # 11,765 computed convolved spectra ([M-H]- 2694, [M+H]+ 4503, [M+Na]+ 4568) + 204 experimental IRIS spectra
    num_spectral_values=11765 * 4001 + 204 * 264,
    spectral_target_relationship="IR spectrum of an m/z-selected ion -> metabolite identity / isomer annotation by cosine-similarity search of the in silico library (75 % top-1 identification of 189 experimental IRIS spectra, 97 % top-5); substructure search without m/z constraint",
    source_file="7706021.pdf (Houthuijs et al. 2023 Anal. Chem.); ComputedIRspectra.zip (11,765 x conv .xy, stick .xy, .xml with geometry/energies, .png); ExperimentalIRspectra.zip (204 .xy/.xml/.png); exp_vs_*.pdf comparison plots",
    confidence=0.9,
)

R["7706292"] = dict(
    modality="Transmission FTIR (MCT, purged chamber) of PTFE aerosol filters loaded with organosulfur compounds (+ gravimetry, IC, ICP-OES)",
    spectral_range_original_min=419.77, spectral_range_original_max=3998.42, spectral_range_original_unit="cm-1",
    num_spectral_channels=4896, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.3214, sampling_interval_unit="cm-1 (exported grid; 4527-5415 points per figure)",
    num_samples=4,  # MSA, HMS, MS, 2-MTS (one FTIR filter series each; 3-4 gravimetric filters per compound)
    num_spectra=62,  # Figs 2/4/7/9: 8 + 17 + 17 + 20 day-series spectra incl. blanks
    num_spectral_values=291167,
    spectral_target_relationship="FTIR absorbance of PTFE filters over 1-132 days of storage -> stability/chemical change of methanesulfonic acid, hydroxymethanesulfonate (converts to sulfate), methyl sulfate and 2-methyltetrol sulfate; compared with gravimetric mass, IC and ICP-OES sulfur recovery (IMPROVE network suitability)",
    source_file="7706292.pdf (Anunciado et al. 2023 AMT); Figure_1-9.xlsx (gravimetric, FTIR day-series, IC); README.md",
    confidence=0.9,
)

R["7706625"] = dict(
    modality="13C CP/MAS solid-state NMR (+ XRD, SEM) of pretreated lignocellulosic biomass (no FTIR in archive)",
    spectral_range_original_unit="ppm",
    num_spectral_channels=3584,  # TD; SW 405 ppm at 100.6 MHz 13C
    num_samples=15,  # 3 biomass types (SP, WB, WS) x 5 pretreatments (EtOH, H2O, H2SO4, NaCS, NaOH)
    num_spectra=30,  # 15 NMR + 15 XRD patterns (2theta 4.85-90 deg, 3281 pts); + 680 SEM TIFF images
    num_images=680,
    spectral_target_relationship="13C CP/MAS NMR (cellulose C1/C4 crystalline vs amorphous, lignin aromatic/methoxyl) and XRD crystallinity of pine/beech/wheat-straw biomass after microwave-assisted pretreatments (NaCS hydrotrope, NaOH, H2SO4, EtOH, H2O) -> delignification and cellulose accessibility for fermentation",
    source_file="7706625.pdf (Mikulski & Klosowski 2022 Sci. Rep. - earlier related study); Stage IV - spectra.rar (NMR/101-115 Bruker TopSpin folders, XRD/*.txt, SEM/*.tif); Stage III.rar, Stage IV.rar (statistics .docx, Polish)",
    confidence=0.6,
)
R["7741369"] = dict(
    modality="Ultrasound-guided time-domain diffuse NIR spectroscopy (TD-NIRS, 8 wavelengths) + diffuse correlation spectroscopy (DCS, 785 nm) of human sternocleidomastoid muscle - derived optical/hemodynamic parameters",
    spectral_range_original_min=637, spectral_range_original_max=1050, spectral_range_original_unit="nm",
    num_spectral_channels=8,  # 637, 669, 722, 825, 841, 905, 971, 1050 nm (wavelength.mat)
    num_samples=65,  # subjects (healthy + thyroid-nodule patients, LUCA project)
    spectral_target_relationship="Absolute mua/mus' at 8 wavelengths (TD-NIRS) and blood-flow index (DCS) -> HbO2, Hb, THC, StO2, BFi, MRO2 of SCM muscle; linear mixed-effects models vs age, BMI, sex, muscle depth (US), side, nodule presence",
    source_file="7741369.pdf (arXiv/medRxiv preprint, Cortese et al.); open_data_Zenodo_rev1.zip (MATLAB table_upto66_hemat_corrected_muscle.mat, demographics_table.mat, wavelength.mat, scripts; R scripts + LME result xlsx; figures)",
    confidence=0.75,
)

_NANO = dict(
    modality="Nano-FTIR (s-SNOM, 2nd-harmonic demodulated interferograms) hyperspectral imaging + compressive subsampling reconstructions",
    num_spectral_channels=1024,  # interferogram points (dz ~1.39 um); spectral resolution 7.03 cm-1 after FT
    spectral_resolution=7.03, spectral_resolution_unit="cm-1",
    num_samples=1,  # edge of ultrathin Ga film beneath epitaxial graphene on 6H-SiC
    num_spectra=961,  # 31 x 31 pixels (full cube); + 5 subsampling masks and 5 low-rank reconstructions of same size
    num_pixels=961, image_height=31, image_width=31,
    num_spectral_values=961 * 1024,
    spatial_resolution=66.7, spatial_resolution_unit="nm pixel pitch (2 um x 2 um field, 31 x 31 grid)",
    spectral_target_relationship="Fully sampled 31x31x1024 nano-FTIR interferogram cube (ground truth) vs Lissajous, triangle-Lissajous, random-reflection, white-line and random subsampling (~10 %) -> low-rank matrix reconstruction quality (RMSE, SSIM); phononic SiC resonance ~920 cm-1 and metallic Ga response",
    confidence=0.85,
)
R["7764082"] = dict(_NANO, source_file="7764082.pdf (Metzner et al. 2022 IEEE TIM 71:4506208); DFG-routing-for-zenodo/: Ga-G1125_Data.mat (984,064 values), 4 *_Points_*_10.mat masks, UndersampledData.mat, 5 Result_*_10.mat (Xrec 961x1024), plot scripts (.py/.m), figure PDFs")
R["7781090"] = dict(_NANO, source_file="7781090.pdf (same paper as 7764082); dataset byte-identical to record 7764082 (18 files, same MD5) - second Zenodo version", confidence=0.8)

R["7782757"] = dict(
    modality="Confocal Raman imaging + ATR/transmission FTIR + spatially resolved (z-axis) 1H/7Li/19F NMR of salt-salt aqueous biphasic systems",
    spectral_range_original_min=684, spectral_range_original_max=3950, spectral_range_original_unit="cm-1",  # Raman TFSI 684-1200 and OH 2830-3950 cm-1; FTIR 400-4000 cm-1
    spectral_resolution=15, spectral_resolution_unit="cm-1 (Raman)",
    num_samples=4,  # 2.6 m LiTFSI-5.2 m LiCl, 5 m LiTFSI-10 m LiCl, 5 m LiTFSI-10 m HCl (+ 3 m-6 m) biphasic systems
    num_spectra=958,  # Raman: 2.6m system 50 OH + 300 TFSI line spectra + 4 phase-averaged; HCl system 300 OH + 300 TFSI; + 4 FTIR (+ 9 NMR z-profiles)
    num_images=2, image_height=300, image_width=300,
    spatial_resolution=300, spatial_resolution_unit="nm lateral (800 nm axial)",
    spectral_target_relationship="Raman TFSI (~740 cm-1: free/CIP/aggregate) and OH-stretch (3230/3365/3570 cm-1) band intensities across liquid-liquid interface -> sigmoidal concentration profiles, interface thickness 2-11 um (negative adsorption); FTIR of separated phases; VT-NMR ion partition vs temperature; binodal curves, surface tension",
    source_file="7782757.pdf (Degoulange et al., PNAS preprint); Data_ABS_PNAS_Degoulange.zip (Raman_imaging .npy maps/spectra/fits, FTIR 4 CSV, NMR 9 z-profile txt, Binodal_curves txt, Surface_tensions txt); Binodal_LiTFSI-LiCl_LiTFSI-side.txt",
    confidence=0.8,
)
R["7808571"] = dict(
    modality="UV-Vis absorption spectroscopy (98 % H2SO4 solutions) + 1D/2D 1H, 13C, 15N NMR (HMBC, HMQC) of nucleic acid bases in concentrated D2SO4",
    spectral_range_original_min=190, spectral_range_original_max=600, spectral_range_original_unit="nm",
    num_spectral_channels=411, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=8,  # adenine, cytosine, guanine, thymine, uracil, 2,6-diaminopurine, purine, pyrimidine
    num_spectra=16,  # UV-Vis: 8 bases x (t=0.5 h, t~24 h); + ~120 NMR datasets (90 zipped experiments incl. 2-week series)
    num_spectral_values=16 * 411,
    spectral_target_relationship="UV-Vis absorbance (peak positions/intensity at t0 vs 24 h) and 1H/13C/15N chemical shifts in 81-98 % D2SO4 (vs DMSO-d6) after up to 2 weeks -> stability (no degradation) and protonation state of nucleic acid bases under Venus-cloud acid conditions",
    source_file="7808571.pdf (Seager et al., PNAS 2023 manuscript); UV-VIS_plots-data-code-tables DATASET S1.zip (16 Helios Omega CSV, plotpaper.py, peak-wavelength xlsx); ORIGINAL NMR DATA_DATASET S2.zip (90 nested Bruker experiment zips); dataset description .docx",
    confidence=0.85,
)

R["7875469"] = dict(
    modality="IR absorption + vibrational circular dichroism (VCD) spectroscopy of monoterpenes, monoterpene mixtures and essential oils (CDCl3 solution)",
    spectral_range_original_min=0, spectral_range_original_max=7895.99, spectral_range_original_unit="cm-1",  # exported FFT axis; analysed region 950-1800 cm-1
    num_spectral_channels=4096, sampling_interval=1.9282, sampling_interval_unit="cm-1",
    num_samples=54,  # 36 pure terpenes + 14 mixtures of known composition + 4 essential oils
    num_spectra=104,  # 54 IR + 50 VCD (3 pure terpenes IR only)
    num_spectral_values=104 * 4096,
    spectral_target_relationship="IR and VCD spectral markers (950-1800 cm-1) of 36 chiral/achiral monoterpenes -> identification and absolute-configuration assignment of components in mixtures and essential oils (tea tree, rosemary, lavender, ylang-ylang) without DFT; ML model trained on in-silico noisy linear mixtures (IR model 29/31 correct, VCD 25)",
    source_file="7875469.pdf (Vermeyen, Batista, Valverde, Herrebout & Batista Jr., RSC preprint); Spectra.zip (pure_terpenes 36, mixtures_known_composition 14 + mixture_labels.txt, oils 4 CSV: wavenumber, IR, VCD)",
    confidence=0.85,
)

R["7939919"] = dict(
    modality="Computed (DFT) infrared emission/absorption band spectra of polycyclic aromatic hydrocarbons + random-forest feature importance of molecular fragments (ECFP)",
    spectral_range_original_min=2.761, spectral_range_original_max=1172.745, spectral_range_original_unit="um",
    num_spectral_channels=323,  # spectral bins ('bins' in Dataset.json)
    num_samples=14124,  # 2,925 neutral PAHs from NASA Ames PAHdb + 11,199 larger PAHs computed by authors (B3LYP/6-31G, scale 0.961)
    num_spectra=14124, num_spectral_values=14124 * 323,
    spectral_target_relationship="Binned IR spectra of 14,124 PAHs vs extended-connectivity fingerprints (10,632 fragments, Rcut=3) -> random-forest importance of fragments for each band (2.76-1173 um), compared with unidentified infrared emission (UIE) bands 3.3, 6.2, 7.7, 8.6, 11.2, 12.7 um",
    source_file="7939919.pdf (Meng, Zhang, Liang & Wang 2023, arXiv:2307.08277); Supplementary_Data_IV.zip (Dataset.json: Dataset_nasa, Dataset_yc, bins; ECFPs.json; RF_importance.py); Supplementary_Data_III.zip (11,199 .xyz + information_for_molecules.csv with SMILES); Supplementary_Data_I/II.pdf importance tables",
    confidence=0.85,
)
R["7945557"] = dict(
    modality="Airborne VNIR-SWIR imaging spectroscopy (HySpex) - plot-mean canopy reflectance of grazed grasslands",
    spectral_range_original_min=414.94, spectral_range_original_max=2350.96, spectral_range_original_unit="nm",
    num_spectral_channels=317, sampling_interval=3.6261, sampling_interval_unit="nm (VNIR; ~6 nm SWIR)",
    num_samples=104,  # 1 m2 plots on Oland (Sweden) in 3 grassland age classes
    num_spectra=104, num_spectral_values=104 * 317,
    spectral_target_relationship="Plot-mean canopy reflectance (317 bands) vs presence/absence of 100 plant species and their habitat-preference values (phosphorus, ammonium, nitrate, S1-S4 axes) and grassland age class (5-15, 16-50, >50 yr grazing) -> community-weighted habitat indicators; PLS / PLS-DA (paper: 85 % age-class accuracy with selected bands)",
    source_file="7945557.pdf (Mockel et al. 2014 Remote Sens. 6:7732 - earlier related study on same plots); Hyspex.csv (104 x 317 bands); Plant_species_data.csv; Species_info.csv; Plots_info.csv (SWEREF99TM); README.md",
    confidence=0.8,
)

R["7946420"] = dict(
    modality="Machine-learned one-electron reduced density matrices (QMLearn) - computed electronic-structure databases, ML/DFT molecular dynamics with dipoles -> anharmonic IR spectra (+ reference IR spectra)",
    spectral_range_original_min=450, spectral_range_original_max=3974.97, spectral_range_original_unit="cm-1",  # reference IR txt (benzene 575-3975 @0.06; 1-propanol 455-3792; 2-propanol 450-3966 @4)
    num_samples=8,  # molecules: H2O, NH3, CO2, CH3OH, C6H6, 1-propanol, 2-propanol, N2/CO
    num_spectra=3,  # reference IR spectra; MD trajectories (31 x 300 K xyz with dipoles) to derive computed IR spectra
    num_spectral_values=56417 + 3751 + 880,
    spectral_target_relationship="Learned 1-rdm gamma[v] from external potential -> energies, forces, dipoles, band gaps; ML-driven MD dipole autocorrelation -> anharmonic, temperature-dependent IR spectra of benzene and propanols compared with reference spectra",
    source_file="7946420.pdf (Shao, Paetow, Tuckerman & Pavanello 2023 Nat. Commun. 14:6281); qmlearn_database.zip (15.9 GB: db/*.hdf5 training sets up to 41,472 configurations, ir/<mol>/300K/*.xyz MD with dipoles, *-IR.txt reference spectra, notebooks, md logs, test_100)",
    confidence=0.7,
)

R["7956450"] = dict(
    modality="UV-Vis absorption spectra of chromatography fractions (+ FPLC UV traces, LC-MS/MS raw files, AFM topography) for a microalgal PETase",
    spectral_range_original_min=200, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=602, sampling_interval=1, sampling_interval_unit="nm (~1 nm)",
    num_samples=5,  # red fractions 'red', 'red1' and cytochrome c references cytc1-3
    num_spectra=5, num_spectral_values=5 * 602,
    num_images=4,  # AFM Gwyddion files: PET/PS (PCP) control vs enzyme-treated
    spectral_target_relationship="UV-Vis of red cation-exchange fractions vs cytochrome c references -> identification of co-purified cytochrome c (Soret/Q bands) with PETase; AFM roughness change of PET/PS films after incubation (PS +17.5 nm rms) -> PETase activity; HPLC of BHET/TPA products",
    source_file="7956450.pdf (Di Rocco et al., Research Square preprint); Frazioni rosse PETase UV.xls; 2 AKTA chromatogram .xls; 3 Thermo LC-MS .raw (Q Exactive); 4 .gwy AFM; morphology parameters .xlsx; 17 chromatogram PDFs (BHET, TPA, PET)",
    confidence=0.7,
)

R["7980675"] = dict(
    modality="NIR hyperspectral imaging (Specim SWIR camera, reflectance) of heat-treated and brown-rot-decayed Scots pine + dynamic vapour sorption",
    spectral_range_original_min=935.67, spectral_range_original_max=2547.81, spectral_range_original_unit="nm",
    num_spectral_channels=288, spectral_resolution=12, spectral_resolution_unit="nm FWHM", sampling_interval=5.6, sampling_interval_unit="nm",
    num_samples=36,  # sample-mean spectra: Ref / 200C / 230C x C. puteana / R. placenta x 6 decay levels
    num_spectra=36, num_spectral_values=36 * 288,
    spectral_target_relationship="Mean NIR reflectance of decayed wood (1400-2400 nm, SNV, PCA) -> early-decay chemistry (hemicellulose loss 1906 nm, cellulose/lignin changes) explaining increased hygroscopicity of heat-treated wood; sorption isotherms (DVS) vs decay mass loss",
    source_file="7980675.pdf (Belt et al. 2024 Int. Biodeterior. Biodegrad. 186:105690); NIR spectra.csv (288 wavelengths x 36 samples); Sample IDs and mass data.csv (252 samples); Sorption measurements_*.xlsx (DVS step data per sample)",
    confidence=0.9,
)
_WHUS = dict(
    modality="Satellite multispectral imaging (Sentinel-2 MSI digital numbers, 13 bands at 10/20/60 m) - paired cloudy / cloud-free image clips",
    spectral_range_original_min=443, spectral_range_original_max=2190, spectral_range_original_unit="nm",  # band centres B1-B12
    num_spectral_channels=13,
    spatial_resolution=10, spatial_resolution_unit="m (10 m: B2,B3,B4,B8; 20 m: B5-B7,B8A,B11,B12; 60 m: B1,B9,B10)",
    image_height=384, image_width=384,  # 10 m clips (20 m 192x192, 60 m 64x64)
    spectral_target_relationship="Cloudy vs cloud-free (10-day revisit) Sentinel-2 clip pairs -> deep-learning thin-cloud removal (CR4S2 multi-input/output CNN fusing all bands); evaluation PSNR 39.55, SSIM 0.9443, NRMSE 0.0245, SAM 2.57 deg over 12 bands on 20 test images",
)
R["8035347"] = dict(
    _WHUS,
    num_samples=73,  # training scenes (123 scene pairs in full WHUS2-CRv)
    num_images=91326,  # 15,221 clip pairs x 2 (cloudy/clear) x 3 resolutions
    num_pixels=15221 * 2 * (384 * 384 + 192 * 192 + 64 * 64),
    num_spectral_values=15221 * 2 * (384 * 384 * 4 + 192 * 192 * 6 + 64 * 64 * 3),
    source_file="8035347.pdf (Li et al. 2022 IEEE JSTARS 15:8759); train.z01-z08 + train.zip (split zip, 37.6 GB; 50.2 GB uncompressed): train/clearDNclips|cloudDNclips/{10m,20m,60m}/<scene>/<n>.tif + 15221.txt",
    confidence=0.85,
)
R["8035349"] = dict(
    _WHUS,
    num_samples=50,  # 24 validation + 26 test scenes
    num_images=55374,  # (4,496 val + 4,733 test) clip pairs x 2 x 3 resolutions
    num_pixels=(4496 + 4733) * 2 * (384 * 384 + 192 * 192 + 64 * 64),
    num_spectral_values=(4496 + 4733) * 2 * (384 * 384 * 4 + 192 * 192 * 6 + 64 * 64 * 3),
    source_file="8035349.pdf (same paper as 8035347); val.z01-z02 + val.zip, test.z01-z02 + test.zip (split zips, 30.4 GB uncompressed); leftover *.part files from interrupted downloads (val.z01.part 236 MB, val.z02.part, val.zip.part, test.z0*.part 0 B)",
    confidence=0.8,
)

R["8046504"] = dict(
    modality="FTIR (transmission/ATR, OMNIC) + in-situ SAXS, XRD, X-ray PDF, NMR and TEM of copper sulfide nanoplates grown with a preceramic polymer ligand",
    spectral_range_original_min=700.045, spectral_range_original_max=8000.37, spectral_range_original_unit="cm-1",  # CSV export; SPA 700-5000 cm-1 (4460 pts)
    num_spectral_channels=7572, sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=7,  # neat PyMPS, neat oleylamine, Cu2S with PyMPS:OLAM 1:16, 2:16, 3:16, 1:8, 1:0
    num_spectra=20,  # FTIR CSV (baseline-corrected + uncorrected; Fig 3 and Fig S2 share some samples); + 145 SAXS 1D curves, 312 SAXS 2D .edf frames
    num_spectral_values=20 * 7572,
    spectral_target_relationship="FTIR bands of PyMPS (C-N 1300-1600, Si-CH3 1250, Si-O-Si 1020, Si-CH 950, Si-C 820 cm-1) retained on Cu2S at all ligand ratios -> polymer remains bound; in-situ SAXS during 200 C hold -> nucleation/growth kinetics and nanoplate size; XRD/PDF phase (Cu2S / Cu)",
    source_file="8046504.pdf (Loughney et al. 2023 Commun. Mater. 4:53); Dryad_Data_Share.zip (FTIR 20 CSV + 20 SPA; SAXS 312 .edf + 145 .dat; XRD .ras/.asc/.csv; PDF .tif; NMR Bruker folders; TEM .ser/.emi/.tif; per-technique README .md); README.md (RTF)",
    confidence=0.8,
)

R["8126759"] = dict(
    modality="Laboratory VIS-NIR-SWIR soil reflectance spectroscopy (ASD spectroradiometer, 1 nm) + digital soil mapping covariates (Sentinel-2 L2A, ALOS PALSAR DEM)",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    num_spectral_channels=2151, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=372,  # soil horizon samples with spectra (84 profiles); C for 321, clay for 203
    num_spectra=372, num_spectral_values=372 * 2151,
    spectral_target_relationship="Vis-NIR-SWIR spectra of soil horizons of Itatiaia National Park -> soil properties (C, N, texture, pH, cations) and 'hyperspectral subsurface images' generated from lab spectra + covariates for digital soil mapping (random forest / GAM)",
    source_file="8126759.pdf (Costa et al. 2020 Rev. Bras. Cienc. Solo 44:e0190107 - related DSM study of the same park); Hyperspectral_Soil_Mapping__Gelsleichter_et_al_2023.zip (input/dataset/dados_PNI_sc_spctr_data.csv 481 rows x 2192 cols; SiBCS/WRB csv; Sentinel-2 SAFE subset jp2; ALOS DEM tif; shapefiles; R scripts; Readme__leia_me.txt)",
    confidence=0.8,
)
R["8141012"] = dict(
    modality="Stimulated Raman photothermal (SRP) and stimulated Raman scattering (SRS) microscopy - hyperspectral image stacks and spectra",
    spectral_range_original_min=1531.5, spectral_range_original_max=3498.2, spectral_range_original_unit="cm-1",  # Raman shift (C-D 1984-2400, C-H 2761-3200, fingerprint 1531-1798)
    num_samples=10,  # DMSO / dimethyl sulfide dilutions, PMMA beads, virus particles, cancer cells, C. elegans / myelin tissue, PA-d31 labelled cells, ...
    num_spectra=75,  # spectra columns in RawData.xlsx (concentration series, ROI spectra)
    num_images=17,  # TIFF image stacks (e.g. 300x300x80, 400x400x60, 600x600x100 frames)
    spectral_target_relationship="Photothermal detection of SRS energy deposition (probe-beam thermal lensing) -> Raman spectra/images with ~500x lower detection limit than SRS (sub-mM DMSO, dimethyl sulfide), imaging of viruses, cells (lipids, ER, nucleolus) and myelin; concentration calibration series",
    source_file="8141012.pdf (Zhu, Ge, Ni, ... Cheng, preprint); RawData.xlsx (40 sheets: simulations, time traces, SRS/SRP spectra, concentration series, ROI spectra); 17 TIFF stacks (Fig3-5, S14-S18)",
    confidence=0.75,
)

R["8161216"] = dict(
    modality="FTIR spectroscopy (%T, 4000-450 cm-1) of experimentally matured modern feathers, Mesozoic fossil feathers and host sediments (+ S K-edge XANES)",
    spectral_range_original_min=450, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3551, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=13,  # black Gallus & white Egretta feathers x {untreated, 200 C, 250 C} + 3 fossils (Confuciusornis, Sinornithosaurus, Green River) organic + sediment
    num_spectra=80,  # 73 PerkinElmer .sp (54 x 3551 pts, 19 x 3401 pts 4000-600) + 7 merged baseline-corrected z-score .spc
    num_spectral_values=54 * 3551 + 19 * 3401 + 7 * 3400,
    spectral_target_relationship="Amide A/B/I/II/III band positions and amide I+II deconvolution (beta-sheet, beta-turn, alpha-helix, random coil fractions) vs maturation temperature (200/250 C) -> preservation of corneous beta-proteins (CBPs) in fossil feathers; S XANES cysteine -> sulfate oxidation",
    source_file="8161216.pdf (Slater, Edwards, Webb, Zhang & McNamara 2023 Nat. Ecol. Evol. 7:1706); 73 *.sp (PerkinElmer, %T), 7 *_BC_zscore.spc; Origin projects (*.opju deconvolution); Athena *.prj (XANES)",
    confidence=0.85,
)

R["8182624"] = dict(
    modality="Laboratory VIS-NIR-SWIR reflectance spectroscopy (ASD FieldSpec, 1 nm) of soil samples + soil physico-chemical database",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    num_spectral_channels=2151, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=137,  # georeferenced poplar plantation sites (soil profiles, 1994-1996)
    num_spectra=300,  # all soil layers + reference sands (black/grey/white sand)
    num_spectral_values=300 * 2151,
    spectral_target_relationship="Vis-NIR reflectance of every soil layer (350-2500 nm) alongside topsoil texture, NH4+, NO3-, CaCO3, P2O5, pH, organic matter / SOC, irrigation and water-table depth -> archive for SOC change / carbon-farming studies (no model in paper)",
    source_file="8182624.pdf (Annals of Silvicultural Research 49(2):53-56, 2024, doi:10.12899/asr-2505); Soil Dataset.xlsx (sheets 'Soil samples' 137 x 46, 'Vis-NIR' 300 x 2152); Table.docx (field descriptions)",
    confidence=0.85,
)

R["8189935"] = dict(
    modality="Photothermal-induced resonance (PTIR / AFM-IR) nanospectroscopy and IR imaging of intact (non-dried, non-fixed) eukaryotic cells",
    spectral_range_original_min=900, spectral_range_original_max=3600, spectral_range_original_unit="cm-1",
    num_spectral_channels=1051, sampling_interval=2, sampling_interval_unit="cm-1 (900-3000 cm-1 in 1051 points)",
    num_samples=5,  # 5 measurement sets (cells)
    num_spectra=11,  # point spectra in Set1/Set3/Set5 (Set3: 8 spectra 900-3000 cm-1)
    num_images=87,  # AFM height/deflection + IR absorption maps (128-512 px) at 1090-2925 cm-1
    spatial_resolution=100, spatial_resolution_unit="nm (PTIR, below diffraction limit)",
    spectral_target_relationship="PTIR spectra and single-wavenumber IR maps (amide I 1650/1678, amide II 1545, lipid C-H 2921/2925, 1440, 1380, 1275, 1090 cm-1) -> subcellular localisation of proteins and acyl lipids in nucleus and organelles of hydrated cells; variable PTIR response discussed",
    source_file="8189935.pdf (Quaroni et al., Molecules 24:4504, 2019); Data for molecules-24-04504/Set1-5.axz (Anasys Analysis Studio, gzip UTF-16 XML: height maps + spectra)",
    confidence=0.7,
)
# <append>

R["8214858"] = dict(modality="NIR-excited SHG and Er3+ NIR luminescence spectroscopy (+ FTIR, XRD, TGA) of noncentrosymmetric Ln-MOFs - data only in proprietary Origin/Publisher files", spectral_range_original_min=400, spectral_range_original_max=1650, spectral_range_original_unit="nm", num_samples=2, spectral_target_relationship="SHG (e.g. 488 nm) and Er3+ 1550 nm emission under 800-1500 nm pulsed excitation vs temperature -> ratiometric nonlinear optical thermometry", source_file="8214858.pdf (Runowski et al. 2023 ACS AMI 15:3244); .opju/.pub figure projects, MOF1.dsv (SQLite), elemental-analysis zips", confidence=0.5)
R["8247888"] = dict(modality="None (no spectra): GC-MS compound table of Plantago major hexane extract (paper also reports FTIR/NMR/HPTLC of beta-sitosterol)", num_samples=1, spectral_target_relationship="No spectral data; 11 GC-MS phytochemicals (retention time, area %) -> beta-sitosterol identification", source_file="8247888.pdf (Albadri et al. 2023 F1000Research 12:1349); Data.xlsx (13 x 5)", confidence=0.85)
R["8280710"] = dict(modality="Empirical Earth transmission (transit) spectrum from ACE-FTS solar-occultation spectra", spectral_range_original_min=2.2, spectral_range_original_max=14.3, spectral_range_original_unit="um", num_spectral_channels=1538460, num_samples=1, num_spectra=1, num_spectral_values=1538460, spectral_target_relationship="Effective atmospheric thickness (2.1-80.9 km) vs wavelength -> opacity windows and biosignatures (O3, CH4, H2O, CO2) of Earth as a transiting exoplanet", source_file="8280710.pdf (Macdonald & Cowan 2019 MNRAS, arXiv:1908.10873); Spectrum.txt (row 1 wavelength um, row 2 effective height km)", confidence=0.9)
R["8322076"] = dict(modality="Angle-dependent NIR reflectance at 945 nm measured with a time-of-flight camera (material dataset for lidar/ToF simulation)", spectral_range_original_min=945, spectral_range_original_max=945, spectral_range_original_unit="nm", num_spectral_channels=1, num_samples=314, num_spectra=314, num_spectral_values=314 * 9, num_images=272, spectral_target_relationship="Reflectance (%) at 0-80 deg incidence (10 deg steps) for 314 material samples (incl. vehicle varnishes, moss rubber) -> material classification / sensor simulation", source_file="8322076.pdf (Data in Brief 51:109747, 2023 update); v1.1.0_database 314 txt, v1.1.0_description 314 txt, pictures, supplement data", confidence=0.85)
R["8329357"] = dict(modality="UV-Vis absorption + FTIR (PerkinElmer ASCII) + XRD of shilajit extract and green-synthesised ZnO nanoparticles", spectral_range_original_min=190, spectral_range_original_max=1100, spectral_range_original_unit="nm", num_spectral_channels=18201, sampling_interval=0.05, sampling_interval_unit="nm", num_samples=2, num_spectra=4, num_spectral_values=2 * 18201 + 2 * 3601, spectral_target_relationship="UV-Vis peaks (ZnO 357.9 nm, extract 422.4 nm) and FTIR bands (3399 OH, 2924 C-H, 1617, 1384, Zn-O <600 cm-1) -> confirmation of ZnO NP formation and capping; anticancer activity vs HeLa", source_file="8329357.pdf (Perumal et al. 2024 Sci. Rep. 14:2204); Characterization_data/UV (2 .asc 1100-190 nm), FTIR (2 .ASC 4000-400 cm-1), XRD .ASC, particle size", confidence=0.85)
R["8355737"] = dict(modality="Dry-film ATR-FTIR spectroscopy of urine and urinary protein extracts", spectral_range_original_min=549.72, spectral_range_original_max=3996.56, spectral_range_original_unit="cm-1", num_spectral_channels=1788, spectral_resolution=4, spectral_resolution_unit="cm-1", num_samples=21, num_spectra=165, num_spectral_values=109 * 1788 + 46 * 3601 + 10 * 3551, spectral_target_relationship="Urine dry-film spectra of 21 volunteers (14 runners, 7 controls) before and 0-24 h after 10 km run -> PCA and PLS regression of recovery time (significant in exercise group, max change at 11 h); protein extract spectra by PCA", source_file="8355737.pdf (Bejar-Grimalt et al., Analyst/RSC); rawdata/dryfilm_urine 109 Bruker OPUS .0 (Tensor 27, 100 scans); dryfilm_proteins 56 PerkinElmer .sp; proteinas.mat; SampleMetadata.xlsx; MATLAB scripts", confidence=0.9)
R["8356427"] = dict(modality="Mid-IR FTIR transmittance/reflectance micro-spectroscopy and electromagnetic simulations of BIC metasurfaces", spectral_range_original_min=952, spectral_range_original_max=1794, spectral_range_original_unit="cm-1", num_spectral_channels=422, sampling_interval=2, sampling_interval_unit="cm-1", num_samples=9, num_spectra=61, num_spectral_values=25742, spectral_target_relationship="Measured (61 normal-incidence transmittance spectra in 11 txt files, Figs 5-7) and simulated transmittance spectra vs displacement, angle and polarisation -> displacement-mediated quasi-BIC resonances, Q-factors and angular robustness vs tilted ellipses / Au nanohole references", source_file="8356427.pdf (Berger, Barkey, Maier & Tittl, Adv. Opt. Mater.); AllData/Coherent/Figure2-7, S1-S2 (csv simulation maps, field txt, measured txt, .mat reflective-objective spectra)", confidence=0.75)
R["8361419"] = dict(modality="Brazilian Soil Spectral Library: laboratory VIS-NIR-SWIR (350-2500 nm) and MIR (4000-600 cm-1) soil reflectance + soil attributes", spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm", num_spectral_channels=2151, sampling_interval=1, sampling_interval_unit="nm (MIR 5 cm-1, 681 ch)", num_samples=16084, num_spectra=16084 + 1783, num_spectral_values=16084 * 2151 + 1783 * 681, spectral_target_relationship="Soil spectra from 48 contributors across Brazil -> sand, clay, SOM, pH, Ca, Mg, Na, CEC prediction via BraSpecS web service", source_file="8361419.pdf (Dematte et al. 2022 Remote Sens. 14:740); BSSL_DB_V002.xlsx (attributes 16,084 x 26; Vis_NIR_SWIR 16,084 x 2153; MIR 1,783 x 683; contributors; metadata)", confidence=0.9)
R["8387073"] = dict(modality="Operando DRIFTS (CO adsorption bands) + Pd K-edge EXAFS during palladium hydride formation", spectral_range_original_min=1749.92, spectral_range_original_max=2149.53, spectral_range_original_unit="cm-1", num_spectral_channels=830, sampling_interval=0.482, sampling_interval_unit="cm-1", num_samples=4, num_spectra=870, num_spectral_values=435 * 830 + 435 * 1722, spectral_target_relationship="Time-resolved CO DRIFTS (5 fitted bands) and EXAFS (24050-25188 eV) at 30/50/70/90 C under H2 -> machine-learning extraction of Pd-Pd distance / hydride fraction from IR spectra", source_file="8387073.pdf (Usoltsev et al. Small Methods); DRIFTS.dat (435 x 830), EXAFS.dat (435 x 1722), Params.dat (band fit parameters)", confidence=0.85)
