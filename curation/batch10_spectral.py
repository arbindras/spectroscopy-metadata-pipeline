# Batch10 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (E:\Batch10\papers\<id>.pdf or PMC JATS <id>.xml) + dataset (E:\Batch10\Datasets\<id>_<title>\),
# reviewed through direct checks of the files (table shapes, axes, headers) and the paper methods.
# Records without spectra are listed in NO_SPECTRA and are not part of the batch10 parquet files
# (they go to output/batch10_no_spectra.csv); their dataset folders were moved to E:\Batch10_no_spectra.
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

# Records left out of the Batch10 parquet files because the dataset holds no spectra (record id -> reason).
NO_SPECTRA = {
    "14826742": "TRS-NIRS + DCS cerebrovascular CO2 reactivity in newborns (Neurophotonics 2023): only the article PDF was deposited - no data files, no spectra",
    "14826764": "robustness of CW space-resolved NIRS tissue oxygenation (JBO 2023): SRS_FIGURE.xlsx holds simulated OHb/HHb/tHb/StO2 estimates and errors at two wavelengths (760/850 nm) per figure - derived haemoglobin values, no spectra",
    "14831672": "metabolomic profiling of pollen: the 5 GB zip holds only Waters Cyclic-IMS mass-spectrometry raw folders (ASAP, LC-MS, MALDI imaging) and two MarkerLynx feature tables - the FTIR spectra of the paper are not deposited, mass spectra only",
    "15097417": "FTIR-derived soil degradation indices, Northern Apennines watershed (PLOS One 2025): S1 datasets (csv/xlsx) of four FTIR band-ratio indices (A/B, A/D, B/D, C/D) per sediment sample with terrain/soil covariates + raster/shapefile GIS layers - the KBr FTIR spectra themselves are not deposited",
    "15126158": "dual micro-electromembrane extraction + on-line HPLC-UV-Vis of polyphenols (Anal. Bioanal. Chem. 2025): one CSV of chromatograms (absorbance vs retention time at three fixed detector wavelengths) for incurred/spiked eggplant samples - chromatograms, no spectra",
    "15246074": "FTIR and VSC colour assessment of cremated archaeological bones (Data in Brief 2025): only four bone-list / excavation workbooks (Aakre Kivivare, Viimsi I, tarand cemeteries, heading explanations) were downloaded - the FTIR spectra and VSC colour data of the article are not in this download",
    "15395585": "DeepForest aerial sensing of self-occluding vegetation volumes (drone synthetic-aperture imaging): Parrot-type 4-band multispectral (green, red, red edge, NIR) image series, VTI reflectance/NDVI focal stacks, CNN checkpoints, code and movies (40 GB) - broadband 4-channel imagery, no spectra",
    "15741144": "all-electrochem-active graphite electrode for Li batteries (VSB-TUO deposit): figure PNGs (incl. in-situ XRD), table TIFF, the article PDF, supporting-information PDF and ReadMe - only figure images, no data files and no spectra",
    "16949120": "PP/PET microplastics and trypsin structure/function (IJMS 2025): seven CSVs of trypsin activity - absorbance vs time (13-313 s) kinetics at a fixed wavelength and derived activities for lPP/sPP/PET bulk and SC samples - kinetic traces, no spectra (CD/fluorescence spectra of the paper not deposited)",
    "18209096": "microplastics in marine sediments of the Colombian Caribbean (2026): one workbook with metadata, microplastic counts per station, granulometry and an 'FTIR' sheet listing the polymer identification result per particle (size, shape, colour, polymer) - identification table only, the FTIR spectra are not deposited",
    "18609418": "Monte Carlo correction of single-distance time-domain NIRS on muscle (Biomed. Opt. Express 2026): CSVs of instrument response functions and photon time-of-flight distributions (DTOF vs ps) plus fitted vs ground-truth mua/mus' tables from simulations, and PNG figures - time-domain photon counts and optical coefficients, no spectra",
    "18713028": "imidazolium hydrogen o-phthalate under high pressure (J. Phys. Chem. Lett. 2026): Gaussian PES-scan logs of helix hydrogen bonds (models 1-3), two freq-job inputs (.gjf), average-position CIFs at 0 and 17 GPa and mol2 models - computational inputs/outputs only; the high-pressure Raman/IR spectra of the paper are not deposited",
    "18945614": "heat-evolved coral photosymbionts (New Phytol. 2026): nine workbooks of synchrotron-FTIR integrated band areas per cell (culture, expelled, in hospite), RGB reflectance of juveniles, iPAM/SSLC photophysiology, pigment and cell-density tables - band-area summaries only, the FTIR spectra are not deposited",
    "19675863": "orthogonal functionalisation of lithium-niobate nanoparticles with aptamer/drug (RSC Appl. Interfaces 2026): Bruker NMR experiment folders, a Malvern DLS .dts file and one 96-well plate-reader workbook (single-wavelength fluorescence/absorbance counts per well) - no spectra",
    "19339684": "growth-factor thermostability dataset for cultured meat (Data in Brief 2026): one workbook compiling literature melting temperatures/methods per growth factor (Sheet1) and FoldX in-silico energy terms per PDB structure (Sheet2) - tabular values, no spectra",
    "19634497": "5-(pyridin-3-yl)-1,3,4-oxadiazoles as VEGFR2 inhibitors (Res. Pharm. Sci. 2026): only the supplementary-materials PDF (NMR/IR/MS spectra as images) was deposited - no spectral data files",
    "19636445": "'Opto-Metallurgy and the Photonide Class' deposit: a single 1.8 MB PDF (concept/theory document; attached paper is the related ACS Omega 2023 UV-plasmonics study of Ag/Au p-block compounds) - no data files, no spectra",
    "20942415": "brain-hormone-mind-behaviour dynamics with fNIRS (attached paper: MazeSuite + fNIRS, JoVE 2011): fNIRS recordings (.nir/.oxy/.mrk/.log, two LED wavelengths 730/850 nm) with behavioural/hormone xlsx, R/SPSS scripts - haemodynamic time series at two fixed wavelengths, no spectra",
    "21234283": "berberine ROS-sensitive polymersomes (Nanoscale Adv. 2025): 000_ReadMe.txt and two PDFs (PrimaryData.pdf, MVshortResults.pdf) with DLS reports, HPLC loading/release, histology and western-blot images - only PDF documents, no spectral data files",
    "21537182": "ViBra VSCF/VCI anharmonic vibrational structure code (arXiv 2026, quantum-classical): ORCA optimisation/Hessian/VPT2 outputs, quartic force fields, VCI inputs/outputs and QPU benchmark logs for small molecules (H2O, C2H4, HFCO, N2H4, N2H2, water crystal) - vibrational energy levels and computational files, no spectral data files",
    "21721841": "edible NADES extraction of Nigella sativa bioactives (Molecules 2026): the 89 ATR-FTIR spectra are deposited only as TIFF images (plus DSC thermogram JPGs and GraphPad Prism statistics) - spectra as images only, no numeric spectra",
    # --- end NO_SPECTRA ---
}

R["14834415"] = dict(
    modality="UV-Vis absorption and steady-state photoluminescence of low-dimensional NI/NDI lead iodide perovskite films, and absolute (integrating-sphere) PL spectra for PLQY of FTO/MeO-2PACz/perovskite films with interlayers, with and without PCBM",
    spectral_range_original_min=300, spectral_range_original_max=950.072, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (UV-Vis 471 pts 330-800 nm; PL 301-401 pts 300-800 nm; PLQY 606 pts 700.2-950.1 nm, ~0.41 nm)",
    num_samples=14,  # 4 LD perovskite films ((NI)2PbI4, (NI)2FAPb2I7, (NDI)PbI4, (NDI)FAPb2I7) + 5 interlayer stacks (control, PDA, NI, NDI 0.2/0.1 mg/mL) x with/without PCBM
    num_spectra=58,  # Fig1 4 UV-Vis + 4 PL; Fig4 PLQY 5 conditions x 5 replicates x 2 (without/with PCBM); averages, IPCE, TRPL, XRD, J-V not counted
    num_spectral_values=33498,  # 4x471 + (311+401+301+301) + 50x606
    spectral_target_relationship="Excitonic absorption (350-450 nm) and PL of NI/NDI low-dimensional perovskite phases -> phase identification; absolute PL / PLQY of the ~800 nm perovskite emission with and without PCBM -> non-radiative recombination and charge extraction at NI/NDI-modified interfaces, linked to solar cell Voc/PCE and stability",
    source_file="14834415.xml (Armadorou, AlSabeh, Vezzosi, ... Milic & Gratzel 2025 J. Mater. Chem. C 13:20040, doi:10.1039/d5tc01418b); Figure_1_rawdata.xlsx sheet 'UVVis and PL'; Figure_4_rawdata.xlsx sheets PLQY / PLQY w PCBM (+ avg, IPCE, TRPL, JV); Figure_3/6 and Figures_SI rawdata (PV statistics, XRD, MPP), opju/mnova SI files; DFT_calculations.tar.gz (CP2K, not spectra)",
    confidence=0.8,
)

R["14999214"] = dict(
    modality="Spectroscopic ellipsometry (J.A. Woollam M-2000, psi/delta) and UV-Vis absorption (PerkinElmer) of thermally evaporated CsPbCl3 perovskite thin films, with model-derived n, k and absorption coefficient",
    spectral_range_original_min=190, spectral_range_original_max=999.883, spectral_range_original_unit="nm",
    sampling_interval=1.6, sampling_interval_unit="nm (SE 444/453 pts 272-1,000 nm; UV-Vis 1 nm 190-799 nm, 610 pts; n,k 392/426 pts; alpha 469 pts 246-1,000 nm)",
    num_samples=2,  # sample A (90 nm) and sample B (180 nm) CsPbCl3 on Si/SiO2 (UV-Vis films on glass)
    num_spectra=12,  # 2 UV-Vis + 2x2 SE psi/delta + 2x2 n/k + 2 absorption coefficient (model fits and Tauc transforms not counted)
    num_spectral_values=5588,  # 2x610 + 2x444 + 2x453 + 2x392 + 2x426 + 2x469
    spectral_target_relationship="Ellipsometric psi/delta fitted with a Tauc-Lorentz / harmonic oscillator model -> complex refractive index n, k and absorption coefficient of CsPbCl3; UV-Vis absorption edge and Tauc plots -> optical bandgap (~3 eV) of 90 vs 180 nm films",
    source_file="14999214.pdf (Khan, Cegielski, Runkel, Riedl, Mohammadi & Lemme 'Spectroscopic ellipsometry of CsPbCl3 perovskite thin films'); SE raw psi and delta (.txt + .SE) for samples A/B, fitting results txt, 'Sample A/B SE processed data-extracted n and k.txt', absorption coefficient txt, 'calculated bandgap from UV vis data' xlsx, 'simulated bandgap from k values' xlsx, Tauc-Lorentz parameter txt",
    confidence=0.85,
)

R["15001025"] = dict(
    modality="High-resolution near-infrared (H and K band) echelle spectroscopy of the brown-dwarf binary Luhman 16AB with IGRINS on Gemini South (R~28,000), per-epoch order spectra of both components plus stitched atlas and model fits",
    spectral_range_original_min=1.47845, spectral_range_original_max=2.48367, spectral_range_original_unit="um",
    num_spectral_channels=2048, sampling_interval=1.2e-05, sampling_interval_unit="um (2,048 pixels per echelle order; stitched atlas 13,184 pts; fitted orders ~1,900 pts)",
    spectral_resolution=28000, spectral_resolution_unit="resolving power R",
    num_samples=2,  # Luhman 16A (L7.5) and Luhman 16B (T0.5)
    num_spectra=8650,  # 93 frames x 46 orders x 2 components = 8,556 epoch spectra + 92 fitted order spectra (46 x A/B) + 2 combined stitched spectra
    num_spectral_values=17723856,  # approx.: 8,556 x 2,048 + 92 x ~1,900 + 2 x 13,184
    spectral_target_relationship="Telluric-corrected H2O, CH4, CO, NH3, FeH, H2 absorption features per order vs Sonora-Diamondback/atmosphere models -> Teff, log g, fsed, Kzz, vsini and RV per order, molecular line identification atlas and variability/rotation of the two brown dwarfs over 33 nights",
    source_file="15001025.pdf (Ishikawa, Metchev, Tannock, Mace, Hood, Fortney, Mukherjee, Miles-Paez & Kurtev 2025 MNRAS, arXiv:2503.19322 'A 1.48-2.48 um R=28 000 spectroscopic atlas of ... Luhman 16AB'); each_epoch_spectra.zip (ascii_Horder*/ascii_Korder* 46 orders x 93 SDCH/SDCK *_2f.txt: wav, flux_A, uncert_A, flux_B, uncert_B; BVCs.txt, JDs.txt), fitted_models_and_spectra.zip (92 .dat data+model), all_combined_stitched_spectra_and_fitting_parameters.zip (fig6/fig7 flux, uncertainty, single-molecule model spectra, best-fit parameters), RV_data.zip",
    confidence=0.85,
)

R["15009894"] = dict(
    modality="UV-Vis absorption (Shimadzu UV-1900i, second-derivative analysis) and far-UV circular dichroism (Jasco J-1500 with Peltier temperature scans) of phenylalanine ammonia-lyase (RgPAL) in cholinium ionic-liquid / Tris-HCl media",
    spectral_range_original_unit="nm",
    num_samples=10,  # approx.: RgPAL in Tris-HCl and 3 ILs ([Ch][Cl], [Ch][Ac], [Ch][Dhp]) at several concentrations
    spectral_target_relationship="Second-derivative UV tyrosine/tryptophan peak-to-peak ratios (250-300 nm) and far-UV CD ellipticity (208/222 nm) vs IL concentration and temperature -> solvent-induced structural changes, unfolding fraction and thermal stability of RgPAL, alongside activity kinetics and docking",
    source_file="15009894.xml (Bharadwaj, Barua, Bisht, Sarkar, Biswas, Franklin & Mondal 2024 J. Phys. Chem. B 128:9102, doi:10.1021/acs.jpcb.4c04272); Dataset.zip -> 'Meta data/Figure 2a ... S1b.opju' (28 OriginLab projects, one per figure panel; Figures 5a-c UV second derivative, 6a-c CD, 7a-d CD temperature scans) - values not readable without Origin",
    confidence=0.35,
)

R["15056424"] = dict(
    modality="Simulated mid-infrared thermal emission spectra of temperate terrestrial exoplanets as observed by the LIFE mission (LIFEsim instrument simulator) for a 13-scenario CO2 population, used as input to Bayesian atmospheric retrievals",
    spectral_range_original_min=4.0605, spectral_range_original_max=18.381, spectral_range_original_unit="um",
    spectral_resolution=50, spectral_resolution_unit="resolving power R (R=50: 75 bins; R=100: 152 bins)",
    num_samples=13,  # atmospheric CO2 scenarios (CO2 abundance E-00..E+01 x stellar flux S 0.4-1.x)
    num_spectra=104,  # 13 scenarios x 4 quality cases (S/N 10/20 x R 50/100) x 2 sets (variable / fixed H2O profiles)
    num_spectral_values=11804,  # 2 x (26 x 152 + 26 x 75)
    spectral_target_relationship="Simulated emission flux with LIFEsim noise (15 um CO2 band, 9.6 um O3, H2O) -> retrieved CO2 partial pressure per planet -> population-level CO2 trend vs instellation as signature of carbonate-silicate weathering, surface oceans and biotic activity",
    source_file="15056424.pdf (Hansen, Angerhausen, Quanz, Vance, Konrad, Garvin, Alei, Kammerer & Dannert 2025, arXiv:2505.23230 'Detecting Atmospheric CO2 Trends as Population-Level Signatures ...'); LIFEsim_Spectrum_Data(.tar.gz) and LIFEsim_Spectrum_Data_Fixed_H2O: 52 input_LIFEsim_spectrum_CO2_E*_S_*_observation_SNR*_R*.txt each (wavelength um, flux erg/m2/s/Hz, uncertainty); Atm_Post_Data*, Trend_Post_Data* = retrieval posteriors (not spectra)",
    confidence=0.75,
)

R["15166836"] = dict(
    modality="Far- and mid-infrared reflectivity spectroscopy (FTIR + THz) of a Bi2O2Se single crystal at 2-300 K, with derived dielectric function (eps1, eps2) and energy-loss function",
    spectral_range_original_min=0.25008, spectral_range_original_max=800, spectral_range_original_unit="cm-1",
    sampling_interval=0.5, sampling_interval_unit="cm-1 (reflectivity 1,288 pts 19.8-640.3 cm-1; eps1/eps2 3,199/3,184 pts 0.25/4-800 cm-1; loss function 2,481 pts 20.3-640.5 cm-1)",
    num_samples=1,  # Bi2O2Se single crystal (tetragonal ab plane), 7 temperatures
    num_spectra=28,  # 7 temperatures x (reflectivity + eps1 + eps2 + loss function)
    num_spectral_values=71064,  # 7 x (1,288 + 3,199 + 3,184 + 2,481)
    spectral_target_relationship="IR reflectivity fitted with oscillator models -> polar phonon frequencies (soft optical phonon ~34 cm-1), static permittivity (~500) and their temperature dependence, explaining high electron mobility and the unconventional (low) thermal conductivity; compared with DFT phonon dispersion",
    source_file="15166836.pdf (Zich, Sojka, Levinsky, Misek, Ahn, Navratil, Hejtmanek, Knizek, Holy, Nuzhnyy, Borodavka, Kamba & Drasar 'Phonon properties and unconventional heat transfer in quasi-2D Bi2O2Se crystal'); Fig4.zip TemperatureDependenceofReflectivities.txt; Fig5.zip Epsilon1_vs_T.txt, Epsilon2_vs_T.txt; FigS11.zip LossFunction_vs_T.txt; other zips = Hall, Cp, thermal conductivity, phonopy DOS/bands, HRXRD .ras (not spectra); SupplementaryMaterials.pdf",
    confidence=0.8,
)

_HONEY = dict(
    modality="ATR-FTIR (mid-infrared) spectroscopy of Latvian honeys of different botanical origin (willow, clover, heather, linden, rapeseed, raspberry, buckwheat, polyfloral)",
    spectral_range_original_min=499.955, spectral_range_original_max=4000.12, spectral_range_original_unit="cm-1",
    num_spectral_channels=7261, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=28,  # honey samples Wil_1-7, Clo_4/6/7, Hea_1-3, Lin_1/5/6/7, Rap_2/6, Ras_1, Man_1, ApI_1/2, Buck_1-3 ...
    num_spectra=28,
    num_spectral_values=203308,  # 28 x 7,261
    spectral_target_relationship="ATR absorbance of sugars (C-O/C-C 900-1,150 cm-1), water (1,640, 3,300 cm-1) and minor phenolics/proteins -> characterisation and grouping of honeys by botanical origin, supporting the antimicrobial/antibiofilm comparison of Latvian honeys",
)

R["15231441"] = dict(
    _HONEY,
    source_file="15231441.xml - related paper of the same group (Skadins, Labsvards, Grava, Amirian, Tomsone, Rusko, Viksna, Bandere & Brangule 2023 Antibiotics 12:816 'Antimicrobial and Antibiofilm Properties of Latvian Honey ...', doi:10.3390/antibiotics12050816; FTIR not described there); 'Characterization of Latvian honey through FTIR-ATR spectroscopy (1).csv' (semicolon-separated, wavenumber + 28 sample columns); byte-identical to record 15648108",
    confidence=0.65,
)

R["15648108"] = dict(
    _HONEY,
    source_file="15648108.xml - same related paper as 15231441 (Skadins et al. 2023 Antibiotics 12:816, doi:10.3390/antibiotics12050816); 'Characterization of Latvian honey through FTIR-ATR spectroscopy (1).csv' - byte-identical copy of the file in record 15231441 (second Zenodo version of the same deposit)",
    confidence=0.6,
)

R["15237061"] = dict(
    modality="Transmission FTIR and polarized FTIR (Thermo Nicolet iS20) of uniaxially stretched amorphous polylactide (aPLA) films in the 900-1,000 cm-1 conformational band region",
    spectral_range_original_min=900.1119, spectral_range_original_max=1000.0, spectral_range_original_unit="cm-1",
    num_spectral_channels=415, sampling_interval=0.241, sampling_interval_unit="cm-1",
    spectral_resolution=2, spectral_resolution_unit="cm-1",
    num_samples=7,  # aPLA films at true draw ratios 1.00, 1.27, 1.72, 2.03, 2.72, 2.99, 3.49
    num_spectra=21,  # 7 unpolarized + 7 x 2 polarized (parallel / perpendicular)
    num_spectral_values=8715,  # 21 x 415
    spectral_target_relationship="Absorbance of the 955 cm-1 amorphous and 918/921 cm-1 crystalline/mesophase bands, and polarized dichroic ratios -> mesophase content and amorphous-phase orientation factor Fam vs draw ratio -> shear piezoelectric coefficient d14 of oriented PLA",
    source_file="15237061.pdf (HAL hal-05176283; 'Unveiling the Amorphous Phase Contribution to Shear Piezoelectric Properties of Polylactide', Macromolecules 2025, doi:10.1021/acs.macromol.5c01023; GENEPI ANR project); '..._DSC FTIR raw datas.xlsx' sheets DSC data, FTIR data, Polarized FTIR; '..._Datas.xlsx' (material TDS, extrusion/MDO, DSC/DMA/FTIR peak tables, piezo evaluation)",
    confidence=0.8,
)

R["15266985"] = dict(
    modality="UV-Vis absorption, steady-state photoluminescence / triplet-triplet annihilation upconversion emission, and nanosecond time-gated (ICCD) emission spectra of three-component TTA-UC systems (4CzBN sensitizer, TIPS-naphthalene annihilator, benzothiophene-type mediator) in toluene",
    spectral_range_original_min=199.98, spectral_range_original_max=800.01, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (absorption/emission 1 nm; gated emission ~0.57 nm, 691-701 pts 308-735 nm)",
    num_samples=12,  # approx.: Nap, BT, DPA/PtOEP references and bi-/tri-component sensitizer-mediator-annihilator mixtures at several concentrations
    num_spectra=140,  # 86 steady-state absorption/emission spectra (Fig 2, 3b, S8-S15, S22-S28, S32-S34, S37-S38, S40-S42) + 54 gated emission spectra at delays 100 ns-300 us (Fig 4a-c, 5b); decay traces (S31, S35, S36, S39) and power-dependence tables not counted
    num_spectral_values=68532,  # 30,858 + 37,674
    spectral_target_relationship="Delayed upconverted emission (~350-450 nm) of TIPS-naphthalene vs mediator concentration, excitation power and gate delay -> homo- vs hetero-annihilation pathways and enhanced TTA-UC quantum yield via triplet mediator; absorption before/after irradiation -> photostability",
    source_file="15266985.xml (Kandappa & Gray 2025 J. Am. Chem. Soc. 147:40214, doi:10.1021/jacs.5c09906); Fig4a/4b/4c/5b.zip (gated emission TXT, header Delay/Width/Gain, wavelength vs counts, FL-corrected), 'Figure 2a ... S43-S58' zips of xlsx (wavelength + intensity/absorbance), MestReNova NMR (S43-S58), MatlabCode.zip (kinetic fits)",
    confidence=0.75,
)

R["15326266"] = dict(
    modality="Photothermal AFM-IR nanospectroscopy (QCL-excited, resonance-enhanced and new force-volume / surface-sensitive modes) of polymer blends and block copolymers (dPS-b-PMMA, PS-LDPE, purple membrane, kapton)",
    spectral_range_original_min=780, spectral_range_original_max=1920, spectral_range_original_unit="cm-1",
    sampling_interval=2, sampling_interval_unit="cm-1 (Fig3 224 pts 1,474-1,920; Fig4 151 pts 1,400-1,700; Fig7 531 pts 780-1,840)",
    num_samples=6,  # Au reference, purple membrane, PS, LDPE, PS films 30-152 nm thick, kapton
    num_spectra=10,  # Fig3 2 + Fig4 2 + Fig7 6 point spectra; the .spm files are single-wavenumber IR/mechanical maps and force-volume cubes (not spectra)
    num_spectral_values=3936,  # 2x224 + 2x151 + 6x531
    spectral_target_relationship="AFM-IR amplitude spectra (C=O 1,730 cm-1 PMMA, aromatic 1,492/1,452 cm-1 PS, CH2 1,472 cm-1 LDPE, amide I purple membrane) recorded in force-volume mode -> simultaneous nanoscale chemical identification and mechanical (modulus, adhesion) mapping, probing depth vs cantilever frequency",
    source_file="15326266.xml (ACS Nano 2025 19:18791, doi:10.1021/acsnano.5c04015 'Force Volume Atomic Force Microscopy-Infrared for Simultaneous Nanoscale Chemical and Mechanical Spectromicroscopy'); Fig3 spectrum Au/PM.txt, Fig4 LDPE/PS.txt, 'Fig7 spectra REFV and SSFV.txt' (cm-1 vs mV); 31 Bruker .spm maps/force volumes (up to 1.6 GB; three leftover .spm.part partial downloads), Fig6/FigS2/FigS3 curves and profiles",
    confidence=0.75,
)

R["15347991"] = dict(
    modality="ATR-FTIR spectroscopy (PerkinElmer) of cellulose textile, myristic-acid phase-change material and OSA-grafted thermoregulating / water-repellent textiles",
    spectral_range_original_min=500, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=4201, sampling_interval=0.833, sampling_interval_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=5,  # plain cellulose, myristic acid (MA), 40% MA, 50% MA, OSA-g-textile
    num_spectra=5,
    num_spectral_values=21005,
    spectral_target_relationship="Transmittance bands of MA (C=O 1,700, CH2 2,850/2,920 cm-1) and OSA ester carbonyl (~1,730 cm-1) on cellulose (O-H 3,330, C-O 1,030 cm-1) -> confirmation of PCM loading and octenyl-succinic-anhydride grafting giving thermoregulating, water-repellent textile",
    source_file="15347991.xml (Green Chem. 2025 27:6482, doi:10.1039/d5gc00943j 'Multifunctional thermoregulating and water repellent cellulosic textile'); FTIR.xlsx (5 wavenumber/transmittance column pairs); DSC.xlsx, TGA.xlsx, Tensile test.xlsx, Thermal camera.xlsx, Elemental analysis.opju (not spectra)",
    confidence=0.85,
)

R["15421555"] = dict(
    modality="Mid-infrared photo-induced force microscopy (PiF-IR, QCL-tuned, ANFATEC/Molecular Vista VistaScan) point spectra and hyperspectral hyPIR cubes of Bacillus subtilis cell surfaces after vancomycin treatment, CaF2 background spectra and bulk FTIR reference spectra",
    spectral_range_original_min=770, spectral_range_original_max=1891.85, spectral_range_original_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1 (point spectra 1,121 pts 770-1,890; hyPIR 260 pts 1,400-1,659; FTIR 490 pts 949-1,892, ~1.93 cm-1)",
    spectral_resolution=1, spectral_resolution_unit="cm-1",
    num_samples=6,  # B. subtilis + vancomycin 15/30/60 min and untreated controls 15/30 min (series 2/3)
    num_spectra=2211,  # 107 PiF-IR point spectra + 54 CaF2 raw background spectra + 2 raw FTIR (BacVan30, Control30) + 2 hyPIR cubes x 1,024 pixels
    num_images=2, num_pixels=2048, image_height=32, image_width=32,
    spatial_resolution=13.1, spatial_resolution_unit="nm (0.42 um scan / 32 px hyPIR; PiF-IR tip resolution ~5 nm)",
    num_spectral_values=713941,  # 107x1,121 + 60,534 + 2x490 + 2,048x260
    spectral_target_relationship="Nanoscale PiF-IR amide I/II, lipid ester C=O and peptidoglycan/teichoic acid bands of single bacterial cell surfaces vs bulk FTIR -> chemical changes induced by vancomycin binding to the cell wall (D-Ala-D-Ala), heterogeneity between treated and control cells",
    source_file="15421555.xml (Anal. Chem. 2025 97:23914, doi:10.1021/acs.analchem.5c03502 'Nanochemical Cell-Surface Evaluation in Photothermal Spectroscopic Imaging of Antimicrobial Interactions in the Model System Bacillus subtilis and Vancomycin'); 12 zips (BacVan15/30/60, Control15/30 series 2/3: *_afmspectrumNNNN.txt, CaF2_*_Rawspectra.txt, *hyPIRFwd.int + Wavelengths.txt, ANFATEC .int topography/PiFM images and parameter .txt); FTIR_BacVan_Control_series2.txt",
    confidence=0.75,
)

R["15465200"] = dict(
    modality="Diffuse reflectance FTIR (DRIFT, Bruker Vertex 70v) of nanocrystalline ceria prepared by five precipitation routes and of ceria after adsorption of cefalexin, 2,4-D herbicide and phosphate",
    spectral_range_original_min=399.18325, spectral_range_original_max=3997.65542, spectral_range_original_unit="cm-1",
    num_spectral_channels=1867, sampling_interval=1.93, sampling_interval_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=11,  # Ce-CARB, Ce-UREA, Ce-HMT, Ce-PER, Ce-AMN; 2,4-D, cefalexin, phosphate references; 2,4-D/CEF/PO4 on Ce-CARB
    num_spectra=12,  # 5 clean ceria + 7 pollutant set (Ce-CARB clean repeated)
    num_spectral_values=22402,
    spectral_target_relationship="DRIFT transmittance bands of adsorbed pollutants (carboxylate, phosphate P-O ~1,050 cm-1, beta-lactam C=O) and surface carbonates/hydroxyls of ceria -> binding mode of antibiotics, herbicides and phosphate on CeO2, related to adsorption isotherms/kinetics",
    source_file="15465200.xml (RSC Adv. 2025 15:38391, doi:10.1039/d5ra05301c 'Physicochemical aspects of adsorption efficiency of nanocrystalline ceria toward antibiotics, herbicides, and inorganic phosphates'); RAW_data_ZENODO_JEderer2.zip -> FTIR/FTIR-clean_samples.csv, FTIR/FTIR-DRIFT-all-samples_polutant.csv (semicolon CSV, wavenumber/transmittance pairs); BET, DLS, isotherms, kinetics, titration, XRD, zeta potential CSVs and SEM tif (not spectra)",
    confidence=0.85,
)

R["15593182"] = dict(
    modality="FTIR (ATR/transmission, 525-4,000 cm-1) and Raman spectroscopy (Thermo DXR Raman microscope, 532 nm) of graphene oxide (GO) and reduced GO papers gamma-irradiated (50-300 kGy) in air or isopropanol",
    spectral_range_original_min=99.9594, spectral_range_original_max=4000.12, spectral_range_original_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1 (FTIR 7,209 pts 525-4,000; Raman shift 3,528 pts 100-3,501, ~0.96 cm-1)",
    num_samples=18,  # GOp, rGOp and each irradiated at 50/100/200/300 kGy in air (O2) or IPA
    num_spectra=40,  # FTIR 4 files x 5 + Raman 4 files x 5 (pristine GOp/rGOp repeated in air and IPA files)
    num_spectral_values=214740,  # 20 x 7,209 + 20 x 3,528
    spectral_target_relationship="FTIR oxygen functional groups (O-H 3,400, C=O 1,730, C-O 1,050 cm-1) and Raman D/G band ratio (1,350/1,590 cm-1) vs gamma dose and medium -> reduction degree and defect density of GO/rGO, related to EMI shielding effectiveness (8-12 GHz VNA), conductivity and wettability",
    source_file="15593182.pdf (HAL hal-05298623; Chem. Eng. J. Adv. 24 (2025) 100873 'Sustainable Gamma Irradiation Strategy for GO and rGO Modification ...'); Vinca_FTIR_GO_rGO_*.rar -> Vinca_FTIR_{GO,rGO}_{air,IPA}_*.txt; Vinca_Raman_GO_rGO_*.rar -> Vinca_Raman_*.txt; UniOldenburg VNA (EMI LM/LD/SET 8-12 GHz) and 4-point, contact angle, EDX, SEM tif, XRD rar (not optical spectra)",
    confidence=0.8,
)

R["15480863"] = dict(
    modality="Calculated infrared near-field (s-SNOM / nano-FTIR) amplitude and phase spectra of thin anisotropic molecular layers (PMMA-like C=O vibration) on Au, Si and CaF2, from electrostatic and full electrodynamic simulations",
    spectral_range_original_min=1679.9946, spectral_range_original_max=1780.0, spectral_range_original_unit="cm-1",
    sampling_interval=0.01, sampling_interval_unit="cm-1 (most spectra 9,901 pts over 1,680-1,780 cm-1; parameter scans 51/101 pts; 4,001-pt series)",
    num_samples=3,  # model layer types: isotropic, in-plane (xy) and out-of-plane (z) oriented vibrations (on Au, Si, CaF2; thickness 5-100 nm)
    num_spectra=371,  # 2-column frequency spectra (S2 amplitude, phi2 phase, PMMA dielectric function) in main-text and SI figure folders; 3-4 column field maps not counted
    num_spectral_values=1990849,
    spectral_target_relationship="Simulated near-field amplitude/phase spectra vs molecular orientation, layer thickness, substrate reflectivity and tip demodulation order -> how in-plane and out-of-plane vibrations appear (peak shifts, phase sign) in infrared nanospectroscopy, guiding interpretation of nano-FTIR of thin films",
    source_file="15480863.xml (Pascual Robledo, Maciel Escudero, Schnell, Mester, Aizpurua & Hillenbrand 'Theoretical description of infrared near-field spectroscopy of in- and out-of-plane molecular vibrations in thin layers'); 'Main text figures.zip' (Fig1-Fig6 folders with FigN_readme.txt; 2-column spectra, 4-column |Ey|/|Ez| field maps) and SI.zip (FigS1-...); macOS metadata files ignored",
    confidence=0.7,
)

R["15601820"] = dict(
    modality="FTIR transmission spectroscopy (PerkinElmer, PE IR ASCII) of barium hexaferrite (BHF) nanoplatelets functionalised with catechol, caffeic acid and dopamine, and of the free ligands",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3601, sampling_interval=1, sampling_interval_unit="cm-1 (CAT spectrum 3,551 pts 4,000-450)",
    num_samples=7,  # BHF, BHF@CAT10, CAT, BHF@CAF10, CAFA, BHF@DA10, DA
    num_spectra=7,
    num_spectral_values=25157,  # 6 x 3,601 + 3,551
    spectral_target_relationship="Catechol ring and C-O / C=O bands of adsorbed ligands vs free ligands and removal of nitrate bands -> binding (bidentate catecholate) of catechol, caffeic acid and dopamine on BHF platelet surfaces, related to ligand loading (TGA) and magnetic properties (VSM)",
    source_file="15601820.xml (Drobez, Popov & Lisjak 2025 Nanoscale Adv. 7:4886, doi:10.1039/d4na01035c 'Effect of the catechol structure on the functionalization and magnetic properties of barium hexaferrite nanoplatelets'); 'Data Figure 5 BHF.txt', 'Data Figure 5a-c *.txt' (PE IR ASCII, #DATA wavenumber/%T); TGA txt (Fig 4, S2, S5), VSM magnetisation xlsx/csv (S8, 3d), EDS spectrum (3c) - not optical",
    confidence=0.85,
)

R["15690762"] = dict(
    modality="Mid-infrared transmission FTIR spectroscopy (Bruker OPUS .dpt exports, 2 cm-1, 128 scans) of SO2 ices deposited at 10-80 K on MgF2/CsI before and after VUV irradiation in the ISAC ultra-high-vacuum set-up, with QMS photodesorption monitoring",
    spectral_range_original_min=399.21284, spectral_range_original_max=4999.3212, spectral_range_original_unit="cm-1",
    num_spectral_channels=4771, sampling_interval=0.964, sampling_interval_unit="cm-1 (Exp2 at 1 cm-1 resolution, more points)",
    spectral_resolution=2, spectral_resolution_unit="cm-1 (Exp2: 1 cm-1)",
    num_samples=14,  # 14 experiments (SO2 ice at 10-80 K deposition, different irradiation times; MgF2 substrate blanks)
    num_spectra=37,  # IR_Exp*_*.dpt: substrate blanks, after deposition, after irradiation
    num_spectral_values=186067,
    spectral_target_relationship="IR column densities of SO2 (nu3 ~1,320, nu1 ~1,150 cm-1) and photoproduct SO3 (~1,395 cm-1, new band strength 1.1e-16 cm/molecule) before/after VUV dose -> ice consumption and photoproducts, combined with QMS m/z 64/48 signals -> photodesorption yields of SO2 and SO for protostellar envelope chemistry",
    source_file="15690762.pdf (Martin-Domenech, Escribano, Navarro-Alamida, Taillard, Carrascosa, Munoz Caro & Fuente 2025 MNRAS 'Photodesorption of SO2 and SO from UV-irradiated SO2 ices'); Exp1-Exp14.zip -> IR_Exp*_*.dpt (wavenumber, absorbance) and QMS_*_so2_irr.dat (mass spectrometer time series, not counted)",
    confidence=0.8,
)

R["15728134"] = dict(
    modality="UV-Vis absorption spectroscopy of A2B2 meso-substituted porphyrins and C-C-conjugated (Sonogashira) glycoporphyrins in solution (Soret and Q bands), with ROS (DPBF bleaching at 377 nm) and singlet-oxygen quantum-yield kinetics",
    spectral_range_original_min=250, spectral_range_original_max=900, spectral_range_original_unit="nm",
    sampling_interval=0.1, sampling_interval_unit="nm (11 files 0.1 nm, 6,501 pts; 13 .wls.txt files 0.2 nm, 3,251 pts)",
    num_samples=23,  # 12 glycoporphyrins (6a-d, 7b-h, 8a) + 10 A2B2 starting porphyrins (4b/e/h, 5b/c/e/f/g/h, EtDPP) + TPP
    num_spectra=24,  # one absorbance spectrum per UV-Vis txt (6a measured in two solvents); ROS .bas and quantum-yield .QUA files are single-wavelength (377 nm) time series, not counted
    num_spectral_values=107274,
    spectral_target_relationship="Soret (~420 nm) and Q-band (500-700 nm) positions and intensities vs sugar (Glu, Gal, Xyl, Rha) and aryl/alkynyl substituents -> red-shifted absorption beyond 645 nm for photodynamic therapy; DPBF absorbance decay under 425/550/690 nm irradiation -> ROS / singlet oxygen generation efficiency",
    source_file="15728134.xml (Org. Lett. 2025 27:7779, doi:10.1021/acs.orglett.5c02038 'Red-Shifted Glycoporphyrins: Synthesis via Sonogashira Cross-Coupling and Studies on Reactive Oxygen Species Production'); Charakterystyka.zip -> glycoporphyrins/, 'Porphyrin A2B2 starting materials'/, 'sugar derivatives'/ each compound folder with UV-Vis (*.txt WL/Abs/T%, *.wls + .wls.txt), NMR (JEOL .jdf), ROS (*.bas + .txt); 'Quantum yield.zip' (.QUA + txt at 377 nm)",
    confidence=0.8,
)

R["15728993"] = dict(
    modality="Reflection-absorption infrared spectroscopy (RAIRS, FTIR) of CO2 ice deposited on gold-supported amorphous MgFeSiO4 silicate films, bare or pre-covered with CH3OH, CH4, CO, compact/porous amorphous water or CH3OH:H2O ices, during warm-up from 15 K",
    spectral_range_original_min=599.7531738, spectral_range_original_max=4999.0680542, spectral_range_original_unit="cm-1",
    num_spectral_channels=9126, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=7,  # Au-Si (bare silicate), Au-Si_CH3OH, Au-Si_CH4, Au-Si_CO, Au-Si_CW (compact water), Au-Si_pASW (porous water), Au-Si_CH3OH-H2O
    num_spectra=125,  # temperature series 15-125 K in 5 K steps per substrate/ice system
    num_spectral_values=1140750,  # 125 x 9,126
    spectral_target_relationship="CO2 nu3 (2,343 cm-1), 13CO2 (2,283 cm-1, split marking diffusion onset) and bending-mode profiles vs temperature and underlying ice -> surface selection-rule relaxation on silicate, CO2 segregation and crystallisation temperatures, compared with JWST ice band observations",
    source_file="15728993.pdf (Suhasaria, Leuschner, Jager, Gieser & Henning 2025, arXiv:2507.00836 'CO2 infrared spectra on silicate dust grain analogs: Implications for JWST observations'); 7 zips Au-Si*.zip -> <system>_<T>K.dpt (2-column OPUS export, wavenumber/absorbance)",
    confidence=0.85,
)

R["15761563"] = dict(
    modality="UV-Vis-NIR absorption (Agilent Cary 5000), photoluminescence excitation/emission (Edinburgh FLS1000; VUV McPherson for UVC), temperature-dependent and NIR emission, and visible-to-UVC up-conversion spectra of Pr3+-doped SrO-CaO-MgO-SiO2 glasses",
    spectral_range_original_min=190, spectral_range_original_max=2595, spectral_range_original_unit="nm",
    sampling_interval=0.5, sampling_interval_unit="nm (absorption 190-2,595 nm; PL 0.25-1 nm grids)",
    num_samples=3,  # SCMS glasses with 0.5, 1.0 and 2.5% Pr3+
    num_spectra=41,  # Fig2a 3 absorption, Fig2b 3, Fig5 1 UVC emission, Fig7 3 up-conversion, Fig8a-c/9a-c 18 excitation/emission, Fig10 1 NIR emission, Fig11a-c 12 temperature-dependent; XRD (Fig1), decays (Fig13), energy levels/power tables not counted
    num_spectral_values=48061,  # approx. for Fig8/9 (3 x ~3,420 rows)
    spectral_target_relationship="Pr3+ 4f-4f absorption lines (3H4->3P2,1,0, 1D2, 1G4, 3F4,3, 3F2) and 4f5d UVC emission (230-300 nm) under blue excitation, up-conversion intensity vs power density and Pr concentration -> UVC up-conversion for antimicrobial surfaces, Vis-NIR luminescence and thermal quenching (80-715 K)",
    source_file="15761563.xml (Materials 2024 17:1771, doi:10.3390/ma17081771 'UVC Up-Conversion and Vis-NIR Luminescence Examined in SrO-CaO-MgO-SiO2 Glasses Doped with Pr3+'); 'Figure 1.dat ... Figure 13b.dat' (tab-separated, wavelength/intensity pairs per figure)",
    confidence=0.8,
)

R["15863720"] = dict(
    modality="UV-Vis transmittance spectroscopy of poly(lactic acid) films with lignin (L) and nanolignin (NL) prepared by melt mixing or in-situ ring-opening polymerisation (UV-blocking)",
    spectral_range_original_min=199.9991, spectral_range_original_max=800.00751, spectral_range_original_unit="nm",
    num_spectral_channels=1202, sampling_interval=0.5, sampling_interval_unit="nm",
    num_samples=8,  # 3 melt-mixed films (PLA and PLA/L, PLA/NL) + 5 ROP films (neat PLA and lignin/nanolignin contents)
    num_spectra=8,
    num_spectral_values=9616,
    spectral_target_relationship="UV-Vis transmittance (UVA/UVB blocking 200-400 nm, visible transparency) vs lignin/nanolignin type, content and processing route -> UV-shielding of PLA/lignin composites",
    source_file="15863720.xml (Polymers 2023 15:2386, doi:10.3390/polym15102386 'Poly(Lactic Acid) Composites with Lignin and Nanolignin Synthesized by In Situ Reactive Processing'); 'UV-Vis transmittance of the PLA L and NL composites.xlsx' sheets 'melt mixed' and 'ROP' (wavelength nm + transmittance % columns)",
    confidence=0.75,
)

R["15863753"] = dict(
    modality="ATR-FTIR spectroscopy of organosolv beech-wood lignin before and after ball milling",
    spectral_range_original_min=650, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3351, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=2,  # OBS lignin, OBSBM8 (ball-milled 8 h)
    num_spectra=2,
    num_spectral_values=6702,
    spectral_target_relationship="Lignin aromatic skeletal (1,600/1,510 cm-1), C=O (1,710 cm-1) and OH (3,400 cm-1) bands before/after ball milling -> structural integrity of lignin used as PLA filler",
    source_file="15863753.xml (Terzopoulou, Xanthopoulou, Pardalis, Pappa, Torofias, Triantafyllidis & Bikiaris 2022 Molecules 27:8143, doi:10.3390/molecules27238143); 'FTIR Spectra of organosolv lignin and organosolv lignin after ball milling.xlsx' sheets OBS, OBSBM8",
    confidence=0.8,
)

R["15863755"] = dict(
    modality="ATR-FTIR spectroscopy of PLA composites with organosolv lignin (OBS) and ball-milled organosolv lignin (OBSBM8) at different loadings",
    spectral_range_original_min=650, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3351, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=11,  # PLA neat and PLA/OBS, PLA/OBSBM8 composites (0.5-5 wt%)
    num_spectra=11,  # sheet PLA_OBS 4 + sheet PLA_OBSBM8 7
    num_spectral_values=36861,
    spectral_target_relationship="PLA ester C=O (1,750 cm-1) and lignin aromatic/OH bands vs lignin content -> lignin dispersion and PLA-lignin interactions in melt-mixed composites",
    source_file="15863755.xml (Terzopoulou et al. 2022 Molecules 27:8143, doi:10.3390/molecules27238143 'Synthesis and Characterization of Poly(lactic acid) Composites with Organosolv Lignin'); 'FTIR Spectra of PLA Lignin Composites.xlsx' sheets PLA_OBS, PLA_OBSBM8",
    confidence=0.8,
)

R["15968135"] = dict(
    modality="FTIR spectroscopy (PerkinElmer FTIR-2000) of spent-wood-pellet biochars pyrolysed at 550 and 700 C",
    spectral_range_original_min=450, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3551, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=2,  # SWP550, SWP700
    num_spectra=2,
    num_spectral_values=7102,
    spectral_target_relationship="Loss of O-H, aliphatic C-H and C=O bands and growing aromatic C=C with pyrolysis temperature -> carbonisation degree of biochar fillers for PLA biocomposites",
    source_file="15968135.xml (Polymers 2025 17:263, doi:10.3390/polym17030263 'Synthesis and Characterization of PLA/Biochar Bio-Composites Containing Different Biochar Types and Content'); 'FTIR of biochar pyrolyzed at two different temperatures.xlsx' sheets SWP550, SWP700",
    confidence=0.85,
)

R["15968181"] = dict(
    modality="FTIR spectroscopy (PerkinElmer FTIR-2000) of PLA/biochar biocomposites with 1-5 wt% SWP550 or SWP700 biochar",
    spectral_range_original_min=450, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3551, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=7,  # PLA neat, PLA/SWP550 1/2.5/5%, PLA/SWP700 1/2.5/5% (neat PLA repeated in both sheets)
    num_spectra=8,
    num_spectral_values=28408,
    spectral_target_relationship="PLA ester bands with biochar addition -> absence of chemical interaction / dispersion of biochar in PLA biocomposites (with DSC, XRD, mechanical tests)",
    source_file="15968181.xml (Polymers 2025 17:263, doi:10.3390/polym17030263); FTIR.xlsx sheets PLA-SWP550, PLA-SWP700 (wavenumber + 4 absorbance columns: PLA neat, 1%, 2.5%, 5%)",
    confidence=0.85,
)

R["15969268"] = dict(
    modality="FTIR spectroscopy of poly(butylene succinate) and PBSu/5% biochar films during accelerated UV ageing (0-21 days)",
    spectral_range_original_min=450, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3551, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=2,  # PBSu and PBSu/5% biochar, each at 0, 7, 14, 21 days of UV irradiation
    num_spectra=8,
    num_spectral_values=28408,
    spectral_target_relationship="Growth of carbonyl/hydroxyl bands (photo-oxidation products) with UV exposure time, reduced for biochar-filled films -> biochar as UV stabiliser of PBSu",
    source_file="15969268.xml (Polymers 2024 16:3080, doi:10.3390/polym16213080 'Biochar as a UV Stabilizer: Its Impact on the Photostability of Poly(butylene succinate) Biocomposites'; Zenodo title: Papadopoulou, Ainali et al.); FTIR.xlsx sheets 'Figure 2a' (PBSu 0/7/14/21 d), 'Figure 2b' (PBSu/5% BC 0/7/14/21 d)",
    confidence=0.85,
)

R["16029124"] = dict(
    modality="ATR-FTIR spectroscopy of human milk extracellular vesicle (HMEV) isolates for biochemical fingerprinting",
    spectral_range_original_min=399.68863, spectral_range_original_max=3996.88633, spectral_range_original_unit="cm-1",
    num_spectral_channels=1747, sampling_interval=2.06, sampling_interval_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=10,  # human milk donors/isolates m1-m10 (1-3 replicate spectra each)
    num_spectra=19,  # readable 2-column TXT spectra (m10.2 present twice: 'm10.2.txt' and 'm10.2..txt'); m7.2 and m8.2 are binary SPC files saved as .txt (not counted)
    num_spectral_values=33193,  # 19 x 1,747
    spectral_target_relationship="ATR absorbance of EV proteins (amide I/II 1,650/1,540 cm-1), lipids (CH2 2,850/2,920, ester C=O 1,740 cm-1) and nucleic acids/sugars (1,080 cm-1) -> purity and biochemical fingerprint of HMEVs isolated by the proposed workflow, alongside TRPS size, ExoView tetraspanins and inflammatory biomarkers",
    source_file="16029124.xml (J. Extracell. Biol. 2026 5:e70110, doi:10.1002/jex2.70110 'Workflow for the Isolation and Characterisation of Human Milk Extracellular Vesicles (HMEVs) and Their Inflammatory Biomarker Profile'); RAWDATA.zip -> ATR-FTIR/m*.txt (x, M.n.mat), ExoView (xlsx/png/html report), TRPS (txt/xlsx)",
    confidence=0.75,
)

R["16261501"] = dict(
    modality="ATR-FTIR (Agilent Cary 630) of ZIF-8 frameworks synthesised with melamine / triaminopyrimidine modulators and of the modulators, plus Raman (Renishaw inVia, 532 nm) of the carbonised (1,000 C) ZIF-derived materials",
    spectral_range_original_min=501.086, spectral_range_original_max=4000.36533, spectral_range_original_unit="cm-1",
    sampling_interval=0.93, sampling_interval_unit="cm-1 (FTIR 3,596 pts 4,000-651 cm-1; Raman shift 1,742 pts 501-3,201 cm-1, ~1.55 cm-1)",
    num_samples=8,  # melamine, TAP, ZIF-8, Mel-ZIF, TAP-ZIF (FTIR); ZIF 1000, Mel-ZIF 1000, Tap-ZIF 1000 (Raman)
    num_spectra=8,  # 5 FTIR + 3 Raman (XRD, NMR, XPS, ToF-SIMS, TGA, sorption sheets not counted)
    num_spectral_values=23206,  # 5 x 3,596 + 3 x 1,742
    spectral_target_relationship="FTIR imidazolate ring / triazine and amine bands -> incorporation of N-heterocyclic amine modulators into ZIF-8; Raman D/G bands of carbonised products -> graphitisation and defect structure after thermal conversion, linked to N-doping and CO2 adsorption",
    source_file="16261501.xml (J. Mater. Chem. A 2025 13:28006, doi:10.1039/d5ta04831a 'Impact of N-heterocyclic amine modulators on the structure and thermal conversion of a zeolitic imidazole framework'); 'Melamine-ZIF DATA1406.xlsx' sheets FTIR (%T/wavenumber pairs), Raman; plus XRD, SS-NMR, TGA, liquid NMR, BET, XPS, CO2/N2 adsorption, ToF-SIMS sheets",
    confidence=0.8,
)

R["16268857"] = dict(
    modality="Raman spectroscopy (Renishaw inVia, 532 nm) of graphene oxide foils, pristine and after focused Cu ion beam bombardment (stripe and edge regions)",
    spectral_range_original_min=-49.0093, spectral_range_original_max=3002.13, spectral_range_original_unit="cm-1",
    wavelength_min_nm=3330.97, wavenumber_min_cm1=-49.0093, wavenumber_max_cm1=3002.13,  # Raman shift axis starts below 0
    num_spectral_channels=2784, sampling_interval=1.1, sampling_interval_unit="cm-1 Raman shift",
    num_samples=3,  # pristine GO, bombarded stripe, bombarded edges/cracks
    num_spectra=3,
    num_spectral_values=8352,
    spectral_target_relationship="Raman D (~1,350) / G (~1,590 cm-1) band intensities and widths -> defect generation and partial reduction of GO by Cu ion bombardment, linked to enhanced edge electrochemical reactivity (SECM) and XPS oxygen loss",
    source_file="16268857.xml (Luxa, Malinsky, Novak, Havranek, Mazanek, Regner & Sofer 2026 Langmuir 42:18801, doi:10.1021/acs.langmuir.6c01117); Dataset_for_Copper_Ion_Beam-Induced_..._Foils.zip -> Raman/*.csv (3), XPS/C 1s csv, SECM array-scan approach curves (4,143 .dat) and CVs, RMF.txt (not optical spectra)",
    confidence=0.85,
)

R["16315733"] = dict(
    modality="ATR-FTIR (Thermo Nicolet iS50, Ge ATR), confocal Raman (Renishaw inVia InSpect) and intrinsic tryptophan/tyrosine fluorescence emission (SpectraMax iD3, excitation 260/270/280 nm) of freeze-dried E. coli inclusion bodies from an ambr250 cultivation design of experiments",
    spectral_range_original_min=100.834, spectral_range_original_max=4000.122, spectral_range_original_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1 (FTIR 7,053 pts 600-4,000; Raman shift 3,189 pts 101-3,201, ~0.97 cm-1); fluorescence 1 nm, 71 pts 300-370 nm",
    spectral_resolution=4, spectral_resolution_unit="cm-1 (FTIR)",
    num_samples=24,  # inclusion-body samples H1V1-H1V12 x 2 bioreactor replicates (.1/.2)
    num_spectra=174,  # 27 FTIR (24 samples + 3 backgrounds) + 75 Raman (triplicates) + 72 fluorescence (24 x 3 excitation wavelengths)
    num_spectral_values=434718,  # 190,431 + 239,175 + 5,112
    spectral_target_relationship="Amide I secondary-structure bands (FTIR/Raman beta-sheet ~1,625 cm-1 vs native helix), aromatic fluorescence emission maxima and intensity -> inclusion-body biophysical properties (aggregation state, compactness) linking cultivation conditions (temperature, feed, induction) to refolding yield; used in a causal DAG / ML model",
    source_file="16315733.xml (Biotechnol. Bioeng. 2025 122:3098, doi:10.1002/bit.70033 'The Missing Link: Connecting Cultivation Conditions and Refolding Performance via Inclusion Body Biophysical Properties'); ORD_effic_ib.zip (Snakemake project): experiments/results/ambr250 material/FT-IR/raw data/*.CSV, Raman/*.txt (#Wave #Intensity), Fluorescence/ex260/270/280nm_data.csv (wavelength + 24 sample columns), CE-SDS, LD, notebooks, src",
    confidence=0.8,
)

R["16633922"] = dict(
    modality="Transmission infrared spectroscopy of silica-supported organometallic precursors and MGa@SiO2 catalysts (M = Ru, Os, Rh, Ir) during surface-organometallic synthesis, CO-adsorption IR, and in situ IR time series under CO2 hydrogenation (X-ray absorption XANES/EXAFS also deposited, not counted)",
    spectral_range_original_min=399.1989, spectral_range_original_max=4001.632, spectral_range_original_unit="cm-1",
    sampling_interval=1.02, sampling_interval_unit="cm-1 (synthesis IR 3,529 pts 400-3,998; in situ 6,950 pts 650-4,000, ~0.48 cm-1)",
    num_samples=16,  # approx.: SiO2-700, Ga@SiO2, grafted Ru/Os/Rh/Ir precursors and M@SiO2 / MGa@SiO2 / Rh1Ga2, Rh1Ga4 catalysts
    num_spectra=138,  # Fig 1 10 + S2, S13-S20 27 + S30 CO-adsorption 12 + S81/S82 in situ 8 x 7
    num_spectral_values=535266,
    spectral_target_relationship="IR bands of grafted ligands (C-H, Si-OH 3,747 cm-1) disappearing after H2 treatment -> ligand-free MGa nanoparticles; red shift of adsorbed CO on MGa vs M -> alloy formation; in situ IR under CO2/H2 -> formate/methoxy intermediates at MGa-GaOx interfaces responsible for methanol vs methane selectivity",
    source_file="16633922.xml (JACS Au / J. Am. Chem. Soc. 2025 'Gallium: A Universal Promoter Switching CO2 Methanation to Methanol ...'); Figures-manuscript.XLSX (Fig 1 IR, Fig 3 XANES), 'Figures S2 S13-S25 and S30.XLSX' (IR; S21-S25 particle sizes), 'Figure S81-S82.XLSX' (in situ IR vs time), Figure S44-S58 / S59-S71 / S72-S80 (EXAFS/XANES), 'Catalytic data.rar' (S31-S40 xlsx), CIF rar (DFT)",
    confidence=0.75,
)

R["16875423"] = dict(
    modality="UV-Vis absorption spectroscopy of carbon nitride quantum dots (CNQDs) prepared from urea, thiourea and their mixture (sulfur doping); EPR and XPS spectra also deposited (not optical)",
    spectral_range_original_min=200, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=601, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=3,  # CNQD-U, CNQD-UT, CNQD-T
    num_spectra=3,
    num_spectral_values=1803,
    spectral_target_relationship="pi-pi* (~230 nm) and n-pi* (~330 nm) absorption bands and visible tail vs sulfur doping -> band-structure changes of CNQDs governing controlled ROS generation (EPR spin trapping)",
    source_file="16875423.xml (Global Challenges 2026 10:e00447, doi:10.1002/gch2.202500447 'Engineering Carbon Nitride Quantum Dots via Sulfur Doping for Controlled Reactive Oxygen Species Generation'); UVVis_Spectra_fig3.xlsx (3 wavelength/absorbance pairs); EPR_spectra_fig5.xlsx, XPS_spectra_fig2.xlsx (not optical)",
    confidence=0.8,
)

R["17053968"] = dict(
    modality="UV-Vis absorption / photoluminescence spectra (in OriginLab projects only) and fluorescence lifetime (TCSPC) of bay-functionalised dibenzo[b,d]thiophene sulfone derivatives; dataset dominated by NMR, HRMS, single-crystal X-ray frames and Gaussian DFT outputs",
    spectral_range_original_unit="nm",
    num_samples=4,  # compounds 3, 9, 10, 11 with spectra_N.opju (lifetimes for 3, 10, 11)
    spectral_target_relationship="Absorption/emission of bay-extended DBTS derivatives (alkynyl, aryl, phosphine oxide substituents) and their excited-state lifetimes vs DFT HOMO/LUMO energies and torsion angles -> structural expansion tuning photophysics of DBTS luminophores",
    source_file="17053968.xml (Org. Lett. 2025 27:9136, doi:10.1021/acs.orglett.5c02414 'Structural Expansion of Dibenzo[b,d]thiophene Sulfone through Functionalization at Bay Positions'); spectra_3/9/10/11.opju and dbs.opju (Origin projects, values not readable here); lifetime_3/10/11 (FLS .FL + txt decays, IRF); calculations.xlsx (HOMO/LUMO, energies, torsions); NMR .mnova/raw, HRMS tif, 4 SCXRD .rar (CrysAlisPro), Gaussian .log/.FChk",
    confidence=0.35,
)

R["17358913"] = dict(
    modality="Far-UV and near-UV/visible (Soret) electronic circular dichroism spectroscopy of human eosinophil peroxidase (EPO) and myeloperoxidase (MPO), with CD thermal unfolding curves",
    spectral_range_original_min=180, spectral_range_original_max=500, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (far-UV 180-260/300 nm, 81/121 pts; near-UV-Vis 260-500 nm, 241 pts)",
    num_samples=3,  # EPO, MPO (incl. heat-treated MPO at 104 C) and phosphate buffer blank
    num_spectra=8,  # unique CD spectra: buffer, EPO 20 C, MPO 20 C, MPO 104 C, far-UV EPO/MPO, near-UV EPO/MPO (repeats in xlsx summary sheets and single-wavelength temperature/DSF melting curves not counted)
    num_spectral_values=1048,  # 4 x 81 + 2 x 121 + 2 x 241
    spectral_target_relationship="Far-UV CD (alpha-helical minima 208/222 nm) and Soret-region CD of the heme (~411-413 nm) -> secondary structure and heme-cavity architecture of EPO vs MPO, thermal stability (Tm from 411/222 nm melting) linked to posttranslational modifications seen in the first EPO crystal structure",
    source_file="17358913.xml (Pfanzagl, Gruber-Grunwald, Leitgeb, Furtmuller & Obinger 2023 J. Biol. Chem. 299:105402, doi:10.1016/j.jbc.2023.105402); EPO_2023.zip -> Data/CD/*.csv + .dsx (Jasco) and xlsx, Data/CD/20221213/EPO_MPO_far/near.csv; DSC, MS (peptide mapping raw), SDS-PAGE, alignment, structure (PDB/PSE/Robetta); Data/UV-VISspec folder is empty",
    confidence=0.75,
)

R["17415044"] = dict(
    modality="Grazing-angle ATR infrared (IR-GAATR) spectra of zwitterionic/hydrophilic terpolymer brushes (CBMAA/HPMA/SBMAA) on silicon, plus IRRAS spectra of RGD peptide binding (binary vendor files); XPS core-level data also deposited",
    spectral_range_original_min=69.4259, spectral_range_original_max=4001.634, spectral_range_original_unit="cm-1",
    num_spectral_channels=2040, sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=3,  # pHP(97)SB(3), pCB(20)HP(77)SB(3), pCB(30)HP(67)SB(3) brushes
    num_spectra=3,  # FIG.2 d.xlsx; the 4 IRRAS files (*.DX.JDX, Fig S3) are binary spectra despite the .JDX name and are not counted
    num_spectral_values=6120,
    spectral_target_relationship="Amide I/II (1,650/1,530 cm-1), carboxylate (~1,600 cm-1) and sulfonate (1,040/1,180 cm-1) bands vs CBMAA content -> brush composition confirmation; IRRAS difference after RGD coupling -> peptide immobilisation for antifouling, antibacterial and osteoblast-adhesive coatings",
    source_file="17415044.xml ('Fine-Tuned Functionalizable Terpolymer Brush Nanocoating Resists Bacterial Biofilm and Promotes Osteoblast Adhesion'); data.rar -> fig. 2/FIG.2 d.xlsx (3 wavenumber/absorbance pairs), fig.2 a b c.xlsx (XPS), fig. 3-6 xlsx/png (QCM-D, bacterial and cell counts, images), 4 binary '*.DX.JDX' IRRAS spectra, videos; readme.txt with figure captions",
    confidence=0.7,
)

R["17422743"] = dict(
    modality="UV-Vis-NIR absorbance spectroscopy (Thermo Evolution 350, temperature-controlled) of EDOT/PSS oxidative polymerisation kinetics with APS or Fe(II), and of ultrasound-triggered (focused ultrasound) PEDOT formation in double emulsions",
    spectral_range_original_min=190, spectral_range_original_max=1100, spectral_range_original_unit="nm",
    num_spectral_channels=911, sampling_interval=1, sampling_interval_unit="nm (kinetics 911 pts; Fig 4b 456 pts at 2 nm)",
    num_samples=20,  # approx.: reaction conditions varying temperature, APS and EDOT/PSS concentration + ultrasound/control double-emulsion samples
    num_spectra=231,  # kinetic series 'Cycle N' (3-min increments) in Fig 2a, 2b, S6-S9 + Fig 4b FUS/control + S11/S17/S20 spectra
    num_spectral_values=206027,
    spectral_target_relationship="Growth of the PEDOT polaron/bipolaron band (broad NIR shoulder > 700 nm) and EDOT depletion vs time, temperature, oxidant and monomer concentration -> polymerisation rate constants guiding acoustic (ultrasound-heated) in-situ printing of conductive polymers in tissue-like media",
    source_file="17422743.xml (Trepka, Cooper, Brinson, Thompson, Malinao, Rommelfanger, Fordyce & Hong 2025 PNAS 122:e2509652122, doi:10.1073/pnas.2509652122 'Acoustic printing of conductive polymers'); dataset.zip -> 'Fig. 2a', 'Fig. 2b', 'Fig. S6, S7, S8, S9' (CSV per cycle: Wavelength (nm), Absorbance), 'Fig. 4b' FUS/Control, S11/S17/S20 csv; Mnova NMR (S1, S2, S12); README.rtf",
    confidence=0.8,
)

R["17423992"] = dict(
    modality="Optical emission/absorption spectra (Avantes fibre spectrometer, counts) of carbon dots produced by blue-laser ablation in liquid for 30/60 min, and ATR-FTIR (JASCO FT/IR-4600) of polycaprolactone (PCL) and PCL + carbon dot composites",
    spectral_range_original_min=294.64, spectral_range_original_max=25050.5, spectral_range_original_unit="nm",
    sampling_interval=0.27, sampling_interval_unit="nm (Fig 4: 1,705 pts 294.6-754.8 nm); FTIR 3,736 pts 399.2-4,000.6 cm-1 (~0.96 cm-1)",
    num_samples=4,  # carbon/graphite target, PCL, PCL + CDs 30 min, PCL + CDs 60 min (Fig 4: pristine, 30 min, 60 min ablation)
    num_spectra=7,  # Fig4 3 + Fig6 4 FTIR
    num_spectral_values=20059,  # 3 x 1,705 + 4 x 3,736
    spectral_target_relationship="Carbon-dot optical spectra vs ablation time -> CD formation/concentration; FTIR C=O (1,720 cm-1), C-O and O-H bands of PCL with embedded CDs -> chemical compatibility of fluorescent PCL composites for tissue engineering/packaging",
    source_file="17423992.xml (Polymers 2024 16:2801, doi:10.3390/polym16192801 'Blue Laser for Production of Carbon Dots'); Fig4.dat (wavelength + pristine/30 min/60 min), Fig6.dat (wavenumber + carbon, PCL, PCL CDs30, PCL CDs60)",
    confidence=0.7,
)

R["17424121"] = dict(
    modality="ATR-FTIR (JASCO) of polyvinyl alcohol and PVA + carbon dot composites, UV-Vis transmittance of the films, and fibre-spectrometer (Avantes) optical spectra of carbon dots made by laser ablation in liquid",
    spectral_range_original_min=200, spectral_range_original_max=25050.5, spectral_range_original_unit="nm",
    sampling_interval=0.5, sampling_interval_unit="nm (UV-Vis 1,293 pts 200-846 nm; Avantes 1,705 pts 294.6-754.8 nm); FTIR 3,736 pts 399.2-4,000.6 cm-1",
    num_samples=3,  # PVA virgin, PVA virgin repeat, PVA + CDots (FTIR); 2 films UV-Vis; 3 CD suspensions (Fig 8)
    num_spectra=8,  # Fig6 3 FTIR + Fig7 2 UV-Vis transmittance + Fig8 3 Avantes spectra
    num_spectral_values=18909,  # 3 x 3,736 + 2 x 1,293 + 3 x 1,705
    spectral_target_relationship="FTIR O-H/C-O bands of PVA with CDs -> hydrogen bonding of CDs in the matrix; UV-Vis transmittance -> UV-shielding/optical clarity of PVA+CD films; CD optical spectra -> luminescent CDs (blue emission under 365 nm) from laser ablation in PBS",
    source_file="17424121.xml (Polymers 2024 16:1390, doi:10.3390/polym16101390 'Polyvinylalcohol Composite Filled with Carbon Dots Produced by Laser Ablation in Liquids'); Fig6.txt (JCAMP-like header block, 3 FTIR columns), Fig7.txt (wavelength + 2 transmittance columns), Fig8.txt (Wave [nm] + 3 count columns)",
    confidence=0.7,
)

R["17424222"] = dict(
    modality="ATR-FTIR (JASCO FT/IR-4700) and UV-Vis transmittance (JASCO V-750) of cyclic olefin copolymer (COC) and PET foils before and after pulsed-laser deposition of MoS2",
    spectral_range_original_min=200, spectral_range_original_max=25050.5, spectral_range_original_unit="nm",
    sampling_interval=0.5, sampling_interval_unit="nm (UV-Vis 1,301 pts 200-850 nm); FTIR 3,736 pts 399.2-4,000.6 cm-1",
    num_samples=4,  # COC virgin, COC/MoS2 (and high deposit), PET virgin, PET/MoS2 (and high deposit)
    num_spectra=8,  # 4 FTIR + 4 UV-Vis; laser-plasma TOF trace (Fig 4a), Origin crater scan and capacitance tables (Fig 9) not counted
    num_spectral_values=20148,  # 4 x 3,736 + 4 x 1,301
    spectral_target_relationship="FTIR polymer bands and UV-Vis transmittance loss vs MoS2 deposit -> chemical stability of COC/PET substrates and optical/dielectric modification by PLD MoS2 coatings for capacitive sensing",
    source_file="17424222.xml (Cutroneo, Malinsky, Novak, Maly, Stofik, Slepicka & Torrisi 2024 Micromachines 15:1425, doi:10.3390/mi15121425); 'Fig 6 a/b FTIR *.txt' (2-column), Fig7_*.txt (2-column UV-Vis), 'Fig. 4 a MoS2 600 mJ SF 1 colpo.txt' (oscilloscope), 'Fig. 4 b Scan of the crater.opj', Fig9a-d.txt (capacitance)",
    confidence=0.8,
)

R["17575141"] = dict(
    modality="UV absorbance spectra (SpectraMax M2e plate/cuvette reader, 200-300 nm) of purified cyanobacterial anabaenopeptins A, C, D and ferintoic acid A at several concentrations for molar extinction coefficients; NMR, HRMS/MS2 and HPLC-PDA purity data also deposited",
    spectral_range_original_min=200, spectral_range_original_max=300, spectral_range_original_unit="nm",
    num_spectral_channels=101, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=4,  # AP-A, AP-C, AP-D, FAA (each at 5-6 concentrations)
    num_spectra=63,  # approx.: (5 + 6 + 5 + 5) concentration blocks x 3 stacked replicate scans of 101 points
    num_spectral_values=6363,
    spectral_target_relationship="Absorbance at 278 nm (Tyr/Trp-type chromophore) vs molar concentration (Beer-Lambert) -> molar extinction coefficients of anabaenopeptins for quantification in toxicology and environmental monitoring",
    source_file="17575141.xml (Quandt, Stringer, Silva, Prakash, Anderson, Peraino, Kodanko & Westrick 2026 Data in Brief 66:112701, doi:10.1016/j.dib.2026.112701); All-Anabaenopeptin-Files.zip -> <compound>-Data/UV-VIS-and-Extinction-Coefficient/UV-VIS-Data-*.xlsx (blocks: concentration M, Wavelength, Temperature, A1), *.opj plots, NMR (.mnova/FIDs), timsTOF/FTMS raw MS, Shimadzu .lcd purity, optical-rotation txt",
    confidence=0.7,
)

R["17649859"] = dict(
    modality="ATR-FTIR spectroscopy of spray-dried nano-hydroxyapatite (nHAp) powder before and after sintering at 1,100 C",
    spectral_range_original_min=399.263973, spectral_range_original_max=4000.354973, spectral_range_original_unit="cm-1",
    num_spectral_channels=1868, sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=2,  # 843.HAp (as spray-dried) and Ht_843_1100 (sintered 1,100 C, 1 h)
    num_spectra=2,
    num_spectral_values=3736,
    spectral_target_relationship="Phosphate nu3/nu1 (1,020-1,090/962 cm-1), nu4 (560-600 cm-1), OH (3,570/630 cm-1) and carbonate (1,410-1,450 cm-1) bands before/after sintering -> phase purity and carbonate loss of calcium phosphate nanoparticles used in GelMA/HAp osteochondral bioinks",
    source_file="17649859.xml - related paper using the powder (Materials 2023 16:7214, doi:10.3390/ma16227214 'Cell-Laden 3D Printed GelMA/HAp and THA Hydrogel Bioinks ...'); 'FT-IR_ATR data.zip' -> 843.HAp.csv, Ht_843_1100.csv (+ bmp screenshots); BET, SEM, TEM, XRD (.xrdml/csv) zips; overview PDF; ReadMe",
    confidence=0.75,
)

R["17787891"] = dict(
    modality="Low-temperature (100 K) Raman spectroscopy and ATR-IR spectroscopy (JCAMP-DX, 4 cm-1) of XeF2 adduct salts [Xe2F3][MF3(XeF2)3][AsF6]2 (M = Pd, Pt), [Xe2F3][AsF6] and KAsF6",
    spectral_range_original_min=50, spectral_range_original_max=3996.3616, spectral_range_original_unit="cm-1",
    sampling_interval=0.5, sampling_interval_unit="cm-1 Raman shift (raw/processed .dpt 50-1,410 cm-1); ATR-IR 1,746 pts 3,996-400 cm-1 (~2.06 cm-1)",
    spectral_resolution=4, spectral_resolution_unit="cm-1 (ATR-IR)",
    num_samples=5,  # KAsF6, [Xe2F3][AsF6], [Xe2F3][PdF3(XeF2)3][AsF6]2, Pt analogue in aP256 and oP256 polymorphs
    num_spectra=35,  # Raman 30 .dpt (raw replicate scans + 3 averaged) + 5 ATR-IR
    num_spectral_values=90360,  # 81,630 Raman + 5 x 1,746 IR
    spectral_target_relationship="Xe-F terminal/bridging stretches (580-620, ~500 cm-1), M-F modes and AsF6- nu1/nu5 (681/369 cm-1) compared with DFT frequencies -> coordination of XeF2 to PdF3+/PtF3+ cations and distinction of polymorphs",
    source_file="17787891.xml (Motaln, Virant & Lozinsek 2026 Inorg. Chem. 65:5668, doi:10.1021/acs.inorgchem.5c05940); Raman-data.zip (raw/<compound>/*.dpt, processed/*_avg.dpt), ATR-IR-data.zip (5 .dx JCAMP), DFT-data.zip (ORCA .out/.hess/.xyz); SCXRD-data.zip (2.96 GB) is not a valid zip (truncated/corrupt download)",
    confidence=0.8,
)

R["17816356"] = dict(
    modality="Raman and FTIR spectroscopy of argyrodite Li6PS5ClBr (LPSClBr) sulfide solid electrolyte, octylphosphonic acid (OPA) and its lithium salt (Li-OPA) coatings, including FTIR after humidity exposure",
    spectral_range_original_min=118.954, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1 (FTIR ~3,700 pts 300-4,000 / 250-4,000; Raman ~1,600 pts from ~119 cm-1)",
    num_samples=8,  # approx.: pristine LPSClBr, OPA, Li-OPA, OPA- and Li-OPA-coated LPSClBr at several loadings, before/after humid air
    num_spectra=38,  # approx.: Raman F1 5 + FTIR F1 14 + FTIR SI 1 4 + FTIR S1 1b 9 + humidity-test FTIR (S6) ~6; extra derived columns not separated
    num_spectral_values=129427,  # approx.
    spectral_target_relationship="Raman PS4^3- stretching (~425 cm-1) retention and FTIR P-O/P=O (1,000-1,200 cm-1), alkyl C-H and O-H bands -> chemical binding of Li-OPA molecular layer on the sulfide surface and suppression of hydrolysis (P-O-P/H2S formation) under humidity, enabling robust Li-metal all-solid-state batteries",
    source_file="17816356.xml (Fadillah, Braks, Oh, Liu, Turk, Tisi, Mensi, Ceriotti, Choi & Coskun 2025 Adv. Mater. 38:e15013, doi:10.1002/adma.202515013); 'Main manuscript Data - LiOPA.xlsx' (Raman F1, FTIR F1, electrochemistry, XPS sheets), 'Supporting Information - LiOPA.xlsx' (FTIR SI 1, FTIR S1 1b, XRD & FTIR humid test S6, XPS, EIS, cycling)",
    confidence=0.65,
)

R["17834901"] = dict(
    modality="DFT-computed (Gaussian, broadened harmonic) infrared spectra of lignin model compound monomers and hydrogen-bonded / pi-stacked dimers (benzene, phenol, anisole, guaiacol, biphenyl, guaiacyl dimers), with NIST experimental reference IR spectra (JCAMP-DX)",
    spectral_range_original_min=0, spectral_range_original_max=3999, spectral_range_original_unit="cm-1",
    wavelength_min_nm=2500.625,  # axis starts at 0 cm-1, so only the short-wavelength end is defined
    sampling_interval=1, sampling_interval_unit="cm-1 (computed 4,000 pts 0-3,999; NIST gas-phase 880 pts 450-3,966, solution ~3,600-3,860 pts 213-3,990)",
    num_samples=23,  # 17 computed structures (monomers, dimers, guaiacyl conformers) + 6 NIST compounds
    num_spectra=23,  # 17 computed + 6 experimental
    num_spectral_values=81884,  # 17 x 4,000 + 3 x 880 + 3,862 + 3,778 + 3,604
    spectral_target_relationship="Shifts of O-H stretching/bending and C-H stretching/bending bands between monomers and dimers vs noncovalent interaction (NCI) strength -> how hydrogen bonding and pi-stacking shape the IR spectra of lignin; validated against NIST spectra",
    source_file="17834901.xml (Molecules 2025 30:4694, doi:10.3390/molecules30244694 'The Role of Noncovalent Interactions in the Infrared Spectra of Lignin Model Compounds: A DFT Study'); IR_spectra_Final.rar -> 17 '<n>-IR_<structure>.txt' (X, Y, DY/DX); Experimental_IR_spectra-NIST.rar -> 6 .jdx; FCHK_final.rar and Log_files_Final.rar (Gaussian outputs)",
    confidence=0.75,
)

R["18060234"] = dict(
    modality="Mid-infrared photo-induced force microscopy (PiF-IR, MIRcat QCL) point spectra, 51-wavenumber sweep images and a full hyPIR hyperspectral cube of perylene (PMIS-C8) Langmuir-Blodgett monolayers on planar and nanostructured / evaporated gold, with bulk ATR-FTIR and transmission FTIR references",
    spectral_range_original_min=599.76792, spectral_range_original_max=4000.626132, spectral_range_original_unit="cm-1",
    sampling_interval=0.5, sampling_interval_unit="cm-1 (PiF-IR point spectra 2,001/2,145 pts 766-1,838 cm-1; hyPIR 2,145 channels; sweep images 51 wavenumbers; FTIR ~1 cm-1)",
    num_samples=4,  # PMIS-C8 monolayer on nanostructured Au (Pos1/Pos2, June 2025), on evaporated Au (Nov 2025, 2 days); bulk PMIS-C8 powder for ATR/FTIR
    num_spectra=379953,  # 44 point spectra + 5 FTIR/ATR + 13 forward sweep cubes (378,880 pixels x 51) + 1 hyPIR cube (32 x 32 x 2,145); backward-trace duplicates and the duplicate hyPIR zip not counted
    num_images=14, num_pixels=379904,
    num_spectral_values=21627284,  # approx.: 90,924 + ~17,000 + 378,880 x 51 + 1,024 x 2,145
    spectral_target_relationship="Anisotropic PiF-IR intensities of perylene imide C=O (~1,650-1,700 cm-1) and ring modes on nanostructured vs planar gold, compared with DFT-oriented vibrational oscillators -> hybrid near-field coupling and molecular orientation effects in nanoscale IR imaging",
    source_file="18060234.pdf (James, Ali, Ye, ... Presselt & Tauber 'Effect of hybrid field coupling in nanostructured surfaces on anisotropic signal detection in nanoscale infrared spectroscopic imaging methods'); 14 zips: 25061x/25112x_PMIS-C8_*_spectra/_scans/_hypir (VistaScan *_afmspectrumNNNN.txt, *Sweep PiFM*.int + Wavelengths.txt, topography .int, ANFATEC .txt), PiF-IR_PMISC8_evaporated-Au_hypir (duplicate cube), ATR-FTIR.zip (csv + BRUKER .dpt, water-vapour references), AFM.zip (.FLT), BAM_Deposition (jpg), Calculated_PMIS-C8_Spectra.zip (DFT mode HTML report, not counted)",
    confidence=0.6,
)

R["18216266"] = dict(
    modality="UV-Vis spectrophotometric titrations (Agilent Cary 60 with fibre-optic external cell, glovebox) for relative acidity (delta pKip) measurements of 33 acids in 1,2-difluorobenzene",
    spectral_range_original_min=270, spectral_range_original_max=800, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (mostly 270-700 nm, 431 pts; some to 600/800 nm)",
    num_samples=33,  # acids (CH, NH, OH acids) measured in 64 pairwise titration experiments
    num_spectra=6073,  # approx.: all absorbance columns of the 64 'Spectral_data' sheets (titration steps of acid pairs); may include a few processed columns
    num_spectral_values=2217401,  # approx.
    spectral_target_relationship="Spectral changes of neutral/anionic forms of two acids during titration with base/acid in 1,2-DFB -> ion-pair delta pKip between acid pairs -> self-consistent pKa (and pHabs via potentiometry) acidity scale in a low-polarity solvent, compared with COSMO-RS calculations",
    source_file="18216266.xml ('Acidity Scale in 1,2-Difluorobenzene', Univ. Tartu); DFB_pKa_measurement_files.zip -> 64 '<date>_(<acid1>_vs_<acid2>)_DFB.xlsx' (sheet Spectral_data + delta pKip calculation); DFB_pKa/pHabs Measurement and Minimization Results xlsx, potentiometric CSVs, COSMO/energy files, def2-TZVPP geometries, README.txt, Computational_methodology.pdf",
    confidence=0.7,
)

R["18234350"] = dict(
    modality="Raman micro-spectroscopy (Renishaw inVia, 532 nm, 6 cm-1) and transmission FTIR imaging (Bruker Lumos II, FPA hyperspectral maps, 4 cm-1) of fluorescent-protein-tagged and wild-type bacteria (S. aureus, others) in surface-associated microdroplets; fingerprint-region processed spectra",
    spectral_range_original_min=693.84765625, spectral_range_original_max=1851.140625, spectral_range_original_unit="cm-1",
    sampling_interval=1.14, sampling_interval_unit="cm-1 (Raman 1,015 pts 694-1,851; FTIR 508 pts 964-1,767, ~1.59 cm-1)",
    spectral_resolution=6, spectral_resolution_unit="cm-1 (Raman; FTIR 4 cm-1)",
    num_samples=6,  # approx.: bacterial strains (wild type and GFP/mCherry-tagged, e.g. S. aureus SH10)
    num_spectra=658,  # 58 Raman + 600 FTIR pixel/selected spectra (rows of the two sheets)
    num_spectral_values=363670,  # 58 x 1,015 + 600 x 508
    spectral_target_relationship="Protein amide, lipid, nucleic acid and carbohydrate bands, and fluorescent-protein chromophore contributions -> label-free discrimination of tagged vs wild-type bacteria and species within microdroplets (multivariate analysis in MATLAB), testing whether FP tags perturb vibrational signatures",
    source_file="18234350.xml (Faraday Discuss. 2026 265:76, doi:10.1039/d5fd00175g 'Vibrational spectroscopic characterisation of fluorescent-protein-tagged and wild-type bacteria in surface-associated microdroplets'); one workbook with sheets Raman (laser, power, strain, spectrum no. + 1,015 wavenumber columns) and FTIR (strain, spectrum no. + wavenumber columns)",
    confidence=0.75,
)

R["18269172"] = dict(
    modality="SWIR near-infrared hyperspectral imaging (Specim SWIR 3 line-scan camera, 288 bands) of post-industrial textile samples for fibre identification; only per-sample mean reflectance spectra are usable in this download",
    spectral_range_original_min=953.04, spectral_range_original_max=2547.64, spectral_range_original_unit="nm",
    num_spectral_channels=288, sampling_interval=5.6, sampling_interval_unit="nm",
    num_samples=71,  # textile samples (cotton, polyester, wool, viscose, blends, colours) with fibre-composition ground truth
    num_spectra=71,  # swir_mean_spectra.csv; SWIR-HSI.zip (10.8 GB, >11 M pixel spectra per the paper) is zero-filled in this download and not counted
    num_spectral_values=20448,  # 71 x 288
    spectral_target_relationship="SWIR reflectance features of cellulose (1,490/1,930/2,100 nm), polyester (1,660/2,130/2,250 nm), wool/protein (1,510/2,050/2,180 nm) and blends -> machine-learning identification of textile fibre composition for sorting and recycling",
    source_file="18269172.xml (Data in Brief 2026 65:112559, doi:10.1016/j.dib.2026.112559 'Introducing OpenTextile-NIR: Near-infrared hyperspectral imaging and photography dataset for optical identification of textiles'); swir_mean_spectra.csv (Label + 288 band columns), swir_mean_spectra_coordinates.csv, ground_truth_final.csv, rgb_mean_values.csv, RGB.zip (71 photos), example_file_reading.py; SWIR-HSI.zip is all zeros (incomplete download, needs re-download)",
    confidence=0.55,
)

R["18295631"] = dict(
    modality="ATR-FTIR spectroscopy (PerkinElmer Spectrum CSV exports) of cellulose and lignin purified from leaves of Asparagaceae species (Agave, Yucca and relatives)",
    spectral_range_original_min=650.612131, spectral_range_original_max=4000.612131, spectral_range_original_unit="cm-1",
    num_spectral_channels=1798, sampling_interval=1.865, sampling_interval_unit="cm-1",
    num_samples=14,  # approx.: 7 species x 2 fractions (cellulose, lignin), each in triplicate
    num_spectra=42,
    num_spectral_values=75516,  # 42 x 1,798
    spectral_target_relationship="Cellulose bands (1,430/1,372/1,336/897 cm-1) -> crystalline cellulose (LOI/TCI) indices; lignin aromatic 1,595/1,510 and syringyl/guaiacyl 1,325/1,265 cm-1 -> S/G character, related to wet-chemical extractives, lignocellulose, cellulose, lignin and hemicellulose contents of leaf biomass",
    source_file="18295631.xml (Villada-Lozada, Andres-Hernandez & Maceda 2026 Plants 15:468, doi:10.3390/plants15030468 'Chemical Composition and Structural Traits of Leaf Biomass in Selected Asparagaceae Species'); 'FTIR data' zip -> celulosa/*.csv and lignina/*.csv ('<species> cel|lig <rep>.csv', header lines then wavenumber,absorbance); 'Asparagaceae leaves raw data.xlsx' (composition table)",
    confidence=0.85,
)

R["18332267"] = dict(
    modality="Binned DFT-computed mid-infrared absorption spectra of polycyclic aromatic hydrocarbons from the NASA Ames PAH database (PAHdb), prepared as SMILES-spectrum training sets for graph-neural-network IR prediction",
    spectral_range_original_unit="cm-1",
    num_spectral_channels=180, sampling_interval_unit="bins (180-bin 'ALL_High' and 128-bin versions; bin edges not stated in the deposit)",
    num_samples=1570,  # unique PAH molecules (SMILES); 997 in the 50-100 atom subsets
    num_spectra=5134,  # 4 pickled datasets: 1,570 x 180 + 1,570 x 128 + 997 x 180 + 997 x 128 (overlapping molecules, different binning/subsets)
    num_spectral_values=790636,
    spectral_target_relationship="Molecular graph (SMILES) -> predicted binned IR absorption (3.3, 6.2, 7.7, 8.6, 11.2, 12.7 um aromatic infrared bands) with EMD/JSD/TVD/SIS losses -> fast reference spectra for interstellar PAH band analysis (JWST)",
    source_file="18332267.pdf (Tang, He, Wang & Qiu 'Graph Neural Network Prediction of Infrared Spectra of Interstellar Polycyclic Aromatic Hydrocarbons'); '3.2_CH_Cleaner PAHs Dataset.pickle', '3.2_CH_Cleaner ALL_High_PAHs Dataset.pickle', '4.0_CH_Cleaner 50_100_*.pickle' (pandas/numpy: smiles object array + sequences float64 [N x 128|180]; shapes read with pickletools, not unpickled), PAH_*_AFP/GAT/GCN/MFP/MPNN.py, EN_GNN_PAH_IR_Prediction.zip, READ_ME",
    confidence=0.55,
)

R["18347511"] = dict(
    modality="Steady-state UV-Vis-NIR absorption spectra of heptamethine/pentamethine cyanine dyes with C1' chain substituents, with quantum-chemical (TD-DFT/ensemble) calculations; one computed absorption spectrum on an energy axis",
    spectral_range_original_min=223.4, spectral_range_original_max=961.085, spectral_range_original_unit="nm",
    sampling_interval=0.7, sampling_interval_unit="nm (irregular grids, 600-760 pts per spectrum; computed spectrum 4,001 pts 1.55-5.55 eV)",
    num_samples=40,  # approx.: synthesised cyanine derivatives (VZ4_024_021_VSCHT_D_0175 ... 0323 compound codes)
    num_spectra=87,  # 67 .dat in the main folder (66 nm-axis spectra + 1 computed in eV) + 20 .dat in Absorption_Spectra (added version)
    num_spectral_values=64164,  # 51,627 + 12,537
    spectral_target_relationship="Absorption maxima and band shapes of cyanines vs C1' substituent (electron donating/withdrawing, steric) and solvent, compared with quantum-chemical excitation energies -> structure-photophysics rules for tuning absorption/emission, singlet-oxygen production and photostability",
    source_file="18347511.xml (Bedocchi, Polena, Okorocenkova, Slavicek & Klan 2025 J. Org. Chem. 90:17797, doi:10.1021/acs.joc.5c02283 'Engineering the Photophysics of Cyanines by Chain C1' Substituents'); VZ4_024_021_VSCHT_D.zip (*_NNNN_v1.dat 2-column spectra, Gaussian/ORCA .log/.out/.fchk/.molden, .xyz) and VZ4_024_021_VSCHT_D_added.zip (Absorption_Spectra/*.dat, Quantum_Chemical_Calculations)",
    confidence=0.6,
)

R["18373451"] = dict(
    modality="UV-Vis absorption spectroscopy of Zn-porphyrin-dipeptide conjugates (ZnTriMesZAF, ZnTPPZAF) in good-solvent / poor-solvent mixtures to follow self-assembly (EU project WP2, FORTH)",
    spectral_range_original_min=300, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=501, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=2,  # ZnTriMesZAF and ZnTPPZAF conjugates in several solvent mixtures (THF, THF-heptane, THF-ACN, DCM, DCM-MeOH)
    num_spectra=7,
    num_spectral_values=3507,  # 7 x 501
    spectral_target_relationship="Soret (~420 nm) and Q-band shifts/broadening on going from monomeric (THF/DCM) to aggregating solvent mixtures -> J/H-type self-assembly of porphyrin-dipeptide conjugates, related to enhanced photocatalytic H2 production",
    source_file="18373451.xml (ChemSusChem 2025 18:e202501251, doi:10.1002/cssc.202501251 'Modulation of Self-Assembly and Enhanced Photocatalytic H2 Production by Porphyrin-Dipeptide Conjugates'); 18022025_Characterisation_UV_WP2_FORTH.csv (semicolon CSV, two nm blocks with sample/solvent columns); description docx",
    confidence=0.8,
)

R["18373942"] = dict(
    modality="FTIR transmission spectroscopy of lutetium ferrite (LuFeO3) nanoparticles annealed at 800 and 1,000 C (hexagonal vs orthorhombic phase)",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=1801, sampling_interval=2, sampling_interval_unit="cm-1",
    num_samples=2,  # LFO-800, LFO-1000
    num_spectra=2,
    num_spectral_values=3602,
    spectral_target_relationship="Fe-O / Lu-O lattice vibration bands below 700 cm-1 and residual carbonate/hydroxyl bands vs annealing temperature -> hexagonal-to-orthorhombic phase transition of LuFeO3 nanoparticles, supporting XRD/Raman and Landau-theory analysis",
    source_file="18373942.pdf (Fesenko, Fesych, Zatovsky, Yaremkevych, Rallev, Bodnaruk, Eliseev & Morozovska 'Temperature-Induced Hexagonal-Orthorhombic Phase Transition in Lutetium Ferrite Nanoparticles'); 19012026_Experimental_FTIR_Characterisation_WP2_TSNUK.csv (wavenumber / T% pairs); description docx",
    confidence=0.8,
)

R["18435618"] = dict(
    modality="FTIR (linear) spectroelectrochemistry in the metal-carbonyl / metal-hydride stretching region of a hydridocarbonyl complex in DCM before and after one- and two-step oxidation, plus ultrafast 2D-IR spectroelectrochemistry data (binary .p2dat, not parsed)",
    spectral_range_original_min=1850.5, spectral_range_original_max=2200, spectral_range_original_unit="cm-1",
    num_spectral_channels=700, sampling_interval=0.5, sampling_interval_unit="cm-1",
    num_samples=3,  # hydride complex H1 in DCM, oxidised state ox1, ox2
    num_spectra=3,  # linear IR CSVs; three 2D-IR .p2dat datasets (~7.8 MB each) not counted
    num_spectral_values=2100,  # 3 x 700
    spectral_target_relationship="nu(CO) and nu(M-H) band shifts upon electrochemical oxidation, and 2D-IR cross peaks/anharmonic coupling between M-H and trans-CO -> distinguishing metal oxidation from protonation in proton-coupled electron transfer of the hydridocarbonyl complex",
    source_file="18435618.xml (J. Phys. Chem. Lett. 2026 17:3008, doi:10.1021/acs.jpclett.5c03977 'Proton-Coupled Electron Transfer from the Hydride Perspective: Resolving Metal Oxidation and Protonation in a Hydridocarbonyl Complex by 2D-IR Spectroelectrochemistry'); H1_dcm.csv, ox1.csv, ox2.csv (wavenumber, absorbance); three .p2dat 2D-IR files",
    confidence=0.7,
)

R["18471662"] = dict(
    modality="VIS-NIR-SWIR reflectance spectroscopy of refuse-derived fuel (RDF) particles with a benchtop-grade ASD FieldSpec 4 Hi-Res (350-2,500 nm) and a handheld Viavi MicroNIR (908-1,676 nm) - paired 'twin' scans",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (ASD 2,151 channels; MicroNIR 125 channels at ~6.2 nm)",
    num_samples=720,  # RDF particles in 6 classes (3D-print, foam, foil, PC, rubber, textile) with CV folds
    num_spectra=1438,  # 720 MicroNIR + 718 ASD FieldSpec spectra
    num_spectral_values=1634418,  # 720 x 125 + 718 x 2,151
    spectral_target_relationship="NIR reflectance features of polymers and textiles (C-H overtones 1,200/1,700 nm, combination bands 2,100-2,400 nm) -> classification of RDF particle material groups, cross-instrument comparison / calibration transfer between high-end and miniaturised spectrometers",
    source_file="18471662.xml (Fischer, Bikhit, Wrzesniowski, Niepala, Mielcarek, Illana-Mahiques & Ruszczak 2026 Data in Brief 67:112920, doi:10.1016/j.dib.2026.112920 'TwinSpectra - Spectroscopic scans of refuse-derived fuel particles'); measurements_2151.csv and measurements_125.csv (id, sample, group, fold + wavelength columns), baseline_model.ipynb, data_preview.ipynb",
    confidence=0.9,
)

R["18478460"] = dict(
    modality="Raman spectroscopy, infrared absorbance (FTIR) and cathodoluminescence (CL) spectroscopy of HPHT nanodiamond-modified ZnO photocatalyst composites (5-20% ND), ZnO reference and oxidised nanodiamonds; XPS and XRD also deposited",
    spectral_range_original_min=52.5, spectral_range_original_max=4000.19, spectral_range_original_unit="cm-1",
    sampling_interval=0.48, sampling_interval_unit="cm-1 (FTIR 7,468 pts 400-4,000; Raman ~3,530-3,580 pts 52-3,500 cm-1 shift); CL 63-350 pts on 1.72-3.44 eV energy axis (360-719 nm)",
    num_samples=6,  # oxidised HPHT ND, ZnO reference, ND-ZnO 5, 10, 15, 20
    num_spectra=16,  # Raman 6 (Fig 3a, 3c) + FTIR 6 (Fig 3b, 3d) + CL 4 (Fig 8a-d); XPS (Fig 4-6), XRD (Fig 7) not counted
    num_spectral_values=66621,  # approx. for Fig 3c (split column blocks)
    spectral_target_relationship="ZnO E2(high) Raman mode (437 cm-1) and diamond line (1,332 cm-1), IR surface groups of oxidised ND (C=O, O-H) and ZnO near-band-edge vs defect (green) CL emission vs ND loading -> interfacial coupling and defect states explaining enhanced methylene-blue photocatalytic degradation",
    source_file="18478460.xml (Materials 2026 19:609, doi:10.3390/ma19030609 'High-Pressure High-Temperature Nanodiamond-Modified ZnO Nanocomposites as Promising Photocatalysts: Synthesis and Characterization'); data.zip -> Figure3a-d.txt (Raman, IR absorbance), Figure4-6 (XPS Zn 2p/O 1s/C 1s fits), Figure7.txt (XRD), Figure8a-d.txt (CL), Figure9 (kinetics), SEM png",
    confidence=0.8,
)

R["18851416"] = dict(
    modality="FTIR (ATR) characterisation spectra (JCAMP-DX) of synthetic products of alcohol-directed carboamination of conjugated enynes; record also holds NMR and HRMS JCAMP files (not counted)",
    spectral_range_original_min=799.8317, spectral_range_original_max=4000.1226, spectral_range_original_unit="cm-1",
    num_spectral_channels=6639, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=65,  # approx.: one IR spectrum per synthesised compound
    num_spectra=65,  # 64 spectra with 6,639 points + 1 with 6,847 points (INFRARED SPECTRUM data type)
    num_spectral_values=431743,
    spectral_target_relationship="Functional-group IR bands (O-H ~3,400, C=O, C=C, C-N, alkyne/allene) of carboamination products -> routine structural confirmation of new compounds alongside NMR and HRMS",
    source_file="18851416.xml (Angew. Chem. Int. Ed. 2026 65:e6963888, doi:10.1002/anie.6963888 'Alcohol-Directed Carboamination of Conjugated Enynes'); 69 per-compound zips (extracted) with spectra/ir/*.jdx (and *.dx), spectra/nmr, spectra/mass (QTOF JCAMP), .mol structures, .json/.md metadata (Chemotion-style export)",
    confidence=0.75,
)

R["18852230"] = dict(
    modality="FTIR spectroscopy of N,S-doped covalent triazine framework (CTF)-derived carbons and their carbon nano-onion (CNO) hybrids; Raman D/G fitting only as Origin projects/figures",
    spectral_range_original_min=400.2, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=7468, sampling_interval=0.48, sampling_interval_unit="cm-1",
    num_samples=6,  # NS, NS-CNO, SS, SS-CNO, NSN, NSN-CNO
    num_spectra=6,  # IR.CSV, one column pair per sample; many intensity values were turned into Excel dates (e.g. '16.wrz' = 16 Sep) - partly unusable
    num_spectral_values=44808,  # nominal 6 x 7,468
    spectral_target_relationship="IR bands of triazine/C=N (1,350-1,600 cm-1), C-S and residual functional groups in heteroatom-doped carbons vs CNO hybridisation -> doping and graphitisation degree linked to porosity and supercapacitor capacitance (CV in 1 M H2SO4)",
    source_file="18852230.xml (ACS Omega 2026 11:19094, doi:10.1021/acsomega.5c11683 'Decoding the Role of Porosity and N,S-Doping in Covalent Triazine Framework-Derived Carbons and Their Carbon Nano-Onion Hybrids for Superior Supercapacitors'); Raw Data.7z -> FTIR/IR.CSV (semicolon; Polish-locale Excel date corruption), 'Raman spectroscopy' (29 files: .opju fits, png, pdf - no raw text), Electrochemistry CV xlsx, XRD PD_Data.xlsx, figure PNG/PDF",
    confidence=0.4,
)

R["18893836"] = dict(
    modality="Computed protein charge-transfer (ProCharTS) UV-vis absorption spectra: TDDFT (ZINDO/TD) molar extinction spectra of charged amino-acid clusters from MD snapshots of native and acetylated proteins; the measured Cary-100 UV-vis and CD spectra are not deposited as data",
    spectral_range_original_min=100, spectral_range_original_max=793.65, spectral_range_original_unit="nm",
    num_spectral_channels=875, sampling_interval_unit="nm (non-uniform grid, 875 pts 100-794 nm)",
    num_samples=5,  # protein systems (e.g. a3c and four others; native vs acetylated, 10 MD systems in total)
    num_spectra=243,  # broadened epsilon(lambda) spectra per MD frame (epsilon_data/concat_output_*.txt); thousands of per-cluster stick-transition .dat files not counted
    num_spectral_values=212625,  # 243 x 875
    spectral_target_relationship="Charge-transfer absorption tail (250-800 nm) of charged Lys/Glu/Asp/Arg clusters, reduced upon lysine acetylation -> label-free optical detection of protein acetylation via UV-vis CT spectra (ProCharTS), compared with measured spectra",
    source_file="18893836.xml (Chem. Sci. 2026 17:10529, doi:10.1039/d5sc09293k 'Label-free optical detection of protein acetylation using UV-vis charge transfer spectra'); procharts_repo.zip -> figure2E/2F_2G/3E_3F (GROMACS .gro/.xtc/.xvg MD analysis), figure4E_4F_4G (Gaussian .com/.out, cluster spectra scripts), figure6 (frames/*/*.dat transitions, epsilon_data/concat_output_*.txt broadened spectra, csv feature tables), README .md per figure",
    confidence=0.6,
)

R["18895495"] = dict(
    modality="Surface-enhanced Raman spectroscopy (SERS, Ag/Au nanoparticle-enhanced) of dyed and undyed human hair from donors of different race/ethnicity, sex and age, for forensic colorant identification",
    spectral_range_original_min=308.5360413, spectral_range_original_max=1952.093506, spectral_range_original_unit="cm-1",
    num_spectral_channels=1340, sampling_interval=1.23, sampling_interval_unit="cm-1 Raman shift",
    num_samples=100,  # approx.: hair samples (subjects x colorant: permanent, semi-permanent, undyed) - labelled 'Subject_N_<dye>-<date> <rep>'
    num_spectra=2000,
    num_spectral_values=2680000,  # 2,000 x 1,340
    spectral_target_relationship="SERS bands of artificial hair colorants vs keratin/melanin background -> PLS-DA/ML identification of dye brand/type and test whether race/ethnicity, sex or age of the donor biases SERS- and IR-based colorant detection",
    source_file="18895495.xml (ACS Omega 2023 8:20675, doi:10.1021/acsomega.3c01241 'Role of Race/Ethnicity, Sex, and Age in Surface-Enhanced Raman Spectroscopy- and Infrared Spectroscopy-Based Analysis of Artificial Colorants on Hair'); single CSV: Label column + 1,340 Raman-shift columns, one row per spectrum",
    confidence=0.75,
)

R["18895733"] = dict(
    modality="ATR-FTIR spectroscopy (Thermo OMNIC .SPA exports) of human fingernail clippings from control donors and fentanyl-exposed/spiked samples for machine-learning detection",
    spectral_range_original_min=600.2353346, spectral_range_original_max=3900.806985, spectral_range_original_unit="cm-1",
    num_spectral_channels=5397, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=400,  # approx.: nail samples (donor x clipping) labelled UK1 1.1 ... with class Control / fentanyl
    num_spectra=1185,
    num_spectral_values=6395445,  # 1,185 x 5,397
    spectral_target_relationship="Keratin amide/lipid bands plus fentanyl-specific bands (aromatic, amide C=O ~1,650, C-N) in ATR spectra of nails -> classification (PLS-DA, SVM, random forest) of fentanyl presence in nails",
    source_file="18895733.xml (Sensors 2025 25:227, doi:10.3390/s25010227 'From Spectra to Signatures: Detecting Fentanyl in Human Nails with ATR-FTIR and Machine Learning'); single CSV: file name (.SPA), sample id, class + 5,397 wavenumber columns",
    confidence=0.8,
)

R["18923448"] = dict(
    modality="ATR-FTIR spectroscopy (Bruker OPUS .dpt exports) of poly(ethylene furanoate) (PEF), poly(butylene furanoate) (PBF), epoxidized natural rubber (ENR) and their 90/10, 75/25, 50/50 blends",
    spectral_range_original_min=399.20627, spectral_range_original_max=3997.84833, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=9,  # ENR, PBF, PEF and PBF/ENR, PEF/ENR blends at 90/10, 75/25, 50/50
    num_spectra=9,
    num_spectral_values=16795,  # 8 x 1,866 + 1,867
    spectral_target_relationship="Furan ring (1,580, 1,020, 960 cm-1), ester C=O (1,715-1,720 cm-1) and ENR epoxy bands (836/870 cm-1) vs blend ratio -> miscibility / interactions in biobased PEF- and PBF-ENR blends, with DSC, TGA and tensile results",
    source_file="18923448.xml (Materials 2025 18:4040, doi:10.3390/ma18174040 'Ecofriendly PEF- and PBF-Based Blends with Epoxidized Natural Rubber: Unraveling the Structure-Property Relationship'); 9 .dpt (x and y separated by '.', decimal points - e.g. '3996.15494.-0.00853'), DSC ExpDat_*.txt (heating/cooling), TGA_*.txt, tensile-test CSVs",
    confidence=0.8,
)

R["18946029"] = dict(
    modality="FTIR spectroscopy (Jasco FT/IR-4600, 4 cm-1, 32 scans) of three biobased low-density polyethylenes (SBC-818, SEB-853, SPB-681) thermally aged at 90, 100 and 110 C for 1-20 days",
    spectral_range_original_min=399.1927, spectral_range_original_max=4000.6047, spectral_range_original_unit="cm-1",
    num_spectral_channels=3736, sampling_interval=0.964, sampling_interval_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=72,  # 3 LDPE grades x (unaged + 3 temperatures x 7 ageing times), 2-3 replicate spectra each
    num_spectra=202,
    num_spectral_values=754672,  # 202 x 3,736
    spectral_target_relationship="Growth of carbonyl (1,710-1,740 cm-1), hydroxyl and vinyl bands relative to CH2 bands vs ageing temperature/time -> carbonyl index and oxidation kinetics of biobased LDPE, with oxidation induction (DSC-OOT), rheology and GPC",
    source_file="18946029.xml (Anisko-Michalak, Sokolohorskyj, Szafraniak-Wiza, Kosmela, Piasecki & Barczewski 2025 ACS Omega 10:25432, doi:10.1021/acsomega.5c00636); FTIR_spectra/FTIR_spectra_<grade>_<T-days>_<rep>.txt (Jasco JCAMP-like text: header + XYDATA, decimal commas); FTIR_DECONVOLUTION, DSC, DSC_OOT, GPC, RHEOLOGY, SEM, SEM_EDS, XRD folders",
    confidence=0.85,
)

R["18988888"] = dict(
    modality="ATR-FTIR spectroscopy of third-instar Chrysomya rufifacies blow-fly larvae with a benchtop FTIR and a handheld (portable) FTIR, interpolated to a common 898-3,000 cm-1 axis, for machine-learning sex determination",
    spectral_range_original_min=898.2884188, spectral_range_original_max=3000.506959, spectral_range_original_unit="cm-1",
    num_spectral_channels=1129, sampling_interval=1.86, sampling_interval_unit="cm-1 (interpolated grid)",
    num_samples=65,  # approx.: individual larvae (L1-L35 benchtop event 1/2, handheld event 1), ~5 replicate spectra each
    num_spectra=325,  # benchtop event 1: 100, benchtop event 2: 115, handheld event 1: 110
    num_spectral_values=366925,  # 325 x 1,129
    spectral_target_relationship="Cuticular lipid/hydrocarbon (CH2 2,850/2,920 cm-1), protein amide and chitin bands -> PLS-DA / ML prediction of larval sex (later confirmed in adults), comparing benchtop vs portable instruments for forensic entomology",
    source_file="18988888.xml (Holman, Pickett, West, Tarone & Kurouski 2025 J. Forensic Sci. 70:1468, doi:10.1111/1556-4029.70054 'Portable Fourier-transform infrared spectroscopy and machine learning for sex determination in third instar Chrysomya rufifacies larvae'); BenchtopSpectra_Raw_Event01/02.csv, HandheldSpectra_Raw_Event01.csv (MATLAB TEXTREADR export: 8 header rows, axis row, one row per spectrum with ID and larva label)",
    confidence=0.85,
)

R["18999221"] = dict(
    modality="UV-Vis absorbance spectra (BioTek Epoch 2 plate reader) of alizarin, alizarin-BSA boronate-ester conjugate and controls, plus an alizarin serial-dilution spectral calibration, supporting visually trackable dynamic covalent enzyme immobilisation",
    spectral_range_original_min=230, spectral_range_original_max=700, spectral_range_original_unit="nm",
    sampling_interval=10, sampling_interval_unit="nm (48 pts 230-700 nm; calibration 250-700 nm)",
    num_samples=5,  # buffer control, alizarin, alizarin+BSA, BSA alone; alizarin dilution series
    num_spectra=15,  # 4 spectra + 11 dilution spectra (values '>4' = detector overflow)
    num_spectral_values=698,  # approx.
    spectral_target_relationship="Alizarin boronate-ester absorption band (~520 nm) appearing on conjugation and its Beer-Lambert calibration -> visual tracking/quantification of boronic-acid-mediated reversible immobilisation and release of enzymes (MsAcT, CbFDH, SpLCD, ...)",
    source_file="18999221.xml (Chem. Sci. 2026 17:8513, doi:10.1039/d5sc08585c 'Going full circle: dynamic covalent enzyme immobilisation via visually trackable boronate esters'); Alizarin_UVVis_spectrum_230to700nm.csv, Alizarin_calibration_spectrum_250to700nm.csv; Bradford, activity and kinetics CSVs, xlsx; AlphaFold PDB/JSON/FASTA; analysis .py and README.md",
    confidence=0.7,
)

R["19096639"] = dict(
    modality="Diffuse reflectance infrared Fourier transform spectroscopy (DRIFTS, Bruker OPUS) of group-4 metallocenes (Cp2ZrMe+, Cp*2ZrMe+, Cp*ZrMe2+, Cp2HfMe+, Cp2TiMe+, 13C-labelled) chemisorbed on sulfated zirconia (SZO) and SiO2-700; solid-state and solution NMR dominate the record",
    spectral_range_original_min=398.65, spectral_range_original_max=4496.08, spectral_range_original_unit="cm-1",
    sampling_interval=2.06, sampling_interval_unit="cm-1 (1,995 pts 399-4,496; 1,752 pts 399-3,997; 1,557 pts 799-3,997)",
    num_samples=9,  # SZO, SiO2-700 supports and 7 supported metallocene precatalysts (incl. Cp2ZrMe-SZO time point .24 and 13C-labelled)
    num_spectra=9,  # one final absorbance block per OPUS file (single-channel sample/reference blocks not counted); point counts read from OPUS headers
    num_spectral_values=16155,
    spectral_target_relationship="Consumption of surface O-H (3,600-3,750 cm-1) and appearance of nu(C-H) 2,700-3,100 cm-1 on SZO/SiO2 -> chemisorption of metallocenes as electrostatically bound cations (SZO) vs covalently bound species (SiO2), the active precatalysts for benzene C-H borylation",
    source_file="19096639.xml (J. Am. Chem. Soc. 2026 148:16944, doi:10.1021/jacs.6c01025 'Group 4 Metallocenes Supported on Sulfated Zirconium Oxide Catalyze Benzene C-H Borylation'); DRIFTS.zip -> 9 Bruker OPUS binaries (DRIFTs_<sample>.0/.1/.24); solid-state NMR and solution NMR (11B, 1H, 13C) Bruker folders; catalysis data",
    confidence=0.7,
)

R["20640038"] = dict(
    modality="FTIR spectroscopy of a hydrophobic eutectic solvent (TOPO : decanoic acid, x_TOPO = 0.5) after extraction of Eu(III) from aqueous nitrate solutions of increasing concentration; EXAFS, ITC and NMR also deposited",
    spectral_range_original_min=349.0525, spectral_range_original_max=4000.6045, spectral_range_original_unit="cm-1",
    num_spectral_channels=3788, sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=7,  # HES phases after contact with 0, 1, 5, 10, 20, 30, 50 g/L Eu(NO3)3 solutions
    num_spectra=7,  # non-normalised block of sheet FTIR (a second, normalised block of the same 7 spectra is not counted)
    num_spectral_values=26516,  # 7 x 3,788
    spectral_target_relationship="Shift/attenuation of TOPO P=O stretch (~1,150 cm-1) and decanoic acid C=O stretch (~1,710 cm-1) and nitrate bands with Eu loading -> Eu coordination by TOPO and nitrate co-extraction, connecting the extraction thermodynamics (ITC enthalpy/entropy) to the molecular mechanism",
    source_file="20640038.xml (Vaz, Saldanha Pinheiro, Olea, Cirillo, Mannucci, Busato, D'Angelo, Santos, Bastos, Santos, Coutinho & Schaeffer 2026 ChemSusChem 19:e70794, doi:10.1002/cssc.70794 'Identifying the Thermodynamic Driving Force of Metal Extraction by Hydrophobic Eutectic Solvents'); Data_file.zip -> Results_ITCsummary_Partitions_FTIR.xlsx (sheet FTIR), ITC raw data CSV, EXAFS (Athena/Larch/xlsx), NMR Bruker folders",
    confidence=0.8,
)

R["19183671"] = dict(
    modality="Nanoelectromechanical (NEMS) photothermal FTIR spectroscopy of submicrometer atmospheric aerosol particles collected on nanomechanical resonators, with reference FTIR spectra of standards (ammonium sulfate/nitrate, organics) and field samples",
    spectral_range_original_min=399.722, spectral_range_original_max=3999.21, spectral_range_original_unit="cm-1",
    sampling_interval=0.48, sampling_interval_unit="cm-1 (6,501-7,466 pts per spectrum; field/lab spectra 865-3,999 or 1,500-3,999 cm-1)",
    num_samples=20,  # approx.: laboratory aerosol standards and ambient aerosol samples
    num_spectra=46,  # fig2 8 + fig4 23 + fig5 2 + fig6 panel g 3 + fig7 panel d 10; particle size distributions (fig6 a/d, fig7 b) and theory curves (fig1) not counted
    num_spectral_values=302819,
    spectral_target_relationship="Absorption bands of sulfate (~1,100 cm-1), nitrate (~1,350/830 cm-1), ammonium (~1,420/3,200 cm-1) and organic C-H/C=O in NEMS-FTIR spectra of picogram aerosol masses -> quantitative chemical composition of submicrometer aerosol (calibration vs mass, comparison with AMS)",
    source_file="19183671.xml (Sci. Adv. 2026 12:eaeb2254, doi:10.1126/sciadv.aeb2254 'Quantifying submicrometer atmospheric aerosol chemical composition using nanoelectromechanical Fourier transform infrared spectroscopy'); fig1_data.xlsx ... fig7_data.xlsx (one sheet per panel, wavenumber + absorbance columns; size distributions in fig6/fig7)",
    confidence=0.75,
)

R["19257685"] = dict(
    modality="UV-Vis absorption spectroscopy of meso-tetraethynylporphyrin-derived glycoconjugates (red-shifted glycoporphyrins)",
    spectral_range_original_min=250, spectral_range_original_max=900, spectral_range_original_unit="nm",
    num_spectral_channels=6501, sampling_interval=0.1, sampling_interval_unit="nm",
    num_samples=7,  # compounds 4c, 4d, 4e, 5a, 6a and two further derivatives (folders under 'Widma Artykul')
    num_spectra=7,  # one spectrum per compound, stored twice (.csv and .txt with WL/Abs/T%)
    num_spectral_values=45507,  # 7 x 6,501
    spectral_target_relationship="Soret and Q-band positions of tetraethynyl-linked glycoporphyrins vs sugar and linker -> red-shifted absorption (> 650 nm) for photodynamic therapy photosensitisers",
    source_file="19257685.xml (Mitrzak & Malinowski 2026 ACS Org. Inorg. Au 6:438, doi:10.1021/acsorginorgau.6c00033 'Pursuing the Red-Shift in Glycoporphyrins - A New Synthetic Approach toward Glycoconjugates from the meso-Tetraethynylporphyrin Scaffold'); spectra.7z -> 'Widma Artykul'/<compound>/<compound>.csv|.txt; NMR .mnova, HRMS pdf, singlet-oxygen .sca/.0 files",
    confidence=0.8,
)

R["19637299"] = dict(
    modality="Simulated gas- and liquid-phase infrared spectra of pure compounds, binary and ternary mixtures (MD/ML-potential dipole autocorrelation, 300 K) for automatic mixture identification, plus experimental ATR-FTIR spectra of battery-electrolyte solvents and test mixtures",
    spectral_range_original_min=0.0, spectral_range_original_max=4996.0, spectral_range_original_unit="cm-1",
    wavelength_min_nm=2001.601,  # axis starts at 0 cm-1, so only the short-wavelength end is defined
    sampling_interval=4, sampling_interval_unit="cm-1 (simulated 1,250 pts 0-4,996; experimental ATR 400-4,000 cm-1, ~7,200 pts)",
    num_samples=9000,  # approx.: unique molecules/mixtures (8,800 gas-phase molecules, drugs subset, binary and ternary mixtures; 29 experimental liquids/mixtures)
    num_spectra=79935,  # 79,906 simulated (gas 8,800 + 117 drugs; liquid 8,472 + 115 drugs; mixtures 39,576 + 13,584 drugs; ternary 9,242) + 29 experimental ATR
    num_spectral_values=100092005,  # 79,906 x 1,250 + 209,505
    spectral_target_relationship="Simulated condensed-phase IR spectra (with solvent shifts/broadening) of single compounds and mixtures -> training of models that decompose experimental liquid-phase IR spectra into constituent compounds and fractions, validated on measured ATR spectra of carbonate/ether electrolyte solvents and prepared mixtures",
    source_file="19637299.xml (Melle, Nguyen, Lopez & Schwalbe-Koda 2026 Chem. Sci. 17:13465, doi:10.1039/d6sc01583b 'Automatic identification of compounds in molecular mixtures from liquid-phase infrared spectra'); 250716-simulated-ir.tar.gz -> 02_ir_gas*, 03_ir_liq*, 04_ir_mix*, 06_ir_mix_ternary_v2.json (list of jobs: data.smiles, phase, n_mols, wavenumber[1,250], intensity[1,250], MD settings); experimental-ir.zip -> 2506xx/2508xx_atr_baseline_4000_correction/*.csv (Wavenumbers [1/cm], Absorbance)",
    confidence=0.75,
)

R["19666143"] = dict(
    modality="High-throughput microplate UV-Vis absorbance spectroscopy (384-well plates, robot-dispensed) of mixed-ligand (TEG/MUA) gold nanocrystals with simple salts at varying ionic strength, following the LSPR band for agglomeration",
    spectral_range_original_min=450, spectral_range_original_max=750, spectral_range_original_unit="nm",
    num_spectral_channels=51, sampling_interval=6, sampling_interval_unit="nm",
    num_samples=13056,  # wells: salt x concentration/ionic strength x TEG:MUA ligand ratio
    num_spectra=13056,  # one raw spectrum per well (ordered_data; same as 35 raw plate CSVs); background-subtracted (13,495), interpolated and fitted copies not counted
    num_spectral_values=665856,  # 13,056 x 51
    spectral_target_relationship="LSPR peak position/intensity (~520 nm, red-shift and broadening on aggregation) vs salt type (cation/anion radius, polarisability, charge), ionic strength and ligand ratio -> agglomeration efficacies of salts on charged Au nanocrystals and ML model of colloidal stability",
    source_file="19666143.xml (ACS Mater. Au 2026 6:860, doi:10.1021/acsmaterialsau.6c00051 'Agglomeration Efficacies of Simple Salts on Charged Gold Nanocrystals with Mixed Ligand Shells: A High-Throughput Study'); UV-Vis_data_analysis/manuscript measurements: raw_data (35 plate-reader CSV, 384 wells x 51 wavelengths), ordered_data (13,056 per-well txt), UVvis_data_ionicstrength_all_bkg (bkg-subtracted), UVvis_interpolation/fits, ML_results, Python scripts",
    confidence=0.8,
)

R["20530941"] = dict(
    modality="FTIR spectroscopy of carboxymethyl-dextran-coated iron oxide nanoparticles (ION@CMD) before and after EDC/NHS activation and T4-phage conjugation, for phage-functionalised magnetic separation of E. coli",
    spectral_range_original_min=450, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3551, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=4,  # CMD-ION, EDC/NHS-activated CMD-ION, phage-conjugated (two preparations)
    num_spectra=7,  # 7 CSV spectra (two measurement series); DLS size distributions (10 txt) and the xlsx plate data not counted
    num_spectral_values=24857,  # 7 x 3,551
    spectral_target_relationship="Carboxylate/ester (1,600-1,730 cm-1), amide (1,650/1,540 cm-1) and Fe-O (~580 cm-1) bands before/after EDC/NHS activation and phage coupling -> covalent attachment of T4 phages to magnetic nanoparticles used for rapid selective E. coli capture",
    source_file="20530941.xml (ACS Omega 2026 11:37605, doi:10.1021/acsomega.6c02406 'Phage-Functionalized Magnetic Separation for Rapid and Selective Detection of Escherichia coli'); CMD.csv, CMD_Ph_W2.csv, CMD_Phage_W2.csv, 20251001/20251002_CMD_*_w.csv (wavenumber, absorbance/%T); DLS *-Number-cum-*.txt; 20250201.xlsx",
    confidence=0.75,
)

R["20585222"] = dict(
    modality="SERS (methylene blue and malathion on ZnO nanotube/Au hybrids), Raman, UV-Vis absorption/reflectance and photoluminescence spectroscopy of ZnO nanorods/nanotubes with and without Au nanoparticles; XRD and XPS also deposited",
    spectral_range_original_min=50.4719, spectral_range_original_max=2001.14, spectral_range_original_unit="cm-1",
    sampling_interval=2.8, sampling_interval_unit="cm-1 Raman shift (SERS 650-1,144 pts; Raman 682 pts); UV-Vis 801 pts 300-1,100 nm (1 nm); PL 1,422 pts 348-1,100 nm",
    num_samples=6,  # ZnO NRs, ZnO NTs (16, 18, 20), ZnO NRs/Au, ZnO NTs18/Au (+ glass reference, analyte concentrations)
    num_spectra=110,  # UV-Vis 6 + Raman 6 + PL 6 + SERS MB (Figs 10, 11, 13) ~62 + malathion SERS 10 + 20 blank SERS spectra; XRD 6 and XPS 4 not counted
    num_spectral_values=90332,
    spectral_target_relationship="SERS enhancement of MB/malathion bands (e.g. MB 1,620 cm-1; malathion P=S ~ 650 cm-1) vs ZnO morphology, defects (PL visible emission, UV-Vis band edge) and Au decoration -> defect-assisted charge transfer + plasmonic enhancement; LOD down to 1e-11 M and malathion quantification",
    source_file="20585222.xml (Nguyen, Nguyen, Pham, Cu, Le & Le 2026 RSC Adv. 16:32461, doi:10.1039/d6ra01952h 'Defect-assisted charge transfer and plasmonic enhancement in ZnO nanotube/Au hybrids for ultrasensitive malathion detection'); Raw_data zip -> 02_UVVis_Fig5, 04_Raman_Fig7, 05_PL_Fig8, 07_SERS_MB_Figs10-11 and 13, 08_Malathion_SERS_Fig14, 09_Blank spectra (2-column CSV), 01_FESEM_EDX, 03_XRD, 06_XPS",
    confidence=0.85,
)

R["20675391"] = dict(
    modality="Confocal Raman imaging (Renishaw WiRE .wdf hyperspectral maps) of never-dried, oven-dried and solvent-exchanged wood cell walls before/after acetylation (native and delignified), plus ATR-FTIR (PerkinElmer Spectrum Two, Specac Quest diamond ATR) of wood and delignified wood",
    spectral_range_original_min=300.56055, spectral_range_original_max=4000.0, spectral_range_original_unit="cm-1",
    num_spectral_channels=1015, sampling_interval=3.3, sampling_interval_unit="cm-1 Raman shift (1,015 channels per map pixel; mean spectra 300-3,598); FTIR 3,551/3,601 pts at 1 cm-1",
    num_samples=8,  # never-dried / delignified wood: non-acetylated, ND-, OD-, SE-acetylated
    num_spectra=283458,  # 8 unique Raman maps (4 x ~22,450 px delignified 150x150, 4 x 48,400 px wood 220x220; cosmic-ray-removed duplicates not counted) + 8 ATR-FTIR spectra; mean/PCA spectra in xlsx not counted
    num_images=8, num_pixels=283450,
    num_spectral_values=287730358,  # 283,450 x 1,015 + 28,608 FTIR values
    spectral_target_relationship="Raman acetyl C=O (~1,740 cm-1) and CH3 bands vs lignin aromatic (1,600 cm-1) and cellulose bands mapped over cell wall layers, and FTIR ester C=O (1,740), C-O (1,240) bands -> spatial distribution and degree of acetylation achieved by diffusion-driven solvent exchange of never-dried wood compared with oven-dried routes",
    source_file="20675391.xml (Biomacromolecules 2026 27:4802, doi:10.1021/acs.biomac.6c00768 'Acetylation of Never-Dried Wood via Diffusion-Driven Solvent Exchange'); Sultan_et_al_Biomacromolecules_Zenodo_Data_1_1.zip -> 15 *.wdf Raman maps (raw and _CR_removed; OD-acetylated raw map missing), renishawWire.m, Mean Raman spectra / Wood ATR-FTIR / Delignified wood ATR-FTIR / PCA / histogram xlsx + .opju, saponification and solvent-exchange workbooks",
    confidence=0.75,
)

R["20769482"] = dict(
    modality="FTIR spectroscopy (Bruker IR Biotyper, transmission of dried colony suspensions) of Malassezia pachydermatis isolates for strain typing; polysaccharide fingerprint region 1,300-800 cm-1 exported",
    spectral_range_original_min=800, spectral_range_original_max=1300, spectral_range_original_unit="cm-1",
    num_spectral_channels=501, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=100,  # approx.: M. pachydermatis isolates (plus reference species) with technical/biological replicates
    num_spectra=1490,  # rows of the 7 figure spectra CSVs (27 + 510 + 337 + 279 + 130 + 149 + 58); the matching zips hold the same spectra as ~3,000 IR Biotyper XML exports
    num_spectral_values=746490,  # 1,490 x 501
    spectral_target_relationship="Second-derivative/vector-normalised carbohydrate fingerprint (1,300-800 cm-1) -> hierarchical clustering / LDA-ANN strain typing of M. pachydermatis isolates (host, disease association, reproducibility across incubation conditions), compared with MLST",
    source_file="20769482.xml (J. Clin. Microbiol. 2026 64:e01422-25, doi:10.1128/jcm.01422-25 'Fourier transform infrared spectroscopy enables rapid strain typing in M. pachydermatis'); FIG2/3/4A/4B/5A/5B/5C_*_spectra.csv (metadata columns name, isolate, species, qc, acquisition date, incubation protocol + 501 wavenumber columns), FIG*.zip (IR Biotyper baseTransport XML exports), FIG1_S2.zip, Newick trees (.nwk)",
    confidence=0.8,
)

R["21096098"] = dict(
    modality="FTIR spectroscopy (Thermo Scientific iN10, OMNIC .SPA) of rigid biobased vinylogous urethane vitrimers from D-isosorbide- and furfural-derived monomers (pristine and reprocessed)",
    spectral_range_original_min=350.02, spectral_range_original_max=4000.12, spectral_range_original_unit="cm-1",
    num_spectral_channels=7572, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=8,  # vitrimer formulations P1, P3, X1, X3, each in 'J' and 'T' variants
    num_spectra=8,  # .SPA binaries; point counts and range read from SPA headers
    num_spectral_values=60576,  # 8 x 7,572
    spectral_target_relationship="Vinylogous urethane C=C-N/C=O bands (~1,600-1,650 cm-1), disappearance of acetoacetate C=O (1,710-1,740 cm-1) and amine N-H -> network formation and chemical stability after reprocessing, linked to stress relaxation (exchange kinetics), DMA and TGA",
    source_file="21096098.xml (ACS Polym. Au 2026 6:1147, doi:10.1021/acspolymersau.6c00063 'Rigid Biobased Vinylogous Urethane Vitrimers from D-isosorbide/Furfural-Derived Monomers'); 001_Data_Raw/FTIR_Raw_original-<sample>.SPA (8), DMA/TGA/DSC/relaxation-test CSVs, NMR folders",
    confidence=0.75,
)

R["21212670"] = dict(
    modality="FTIR spectroscopy of puerarin raw material and melt-sonocrystallised puerarin (MSC-PUE)",
    spectral_range_original_min=400.157, spectral_range_original_max=4000.12, spectral_range_original_unit="cm-1",
    num_spectral_channels=7468, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=2,  # PUE, MSC-PUE
    num_spectra=2,
    num_spectral_values=14936,
    spectral_target_relationship="O-H/C=O/aromatic band shifts between raw and sonocrystallised puerarin -> unchanged chemical identity but altered hydrogen bonding/crystal form, explaining enhanced solubility and dissolution (with DSC, PXRD, TGA)",
    source_file="21212670.xml (PLOS One 2026 21:e0355646, doi:10.1371/journal.pone.0355646 'Enhancing the solubility of puerarin via melt sonocrystallization'); 'raw data.xlsx' sheets solubility, dissolution, DSC, PXRD, FT-IR (wavenumber/%T pairs), TGA",
    confidence=0.85,
)

R["21256763"] = dict(
    modality="ATR-FTIR spectroscopy (normalised) of skin (stratum corneum) treated with imiquimod nanoformulations containing HPMA copolymer excipients (P1-P3) at different polymer concentrations",
    spectral_range_original_min=399.2094, spectral_range_original_max=4000.774, spectral_range_original_unit="cm-1",
    num_spectral_channels=3737, sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=10,  # approx.: blank skin, HPMA, polymers P1-P3 and concentrations 0.02-0.25%
    num_spectra=20,  # FTIR fig.5 9 + FTIR fig.6 11 (normalised); colour-intensity profiles (fig 3) not counted
    num_spectral_values=74732,
    spectral_target_relationship="Lipid CH2 stretching (2,850/2,920 cm-1) and amide bands of stratum corneum after HPMA-polymer formulations -> lipid disordering / barrier interaction explaining enhanced dermal imiquimod delivery, with TEWL and ex vivo permeation",
    source_file="21256763.xml (Int. J. Pharm. X 2026 11:100486, doi:10.1016/j.ijpx.2026.100486 'HPMA polymers as functional excipients in dermal nanoformulations of imiquimod'); 'GACR_HPMA_260107_data summary.xlsx' sheets 'FTIR fig.5', 'FTIR fig.6' (wavenumber + normalised absorbance columns), colour profiles, TEWL, permeation, NP characterisation; ReadMeFile_HPMA.docx",
    confidence=0.75,
)

R["21259994"] = dict(
    modality="ATR-FTIR spectroscopy (Bruker Tensor 27, diamond ATR) of solvent-fractionated spruce kraft lignin (Indulin AT) fractions; record dominated by FT-ICR mass spectrometry, tandem MS and Py-GC/MS data",
    spectral_range_original_min=399.25274, spectral_range_original_max=6497.98295, spectral_range_original_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1 (~3,160 pts per spectrum)",
    num_samples=13,  # Indulin AT and solvent fractions (water/acetone ratios WA1000 ... WA4060, I/II)
    num_spectra=13,
    num_spectral_values=41119,
    spectral_target_relationship="Lignin aromatic (1,595/1,510 cm-1), guaiacyl (1,270 cm-1), carbonyl (1,710 cm-1) and hydroxyl band intensities per fraction, correlated with FT-ICR MS molecular-formula statistics and quantitative 13C NMR -> benchmarking ultrahigh-resolution MS against conventional lignin characterisation",
    source_file="21259994.xml (Biomacromolecules 2026 27:5766, doi:10.1021/acs.biomac.6c01199 'Benchmarking Fourier Transform Ion Cyclotron Resonance Mass Spectrometry against Conventional Methods for the Characterization of Solvent-Fractionated Kraft Lignin'); FTIR/*_FTIR.dpt (13), FT-ICR-MS (ESI/GALDI formula lists csv/xlsx), Tandem MS, Py-GCMS, correlation workbooks, MATLAB .mat",
    confidence=0.8,
)

R["21419320"] = dict(
    modality="FTIR absorption and vibrational circular dichroism (VCD) spectra of R/S-BINOL and solvent blanks on liquid-phase-exfoliated 2D nanomaterials (2H-NbS2, Ti3C2 MXene, TiS2) and Au/Cr/CaF2 reference substrates",
    spectral_range_original_min=0.0, spectral_range_original_max=7897.92, spectral_range_original_unit="cm-1",
    wavelength_min_nm=1266.155,  # axis starts at 0 cm-1, so only the short-wavelength end is defined
    num_spectral_channels=4096, sampling_interval=1.93, sampling_interval_unit="cm-1 (full interferogram-transform axis 0-7,898 cm-1, 4,096 pts)",
    num_samples=15,  # 2D materials / reference substrate x (ACN or no BINOL, R-BINOL, S-BINOL)
    num_spectra=45,  # ir_* and vcd_* CSVs (2-column)
    num_spectral_values=184320,  # 45 x 4,096
    spectral_target_relationship="VCD (delta A) and IR bands of BINOL enantiomers (aromatic C=C, C-O, O-H bending 1,000-1,600 cm-1) with and without 2D nanosheets -> surface-enhanced VCD factors and sign fidelity enabling chiral molecule discrimination at low concentration",
    source_file="21419320.xml (Nano Lett. 2025 25:14363, doi:10.1021/acs.nanolett.5c03583 'Liquid-Phase Exfoliated 2D Nanomaterials for Enhanced Vibrational Circular Dichroism of Chiral Molecules'); 45 CSVs named <ir|vcd>_<substrate>_<acn|rbinol|sbinol>.csv",
    confidence=0.75,
)

R["21506062"] = dict(
    modality="Machine-learning double-harmonic (neural-network force field + dipole model) infrared stick spectra (scaled frequencies and intensities, km/mol) of 144,111 polycyclic aromatic hydrocarbons from COMPAS-2 in anionic, neutral and cationic charge states",
    spectral_range_original_min=4.3747, spectral_range_original_max=6281.6305, spectral_range_original_unit="cm-1",
    sampling_interval_unit="stick spectra: 3N-6 normal modes per molecule (mean ~187), frequencies scaled by 0.956/0.960",
    num_samples=48037,  # unique PAH structures, each in 3 charge states (-1, 0, +1)
    num_spectra=144111,  # one .xyz per molecule/charge: geometry + mode list (scaled_Freq, Inten, scale_factor)
    num_spectral_values=27000396,  # total normal-mode intensities over all 144,111 files (counted)
    spectral_target_relationship="Computed IR band positions/intensities (C-H stretch 3.3 um, C-C 6.2/7.7 um, C-H in/out-of-plane 8.6/11.2/12.7 um) across charge states and structures, validated against DFT and PAHdb -> reference library for interpreting interstellar aromatic infrared bands (JWST)",
    source_file="21506062.pdf (Mai, Lu & Wang 2026 A&A 'A machine-learning-driven dataset of 144,111 polycyclic aromatic hydrocarbon infrared spectra for interpreting aromatic infrared bands'); IR_COMPAS.zip -> IR_COMPAS/charge_-1, charge_0, charge_1 (48,037 .xyz each: atom count, 'Source=COMPAS2 Formula Charge JSD' line, Cartesian coordinates, then scaled_Freq(cm^-1) Inten(KM/mol) scale_factor table)",
    confidence=0.7,
)

R["18495815"] = dict(
    modality="Mid-infrared (FTIR) hyperspectral imaging (PerkinElmer Spotlight .fsm, transmittance, 25 um pixels) of colorectal cancer liver metastasis (CRLM) tissue sections, co-registered with H&E histopathology and MALDI mass-spectrometry imaging lipidomics",
    spectral_range_original_min=748.0, spectral_range_original_max=4000.0, spectral_range_original_unit="cm-1",
    num_spectral_channels=814, sampling_interval=4, sampling_interval_unit="cm-1",
    num_samples=12,  # CRLM patients (ID5a, 7b, 9, 10, 18a, 19, 21, 25, 27, 30, 31 top/bottom, 32)
    num_spectra=1534104,  # 13 cohort cubes (1,393,304 pixel spectra) + example ID18 raw cube (140,800); example ID5a/ID32 cubes are byte-identical copies of cohort cubes and not counted
    num_images=14, num_pixels=1534104,
    spatial_resolution=25, spatial_resolution_unit="um pixel size",
    num_spectral_values=1248760656,  # 1,534,104 x 814
    spectral_target_relationship="Tissue-type-specific wavenumber features (tumor PO2- 1,156/1,108/964 cm-1, connective tissue amide III 1,200-1,300 cm-1, liver parenchyma lipid C=O 1,740-1,760 cm-1, necrosis amide I/II) selected by random forest + error test -> projection images and spatial-autocorrelation (local Moran's I) hot-spot maps for cohort-wide tumor prediction, used as regions of interest for MALDI-MSI lipid biomarker discovery",
    source_file="18495815.xml (Adv. Sci. 2026 13:e16847, doi:10.1002/advs.202516847 'Cohort-Scale Spatial Autocorrelation for Tumor Prediction in Mid-Infrared Pathology and Spatial Biomarker Discovery Using MALDI Imaging Lipidomics'); re-downloaded 2026-10-29: datasets/MIRimaging/ID*_MIRimaging.fsm (13 cubes, 245x637 to 451x467 px x 814 channels, dimensions from FSM headers), datasets/HEstaining/*.svs, MALDI *.imzML/*.ibd (24, not counted); example_data_set (IRIraw_ID18/32/5a.fsm, projection/hot-spot .npy, annotations, co-registration tif)",
    confidence=0.8,
)

# === end R ===
