# Per-record metadata extracted from paper (C:\Users\Admin\RAG\2\papers\<id>.pdf) + dataset folder.
# Only keys that are known are given; build_parquet.py fills the rest with null and derives
# wavelength/wavenumber conversions + num_spectral_values where possible.
R = {}

R["1001720"] = dict(
    modality="NIR spectroscopy (diffuse reflectance, absorbance)",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    num_spectral_channels=2151, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=379,  # 300 mosquitoes (sporozoite set) + 79 mosquitoes (oocyst set)
    num_spectra=1012,  # 700 + 312 scans
    spectral_target_relationship="NIR spectrum of whole mosquito -> Plasmodium berghei infection status/intensity (sporozoite score 0-4, oocyst count) from microscopy dissection; classification (PLS)",
    source_file="1001720.pdf; NIRSdata2017_Lab_AnSteph_PlasmBerg_sporozoites.txt; NIRSdata2017_Lab_AnSteph_PlasmBerg_oocysts.txt",
    confidence=0.95,
)

R["1098206"] = dict(
    modality="ATR-FTIR spectroscopy (transmittance)",
    spectral_range_original_min=600, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3401, spectral_resolution=1, spectral_resolution_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=5, num_spectra=5,
    spectral_target_relationship="FTIR spectra of TPU and CNF/TPU nanocomposites (0-40 wt% CNF) -> chemical structure / H-bonding characterisation vs CNF loading (descriptive)",
    source_file="1098206.pdf; Supronics_Porous-TPU-Nanocomposites Dataset.xlsx (sheet '1. FTIR')",
    confidence=0.95,
)

R["1170059"] = dict(
    modality="Optical spectrum analysis (grating OSA + FTIR spectrometer) of mid-IR supercontinuum / frequency comb",
    spectral_range_original_min=350, spectral_range_original_max=5000, spectral_range_original_unit="nm",  # OSAs 0.35-2.4 um, FTIR up to 5 um
    spectral_target_relationship="Supercontinuum / dispersive-wave output spectra -> Si3N4 waveguide geometry (width 1.3-1.8 um, height 0.87/2.3 um) and comparison with NLSE simulation; mid-IR comb coherence (descriptive, no prediction target)",
    source_file="1170059.pdf; open_data_source.7z (figure_raw_data/Figure_Raw_Data.opj, supercontinuum_simulation_code/*.m)",
    confidence=0.55,
)

R["1461817"] = dict(
    modality="ATR-FTIR spectroscopy (+ fluorescence excitation-emission spectroscopy)",
    spectral_range_original_min=750, spectral_range_original_max=3650, spectral_range_original_unit="cm-1",
    spectral_resolution=0.5, spectral_resolution_unit="cm-1",
    num_samples=4, num_spectra=4,  # TBA leaf / primary wood / secondary wood extracts + birch pollen washing water
    spectral_target_relationship="FTIR (and fluorescence) spectra of birch tissue extracts -> chemical similarity to birch pollen ice-nucleating macromolecules (qualitative band assignment); dataset itself only holds droplet-freezing data",
    source_file="1461817.pdf (Sect. 2.4/3.3, Fig. 5); Raw data freezing.xlsx (no spectra in dataset)",
    confidence=0.5,
)

R["19060"] = dict(
    modality="NIR spectroscopy (astronomical long-slit / prism / cross-dispersed spectra)",
    spectral_range_original_min=0.642, spectral_range_original_max=2.583, spectral_range_original_unit="um",
    num_spectral_channels=2236,  # median per spectrum (range 502-6690)
    spectral_resolution=500, spectral_resolution_unit="R (lambda/dlambda); most common (Flamingos-2), range 90-6000",
    num_samples=221, num_spectra=238,
    num_spectral_values=658978,  # sum of channels over all 238 FITS spectra
    spectral_target_relationship="NIR spectra of M4-L7 dwarfs -> spectral type and gravity class (low-gravity / youth indicators), young moving-group membership",
    source_file="19060.pdf; 238 *.fits (+ .txt, .png) spectra",
    confidence=0.85,
)

R["58501"] = dict(
    modality="NIR spectroscopy (astronomical; SIMON, GNIRS, NIRI, SpeX)",
    spectral_range_original_min=0.633, spectral_range_original_max=2.557, spectral_range_original_unit="um",
    num_spectral_channels=564,  # median per spectrum (range 82-3986)
    spectral_resolution_unit="R (lambda/dlambda); varies by instrument: SIMON ~40, SpeX 75-750, NIRI ~500, GNIRS ~1700",
    num_samples=169, num_spectra=201,  # paper: 197 spectra of 169 targets; dataset holds 201 FITS spectra
    num_spectral_values=379437,
    spectral_target_relationship="NIR spectra of SIMP proper-motion candidates -> spectral type classification (M/L/T dwarfs; spectral indices + standard comparison), peculiarity/youth flags",
    source_file="58501.pdf; 201 *.fits (+ .txt, .png) spectra",
    confidence=0.85,
)

R["2538430"] = dict(
    modality="FTIR transmission spectroscopy (RAIRS-free, ice on IR window; absorbance)",
    spectral_range_original_min=599.68, spectral_range_original_max=3999.13, spectral_range_original_unit="cm-1",
    num_spectral_channels=7053, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=28,  # 28 ice experiments (exp_01..exp_29, exp_27 absent)
    num_spectra=1235, num_spectral_values=8710455,
    spectral_target_relationship="Time/temperature series of IR spectra of UV-irradiated C2H6/C2H4/C2H2 : CO2/CO ices -> product column densities (ethanol, acetaldehyde, ethylene oxide, ketene) and branching ratios via band integration",
    source_file="2538430.pdf; exp_01_IR.txt ... exp_29_IR.txt (28 files, columns = scans)",
    confidence=0.85,
)

R["2605449"] = dict(
    modality="FTIR transmission spectroscopy (KBr pellet, absorbance)",
    spectral_range_original_min=649.9, spectral_range_original_max=3200.0, spectral_range_original_unit="cm-1",
    num_spectral_channels=42312, spectral_resolution=0.2, spectral_resolution_unit="cm-1",
    sampling_interval=0.0603, sampling_interval_unit="cm-1",
    num_samples=4,  # 4 pyrene/KBr pellets (0.30, 0.33, 0.83, 0.86 mg)
    num_spectra=20,  # full spectra at 20 temperatures 14-723 K (plus band-region cut-outs)
    spectral_target_relationship="IR spectrum of pyrene vs temperature (14-723 K) -> band positions, widths and integrated intensities; empirical anharmonic factors (regression vs T)",
    source_file="2605449.pdf; Dataset_IRPyrene_Tevol_2019.zip (Spectra/Total_spec/*K.txt; Data/band_pos_T.txt, band_width_T.txt, inten_T.txt)",
    confidence=0.9,
)

R["3241923"] = dict(
    modality="VIS-NIR hyperspectral imaging (push-broom, reflectance) + RGB imaging",
    spectral_range_original_min=383.22, spectral_range_original_max=1006.47, spectral_range_original_unit="nm",
    num_spectral_channels=256, sampling_interval=2.444, sampling_interval_unit="nm",
    num_samples=8640,  # 90 varieties x 96 seeds
    num_images=180,  # 90 varieties x 2 HSI cubes of 48 seeds (+ calibration cubes; 181 RGB JPGs)
    num_pixels=312816,  # 336 x 931 pixels per cube
    image_height=931, image_width=336,
    num_spectral_values=14414561280,  # 180 x 312816 x 256
    spectral_target_relationship="Per-seed hyperspectral (+RGB morphological) features -> rice seed variety (90-class classification)",
    source_file="3241923.pdf; RGB and VIS-NIR HSI Data for 90 Rice Seed Varieties.zip (ENVI .hdr/.raw cubes, wavelengths.csv, index.csv, .JPG)",
    confidence=0.85,
)

R["3533467"] = dict(
    modality="UV-Vis absorption spectroscopy (+ EPR in paper)",
    spectral_range_original_min=12500, spectral_range_original_max=50000, spectral_range_original_unit="cm-1",  # 200-800 nm
    num_spectral_channels=600,
    num_samples=5,  # FdM-7 (AKG51-53), AKG_2_80 maquette, [4Fe-4S](SEt)4, [4Fe-4S](bME)4 references, PFL-AE enzyme
    num_spectra=5,
    spectral_target_relationship="UV-Vis spectra of [4Fe-4S]-maquettes and reference complexes -> quantitation of [4Fe-4S]2+ cluster incorporation via multi-peak (Gauss+Lorentz) deconvolution / integrated intensities",
    source_file="3533467.pdf; UV-vis models.zip (*/*.dat spectra, *.txt fit reports, summary xlsx)",
    confidence=0.75,
)

R["3593769"] = dict(
    modality="In situ UV-Vis absorption spectroscopy (submersible spectro::lyser probe) -> derived NO3-N / DOC",
    num_samples=4,  # stream stations NF (natural forest), SHA (smallholder agric.), TTP (tea/tree plantation), OUT (outlet)
    spectral_target_relationship="In situ UV-Vis absorbance spectra -> NO3-N and DOC concentrations (sensor calibration against 622 grab-sample lab analyses); 10-min time series used for diurnal/land-use analysis. Dataset holds derived concentrations only, no raw spectra",
    source_file="3593769.pdf; Data.zip (NF/SHA/TTP/OUT .ts.csv, *.exp.csv, Calibration.csv)",
    confidence=0.4,
)

R["3716316"] = dict(
    modality="TGA-FTIR evolved-gas FTIR spectroscopy (gas cell) (+ TED-GC-MS, XRF)",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=10,  # SAE, HK, CCP activated carbons with/without carbamazepine loadings (10 systems)
    spectral_target_relationship="Time/temperature-resolved FTIR spectra of evolved pyrolysis gases (23 TGA-FTIR series, OMNIC .srs) -> identification of decomposition products (H2O, CO2, NH3, ...) and release rates vs carbamazepine loading / adsorption sites",
    source_file="3716316.pdf; TGA-FTIR.zip (23 *.srs series); overview_measurements.xlsx",
    confidence=0.6,
)

R["3758200"] = dict(
    modality="Mass-resolved electronic circular dichroism ion spectroscopy (UV electron photodetachment action spectra)",
    spectral_range_original_min=230, spectral_range_original_max=295, spectral_range_original_unit="nm",
    num_spectral_channels=27, sampling_interval=2.5, sampling_interval_unit="nm",
    num_samples=3,  # dTG4T, lTG4T quadruplexes and 5YEY (d/l mixtures at 260 nm)
    spectral_target_relationship="Gas-phase CD (anisotropy factor g from ePD yields with L/R circularly polarised light) of mass-selected DNA G-quadruplex anions -> helical topology / handedness; g at 260 nm vs d/l enantiomer fraction",
    source_file="3758200.pdf; Supplementary_data.rar (Figure_2/*CDMS.csv + raw laser/MS logs)",
    confidence=0.6,
)

R["3787228"] = dict(
    modality="Vibrational STEM-EELS hyperspectral imaging (monochromated, 60 keV)",
    spectral_range_original_min=-0.1097, spectral_range_original_max=0.7745, spectral_range_original_unit="eV",
    num_spectral_channels=1976, spectral_resolution=8, spectral_resolution_unit="meV (ZLP FWHM 6-10 meV)",
    sampling_interval=0.4477, sampling_interval_unit="meV",
    num_images=33,  # .hspy aligned spectrum images recovered from (truncated) archive; + 8 .dm3 raw spims
    num_pixels=10000, image_height=50, image_width=200,  # example spim Cut0/Tip1
    spatial_resolution=6.25, spatial_resolution_unit="nm (pixel size)",
    spectral_target_relationship="EELS spectrum images of Ag nanowire on h-BN -> plasmon-phonon strong coupling (peak splitting) vs nanowire length (FIB cuts) and beam position; phonon mode enhancement",
    source_file="3787228.pdf; Dataset_hBN-PlasmonPhononCoupling_Tizei_NL_2020.zip (truncated; *.hspy, *.dm3, *.npy)",
    confidence=0.6,
)

R["3885450"] = dict(
    modality="Transient electronic absorption spectroscopy (UV pump / white-light probe) + transient vibrational absorption (mid-IR probe)",
    spectral_range_original_min=319.514, spectral_range_original_max=719.530, spectral_range_original_unit="nm",  # TEAS; TVAS probe 1497-1643 cm-1
    num_spectral_channels=686, sampling_interval=0.58, sampling_interval_unit="nm",
    num_samples=2,  # ACyO in EtOH and in DMSO
    num_spectra=412,  # TEAS 2 x 120 delays + TVAS 2 x 86 delays
    num_spectral_values=175132,  # 2*686*120 + 2*61*86
    spectral_target_relationship="Pump-probe transient spectra vs time delay -> excited-state relaxation dynamics/lifetimes (global kinetic fit) and ground-state recovery of mycosporine motif ACyO (photoprotection)",
    source_file="3885450.pdf; 4mM_ACyO_{EtOH,DMSO}_TEAS_chirp_corrected.csv; 50mM_ACyO_{EtOH,DMSO}_TVAS.csv",
    confidence=0.85,
)

R["3986895"] = dict(
    modality="UV-Vis absorption spectroscopy (+ FTIR 500-3600 cm-1, XRD)",
    spectral_range_original_min=300, spectral_range_original_max=700, spectral_range_original_unit="nm",
    num_samples=6,  # AgNPs from 3 extract volumes x 2 plant extracts (A. indica, C. colocynthis)
    num_spectra=6,
    spectral_target_relationship="UV-Vis surface-plasmon absorption peak (412-431 nm) -> confirmation of AgNP formation and selection of optimal extract volume; FTIR -> surface functional groups (descriptive)",
    source_file="3986895.pdf; Figure_4a/4b_(UV-VIS_Data).opj; Figure_8a/8b_(FTIR_Data).opj",
    confidence=0.6,
)

R["3994312"] = dict(
    modality="Surface-enhanced Raman spectroscopy (SERS, 785 nm excitation) incl. Raman mapping",
    spectral_range_original_min=800, spectral_range_original_max=1800, spectral_range_original_unit="cm-1",  # Raman shift, as plotted
    spatial_resolution=1, spatial_resolution_unit="um (map step; 0.1 um small-scale map)",
    spectral_target_relationship="SERS spectra of R6G, beta-lactoglobulin, glucose on porous carbon nanowire array -> analyte concentration (peak intensity vs concentration, LOD), enhancement factor and substrate uniformity/reproducibility (20 substrates, CV)",
    source_file="3994312.pdf; Figure 1-4.zip (*.opj, Fig. 3c.xlsx, map .tif)",
    confidence=0.5,
)

R["4006464"] = dict(
    modality="UV-Vis absorption spectroscopy (+ far-UV circular dichroism)",
    spectral_range_original_min=200, spectral_range_original_max=900, spectral_range_original_unit="nm",
    num_spectral_channels=701, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=19,  # Cyt c (20 uM) titrated with 19 DNA concentrations (0-200 uM)
    num_spectra=27,  # 19 UV-Vis titration spectra + 8 CD spectra (180-500 nm)
    spectral_target_relationship="UV-Vis (Soret band) and CD spectra of cytochrome c vs DNA concentration -> Cyt c-DNA binding, heme/secondary-structure conformation changes linked to peroxidase-like activity",
    source_file="4006464.pdf; Figure_2.xlsx (sheet 'figure 2a'); Figure_4_and_table_1.xlsx (CD)",
    confidence=0.75,
)

R["4015439"] = dict(
    modality="ATR-FTIR spectroscopy (transmittance)",
    spectral_range_original_min=2500.257, spectral_range_original_max=4000.122, spectral_range_original_unit="cm-1",
    num_spectral_channels=3112, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=3, num_spectra=3,  # laccase/TEMPO/OA-treated jute, control jute, OA monomer
    spectral_target_relationship="FTIR spectra -> confirmation of octadecylamine grafting onto jute fibres (CH2 stretching bands 2920/2851 cm-1), linked to surface hydrophobicity (descriptive)",
    source_file="4015439.pdf; Data_RSOS-.xlsx (Sheet2, Fig. 1 columns)",
    confidence=0.9,
)

R["4134667"] = dict(
    modality="FTIR spectroscopy",
    spectral_range_original_min=500, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_samples=2, num_spectra=2,  # water-soluble (WSC) and alkali-soluble (ASC) concentrates
    spectral_target_relationship="FTIR spectra of WSC/ASC -> qualitative identification of polysaccharide and protein (amide I-III) functional groups; dataset holds functional-property tables only (no spectra)",
    source_file="4134667.pdf (Sect. 2 / 3.2.2, Fig. 2); rors.xlsx (no spectral data)",
    confidence=0.45,
)

R["4263842"] = dict(
    modality="VIS-SWIR reflectance spectroscopy (SVC HR-1024) + LWIR FTIR emissivity spectroscopy (MIDAC M2000)",
    spectral_range_original_min=348.1, spectral_range_original_max=13995.8, spectral_range_original_unit="nm",  # SW 348.1-2505.8 nm; LWIR 8.0-14.0 um
    num_spectral_channels=1544,  # 988 SW + 556 LWIR
    spectral_resolution=2, spectral_resolution_unit="cm-1 (LWIR FTIR); SW 3.5-9.5 nm",
    num_samples=74, num_spectra=148, num_spectral_values=114256,
    spectral_target_relationship="Reflectance + emissivity spectra of 74 impervious urban material samples -> material class identification/discrimination (spectral library for remote sensing)",
    source_file="4263842.pdf; LUMA_SLUM_SW.csv; LUMA_SLUM_IR.csv; 2013_LUMA_SLUM.pdf",
    confidence=0.9,
)

R["4310961"] = dict(
    modality="Time-resolved (ns-us) UV-pump / visible-probe transient absorption + mid-IR transient absorption (+ steady-state UV-Vis, FTIR difference)",
    spectral_range_original_min=453.27, spectral_range_original_max=787.50, spectral_range_original_unit="nm",  # transient Vis; transient IR 1516-1780 cm-1; steady-state UV-Vis 250-750 nm
    num_spectral_channels=427, spectral_resolution=0.8, spectral_resolution_unit="nm (Vis probe); IR ~2 cm-1/pixel",
    num_samples=2,  # Slr1393g3 CBCR in Pr and Pg photostates
    num_spectra=188,  # Vis 2x46 delays + IR 2x46 delays + 2 UV-Vis + 2 FTIR difference spectra
    spectral_target_relationship="Transient Vis/IR difference spectra vs delay (100 ps - 42 us) -> photocycle intermediates and their lifetimes (global/target kinetic analysis) for Pr->Pg and Pg->Pr photoconversion",
    source_file="4310961.pdf; Fig1.dat (UV-Vis, FTIR); Fig2.dat (transient Vis 46x427 x2); Fig3.dat (transient IR 46x112 x2)",
    confidence=0.85,
)

_jelly = dict(
    modality="FTIR spectroscopy (KBr pellet, transmittance)",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=2, num_spectra=2,  # EDC-crosslinked and non-crosslinked collagen scaffold
    spectral_target_relationship="FTIR spectra of jellyfish A. aurita collagen scaffolds -> identification of amide A/B/I/II/III bands, effect of EDC cross-linking (qualitative)",
)
R["4431156"] = dict(_jelly, source_file="4431156.pdf; FTIR_EDC.pdf; FTIR_Non EDC.pdf (plotted spectra with peak tables)", confidence=0.65)
R["4450040"] = dict(_jelly, source_file="4450040.pdf (same article as 4431156); FTIR_EDC.pdf; FTIR_Non EDC.pdf (plotted spectra with peak tables)", confidence=0.65)

R["4544876"] = dict(
    modality="FTIR transmission spectroscopy (absorbance, dust on Si substrate)",
    spectral_range_original_min=349.1, spectral_range_original_max=5999.0, spectral_range_original_unit="cm-1",  # files: P0 400-4000, P1 350-4000, P1bis 349-5999
    num_spectral_channels=5860,  # P1bis spectra (P0: 3733, P1: 3786)
    spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=3,  # P0 (no Ag), P1 and P1bis (with Ag)
    num_spectra=13,  # 9 full spectra (incl. P1bis heated 200/500 C, 0-2 h) + 4 local-continuum band cut-outs
    spectral_target_relationship="IR absorbance of plasma-grown organosilicon/Ag dust analogues -> band assignment (Si-O-Si, Ag2CO3, Si-H...) and evolution with annealing temperature/time (descriptive)",
    source_file="4544876.pdf; Dataset_IR_plasma_samples_Frontiers_Berard2021.zip (P0*.txt, P1*.txt, P1bis_*.txt, readme)",
    confidence=0.9,
)

R["4563039"] = dict(
    modality="ATR-FTIR spectroscopy (+ XPS)",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_samples=3, num_spectra=3,  # GO, SA-GO before and after U(VI) adsorption
    spectral_target_relationship="FTIR spectra of GO and SA-GO before/after U(VI) adsorption -> functional groups involved in uranium binding (peak shifts; qualitative); dataset holds adsorption kinetics/isotherm data only",
    source_file="4563039.pdf (FTIR characterization, Fig. 2); Manuscript_date.xls (no spectra)",
    confidence=0.45,
)

R["4568684"] = dict(
    modality="Raman micro-spectroscopy (532 nm) + ATR-FTIR micro-spectroscopy",
    spectral_resolution=4, spectral_resolution_unit="cm-1 (ATR-FTIR)",
    num_samples=19,  # 19 polymer types (14 commodity polymers + 5 paint resins), 10-70 um particles
    spectral_target_relationship="Raman/FTIR spectra of microplastic particles before vs after chemical digestion treatments (>=3 replicate particles each) -> polymer recognisability / treatment-induced spectral changes (qualitative)",
    source_file="4568684.pdf; Raman+FTIR_commodityPolymers.pdf (229 p.); Raman+FTIR_paintResins.pdf (78 p.)",
    confidence=0.5,
)

R["4574259"] = dict(
    modality="ATR-FTIR spectroscopy (absorbance)",
    spectral_range_original_min=548.68, spectral_range_original_max=4000.80, spectral_range_original_unit="cm-1",  # paper: 4000-400 cm-1, 64 scans
    num_spectral_channels=3581,  # HDPE spectra (PP spectra: 2562 points, 720-3190 cm-1)
    sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=4, num_spectra=4,  # PP and HDPE, 0 and 120 kGy e-beam dose
    num_spectral_values=12286,
    spectral_target_relationship="FTIR of e-beam irradiated vs non-irradiated PP/HDPE -> radiation-induced chemical changes (C=C, C=O formation, 1500-1800 cm-1) linked to crystallization behaviour (descriptive)",
    source_file="4574259.pdf; RSOS-202250.R1-Svoboda-numbers-a.xlsx (sheet Fig04)",
    confidence=0.85,
)

R["4577395"] = dict(
    modality="UV-Vis diffuse reflectance spectroscopy (+ reflection FTIR 400-2000 cm-1, ED-XRF, colorimetry)",
    spectral_range_original_min=300, spectral_range_original_max=900, spectral_range_original_unit="nm",
    num_spectral_channels=1201, sampling_interval=0.5, sampling_interval_unit="nm",
    num_samples=35,  # turquoise-group samples analysed (ED-XRF); UV-Vis data provided for 6 representative samples
    num_spectra=6,
    spectral_target_relationship="UV-Vis absorption bands of Fe3+, Cu2+, V3+, Cr3+ (and FTIR water/OH bands) -> transition-metal / water content effects on turquoise colour (CIE L*a*b*); FTIR ROH ratio to discriminate turquoise/chalcosiderite/faustite",
    source_file="4577395.pdf; UV-Vis_Data.xlsx; FTIR_Data.docx (peak tables); Color_Data.docx; Primary_EDXRF_data_for_35_turquoise_samples.docx",
    confidence=0.8,
)

R["4658303"] = dict(
    modality="Computed anharmonic IR absorption spectra (AnharmoniCaOs DFT + DFTB molecular dynamics), no measurement",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=18001, sampling_interval=0.2, sampling_interval_unit="cm-1",  # AC stick spectra; DFTB spectra: 2160 points (~1.67 cm-1)
    num_samples=1,  # pyrene C16H10
    num_spectra=21,  # 12 AC temperatures (14-523 K) + 9 DFTB temperatures (200-1600 K)
    num_spectral_values=235452,
    spectral_target_relationship="Simulated IR spectra of pyrene vs temperature -> band positions and widths vs T (anharmonic factors), compared with experimental spectra",
    source_file="4658303.pdf; Dataset_Pyrene_theory_2021.tar.gz (data_AC/spectra/*.txt, data_DFTB/spectra/*.txt, bp_T/bw_T tables)",
    confidence=0.85,
)

R["4670183"] = dict(
    modality="FTIR micro-spectroscopy (unpolarized, transmission; OH stretching region)",
    spectral_range_original_min=1001, spectral_range_original_max=5000, spectral_range_original_unit="cm-1",
    num_spectral_channels=2075, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=8,  # recovered high-pressure run products (Fe-bearing and Fe-free wadsleyite)
    num_spectra=66, num_spectral_values=131770,
    spectral_target_relationship="IR absorbance integrated over 3000-4000 cm-1 (Beer-Lambert) -> water content (CH2O) of wadsleyite; relation of water solubility to Fe content, P and T",
    source_file="4670183.pdf; FTIR data.zip (66 *.txt spectra); EPMA data.xlsx",
    confidence=0.9,
)

R["4784179"] = dict(
    modality="NIR FTIR diffuse reflectance spectroscopy (fibre-optic probe, Titan simulation chamber)",
    spectral_range_original_min=3999.7, spectral_range_original_max=9999.3, spectral_range_original_unit="cm-1",  # = 1.0-2.5 um
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=4,  # experiments: CH4+C2H4, C2H6+C2H4 (90-94 K), CH4+C2H6+C2H4, C2H6+C2H4 warming 90-166 K
    spectral_target_relationship="Time/temperature series of NIR spectra of evaporating hydrocarbon mixtures -> ethylene evaporite formation, band depths/shifts (1.630, 2.121 um) vs composition and temperature; mass loss -> evaporation rates",
    source_file="4784179.pdf; C2H4_Raw-Experimental-Data_Version1.0.zip (*_Spectra.xlsx, *_Band Depths.xlsx, *_Mass_Temp.xlsx)",
    confidence=0.7,
)

R["4792633"] = dict(
    modality="FTIR spectroscopy (+ X-ray micro-CT)",
    spectral_range_original_min=399.68, spectral_range_original_max=4000.19, spectral_range_original_unit="cm-1",
    num_spectral_channels=7469, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=6, num_spectra=6,  # 2 termite mounds x (ground material, not-ground material, soil)
    num_spectral_values=44814,
    spectral_target_relationship="FTIR spectra of termite mound materials vs surrounding soil -> compositional differences (organic/mineral bands) supporting mound microstructure/mechanics analysis. NOTE: supplied paper 4792633.pdf is unrelated (Naive Bayes ML article); values derived from dataset only",
    source_file="FTIR.mat (6 variables, 7469x2); ctScan_Sample.pvl.nc.001; 4792633.pdf mismatched",
    confidence=0.45,
)

R["4816493"] = dict(
    modality="FTIR spectroscopy (sample water check) + low-frequency forced-oscillation mechanical spectroscopy",
    spectral_range_original_min=399.2, spectral_range_original_max=3998.0, spectral_range_original_unit="cm-1",
    num_spectral_channels=3734, sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=3,  # olivine-orthopyroxene aggregates Ol95Px5, Ol70Px30, Ol5Px95
    num_spectra=3, num_spectral_values=11202,
    spectral_target_relationship="FTIR spectra -> water content / dryness of Ol-Px aggregates before/after testing; main data: shear modulus G and attenuation vs oscillation period (1-1000 s, 20 periods) at 400-1300 C (53 curves). NOTE: supplied paper 4816493.pdf is unrelated (maths article); values derived from dataset only",
    source_file="Ol-Px_manuscript_dataset.7z (FTIR/*.dpt, Ol-Px_raw_data.xlsx, SEM, EBSD); 4816493.pdf mismatched",
    confidence=0.45,
)

R["4882967"] = dict(
    modality="FTIR (mid-IR) transmission spectroscopy of PTFE filter samples (+ HR-ToF aerosol mass spectrometry)",
    spectral_range_original_min=399.24, spectral_range_original_max=3996.30, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=20, num_spectra=20,  # chamber filters (primary/aged wood burning & coal combustion); + IMPROVE network ambient spectra for comparison
    num_spectral_values=37320,
    spectral_target_relationship="MIR absorbance spectra of fine PM -> organic functional group mass concentrations (peak fitting: aCH, COH, COOH, CO...), OM, O:C compared with AMS; primary vs OH/NO3-aged burning aerosol; lignin/levoglucosan markers in IMPROVE spectra",
    source_file="4882967.pdf; FTIR_raw_spectra.csv; FTIR_baseline_corrected*_spectra.csv; FTIR_FG_mass_concentration.csv; Baselined_spectra_corrected_IMPROVE.csv; DATASET_README.txt",
    confidence=0.85,
)

R["48902"] = dict(
    modality="Ground-based high-resolution solar absorption FTIR spectroscopy (NDACC) -> retrieved H2O/HDO profiles",
    spectral_range_original_min=2655, spectral_range_original_max=3021, spectral_range_original_unit="cm-1",  # MUSICA H2O isotopologue microwindows (+ CO2 windows 2620-2630 cm-1)
    num_samples=12,  # 12 NDACC FTIR stations (one zip per station)
    spectral_target_relationship="Solar absorption spectra (microwindows of H2-16O, HD-16O, H2-18O lines) -> retrieved tropospheric H2O and deltaD vertical profiles via optimal-estimation inversion; dataset holds retrieval products (GEOMS HDF), not spectra",
    source_file="48902.pdf; musica_<station>.zip (groundbased_ftir.iso*.hdf)",
    confidence=0.6,
)

R["4923133"] = dict(
    modality="TGA-FTIR evolved-gas FTIR spectroscopy (+ XPS, XRF, XRD, N2 sorption)",
    num_samples=8,  # activated carbons: 5000P-f, AZ1050, CC401, CCP90D, HK950, HKP1050, SAE Super, WP235 (triplicate TGA-FTIR)
    spectral_target_relationship="Evolved-gas FTIR spectra -> H2O, CO2, CO, CH4 release rates (calibrated with Ca oxalate) -> surface oxygen group quantities and oxygen content of activated carbons (Gaussian deconvolution, PCA); dataset holds processed gas-release profiles",
    source_file="4923133.pdf; zenodo_raw-data.zip (08_TGA-FTIR/*, 05_XPS, 06_XRF)",
    confidence=0.5,
)

R["4936038"] = dict(
    modality="NIR spectroscopy (diffuse reflectance, whole insect)",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    num_spectral_channels=2151, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=266, num_spectra=266,  # 154 species-ID + 112 triglyceride spectra (individual flies)
    spectral_target_relationship="NIR spectra of individual Drosophila -> triglyceride level (PLS regression vs assay kit, R2 0.70-0.73) and species D. melanogaster vs D. simulans (classification vs allele-specific PCR, >80%)",
    source_file="4936038.pdf; NIRS.zip (*.spc raw spectra, Species Identification.xlsx, Triglyceride quantification.xlsx)",
    confidence=0.9,
)

R["4941781"] = dict(
    modality="UV-VIS-NIR reflectance and transmission spectroscopy (Ocean Optics USB2000+ / NIRQuest dual spectrometer)",
    spectral_range_original_min=300, spectral_range_original_max=2100, spectral_range_original_unit="nm",
    num_spectral_channels=901, sampling_interval=2, sampling_interval_unit="nm",
    num_samples=50,  # white contour feathers of 50 bird species
    num_spectra=679,  # 438 reflectance + 241 transmission spectra
    num_spectral_values=611779,
    spectral_target_relationship="Feather VIS/NIR reflectance & transmission spectra (average reflectance per band) <- predicted by feather macro/micro-structure (barb roundness, barbule density, size, thickness) via phylogenetic comparative models",
    source_file="4941781.pdf; reflectance and transmission spec measurements.xlsx (sheets Reflectance, Transmission); data for comparative analyses.csv",
    confidence=0.85,
)

R["4950040"] = dict(
    modality="Functional near-infrared spectroscopy (fNIRS, continuous-wave; HbO/HbR)",
    spatial_resolution=3, spatial_resolution_unit="cm (deep-channel source-detector separation; 1.5 cm reference channels)",
    num_samples=28,  # 14 listeners in each of 2 experiments
    spectral_target_relationship="Task-evoked HbO/HbR hemodynamic responses over STG and cIFS (from fNIRS optical density) -> individual vulnerability to informational masking in speech perception (regression, LMEM; ~1/3 of behavioural variance explained)",
    source_file="4950040.pdf; Ex1/Ex2_SPEECH_vs_*_behavior_and_raw_fNIRS_data.rar (processed/unprocessed .mat per listener); Ex*_LMEMoutput_from_R.rar",
    confidence=0.5,
)

R["4962336"] = dict(
    modality="NIRS tissue oximetry (INVOS 5100C, StO2; 4 cm source-detector spacing)",
    spatial_resolution=4, spatial_resolution_unit="cm (source-detector spacing)",
    num_samples=6,  # healthy adults analysed (8 recruited), NIRS leads on 4 sites (cerebral, shoulder, kidney, leg)
    spectral_target_relationship="NIRS-derived tissue oxygen saturation/extraction during exercise -> regional arterial flow distribution from MRI/CFD (linear regression, r2 0.96 cerebral-LCCA, 0.87 leg-dAo); used as surrogate for CFD boundary conditions",
    source_file="4962336.pdf; DryadRespository_PMID27376865.xls (Windkessel params, NIRS surrogate regressions, waveforms)",
    confidence=0.5,
)

R["4965176"] = dict(
    modality="FTIR transmission micro-spectroscopy of doubly polished glass wafers (H2O/OH bands) (+ EPMA major elements)",
    spectral_range_original_min=1630, spectral_range_original_max=5230, spectral_range_original_unit="cm-1",  # analytical bands used: 1630 (H2Omol), 4500 (OH-), 5230 (H2Omol)
    num_samples=23,  # Samail ophiolite volcanic glass samples with FTIR (29 analysed chips)
    num_spectra=101,  # FTIR measurements summed over chips (Beer-Lambert sheet)
    spectral_target_relationship="Absorbance of H2O/OH bands (Beer-Lambert with composition-dependent epsilon, density, thickness) -> dissolved water content of volcanic glasses, related to volcanic unit / magma source (Samail vs Troodos). Supplied paper (Belgrano 2019, Solid Earth) is the companion mapping study; FTIR details from dataset",
    source_file="4965176.pdf (companion study); Belgrano_et_al_2021_JGR-SE_datasets.xlsx (sheets 'Samail Ophiolite Results', 'Samail Beer-Lambert Parameters')",
    confidence=0.55,
)

R["4967075"] = dict(
    modality="Fecal NIR spectroscopy (NIRS-predicted diet quality) (+ DNA metabarcoding, stable isotopes)",
    num_samples=92,  # fecal samples (KS and SD bison, male/female, 2011-2014) with NIRS-derived %CP/%DOM
    spectral_target_relationship="Fecal NIRS spectra -> dietary crude protein (%CP) and digestible organic matter (%DOM) via calibrations against directly measured cattle forage quality; dataset holds predicted values only (no spectra)",
    source_file="4967075.pdf (Methods); Table4.csv (Fecal CP, isotopes); README.txt",
    confidence=0.5,
)

R["4977010"] = dict(
    modality="FTIR transmission spectroscopy of PTFE aerosol filters (Bruker Tensor II)",
    spectral_range_original_min=1499.087, spectral_range_original_max=3998.423, spectral_range_original_unit="cm-1",
    num_spectral_channels=1945, sampling_interval=1.286, sampling_interval_unit="cm-1",
    num_samples=6123,  # PM2.5 filter samples, 5 SEARCH sites, 2009-2016 (1-in-3 days) + all days 2016
    num_spectra=6123, num_spectral_values=11909235,
    spectral_target_relationship="Raw FTIR absorbance spectra -> organic functional group concentrations (aCH, COOH, oxOCO, naCO, aCOH), OM and OC via PLS calibration on laboratory standards; validated against TOR OC (R2=0.74) and mass-closure OM (R2=0.82)",
    source_file="4977010.pdf; FT-IR_OM_and_Functional_Groups_in_SEARCH_DataSet_-_2009_to_2016_1in3_days.csv; ..._2016_All_Days.csv; README",
    confidence=0.9,
)

R["4997973"] = dict(
    modality="ATR-FTIR spectroscopy (single-reflection diamond ATR, Bruker Vertex 70)",
    spectral_range_original_min=599.83, spectral_range_original_max=6997.33, spectral_range_original_unit="cm-1",  # analysed range 4000-600 cm-1
    num_spectral_channels=3318, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=310,  # pollen samples (trees x sampling) of 6 Quercus taxa in Portugal
    num_spectra=959,  # 3 replicate measurements per sample
    num_spectral_values=3181962,
    spectral_target_relationship="Pollen ATR-FTIR spectra -> Quercus section/species classification (CPPLS + LDA; ~97-100% at section level)",
    source_file="4997973.pdf; Muthreich_et_al_2020.zip (Data/Input/Quercus_ATR_RAW.csv, data_metainfo.csv, R scripts)",
    confidence=0.9,
)

R["5004464"] = dict(
    modality="Wearable continuous-wave spatially-resolved NIRS (Artinis PortaLite; O2Hb/HHb/tHb)",
    num_samples=4,  # captive harbour seals (data for Ulf, Vebjorn, Thor; brain and blubber placements)
    spectral_target_relationship="NIRS-derived relative changes in oxy/deoxy-haemoglobin and blood volume in brain and blubber -> timing of dive response (pre-dive vasoconstriction, cerebral blood volume) relative to dive phases; time series, no spectra",
    source_file="5004464.pdf; Figures 2 and 3.txt, Figures 4 and 5.txt, Figure 6A/6B *.txt, Figure S1/S2 *.txt, Metadata.txt",
    confidence=0.55,
)

R["5024543"] = dict(
    modality="Photodetector spectral responsivity / external quantum efficiency spectroscopy",
    spectral_range_original_min=400, spectral_range_original_max=1600, spectral_range_original_unit="nm",
    num_spectral_channels=61, sampling_interval=20, sampling_interval_unit="nm",
    num_samples=3,  # Si:CQD PVFET with 1500 nm and 1300 nm exciton CQDs, silicon-only control device
    num_spectra=5, num_spectral_values=230,
    spectral_target_relationship="EQE/gain vs wavelength of quantum-dot-sensitised silicon photovoltage FETs -> IR sensitisation beyond Si bandgap (excitonic peak at 1300/1500 nm, gain ~6e4) vs silicon-only device",
    source_file="5024543.pdf; Published_data.zip (Spectral_Resp.zip: Spectral_Responsivity_*.xls)",
    confidence=0.8,
)

R["5076283"] = dict(
    modality="ATR-FTIR spectroscopy (+ proteomics / transcriptomics)",
    spectral_range_original_min=500, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    spectral_target_relationship="FTIR spectra of Tridacna crocea shell organic matrix extracts (AIM bleaching fractions) -> qualitative identification of proteins, saccharides, lipids, phosphates; dataset holds only sequences (transcriptome, shell-matrix peptides), no spectra",
    source_file="5076283.pdf (FT-IR Spectroscopy, Fig. 2); Tridacna_crocea_SMP_pep.fa.gz; Tridacna_crocea_transcriptome_nuc.fa.gz",
    confidence=0.4,
)

R["5143698"] = dict(
    modality="FT-MIR milk spectroscopy (Bentley FTS routine milk testing)",
    spectral_range_original_min=656.5, spectral_range_original_max=3991.1, spectral_range_original_unit="cm-1",
    num_spectral_channels=895, sampling_interval=3.73, sampling_interval_unit="cm-1",
    num_samples=38085,  # cows (adjusted per-cow wavenumber phenotypes in dataset)
    num_spectra=100571,  # individual milk test-sample spectra used in the paper
    spectral_target_relationship="Individual FT-MIR wavenumber absorbances (and MIR-predicted fat/protein/lactose %) treated as phenotypes -> sequence-based GWAS / QTL and eQTL co-location (genetic variants associated with each wavenumber)",
    source_file="5143698.pdf; phenotypic-data.txt.zip; imputed-seq-genotypes-trait-qtl-output.vcf; eQTL-seq-model-outputs.zip; README.xlsx",
    confidence=0.85,
)

R["825527"] = dict(
    modality="Ground-based solar absorption FTIR spectroscopy (Bruker IFS 125HR high-res + Vertex 80 medium-res) -> O3 profile retrieval",
    spectral_range_original_min=991.25, spectral_range_original_max=1073.0, spectral_range_original_unit="cm-1",  # O3 retrieval windows
    num_spectral_channels=3634,  # IFS125 window bins (Vertex80: 1472)
    spectral_resolution=0.005, spectral_resolution_unit="cm-1 (IFS 125HR; Vertex 80: 0.1 cm-1)",
    sampling_interval=0.00417, sampling_interval_unit="cm-1 (IFS125; Vertex80 0.0556)",
    num_samples=2,  # sites/instruments: Altzomoni (NDACC, ~4 km a.s.l.) and UNAM Mexico City
    num_spectra=1537,  # 1040 Altzomoni + 497 UNAM measured spectra (with simulated fits)
    num_spectral_values=4510944,
    spectral_target_relationship="Measured solar absorption spectra in O3 windows -> retrieved O3 vertical profiles / total & partial columns (optimal estimation, PROFFIT) with averaging kernels, Jacobians and gain matrices; comparison of high- vs medium-resolution retrievals",
    source_file="825527.pdf; ALTZ_IFS125_O3.nc; ALTZ_IFS125_O3_Jac+Gain.nc; UNAM_Vertex80_O3.nc; UNAM_Vertex80_O3_Jac+Gain.nc; readNETCDF_and_combine2FTIR.m",
    confidence=0.9,
)

