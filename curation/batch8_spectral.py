# Batch8 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (E:\Batch8\papers\<id>.pdf or PMC JATS <id>.xml) + dataset (E:\Batch8\Datasets\<id>_<title>\),
# reviewed through the evidence packs in output/batch8/llm_packs/<id>.md (same input the LLM stage uses).
# Records without spectra stay in E:\Batch8\Datasets; they are listed in NO_SPECTRA and are not part
# of the batch8 parquet files (they go to output/batch8_no_spectra.csv).
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

# Records left out of the Batch8 parquet files because the dataset holds no spectra (record id -> reason).
NO_SPECTRA = {
    "3660940": "long-term field erosion plot tables (runoff, soil loss, N/P/SOC losses, crop yields; Mistelbach, Pixendorf, Pyhra 1994-2018; Data in Brief) - no spectra",
    "3966329": "Clinacanthus nutans AgNP workbook: TPC/TFC colorimetric standard-curve absorbances (single wavelength), TEM size histogram, XRD patterns (RSOS) - no spectra",
    "4529169": "Fig. S1 of an LC-MS/MS bile-acid method paper: plasma total cholesterol/HDL/LDL concentrations from a colorimetric UV/VIS assay (simvastatin mice) + PNG/PDF - concentrations only, no spectra",
    "4529977": "Fig. 4 data of the 11beta-HSD1 bile-acid biomarker paper (Br. J. Pharmacol.): LC-MS/MS quantification tables, scintillation counts and single-wavelength plate-reader NADPH readings (BioTek Synergy HT) - no spectra",
    "4572616": "silver-citrate endodontic irrigant (BioAKT) biofilm live/dead quantification workbook + MIC/MBC/MBEC table docx (Materials 2020); IR spectroscopy mentioned in the paper is not deposited - no spectra",
    "4723972": "chamois faecal NIRS crude-protein predictions per sample with weather/elevation covariates (single csv; Ecol. Evol. 2020) - f-NIRS predictions only, the spectra themselves are not included",
    "4783271": "Kallavesi lake microplastic workbook: sampling sites/volumes and per-particle FTIR-microscopy identification results (polymer, hit quality, size, colour) - library-match results only, no spectra",
    "4846182": "Arabidopsis HUB2/PIRIN2 lignin study (J. Exp. Bot.): yeast two-hybrid clone table and RNA-seq differential expression table - the FT-IR/Raman microspectra of the paper are not deposited, no spectra",
    "4939009": "acridine thiosemicarbazone fluoride chemosensors (RSOS): Bruker TopSpin 1H/13C/2D NMR raw data only - the UV-Vis/fluorescence titrations of the paper are not deposited, no optical spectra",
    "4946544": "1,4-dihydropyridine intramolecular H-bond study (RSOS): 21 Gaussian 09 NMR/DFT output files + 1H/13C-IE/15N-HSQC NMR spectra PDFs - no optical/vibrational spectra",
    "4951378": "Rhizophora mucronata tannin corrosion-inhibitor workbook (PLoS ONE): weight-loss and electrochemical corrosion rates vs concentration/temperature - the FTIR spectrum of the paper is not deposited, no spectra",
    "4952884": "Pt-Pd dendrimer nanocatalyst data (RSOS): 8 PANalytical XRD pattern csv exports only - no optical spectra",
    "4955272": "winter-wheat crown apoplast proteomics (J. Exp. Bot.): protein identification/quantification tables + figure PDFs (FTIR-FPA second-derivative spectra only as figures) - no spectra",
    "4964662": "cinchonidine-TCNQ helical charge-transfer complex (RSOS): 5 SEM micrographs and 1 HEED pattern (jpg) only - UV-Vis/CD spectra are only in the paper figures, no spectra",
    "4970315": "lotus fibre microwave extraction (RSOS): 6 PANalytical XRD csv + supplementary docx (morphology, moisture, mechanics) - FTIR spectra of the paper not deposited, no spectra",
    "4985780": "graphene/waterborne epoxy coating corrosion data (RSOS): EIS Nyquist/Bode tables, polarisation curves and water absorption - FTIR/Raman spectra of the paper not deposited, no optical spectra",
    "5667506": "PortaMon CW-NIRS tissue oximeter assessment (Sensors 2021): MATLAB .mat with optical-density and haemoglobin/TSI time series at two fixed wavelengths x 3 source-detector distances (phantoms, arm, VOT, stability) - multi-wavelength time courses, no spectra",
    "5115283": "vineyard biodiversity vs grape quality (J. Appl. Ecol.): CSV of FTIR-derived grape juice parameters (YAN, sugars, acids), soil N and vegetation per vineyard + R script - FTIR spectra not deposited, no spectra",
    "5026962": "neonatal ECMO cerebral oximetry (PLoS ONE): patient-level clinical table with summary INVOS NIRS StcO2 values (means, desaturation durations) - no spectra",
    "5001949": "yak dung biochar F/As adsorption (RSOS): single txt of adsorption isotherm/kinetic concentrations (ICP-OES, ion meter) - FTIR spectra of the paper not deposited, no spectra",
    "5000306": "akaganeite nanorice/mica photocatalyst (RSOS): docx/pdf with XRD patterns and methylene-blue degradation tables (single-wavelength absorbance vs time) - FT-IR spectra of the paper not deposited, no spectra",
}

R["1064966"] = dict(
    modality="Near-infrared low-resolution spectral templates (averaged IRTF/SpeX prism spectra) of field-gravity and low-gravity (beta, gamma) L0-L8 brown dwarfs in J, H and K bands",
    spectral_range_original_min=0.8004, spectral_range_original_max=2.3996, spectral_range_original_unit="um",
    sampling_interval=0.0039, sampling_interval_unit="um (J 152-155, H 126-128, K 158-159 points per band)",
    num_samples=16,  # templates: L0-L8 field (9), L0-L1 beta (2), L0-L4 gamma (5)
    num_spectra=48,  # 16 templates x 3 bands (J 0.80-1.40, H 1.40-1.90, K 1.90-2.40 um)
    num_spectral_values=28132,  # 7,033 wavelength points x 4 columns (mean, std, min, max normalised flux)
    spectral_target_relationship="Average, standard deviation and min/max envelope of band-normalised NIR flux (H2O 1.4/1.85 um bands, FeH, K I/Na I lines, CO 2.3 um, H-band shape) per optical spectral type and gravity class -> optically-anchored NIR classification and gravity diagnosis of L dwarfs",
    source_file="1064966.pdf (Reid, Burgasser, Cruz, Kirkpatrick & Gizis 2001 AJ 121:1710, arXiv:astro-ph/0012275 'Near-Infrared Spectral Classification of late-M and L Dwarfs' - earlier UKIRT/CGS4 classification paper, not the template paper Cruz et al. 2018 AJ 155:34); Ldwarf_NIRtemplates_v1.tar: 48 CDS-style .dat files <SpT><band>_<f|b|g>.dat (Wave um, <Flux>, e_<Flux>, MinFlux, MaxFlux)",
    confidence=0.8,
)

R["1095503"] = dict(
    modality="Computed (ab initio) far-infrared H2-H2 collision-induced absorption spectra including hydrogen dimer free-to-bound, bound-to-free and bound-to-bound transitions - modelled opacity tables, not measured",
    spectral_range_original_min=0.0, spectral_range_original_max=2400.0, spectral_range_original_unit="cm-1",
    sampling_interval=0.01, sampling_interval_unit="cm-1 (bound-bound tables; free-free 0.1-10 cm-1 grid to 2400 cm-1; S(0)/S(1) dimer tables 1-10 cm-1)",
    num_samples=11,  # para-H2 fractions fp = 0.25, 0.30, 0.35, 0.41, 0.47, 0.54, 0.62, 0.70, 0.80, 0.90, 1.0
    num_spectra=550,  # 11 fp x 10 temperatures (40-400 K) x 5 components (ff, bb, fb/bf Q, S0, S1)
    num_spectral_values=319110,  # rows (T, wavenumber, absorption coefficient) over 55 tables
    spectral_target_relationship="Absorption coefficient (cm-1 amagat-2) vs wavenumber near the H2 S(0) 354 cm-1 and S(1) 587 cm-1 quadrupole lines for 40-400 K and para-H2 fraction 0.25-1.0 -> opacity database for NEMESIS retrievals of temperature and para-H2 from Cassini/CIRS, Spitzer/IRS and Voyager/IRIS giant-planet spectra; validated against 20/77 K laboratory spectra",
    source_file="1095503.pdf (Fletcher, Gustafsson & Orton 2018 ApJS 235:24, arXiv:1712.02813 'Hydrogen dimers in giant-planet infrared spectra'); GitHub release leighfletcher/hydrogendimers v1.0: ff/ (11 free-free tables), bb/ (11 bound-bound), fbbf_Q, fbbf_S0, fbbf_S1 (11 each), README.md",
    confidence=0.75,
)

R["1134664"] = dict(
    modality="Transmission FTIR spectroscopy (Bruker Vertex 70v) of UV-irradiated (H2D2 lamp + sapphire filter) CH4:O2 and CO:CH4:O2 astrophysical ice analogues at 9-25 K, time series during 2 h irradiation",
    spectral_range_original_min=600.6, spectral_range_original_max=3999.131, spectral_range_original_unit="cm-1",
    num_spectral_channels=7053, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=28,  # experiments (Table 1: groups I-X, isotopologues 13CH4/16O2, CD4/18O2, ...)
    num_spectra=1021,  # 21-41 spectra per experiment taken every 3 min (0-118 min)
    num_spectral_values=7201113,
    spectral_target_relationship="Growth of the 13CH3OH nu8 C-O stretch (1008 cm-1; CD3(18)OD 952 cm-1) fitted with double Gaussians next to O3 nu3 (1034 cm-1), and H2CO, CO, CO2, H2O band areas (band strengths, Table 2) vs irradiation time -> CH3OH column densities, first-order kinetic rate constants kr (~1e-4 s-1, no temperature dependence 9-24 K) and ~65 % CH3OH branching ratio of O(1D) insertion into CH4",
    source_file="1134664.pdf (Bergner, Oberg & Rajappan 2017 ApJ 845:29, arXiv:1707.01120); IR_01.txt-IR_28.txt (one file per experiment of Table 1: wavenumber + absorbance columns headed by irradiation time in min), README.txt",
    confidence=0.9,
)

R["154446"] = dict(
    modality="UV-Vis absorption spectroscopy of the iron oxide (Fe3O4) nanoparticles used as light-absorbing shell component of Bacillus thuringiensis colloidosomal microcapsules (single supporting spectrum)",
    spectral_range_original_min=200, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=601, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=1,
    num_spectra=1,
    num_spectral_values=601,
    spectral_target_relationship="Broad absorbance of Fe3O4 nanoparticles across 300-900 nm (maximum ~440 nm) -> justification of the opaque, light-resistant colloidosome wall that protects encapsulated B. thuringiensis spores/crystals from UV degradation; main results are bioassay and field larval counts",
    source_file="154446.xml (Bashir, Claverie, Lemoyne & Vincent 2016 PeerJ 4:e2524, doi:10.7717/peerj.2524); 'UV-VIS absorption of Fe NP/Fe nanoparticles.xlsx' (sheet Fe2O3: wavelength, Abs); other files: 4 field/bioassay xlsx, AFM (.000/.002 Nanoscope), DLS and DSC PDFs, microscopy jpg/bmp/tif",
    confidence=0.6,
)

R["3235827"] = dict(
    modality="NIR transmission spectroscopy (CDI NIR-128L, 904-1707 nm, halogen lamp, 5 mL quartz cuvette) of paprika hydroponic nutrient solutions + VIS-NIR (Ocean Optics USB2000, 299-990 nm) and Tecan plate-reader UV-Vis (250-1000 nm) absorbance",
    spectral_range_original_min=250, spectral_range_original_max=1707, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (CDI NIR 904-1707 nm, 804 pts; USB2000 0.34 nm, 2,046 pts; Tecan 1 nm, 751 pts)",
    num_samples=80,  # nutrient solutions with PO4 1.6-1,378 mg/L (56 calibration + 24 validation)
    num_spectra=408,  # CDI raw + absorbance (82 each incl. 'Nothing'/'Empty' references), USB2000 raw + absorbance (82 each), Tecan 80
    num_spectral_values=527480,
    spectral_target_relationship="NIR intensity/absorbance (PO4 bands 930-960 and 1020-1120 nm) with moving-average, SNV and MSC preprocessing -> PLSR/PCR of phosphate concentration (R2 <= 0.64); 11 PCR scores fused with EMF of three cobalt electrodes in a PC-NN (ANN) model -> PO4 R2 0.89, RMSE 119.5 mg/L on 24 test samples",
    source_file="3235827.xml (Jung, Kim, Kim, Choi, Kim & Park 2019 Sensors 19:2596, doi:10.3390/s19112596); Total_spectra.xls (sheets Sheet1 reference K/NO3/PO4, USB2000, CDI_nir, AbsorptionUSB2000, AbsorptionCDI, Tecan; samples as columns with K/NO3/PO4 header rows); cobalt_3.xlsx (PO4 + EMF of 3 cobalt electrodes)",
    confidence=0.85,
)

R["3332899"] = dict(
    modality="Transmission FTIR spectroscopy (Bruker Vertex 70v) of layered and co-deposited NH3/HCOOH interstellar ice analogues during isothermal holds and warm-up (14-240 K)",
    spectral_range_original_min=599.677, spectral_range_original_max=3999.13, spectral_range_original_unit="cm-1",
    num_spectral_channels=7053, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=19,  # experiments 4-7 and 10-24 of Table 1 (TPD experiments 1-3 and step experiments 8-9 not deposited)
    num_spectra=1042,  # 39-129 spectra per experiment, columns labelled '<time>min_<T>K'
    num_spectral_values=7349226,
    spectral_target_relationship="Growth of NH4+ HCOO- salt bands (HCOO- nu2 1573 cm-1 and 1346 cm-1, Gaussian-fitted 1320-1600 cm-1) vs time at 15-140 K -> two-step kinetic model: proton-transfer barrier 70 +/- 30 K (A 1.4e-3 s-1) and diffusion-limited pre-reaction barrier 770 +/- 110 K; NH3/HCOOH column densities from band strengths",
    source_file="3332899.pdf (Bergner, Oberg, Rajappan & Fayolle 2016 ApJ 829:85, arXiv:1608.00010); exp_04_IR.txt-exp_24_IR.txt (19 files: wavenumber + absorbance columns headed '<time>min_<temperature>K')",
    confidence=0.9,
)

R["3712368"] = dict(
    modality="Transmission micro-FTIR (Bruker Vertex 70 + HYPERION 3000, LN-MCT) and AFM-IR nanospectroscopy (Bruker Anasys nanoIR2-FS, contact mode, 4 QCL sources) of 4,000-5,000-year-old mineralised cellulosic textile fibres + SHG microscopy and synchrotron uCT image stacks",
    spectral_range_original_min=800.272, spectral_range_original_max=4001.568, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1 (u-FTIR)",
    sampling_interval=0.964, sampling_interval_unit="cm-1 (u-FTIR; AFM-IR 902-1900 cm-1 at 1 cm-1; chrysocolla reference 1.93 cm-1)",
    num_samples=5,  # fibres from Gonur-Depe (GD), Nausharo (NS), Tello (AO, Louvre) + modern linen (LM) + chrysocolla reference
    num_spectra=21,  # 8 u-FTIR (4 raw + 4 thickness-corrected) + ~12 AFM-IR (NS zones 0-5) + 1 chrysocolla AFM-IR reference
    num_spectral_values=39993,  # approx.: 26,360 u-FTIR + ~13,600 AFM-IR values
    num_images=1785,  # SHG TIFF slices (d3-d27 z-stacks, polarisation series) + 4 uCT volumes
    spectral_target_relationship="Cellulose fingerprint bands (C-O-C/C-O 1000-1160 cm-1, O-H 3300-3400 cm-1), absence of hemicellulose C=O (~1735 cm-1), silicate Si-O (1020 cm-1) and hydroxy-silicate O-H shoulder (3620 cm-1, chrysocolla-like) at nano- and microscale, combined with SHG cellulose order and uCT attenuation -> three-step mineralisation/silicification pathway preserving cellulose in place",
    source_file="3712368.xml (Reynaud, Thoury, Dazzi, Latour, Scheel, Li, Thomas, Moulherat, Didier & Bertrand 2020 PNAS 117:19670, doi:10.1073/pnas.2004139117); FTIR/Raw Spectra and Corrected Spectra (AO, GD, LM, NS txt), AFM-IR/ (Chrysocolla.txt, NS_Zone0-5.txt), SHG/ d3-d27 TIFF z-stacks with info.txt, Tomography/ 4 uCT TIFF volumes (1 GB)",
    confidence=0.75,
)

R["3723806"] = dict(
    modality="UV absorption spectroscopy in 96-well plates (BioTek PowerWave HT plate reader) of nucleosides and nucleobases in alkaline solution for spectral-unmixing reaction monitoring of nucleoside phosphorylase reactions",
    spectral_range_original_min=250, spectral_range_original_max=350, spectral_range_original_unit="nm",
    num_spectral_channels=101, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=40,  # reference compounds (nucleosides 1-39 and their bases)
    num_spectra=424,  # approx.: 40 reference spectra + 4 plates x 96 wells; 5 further Gen5 plate exports (txt) not counted
    num_spectral_values=42824,
    spectral_target_relationship="Blank-corrected spectra normalised at the nucleoside/nucleobase isosbestic point and fitted as linear combinations of pure reference spectra (lmfit least squares, 250 nm to compound-specific upper limit) -> molar fractions / conversion of base cleavage by pyrimidine and purine nucleoside phosphorylases, validated against HPLC",
    source_file="3723806.xml (Kaspar, Giessmann, Neubauer, Wagner & Gimpel 2019 Methods Protoc. 2:60, doi:10.3390/mps2030060 - original assay paper; the deposit supports the 2020 update 'Updating and Extending an UV/Vis Spectroscopy-Based Assay...'); Reference_Spectra/ 40 csv (Wavelength, Abs); Data_for_Figures/ 4 plate Spectrum.tsv (wavelength x A1-H12), Well_IDs.tsv, 5 Gen5 txt exports, FEK140/FEK180 condition + results csv; Supporting Info PDF and Notes PDF",
    confidence=0.75,
)

R["3908210"] = dict(
    modality="NIR spectroscopy of dried, ground organic wastes and plant biomass (miscanthus, sorghum) on three spectrometers: Buchi NIRFlex N-500 FT-NIR (reflectance, cm-1), FOSS NIRSystem 5000 (absorbance, nm), Thermo ANTARIS II FT-NIR (absorbance, cm-1)",
    spectral_range_original_min=999.9, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    sampling_interval=2, sampling_interval_unit="nm (FOSS 1100-2498 nm, 700 pts); Buchi 4000-10000 cm-1 at 4 cm-1 (1,501 pts); ANTARIS 3999.6-10001.0 cm-1 at 3.86 cm-1 (1,557 pts)",
    spectral_resolution=4, spectral_resolution_unit="cm-1 (Buchi; ANTARIS 3.86 cm-1; FOSS 2 nm)",
    num_samples=127,  # 92 transfer-set + 35 validation-set (11 sorghum, 24 miscanthus) samples
    num_spectra=315,  # averaged spectra: Buchi 92+35, FOSS 71+35, ANTARIS 53+29
    num_spectral_values=392501,
    spectral_target_relationship="Paired spectra of the same samples on two instruments -> six Piecewise Direct Standardisation (PDS, window 7) transfer models (transform matrices) between Buchi, FOSS and ANTARIS after unit/absorbance conversion and SimulFilter interpolation (ChemFlow) -> inter-laboratory calibration transfer for organic-matter composition prediction; validated on an independent set",
    source_file="3908210.xml (Chauvergne, Latrille, Rossard, Bonnal, Bastianelli, Griveau, Mechin, Jacquemot, Reymond & Carrere 2020 Data in Brief 31:106264, doi:10.1016/j.dib.2020.106264); 6 raw .tabular (TSV, samples x wavenumbers/wavelengths: transfer and validation sets per instrument), Appendix 2 FOSS->Buchi transform matrix (1,276 x 1,276), Appendix 1/3 sample lists xlsx, 6 ChemFlow Galaxy history tar.gz (intermediate/transferred spectra, PDF plots), README.pdf",
    confidence=0.85,
)

R["3962243"] = dict(
    modality="FTIR transmission spectroscopy (Thermo Nicolet IR200, KBr pellets) of polyacrylonitrile fibres before/after cysteamine grafting and Ag-ion chelation (+ XRD, TGA, XPS in the same workbook)",
    spectral_range_original_min=399.19, spectral_range_original_max=3999.64, spectral_range_original_unit="cm-1",
    num_spectral_channels=1868, sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=3,  # PANF, SH-PANF, Ag-SH-PANF
    num_spectra=3,
    num_spectral_values=5604,
    spectral_target_relationship="Changes in -CN (2243 cm-1), ester C=O (1732 cm-1), N-H/O-H (3150-3700 cm-1), C-N (1389 -> 1384 cm-1), S-H (2424 cm-1) and S-S (520 cm-1) bands -> confirm cysteamine grafting on nitrile groups and Ag chelation by amino/sulfhydryl/disulfide groups of antibacterial Ag-SH-PANF",
    source_file="3962243.xml (Chang, Duan, Chen, Li, Huang, Tang, Pan, Deng, Zhao, Li & Zhao 2020 R. Soc. Open Sci. 7:200324, doi:10.1098/rsos.200324); single RSOS data-accessibility xls: Fig. 3 FT-IR (3 x wavenumber/%T), Fig. 4 XRD, Fig. 5 TG, Fig. 7 XPS, Fig. 1/8/9 Ag uptake, antibacterial and release data",
    confidence=0.85,
)

R["3962404"] = dict(
    modality="High-throughput UV-Vis absorption and photoluminescence emission spectroscopy (96-well plates) of CsPbBr3 / Cs4PbBr6 / CsPb2Br5 / layered nanocrystals synthesised and transformed under varied precursor ratios",
    spectral_range_original_min=250, spectral_range_original_max=700, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (absorbance 250-700 nm, 451 pts; PL emission 400-550 nm, 151 pts)",
    num_samples=2337,  # 1,351 syntheses + 986 transformation wells
    num_spectra=4674,  # absorption + emission spectrum per well
    num_spectral_values=1406874,
    spectral_target_relationship="Absorption spectra deconvolved into PbBr3-, Cs4PbBr6, CsPb2Br5, PbBr2, 1-4 monolayer platelets and CsPbBr3 components (fractions + R2) and PL emission vs Cs/Pb/Br/oleylamine/oleic acid concentrations -> high-throughput phase maps and weakly reversible transformation network of Cs-Pb-Br perovskite nanocrystals",
    source_file="3962404.xml (Imran, Caligiuri, Wang, Goldoni, Prato, Krahne, De Trizio & Manna 2018 JACS 140:2656, doi:10.1021/jacs.7b13477 - benzoyl-halide perovskite NC synthesis, not the dataset paper Dahl, Wang, Huang, Chan & Alivisatos 2020 JACS 142:11915, doi:10.1021/jacs.0c04997); CsPbBr_synthesis.csv (1,351 rows) and CsPbBr_transformations.csv (986 rows): absorbance 250-700, precursor concentrations, deconvolution fractions, emission e400-e550; processing notebook; Metadata.pdf",
    confidence=0.8,
)

R["3967205"] = dict(
    modality="Temperature-dependent polarised UV-Vis-NIR transmittance and reflectance micro-spectroscopy (Jasco MSV-370 microspectrophotometer) of scheelite BiVO4 single crystals through the ferroelastic transition",
    spectral_range_original_min=300, spectral_range_original_max=1500, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm ((110) crystal 1500-300 nm, 1,201 pts; (001) crystal 750-400 nm, 351 pts)",
    num_samples=2,  # (110)-oriented 360 um crystal 'Maria' and (001)-oriented 100 um crystal 'Martin-Christian'
    num_spectra=80,  # 52 (T and R, polarisation along b and c, 13 temperatures) + 28 (T, pol0/pol90, 14 temperatures)
    num_spectral_values=72280,
    spectral_target_relationship="Absorption edge (~2.4-2.6 eV) from transmittance/reflectance vs temperature (25-550 C) and light polarisation parallel/perpendicular to the principal axis -> thermochromic band-gap shift, dichroism decreasing from 0.2 eV (tetragonal) to 0.1 eV (monoclinic), controlled by the ferroelastic shear strain below Tc = 523 K",
    source_file="3967205.pdf (Hill, Weber, Lehmann, Leinen, Fiebig, Kreisel & Guennou 2020 APL Mater. 8:081108, arXiv:2004.10183, doi:10.1063/5.0011507); data_BVO110-Maria/ 52 JASCO txt (header + wavelength, %T or %R), data_BVO001-Martin-Christian/ 28 JASCO txt, Readme_BVO001.txt, Readme_BVO110.txt",
    confidence=0.9,
)

R["4002693"] = dict(
    modality="FTIR transmission spectroscopy (Bruker Tensor 27, 4 cm-1) of the flame retardant aluminium beta-(p-nitrobenzamide) ethyl methyl phosphinate (AlNP) (+ XRD, MCC, TG/DTG, DSC data in the same workbook)",
    spectral_range_original_min=599.83, spectral_range_original_max=3996.29, spectral_range_original_unit="cm-1",
    num_spectral_channels=1762, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=1,
    num_spectra=1,
    num_spectral_values=1762,
    spectral_target_relationship="N-H (3300, 1502, 1255, 756 cm-1), amide C=O (1700), NO2 (1550, 1338, 850), P=O (1155) and P-O-Al (1082, 968 cm-1) bands -> confirm synthesis of AlNP (with NMR/XRF) used to flame-retard ABS (UL-94 V0 at 25-30 wt%)",
    source_file="4002693.xml (Yang, Wang, Liu & Liu 2020 R. Soc. Open Sci. 7:200800, doi:10.1098/rsos.200800); spreadsheet.xls: 'Figure 3' FTIR (wavenumber, transmittance), 'Figure 4-XRD', 'Figure 5' MCC heat release, 'Figure 7-TG'/'DTG', 'Figure 9' DSC",
    confidence=0.8,
)

R["4054606"] = dict(
    modality="Laser-induced fluorescence (photoluminescence) spectroscopy at 325, 442 and 532 nm excitation of Smithsonian rare-earth-element orthophosphate reference crystals (UV-Vis-NIR emission, high resolution)",
    spectral_range_original_min=320.006, spectral_range_original_max=1079.865, spectral_range_original_unit="nm",
    sampling_interval=0.13, sampling_interval_unit="nm (3,297-5,898 pts per spectrum)",
    num_samples=12,  # CePO4, Ce:LuPO4, Ce:YPO4, DyPO4, ErPO4, EuPO4, HoPO4, NdPO4, PrPO4, SmPO4, TbPO4, YbPO4
    num_spectra=19,  # sample x excitation-laser combinations
    num_spectral_values=94785,
    spectral_target_relationship="Narrow 4f-4f (and Ce3+ 5d-4f) emission lines of each REE3+ in the orthophosphate host at three excitation wavelengths -> reference spectral library for LiF identification and mapping of REE in minerals/ores (hyperspectral drill-core and outcrop scanning); trace REE impurities (INAA) explain secondary lines",
    source_file="4054606.xml (Donovan, Hanchar, Picolli, Schrier, Boatner & Jarosewich 2002 J. Res. NIST 107:693, doi:10.6028/jres.107.056 - REE orthophosphate standard contamination paper, background reference only); 19 txt (index, WL nm, PL) named <REE>PO4_laser@<nm>_<power>_MC-slit@<um>_<exposure>.txt + 19 plot PDFs (some incl. INAA results) + _REEPhosphates_data-sheet.pdf",
    confidence=0.8,
)

R["4069308"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet 6700, 4 cm-1, 10 scans) of cellulose nanocrystals, graphene oxide and the CNCs-GO composite adsorbent for levofloxacin (+ XRD, EDS, XPS, BET data)",
    spectral_range_original_min=399.675, spectral_range_original_max=4000.12, spectral_range_original_unit="cm-1",
    num_spectral_channels=7469, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=3,  # CNCs, GO, CNCs-GO
    num_spectra=3,
    num_spectral_values=22407,
    spectral_target_relationship="O-H (3400 cm-1), C=O of GO carboxyls (~1730 cm-1), C=C (1620), C-O-C/C-O of cellulose (1060-1160 cm-1) bands of CNCs, GO and composite -> hydrogen-bonded CNC-GO 3D network explaining Levo-HCl adsorption (Sips isotherm, pseudo-second-order kinetics, >80 % removal at pH 4)",
    source_file="4069308.xml (Tao, Yang, Ma, Li, Du, Wei, Chen, Wang, Zhao & Deng 2020 R. Soc. Open Sci. 7:200857, doi:10.1098/rsos.200857); CNCs_FTIR.CSV, GO_FTIR.CSV, CNCs-GO_FTIR.CSV (wavenumber, %T); XRD txt (Bruker RAW4), EDS csv/docx, XPS xls, BET XLS, adsorption isotherm/kinetics/single-factor xlsx, Design-Expert .dxpx",
    confidence=0.85,
)

R["4086845"] = dict(
    modality="In-situ real-time ATR UV-Vis spectroscopy (Zeiss MCS621 immersion probe) of the acidic NaCl/HCl solution during dissolution of AA7150 Al-Zn-Mg-Cu alloy (+ ex-situ Agilent Cary 60, ICP-AES, STEM-EDX)",
    spectral_range_original_min=188.667, spectral_range_original_max=724.753, spectral_range_original_unit="nm",
    num_spectral_channels=256, sampling_interval=2.15, sampling_interval_unit="nm",
    num_samples=2,  # dissolution runs at 15 C (full spectra) and 45 C (252 nm absorbance trace)
    num_spectra=5293,  # time-series spectra over 24 h at 15 C; 45-RAW.CSV holds a single-wavelength trace of 5,317 points
    num_spectral_values=1360324,  # 1,355,007 spectral values + 5,317 trace values
    spectral_target_relationship="Absorbance growth at 252 nm (Cu-chloro complexes, confirmed by ICP-AES of Al-Cu binary alloys) vs immersion time -> apparent hours-long 'induction' period reflecting galvanic release of Cu after Al/Zn/Mg (EIS comparison); UV-Vis limited for total alloy dissolution rate",
    source_file="4086845.xml (Sun et al. 2020 R. Soc. Open Sci. 7:200461, doi:10.1098/rsos.200461); 15-revised.CSV (wavelength x 5,293 time spectra), 45-RAW.CSV (252 nm trace, 45 C), ICP_Al-Cu_and_7150.xls and sunqq-20191211.xls (ICP-AES), 2 STEM EDS-HAADF .emd spectrum images (Talos F200X, 536 MB)",
    confidence=0.75,
)

R["4134643"] = dict(
    modality="ATR-FTIR spectroscopy (Bruker Invenio, Platinum diamond ATR) of degummed hemp fibre through alkalisation, periodate oxidation, amination and quaternary-ammonium grafting (+ XPS, XRD, TGA in the workbook)",
    spectral_range_original_min=400.2125, spectral_range_original_max=3997.84, spectral_range_original_unit="cm-1",
    num_spectral_channels=2518, sampling_interval=1.429, sampling_interval_unit="cm-1",
    num_samples=5,  # HF, HF-OH, HF-CHO, HF-NH2, HF-GTA
    num_spectra=5,
    num_spectral_values=12590,
    spectral_target_relationship="Aldehyde C=O (~1730 cm-1) after NaIO4 oxidation, C=N/N-H (1650/1560 cm-1) after TETA amination and C-N+ quaternary ammonium (~1480 cm-1) after GTA grafting on cellulose O-H/C-O bands -> confirm stepwise covalent grafting of antibacterial HF-GTA (95.4 % E. coli, 99.6 % S. aureus)",
    source_file="4134643.xml (Chang, Duan, Huang, Chen, Li, Tang, Pan, Deng, Zhao & Li 2021 R. Soc. Open Sci. 8:201904, doi:10.1098/rsos.201904); single RSOS xls: Fig.6 FT-IR (5 x wavenumber/%T), Fig. 8 XPS, Fig. 9 XRD, Fig.10 TG, Fig. 2-5 reaction optimisation, Fig.11 antibacterial",
    confidence=0.85,
)

R["4281318"] = dict(
    modality="FTIR transmission (Thermo Nicolet 6700, KBr pellets) of graphite, GO and Ag/GO + UV-Vis absorption of ultrasound-synthesised Ag/GO nanomaterials (orthogonal design T1-T9)",
    spectral_range_original_min=300, spectral_range_original_max=25000, spectral_range_original_unit="nm",
    sampling_interval=0.5, sampling_interval_unit="cm-1 (FTIR 400-4000 cm-1, 7,201 pts); UV-Vis 300-597 nm at 1 nm (298 pts)",
    num_samples=11,  # graphite, GO, Ag/GO T1-T9 (T6 for FTIR)
    num_spectra=12,  # 3 FTIR + 9 UV-Vis
    num_spectral_values=24285,
    spectral_target_relationship="Ag surface plasmon resonance (~400-420 nm) intensity across ultrasound conditions (GO dose, AgNO3, time, power) and loss/shift of GO oxygen bands (C=O 1730, C-O 1050 cm-1) -> confirm AgNP reduction by ascorbic acid and anchoring on GO for antibacterial Ag/GO (inhibition zones vs S. aureus/E. coli)",
    source_file="4281318.xml (Zhu, Ni, Hu, Zhu, Cai, Liu, Gao, Yang & Liu 2021 R. Soc. Open Sci. 8:201744, doi:10.1098/rsos.201744); RAR archive: 2.FTIR/ 3 xls (graphite, GO, AgGO T6: wavenumber, intensity) + experimental detail txt; 4.UV-vis/UV-vis.xlsx (wavelength + T1-T9); 5.XPS/ 3 .opju + XPS-summary.xlsx; 6.XRD; 3.SEM EDS; 7.Zeta; 1.Antibacterial; README.txt",
    confidence=0.8,
)

R["4320109"] = dict(
    modality="Femtosecond UV-pump (265 / 199 nm) mid-infrared transient absorption spectroscopy of gas-phase Fe(CO)5 in the C-O stretching region (64-element MCT array), with CFOUR/Q-Chem computed vibrational frequencies and excited states",
    spectral_range_original_min=1790.3, spectral_range_original_max=2215.2, spectral_range_original_unit="cm-1",
    sampling_interval=5, sampling_interval_unit="cm-1 (64-pixel transient maps, ~5 cm-1/pixel; high-resolution spectra ~2.2 cm-1)",
    num_samples=1,  # Fe(CO)5 vapour at 1.5 Torr
    num_spectra=1336,  # approx.: 4 transient maps x ~329-331 pump-probe delays + 2 high-resolution spectra x 10 delays
    num_spectral_values=91400,  # approx.: 84,224 map values + ~7,200 high-resolution values
    spectral_target_relationship="Transient bleach of Fe(CO)5 C-O bands (2013/2034 cm-1) and rise of Fe(CO)4, Fe(CO)3, Fe(CO)2 bands (1880-2000 cm-1) and free CO vs delay -> sequential dissociation via short-lived Fe(CO)4 at 265 nm, prompt Fe(CO)3 within 0.25 ps at 199 nm plus a 15 ps component (intersystem crossing); assignments via CCSD(T)/EOM-CCSD(dT) frequencies and potential-energy cuts",
    source_file="4320109.pdf (Cole-Filipiak, Tross, Schrader, McCaslin & Ramasesha 2021 J. Chem. Phys. 154:134308, SAND2021-3148J); IP265/IP199 transient csv (row 0 = delays ps, column 0 = wavenumber; magic angle, with/without PFID filter) + 2 high-resolution spectra csv; 31 .out (CFOUR harmonic frequencies, Q-Chem orbitals/NTOs, EOM-EE-CCSD(dT) scans); README",
    confidence=0.75,
)

R["4429292"] = dict(
    modality="FTIR (Bruker TENSOR II, KBr) and Raman (HORIBA LabRAM HR Evolution, 532 nm) of fresh vs 2-year-aged graphene oxide + TG-FTIR evolved-gas infrared spectra (Netzsch STA 449F3, 650-4000 cm-1) during thermal decomposition",
    spectral_range_original_min=499.446, spectral_range_original_max=3998.426, spectral_range_original_unit="cm-1",
    sampling_interval=1.427, sampling_interval_unit="cm-1 (solid FTIR 2,453 pts); evolved-gas IR 649.9-3997.7 cm-1 at 1.93 cm-1 (1,737 pts); Raman 801-2000 cm-1",
    num_samples=2,  # GO (5 days) and GO-a (aged 2 years)
    num_spectra=743,  # approx.: 2 FTIR + 2 Raman + ~725 evolved-gas spectra (Fig.5 temperature contours) + 14 selected (Fig.6)
    num_spectral_values=1296879,  # approx., all numeric cells of the spectral sheets
    spectral_target_relationship="Oxygen functional groups (C=O 1720, C-O 1050, C-O-C 1220 cm-1, -CH2-/-CH3 2850-2920 cm-1, adsorbed water) and Raman ID/IG (0.87 -> 0.92) of fresh vs aged GO, and CO2/CO/H2O/SO2 evolved-gas absorbance vs temperature -> ageing raises C/O 1.96 -> 2.76, lowers decomposition peak 216 -> 195 C and activation energy 150 -> 134 kJ/mol",
    source_file="4429292.xml (Li, Lu, Yan, Yu, Zhao, Du & Niu 2021 R. Soc. Open Sci. 8:202309, doi:10.1098/rsos.202309); Data.xlsx (12 sheets: Fig.1 XRD/FTIR/Raman, Fig.2 AFM profiles, Fig.3 XPS, Fig.4 TG/Gram-Schmidt/MS, Fig.5(a)/(b) evolved-gas IR contour data, Fig.6 gas IR at selected temperatures, Fig.7 gas band intensities, Fig.8 DSC)",
    confidence=0.75,
)

R["4432613"] = dict(
    modality="FTIR transmission spectroscopy (Bruker VECTOR-22, KBr disc) of the amphoteric copolymer P(SS-co-AA-co-DMDAAC) coal-water-slurry dispersant (+ 1H NMR, XPS of coal)",
    spectral_range_original_min=399.253, spectral_range_original_max=3996.39, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=1,
    num_spectra=1,
    num_spectral_values=1866,
    spectral_target_relationship="O-H (3485), N+-CH2 (2924/2825), carboxyl C=O (1724), benzene ring (1570/1453, 650-900) and -SO3 (1041/1182 cm-1) bands -> confirm copolymerisation of sodium p-styrenesulfonate, acrylic acid and DMDAAC for the CWS dispersant",
    source_file="4432613.xml (Du, Zhang, Yang, Luo, Liu, Zhang, Zhang, Li & Zhu 2021 R. Soc. Open Sci. 8:201480, doi:10.1098/rsos.201480); Basic_data.xlsx: 'FTIR Spectrum' (wavenumber, T), '1H NMR Spectrum', 'XPS Spectrum', viscosity, zeta potential, stability, contact angle sheets",
    confidence=0.8,
)

R["4484620"] = dict(
    modality="UV-Vis absorption (Hitachi UV-3900H) of multicoloured anodised titanium sheets + micro-Raman (Renishaw inVia, 532 nm) of 20 V and 140 V films",
    spectral_range_original_min=200, spectral_range_original_max=1000, spectral_range_original_unit="nm",
    num_spectral_channels=801, sampling_interval=1, sampling_interval_unit="nm (UV-Vis); Raman 100-2000 cm-1, 665 pts",
    num_samples=13,  # anodisation voltages 20-140 V (10 min) and durations 10-300 min (100 V)
    num_spectra=15,  # 13 UV-Vis + 2 Raman
    num_spectral_values=11743,
    spectral_target_relationship="Number and position of visible interference/absorption peaks and absorption band edge vs anodisation voltage (20-140 V) and duration (10-300 min); Raman anatase modes at 140 V -> thicker TiO2 films absorb more visible light and give linearly increasing photocurrent under simulated sunlight",
    source_file="4484620.xml (Li, Chen, Wang & Chen 2021 R. Soc. Open Sci. 8:201778, doi:10.1098/rsos.201778); 'UV-Vis absorption.xlsx' (13 wavelength/absorbance pairs), Raman.xlsx (140 V, 20 V), xrd.xlsx, photocurrent and anodisation-current workbooks",
    confidence=0.8,
)

R["4538882"] = dict(
    modality="FTIR spectroscopy (Bruker Tensor 27, OPUS .dpt export) of carbonated flowerlike hydroxyapatite microspheres synthesised hydrothermally with 0.01-2 M EDTA (+ XRD, SEM, laser PSD)",
    spectral_range_original_min=399.249, spectral_range_original_max=3996.352, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=3,  # EDTA 0.01, 0.2, 2 M
    num_spectra=3,
    num_spectral_values=5598,
    spectral_target_relationship="Phosphate (PO4 nu3 1030-1090, nu1 960, nu4 565/603 cm-1), B-type carbonate (1420-1460, 872 cm-1) and O-H bands vs EDTA concentration -> confirm carbonated HA phase while EDTA controls microsphere size (tens of um -> few um)",
    source_file="4538882.xml (Yao, Qi, Qi, Ding, Chen & Wang 2021 R. Soc. Open Sci. 8:202148, doi:10.1098/rsos.202148); Data/Fig. 2 FTIR/ 3 .dpt (wavenumber, absorbance), Fig. 1 XRD txt, Fig. 3/5 FE-SEM tif, Fig. 4 PSD (LS13320 text exports named .xls), README.txt",
    confidence=0.85,
)

R["4543908"] = dict(
    modality="FTIR transmission spectroscopy of telechelic acetylene/azide precursors and click-chemistry (CuAAC) triazole polymer-network hydrogels (+ 1H NMR, TGA, swelling, DFT reactivity)",
    spectral_range_original_min=399.278, spectral_range_original_max=4000.497, spectral_range_original_unit="cm-1",
    num_spectral_channels=3735, sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=9,  # compounds 1-8 and hydrogel (Fig. 1b, 2a, 2b)
    num_spectra=9,
    num_spectral_values=33615,
    spectral_target_relationship="Disappearance of azide (~2100 cm-1) and terminal alkyne C-H (~3290 cm-1)/C=C (~2120 cm-1) bands and appearance of triazole/urethane bands -> confirm Cu-catalysed azide-alkyne cycloaddition network formation; supported by HOMO-LUMO DFT descriptors",
    source_file="4543908.xml (Ahmed, Kumer & Imran 2021 R. Soc. Open Sci., doi via Dryad 10.5061/dryad.5x69p8d1v); Figure_1b.xlsx and Figure_2a/2b.xlsx FTIR (wavenumber, %T), Figure_1c/3.xlsx 1H NMR, Figure_6a/6b swelling and TGA, SigmaPlot .JNB, ChemDraw .cdx, Table_1 DFT reactivity, supplementary docx",
    confidence=0.7,
)

R["4557142"] = dict(
    modality="UV-Vis absorption pH titrations (Agilent Cary 60 / Hitachi U-3900) and electronic circular dichroism (Applied Photophysics Chirascan, far-UV and Soret region, thermal unfolding) of heme chlorite dismutase CCld wild type and Q74E/Q74V variants (+ X-band CW-EPR, DSC, O2-evolution kinetics, X-ray data)",
    spectral_range_original_min=180, spectral_range_original_max=800, spectral_range_original_unit="nm",
    sampling_interval=0.5, sampling_interval_unit="nm (UV-Vis 800-200 nm, ~1,170 pts); ECD far-UV 180-260 nm and visible 260-500 nm",
    num_samples=3,  # CCld wt, Q74E, Q74V (pH 5-12)
    num_spectra=89,  # 50 UV-Vis pH-series spectra + 39 ECD files (spectra and single-wavelength unfolding curves)
    num_spectral_values=58356,  # UV-Vis only (ECD binary .dsx not counted)
    spectral_target_relationship="Soret (404-423 nm), Q-band and charge-transfer (508, 575, 641 nm) absorbance changes vs pH -> pKa of the alkaline transition (hydroxide/His-ligation, high- to low-spin) for wt vs Q74E/Q74V; far-UV (210 nm) and Soret ECD vs temperature -> secondary-structure and heme-cavity stability, complementing EPR spin states and DSC",
    source_file="4557142.xml (Schmidt, Serra, Mlynek, Pfanzagl, Hofbauer, Furtmuller, Djinovic-Carugo, Van Doorslaer & Obinger 2021 Biochemistry 60:621, doi:10.1021/acs.biochem.0c00910); PARACAT_WP3_20210217.rar: 02_UV-vis raw_<wt|Q74E|Q74V>_pH_titration.csv (wavelength/absorbance column pairs per pH), 03_ECD/ 39 Chirascan .dsx (pH 5/7/9, far-UV and visible), 01_EPR (Bruker .spc/.par + EasySpin .m/.mat), 04_activity (360 Oxygraph O2 csv), 05_DSC csv, 06_Xray mtz",
    confidence=0.75,
)

R["4589417"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet 6700, 4 cm-1, 32 scans) of urea-epichlorohydrin-modified peanut protein isolate, arachin and conarachin wood adhesives at five urea concentrations (+ TGA, viscosity, shear strength)",
    spectral_range_original_min=400.1569, spectral_range_original_max=4000.123, spectral_range_original_unit="cm-1",
    num_spectral_channels=7468, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=15,  # PPI (I0-I4), arachin (A0-A4), conarachin (C0-C4) adhesives at urea 0-4 levels
    num_spectra=15,
    num_spectral_values=112020,
    spectral_target_relationship="Amide I/II/III (1658, 1528, 1238 cm-1), C-O-C ether/ester (~1040-1150 cm-1) and N-H/O-H bands vs urea concentration -> protein unfolding and ECH cross-linking explain wet shear strength (maximum at 2 mol/l urea), mainly driven by the arachin fraction",
    source_file="4589417.xml (Chen et al. 2021 R. Soc. Open Sci. 8:202227); Data-RSOS-202227.rar: Data-FTIR.xlsx (3 sheets x 5 adhesives, wavenumber/%T pairs), Data-TGA.xlsx, Data-Wet shear strength.xls, Data-Apparent viscosity.xls, Data-Solid content.xls",
    confidence=0.85,
)

R["4594075"] = dict(
    modality="FTIR spectroscopy of phenolic hydrogen-bond donors, choline chloride and the resulting phenol-based deep eutectic solvents used for emulsification liquid-liquid microextraction of phenoxy acid herbicides",
    spectral_range_original_min=600, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3401, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=11,  # phenol, 2-CP, 3-CP, 4-CP, 3,4-DCP, their ChCl DESs, ChCl
    num_spectra=11,
    num_spectral_values=37411,
    spectral_target_relationship="Broadening/shift of phenolic O-H (3200-3400 cm-1) and C-O bands on mixing with choline chloride -> hydrogen-bond formation confirming DES synthesis (DES 1-6) before HPLC-UV (235 nm) determination of dicamba and MCPA in paddy-field water",
    source_file="4594075.xml (Mohamad Yusoff, Rahim, Mohammad, Yahaya & Miskam 2021 R. Soc. Open Sci., Dryad doi:10.5061/dryad.v15dv41v3); Nisa_et_al_Raw_Data.xlsx ('FTIR Raw' cm-1 + 11 %T columns; NMR placeholder; HPLC calibration/optimisation/validation sheets); Nisa_et_al_DATASET_Readme.txt",
    confidence=0.75,
)

R["4650475"] = dict(
    modality="2D-IR spectroscopy (100 kHz Yb laser, pulse-shaper, 2x32 MCT) and FTIR / Pg-minus-Pr difference FTIR of isotope-labelled cyanobacteriochrome AmI-g2 in D2O, plus UV-Vis absorption of the Pr and Pg photostates",
    spectral_range_original_min=999.1, spectral_range_original_max=3997.5, spectral_range_original_unit="cm-1",
    sampling_interval=1.29, sampling_interval_unit="cm-1 (FTIR, 2,333 pts); 2D-IR probe ~5.6 cm-1 (61 pts) x 32 pump points; UV-Vis 190-800 nm at 1 nm",
    num_samples=4,  # isotope-normal and 13C15N-labelled protein, each in Pr and Pg states
    num_spectra=144,  # 2 UV-Vis, 7 FTIR/difference, 4 2D-IR maps (32 pump slices each), diagonal cuts and CLS curves
    num_spectral_values=30491,
    spectral_target_relationship="Amide I' downshift (~50 cm-1) on 13C15N labelling isolates two unlabelled bilin carbonyl marker modes (ring A/D C=O); 2D-IR diagonal/anti-diagonal widths and centre-line-slope decay (200 fs vs 2 ps) in Pr vs Pg -> homogeneous vs inhomogeneous broadening reflecting hydrogen-bonding heterogeneity of the chromophore pocket",
    source_file="4650475.xml (Buhrke, Ruf & Hamm 2021 Phys. Chem. Chem. Phys. 23, doi:10.1039/d1cp00996f); Fig_1C UV-Vis txt (Pg, Pr), Fig_2A/2B FTIR and difference dat, Fig_2C/2D carbonyl-region dat, Fig_3 2D-IR maps (Pg/Pr at 200 fs and 2 ps), Fig_4 CLS and diagonal-cut dat",
    confidence=0.85,
)

R["4722747"] = dict(
    modality="Surface-enhanced Raman scattering (785 nm, 50x) of polystyrene (161/33 nm) and PET sub-micro/nanoplastics on PAH-coated glass with 14 or 46 nm gold-nanoparticle substrates (single spectra and maps) + UV-Vis (JASCO) of AuNPs and substrates",
    spectral_range_original_min=165.235, spectral_range_original_max=2778.39, spectral_range_original_unit="cm-1",
    num_spectral_channels=1024, sampling_interval=0.58, sampling_interval_unit="cm-1 (SERS windows ~690-1245 or ~1515-2035 cm-1; UV-Vis 1200-200 nm at 1 nm)",
    num_samples=12,  # PS161/PS33/PET at 10-100 ug/ml on 14/46 nm Au substrates + backgrounds and controls
    num_spectra=40,  # 36 Raman/SERS txt + 4 UV-Vis
    num_spectral_values=40870,  # approx.: 36,864 Raman + ~4,000 UV-Vis
    spectral_target_relationship="PS ring-breathing band at 1002 cm-1 (and PET 1615/1730 cm-1) SERS intensity and mapped distribution vs particle size, concentration (10-100 ug/ml) and AuNP size, compared with non-enhanced Raman -> enhancement factors and detection of sub-micro- and nanoplastics; AuNP LSPR (~520-530 nm) by UV-Vis",
    source_file="4722747.xml (Caldwell, Taladriz-Blanco, Rothen-Rutishauser & Petri-Fink 2021 Nanomaterials 11:1149, doi:10.3390/nano11051149); per-figure folders: SERS/Raman txt (background-subtracted, 1024 pts) + PNG plots, UV-Vis JASCO csv (AuNPs, substrates), SEM tif, DLS/zeta PDFs, sizing xlsx/csv",
    confidence=0.8,
)

R["4752282"] = dict(
    modality="FTIR spectroscopy (Bruker Tensor 27, KBr, 4 cm-1, 64 scans; variable temperature -170 to +250 C, Specac cell) of oleanolic and ursolic acids + DFT (B3LYP-D3/6-31G**, PCM n-octanol) computed IR spectra of monomers, dimers and tetramers",
    spectral_range_original_min=190.95, spectral_range_original_max=3996.304, spectral_range_original_unit="cm-1",
    sampling_interval=1.929, sampling_interval_unit="cm-1 (experimental, ~1,814-1,852 pts); computed spectra 190.95-3800 cm-1 at 0.95 cm-1 (3,800 pts, FWHM 10 cm-1)",
    num_samples=2,  # oleanolic acid, ursolic acid
    num_spectra=44,  # 2 room-temperature FTIR + 14 variable-temperature FTIR + 28 computed IR spectra (conformers/aggregates)
    num_spectral_values=136000,  # approx.
    spectral_target_relationship="Carboxylic nu(C=O) band (1690-1700 cm-1) deconvolved into 4 components and O-H stretching bands vs temperature, matched to Maxwell-Boltzmann weighted DFT spectra of H-bonded dimers/tetramers -> raw triterpenoid acids are blends of conformer clusters aggregated by hydrogen bonds",
    source_file="4752282.xml (Gomez-Pulido, Gonzalez-Cano, Dominguez, Heredia et al. 2021 R. Soc. Open Sci. 8:210162, doi:10.1098/rsos.210162); Raw_data.xlsx (Figure 2 computed + experimental, Figure 3 C=O deconvolution, Figure 8 tetramers, Figures S3/S5/S7/S9 computed aggregates, Figure S10 variable-temperature FTIR)",
    confidence=0.75,
)

R["4927462"] = dict(
    modality="UV-Vis absorption spectroscopy (Shimadzu UV-1800) of graphene quantum dots, green-synthesised Ag nanoparticles and the GQDs/AgNPs humidity-sensing nanocomposite (+ XPS, TEM sizes, sensor responses)",
    spectral_range_original_min=200, spectral_range_original_max=600, spectral_range_original_unit="nm",
    num_spectral_channels=401, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=3,  # GQDs, AgNPs, GQDs/AgNPs
    num_spectra=3,
    num_spectral_values=1203,
    spectral_target_relationship="GQD n-pi*/pi-pi* absorption (~230/330 nm) and Ag SPR (~420 nm) superposed in the nanocomposite -> confirm core/shell-like AgNPs/GQDs formation used for resistive humidity sensing (98 % response, 25-95 % RH)",
    source_file="4927462.xml (Chaloeipote, Samarnwong, Traiwatcharanon, Kerdcharoen & Wongchoosuk 2021 R. Soc. Open Sci. 8:210407, doi:10.1098/rsos.210407); Datasets.xlsx (Fig3a UV-Vis, Fig 3b-d XPS survey/C1s/Ag3d, Fig4 TEM size histograms, Fig5 sensor resistance/response vs RH and time)",
    confidence=0.8,
)

R["4932909"] = dict(
    modality="UV-Vis absorption spectroscopy (Shimadzu UV-2450) of TiO2, CdS/CdSe and CdS/Mn:CdSe quantum-dot-sensitised photoanodes (+ EDS, J-V and EIS data)",
    spectral_range_original_min=400, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=401, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=3,  # TiO2, CdS/CdSe, CdS/Mn:CdSe films
    num_spectra=3,
    num_spectral_values=1203,
    spectral_target_relationship="Visible absorption onset/red shift and higher absorbance of Mn2+-doped CdSe QDs vs undoped on TiO2 -> improved light harvesting, together with faster transport/slower recombination (EIS), raising QDSSC efficiency from 3.4 % to 4.9 %",
    source_file="4932909.xml (Zhang, Liu, Liu, Deng, Xiong & Tsai 2018 R. Soc. Open Sci. 5:171712, doi:10.1098/rsos.171712); Fig 3.xlsx UV-Vis (lambda, absorption for 3 films), Fig 2.xlsx EDS, Fig 4.xlsx J-V, Fig 5.xlsx EIS",
    confidence=0.8,
)

R["4933783"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet Avatar 360, KBr disc, 2 cm-1) of zeolites Na-A and Na-X synthesised from tablet-compressed, Na2CO3-calcined coal fly ash (+ XRD series, TGA)",
    spectral_range_original_min=399.212, spectral_range_original_max=4001.77, spectral_range_original_unit="cm-1",
    num_spectral_channels=1869, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=2,  # zeolite Na-A, zeolite Na-X
    num_spectra=2,
    num_spectral_values=3738,
    spectral_target_relationship="Framework T-O asymmetric/symmetric stretching (~1000, 660-750 cm-1), double-ring (D4R ~555 cm-1 for LTA, D6R ~560 cm-1 for FAU) and T-O bending (~460 cm-1) bands -> confirm phase-pure Na-A (LTA) and Na-X (FAU) from coal fly ash alongside XRD",
    source_file="4933783.xml (Hu, Gao, Liu, Zhang & Meng 2017 R. Soc. Open Sci. 4:170921, doi:10.1098/rsos.170921); RSOS-170921/Figure6.txt FT-IR (Na-A, Na-X); Figure1-5.txt XRD series; Figure7a/7b TGA; Figure1ai/8a/8b SEM tif; README",
    confidence=0.75,
)

R["4936575"] = dict(
    modality="UV-Vis absorption spectroscopy (PerkinElmer Lambda 750S) of nanoporous TiO2/Ti and BiVO4/TiO2/Ti photoanodes with BiOI electrodeposition times 10-1000 s, with Tauc (ahv)^2 band-gap fitting (+ XRD, EIS, i-t)",
    spectral_range_original_min=309, spectral_range_original_max=758, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (345-466 pts per spectrum)",
    num_samples=6,  # TiO2/Ti and BiVO4/TiO2/Ti for 10, 30, 100, 500, 1000 s
    num_spectra=6,
    num_spectral_values=2436,
    spectral_target_relationship="Visible absorption increasing with BiVO4 loading (deposition time) and Tauc-plot band gap lower than TiO2 -> enhanced visible-light harvesting and photocurrent (0.336 mA/cm2 at 0.6 V vs SCE for 1000 s) of the heterojunction for PEC water splitting",
    source_file="4936575.xml (Liu, He & Dong 2018 R. Soc. Open Sci. 5:180728, doi:10.1098/rsos.180728); 'UV data for different photoelectrode in Figure S3.xlsx' (6 sheets: wavelength, absorbance, hv, (ahv)^2), XRD Figure 1 xlsx, EIS data.xlsx, i-t data.xlsx",
    confidence=0.8,
)

R["4936773"] = dict(
    modality="UV-Vis-NIR absorption spectroscopy in microplates (plate reader, 300-990 nm) of seedless, seeded and HEPES gold nanostars: synthesis comparison, glucose-oxidase functionalisation, salt stability and colorimetric glucose sensing (+ TEM, DLS, EDS)",
    spectral_range_original_min=300, spectral_range_original_max=990, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (300-990 nm, 691 pts; glucose readings 400-900 nm at 2 nm)",
    num_samples=12,  # nanostar syntheses, GOx-modified/control AuNSs, salt and glucose concentrations
    num_spectra=40,  # approx.: well spectra across Figure 1, 3, 4 and 6 workbooks
    num_spectral_values=19700,  # approx.
    spectral_target_relationship="LSPR band position/intensity of branched AuNSs (~600-800 nm) vs synthesis route, GOx conjugation, NaCl concentration and glucose (H2O2-mediated reshaping/etching with AgNO3) -> stable seedless nanostars and naked-eye/UV-Vis glucose biosensing",
    source_file="4936773.xml (Phiri, Mulder & Vorster 2019 R. Soc. Open Sci. 6:181971, doi:10.1098/rsos.181971); per-figure folders: plate-reader UV-Vis xlsx (Well, wavelength rows, OD) for Figure 1, 3, 4, 6; DLS and EDS xlsx; 44 TEM jpg; agarose gel image; method PDF",
    confidence=0.65,
)

R["4946433"] = dict(
    modality="Single-reflection diamond ATR-FTIR spectroscopy (ABB Bomem MB102, Specac Golden Gate, 4 cm-1, 30 scans) of fresh and archived basidiospores and of pollen (Pinales, Fagales, Poales)",
    spectral_range_original_min=800.4, spectral_range_original_max=1899.7, spectral_range_original_unit="cm-1",
    num_spectral_channels=571, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=192,  # 71 spore + 121 pollen samples (fresh/archived spores 1961-2010)
    num_spectra=609,  # 192 archived/fresh spore spectra + 417 fresh pollen/spore spectra (technical replicates)
    num_spectral_values=347739,
    spectral_target_relationship="Lipid (1745), protein amide I/II (1650/1550), carbohydrate (1000-1200), sporopollenin/phenolic (1605, 1515) and chitin bands, EMSC-preprocessed and second-derivative -> PCA/HCA differentiation of pollen vs spores and of confamiliar/congeneric species; scattering signals reflect grain morphology; archived spores retain chemical composition",
    source_file="4946433.xml (Zimmermann, Tkalcec, Mesic & Kohler 2015 PLoS ONE 10:e0124240, doi:10.1371/journal.pone.0124240); ATRspectraArchivedSpores.txt (192 x 571), ATRspectraFreshPollenSpores.txt (417 x 571), Wavenumbers.txt (571), sample lists xlsx (species, marks, year/order)",
    confidence=0.9,
)

R["4949999"] = dict(
    modality="UV-Vis-NIR total transmittance (Jasco V-670 with integrating sphere) and micro-Raman (HORIBA HR800, 532 nm) of ultrasonic-spray-pyrolysed TiO2 thin films on window glass deposited at 250-450 C",
    spectral_range_original_min=200, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm (250 C film 200-2500 nm 1,151 pts at 2 nm above 800 nm; 350/450 C 200-2000 nm 1,801 pts); Raman 50-800 cm-1, 1,550 pts",
    num_samples=3,  # TiO2 films deposited at 250, 350, 450 C (annealed 500 C)
    num_spectra=6,  # 3 transmittance + 3 Raman (Tauc band-gap sheets derived from the transmittance)
    num_spectral_values=9403,
    spectral_target_relationship="Transmittance (~85 % visible) and Tauc indirect/direct band gaps from absorption coefficient, plus anatase Raman Eg mode (~144 cm-1) vs deposition temperature -> crystallinity 33-98 % and optical quality of transparent superhydrophilic TiO2 coatings that convert ~80 % MTBE in a plug-flow photoreactor",
    source_file="4949999.xml (Dundar, Krichevskaya, Katerski & Acik 2019 R. Soc. Open Sci. 6:181578, doi:10.1098/rsos.181578); 'UV-VIS spectroscopy.xlsx' (3 sheets wavelength/transmittance), 'Band gap Cal..xlsx' (Tauc calculations), 'Raman Spectroscopy.xlsx', XRD data.xlsx, XPS.xlsx, 'Degradation of MTBE.xlsx'",
    confidence=0.85,
)

R["4953516"] = dict(
    modality="Photoluminescence excitation/emission spectroscopy and luminescence decay (Edinburgh FLS980, red PMT) + FTIR (Nicolet NEXUS-670, KBr) of core-shell SiO2(600)@Tb(MABA-Si)L (L = dipy, phen) composites and the corresponding ternary Tb complexes - data only in Origin projects",
    sampling_interval_unit="nm (emission/excitation scans; exact grids not readable outside Origin)",
    num_samples=4,  # two core-shell composites and two ternary terbium complexes (dipy, phen)
    num_spectra=20,  # approx.: excitation, emission, IR spectra and decay curves across 7 Origin projects
    spectral_target_relationship="Tb3+ 5D4->7FJ emission (490, 545, 585, 620 nm) under ligand excitation; core-shell composites emit 2.49x (dipy) and 3.35x (phen) stronger with longer lifetimes than the complexes -> efficient antenna energy transfer via MABA-Si grafted on SiO2; IR confirms Si-O-Si grafting and Tb coordination",
    source_file="4953516.xml (Ma, Li, Zheng, Bao, Li, Feng, Yang, Qiao & Wu 2018 R. Soc. Open Sci. 5:171655, doi:10.1098/rsos.171655); Figuresnew/ 7 Origin .opj projects 'Result present in Fig 2/3/4/9/10/11/12' (IR spectra, FLS980 ExScan/EmScan workbooks, decay curves)",
    confidence=0.4,
)

R["4954607"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet NEXUS, OMNIC .SPA + CSV) of forward-osmosis membranes CTA-NW and TFC-ES used for lithium enrichment from salt-lake brine",
    spectral_range_original_min=399.199, spectral_range_original_max=4001.634, spectral_range_original_unit="cm-1",
    num_spectral_channels=1869, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.928, sampling_interval_unit="cm-1 (collected 649.9-3999.7 cm-1, zero-padded)",
    num_samples=2,  # CTA-NW and TFC-ES membranes
    num_spectra=2,
    num_spectral_values=3738,
    spectral_target_relationship="Cellulose triacetate ester C=O (~1740 cm-1) and C-O bands vs polyamide amide I/II (1660/1540 cm-1) and polysulfone support bands -> membrane surface chemistry/hydrophilicity explaining water flux and Li+ concentration factor (~3 for CTA-NW with MgCl2 draw)",
    source_file="4954607.xml (Li, Wang, Zhao, Yang & Zhong 2018 R. Soc. Open Sci. 5:180965, doi:10.1098/rsos.180965); 'Infrared spectrum data.rar': CTA-NW and TFC-ES as .CSV (wavenumber, %R), .SPA (OMNIC) and .TIF plots",
    confidence=0.8,
)

R["4956732"] = dict(
    modality="UV-Vis absorption spectra (benchtop spectrophotometer reference) of Griess-reagent nitrite standards used to validate a Raspberry-Pi camera photocolorimeter (HSV) for nitrite and pH",
    spectral_range_original_min=300, spectral_range_original_max=650, spectral_range_original_unit="nm",
    num_spectral_channels=351, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=13,  # water blank + nitrite standards 0.2-1.8 ppm
    num_spectra=13,  # replicate means (with standard error columns)
    num_spectral_values=4563,
    spectral_target_relationship="Absorbance of the azo dye formed by the Griess reaction (maximum ~540 nm) vs nitrite concentration (0.2-1.8 ppm) -> reference calibration for the camera-based HSV readout (R2 0.999, LOD 0.2 mg/l)",
    source_file="4956732.xml (Luka, Nowak, Kawchuk, Hoorfar & Najjaran 2017 R. Soc. Open Sci. 4:171025, doi:10.1098/rsos.171025); 'Results presented in figure .11 (Top) and (Botoom).xlsx' (wavelength + mean/error per standard), figure 7-10 result xlsx (HSV/pH comparisons), Photocolorimeter algorithm.py",
    confidence=0.7,
)

R["4958551"] = dict(
    modality="UV-Vis absorption spectroscopy (Shimadzu UV-3100PC, 10 mm quartz) of silver nanoparticle inks formed from AgNO3 W/O nanoemulsions with Tween 80/Span 80 at four AgNO3 concentrations (+ TGA, DLS, emulsion data)",
    spectral_range_original_min=200, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=601, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=4,  # AgNO3 0.10, 0.20, 0.30, 0.50 g/ml
    num_spectra=4,
    num_spectral_values=2404,
    spectral_target_relationship="Ag surface plasmon band (~400-420 nm) position/width vs AgNO3 concentration -> smaller particles (8.6-13.4 nm) at higher AgNO3, consistent with DLS; Tween 80 acts as reductant and stabiliser",
    source_file="4958551.xml (Hu, Ogawa, Kajiyama & Enomae 2020 R. Soc. Open Sci. 7:200296, doi:10.1098/rsos.200296); AgNPs_data.xlsx (Fig. 11 UV-Vis, Fig. 6/7 TG/DTA, Fig. 10 DLS, Fig. 2/3 emulsion data, Supplementary diameters)",
    confidence=0.8,
)

R["4959888"] = dict(
    modality="FTIR spectroscopy (PerkinElmer Spectrum 400, KBr, 16 scans) of methyl red and its biodegradation metabolites from Lysinibacillus fusiformis W1B6 static and shaking cultures",
    spectral_range_original_min=450, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3551, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=3,  # untreated dye, static-culture and shaking-culture metabolite extracts
    num_spectra=3,
    num_spectral_values=10653,
    spectral_target_relationship="Loss of azo N=N (~1600/1510 cm-1) and appearance of N-H/amine and carboxyl bands in metabolite extracts -> reductive azo cleavage of methyl red into 2-aminobenzoic acid and N,N-dimethyl-p-phenylenediamine (confirmed by HPLC/GC-MS), slightly faster under static culture",
    source_file="4959888.xml (Sari & Simarani 2019 R. Soc. Open Sci. 6:190152, doi:10.1098/rsos.190152); FTIR results/ 3 PerkinElmer PEDS ASCII .asc (Untreated dye, static, shaking); HPLC and GC-MS report PDFs; toxicity photographs; 16S sequence.fasta",
    confidence=0.85,
)

R["4959890"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet 6700, KBr 1:100, 4 cm-1, 32 scans) of peanut-meal wood adhesives unmodified and modified with urea and/or epichlorohydrin (+ XRD, TGA/DTG, shear strength)",
    spectral_range_original_min=399.6747, spectral_range_original_max=4000.123, spectral_range_original_unit="cm-1",
    num_spectral_channels=7469, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=4,  # adhesives A (PM), B (PM+U), C (PM+U+ECH), D (PM+ECH)
    num_spectra=4,
    num_spectral_values=29876,
    spectral_target_relationship="Amide I/II/III, N-H/O-H (3280 cm-1) and C-O-C ether (~1040-1100 cm-1) band changes -> urea unfolds peanut protein exposing reactive groups that ECH cross-links into a dense network (dry shear 0.53 -> 1.79 MPa, improved water resistance)",
    source_file="4959890.xml (Chen, Liu, Du, Liu, Xin & Liu 2019 R. Soc. Open Sci. 6:191154, doi:10.1098/rsos.191154); Data-RSOS-191154/ Data-FTIR.xls (4 x wavenumber/%T), Data-XRD, Data-TGA, Data-DTG, shear strength, viscosity, solid content xls",
    confidence=0.85,
)

R["4961775"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet 380, KBr) of tosyl-, ethylenediamine- and acryloyl-modified beta-cyclodextrin and the AM-beta-CD-DMDAAC flocculant - data only in an Origin project (+ XRD, TG and dye-adsorption Origin projects)",
    sampling_interval_unit="cm-1 (4000-400 cm-1 KBr spectra; grid not readable outside Origin)",
    num_samples=4,  # TsO-beta-CD, EDA-beta-CD, AM-beta-CD, AM-beta-CD-DMDAAC
    num_spectra=4,
    spectral_target_relationship="Appearance of tosyl S=O, amine N-H, acrylamide C=O/C=C and quaternary ammonium bands along the synthesis -> confirm the cationic cyclodextrin acrylamide flocculant that removes bromocresol green/thymol blue and cresol red/xylenol orange dyes (UV-Vis at 416/438 nm; Langmuir qmax 147 mg/g)",
    source_file="4961775.xml (Su, Wang, Sun, Liang, Meng, Wang & Li 2020 R. Soc. Open Sci. 7:191519, doi:10.1098/rsos.191519); 'Data_datasets/Dati Availability/' 13 Origin .opj: Figure 1 FT-IR spectra, Figure 2 XRD, Figure 4 TG, Figures 5-10 adsorption/kinetics/isotherms",
    confidence=0.45,
)

R["4962844"] = dict(
    modality="Transmission FTIR spectroscopy (Bruker Tensor 27, KBr, 4 cm-1, 128 scans) of heat-treated (1100 C) zinc and silicate co-substituted hydroxyapatites (+ Rietveld XRD, XRF, CASTEP DFT models)",
    spectral_range_original_min=374.172, spectral_range_original_max=3996.314, spectral_range_original_unit="cm-1",
    num_spectral_channels=1879, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=4,  # ZnSiHA 0.06/0.3, 0.06/0.5, 0.1/0.3, 0.1/0.5 (wt% Zn / Si)
    num_spectra=4,
    num_spectral_values=7516,
    spectral_target_relationship="Silicate Si-O bands (~890, 500 cm-1), PO4 nu1/nu3/nu4 and weakened/shifted OH stretching (3572 cm-1) and libration (630 cm-1) vs Zn/Si content -> evidence for Zn and SiO4 co-substitution in phase-pure HA, supported by lattice expansion and DFT energetics",
    source_file="4962844.xml (Friederichs, Chappell, Shepherd & Best 2015 J. R. Soc. Interface 12:20150190, doi:10.1098/rsif.2015.0190); 'FTIR raw data.csv' (wavenumber + 4 ZnSiHA compositions), XRD raw data (Rietveld csv for 9 compositions, HA/TCP check), XRF raw data.csv, Modelling files (CASTEP outputs + CIF)",
    confidence=0.8,
)

R["4964244"] = dict(
    modality="FTIR spectroscopy (700-4000 cm-1) of H3PO4-pretreated coconut shell and palm kernel shell bioadsorbents after one-stage N2 and two-stage N2>Air physical activation (+ TGA, adsorption and BET tables)",
    spectral_range_original_min=700.16, spectral_range_original_max=4000.364, spectral_range_original_unit="cm-1",
    num_spectral_channels=1712, sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=4,  # CS and PKS after N2 75 min and N2>Air 105 min
    num_spectra=4,
    num_spectral_values=6848,
    spectral_target_relationship="Surface functional groups (O-H, C=O, aromatic C=C, P-O-C/Si-O ~1000-1100 cm-1) of activated carbons vs activation route -> silica removal and pore opening by the extra air stage, consistent with higher BET area (PKS 456, CS 479 m2/g) and methylene blue/iodine uptake",
    source_file="4964244.xml (Lee, H'ng, Paridah, Chin, Rashid, Maminski et al. 2018 R. Soc. Open Sci. 5:180775, doi:10.1098/rsos.180775); Book6.xlsx 'FTIR' (wavelength(cm-1) + 4 sample columns), Book7.xlsx TGA, Book1-5 adsorption/BET/yield tables",
    confidence=0.75,
)

R["4966542"] = dict(
    modality="UV-Vis absorption spectroscopy of cobalt cores and silver-nanoparticle-decorated cobalt nanocomposites (Co@AgNPs) - data only in an Origin project (+ XRD and VSM Origin projects, antibacterial/cytotoxicity tables)",
    sampling_interval_unit="nm (Cary-style 'Wavelength/Absorbance' workbooks; grid not readable outside Origin)",
    num_samples=4,  # S0 Co-core, S1-S3 with 0.01/0.1/0.2 g silver acetate
    num_spectra=4,  # approx.
    spectral_target_relationship="Ag surface plasmon absorption (~400-450 nm) growing with silver acetate amount on Co cores -> AgNP density on Co@AgNPs, which scales the antibacterial effect against E. coli and B. subtilis",
    source_file="4966542.xml (Kanwal, Raza, Riaz, Manzoor, Tayyeb, Sajid & Naseem 2019 R. Soc. Open Sci. 6:182135, doi:10.1098/rsos.182135); 'UV-vis data.opj' (workbooks SEH CORE, SEH A, SEH B: Wavelength, Absorbance), XRD Data.opj, VSM Data.opj, antibacterial and cytotoxicity xlsx",
    confidence=0.4,
)

R["4968178"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet 6700) of bamboo cellulose nanofibres before and after Fe(OH)3 loading for low-concentration phosphorus adsorption (+ adsorption/regeneration tables)",
    spectral_range_original_min=399.1991, spectral_range_original_max=4001.634, spectral_range_original_unit="cm-1",
    num_spectral_channels=1869, sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=2,  # CNFs, Fe(OH)3@CNFs
    num_spectra=2,
    num_spectral_values=3738,
    spectral_target_relationship="Cellulose O-H/C-O bands and new Fe-O/Fe-OH vibrations (~400-700 cm-1) after loading -> confirm ferric hydroxide immobilisation on CNFs (best FeCl3, Fe(OH)3:CNFs 1.5:1, liquid-N2 freeze-drying) used for phosphate removal and NaOH regeneration",
    source_file="4968178.xml (Luo, Liu, Chen, Wang & Zhang 2019 R. Soc. Open Sci. 6:190764, doi:10.1098/rsos.190764); datas/Fig.3-9.xlsx (identical workbooks: 'Fig. 3' FTIR wavenumber + 2 transmission columns, 'Fig. 4-9' adsorption, kinetics, regeneration)",
    confidence=0.75,
)

R["4970989"] = dict(
    modality="FTIR spectroscopy (Bruker TENSOR 27) of the PEG@MoS2 dispersive solid-phase extraction sorbent (+ BET, capillary zone electrophoresis DAD electropherograms at 254 nm)",
    spectral_range_original_min=399.234, spectral_range_original_max=3996.195, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=1,
    num_spectra=1,
    num_spectral_values=1866,
    spectral_target_relationship="PEG C-O-C/C-H bands and Mo-S vibrations (~470 cm-1) -> confirm PEG coating of hydrothermal MoS2 that enlarges surface area and enrichment of eight sulfonamides from milk before CZE (R2 > 0.990, recoveries 60.5-110.9 %)",
    source_file="4970989.xml (An, Wang, Ming, Li & Ye 2018 R. Soc. Open Sci. 5:172104, doi:10.1098/rsos.172104); RSOS.xls ('Figure4' FTIR wavenumber/transmittance, 'Figure5' BET isotherm, 'Figure6' extraction optimisation, 'figureS1-S4' CZE electropherograms vs buffer/pH/voltage)",
    confidence=0.8,
)

R["4983902"] = dict(
    modality="FTIR spectroscopy (OPUS .dpt + workbook) of silicone particles through MPS, polystyrene/PVP grafting and Candida rugosa lipase immobilisation, and of PVP/ethanol/toluene-treated lipase controls (+ XPS, XRD, TG, SEM)",
    spectral_range_original_min=399.232, spectral_range_original_max=3996.177, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, sampling_interval=1.929, sampling_interval_unit="cm-1",
    num_samples=11,  # SP, SP-MPS, SP-Pst, SP-PVP, SP-PVP@CRL + 6 supporting lipase/solvent controls
    num_spectra=11,
    num_spectral_values=20526,
    spectral_target_relationship="Si-O-Si/Si-CH3 silicone bands, C=O of MPS (~1720 cm-1), PVP amide C=O (~1660 cm-1) and lipase amide I/II after immobilisation -> confirm amphiphilic PVP grafting and CRL loading that raise activity/stability of the low-cost immobilised lipase",
    source_file="4983902.xml (Zhang, Deng, Li, Zheng, Wan, Zheng, Tang, Huang & Shi 2018 R. Soc. Open Sci. 5:172368, doi:10.1098/rsos.172368); data.rar: 'IR and TG.xls' (sheet IR: 5 wavenumber/intensity pairs; tg; XRD), 'supporting information-IR/' 6 .dpt (PVP, PVP-CRL, ethanol, ethanol-CRL, toluene, toluene-CRL), XPS xls, XRD txt, SEM tif+txt, performance xlsx",
    confidence=0.8,
)

R["4984607"] = dict(
    modality="High-throughput transmission FTIR spectroscopy (Bruker TENSOR 27 + HTS-XT, 384-well silicon microplates, 4 cm-1, 32 scans) of grass pollen from Poa alpina, Anthoxanthum odoratum and Festuca ovina grown under four temperature x nutrient regimes",
    spectral_range_original_min=499.5192, spectral_range_original_max=4000.01, spectral_range_original_unit="cm-1",
    num_spectral_channels=3631, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.964, sampling_interval_unit="cm-1",
    num_samples=380,  # unique species/population/condition/individual codes in the workbook
    num_spectra=1143,  # technical triplicates (379 samples x 3 + one sample x 6)
    num_spectral_values=4150233,
    spectral_target_relationship="Protein (amide I/II), lipid (1745, 2850-2925 cm-1), carbohydrate (1000-1200 cm-1) and sporopollenin bands, 2nd-derivative + EMSC preprocessed -> PCA/PLSR classification of species, populations and growth conditions; temperature drives protein vs lipid/carbohydrate levels (adaptive plasticity of pollen chemistry)",
    source_file="4984607.xml (Zimmermann, Bagcioglu, Tafinstseva, Kohler, Ohlson & Fjellheim 2017 Ecol. Evol. 7:10839, doi:10.1002/ece3.3619); 'Spectral data.xlsx' (sheet Spectra: 1,143 rows coded species/population/condition/individual/batch/replicate x 3,631 wavenumbers; sheet Name codes)",
    confidence=0.9,
)

R["4986863"] = dict(
    modality="FTIR spectroscopy (PerkinElmer Spectrum One, KBr pellets) of nano-Mg(OH)2 before/after Cry11Aa insecticidal protein loading + far-UV circular dichroism (Chirascan) of Cry11Aa free vs adsorbed",
    spectral_range_original_min=399.1989, spectral_range_original_max=3999.703, spectral_range_original_unit="cm-1",
    num_spectral_channels=1868, sampling_interval=1.9285, sampling_interval_unit="cm-1",
    num_samples=2,  # nano-Mg(OH)2 and Cry11Aa+nano-Mg(OH)2 (FTIR); Cry11Aa and Cry11Aa+Mg(OH)2 (CD)
    num_spectra=4,  # 2 FTIR + 2 CD (180-260 nm, 1 nm, 81 points)
    num_spectral_values=3898,  # 2 x 1,868 + 2 x 81
    spectral_target_relationship="Protein amide bands appearing on Mg(OH)2 (with O-H 3698 cm-1 of brucite) confirm Cry11Aa adsorption; CD (190-260 nm) changes indicate secondary-structure alteration of Cry11Aa after loading onto the nano-carrier",
    source_file="4986863.xml (Pan, Xu, Zheng, Huang, Li, Chen, Rao, Chen, Hong & Guan 2017 R. Soc. Open Sci. 4:170883, doi:10.1098/rsos.170883); data/data/FT-IR.xlsx (wavenumber, nano-Mg(OH)2, Cry+nano-Mg(OH)2 transmittance; last row 4001.6 cm-1 zero-padded), CD.xlsx (260-180 nm, Cry11Aa, Cry11Aa+MgOH); other xlsx: isotherm, kinetics, thermodynamics, BET, desorption, zeta potential",
    confidence=0.85,
)

R["4988092"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet iS10, KBr disc, 64 scans, 4 cm-1) of rutin, zein-sodium caseinate nanoparticles and rutin-loaded nanoparticles at different rutin dosages",
    spectral_range_original_min=649.9208, spectral_range_original_max=3999.809, spectral_range_original_unit="cm-1",
    num_spectral_channels=6949, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.4821, sampling_interval_unit="cm-1",
    num_samples=7,
    num_spectra=7,  # columns B-H; columns J-Q repeat the same spectra with vertical offsets for plotting
    num_spectral_values=48643,
    spectral_target_relationship="O-H stretch shift (~3430 cm-1) and amide I/II of zein/caseinate with rutin aromatic bands -> hydrogen bonding/hydrophobic interaction, no new covalent bonds; supports encapsulation of rutin in zein-SC nanoparticles with retained antioxidant activity",
    source_file="4988092.xml (Zhang & Han 2018 PLoS ONE 13:e0194951, doi:10.1371/journal.pone.0194951); 'FTIR Data.xls' (sheet '01TOU': wavenumber + 7 transmittance columns, then repeated wavenumber + 7 offset columns; unlabelled, Fig 3 A rutin, B ZP, C-F 0.05-0.20 g rutin-loaded ZP)",
    confidence=0.75,
)

R["4990766"] = dict(
    modality="Raman spectroscopy (Thermo DXR Raman microscope) and FTIR transmission (Nicolet iS50, on Si wafer) of RF reactive-magnetron-sputtered chromium oxide coatings at different deposition powers (+ XPS, XRD, EIS, Mott-Schottky, crack-spacing data), all deposited as PDF tables",
    spectral_range_original_min=200.8918, spectral_range_original_max=1997.9, spectral_range_original_unit="cm-1",
    sampling_interval=0.9643, sampling_interval_unit="cm-1",  # Raman; FTIR 3.857 cm-1
    num_samples=8,  # Raman 350/400/450/500 W; FTIR 300/400/500 W + bare silicon wafer
    num_spectra=8,
    num_spectral_values=4152,  # Raman 4 x 623 (200.9-800.6 cm-1) + FTIR 4 x 415 (401.1-1997.9 cm-1)
    spectral_target_relationship="Raman A1g (549 cm-1) and Eg (306, 352 cm-1) modes and FTIR Cr-O bands (548, 611 cm-1) plus Eu mode (411 cm-1) identify the coatings as Cr2O3, whose intensity grows with deposition power; relates phase purity to the corrosion stability and absence of Cr-ion release in Ringer's solution",
    source_file="4990766.xml (Oje & Ogwu 2017 R. Soc. Open Sci. 4:170218, doi:10.1098/rsos.170218); 18 PDF data tables: 'Electronic file for figure 1 Raman Spectra ...pdf' (Raman shift + 4 powers), 'figure 2 The FTIR spectrum ...pdf' (wavenumber + 3 powers + silicon wafer), Figure 3 XPS survey/Cr2p/O1s, Figure 5 XRD, Figures 6-19 electrochemistry and adhesion",
    confidence=0.75,
)

R["4990861"] = dict(
    modality="Skeletal FTIR spectroscopy (Bruker VERTEX 70, RT-DLaTGS, KBr pellets, 4 cm-1) of MnWOx/TiO2-SiO2 NH3-SCR catalysts with different SiO2 contents and Mn:W ratios (+ XPS, XRD, BET, H2-TPR raw data)",
    spectral_range_original_min=399.24035, spectral_range_original_max=3996.26087, spectral_range_original_unit="cm-1",
    num_spectral_channels=1866, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.9287, sampling_interval_unit="cm-1",
    num_samples=10,
    num_spectra=10,  # 10 OPUS files (LWZ-0, 0-2, 0-3, 5, 5-2, 10, 20, 20-2, 20-3, 20-4); 4 .dpt are exports of some of them (2nd column = offset copy)
    num_spectral_values=18660,  # approx. 10 x 1,866 (OPUS files assumed same axis as the .dpt exports)
    spectral_target_relationship="Ti-O-Ti (400-800 cm-1), Ti-O-Si (~950 cm-1) and Si-O-Si (1080 cm-1) skeletal bands and surface OH/NH4+ bands vs SiO2 content -> Ti-O-Si linkages and dispersion of MnWOx that improve SO2/H2O tolerance in low-temperature NH3-SCR",
    source_file="4990861.xml (Zhang, Lu & Lu 2019 R. Soc. Open Sci. 6:180669, doi:10.1098/rsos.180669); 'original data/FT-IR/' 10 Bruker OPUS binaries (LWZ-*.0, 25-point smoothed) + 4 .dpt exports (LWZ-10, LWZ-20-3, LWZ-20-4, LWZ-5-2); also XPS (Kratos text exports + pdf), XRD .rd/.xy, BET 3Flex XLS, H2-TPR xls",
    confidence=0.7,
)

R["4991547"] = dict(
    modality="FTIR spectroscopy (FTIR-650, Tianjin Gangdong) of electrospun polycaprolactone nanofibres, free 20(S)-protopanaxadiol and PCL/PPD nanofibres",
    spectral_range_original_min=399.193, spectral_range_original_max=4001.57, spectral_range_original_unit="cm-1",
    sampling_interval=1.9285, sampling_interval_unit="cm-1",  # pclppd/ppd; PCL file 0.964 cm-1 (3,736 points)
    num_samples=3,
    num_spectra=3,
    num_spectral_values=7474,  # 3,736 + 2 x 1,869
    spectral_target_relationship="PCL ester C=O (1725 cm-1) and CH2 bands plus PPD O-H (~3400 cm-1) and triterpene C-H bands in PCL/PPD fibres -> confirms PPD incorporation without chemical reaction, supporting sustained-release anti-tumour (Hep-2) nanofibre carrier",
    source_file="4991547.xml (Liu, Cheng, Feng, Li, Ye & Teng 2018 R. Soc. Open Sci. 5:180137, doi:10.1098/rsos.180137); 'ESM File/ESM File/ESM File4/' PCL.CSV, pclppd.CSV, ppd.CSV (wavenumber, %T; trailing zero rows); other ESM folders: SEM, contact angle, TGA, tensile, release, MTT, tumour data; README.docx",
    confidence=0.85,
)

R["4991801"] = dict(
    modality="UV-Vis absorption (Shimadzu UV-2450) and fluorescence emission/excitation-emission (Hitachi F-4500) spectroscopy of folic-acid-derived carbon dots and their quenching by aqueous nitrite at pH 7 and 5 (+ XRD), deposited only as Origin projects",
    spectral_range_original_unit="nm",
    num_samples=None,
    spectral_target_relationship="Absorption bands at 261 (C=C) and 343 nm (C=O); emission 440-475 nm (excitation 330-365 nm, best 355 nm) red-shifting with lower synthesis temperature; nitrite quenching follows Stern-Volmer I0/I - 1 = 0.046[Q] (R2 = 0.99) -> fluorescent nitrite sensor",
    source_file="4991801.xml (Lin, Ding, Zhang & Huang 2018 R. Soc. Open Sci. 5:172149, doi:10.1098/rsos.172149); 'CDs DATA/' 10 Origin .opj (fig1a XRD, Fig2a absorption, Fig2b-d 3D/excitation-dependent fluorescence, fig3a-b temperature/quantum yield, fig4a-b nitrite quenching pH 7/5, fig5a-b pH and Stern-Volmer, fig6 NaNO3 vs NaNO2 selectivity)",
    confidence=0.4,
)

R["4993576"] = dict(
    modality="FT-NIR diffuse reflectance spectroscopy (Bruker MPA, fibre-optic probe, InGaAs/PbS) of fresh sea cucumber (Apostichopus japonicus) body wall from different Chinese sea origins - representative original spectra",
    spectral_range_original_min=800.44463, spectral_range_original_max=2500.13516, spectral_range_original_unit="nm",
    num_spectral_channels=3439, spectral_resolution=2, spectral_resolution_unit="nm",
    sampling_interval=0.4944, sampling_interval_unit="nm",
    num_samples=62,  # representative subset: Rushan 15, Wanfangdian 20, Yantai 27 (of 189 samples, 9 origins in the paper)
    num_spectra=62,  # 61 text .dpt + RS-2.dpt which is actually an OPUS binary
    num_spectral_values=213218,  # 62 x 3,439
    spectral_target_relationship="NIR overtone/combination bands of water, lipids (C-H 1210/1730 nm), proteins (N-H) -> PLS model of total fat content (RMSEP 0.45%, r 0.90) with OPS wavelength selection, and PCA-Mahalanobis/SFRA identification of geographical origin (100% correct)",
    source_file="4993576.xml (Guo, Cai, Wang, Tang, Li & Zhao 2018 R. Soc. Open Sci. 5:170714, doi:10.1098/rsos.170714); 'representative original spectra/.../{RS,WDF,YT}/*.dpt' (wavelength nm, log(1/R)); README docx",
    confidence=0.85,
)

R["4994640"] = dict(
    modality="UV-visible absorption spectroscopy (Shimadzu UV-1800) of azo-guanidine compounds UA1, UA6, UA7 in 80% ethanol and their titration with salmon-testes DNA (+ cyclic voltammetry data)",
    spectral_range_original_min=200, spectral_range_original_max=1100, spectral_range_original_unit="nm",
    sampling_interval=2, sampling_interval_unit="nm",  # UA7 sets 211-800 nm at 0.5 nm (1,179 points)
    num_samples=3,  # compounds UA1, UA6, UA7 (+ DNA concentrations 0-140 uM)
    num_spectra=27,  # approx.: Fig 1 3 compounds; Fig 4 UA7 8 DNA levels + DNA; Fig 5 UA1 7 levels; Fig 6 UA6 8 levels
    num_spectral_values=19457,  # approx. 2x451 + 1,179 + 9x1,179 + 7x451 + 8x451
    spectral_target_relationship="Azo pi-pi* band (490-524 nm) hypochromism and blue shift with increasing DNA -> intercalative/groove binding constants 7.2e3, 2.4e3, 0.2e3 M-1 (UA1, UA6, UA7) and naked-eye colour-change DNA sensing (LOD 1.8-5.8 ng/ul)",
    source_file="4994640.xml (Altaf, Hashmat, Yousaf, Lal, Ullah, Holder & Badshah 2016 R. Soc. Open Sci. 3:160351, doi:10.1098/rsos.160351); 'Ataf Ali - Excell Data/': Figure 1.xlsx (UV-Vis of UA1/UA6/UA7), Figure 4.xlsx (UA7 + DNA titration; Sheet2/3 derived plots), Figure 5a and 5b.xlsx (UA1 + DNA), Figure 6.xlsx (UA6 + DNA), Figure 2_7_8.xlsx and new1 figur 10n.xlsx (cyclic voltammograms), Figure 9.png, Compound Structures.cdx",
    confidence=0.75,
)

R["4994852"] = dict(
    modality="FTIR absorption spectroscopy (PerkinElmer Spectrum 400) of sophoricoside solid forms (solvent-free form A, DMSO solvate B, pyridine/water solvate C) (+ PXRD, DSC, TGA raw files)",
    spectral_range_original_min=650, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3351, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=3,
    num_spectra=3,
    num_spectral_values=10053,
    spectral_target_relationship="O-H stretching (3600-3100 cm-1), C=O (~1630 cm-1) and fingerprint differences shifted by solvent-host hydrogen bonding -> identification of sophoricoside polymorph/solvatomorph forms",
    source_file="4994852.xml (Xing, Zhang, Gong, Du & Lu 2019 R. Soc. Open Sci. 6:181905, doi:10.1098/rsos.181905); 'Sophoricoside/Sophoricoside/IR/{A,B,C}/' PerkinElmer .sp (HJG-YLY, HJG-DMSO-BT, HJG-BD-S: 4000-650 cm-1, 1 cm-1, %T); PXRD Rigaku files + txt, DSC/TG Mettler raw '0' files",
    confidence=0.85,
)

R["4996322"] = dict(
    modality="Vis/NIR leaf reflectance spectroscopy (Ocean Optics USB4000, tungsten lamp, 45 deg fibre geometry, PTFE reference) of five hybrid rice varieties under six nitrogen fertiliser levels, leaves at four plant heights",
    spectral_range_original_min=281.786970417719, spectral_range_original_max=1114.32382364144, spectral_range_original_unit="nm",
    num_spectral_channels=1024, sampling_interval=0.8195, sampling_interval_unit="nm",
    num_samples=600,  # 5 varieties x 6 N levels x 5 plants x 4 leaves (paper)
    num_spectra=3780,  # approx.: columns across 35 workbooks (5 variety flag-leaf files x 270, 6 N-level flag-leaf files x 225, 24 N x position files x 45); the views partly overlap
    num_spectral_values=3870720,  # 3,780 x 1,024
    spectral_target_relationship="Green peak (550 nm), red absorption (670 nm) and red-edge (700-750 nm) reflectance -> 12 spectral indices (SR, NDVI, MCARI, TVI, MTVI...) with PLS estimate leaf chlorophyll (SPAD; RMSECV 0.506, R2 0.978, RPD 4.6); SVM on 450-850 nm discriminates varieties within N levels",
    source_file="4996322.xml (Zhang, Duan, Li, Zhao, Zhu, Fu, Peng, Zhao, Svanberg & Hu 2019 R. Soc. Open Sci. 6:191132, doi:10.1098/rsos.191132); 'data for publish/': {CY1000,LYPJ,YLY1,YLY2,YLY900}_Reflectance_flag leaf.xlsx, N1-N6_Reflectance_flag leaf.xlsx, N1-N6_R_P1-P4.xlsx (row 1 sample labels, col A wavelength), SPAD values.xlsx",
    confidence=0.75,
)

R["4997776"] = dict(
    modality="ATR-FTIR of four pyridine-containing polyimide films + transmission FTIR (KBr) of the PyDPM diamine monomer (Bruker Vector 22) and UV-Vis transmittance of the polyimide films (+ 1H NMR, XRD, TGA, DSC, DMA, dielectric data)",
    spectral_range_original_min=399.25172, spectral_range_original_max=3998.30342, spectral_range_original_unit="cm-1",
    sampling_interval=0.9644, sampling_interval_unit="cm-1",
    num_samples=5,  # PyDPM monomer + PyDPM-PMDA, -BPDA, -ODPA, -6FDA polyimides
    num_spectra=9,  # 4 ATR-FTIR (559.3-3698.4 cm-1, 3,256 points) + 1 FTIR monomer (3,733 points) + 4 UV-Vis (250-850 nm, 0.5 nm, 1,201 points)
    num_spectral_values=21561,
    spectral_target_relationship="Imide C=O (1779/1713-1731 cm-1) and C-N (1362-1373 cm-1) bands confirm complete imidisation; N-H 3323-3429 cm-1 of PyDPM; UV-Vis cut-off 313-366 nm and >73% T at 450 nm -> colourless, high-Tg polyimides for OLED substrates",
    source_file="4997776.xml (Cheng, Hu, Wu, Shi, Chen, Liu, Yuan, Mo & Zhao 2019 R. Soc. Open Sci. 6:190196, doi:10.1098/rsos.190196); data/data/: 'ATR FTIR-PIs.xlsx' (4 x Wavenumber/%T), 'FTIR-PyDPM.xlsx', 'UV-vis-PIs.xlsx' (4 x nm/%T); also 1H NMR (2), XRD, TGA, DSC, DMA, dielectric constant, HRLC-MS workbooks",
    confidence=0.85,
)

R["4998166"] = dict(
    modality="Raman spectroscopy (WITec alpha300, 488 nm, 50-3500 cm-1), FTIR and UV-Vis diffuse reflectance (Avantes AvaSpec-2048) of graphene oxide-TiO2 thin films sensitised with Bactris guineensis natural dye (+ XPS surveys, BET, XRD, TGA); optical spectra only in Origin projects",
    spectral_range_original_unit="cm-1",
    num_samples=None,
    spectral_target_relationship="Anatase Eg/B1g/A1g Raman modes (145, 195, 395, 515, 638 cm-1) plus GO D/G bands confirm composite formation and charge-transfer enhancement; FTIR verifies dye/GO functional groups; diffuse reflectance gives band-gap/visible absorption of sensitised films relevant to photocatalytic methylene-blue degradation",
    source_file="4998166.xml (Vallejo, Rueda, Diaz-Uribe, Grande & Quintana 2019 R. Soc. Open Sci. 6:181824, doi:10.1098/rsos.181824); 'data manuscript_2/': RAMAN_w.opj, IR.opj, Reflecttance.opj, xrd.opj, TGA.opj (Origin only); xps/*.xls (6 surveys, binding energy vs counts); Copy_BET/ BET, BJH, ISO csv + bmp",
    confidence=0.35,
)

R["4999466"] = dict(
    modality="Raman, FT-IR and UV-Vis diffuse reflectance spectroscopy (PerkinElmer Lambda 650, BaSO4 reference) of BiVO4/P25 heterojunction photocatalysts (+ XPS, XRD, MB degradation kinetics), deposited only as Origin projects",
    spectral_range_original_unit="nm",
    num_samples=6,  # BiVO4, P25, a-d BiVO4/P25 (0.05-0.2 g P25)
    spectral_target_relationship="Monoclinic BiVO4 V-O Raman/IR modes (~826 cm-1) with anatase P25 bands confirm the heterojunction; DRS absorption edge (~520 nm, Eg ~2.4 eV) extended visible absorption explains 85% MB degradation in 60 min under lambda > 420 nm",
    source_file="4999466.xml (Cai, Cheng, Xu, Wang, Xu & Li 2018 R. Soc. Open Sci. 5:180752, doi:10.1098/rsos.180752); 'date/date/' 14 Origin .opj: Raman.opj, 'FT-IR of BiVO4&P25 and p25.opj', 'BiVO4&P25,P25UV-vis.opj', XRD.opj, XPS (Bi 4f, C1s, O, Ti 2p, V2p, all), degradation/kinetics projects",
    confidence=0.35,
)

R["5001067"] = dict(
    modality="Raman spectroscopy (Thermo DXR, 532 nm) and FTIR (Nicolet iS10, KBr) of commercial coconut-shell activated carbon before/after H2O dielectric-barrier-discharge plasma treatment (+ BET, XPS C1s fits, electrochemistry)",
    spectral_range_original_min=399.187, spectral_range_original_max=3997.65429, spectral_range_original_unit="cm-1",
    sampling_interval=1.9284, sampling_interval_unit="cm-1",  # FTIR; Raman 0.964 cm-1
    num_samples=2,  # CSAC, HCSAC
    num_spectra=4,  # Raman 2 x 3,112 (500.4-3,500.1 cm-1) + FTIR 2 x 1,867 (399.2-3,997.7 cm-1)
    num_spectral_values=9958,
    spectral_target_relationship="Raman D/G band ratio (~1350/1590 cm-1) unchanged -> plasma preserves carbon structure; FTIR O-H/C=O/C-O bands increase -> oxygen functional groups introduced by H2O plasma, raising specific capacitance by 64.8% and rate capability",
    source_file="5001067.xml (Wang, Zhou, Chen, Chen & Liu 2019 R. Soc. Open Sci. 6:180872, doi:10.1098/rsos.180872); 'RSOS-data availability wangxin.xlsx' (sheets 'figure 3' Raman CSAC/HCSAC, 'figure 5' FTIR CSAC/HCSAC; 'figure 2' BET/DFT, 'figure 6' XPS C1s fits, 'figure 8' CV/GCD/EIS, 'figure 9' cycling)",
    confidence=0.85,
)

R["5001963"] = dict(
    modality="UV-Vis absorption (Varian Cary 5G), photoluminescence excitation/emission and ATR-FTIR (Bruker TENSOR 27, ZnSe) of riboflavin-doped salmon DNA thin films on fused silica (+ current-voltage data)",
    spectral_range_original_min=190, spectral_range_original_max=699.9, spectral_range_original_unit="nm",
    num_samples=6,  # SDNA (RF0) and RF 1, 3, 5, 7, 9 mM
    num_spectra=27,  # UV-Vis 6 (190-600 nm, 1 nm) + PLE 3 (250-470 nm) + PL 6 (400-700 nm) + PL 6 (500-700 nm) + FTIR 6 (599.8-3,996.4 cm-1, 1,762 points)
    num_spectral_values=49964,  # 6x411 + 3x2,201 + 6x3,054 + (5x2,000 + 1,999) + 6x1,762
    spectral_target_relationship="DNA 260 nm band and RF bands (367, 454 nm) vs [RF] decrease up to the critical doping ~5 mM then rise; PL intensity shows the reverse trend (energy transfer DNA->RF); FTIR peaks at 832, 960, 1733 cm-1 evidence RF groove/electrostatic binding",
    source_file="5001963.xml (Gnapareddy, Dugasani, Son & Park 2018 R. Soc. Open Sci. 5:171179, doi:10.1098/rsos.171179); 'RF-DNA Raw Data/': 'Figure 2(b)_Absorbance-Wavenumber.xlsx' (FTIR, raw + layered offset copies), 'Figure 4_Absorbance-Wavelength.xlsx' (UV-Vis + band intensities), 'Figure 5_PL data.xlsx' (PLE, PL, PL area/height), 'Figure 3_Current-Voltage.xlsx'",
    confidence=0.8,
)

R["5003525"] = dict(
    modality="UV-Vis absorption (Shimadzu UV-2700), fluorescence emission/excitation-dependent emission (Horiba FluoroMax-4) and fluorescence quenching/recovery titrations of N,Cl-co-doped carbon dots with Fe3+ and ascorbic acid; deposited only as Origin projects",
    spectral_range_original_unit="nm",
    num_samples=None,
    spectral_target_relationship="Absorption 274 nm (pi-pi*) / 282 nm (n-pi*), emission 400 nm (ex 323-326 nm) quenched linearly by Fe3+ (0.3-50 uM, LOD 95.6 nM) and restored by ascorbic acid (0.5-10 uM, LOD 137 nM) -> turn-off/on probe for serum and urine",
    source_file="5003525.xml (Li, Tang, Yu, Wang, Tu & Wang 2019 R. Soc. Open Sci. 6:181557, doi:10.1098/rsos.181557); 'raw data/raw data/' 11 Origin .opj (Fig 1b size histogram, Fig 2a UV-Vis/PL, Fig 2b excitation-dependent PL, Fig 3a-d stability/selectivity, Fig 4a-d Fe3+ and ascorbic acid titrations + calibration fits)",
    confidence=0.35,
)

R["5008813"] = dict(
    modality="FTIR spectroscopy (PerkinElmer Spectrum One) of untreated bamboo timber and bamboo coated with reduced graphene oxide/ZnO (+ XPS region scans and XRD patterns)",
    spectral_range_original_min=525.0337, spectral_range_original_max=4000.188, spectral_range_original_unit="cm-1",
    num_spectral_channels=7209, sampling_interval=0.4821, sampling_interval_unit="cm-1",
    num_samples=2,  # BT, ZnO-RGOBT
    num_spectra=2,
    num_spectral_values=14418,
    spectral_target_relationship="Reduced O-H/C=O bands of bamboo cellulose/lignin and Zn-O stretch (~500 cm-1 region) after RGO@ZnO hydrothermal coating -> confirms ZnO/RGO deposition responsible for improved mould resistance and antibacterial activity",
    source_file="5008813.xml (Wang, Li, Zhuang, Pan, Yu, Sun, Song, Jin & Jiang 2018 R. Soc. Open Sci. 5:180173, doi:10.1098/rsos.180173); FTIR/BT.CSV, FTIR/ZnO-RGOBT.CSV (wavenumber, %T); XPS/*.xls (Thermo K-Alpha survey + Zn2p/O1s/N1s/C1s), XRD/*.txt, 'mould record.xlsx'",
    confidence=0.85,
)

R["5010200"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet 6700, KBr, 4 cm-1, 32 scans) of octanohydroxamic acid and fine cassiterite conditioned with OHA with/without Ca2+, Mg2+, Fe3+ (+ XPS exports, zeta potential, flotation), FTIR only in Origin projects",
    spectral_range_original_unit="cm-1",
    num_samples=6,  # OHA, cassiterite in water, cassiterite + OHA, + Ca2+/OHA, + Mg2+/OHA, + Fe3+/OHA
    num_spectra=8,  # approx.: Figures 11-14, two spectra each
    spectral_target_relationship="Hydroxamate C=O/C-N/N-O bands of OHA chemisorbed on cassiterite weaken when CaOH+, MgOH+ or Fe(OH)3 occupy surface Sn sites -> explains depressed flotation recovery and contact angle at pH 6-12",
    source_file="5010200.xml (Ren, Qiu, Qin, Zhang, Li & Wei 2018 R. Soc. Open Sci. 5:180158, doi:10.1098/rsos.180158); 'Final original data and description/': Figure 2-17 .opj (Figures 11-14 FTIR), XPS DATA 1/2.xls (Sn3d, Ca2p, C1s, N1s, O1s, survey), XPS fitting process.docx, data description.docx, Figure 1 XRD png",
    confidence=0.35,
)

R["5012837"] = dict(
    modality="ATR-FTIR (PerkinElmer Spectrum 400, diamond GladiATR) and Raman spectroscopy (Horiba LabRAM ARAMIS, 633 nm) of TTCSZ/poly(acrylic acid) hybrid precursor fibres through cross-linking and pyrolysis to SiOCN (600-800 C) (+ 13C/29Si solid-state NMR, XPS, TGA, BET, viscosity)",
    spectral_range_original_min=600, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_samples=12,  # DCP, PAA raw/XL, TTCSZ-DCP (+XL), TTCSZ/PAA raw, XL, 600, 700, 800 C; pure TTCSZ 600-800 C
    num_spectra=16,  # FTIR 10 x 3,351 (650-4,000 cm-1, 1 cm-1) + Raman 5 x 1,386 (600-3,000 cm-1) + 1 x 854 (1,000-2,500 cm-1)
    num_spectral_values=41294,
    spectral_target_relationship="FTIR loss of vinyl/Si-H/C=O and growth of Si-O-Si/Si-N bands track cross-linking and polymer-to-ceramic conversion; Raman D/G bands (~1340/1590 cm-1) quantify free-carbon formation in carbon-rich SiOCN fibres vs pyrolysis temperature",
    source_file="5012837.xml (Ren, Gervais & Singh 2019 R. Soc. Open Sci. 6:190690, doi:10.1098/rsos.190690); FTIR/*.asc (PerkinElmer PEDS ASCII, 10 files), Raman/*.txt (6), NMR-ASCII/*.txt (13C CP/MAS, 29Si MAS), XPS/*.csv, TGA/*.txt (Netzsch), TTCSZ_PAA_800.XLS (ASAP 2460 BET), Viscosity/*.XLS, SEM tif",
    confidence=0.85,
)

R["5013544"] = dict(
    modality="Multiscale vibrational spectroscopy of conifer (Pinales) pollen: FTIR-ATR of ground and intact pollen, KBr-pellet transmission, FTIR microspectroscopy of multigrain and single grains (Bruker Equinox 55 + IRScope II), and Raman microspectroscopy (Horiba LabRAM HR800, 632.8 nm) of saccus and corpus regions",
    spectral_range_original_min=599.8495, spectral_range_original_max=4000.283, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",  # FTIR; Raman ~11 cm-1
    num_samples=15,  # 15 Pinaceae/Podocarpaceae species
    num_spectra=468,  # ATR ground 55, ATR intact 51, KBr 47, multigrain 106, single grain 86, Raman saccus 62, Raman corpus 61
    num_spectral_values=1164508,
    spectral_target_relationship="Lipid, carbohydrate, protein, carotenoid (Raman 1520/1155 cm-1) and sporopollenin phenolic bands -> consensus PCA links the seven methodologies; Cedrus differs by sporopollenin composition, Picea by higher carotenoids; bulk IR and Raman corpus give best taxonomic differentiation",
    source_file="5013544.xml (Bagcioglu, Zimmermann & Kohler 2015 PLoS ONE 10:e0137899, doi:10.1371/journal.pone.0137899); 'Datadyrad_PlosOne/': ZATG, ZATI (55/51 x 1,764), ZKBR (47 x 1,868), ZMGR, ZSGR (106/86 x 3,527), ZRMS, ZRMC (62/61 x 1,728) whitespace matrices; wavenumbers1.dat / wavenumbers2.dat store axes as ASCII character codes; README",
    confidence=0.8,
)

R["5014968"] = dict(
    modality="FTIR spectroscopy of palm-kernel-shell and coconut-shell bioadsorbents, non-treated vs H3PO4-pretreated and carbonised (+ TGA, BET isotherms, RSM iodine adsorption tables)",
    spectral_range_original_min=650, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3351, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=4,  # non-treated CS, non-treated PKS, pretreated CS, pretreated PKS
    num_spectra=4,
    num_spectral_values=14144,  # 2 x 3,721 (non-treated columns extend ~370 rows beyond the 650 cm-1 axis) + 2 x 3,351
    spectral_target_relationship="Loss of O-H/C-H/C=O lignocellulose bands and appearance of P=O/P-O-C (~1160-1000 cm-1) phosphate bridges after H3PO4 pretreatment + carbonisation -> explains developed micro/mesoporosity and higher iodine adsorption",
    source_file="5014968.xml (Lee, H'ng, Chin, Md Tahir, Rashid & Go 2019 R. Soc. Open Sci. 6:190667, doi:10.1098/rsos.190667); Book4.xlsx (column 'Wavelength' = wavenumber 4000-650 cm-1, %T for 4 samples); Book1 proximate analysis, Book2 CCD/RSM iodine, Book3 N2 isotherms, Book5 TGA",
    confidence=0.8,
)

R["5015841"] = dict(
    modality="FTIR spectroscopy (Jasco FT-IR, KBr pellets, 4000-400 cm-1) of quercetin, BSA, PLGA void nanoparticles, quercetin-loaded PLGA NPs and drug-protein surface-modified nanoformulations NF1/NF2 (+ DSC, TGA, release kinetics), FTIR only in Origin projects",
    spectral_range_original_unit="cm-1",
    num_samples=6,  # Q, BSA, void NPs, Q-NPs, NF1 (BSA-ADR), NF2 (His-MTX)
    num_spectra=6,  # one project per sample (FTIR-Q, -BSA, -VOID, -Q NANO, -NF1, -NF2)
    spectral_target_relationship="Retained PLGA C=O (1758 cm-1) and quercetin O-H/C=C bands with shifts confirm Q encapsulation; protein amide A (3062), amide I/II (1652/1531 cm-1) appear in NF1/NF2 confirming BSA-adriamycin / histone-mitoxantrone surface coating",
    source_file="5015841.xml (Saha, Kaushik, Das, Pal & Majumder 2016 PLoS ONE 11:e0155710, doi:10.1371/journal.pone.0155710); FTIR-Q.opj, FTIR- BSA.opj, FTIR-VOID.opj, FTIR-Q NANO.opj, FTIR-NF1.opj, FTIR-NF2.opj; DSC-*.opj, Release Kinetics.opj; TGA-1..3 xlsx + pdf",
    confidence=0.35,
)

R["5022580"] = dict(
    modality="FTIR spectroscopy (Thermo Nicolet Nexus, KBr 1:50) of astaxanthin, blank PLGA nanoparticles and astaxanthin-loaded PLGA nanoparticles (+ DSC, TG, XRD, DLS size, cell-assay tables and confocal images)",
    spectral_range_original_min=399, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_samples=3,  # AST-PLGA NP, PLGA NP, AST
    num_spectra=3,  # NP spectra 1,869 points (~1.93 cm-1); AST 7,468 points (~0.48 cm-1)
    num_spectral_values=11206,
    spectral_target_relationship="Astaxanthin conjugated C=C/C=O bands masked in AST-PLGA NP while PLGA ester C=O (~1750 cm-1) persists -> astaxanthin encapsulated (amorphous) in PLGA matrix without chemical reaction (EE 96.4%, DL 7.2%)",
    source_file="5022580.xml (Hu, Liu, Yan, Kong & Wei 2019 R. Soc. Open Sci. 6:191184, doi:10.1098/rsos.191184); 'Raw_data/Raw data/F.B.H-Figure3FTIRdata.csv.csv' (paired cm-1/%T columns for AST-PLGA NP, PLGA NP, AST); other CSVs: size, DSC, TG, XRD, MTT, ROS, JC-1, Tables 1-6; confocal/SEM/TEM tif",
    confidence=0.85,
)

R["5023642"] = dict(
    modality="ATR-FTIR (PerkinElmer Spectrum 400, diamond, 4000-450 cm-1) of sporopollenin, Sp-TDI, Sp-TDI-betaCD and magnetic MSp-TDI-betaCD sorbent (+ XRD, BET, VSM, HPLC optimisation data), FTIR only in an Origin project",
    spectral_range_original_unit="cm-1",
    num_samples=4,
    num_spectra=4,  # Fig 3 a-d
    spectral_target_relationship="Isocyanate N=C=O (2276 cm-1), C=O (1709), C-N (1230) bands after TDI grafting, their disappearance on betaCD coupling, and Fe-O (562 cm-1) after magnetisation confirm stepwise synthesis of the MSPE sorbent for NSAIDs",
    source_file="5023642.xml (Syed Yaacob, Kamboh, Wan Ibrahim & Mohamad 2018 R. Soc. Open Sci. 5:171311, doi:10.1098/rsos.171311); 'Sharifah Mohamad - Dataset/': 'IR MSp-TDI-CD.opj' (FTIR), XRD, BET, VSM, HPLC graph and MSPE optimisation .opj; ChemDraw .cdx schemes",
    confidence=0.35,
)

R["5078355"] = dict(
    modality="UV-Vis absorption spectroscopy of the photocatalyst [Cp*Ir(dppz)Cl]+ under different conditions (dark/light, with/without substrate) with differential spectra (+ fluorescence plate-reader screening intensities and NMR-derived time courses)",
    spectral_range_original_min=300.006, spectral_range_original_max=700.0296631, spectral_range_original_unit="nm",
    num_spectral_channels=401, sampling_interval=1.0, sampling_interval_unit="nm",
    num_samples=5,  # conditions A-E
    num_spectra=5,  # plus 2 difference spectra (D-C, E-C) in the same sheet
    num_spectral_values=2005,
    spectral_target_relationship="Absorption changes of the Ir-dppz complex upon blue-light irradiation with salsolidine (differential spectra D-C, E-C) indicate a reduced Ir/dppz species, supporting a flavin-oxidase-like mechanism with H2O2 generation for amine dehydrogenation",
    source_file="5078355.xml (Davis, Haussinger, Ward & Okamoto 2020 ChemCatChem 12:4512, doi:10.1002/cctc.202000488); 'Scheme 4a.xlsx' (wavelength 700-300 nm, A-E, D-C, E-C); 'Scheme 2d.xlsx' fluorescence intensities (ex 320/em 450 nm), 'Scheme 3b/3c.xlsx' concentration time courses",
    confidence=0.8,
)

R["5118920"] = dict(
    modality="UV-Vis absorption and electronic circular dichroism spectra of ortho-tetraphenylene-based helical 'Gelaender' molecules and enantiomers (+ 1H NMR FIDs), optical data only in Origin .opju projects",
    spectral_range_original_unit="nm",
    num_samples=2,  # compounds 1 and 2
    spectral_target_relationship="Mirror-image CD bands of separated enantiomers and UV-Vis absorption of the all-sp2 52-carbon helical architecture characterise its chirality and conjugation",
    source_file="5118920.xml (Dekkiche, Malincik, Prescimone, Haussinger & Mayor 2021 Chem. Eur. J., doi:10.1002/chem.202101968); 'Figure 4/Figure 4/Figure 4a-d.opju' (UV-Vis and CD, Origin 2019+); 'Figure 2/' Bruker TopSpin FIDs for compounds 1 and 2 + Mnova file",
    confidence=0.35,
)

R["5363483"] = dict(
    modality="Reflection-absorption infrared spectroscopy (RAIRS; Bruker Vertex 70v, MCT, 1 cm-1, 128 scans) of H2:CO:15N2 interstellar ice analogues (and isotopic/control ices) before and during 2 keV electron or Ly-alpha photon irradiation (+ TPD QMS and temperature logs)",
    spectral_range_original_min=599.784, spectral_range_original_max=4999.32, spectral_range_original_unit="cm-1",
    num_spectral_channels=9126, spectral_resolution=1, spectral_resolution_unit="cm-1",
    sampling_interval=0.4821, sampling_interval_unit="cm-1",
    num_samples=24,  # experiments 1-14, A1-A2, C1-C7 (ice compositions / processing types)
    num_spectra=92,
    num_spectral_values=839592,
    spectral_target_relationship="Growth of product bands (e.g. HCO, H2CO, CO2, C3O2, 15N-bearing species such as H15NCO/15NH3) and depletion of CO vs electron/photon fluence -> chemistry induced by cosmic-ray secondary electrons and UV photons in the H2-bearing CO-rich apolar ice layer; TPD-QMS confirms products",
    source_file="5363483 (Martin-Domenech, Maksyutenko, Oberg & Rajappan 2021 ApJ, 'Exploring the chemistry induced by energetic processing of the H2-bearing, CO-rich apolar ice layer'); per-experiment folders Exp1-Exp14, ExpA1-A2, ExpC1-C7: *_IR.dpt and *_IR_<N>minutes_irradiation.dpt (wavenumber, absorbance), *_TPD_QMS.asc/.txt, *_TPD_temperature.xls",
    confidence=0.85,
)

R["5392755"] = dict(
    modality="ATR-FTIR spectroscopy (Bruker Vertex 80V, diamond ATR) of cotton, polyester and silk knitted fabrics before and after corona discharge treatment (+ charge, filtration penetration data, thermal-imaging movies, SEM)",
    spectral_range_original_min=399.19, spectral_range_original_max=3997.7, spectral_range_original_unit="cm-1",
    num_spectral_channels=1867, sampling_interval=1.928, sampling_interval_unit="cm-1",
    num_samples=3,  # cotton, polyester, silk
    num_spectra=6,  # pre- and post-CDT
    num_spectral_values=11202,
    spectral_target_relationship="Unchanged ATR-FTIR band positions/intensities pre vs post corona discharge treatment -> CDT does not alter surface chemical bonds of fabrics, so electrocharging (ion adsorption) can be repeated without structural degradation",
    source_file="5392755.xml (Bandi, Ishizu & Kang 2021 Proc. R. Soc. A 477:20210062, doi:10.1098/rspa.2021.0062); {Cotton,Polyester,Silk}-{Pre,Post}CDT-FTIR.txt (Wavenumber (1/cm), ATR units); charge/penetration txt, SEM tif, MOV videos",
    confidence=0.85,
)

R["5513073"] = dict(
    modality="Computed (DFT) infrared emission spectra of interstellar polycyclic aromatic hydrocarbons, binned into a spectral histogram, used as machine-learning targets (random forest on ECFP molecular fingerprints)",
    spectral_range_original_min=0.2049, spectral_range_original_max=5376.6862, spectral_range_original_unit="cm-1",
    num_spectral_channels=323, sampling_interval=16.6455, sampling_interval_unit="cm-1",
    num_samples=4233,  # PAH molecules
    num_spectra=4233,
    num_spectral_values=1367259,
    spectral_target_relationship="Band intensities in the C-H stretch, C-C stretch and out-of-plane bending regions predicted from molecular fragments; random-forest feature importance reveals common fragments behind correlated astronomical UIE bands (e.g. 11.2/12.7 um) and gives a band-correlation map",
    source_file="5513073.pdf (Meng, Zhu, Kovacs, Liang & Wang, 'Machine learning interpretation of the correlation between infrared emission features of interstellar polycyclic aromatic hydrocarbons'); example_code/: Inputdata.json (4,233 molecules x 323 bins), Bins.json (324 bin edges, cm-1), Fingerprint_4.json (ECFP fragments), ID_list.pck, RF_example_code.py; Supporting_Information.pdf",
    confidence=0.7,
)

R["5525748"] = dict(
    modality="NIR transmission and reflectance spectroscopy of raw cow milk with MEMS Fabry-Perot spectrometers (Spectral Engines NIRONE 1.4, 2.0 transmission, 2.0 reflection, 2.5) in an on-farm milk-analyser prototype",
    spectral_range_original_min=1100, spectral_range_original_max=2450, spectral_range_original_unit="nm",
    sampling_interval=2, sampling_interval_unit="nm",
    num_samples=299,  # milk samples (6 milkings over 3 days, ~71 cows) each measured by 4 MEMS modules
    num_spectra=24000,  # 1,196 files x 20 consecutive scans; the 4 'N599_532' files hold two measurements (2 x 20); SE14 126 pts (1100-1350 nm), SE20 201 pts (1550-1950 nm, transmission + reflection), SE25 226 pts (2000-2450 nm)
    num_spectral_values=4523991,  # one SE20 scan row has 200 values
    spectral_target_relationship="Fat (C-H 1210/1725 nm, 2310 nm), protein (N-H) and lactose (O-H/C-O 2100 nm) absorptions -> PLS models; NIRONE 2.5 transmission meets ICAR at-line accuracy (fat RMSEP 0.21%, protein/lactose <= 0.11% w/w) vs Valio reference analysis",
    source_file="5525748.xml (Uusitalo, Diaz-Olivares, Sumen, Hietala, Adriaens, Saeys, Utriainen, Frondelius, Pastell & Aernouts 2021 Foods 10:2686, doi:10.3390/foods10112686); Spectra_<date>_<session>/N<cow>_{Multi SE14, Multi_new SE20, Reflection SE20, Multi SE25}.txt (row 1 wavelengths, 20 scan rows) + .sbm binaries; Measurement notes/*.xlsx; SmartFarm_Valio_reference_data.xls (fat, protein, lactose, TS, urea, SCC)",
    confidence=0.85,
)

R["5528912"] = dict(
    modality="NIR diffuse reflectance spectroscopy of microplastic (PE, PP, PS) extracts from compost/soil on stainless-steel filters with three spectrometers: Bruker MATRIX-F FT-NIR (benchtop), Spectral Engines NIRONE S2.0 (MEMS Fabry-Perot) and Si-Ware NeoSpectra (MEMS Michelson)",
    spectral_range_original_min=3919.12468, spectral_range_original_max=11995.49, spectral_range_original_unit="cm-1",
    num_samples=None,
    num_spectra=2674,  # MatrixF 792 + NeoSpectra 742 + NIRONE 742 + uncertainty sets MatrixF 200 + NIRONE 198
    num_spectral_values=2668038,  # 992 x 2,074 (MATRIX-F 4,000-11,995 cm-1) + 742 x 695 (NeoSpectra 3,919-7,690 cm-1) + 940 x 101 (NIRONE 1,550-1,950 nm, 4 nm)
    spectral_target_relationship="C-H overtone/combination bands of PE, PP, PS (e.g. 5500-6300 and 8200-8800 cm-1) after SG-derivative/normalisation -> PLSR identification and mass quantification of 1-10 mg microplastics (1 mg/g detectable) after NaCl flotation enrichment",
    source_file="5528912.pdf (Wander, Lommel, Meyer, Braun & Paul 2022 Meas. Sci. Technol. 33:075801, doi:10.1088/1361-6501/ac5e5f); MatrixF.xlsx, NeoSpectra.xlsx, NIRONE.xlsx (rows = spectra with metadata File/Compost/Size/PS/PP/PE/Date/Cal-Val/fractions, columns = wavenumbers/wavelengths), *_uncert.xlsx; notebooks (.ipynb/.html), PLSR.py; TGA txt and design-of-experiment workbooks",
    confidence=0.85,
)

R["5555125"] = dict(
    modality="UV-Vis absorption (Shimadzu UV-2401PC) of fac-[Mn(CO)3Br(bpCO2)]2- and its H2O2/pyridine reactions, solution FTIR (Nicolet iS50, CaF2 cell) of carbonyl stretches, and fluorescence of the 7-OH-coumarin hydroxyl-radical probe (+ kinetic absorbance traces, EPR, CV, XRD, ICP)",
    spectral_range_original_min=200, spectral_range_original_max=850, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm",
    num_samples=None,
    num_spectra=192,  # UV-Vis 2 (FigS1) + 70 (FigS16) + 100 (FigS17); emission 5 (420-520 nm); FTIR 15 (399.2-4,001.6 cm-1, 1,869 points)
    num_spectral_values=132012,
    spectral_target_relationship="Decay of the MLCT band of the Mn carbonyl on H2O2 oxidation (initial-rate kinetics first order in [A] and [H2O2], pH dependent) and loss of nu(CO) bands (2022/1936/1920 cm-1) quantify ~2.5 equiv CO release; coumarin emission tests for hydroxyl radicals",
    source_file="5555125.xml (Barrett et al. 2021 R. Soc. Open Sci. 8:211022, doi:10.1098/rsos.211022); 'Suppinfo_RawData_RSOS_Revision_B.xlsx' sheets 'UV-Vis FigS1', '100mMpyridineFigureS16', '32mMH2O2afterpyrFigureS17', 'EmissionFigureS15', 'IRFigureS10' (15 WN/ABS pairs); kinetic time-trace sheets (single-wavelength absorbance vs time), EPR, CV, XRD, ICP",
    confidence=0.8,
)
