# Batch4 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (C:\Users\Admin\RAG\2\papers\<id>.pdf) + dataset (D:\Batch4_datasets\<id>_<title>[.zip]).
# Only the 29 records that contain spectra are kept; the 20 records without spectra were moved
# to D:\Batch4_no_spectra (see NO_SPECTRA below) and are not part of the batch4 parquet files.
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

# Records removed from Batch4 because the dataset holds no spectra (record id -> reason).
NO_SPECTRA = {
    "12787580": "NIRS.txt is only a chemometric classification-results table (and concerns Iberian pig sirloin/live animals, not the cocoa-bean paper)",
    "12789138": "quartz CPO table with FTIR integrated-absorbance water contents only + pptx animation",
    "13344265": "soil chemistry / macroinvertebrate tables (xlsx)",
    "13382544": "1-page PDF with bee sampling design",
    "13382546": "1-page PDF ethics-committee report",
    "13843817": "colorimetric microscopy sRGB TIFF images of spheroids",
    "13845529": "IODP Exp 355 interstitial-water composite report (wet chemistry)",
    "13847711": "article PDF only",
    "13986868": "DFT (VASP/AMSET) band structures, DOS and transport outputs",
    "14013238": "meta-analysis effect-size table (csv + codebook)",
    "14015078": "IODP Exp 359 interstitial-water composite report (wet chemistry)",
    "14286491": "PDF appendix (abundance tables)",
    "14292781": "PDF with 7 FT-IR spectra as images only (no numeric data)",
    "14351146": "review article PDF only",
    "14606547": "IODP Exp 368 interstitial-water composite report (wet chemistry)",
    "14621914": "article PDF only",
    "14653475": "proteomics result tables, western blots and microscopy images",
    "14657903": "AIMD trajectories (FHI-aims outputs, extxyz) - no spectra files; 3 incomplete .part downloads",
    "14795603": "SiPM timing/IRF characterisation data (no wavelength axis)",
    "14832005": "truncated zip holding only the article PDF",
}

# ---------------------------------------------------------------------------
# IODP JOIDES Resolution shipboard data (papers = Proceedings volume front matter /
# expedition summary chapters; methods are standard JRSO shipboard procedures)
# ---------------------------------------------------------------------------
_PAPER = {
    349: "Vol. 349 front matter",
    355: "Vol. 355 front matter",
    356: "Expedition 356 summary",
    359: "Expedition 359 summary",
    368: "Expedition 367/368 summary",
    375: "Expedition 372B/375 summary",
}

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


_spec("13948209", "356", 356, {"ammonium": 148, "phosphate": 154}, 141, 10, "U1459-U1464", 866.4,
      "data_by_hole (10 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (14 xlsx calibration workbooks, 5 Cary .BSR + 5 Simple Reads .RSR reports)", "Cary 100")
_spec("14866404", "375", 375, {"ammonium": 157, "phosphate": 85, "silica": 124}, 163, 4, "U1518, U1520", 1019.46,
      "data_by_hole (4 csv); supplementary raw_data_files (34 Cary Advanced Reads csv, 32 .BAB, 31 *.xlsm calibration workbooks, 1519E sulfide xlsx, rtf)", "Cary 300",
      note="; README states Cary 100, raw reports say Cary 300")


def _rsc(rid, exp, vol, nspectra, nfiles, nholes, sites, depth_max, sensor, bands, lo, hi, values=None, step=2, conf=0.85):
    R[rid] = dict(
        modality=f"VIS diffuse reflectance spectroscopy and colorimetry (RSC) of split-core section halves ({sensor} + integrating sphere on SHMSL)",
        spectral_range_original_min=lo, spectral_range_original_max=hi, spectral_range_original_unit="nm",
        num_spectral_channels=bands, sampling_interval=step, sampling_interval_unit="nm",
        num_samples=nfiles,  # per-section-half normalised reflectance files
        num_spectra=nspectra, num_spectral_values=values or nspectra * bands,
        spectral_target_relationship=f"% reflectance spectra (white/dark-referenced) of sediment/rock core surfaces -> CIE XYZ, L*a*b*, chroma, hue vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}) for lithostratigraphy, cyclostratigraphy and hole-to-hole correlation",
        source_file=f"{rid}.pdf ({_PAPER[vol]}, Exp {exp}); RSC-README.txt; data_by_hole/*-RSC.csv; supplementary raw_data_files norm_*/raw_*_rsc.csv + *.RSC; configuration files",
        confidence=conf,
    )


_USB = "Ocean Optics USB4000-VIS (S/N RF52054)"
_rsc("13845594", "355", 355, 79138, 1534, 8, "U1456-U1457", 1108.89, _USB, 226, 400, 850)
_rsc("14015137", "359", 359, 130771, 2816, 20, "U1465-U1472", 999.915, _USB, 261, 380, 900)
_rsc("14606697", "368", 368, 73664, 1393, 11, "U1501, U1502, U1504, U1505", 920.92, "Ocean Insight QE Pro (S/N QEP00732)", 172, 390, 732,
     values=12901720)  # 72,318 spectra x 172 bands (2 nm) + 1,346 spectra x 344 bands (1 nm)
_rsc("14618483", "349", 349, 104146, 1409, 10, "U1431-U1435", 1007.87, _USB, 261, 380, 900)

# ---------------------------------------------------------------------------

R["12626814"] = dict(
    modality="FTIR transmission absorbance spectroscopy of modern tooth enamel in KBr pellets (grinding-curve method)",
    spectral_range_original_min=399.6748, spectral_range_original_max=4000.123, spectral_range_original_unit="cm-1",
    num_spectral_channels=7469, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=75,  # enamel specimens of 15 African ungulate species, each ground 3 times
    num_spectra=225,
    spectral_target_relationship="FWHM of the phosphate nu3 band (~1034 cm-1) and infrared splitting factor (IRSF) of the nu4 doublet (604/565 cm-1) over three successive grindings of the same pellet -> grinding curves (FWHM vs IRSF) as atomic-order proxy of enamel carbonate hydroxyapatite, used to pre-screen teeth for ESR/U-series dating; carbonate nu2/nu3 bands also present",
    source_file="12626814.pdf (Toffolo & Richard 2024 Sci. Data 11:890); FTIR spectra/ 225 *.CSV + 225 *.SPA (OMNIC originals); Enamel_grinding_curves.xlsx (IRSF/FWHM per spectrum); IRSF_FWHM.mac (OMNIC macro)",
    confidence=0.9,
)

R["12711013"] = dict(
    modality="Transmission FTIR absorbance spectroscopy of HCN-bearing interstellar ice analogues on a Ge window in UHV (deposition at 10 K and TPD warm-up series)",
    spectral_range_original_min=630.0164, spectral_range_original_max=4000.068, spectral_range_original_unit="cm-1",
    num_spectral_channels=27960, spectral_resolution=1, spectral_resolution_unit="cm-1",
    sampling_interval=0.1206, sampling_interval_unit="cm-1",
    num_samples=14,  # ice compositions (HCN with H2O, H2O:NH3, CO, CO2, CH3OH, benzene, aniline, pyridine at 1:8-1:32)
    num_spectra=76,
    num_spectral_values=2124963,  # 73 x 27,960 + 3 x 27,961 points
    spectral_target_relationship="HCN C-N stretch (~2100 cm-1), C-H stretch (~3100 cm-1) and bending (~820 cm-1) band positions/widths change with the surrounding ice matrix, dilution (1:8, 1:16, 1:32) and temperature (10-160 K warm-up) -> laboratory reference profiles for identifying HCN ice in JWST spectra; QMS-calibrated column densities",
    source_file="12711013.pdf (Ozhiganov et al. 2024, AASTeX draft 'Infrared Spectra of Solid HCN Embedded in Various Molecular Environments for Comparison with the Data Obtained with JWST'); 76 CSV (Wavenumber, Absorbance)",
    confidence=0.9,
)

R["12800065"] = dict(
    modality="Leaf VIS-NIR spectroscopy: reflectance, transmittance, absorbance and passive chlorophyll fluorescence (upward/downward) with a FluoWat leaf clip and two Ocean Insight QE Pro spectroradiometers, plus incident irradiance spectra",
    spectral_range_original_min=394.9, spectral_range_original_max=1021, spectral_range_original_unit="nm",
    num_spectral_channels=832,
    num_samples=143,  # tomato leaf samples (d0, d2, d4, d7, d14; 3 treatments x 5 replicates x 2-3 leaves), each measured at PAR300 and PAR1000
    num_spectra=2002,  # 286 leaf measurements x 7 spectral variables (PAR, PARf, R, T, A, Fup, Fdw); smoothed R/T/A copies not counted
    spectral_target_relationship="Leaf R, T, absorbance and fluorescence of tomato under control, water deficit and N deficit -> spectral pigment unmixing (effective absorbance of Chl a, Chl b, beta-carotene, xanthophyll '535-nm peak', anthocyanins, 500-780 nm), APAR by Chl a and fluorescence quantum efficiency (FQE); compared with HPLC pigments, gas exchange and PAM fluorescence (NPQ) for early stress diagnosis",
    source_file="12800065.pdf (Pescador-Dionisio et al. 2024 New Phytologist, doi:10.1111/nph.20253); 5 *_Leaf_Spec_Tomato_Stress.mat (PAR300/PAR1000 structs) + 5 *_Leaf_Fitting_*.mat + README PDFs; Active F.xlsx, HPLC Pigment data.xlsx, Physiological measurements.xlsx, VAZ RT-qPCR xlsx, light-curve txt",
    confidence=0.85,
)

R["12807801"] = dict(
    modality="Solution UV/Vis absorption, circular dichroism (CD), fluorescence and circularly polarised luminescence (CPL) spectroscopy of perylene bisimide foldamer stereoisomers (+ chiral HPLC-DAD chromatograms)",
    spectral_range_original_min=400, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=301, sampling_interval=1, sampling_interval_unit="nm",  # UV/Vis and CD 400-700 nm; emission 535-800 (266 pts); CPL 580-800 (221 pts)
    num_samples=5,  # (R,c)-, (S,t)-, (R,t)-, (S,c)-1 and ref-PBI
    num_spectra=18,  # 5 UV/Vis + 4 CD + 5 emission + 4 CPL
    num_spectral_values=4923,
    spectral_target_relationship="Excitonic absorption (molar extinction) and CD Cotton effects (delta-epsilon) in CHCl3 at 293 K distinguish cisoid/transoid diastereomers and R/S enantiomers (assignment by TDDFT); emission and CPL give g_lum; time-dependent chiral HPLC at 373 K gives the folding/interconversion barrier (116 kJ/mol)",
    source_file="12807801.pdf (Teichmann et al. 2024 Angew. Chem. Int. Ed., doi:10.1002/anie.202414069); anie.202414069_OriginalData.xlsx (sheets Figure 3, 4a, 4b, 5a, S13a, S13b, S15a); movie mp4",
    confidence=0.85,
)

R["12822668"] = dict(
    modality="MIR FTIR directional-hemispherical reflectance (gold integrating sphere) of polished basalt slabs, converted to emissivity by Kirchhoff's law; plus modelled R=100 planetary emission spectra",
    spectral_range_original_min=368.34347, spectral_range_original_max=7498.0075, spectral_range_original_unit="cm-1",
    num_spectral_channels=3698, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.9285, sampling_interval_unit="cm-1",
    num_samples=15,  # basaltic rock samples
    num_spectra=36,  # 15 rock reflectance + 4 gold-standard sessions + NIST D25A reference + 16 flux models (incl. blackbody)
    num_spectral_values=75206,
    spectral_target_relationship="Reflectance rh -> emissivity (1 - rh, 2-25 um): Christiansen feature and Si-O reststrahlen minima (8-12 um) track mineralogy (plagioclase, pyroxene, olivine, amphibole, serpentine from XRD) and bulk chemistry (XRF, e.g. wt% Al2O3); synthetic eclipse spectra/photometry test JWST MIRI LRS and filter detectability of geological diversity on rocky exoplanets",
    source_file="12822668.pdf (First et al. 2025 Nature Astronomy 9:370); First_CSV_Files: Rock Samples (Lab) 15 csv, Standard D25A (Lab) 5 csv, Flux Models 16 csv, READ ME.rtf; Fig. 1-4 source data; Supplementary Tables/Figures; 15 XRD WPF reports",
    confidence=0.9,
)

R["13126540"] = dict(
    modality="UV-Vis spectroscopy with diffuse reflectance accessory of AuCu bimetallic nanostructures on Ti/TiO2 (+ XPS core-level spectra and photoelectrochemical linear voltammetry)",
    spectral_range_original_min=300, spectral_range_original_max=1000, spectral_range_original_unit="nm",
    num_spectral_channels=701, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=9,  # 10AuCu, 5Au5Cu, 5Cu5Au layers annealed at 200/400/600 C
    num_spectra=13,  # 9 UV-Vis + 4 XPS regions (Au4f, Cu2p, O1s, Ti2p)
    num_spectral_values=7377,
    spectral_target_relationship="Annealing temperature drives dewetting of Au/Cu films into AuCu nanomosaics -> plasmonic absorption shifting/broadening (430-550 nm, broadband 300-1000 nm after 600 C); XPS gives Au/Cu chemical states; dark/vis/UV-vis LV photocurrent density links optics to photoelectrochemical activity",
    source_file="13126540.pdf (Lipinska, Grochowska, Karczewski, Ryl & Siuzdak 2022 J. Mater. Sci.: Mater. Electron. 33:19385); UV-vis/ 9 txt; XPS/ 4 txt; photoelectrochemistry/ 12 LV txt",
    confidence=0.85,
)

R["13145196"] = dict(
    modality="Mid-IR nano-FTIR (s-SNOM based) spectroscopy of field-enhanced molecular vibrational scattering at single Au nanorod and gap antennas probed by a PDMS-coated AFM tip (+ s-SNOM images)",
    spectral_range_original_min=667, spectral_range_original_max=2222, spectral_range_original_unit="cm-1",  # 4.5-15 um nano-FTIR laser band
    num_spectral_channels=1024,  # FFT points 0-3196.9 cm-1
    sampling_interval=3.125, sampling_interval_unit="cm-1 (zero-filled FFT axis)",
    num_samples=47,  # antenna/tip measurements (34 rods for Fig. 3, 13 gap antennas for Fig. 5)
    num_spectra=47, num_images=1360,
    num_spectral_values=577536,  # 47 x 1024 x 12 demodulation channels (O0-O5 amplitude and phase)
    spectral_target_relationship="Demodulated (n = 0-5) amplitude/phase spectra show the PDMS Si-CH3 vibration (1258 cm-1) on the dipolar antenna resonance; antenna length (1.5-3.5 um) tunes the resonance above/at/below 1258 cm-1 -> verifies the field-enhanced molecular scattering (E_AOA) model of SEIRA line shapes",
    source_file="13145196.pdf (Virmani, Maciel-Escudero, Hillenbrand & Schnell 2024 Nat. Commun. 15:6760); data_for_repository/ Fig3_rods and Fig5_gapantennas neaspec folders (*Spectra.txt, *Interferograms.txt, .gsf, .html); identical data_for_repository.zip",
    confidence=0.8,
)

R["13151054"] = dict(
    modality="UV-Vis-NIR absorption spectroscopy of gold-nanoprism-functionalised magnetotactic bacteria (+ photothermal heating curves, ICP, OD600 viability)",
    spectral_range_original_min=350, spectral_range_original_max=1100, spectral_range_original_unit="nm",
    num_spectral_channels=751, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=4,  # MSR-1, MSR-AuNPR, MSR-Lp@AuNPR, MSR-Pa@AuNPR
    num_spectra=4,
    spectral_target_relationship="LSPR bands of gold nanoprisms (NIR in-plane dipole plus visible bands) remain after attachment to Magnetospirillum gryphiswaldense MSR-1 with or without exopolysaccharide coating -> confirms functionalisation; 1064 nm irradiation raises temperature by 8-10 C (heating curves)",
    source_file="13151054.pdf (Cerezo-Collado et al. 2025 Materials Today Chemistry, doi:10.1016/j.mtchem.2025.103178); Data MSR-AuNPR-EPS.rar: MSR-AuNPR-EPS Uv-vis.xlsx, 3 heating-curve .dat, ICP.xlsx, viability DO600.xlsx",
    confidence=0.85,
)

R["13308246"] = dict(
    modality="MIR spectroscopy of fine-particulate olivine and pyroxene regoliths of varying porosity: ambient diffuse reflectance (FTIR, converted to emissivity), ambient emissivity and simulated asteroid environment (SAE) emissivity",
    spectral_range_original_min=129.2256, spectral_range_original_max=6001.3, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    num_samples=13,  # mineral x size fraction x KBr porosity proxy (0-90 %)
    num_spectra=37,  # 13 reflectance-derived, 13 ambient emissivity, 11 SAE emissivity
    num_spectral_values=79298,
    spectral_target_relationship="Kirchhoff's law test (E = 1 - R) for high-porosity regolith: Christiansen feature, reststrahlen bands and transparency features of forsterite (Fo91; <20 and 45-63 um) and hedenbergite (45-63 um) mixed with KBr (0-90 %) compared between ambient reflectance, ambient emission and SAE (vacuum, heated from below) emission -> environmental corrections for airless-body MIR remote sensing",
    source_file="13308246.pdf (Martin, Emery, Loeffler & Donaldson Hanna 2025, AGU journal, accepted Apr 2025); 37 txt: *_r (wavelength um, reflectance-derived emissivity, uncertainty), *_a (ambient emissivity vs cm-1), *_sae (SAE emissivity vs cm-1)",
    confidence=0.85,
)

R["13308543"] = dict(
    modality="FTIR-ATR absorbance spectroscopy (Nicolet iS5, ZnSe) of pelagic Sargassum biomass",
    spectral_range_original_min=499.955, spectral_range_original_max=4000.122, spectral_range_original_unit="cm-1",
    num_spectral_channels=7261, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=30,  # specimens, each read in triplicate (a/b/c)
    num_spectra=90,
    spectral_target_relationship="Bands of mannitol, alginate/carboxylates, carboxylic acids and proteins -> univariate tests, PCA, clustering and classification separating flash-freezing at the shore vs after cold transport (d00 vs d01) and morphotypes (S. fluitans III, S. natans I, S. natans VIII); degradation markers for biomass quality",
    source_file="13308543.pdf (Peniche-Pavia et al. 2024 J. Appl. Phycol. 36:1391); 90 CSV (wavenumber, absorbance) named <site>_<morphotype>_<d00|d01>_<replicate><a-c>",
    confidence=0.85,
)

R["13681778"] = dict(
    modality="Gas-phase experimental IR absorbance spectra (NIST) paired with DFT (RB3LYP) structures, harmonic frequencies and IR intensities, plus trained message-passing neural-network IR models",
    spectral_range_original_min=450, spectral_range_original_max=3966, spectral_range_original_unit="cm-1",
    num_spectral_channels=880, sampling_interval=4, sampling_interval_unit="cm-1 (NIST grid; resampled copies 400-4000 cm-1 @2 cm-1, 1,801 pts)",
    num_samples=4896,  # molecules (CAS-indexed)
    num_spectra=4896,  # NIST experimental spectra (each also given broadened/resampled)
    num_spectral_values=4196280,  # 2,856 x 880 + 2,040 x 825 NIST points
    spectral_target_relationship="3D molecular structure (atoms, coordinates, masses; B3LYP-D3BJ/def2-TZVP geometries) -> message-passing neural network predicts the IR spectrum (Gaussian broadening sigma 10 cm-1, 2 cm-1 grid); SIS 0.92 on a 200-molecule test set vs 0.57 for scaled DFT frequencies",
    source_file="13681778.pdf (Abdul Al & Allouche 2024, arXiv:2405.05737); NNMol-IR_DataModels/Data/TRAIN.h5 (pandas HDF, 4,896 x 20 columns; EVAL.h5 byte-identical); Models/ 13 training runs (average/best checkpoints, model_parameters.txt); train/predict/evaluation scripts; example xyz",
    confidence=0.85,
)

R["13757138"] = dict(
    modality="On-chip mid-IR photocurrent spectroscopy (Fourier-transform interferometry with a graphene/h-BN phonon-polariton photodetector) of CBP molecular layers + far-field FTIR transmission reference",
    spectral_range_original_min=1195, spectral_range_original_max=1796, spectral_range_original_unit="cm-1",
    spectral_resolution=6.5, spectral_resolution_unit="cm-1",
    num_samples=14,  # CBP thicknesses: 7 on-chip (0-100 nm) + 7 on CaF2 (10-100 nm)
    num_spectra=21,  # interferogram files (20 runs x 1024 points each); processed spectra in Source data.xlsx
    spectral_target_relationship="CBP vibrational bands (~1450-1500 cm-1) appear as photocurrent contrast in the graphene detector; hyperbolic phonon polaritons in h-BN enhance near-field coupling -> molecular-vibration contrast vs layer thickness (down to ~10 nm), compared with far-field transmission and simulations",
    source_file="13757138.pdf (Bylinkin et al. 2024 Nat. Commun. 15:8907); Interferograms.zip (far-field: 7 thicknesses x mol/NOmol; on-chip: 7 files; neaspec txt + readme); Source data.xlsx (Figs 2-5, Suppl. Figs 2-13; spectra 495-2496 cm-1)",
    confidence=0.8,
)

R["13901594"] = dict(
    modality="Single UV-Vis absorbance spectrum of lysogeny broth (LB) accompanying optical images of 3D-printed hydrogel microfluidics",
    spectral_range_original_min=300, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=501, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=1, num_spectra=1, num_images=158,
    spectral_target_relationship="Higher absorbance of LB near the printer's light wavelength explains the shorter optimal layer exposure of PEGDA-glycerol-LB resin (Fig. S5); the rest of the dataset is optical imagery of printed microchannels and dye diffusion",
    source_file="13901594.pdf (Sun et al. 2025 Prog. Addit. Manuf. 10:7927); 20240409 LB.csv; 4 image ZIPs (jpg; 1.08 GB diffusion flow-rate zip not opened)",
    confidence=0.6,
)

R["13908992"] = dict(
    modality="Reflection-absorption (RAIRS) and transmission FTIR spectroscopy of 2 keV electron- and VUV-irradiated CS2-bearing interstellar ice analogues + QMS temperature-programmed desorption",
    spectral_range_original_min=599.7835, spectral_range_original_max=4999.3212, spectral_range_original_unit="cm-1",
    num_spectral_channels=9126, spectral_resolution=1, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=13,  # experiments
    num_spectra=48,  # 41 x 9,126 points + 7 x 7,883 points
    num_spectral_values=429347,
    spectral_target_relationship="Growth of OCS (and 18O13CS ~1955 cm-1 isotopologue) IR bands and CS2 consumption vs irradiation time and ice temperature (6-50 K) in 13C18O2:CS2, 13C18O:CS2, H2(18)O:CS2 and CO:H2S ices -> relative contribution of CO+S vs CS+O OCS formation pathways; QMS TPD of desorbing products",
    source_file="13908992.pdf (Martin-Domenech, Oberg, Munoz Caro, Carrascosa, Fuente & Rajappan 2024 MNRAS preprint); Exp1-Exp13 zips: 48 .dpt (OPUS export) IR spectra, 13 .asc QMS TPD exports, 13 .xls",
    confidence=0.85,
)

R["13912495"] = dict(
    modality="ATR-FTIR (diamond, Nicolet 6700) spectroscopy of rubber/clay nanocomposites before/after aging and Mullins pre-straining (+ DSC, TGA, XRD, SEM, mechanical tests)",
    spectral_range_original_min=399.1926, spectral_range_original_max=4001.568, spectral_range_original_unit="cm-1",
    num_spectral_channels=1869, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.9284, sampling_interval_unit="cm-1",
    num_samples=12,  # NM/AM x NA/AA x 0 % / 1 % Cloisite Na+ / 2 % Cloisite 20A
    num_spectra=12,
    spectral_target_relationship="Functional-group bands (C-H, C=C, carbonyl/oxidation products, clay Si-O) compared across thermal aging (NA/AA), Mullins stress softening (NM/AM) and organoclay loading -> chemical changes accompanying mechanical property loss",
    source_file="13912495.pdf (Bakar et al. 2024 Polymers 16:3141); RAW_DATA_Reasearch paper_2024-Oct10.zip: 12 FTIR_*.CSV, 12 DSC txt, 12 TGA txt, 12 XRD csv, 12 SEM tif, Mechanical properties.xlsx",
    confidence=0.8,
)

R["13943887"] = dict(
    modality="UV-VIS-NIR hemispherical reflectance (Agilent Cary 5000, internal diffuse reflectance accessory) of passive radiative-cooling paints, substrates and nanoporous film layers (+ one transmittance spectrum)",
    spectral_range_original_min=200, spectral_range_original_max=2650, spectral_range_original_unit="nm",
    sampling_interval=1, sampling_interval_unit="nm",
    num_samples=15,  # Celgard, free-standing paint (1 / multi coat), S90 and V95 substrates (bare, +GB, +1-4 NPF coats)
    num_spectra=16,  # 15 reflectance + 1 transmittance (Celgard)
    num_spectral_values=37166,
    spectral_target_relationship="Solar-range reflectance (0.25-2.5 um) rises with glass bubbles (GB) and successive nanoporous-film (NPF) coats on S90/V95 substrates -> solar-weighted reflectance and sub-ambient daytime cooling in outdoor tests (MIR emissivity from Cary 630 FTIR shown in paper only)",
    source_file="13943887.pdf (Lio et al. 2024 Int. J. Thermophys. 45:153); 15 R_*.txt + T_Celgard.txt (wavelength nm, value); R_Calgard.mat",
    confidence=0.85,
)

R["13948069"] = dict(
    modality="Transmission FTIR absorbance spectroscopy of laboratory polar and methanol-bearing interstellar ice mixtures on CsI (UHV SPACEKITTEN, Bruker Vertex 70v) during warm-up",
    spectral_range_original_min=599.9991, spectral_range_original_max=5999.7502, spectral_range_original_unit="cm-1",
    num_spectral_channels=22401, spectral_resolution=0.5, spectral_resolution_unit="cm-1",
    sampling_interval=0.24106, sampling_interval_unit="cm-1",
    num_samples=6,  # H2O:CO2:CO 10:1:1, 10:2:2, 10:3:3, 10:5:0; CO2:CH3OH 1:1; CO:CH3OH 1:1
    num_spectra=82,  # 10 K steps from 10 K until sublimation (to 150 K)
    num_spectral_values=1529893,  # 45 x 22,401 + 37 x 14,104 points
    spectral_target_relationship="H2O (3 um), CO2 (4.27 um), CO (4.67 um) and CH3OH band profiles vs mixing ratio and temperature -> optical constants (n, k) and radiative-transfer disk models reproducing JWST NIRSpec ice bands of the edge-on HH 48 NE disk (mixed ices, CO trapping in H2O/CO2, ice C/O ~0.1)",
    source_file="13948069.pdf (Bergner et al. 2024 ApJ, doi:10.3847/1538-4357/ad79fc); 82 txt (wavenumber, absorbance); pure and apolar ices are in companion record 10.5281/zenodo.13948083",
    confidence=0.9,
)

R["14171144"] = dict(
    modality="Computed spectral complex refractive index (n, k) of mineral dust (5,000 random compositions per fine/coarse mode) and derived bulk single-scattering properties - modelled, not measured spectra",
    spectral_range_original_min=0.2, spectral_range_original_max=50, spectral_range_original_unit="um",
    num_spectral_channels=127,
    num_samples=10027,  # 5,000 fine + 5,000 coarse synthetic samples + 27 regional dust samples
    num_spectra=10054,  # n,k spectra: 10,000 synthetic + 27 regional x 2 modes
    num_spectral_values=2553716,  # x 127 wavelengths x 2 (n and k)
    spectral_target_relationship="Volume fractions of nine mineral groups (illite, kaolinite, montmorillonite, quartz, feldspar, carbonate, gypsum, hematite, goethite) -> mixed complex refractive index spectra (0.2-50 um) -> TAMUdust2020 extinction/scattering efficiencies, asymmetry and phase matrices (532 nm, 10.5 um) for 13 coarse/fine mixtures; sensitivity of dust SW/LW optics to mineralogy and size",
    source_file="14171144.pdf (Di Biagio et al. 2017 ACP 17:1901 - in-situ LW refractive index measurements, related source data; dataset paper Zhang, Saito, Yang, Schuster & Trepte 2024 JGR-Atmos. not supplied); readme_v1.3.txt; nall27/kall27_{fine,coarse}.dat; DustSamples, GroupRefInd, AdditionalRefInd, BulkProperties, PhaseMatrices (2.2 GB), Supplemental tar.gz; composition xlsx",
    confidence=0.7,
)

R["14246011"] = dict(
    modality="FTIR absorbance spectra (Bruker OPUS .dpt) + 77 K 57Fe Mossbauer, XPS and XRD of Fe-bearing Mg-silicate sol-gel glasses",
    spectral_range_original_min=349.0546, spectral_range_original_max=3997.7354, spectral_range_original_unit="cm-1",
    num_spectral_channels=1893, sampling_interval=1.92848, sampling_interval_unit="cm-1",
    num_samples=12,  # glasses with 5-50 % Fe (FTIR set)
    num_spectra=12,  # FTIR; plus 3 Mossbauer .plt, 7 .xps + 3 .VGD XPS, 18 XRD scans
    spectral_target_relationship="Si-O-Si/Si-O-NBO stretching envelope (~900-1100 cm-1) and Q^n depolymerisation vs Fe content; Mossbauer Fe2+/sum-Fe and tetrahedral/octahedral Fe3+; XPS bridging vs non-bridging oxygen -> dissolution reactivity (Si solubility up to 85 %) for supplementary cementitious materials",
    source_file="14246011.pdf (Jiang et al. 2026 Materials Chemistry and Physics, doi:10.1016/j.matchemphys.2026.132072); 93 files: 12 FTIR .dpt, 3 Mossbauer .plt, 7 .xps + 3 .VGD XPS, 13 .raw + 5 .xrdml XRD, DSC/TGA xls, PSD, ICP pdf, SEM-EDS images, XRF xlsx",
    confidence=0.75,
)

R["14557348"] = dict(
    modality="MIR FTIR spectra (Bruker Vertex 70) of dried topsoil samples + laboratory soil properties",
    spectral_range_original_min=599.76558, spectral_range_original_max=5397.89023, spectral_range_original_unit="cm-1",
    num_spectral_channels=2489, sampling_interval=1.92851, sampling_interval_unit="cm-1",
    num_samples=139, num_spectra=139,
    spectral_target_relationship="MIR absorption features of organic matter, carbonates, clay minerals and quartz -> spectroscopic models of pH, CaCO3, total and organic carbon and sand/silt/clay fractions in a catchment near Badong (Hubei, China); used for sampling-design optimisation and digital soil mapping",
    source_file="14557348.pdf (Wadoux, Stumpf & Scholten 2025 Data in Brief 60:111510); MID_IR_spectra.txt (139 x 2,489 wavenumbers); soil_data.txt (139 x 18 columns incl. UTM coordinates)",
    confidence=0.9,
)

R["14610222"] = dict(
    modality="Vis-NIR diffuse reflectance (ASD FieldSpec 4 with contact probe) soil spectral library",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    num_spectral_channels=2151, spectral_resolution=3, spectral_resolution_unit="nm at 700 nm (8 nm at 1400/2100 nm)",
    sampling_interval=1, sampling_interval_unit="nm (interpolated)",
    num_samples=5490,  # samples from 1,877 HSDOS sites, 3 profile levels, sampled Aug-Nov 2011
    num_spectra=5490,
    spectral_target_relationship="Splice-corrected reflectance (mean of 5 x 50 scans) with pH(KCl), SOM, CaCO3, total salt, TN, AL-P2O5, AL-K2O, plasticity index and profile depth -> national Hungarian SSL for calibrating soil-property prediction models",
    source_file="14610222.pdf (Meszaros et al. 2025 Sci. Data 12:363); HSDOS_SSL_ver1.1.csv (5,490 rows x 2,167 columns: 16 metadata/property + SPC.350-SPC.2500)",
    confidence=0.9,
)

R["14718338"] = dict(
    modality="ATR-FTIR (Shimadzu IRAffinity-1) spectra of pumpkin seed protein concentrates (+ Lowry, DPPH, colour, TD-NMR and functional-property tables)",
    spectral_range_original_min=497.859027, spectral_range_original_max=4000.039771, spectral_range_original_unit="cm-1",
    num_spectral_channels=613, spectral_resolution=16, spectral_resolution_unit="cm-1",
    sampling_interval=5.7225, sampling_interval_unit="cm-1",
    num_samples=10,  # control flour + alkali / salt / enzyme-assisted alkali extraction x untreated / conventional / microwave preheating
    num_spectra=14,
    spectral_target_relationship="Amide I (1600-1700 cm-1) second-derivative + Gaussian deconvolution -> alpha-helix, beta-sheet, beta-turn and random-coil fractions vs extraction method and preheating; related to yield, solubility, foaming/emulsifying and antioxidant properties",
    source_file="14718338.pdf (Tas, Sumnu & Oztop 2025 ACS Food Sci. Technol. 5:105); PSPC_Raw Data.rar: ftir_results_raw data.xlsx (10 sheets, 14 spectra), PSCP Extraction Results.xlsx (yield, proximate, Lowry A750, WSI/T2, FTIR secondary structure, DPPH A517, foaming/emulsifying, colour, aw)",
    confidence=0.85,
)

R["14829996"] = dict(
    modality="Reflectance micro-FTIR (Thermo Nicolet iN10, gold slide, OMNIC Picta mosaics and maps) spectra of suspected microplastic particles from Japanese coastal surface water and sediment",
    spectral_range_original_min=674.99, spectral_range_original_max=3999.81, spectral_range_original_unit="cm-1",
    num_spectral_channels=863, sampling_interval=3.857, sampling_interval_unit="cm-1 (1,725-point spectra: 1.93 cm-1)",
    num_samples=110,  # sample vials (surface water / sediment) with particle spectra
    num_spectra=11796,  # sample spectra (+312 background spectra)
    num_spectral_values=10423112,  # 9,778 x 863 + 1,716 x 853 + 302 x 1,725
    spectral_target_relationship="Particle spectra matched to OMNIC Specta libraries (hit >= 70 %) -> polymer identity of microplastics; combined with counts, Feret size (ImageJ) and CTD water properties -> distribution and coastal retention of microplastics (Tara JAMBIO 2020-2023)",
    source_file="14829996.pdf (Ramtahal et al. 2025, HAL hal-05215331 / ES&T doi:10.1021/acs.est.5c02645); TaraJambio_FTIR.zip (12,108 .spa, 311 .map, 291 png mosaics, FTIR_Polymer_ID xlsx); TaraJambio_CTD_Data.zip; image-analysis and polymer csv; R markdown; README docx",
    confidence=0.85,
)
