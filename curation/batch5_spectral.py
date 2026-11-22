# Batch5 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (C:\Users\Admin\RAG\papers5\<id>.pdf) + dataset (D:\Batch5_datasets\<id>_<title>\).
# Only the 35 records that contain spectra are kept; the 15 records without spectra were moved
# to D:\Batch5_no_spectra (see NO_SPECTRA below) and are not part of the batch5 parquet files.
# 16758266 was first removed as an empty (zero-filled) download and restored after re-download.
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

# Records removed from Batch5 because the dataset holds no spectra (record id -> reason).
NO_SPECTRA = {
    "15054060": "IODP Exp 395 interstitial-water composite report (wet chemistry)",
    "15127604": "IODP Exp 395C interstitial-water composite report (wet chemistry)",
    "15162487": "article PDF only (electrochemical glyphosate sensor)",
    "15162572": "article PDF only (GC-MS breath/hair volatiles)",
    "15238604": "IODP Exp 402 interstitial-water composite report (wet chemistry)",
    "15272190": "IODP Exp 346 interstitial-water composite report (wet chemistry)",
    "15320229": "DFT-optimised structures (xyz) + molecular Hessian matrices (npy) for QM8/QM9/PubChem and a model checkpoint - no INS/vibrational spectra files",
    "15381807": "8 figure PNGs + 3 small tables (BET, lattice parameters, technique comparison) of a zeolite-coke review",
    "15501660": "NDACC GEOMS HDF4 files with retrieved trace-gas profiles/columns and averaging kernels only - no FTIR spectra (plus a 0-byte .part file)",
    "15584525": "PLSR-predicted leaf traits per ASD scan and PLSR coefficient vectors (350-2500 nm) - the reflectance spectra themselves are not included",
    "15672948": "annual soil-salinity GeoTIFF maps (Landsat-derived) + EC sampling points with band indices",
    "15736566": "river-water sensor time series (DOCeq, TSSeq, SAK254, nitrate), online ion chromatography and discharge - concentrations only",
    "15783832": "sewer hydraulics, rainfall and UV/VIS-probe-derived COD/TSS time series + SWMM model - no absorbance spectra",
    "16522718": "article PDF only (Ni/Cu Schiff-base complexes; spectra printed as figures)",
    "17017812": "FTIR-PLSR calibration/validation tables (measured vs predicted root fraction) - no FTIR spectra",
}

# ---------------------------------------------------------------------------
# IODP JOIDES Resolution shipboard data (papers = Proceedings volume front matter;
# methods are standard JRSO shipboard procedures)
# ---------------------------------------------------------------------------
_PAPER = {
    395: "Proc. IODP Vol. 395 front matter (HAL hal-05384185; covers Exps 384, 395C, 395)",
    401: "Proc. IODP Vol. 401 front matter",
    402: "Proc. IODP Vol. 402 front matter",
}

_SPEC_WL = {"ammonium": 640, "phosphate": 885, "silica": 812, "sulfide": 670}


def _spec(rid, exp, vol, counts, nsamples, nholes, sites, depth_max, files, conf=0.85, note=""):
    analytes = list(counts)
    wl = [_SPEC_WL[a] for a in analytes]
    R[rid] = dict(
        modality="Single-wavelength UV-Vis colorimetric absorbance (Agilent Cary 300) of interstitial water: " + ", ".join(f"{a} {w} nm" for a, w in zip(analytes, wl)),
        spectral_range_original_min=min(wl), spectral_range_original_max=max(wl), spectral_range_original_unit="nm",
        num_spectral_channels=len(wl), spectral_resolution=1.5, spectral_resolution_unit="nm (spectral bandwidth, SBW)",
        num_samples=nsamples,
        num_spectral_values=sum(counts.values()),  # concentration results (one absorbance reading per analyte per sample)
        spectral_target_relationship=f"Absorbance at fixed analytical wavelengths vs external standard curve -> pore-water {'/'.join(analytes)} concentrations (uM) vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}); Beer-Lambert linear calibration" + note,
        source_file=f"{rid}.pdf ({_PAPER[vol]}, Exp {exp}); SPEC-README.txt; {files}",
        confidence=conf,
    )


_spec("15054233", "395", 395, {"ammonium": 225, "phosphate": 223}, 226, 8, "U1554, U1564, U1602", 1050.66,
      "data_by_hole (8 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (18 Cary Advanced Reads csv, 18 .BAB, 13 *.xlsm calibration workbooks)",
      note="; README states Cary 100, raw reports say Cary 300")
_spec("15127706", "395C", 395, {"ammonium": 165, "phosphate": 163}, 150, 5, "U1554, U1555, U1562, U1563", 644.16,
      "data_by_hole (5 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (8 Cary Advanced Reads csv, 12 .BAB, 7 .MAB, 8 sample-batch txt, 6 *.xlsm workbooks)",
      note="; README states Cary 100, raw reports say Cary 300")
_spec("15238684", "402", 402, {"ammonium": 135, "phosphate": 136, "sulfide": 125}, 261, 8, "U1612-U1617", 319.72,
      "data_by_hole (8 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (27 Cary Advanced Reads csv, 28 .BAB, 26 *.xlsm workbooks)",
      note="; sulfide by methylene blue at 670 nm; README states Cary 100, raw reports say Cary 300")
_spec("16459629", "401", 401, {"ammonium": 204, "phosphate": 192}, 183, 4, "U1385, U1609, U1610, U1611", 1215.38,
      "data_by_hole (4 csv) + scaled/compiled-scale/splice variants; supplementary raw_data_files (8 *.xlsm workbooks embedding the Cary 300 Advanced Reads absorbance reports)",
      conf=0.8, note="; 55 results reported as 'bdl'")


def _rsc(rid, exp, vol, nspectra, nfiles, nholes, sites, depth_max, sensor, conf=0.85):
    R[rid] = dict(
        modality=f"VIS diffuse reflectance spectroscopy and colorimetry (RSC) of split-core section halves ({sensor} + integrating sphere on SHMSL)",
        spectral_range_original_min=390, spectral_range_original_max=718, spectral_range_original_unit="nm",
        num_spectral_channels=165, sampling_interval=2, sampling_interval_unit="nm",
        num_samples=nfiles,  # per-section-half normalised reflectance files
        num_spectra=nspectra,
        spectral_target_relationship=f"% reflectance spectra (white/dark-referenced) of sediment/rock core surfaces -> CIE XYZ, L*a*b*, chroma, hue vs depth (0-{depth_max} m CSF-A) in {nholes} holes ({sites}) for lithostratigraphy, cyclostratigraphy and hole-to-hole correlation",
        source_file=f"{rid}.pdf ({_PAPER[vol]}, Exp {exp}); RSC-README.txt; data_by_hole/*-RSC.csv (+ scaled, compiled-scale, splice); supplementary_material raw_data_files norm_*/raw_*_rsc.csv + *.RSC; configuration .ini files; standards_measured",
        confidence=conf,
    )


_QEP732 = "Ocean Insight QE Pro (S/N QEP00732) with Ocean Optics BlueLoop source"
_QEP674 = "Ocean Insight QE Pro (S/N QEP00674)"
_rsc("15054221", "395", 395, 149151, 3204, 11, "U1554, U1562, U1564, U1602", 1357.55, _QEP732)
_rsc("15122421", "384", 395, 11245, 260, 5, "U1554, U1555", 308.38, _QEP674)
_rsc("15127696", "395C", 395, 102888, 2110, 11, "U1554, U1555, U1562-U1564", 778.7, _QEP674)
_rsc("15238671", "402", 402, 55481, 1040, 11, "U1612-U1617", 427.94, _QEP732)
_rsc("16459592", "401", 401, 129039, 2187, 7, "U1385, U1609-U1611", 1390.58, _QEP732)

# ---------------------------------------------------------------------------

R["15350566"] = dict(
    modality="Transmission FTIR absorbance spectroscopy of CH4-bearing interstellar ice analogues on a Ge window in UHV (ISEAge setup; deposition at 6.7 K and 10 K)",
    spectral_range_original_min=630.016, spectral_range_original_max=3999.948, spectral_range_original_unit="cm-1",
    num_spectral_channels=27960, spectral_resolution=1, spectral_resolution_unit="cm-1",
    sampling_interval=0.1206, sampling_interval_unit="cm-1",
    num_samples=12,  # 6 compositions (pure CH4, CH4:H2O 1:10, CH4:CO2 1:5 and 1:15, CH4:CH3OH 1:3, CH4:NH3 1:3) x 2 temperatures
    num_spectra=24,  # raw + baseline-corrected for each experiment
    num_spectral_values=672948,  # 23 x 27,960 + 1 x 29,868 points (one raw file extends to 400 cm-1)
    spectral_target_relationship="Position, width and band strength of the CH4 nu3 stretch (~3010 cm-1) and nu4 deformation (~1300 cm-1) change with matrix (H2O, CO2, CH3OH, NH3), mixing ratio and deposition temperature (phase II* at 6.7 K vs phase II at 10 K) -> ~20 % higher band strengths in mixtures; laboratory references fitted to JWST NIRCam/MIRI ice spectra of the B335 protostar",
    source_file="15350566.pdf (Karteyeva, Nakibov, Petrashkevich, Medvedev & Vasyunin 2026, A&A manuscript aa58069-25); 24 headerless CSV (wavenumber, absorbance) named '<T> K <mixture>, raw|corrected'",
    confidence=0.9,
)

R["16571069"] = dict(
    modality="Transmission FTIR absorbance spectroscopy of UV-irradiated CH3CN:O3 (and O2, CO2, H2O, Xe, CH3C15N) interstellar ice analogues on CsI in UHV (SPACECAT) + QMS temperature-programmed desorption",
    spectral_range_original_min=599.6768, spectral_range_original_max=4399.2369, spectral_range_original_unit="cm-1",
    num_spectral_channels=28213, spectral_resolution=1, spectral_resolution_unit="cm-1",
    sampling_interval=0.1205, sampling_interval_unit="cm-1 (Exp 9 files: 0.482 cm-1, 7,883 points to 4399 cm-1)",
    num_samples=10,  # experiments (Table 2)
    num_spectra=96,  # IR spectra during 254 nm / 120-160 nm irradiation time series (0-4.5 h)
    num_spectral_values=2464488,  # 84 x 28,213 + 12 x 7,883 points
    spectral_target_relationship="Decay of CH3CN (920, 1041, 2255 cm-1) and O3 (1037 cm-1) bands and growth of methyl isocyanate CH3NCO (2320/2297/2282/2235 cm-1) with UV fluence -> O(1D) insertion yields (2-35 %) vs irradiation temperature (10-40 K) and matrix (Xe, CO2, H2O, O2); 15N isotopic shifts and QMS TPD confirm product identity",
    source_file="16571069.pdf (Brann, Oberg & Rajappan 2025, AASTeX draft 'Methyl Isocyanate Formation from Oxygen Insertion in Methyl Cyanide Ices'); Binary/ Exp1-4, Exp8_CH3C15N, Exp9_O2 + Ternary/ CO2, HO2 (H2O), Xe + Ex10_Control: 96 txt (wavenumber, absorbance) named irradiation_<time>_<T>K_<date>; TPD/ 2 QMS .asc + .xls; __MACOSX duplicates",
    confidence=0.85,
)

R["15209374"] = dict(
    modality="FTIR transmission, micro-ATR-FTIR, FT-Raman and micro-Raman spectroscopy of 2-aminopyrimidinium phosphite/sulfate salts + UV-Vis-NIR absorption of a 2-AmpH2PO3 single-crystal plate",
    spectral_range_original_min=49.658, spectral_range_original_max=4003.666, spectral_range_original_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1 (FTIR/FT-Raman; ATR 3.86, micro-Raman 0.96 cm-1; UV-Vis 190-1100 nm at 1 nm)",
    num_samples=4,  # 2-AmpH2PO3, 2-Amp2SO4.H2O, 2-AmpHSO4 polymorphs I and II
    num_spectra=11,  # 3 FTIR + 2 ATR + 3 FT-Raman + 2 micro-Raman + 1 UV-Vis-NIR
    num_spectral_values=55831,
    spectral_target_relationship="Vibrational bands (phosphite P-H 2412 cm-1, sPO2 1039/1043 cm-1, SO4/HSO4 modes, aminopyrimidinium ring modes) assigned with solid-state DFT -> hydrogen-bonding and polymorph identification; UV-Vis-NIR transparency (to ~370 nm) and refractive-index dispersion support phase-matched SHG (d = 1.18 d(KDP)) and stimulated Raman scattering of polar 2-AmpH2PO3",
    source_file="15209374.pdf (Matulkova, Bohaty, Becker, Cisarova, Gyepes, Fridrichova, Kroupa, Nemec & Nemec 2025, accepted manuscript); data/ 11 CSV (*_IR, *_ATR, *_Ra, *_micro-Ra, 2-AMPH2PO3_UV-Vis with UNICAM header) + Read_me.txt",
    confidence=0.85,
)

R["16164681"] = dict(
    modality="FTIR (KBr pellet, transmittance), Raman (532 nm) and UV-Vis absorption (toluene dispersions) of NH3-annealed N-doped reduced graphene oxide (+ TGA)",
    spectral_range_original_min=50.5437, spectral_range_original_max=4000.123, spectral_range_original_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1 (FTIR; Raman 0.964 cm-1; UV-Vis 200-800 nm at 2 nm)",
    num_samples=4,  # GO-500, GO-800, HOPG-500, HOPG-800
    num_spectra=12,  # 4 FTIR + 4 Raman + 4 UV-Vis
    num_spectral_values=45703,
    spectral_target_relationship="Loss of O-functional bands (C=O 1700, C-O-C 1042, epoxy 952 cm-1), new C-N (1160 cm-1) and shifted C=C (1552 cm-1) bands, Raman D/G/2D intensity ratios (ID/IG, crystallite size La) and a new 255 nm UV band track one-step N-doping/reduction of GO and HOPG-derived GO in NH3 at 500/800 C -> lower sheet resistance",
    source_file="16164681.pdf (Stefanovic, Yasir, Tobias-Rossell, Rojano, Sredojevic, Kepic, Kleut, Saeed, Milovic, Bajuk-Bogdanovic et al. 2025 Molecules 30:3579); VINCA_FTIR/RAMAN/UVVIS *.txt (12 spectra), 5 VINCA_TGA *.txt, 2 docx data descriptions",
    confidence=0.85,
)

R["14935187"] = dict(
    modality="Grazing-angle (SAGA) reflectance FTIR and 442 nm Raman spectroscopy of oxidised/hydrogenated boron-doped HPHT nanodiamonds + Raman of boron-doped diamond films (+ SAXS, SIMS)",
    spectral_range_original_min=100.035, spectral_range_original_max=4000.188, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1 (FTIR)",
    sampling_interval=0.482, sampling_interval_unit="cm-1 (FTIR; Raman ~1.6 cm-1)",
    num_samples=5,  # O-BND, H-BND nanodiamond powders; BDD films grown on H-DND, TD_HPHT H-ND and H-BND seeds
    num_spectra=7,  # 2 FTIR + 2 nanodiamond Raman + 3 BDD-film Raman
    num_spectral_values=18874,
    spectral_target_relationship="FTIR surface C-Hx/C=O bands distinguish oxidised vs hydrogenated BND (positive zeta potential after hydrogenation); Raman Fano-shaped diamond phonon (1316-1319 cm-1 in films), electronic Raman bands (~350/500 cm-1) and sp2 bands track heavy boron doping and seeding-dependent film quality; SAXS Guinier radii give nanoparticle size",
    source_file="14935187.pdf (Stehlik, Potocky, Aubrechtova Dragounova, Belsky, Medlin, Vincze, Ekimov & Kromka 2025 Diamond Relat. Mater., doi:10.1016/j.diamond.2025.112127); open data/Figure 1-7, S1-S3: per-figure CSV (Fig 2a FTIR, Fig 2b and Fig 6 Raman, Fig 1c/1d SAXS, Fig 5b SIMS) + figure PDFs; readme.txt",
    confidence=0.8,
)

R["15594028"] = dict(
    modality="ATR-IR absorbance and Raman spectroscopy (raw + processed) of xenon difluoride / noble-metal fluoride adducts (+ 3D electron diffraction, PXRD, r2SCAN DFT structures)",
    spectral_range_original_min=50, spectral_range_original_max=3996.3616, spectral_range_original_unit="cm-1",
    sampling_interval=2.061, sampling_interval_unit="cm-1 (ATR-IR; Raman 0.5 cm-1 over 50-1410 cm-1)",
    num_samples=6,  # XeF2/PtF4 in aHF, XePtF6, XePt2F10 (XeF2.2PtF4), XePdF6, XePd2F10 (XeF2.2PdF4), XePdF6 + XeF2
    num_spectra=17,  # 5 ATR-IR + 6 raw + 6 processed Raman
    num_spectral_values=41407,
    spectral_target_relationship="Xe-F stretching and M-F (Pt/Pd) bridging/terminal modes in IR (348-4000 cm-1) and Raman (50-1410 cm-1) fingerprint the XeF+ / [M2F9]- or [MF5]- salt-like adducts vs molecular XeF2, complementing 3D ED crystal structures of XeF2.2PtF4/XeF2.2PdF4 and DFT models of 'XePtF6'",
    source_file="15594028.pdf (Sun, Ruzsinszky & Perdew 2015 PRL 'SCAN' functional - DFT method reference only; dataset paper Motaln, Gurung, Dragomir, Kurzydlowski, Palatinus & Lozinsek 2025 not supplied); ATR-IR-data/ 5 .dpt; Raman-data/raw + processed/ 12 .dpt; PXRD-data (.dat + Eiger frames); 3D_ED-data.rar (PETS2 projects, hkl, cif); DFT-data (VASP POSCAR/KPOINTS/POTCAR, r2SCAN-D3 scripts)",
    confidence=0.6,
)

R["15797834"] = dict(
    modality="Confocal Raman microspectroscopy (532 nm) and Raman mapping of P3HT:PC71BM organic photovoltaic blends with porphyrin metal-organic framework nanosheets",
    spectral_range_original_min=893.6698, spectral_range_original_max=1948.8856, spectral_range_original_unit="cm-1",
    num_spectral_channels=1650, sampling_interval=0.637, sampling_interval_unit="cm-1",
    num_samples=4,  # P3HT-PCBM and blends with Cu2(ZnTPyP), Cu2(CuTCPP), Zn2(ZnTCPP) MONs
    num_spectra=4, num_images=9,  # 4 Raman intensity maps + 5 TCA component/microstructure maps (RGB TIFF)
    spectral_target_relationship="P3HT C=C (1447 cm-1) and C-C (1380 cm-1) intra-ring bands map polymer distribution; porphyrin 1027/1066 cm-1 bands and PCBM components (true component analysis) reveal MON dispersion and nanosheet thickness/size effects that explain doubled (Zn2(ZnTCPP)) or halved (Cu2(CuTCPP)) power conversion efficiency",
    source_file="15797834.pdf (Sasitharan, Frisch, Kulicek, Iraqi, Lidzey, Bar, Rezek & Foster 2024 Sci. Rep., doi:10.1038/s41598-024-80007-y); VZ3_009_021_CVUT_D_0001-0004_v1.txt (Raman spectra, Fig 5a); D_0005-0013 TIFF maps (Fig 5b, S37-S41); ReadMeFile_v2.txt",
    confidence=0.85,
)

R["15863712"] = dict(
    modality="FTIR-ATR absorbance spectroscopy (diamond, Shimadzu IRTracer-100) of PLA, PBSu and PLA-PBSu block copolymers made by reactive processing - carbonyl/fingerprint region only",
    spectral_range_original_min=1170.81129, spectral_range_original_max=1800.58, spectral_range_original_unit="cm-1",
    num_spectral_channels=654, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.9644, sampling_interval_unit="cm-1",
    num_samples=13,  # PLA, PBSu0.22, PBSu0.38 and 10 copolymers (1, 2.5, 5, 10, 15 wt% of each PBSu macroinitiator)
    num_spectra=14,  # PLA column repeated in both sheets
    num_spectral_values=9131,
    spectral_target_relationship="Growth of the PBSu C=O (1713 cm-1) shoulder next to PLA C=O (1746 cm-1) and PBSu CH2 bands (1472/1425/1330 cm-1) with macroinitiator content (1-15 wt%) and PBSu chain length ([eta] 0.22 vs 0.38 dL/g) -> incorporation of PBSu blocks in blocky PLA-b-PBSu-b-PLA copolymers; spectra normalised to the PLA C=O band",
    source_file="15863712.pdf (Terzopoulou, Zamboulis, Bikiaris, Margellou et al. 2024 J. Polym. Environ. 32:316); 'FTIR of PLA PBSu copolymers.xlsx' (sheets 'PLA PBSu 0.22', 'PLA PBSu 0.38')",
    confidence=0.85,
)

R["15667001"] = dict(
    modality="FT-IR (diamond ATR), surface-enhanced Raman (SERS, 532 nm, Ag colloid/Au film) and XPS of natural, acid-treated and Fe-coated Romanian clinoptilolite volcanic tuff (+ XRD, BET)",
    spectral_range_original_min=211.234, spectral_range_original_max=3996.30566, spectral_range_original_unit="cm-1",
    sampling_interval=1.9287, sampling_interval_unit="cm-1 (FT-IR; SERS 3.08 cm-1)",
    num_samples=3,  # VT (raw tuff), VT1 (acid-treated), Fe_VT (iron-coated); XRD also after 5 reuse cycles
    num_spectra=15,  # 3 FT-IR + 3 SERS + 9 XPS regions (C1s, Fe2p3/2, survey)
    num_spectral_values=15137,
    spectral_target_relationship="Zeolite T-O-T (Si/Al-O) framework bands, OH/H2O bands, SERS bands of clinoptilolite/quartz and XPS Fe 2p, O 1s, Si/Al 2p states characterise acid and Fe functionalisation of volcanic tuff used as photo-Fenton-like catalyst for Reactive Black 5 and Methylene Blue decolorisation (>60 % in real effluent)",
    source_file="15667001.pdf (Maftei, Ignat, Dobromir, Buzatu & Neamtu 2025 Sci. Rep. 15:21456); 'Data availability.xlsx' (sheets XRD, FTIR, SERS, BET, XPS)",
    confidence=0.8,
)

R["14924463"] = dict(
    modality="UV-Vis absorption spectroscopy (Jasco V-780) of fungal melanins and arginine-modified melanins in 0.1 M NaOH",
    spectral_range_original_min=200, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=601, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=4,  # DTM, FFM, ADTM, AFFM
    num_spectra=4,  # plus log(absorbance) 400-600 nm versions of the same 4 spectra
    spectral_target_relationship="Strong UV absorbance (maxima 235-238 nm) decaying into the visible and linear log(A) vs wavelength slopes (-0.0018 to -0.0025 over 400-600 nm) confirm melanin identity of Daedaleopsis tricolor and Fomes fomentarius extracts before/after arginine modification; linked to DPPH antioxidant, neuroprotection (H2O2/MPTP) and SH-SY5Y differentiation assays",
    source_file="14924463.pdf (Nguyen, Ho, Mangelings, Van Eeckhaut, Vander Heyden & Tran 2024 BMC Biotechnol. 24:89); 'Raw data.xlsx' (sheets UV-Vis, Viability, Anti-toxicity effect, Differentiation)",
    confidence=0.85,
)

R["16422157"] = dict(
    modality="ATR-FTIR absorbance spectroscopy of precipitates from UV-photooxidised Fe(II)-carbonate solutions (early-Mars analogue experiments) (+ XRD, pH/DIC/Fe chemistry)",
    spectral_range_original_min=249.9815, spectral_range_original_max=4500.15, spectral_range_original_unit="cm-1",
    sampling_interval=0.241, sampling_interval_unit="cm-1 (O-UV_pHi7.46 sheet 0.482 cm-1)",
    num_samples=3,  # experiments O-UV_pHi7.46 (open), C-UV_pHi6.54 and C-UV_pHi7.44 (closed)
    num_spectra=4,  # 70 and 190 min (open) + 180 min (2 closed)
    num_spectral_values=49577,
    spectral_target_relationship="IR bands of precipitated Fe(III) oxyhydroxides / mixed-valence Fe minerals (and carbonate) identify the mineral products of 254 nm UV photooxidation of 1.79 mM Fe(II) + 35 mM DIC solutions vs initial pH and open/closed (CO2-degassing) setup; complemented by time-resolved XRD, pH, DIC and dissolved Fe",
    source_file="16422157.pdf (Rivera Banuchi & Hurowitz 2022 Goldschmidt abstract, doi:10.46427/gold2022.11126); Main_ATRFTIR.xlsx (3 sheets), Main_OpenSystemExps_XRD.xlsx, SI_XRD.xlsx, Main_DIC_pH_Fe.xlsx, Main_IronSpeciation.xlsx, SI_Open/ClosedSystemExperiments.xlsx",
    confidence=0.6,
)

R["16797564"] = dict(
    modality="Mid-IR FTIR absorbance spectra of urinary extracellular vesicles (uEVs) from prostate-cancer patients and healthy controls (per-patient averaged spectra)",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3601, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=53,  # 22 prostate cancer + 31 non-cancerous (labels H1-H21, P1-P16, S1-S16)
    num_spectra=53,
    spectral_target_relationship="uEV molecular signatures (lipid C-H 2850-2950, amide I/II 1650/1540, nucleic-acid/phosphate 1240/1080 cm-1) after baseline correction, unit-vector normalisation, Savitzky-Golay first derivative and SNV -> feature-selected spectra + clinical data classify prostate cancer vs non-cancer (linear SVM AUC 0.917 with SMOTE; outperforms PSA in the 4-20 ng/mL grey zone)",
    source_file="16797564.pdf (Wong, Bu, Supramaniam et al. 2025 Health Technol. 15:563); 'HEAL_average of 53 samples.csv' (53 rows: id, Sample label Cancerous/Non-cancerous, 3,601 absorbance columns 4000-400 cm-1)",
    confidence=0.8,
)

R["15533926"] = dict(
    modality="VIS-NIR leaf reflectance spectroscopy (Inventech Benelux handheld spectrometer, 338-1100 nm) of Alnus glutinosa seedlings under N fertilisation and Frankia inoculation",
    spectral_range_original_min=338, spectral_range_original_max=1100, spectral_range_original_unit="nm",
    num_spectral_channels=763, sampling_interval=1, sampling_interval_unit="nm",
    num_samples=160,  # plants (80 per experimental set; 8 treatments x 10)
    num_spectra=161,  # 160 leaf spectra + 1 blank reference (set 1); set 2 starts at 341 nm (760 bands)
    num_spectral_values=122603,
    spectral_target_relationship="Leaf reflectance of the third fully expanded leaf vs Frankia alni nodulation and NH4NO3 level (0-20 mM): PCA and PLS regression separate Frankia-derived from fertiliser-derived N (up to 54.8 % of spectral variance; key regions around 555 nm and the red edge) where SPAD chlorophyll does not; linked to leaf N, chlorophyll, biomass and nodule data",
    source_file="15533926.pdf (Georgopoulos, Bezemer, Vesterdal, Li, de Nobel, Gomes et al. 2025 Plant-Environment Interactions 6:e70066); 'Experimental set 1/2 NIR measurements.xlsx' (Metadata + 'NIR measurements' sheets); 'Experimental set 1/2 weekly and harvest plant data.xlsx'",
    confidence=0.8,
)

R["16108826"] = dict(
    modality="Transmission FTIR absorbance spectroscopy (KBr pellets, Thermo Nicolet iS10) of modern, experimentally softened and archaeological cervid/bovine bone and antler",
    spectral_range_original_min=399.9158, spectral_range_original_max=3999.8811, spectral_range_original_unit="cm-1",
    num_spectral_channels=14935, spectral_resolution=2, spectral_resolution_unit="cm-1",
    sampling_interval=0.241, sampling_interval_unit="cm-1",
    num_samples=32,  # 13 bone, 15 antler, 4 non-classified (8 reference, 12 experimental, 12 archaeological)
    num_spectra=32,
    num_spectral_values=473344,  # 10 x 14,935 (400-4000 cm-1) + 22 x 14,727 (450-4000 cm-1)
    spectral_target_relationship="Phosphate nu4 (565/605 cm-1) splitting -> crystallinity index, carbonate nu3 (1415 cm-1)/phosphate nu3 (1035 cm-1) -> C/P ratio and amide I height (collagen) distinguish bone from antler of European Cervidae and reveal diagenesis and softening treatments (lye, sour milk, urine, sorrel, water soaking) in Palaeolithic-to-medieval artefacts from Poland and Lithuania",
    source_file="16108826.pdf (Osipowicz, Lisowska-Gaczorek et al. 2025 J. Archaeol. Method Theory 32:58); 31 OMNIC Galactic .SPC + 1 OMNIC .SPA (absorbance; file comments = sample numbers, Polish notes)",
    confidence=0.85,
)

R["15114005"] = dict(
    modality="Non-contact reflection FTIR (Bruker Alpha II) of historical paint samples on Elias Brenner's 1680 colour chart (W2G3 copy); FORS, Raman, MSI and uXRF only as instrument-report PDFs",
    spectral_range_original_min=399.4706, spectral_range_original_max=3996.7542, spectral_range_original_unit="cm-1",
    num_spectral_channels=1757, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=2.06, sampling_interval_unit="cm-1",
    num_samples=6,  # Cerussa, Fissilis, Haematites, Montanum, Sangvis Draconis, Ultramarinum
    num_spectra=6,
    spectral_target_relationship="Reflection-FTIR bands of lead white (cerussite/hydrocerussite carbonate), red ochre/haematite, lazurite, dragon's blood resin and binders complement Raman/FORS/XRF identifications -> first material verification of 17th-century pigment names (Latin/French/Swedish) on Brenner's nomenclature chart",
    source_file="15114005.pdf (Ronnerstam, Fiorillo, Sandstrom & Martensson 2025 npj Herit. Sci., doi:10.1038/s40494-025-01987-2); 'FTIR Raw' 6 Bruker OPUS .0 files; instrument reports (PDF) for FORS, multispectral imaging, Raman (Bruker Bravo, B&W Tek i-Raman), uXRF (docx/doc)",
    confidence=0.75,
)

R["14991118"] = dict(
    modality="Transmission micro-FTIR absorbance (Jasco FTIR-6200 + IRT-7000 microscope) of double-polished carbonated hydrous basaltic glasses recovered from 2 GPa conductivity runs (+ impedance spectra)",
    spectral_range_original_min=599.7532, spectral_range_original_max=7000.335, spectral_range_original_unit="cm-1",
    num_spectral_channels=6639, sampling_interval=0.964233, sampling_interval_unit="cm-1",
    num_samples=7,  # Ba1_dry, Ba1_1, Ba1_3.7, Ba1_6.9 (first batch), Ba2_1.5, Ba2_3.7, Ba2_6.9 (second batch)
    num_spectra=99,  # 36 raw + 35 baseline-subtracted (batch 1) + 28 raw (batch 2) JASCO text exports
    num_spectral_values=657261,
    spectral_target_relationship="Beer-Lambert peak heights of total H2O (3530 cm-1, eps 63), molecular H2O (1630 cm-1, eps 25) and carbonate CO3(2-) doublet (1515/1435 cm-1, eps 375 L mol-1 cm-1) with measured glass thickness (20-45 um) -> dissolved H2O (0.05-4.13 wt%) and CO2 (0.16-0.82 wt%) of quenched melts, used to interpret 2 GPa electrical conductivity vs temperature and the oceanic-mantle conductivity anomaly",
    source_file="14991118.pdf (Zhao, Zhu, He & Yoshino 2025 JGR Solid Earth, doi:10.1029/2025JB032215); Basaltic melt/first batch|second batch: FTIR/ (99 JASCO txt + 29 .jws/15 .jwsu natives + 64 PNG; zip of subtracted spectra), impedance/ (227 csv), conductivity xlsx (R, 1000/T, log C), 'Summary 20250205+20240903.xlsx' (H2O/CO2 contents)",
    confidence=0.85,
)

R["15227508"] = dict(
    modality="Leaf-level VIS-NIR-SWIR reflectance, transmittance, absorbance and passive chlorophyll fluorescence (upward/downward) with FluoWat leaf clip + ASD FieldSpec, plus incoming irradiance, over a wheat season (+ pigment effective-absorbance unmixing outputs)",
    spectral_range_original_min=350, spectral_range_original_max=2500, spectral_range_original_unit="nm",
    num_spectral_channels=2151, spectral_resolution=3, spectral_resolution_unit="nm FWHM (350-1050 nm; 10 nm at 1050-2500 nm)",
    sampling_interval=1, sampling_interval_unit="nm",
    num_samples=243,  # leaf measurements: 9 dates x 3 N treatments x 9 replicates
    num_spectra=1458,  # 243 x 6 spectral variables (R, T, A, Fup, Fdw, E)
    spectral_target_relationship="Leaf R/T/A and SIF emission spectra of durum wheat under low/medium/high N (0/90/202 kg ha-1) -> FAPAR, NNLS pigment unmixing (Chl a/b, beta-carotene, xanthophyll effective absorbance), APAR_Chla and fluorescence quantum efficiency (FQE) used as proxies in linear/nonlinear light-use-efficiency models of net photosynthesis (Anet from LI-6400); FQE-LUE nonlinearity captures seasonal stress",
    source_file="15227508.pdf (Cendrero-Mateo, ..., Ponce-Campos et al. 2025 IEEE J-STARS 18:15069); fluowat/ 9 Fluowat_doyNNN.mat (structs n1/n3/n5: wvl, refl_real, trans_real, abs_real, Fup, Fdw, E; 9 x 2151) + readme PDF; pigment_effective_abs/ 8 Effective_Abs_doyNNN.mat + readme PDF; complile_dataset.xlsx (gas exchange, PAM, light curves)",
    confidence=0.85,
)

R["15253941"] = dict(
    modality="Astronomical UV-to-mid-IR spectroscopy of two diffuse-ISM sightlines (GSC 08152-02121, CPD-59 5831): HST STIS UV/optical, VLT X-shooter UVB/VIS/NIR, JWST NIRCam grism and MIRI MRS (orders and merged)",
    spectral_range_original_min=0.10005, spectral_range_original_max=31.9904, spectral_range_original_unit="um",
    num_samples=2,  # sightlines/background stars
    num_spectra=39,  # 3 STIS + 6 X-shooter arms + 28 JWST segments + 2 merged NIRCam+MRS spectra
    num_spectral_values=178665,
    spectral_target_relationship="Interstellar absorption features vs stellar continuum: 2175 A bump (STIS), 3.3/3.4 um aromatic/aliphatic hydrocarbons and 3 um water (NIRCam), 6.2/6.85/7.25 um carbonaceous bands and 9.7/18 um amorphous silicate (MRS) -> dust composition at low AV (WISCI program), with stellar typing and AV/RV from X-shooter/STIS",
    source_file="15253941.pdf (Zeegers, Marshall, Gordon, Misselt et al. 2025, arXiv:2506.20033 'Investigating silicate, carbon, and water in the diffuse interstellar medium: the first shots from WISCI'); HST_STIS 3 FITS tables; vltxshooter 6 CSV (wave, flux, errs, flags, telluric-corrected, continuum); JWST_NIRCam 4 + JWST_MIRI 24 order FITS; JWST_NIRCam_MIRI_merged 2 FITS + 2 PNG",
    confidence=0.85,
)

R["15489098"] = dict(
    modality="Near-IR echellette spectroscopy (Keck II NIRES, PypeIt-reduced) of lensed source galaxies in six DESI strong-lens systems: 1D coadded spectra + cleaned A-B 2D spectra",
    spectral_range_original_min=9402.676, spectral_range_original_max=24697.101, spectral_range_original_unit="Angstrom",
    sampling_interval=1.95, sampling_interval_unit="Angstrom (median 1D grid spacing)",
    num_samples=6,  # strong-lens systems DESI-006, -094, -133, -154, -165, -215
    num_spectra=18,  # 1D coadds: _ALL/_FINAL, _LEFT, _RIGHT per system
    num_images=26,  # cleaned 2D A-B spectra (2048 x 1024 per extension)
    num_spectral_values=134747,
    spectral_target_relationship="Rest-frame optical emission lines (e.g. [O II], H-beta, [O III], H-alpha) redshifted into the 0.94-2.47 um NIRES coverage -> lensed-source redshifts zs = 1.675-3.332 for six ResNet-discovered DESI Legacy Survey lenses (lens redshifts from DESI), enabling lens modelling",
    source_file="15489098.pdf (Agarwal, Huang, Sheu, Storfer, Tamargo-Arizmendi, Tabares-Tarquinio et al. 2026, AASTeX draft 'DESI Strong Lens Foundry III: Keck Spectroscopy for Strong Lenses Discovered Using Residual Neural Networks'); DESI-SLF-III-Data/DESI-NNN/ Spec1DCoadd (3 FITS: wave, wave_grid_mid, flux, ivar, sigma, mask) + Spec2D (spec2d_*.fits, PypeIt 1.13.0) + Legacy Surveys JPG; README.md",
    confidence=0.85,
)

R["15228144"] = dict(
    modality="Gas-phase IRMPD action spectra (FELIX + Bruker amaZon ion trap) and computed IR spectra (B3LYP harmonic, MLIP harmonic and machine-learning MD anharmonic at 100-1100 K) of cationic pyrene and superhydrogenated pyrenes",
    spectral_range_original_min=1.0, spectral_range_original_max=3999.6, spectral_range_original_unit="cm-1",
    sampling_interval=1.018, sampling_interval_unit="cm-1 (MD spectra; IRMPD 3-6 cm-1 steps; harmonic = stick lists)",
    num_samples=4,  # C16H10+, C16H14+ (THP), C16H16+ (HHP), C16H26+ (PHP)
    num_spectra=35,  # 4 IRMPD + 8 harmonic stick spectra (DFT, MLIP) + 23 MD temperature spectra (C16H26 1100 K empty)
    num_spectral_values=92235,
    spectral_target_relationship="Comparison of experimental IRMPD band positions (550-1800 cm-1) with harmonic DFT/MLIP and temperature-dependent anharmonic MLMD spectra (dipole autocorrelation) -> harmonic approximation adequate for pyrene and partially hydrogenated cations but anharmonic MD required for perhydropyrene; band red-shifts and broadening vs temperature (position-width table) for JWST PAH-band interpretation",
    source_file="15228144.pdf (Tang, Doktor, Jaganathan, Palotas, Oomens, Hornekaer & Hammer 2025, 'Anharmonic infrared spectra of cationic pyrene and superhydrogenated derivatives'); anharmonic-hpyrenes/ experiment (4 IRMPD txt), harmonic (4 txt: DFT and MLIP frequency/intensity), md (4 IR txt at 100-1100 K + band position/width), model (4 PaiNN .pt), structure (4 xyz), README.md",
    confidence=0.85,
)

R["15771437"] = dict(
    modality="Computed anharmonic IR absorption spectra of neutral PAHs from machine-learning molecular dynamics (NNFF potential + EPNN dipoles, dipole autocorrelation) - modelled, not measured",
    spectral_range_original_min=300, spectral_range_original_max=3799.3, spectral_range_original_unit="cm-1",
    num_spectral_channels=3500, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=1705,  # 1,704 NASA Ames PAHdb molecules + 1 extra experimentally tested PAH (48 of 49 overlap)
    num_spectra=5161,  # 1,704 x 3 temperatures (50, 300, 600 K) + 49 experiment-comparison spectra
    num_spectral_values=18063500,
    spectral_target_relationship="PAH 3D structure -> MLMD trajectories (NVT/NVE, 400,000 steps) -> dipole time-autocorrelation Fourier transform -> anharmonic IR band positions, widths and relative intensities (C-H stretch 3.3 um, C-C 6.2/7.7 um, C-H out-of-plane 11.2 um) vs temperature; validated on 49 PAHs with gas-phase experimental spectra for interpreting JWST/astronomical PAH emission",
    source_file="15771437.pdf (Mai, Wang, Pan, Schorghuber, Kovacs, Carrete & Madsen 2025 MNRAS 541:3073, arXiv:2503.05120); Supplementary_Data_Code/outputs: IR_txt_phdb_1704/IR_txt_{50,300,600}K_qm0.zip, IR_txt_EXP/IR_txt_EXP_qm0.zip, IR_txt (2 examples); inputs XYZ (1,704 PAHdb + 49 EXP); code + pretrained NNFF/EPNN models; Supplementary_Information.pdf",
    confidence=0.85,
)

R["16417648"] = dict(
    modality="Computed IR spectra (classical GAFF MD in LAMMPS + ML dipoles trained on DFT, quantum-corrected to 300 K) for 177,461 patent-derived organic molecules + DFT 1H/13C NMR chemical shifts (MD-sampled frames) for 1,255 molecules - modelled, not measured",
    spectral_range_original_min=0.33359745, spectral_range_original_max=4003.1694, spectral_range_original_unit="cm-1",
    num_spectral_channels=12000, sampling_interval=0.3336, sampling_interval_unit="cm-1",
    num_samples=177461,  # unique USPTO molecules with IR spectra (1,255 also with NMR)
    num_spectra=177461,  # IR spectra; plus 1,255 1H/13C NMR shift sets
    num_spectral_values=2129532000,
    spectral_target_relationship="SMILES / 3D structure -> anharmonic IR spectrum from dipole autocorrelation (2.5 fs sampling over 100 ps, Blackman window, Gaigeot-Sprik quantum correction) and thermally averaged DFT NMR shifts -> multimodal IR+NMR benchmark for structure elucidation and spectrum-prediction ML models",
    source_file="16417648.pdf (Zipoli, Alberts & Laino 2025 Sci. Data 12:1375); IR_data_chunk001-009_of_009.parquet (id, smiles, type, Frequency(cm^-1), ir_spectra); NMR_data.parquet (1,255 molecules, frames, averaged shifts, std); ERROR_PRED_TRUE_DIPOLE.zip (dipole ML error analysis: 3,292 npy, 1,647 png, 1,646 txt); scripts tar.gz; README.md",
    confidence=0.9,
)

R["15374056"] = dict(
    modality="1H NMR spectroscopy (Bruker Avance 500 MHz, 1D NOESY-presat) of rat faecal extracts for metabolomics of Polygoni Multiflori Radix Praeparata polysaccharide treatment in ischemic stroke",
    spectral_range_original_min=-5.6, spectral_range_original_max=15.2, spectral_range_original_unit="ppm",
    num_spectral_channels=16384,
    num_samples=72,  # faecal samples (71 experiment folders + 1 zipped experiment '83')
    num_spectra=72,
    num_spectral_values=1179648,  # processed 1r real spectra (16,384 points each); raw FIDs 32k complex points
    spectral_target_relationship="Binned 1H NMR resonances (0.005 ppm, water 4.5-5.5 ppm excluded, PQN-normalised) -> PCA / OSC-PLS-DA separation of sham, MCAO/R model and low/high-dose PMP groups; PMP raises faecal SCFAs (acetate, propionate, butyrate) and amino acids, linked to gut microbiota (16S rRNA) and reduced infarct volume",
    source_file="15374056.pdf (Ruan, Wang, Zheng, Zheng, Qing, Lin, Tao, Wang, Wang & Ge 2025 Front. Pharmacol., doi:10.3389/fphar.2025.1580055); 1H-NMR-pmp/ 71 Bruker TopSpin experiment folders (fid, acqus, pulseprogram, pdata/1: 1r, 1i, procs, title 'ZMY-n') + 83.zip",
    confidence=0.8,
)

R["15881845"] = dict(
    modality="Computed harmonic IR (and 2 Raman) vibrational spectra and TD-DFT UV excitations (Gaussian, B3LYP-D3BJ/6-31+G(d,p), vacuum and SMD water) of a hypothetical S/P-oxide heteropolymer and small Venus-cloud molecules - output logs, modelled not measured",
    spectral_range_original_min=14.0171, spectral_range_original_max=3931.7799, spectral_range_original_unit="cm-1",
    num_samples=29,  # species with frequency jobs (S4 crown, C2, C3, P5S5, P6S6; H2SO4, H3PO4, SO2, SO3, HPO3, H2S, PH3, H2O, O2, H3O+, P4O10; 13 radicals/ions), most in vacuum and SMD water
    num_spectra=53,  # 52 frequency (IR stick) jobs + 1 TD-DFT job (100 states, 155-190 nm)
    num_spectral_values=1130,  # harmonic modes with IR intensities
    spectral_target_relationship="Harmonic frequencies/IR intensities (P=O, S=O stretches and fingerprint bending modes of the S4-symmetric crown heteropolymer vs H2SO4, H3PO4, SO2, SO3) and TD-DFT excitations below 190 nm -> vibrational spectroscopy + mass spectrometry suggested for detecting carbon-free heteropolymers in Venus' clouds; polymers unlikely to be the unknown UV absorber; thermochemistry gives thermodynamic/kinetic stability in concentrated sulfuric acid",
    source_file="15881845.pdf (Madan, Arabi Aliabadi, Huhtasaari, Matic, Hogedal, Kaminska, Nilsson, Stark, Izquierdo-Ruiz, Sandstrom & Rahm 2025 QRB Discovery, doi:10.1017/qrd.2025.10012); 'All Log Files' (111 Gaussian .log + 107 .com: Kinetic Stability, Thermodynamic Stability, Polymer_Energies, Other Molecules Used; __MACOSX copies)",
    confidence=0.5,
)

R["14880579"] = dict(
    modality="High-throughput UV-Vis absorption spectroscopy of crude reaction mixtures (CRAIC microspectrometer on a pipetting robot; Thermo NanoDrop plate spectra) with spectral unmixing, plus 785 nm Raman and 1H NMR (Bruker 400/600 MHz, Spinsolve 80 MHz) of selected samples",
    spectral_range_original_min=190, spectral_range_original_max=870, spectral_range_original_unit="nm",
    sampling_interval=0.433, sampling_interval_unit="nm (CRAIC 1,039 points over 350-800 nm; NanoDrop 1 nm; Raman 51-2891 cm-1, 2,048 points)",
    num_samples=29077,  # crude-mixture wells measured on the CRAIC microspectrometer (several reactions/conditions; NanoDrop on further plates)
    num_spectra=49647,  # 29,077 CRAIC absorbance + 18,957 NanoDrop well spectra + 1,613 Raman (+ 752 dark/reference scans, ~550 NMR spectra not counted)
    num_spectral_values=45430790,  # 30,371,201 CRAIC + 11,760,261 NanoDrop + 3,299,328 Raman points
    spectral_target_relationship="Crude UV-Vis spectra at each condition of multidimensional reaction 'hyperspaces' (concentrations, temperature) are fitted as linear combinations of calibrated reference spectra of purified products/by-products (spectral unmixing, Beer-Lambert) -> yields of E1, SN1, Claisen-Schmidt, Ugi-type, Hantzsch and other reactions over thousands of conditions, anomaly detection and mechanistic network models; NMR/Raman confirm identities",
    source_file="14880579.pdf (Jia, Frydrych, Sobolev, Wong, Prajapati, Matuszczyk, Bilgi, Gadina, Ahumada, Moldagulov, ... Grzybowski 2025 Nature 645:922); data.zip (6.9 GB: craic_microspectrometer_measurements, multicomp-reactions, simple-reactions, BPRF (NMR, raman, nanodrop_spectra, calibrations), nanodrop-spectrophotometer-measurements; .msp spectra, .npy calibrations, pickles, png fits); github-code-repository.zip (robowski code); HyperspaceViewer zips",
    confidence=0.75,
)

R["16758266"] = dict(
    modality="Broadband (580-1313 nm) femtosecond time-resolved pump-probe reflectivity spectroscopy of Pr0.5Ca1.5MnO4 (12 fs, 1780 nm pump; NOPA probe) vs temperature and fluence, plus static 1300 nm rotating-waveplate birefringence vs temperature",
    spectral_range_original_min=580.31, spectral_range_original_max=1312.88, spectral_range_original_unit="nm",
    num_spectral_channels=1088, sampling_interval=0.674, sampling_interval_unit="nm (mean pixel spacing of the calibrated wavelength axis)",
    num_samples=11,  # temperatures 20-350 K on one PCMO crystal (PCMO46), each with 10 pump fluences x 4 repeats
    num_spectra=642400,  # 11 files x 40 scans x 365 delays x 4 channel spectra (CH1/CH2 pump on/off)
    num_spectral_values=698931200,
    spectral_target_relationship="Pump-induced reflectivity change dR/R(lambda, t) from pump-on/off probe spectra over -0.3 to +3.0 ps delays -> ultrafast dynamics of charge/orbital order in the layered manganite (coherent oscillations, decay times) as a function of temperature (20-350 K, across the ordering transition) and pump fluence (calibrated stage positions); PCA/k-means clustering of transient spectra; static birefringence (1300 nm, 202-361 K) tracks the symmetry change",
    source_file="16758266.pdf (Johnson, Amuah, Brahms & Wall 2020 Sci. Rep. 10:4690 - pump/probe pulse method paper cited by the deposit; no dataset article); Emmanuel Pump Probe/Fscan 11 HDF5 (Calib/wavelength_axis, Fluence_calib; Scan000000-039: CH1/CH2_on/off 365 x 1088, delay_time, fluence_position), BTscan 47 HDF5 (raw/processed waveplate-angle traces), 4 Python analysis scripts (re-downloaded 2026-10-21)",
    confidence=0.75,
)
