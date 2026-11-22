# Batch6 per-record spectroscopy metadata (26-column SPECTRAL_SCHEMA), curated from
# paper (C:\Users\Admin\RAG\2\papers\<id>.pdf) + dataset (D:\Batch6_datasets\<id>_<title>\).
# Only the 30 records that contain spectra are kept; the 19 records without spectra were moved
# to D:\Batch6_no_spectra (see NO_SPECTRA below) and are not part of the batch6 parquet files.
# 17309849.pdf (biochar cross-linking, IJAR) has no dataset folder and is not a Batch6 record.
# Only known keys are given; curation/build.py fills nulls and derives nm/cm-1 conversions.
R = {}

# Records removed from Batch6 because the dataset holds no spectra (record id -> reason).
NO_SPECTRA = {
    "17044261": "annual saline-soil identification / salinity-degree GeoTIFF maps (1985-2024, Landsat-derived) + EC sampling points with B10/SIT/PDI indices and a MATLAB model - no spectra",
    "17083067": "article PDF only (oven-dried yacon optimisation, IJAR)",
    "17174485": "OptoSkin time-of-flight sensor histograms (HDF5, 3x64 ToF bins) for an FTIR (frustrated total internal reflection) tactile skin - temporal histograms, not spectra",
    "17187559": "PMIRD gap-filled subset (5.5 GB .rds): posterior draws (8,000) of 25 MIR-predicted peat properties for 3,327 measurements - predictions only, the spectra themselves are not included",
    "17403124": "article PDF only (systematic review on mycodegradation of plastic, IJAR)",
    "17559828": "glacier mass-balance model inputs/outputs (AWS forcing, Landsat/remote-sensing GeoTIFFs, T&C model, MATLAB post-processing) - no spectra; Model_outputs.zip (7.3 GB) is not a readable zip",
    "17610806": "supplementary-material PDF only (microplastics in Ugandan wastewater; FTIR spectra only as figures)",
    "17675424": "IODP Exp 321 interstitial-water composite report (wet chemistry)",
    "17693395": "OralEpitheliumDB H&E histology ROI images (RGB TIFF/JPG) + segmentation masks - no spectra",
    "17716312": "murine gut metagenome-assembled genomes (FASTA, GenBank, MAG metrics/taxonomy) - no spectra",
    "17783185": "IODP Exp 320 interstitial-water composite report (wet chemistry)",
    "17790337": "download failed - 'multimodal_CRC_dataset.zip' (24.3 GB) is entirely zero-filled and a 369 MB .part file remains; the Zenodo record holds FT-IR imaging of colorectal cancer and needs re-downloading",
    "17875094": "download failed - 'UV-Vis.tar' (808 MB) and 'quantum_chemical_calculations.tar.7z' (2.96 GB) are entirely zero-filled; only HPLC_maps.tar (HPLC yield maps, no spectra) is intact - needs re-downloading",
    "17936488": "empty dataset folder (no files downloaded)",
    "17978895": "IODP Exp 320T interstitial-water composite report (wet chemistry)",
    "18106591": "article PDF only (sulfonic grafting on recycled cellulosic fabrics, IJAR)",
    "18264745": "article PDF only (TPS/EVA biodegradable films, IJAR)",
    "18334203": "article PDF only (Immunim tincture standardisation, IJAR)",
    "18370879": "download failed - 'Fishlake.zip' (9.2 GB) is entirely zero-filled; record is AVIRIS-3-derived canopy water content maps (derived product) and needs re-downloading",
}

# ---------------------------------------------------------------------------
# IODP JOIDES Resolution shipboard colour reflectance (paper = Exp 320/321 Preliminary Report)
# ---------------------------------------------------------------------------
_PAPER_320_321 = "Proc. IODP Exp 320/321 Preliminary Report 'Pacific Equatorial Age Transect' (same 21-page PDF supplied for 17675424, 17676297, 17783185, 17783544)"

R["17676297"] = dict(
    modality="VIS diffuse reflectance spectroscopy and colorimetry (RSC) of split-core section halves (Ocean Optics USB4000 + integrating sphere on the SHMSL)",
    spectral_range_original_min=380, spectral_range_original_max=700, spectral_range_original_unit="nm",
    num_spectral_channels=3837, sampling_interval=2, sampling_interval_unit="nm (README '~2 nm bins'; raw .oov spectra hold 3,837 values without a wavelength axis)",
    num_samples=1840,  # non-empty per-section .oov files (5 further files are 0 bytes)
    num_spectra=96873,  # calibrated raw spectra in the <RAW> blocks
    num_spectral_values=371701701,  # 96,873 x 3,837
    spectral_target_relationship="Calibrated reflectance counts of sediment surfaces -> CIE XYZ and L*a*b* (98,800 reduced rows) vs depth in 7 holes (U1337A-D, U1338A-C) of the Pacific Equatorial Age Transect for lithostratigraphy (carbonate vs radiolarian/diatom ooze) and hole-to-hole correlation",
    source_file=f"17676297.pdf ({_PAPER_320_321}, Exp 321); RSC-README.txt; data_by_hole (7 csv) + scaled/compiled-scale/splice variants; supplementary_material.zip raw_data_files (1,845 *.oov: <MULTI> L*a*b*/XYZ + <RAW> calibrated_spectra per offset) + standards_measured blank csv",
    confidence=0.7,
)

R["17783544"] = dict(
    modality="VIS diffuse reflectance spectroscopy and colorimetry (RSC) of split-core section halves on the SHMSL (Minolta CM-2600d spectrophotometer early in Exp 320, then Ocean Optics USB4000 + integrating sphere)",
    spectral_range_original_min=380, spectral_range_original_max=700, spectral_range_original_unit="nm",
    sampling_interval=10, sampling_interval_unit="nm (Minolta, 31 values 400-700 nm); USB4000 raw spectra 3,837 values without wavelength axis",
    num_samples=4140,  # non-empty per-section .oov files (6 further files are 0 bytes)
    num_spectra=155401,  # 98,694 Minolta + 56,707 USB4000 calibrated spectra
    num_spectral_values=220644273,  # 98,694 x 31 + 56,707 x 3,837
    spectral_target_relationship="Calibrated reflectance of sediment surfaces -> CIE XYZ and L*a*b* (114,404 reduced rows) vs depth in 16 holes at Sites U1331-U1336 for lithostratigraphy and correlation across the Eocene-Miocene equatorial Pacific transect",
    source_file=f"17783544.pdf ({_PAPER_320_321}, Exp 320); RSC-README.txt; data_by_hole (16 csv) + scaled/compiled-scale/splice variants; supplementary_material.zip raw_data_files (4,146 *.oov) + standards_measured blank csv",
    confidence=0.7,
)

# ---------------------------------------------------------------------------

R["17099733"] = dict(
    modality="Quantum-cascade-laser (QCL) mid-IR hyperspectral transmission imaging (Daylight Spero-QT 340) of paraffin-embedded colorectal-cancer PDX tumour sections",
    spectral_range_original_min=952, spectral_range_original_max=1800, spectral_range_original_unit="cm-1",
    num_spectral_channels=213, sampling_interval=4, sampling_interval_unit="cm-1",
    num_samples=40,  # tissue sections from 18 mice (2 PDX models x vehicle/FOLFOX/ABT/COMBO)
    num_spectra=9216000, num_images=40, num_pixels=9216000, image_height=480, image_width=480,
    num_spectral_values=1963008000,  # 40 x 230,400 pixels x 213 wavenumbers
    spectral_target_relationship="Per-pixel fingerprint spectra (amide I/II, lipid, phosphate 965 cm-1, nucleic-acid bands) of chemotherapy-resistant CRC0076 vs sensitive CRC0344 PDX tumours -> attention-based multiple-instance deep learning (DREAMER-S) classifies chemosensitivity; attention maps and SHAP identify discriminating wavenumbers",
    source_file="17099733.pdf (Rafsanjani, Dooney, Suresh, O'Farrell, Jarzabek, Shiels, Byrne, Prehn & Meade 2025 bioRxiv 10.1101/2025.10.02.679953, DREAMER-S); 40 MATLAB v5 .mat (wn 1x213, s 213x230400, w=h=480) named <model>_<treatment>_<mouse>-<section>",
    confidence=0.85,
)

R["17103331"] = dict(
    modality="Optical and near-IR spectroscopy of the reddened Type Ia supernova SN 2010ev (VLT X-shooter UVB/VIS/NIR, Gemini GMOS-S, du Pont WFCCD; nebular-phase spectra)",
    spectral_range_original_min=3150, spectral_range_original_max=24789.6, spectral_range_original_unit="Angstrom",
    sampling_interval=0.4, sampling_interval_unit="Angstrom (X-shooter; GMOS 0.91, WFCCD 1.92, nebular 2.78 A)",
    num_samples=1,  # SN 2010ev
    num_spectra=25,  # 9 NIR + 14 optical + 2 nebular epochs
    num_spectral_values=512216,
    spectral_target_relationship="Time series (-7 to +300 d) of Si II, Ca II, S II, Fe line velocities and ratios -> high-velocity-gradient SN Ia classification; invariant Na I D and DIBs (5780/6283 A) trace host-galaxy ISM reddening (low RV ~1.5); NIR spectra and nebular lines compared with explosion models",
    source_file="17103331.pdf (Gutierrez, Gonzalez-Gaitan, Folatelli, Pignata, Anderson, Hamuy, Morrell, Stritzinger, Taubenberger, Bufano et al. 2016 A&A, arXiv:1601.07863); SN2010ev_spectra.zip: NIR/ 9 .dat, Optical/ 14 .dat (date-<yyyymmdd>_tel-<VLT|GEM|DP>_inst-<XS|GM|WF>), Nebular/ 2 .dat (wavelength, flux)",
    confidence=0.85,
)

R["17195859"] = dict(
    modality="ATR-FTIR spectroscopy (PerkinElmer Spectrum Two) of depolymerised PET residue (REX-PET), commercial terephthalic acid and Rhodococcus-produced TAGs and PHBV",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3601, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=6,  # REX-PET batches 1-3, commercial TPA, TAGs, PHBV
    num_spectra=6,
    spectral_target_relationship="Carboxylate/aromatic ring bands (1557, 1391, 1088, 1023 cm-1) confirm disodium terephthalate in REX-PET vs TPA; ester C=O 1744 and C-H 2853/2922 cm-1 identify TAGs; PHBV C=O 1723 and C-O-C bands confirm polyhydroxyalkanoate produced by Rhodococcus sp. Ave7 from PET-derived TPA",
    source_file="17195859.pdf (Rebocho, Torres, Koninckx, Stragier, Attallah, Mojicevic, Tas, Brennan Fournet, Reis & Freitas 2025 Biotechnol. Environ. 2:5); 6 CSV (Wavenumber;Intensity) + readme.txt",
    confidence=0.85,
)

R["17202055"] = dict(
    modality="FTIR spectroscopy (PerkinElmer System 2000, %T) of sugar-beet-leaf protein concentrates from alkali, ultrasound-, enzyme- and combined-assisted extraction",
    spectral_range_original_min=650, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    num_spectral_channels=3351, sampling_interval=1, sampling_interval_unit="cm-1",
    num_samples=4,  # AIP, U-AIP, E-AIP, UE-AIP
    num_spectra=4,
    spectral_target_relationship="Amide I (1600-1700), amide II (1500-1600), primary amine (3300-3500), sulfate/sulfoxide S=O and cellulose C-O / glycosidic C-H bands compare protein secondary structure and co-extracted polysaccharides across extraction methods; linked to yield, purity, colour, density and SEM microstructure",
    source_file="17202055.pdf (Akyuz, Tekin, Aksoy Caf & Ersus 2026 Sugar Tech 28:172); 'Sugar Tech_FTIR+SEM.xlsx' (FTIR sheet, values x1e6 scaled), 'Sugar Tech_Raw Data.xlsx' (dry matter, yield, density, Carr/Hausner, colour)",
    confidence=0.75,
)

R["17227622"] = dict(
    modality="Band-resolved (16 RRTM longwave bands) downward/upward/net longwave irradiance computed with the RRTM radiative-transfer model from ERA5 profiles - modelled broadband spectral fluxes, not measured spectra",
    spectral_range_original_min=10, spectral_range_original_max=3250, spectral_range_original_unit="cm-1",
    num_spectral_channels=16,
    num_samples=443,  # NetCDF cases: TMY months, heatwave episodes, Spanish/French grids, single-site summers
    num_spectra=6818736,  # time x grid-point profiles of band-resolved surface downward flux (sd)
    num_spectral_values=109099776,  # 6,818,736 x 16 bands (sd only; su, sn, tu have the same size)
    spectral_target_relationship="ERA5 temperature/humidity/cloud fields -> RRTM-computed 16-band surface downward LW flux (plus upward, net and TOA) compared with ERA5 avg_sdlwrf (r 0.8-0.95, RMSE ~6-18 W m-2) for radiative-cooling / building-energy applications in European, US and Middle-East cities",
    source_file="17227622.pdf (Mayer, Haimberger & Mayer 2023 Earth Syst. Dynam. 14:1085 - ERA5 air-sea heat flux paper, related reanalysis study, not the dataset paper); wp2_data.zip: 443 NetCDF (sd/su/sn/tu x 17 lw_bands incl. broadband total, ERA5 fluxes, t2m, tcwv, cloud), rrtm_bands.txt, 4 *.readme validation tables",
    confidence=0.5,
)

R["17241207"] = dict(
    modality="Automated on-line reaction monitoring with benchtop spectrometers: 80 MHz 1H/19F NMR (Magritek Spinsolve), UV-Vis transmission (2048-pixel CCD spectrometer), ATR/flow IR and X-band EPR",
    spectral_range_original_min=198.589, spectral_range_original_max=767.508, spectral_range_original_unit="nm",
    num_spectral_channels=2048, sampling_interval=0.279, sampling_interval_unit="nm (UV-Vis; IR 399.9-4000.1 cm-1 at 0.241 cm-1, 14,936 pts; EPR 3394-3494 G, 1,024 pts; NMR in ppm)",
    num_samples=17,  # reaction/monitoring series (lophine, formose, imine, BZ, permanganate, azide, NDI, terpene, photo ...)
    num_spectra=6023,  # 2,992 NMR + 2,873 UV-Vis + 140 IR + 18 EPR
    num_spectral_values=7993376,  # UV-Vis + IR + EPR points (NMR FIDs/spectra not counted)
    spectral_target_relationship="Time series of crude reaction spectra -> similarity measures (Jaccard index, cosine/Pearson) between consecutive spectra detect reactivity, kinetics (Arrhenius analysis of lophine formation by NMR), plateau/end-point and oscillations (Belousov-Zhabotinsky by UV-Vis) without reaction-specific models; azide formation tracked at 2097/2173 cm-1",
    source_file="17241207.pdf (Rauschen, Thomas & Cronin 2025 Angew. Chem. Int. Ed. e21519); 'raw spectra.zip' (3.3 GB): NMR/ 13 series (data.1d, nmr_fid.dx, acqu.par, processing.script, jpg, pickles), UVVis/ BZ_v3, NGR2-4, perm_v2 (2,873 csv), IR/azide_v2 (140 csv + png), EPR/NDI_monitoring (Bruker DSC/DTA/ASC); Figures.zip (svg, notebooks, csv)",
    confidence=0.75,
)

R["17395989"] = dict(
    modality="ATR-FTIR spectroscopy (Thermo Nicolet iS10) of castor-oil-based bio-polyurethane films with bacterial-biomass fillers (+ XRD, TGA/DTGA, tensile tests)",
    spectral_range_original_min=399.69, spectral_range_original_max=4000.29, spectral_range_original_unit="cm-1",
    num_spectral_channels=7469, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=4,  # PU1 (neat), PU-F1, PU-F2, PU-F3
    num_spectra=8,  # a and b sets per film
    spectral_target_relationship="Disappearance of castor-oil O-H (3400 cm-1), urethane N-H (3330), C=O (1700-1730) and C-N/N-H (1530) bands confirm urethane formation; filler-related changes in H-bonded carbonyl and CH2 bands correlate with thermal stability, crystallinity, mechanical properties and biofilm/cytotoxicity behaviour",
    source_file="17395989.pdf (Venkateswara Rao, Ponjavic, Guzik, Maslak, Zimowska, Nikodinovic-Runic, Aleksic et al. 2025 J. Polym. Environ. 33:2443); Dataset.7z: 8 FTIR csv (wavenumber, intensity), 4 XRD, 4 TGA, 4 DTGA, 4 mechanical csv, 3 png figures; readme.txt",
    confidence=0.85,
)

R["17435008"] = dict(
    modality="ATR-FTIR (JASCO FT/IR-7600) and UV-Vis transmittance (JASCO V-600) of PMMA and PMMA-Pd nanocomposite films",
    spectral_range_original_min=399.193, spectral_range_original_max=4000.6, spectral_range_original_unit="cm-1",
    sampling_interval=0.964, sampling_interval_unit="cm-1 (FTIR, 3,736 pts; UV-Vis 200-850 nm at 0.5 nm, 1,301 pts)",
    num_samples=3,  # virgin PMMA, PMMA + 1 % Pd, PMMA + 5 % Pd
    num_spectra=6,  # 3 FTIR + 3 UV-Vis
    num_spectral_values=15111,
    spectral_target_relationship="C=O stretch (1730 cm-1), C-H stretching (2942/2839 cm-1) and bending bands track Pd-induced changes in PMMA; UV-Vis transmittance edge (pi-pi* <240 nm, n-pi* ~290 nm) and ~62 % visible transmittance drop with Pd loading support use as light-shielding packaging",
    source_file="17435008.pdf (Cutroneo, Silipigni, Torrisi, Franco, Malinsky & Torrisi 2025 Radiat. Eff. Defects Solids); 'Fig 2 FTIR.txt' (wavenumber + 3 %T columns), 'Fig 3 UVVIS.txt' (wavelength + 3 %T columns)",
    confidence=0.85,
)

R["17493261"] = dict(
    modality="Laboratory multispectral imaging (8-channel LOROS simulator of MMX/OROCHI, 400-950 nm filters) + spectrometer-measured lamp, filter-transmission and reference reflectance spectra (Ocean Optics HR4)",
    spectral_range_original_min=195.287, spectral_range_original_max=1128.68, spectral_range_original_unit="nm",
    num_spectral_channels=8, sampling_interval=0.256, sampling_interval_unit="nm (HR4 lamp/filter spectra, 3,648 pts; imager has 8 bands 400-950 nm)",
    num_samples=4,  # targets: slant-edge MTF target, Spectralon SCT99, SCT5 (dark), Nogoya CM2 chondrite reference spectrum
    num_spectra=40,  # 1 lamp SPD + 8 filter + 2x7 system responses + 8 synthesized OROCHI filters + 2 QE + 1 solar + 2 high-res reflectance + 4 resampled
    num_images=24459,  # TIFF frames (MTF, photon/dark transfer, Spectralon raw/processed); + 128 FITS products
    num_spectral_values=89420,  # points of the 40 component spectral curves (images not counted)
    spectral_target_relationship="Filter transmissions x lamp SPD x sensor QE -> system spectral response used to resample high-resolution reflectance (Nogoya, SCT5) to the 8 OROCHI/LOROS bands; photon-transfer and dark-transfer image series give gain, read noise, dark current, linearity and SNR; SCT5 reflectance retrieved within uncertainty validates multispectral radiometric calibration",
    source_file="17493261.pdf (Stabbins & Kameda 2026 Prog. Earth Planet. Sci. 13:8); dataset/: A_modulation_transfer_function (TIFF + MTF Mapper txt), B_system_response (LOROS/OROCHI csv), C_expected_reflectance (csv), D_radiometric_calibration (23,483 TIFF + csv), E_dark_spectralon_validation (raw/processed TIFF, FITS, roi csv, pdf); README.md per subset",
    confidence=0.7,
)

R["17533257"] = dict(
    modality="Infrared photodissociation (IRPD) spectroscopy of He-tagged gold-acetylene cluster ions Au_n+/-(C2H2)_m in the C-H stretch region (tunable EKSPLA OPO, HToF mass spectrometer) + DFT",
    spectral_range_original_min=2850, spectral_range_original_max=3400, spectral_range_original_unit="cm-1",
    sampling_interval=5, sampling_interval_unit="nm laser steps (~5 cm-1); laser bandwidth <10 cm-1",
    num_samples=32,  # Au_n(C2H2)_m cations and anions, n <= 4, m <= 4
    spectral_target_relationship="Red-shift and splitting of acetylene antisymmetric/symmetric C-H stretches (e.g. 3189-3196 and 3256-3259 cm-1 for Au+ complexes vs 3288.7 cm-1 free C2H2) vs cluster charge and size -> pi-ligand activation strength; compared with DFT binding energies, ESP charges and isomer structures",
    source_file="17533257.pdf (Reichegger, Knabl, Schmidt, Reider, Oncak, Scheier & Lushchikova 2025 RSC Adv. 15:44304, doi:10.1039/d5ra06762f); AuC2H2+.zip / AuC2H2-.zip: Origin .opju (IR spectra), ToF mass spectrum txt (248,584 pts), RunID xlsx (runs, lambda ranges); Final plots.zip (22 PDF); DFT_AuC2H2.zip (1.9 GB) unreadable/truncated",
    confidence=0.55,
)

R["17559551"] = dict(
    modality="FTIR, UV-Vis absorption and XPS of polypropylene-derived sulfonate surfactants (+ HMBC/13C NMR in MestReNova, APCI-MS, GC, PXRD, TGA/DSC source data)",
    spectral_range_original_min=400.1635, spectral_range_original_max=4000.188, spectral_range_original_unit="cm-1",
    sampling_interval=0.482, sampling_interval_unit="cm-1 (FTIR, 7,468 pts; UV-Vis 183-1020 nm, 1,675 pts; XPS binding energy in eV)",
    num_samples=8,  # PP-T1, PP-T2, PP-T2-S, PP-ST, PP-STW, SLS and SDBS references, PP-T1-5h-S
    num_spectra=22,  # 2 FTIR + 12 UV-Vis + 8 XPS region spectra (NMR in 6 .mnova not counted)
    num_spectral_values=35036,  # FTIR + UV-Vis points
    spectral_target_relationship="FTIR sulfonate S=O and alkenyl C=C bands plus XPS S 2p/O 1s states confirm sulfonation of fractionated PP-derived olefins; HMBC NMR identifies olefinic sulfonate structures; UV-Vis net absorption over 1-7 days tracks surfactant stability vs SDBS",
    source_file="17559551.pdf (Xu, Zhang, Wang, Yang, Sun, Chen, Liu, Xu, Chen, Zhang & Pan 2025 Nat. Commun. 16:11611); DATASET.zip: 15 per-figure xlsx (S25c FTIR, S25d-g XPS, S31 UV-Vis, APCI, GC, PXRD, TGA/DSC ...) + 6 .mnova NMR + Read Me.txt; 'figure 5.ai'",
    confidence=0.75,
)

R["17607147"] = dict(
    modality="Phase-sensitive sum-frequency vibrational spectroscopy (PS-SFVS; 30 ps Nd:YAG + OPA/DFG) of SDS/NaCl solution-air interfaces in the C-H/O-H stretch region",
    spectral_range_original_min=2800, spectral_range_original_max=3801, spectral_range_original_unit="cm-1",
    num_spectra=41,  # Im chi(2) and SF intensity spectra in the source-data sheets
    num_spectral_values=2294,
    spectral_target_relationship="Im chi(2)eff of free-OH (3700 cm-1), bonded-OH (3000-3600 cm-1) and C-H modes vs SDS (0.002-16 mM) and NaCl concentration -> diffuse-layer response and DS- coverage give Na+ counterion binding in the inner Helmholtz layer via modified Gouy-Chapman / Langmuir models (dG = -38.97 kJ/mol)",
    source_file="17607147.pdf (Peng, Gu & Tian, 'Observation of counterion binding in the inner Helmholtz layer at the ionic surfactant-water interface', preprint); 11 'Source Data (Extended Data) Fig. n.xlsx' (spectra + surface charge/tension/coverage tables and model curves)",
    confidence=0.8,
)

R["17628291"] = dict(
    modality="UV-Vis absorption (SLM DW2000) of N719 dye solutions under illumination, ATR-FTIR (Bruker INVENIO-S, Ge ATR) of patterned photoanodes, ToF-SIMS mass spectra and ion images",
    spectral_range_original_min=200, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=601, sampling_interval=1, sampling_interval_unit="nm (UV-Vis; FTIR 599-3997 cm-1 at 1.43 cm-1, 2,384 pts)",
    num_samples=4,  # N719 with/without TiO2 under Xe-lamp illumination, illuminated vs covered photoanode areas
    num_spectra=73,  # 54 UV-Vis + 19 FTIR (+ 12 ToF-SIMS mass spectra)
    num_images=3, image_height=512, image_width=512,  # ToF-SIMS NCO-, NCS-, SO4- maps
    num_spectral_values=77750,
    spectral_target_relationship="Changes of N719 bipyridine pi-pi* and isothiocyanate-related MLCT bands over 10 h Xe-lamp illumination with vs without TiO2, while FTIR bipyridine ring modes (1540/1436 cm-1) persist -> TiO2-catalysed multi-step degradation of the isothiocyanate (NCS) ligand underlies 'photovoltaic photograph' patterning; ToF-SIMS NCO-/SO4- maps confirm",
    source_file="17628291.pdf (Robert, Fransaert, Awouters, Marchal, Adriaensens, Valcke & Manca 2025 arXiv:2507.03008); 52 time-stamped UV-Vis csv (with/without TiO2), 2 UV-Vis xlsx (EtOH/NaOH extraction), 19 Bruker .dpt FTIR, 12 ToF-SIMS channel exports + 12 peak lists, 3 ToF-SIMS 512x512 ion-image dumps",
    confidence=0.8,
)

R["17659785"] = dict(
    modality="FTIR spectroscopy of Scots pine (Pinus sylvestris) wood meal by cambial-age class (+ CHNS, extractives, holocellulose, alpha-cellulose, DP, pH, crystallinity index)",
    spectral_range_original_min=400.1635, spectral_range_original_max=4000.188, spectral_range_original_unit="cm-1",
    num_spectral_channels=7468, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=10,  # cambial-age classes 2-5 ... 46-50 years (pooled from 10 butt logs)
    num_spectra=30,  # 3 replicates per class (+ 10 average spectra)
    spectral_target_relationship="Wood FTIR bands (cellulose 895/1430 cm-1 -> crystallinity index CI = A1430/A895, lignin 1510, carbonyl 1730, OH 3400 cm-1) vs cambial age from pith to bark, alongside chemical composition, density, contact angle, EMC, fibre dimensions and dimensional stability",
    source_file="17659785.pdf (Sooriyaarachchi, Jaber, Covarrubias, Ubhayasekera, Asiegbu & Mowbray 2011, Sp-AMP antimicrobial protein - UNRELATED to this wood-property dataset); Chemical_Composition.xlsx (FTIR, CI, COHN, Exstr, Hol_cel, Cel, DP, pH sheets) + 6 property xlsx (annual rings, contact angles, density, dimensional stability, EMC, fibre dimensions)",
    confidence=0.6,
)

R["17659931"] = dict(
    modality="FTIR spectroscopy of silver birch (Betula pendula) wood meal by cambial-age class (+ extractives, cellulose, pH, crystallinity index)",
    spectral_range_original_min=400.6456, spectral_range_original_max=4000.188, spectral_range_original_unit="cm-1",
    num_spectral_channels=7467, sampling_interval=0.482, sampling_interval_unit="cm-1",
    num_samples=6,  # cambial-age classes (2-5 ... 26-35 years) pooled from 9 butt logs
    num_spectra=18,  # 3 replicates per class (+ 6 average spectra)
    spectral_target_relationship="Wood FTIR bands (cellulose 895/1430 cm-1 crystallinity index, xylan/hemicellulose acetyl C=O 1735, lignin 1505/1595, OH 3400 cm-1) vs cambial age, alongside extractives, cellulose, vessel proportion, density, contact angle, EMC, fibre and dimensional data",
    source_file="17659931.pdf (Engelhardt, Gilg, Richter & Sanchez-Ferrer 2024 Wood Sci. Technol. 58:379 - related birch adhesion study, not the dataset paper); 'Chemical properties.xlsx' (FTIR, CI, Extr, Cel, pH) + 7 property xlsx",
    confidence=0.65,
)

R["17663262"] = dict(
    modality="Polarised Raman (473/514/532/633 nm; LabRam HR800, Trivista 777) and IR reflectivity/absorption (Bruker Vertex 80, He cryostat) + THz spectra of polar antiferromagnet Co2Mo3O8 at 5-300 K",
    spectral_range_original_min=0, spectral_range_original_max=18000.1, spectral_range_original_unit="cm-1",
    sampling_interval=0.964, sampling_interval_unit="cm-1 (IR absorption; reflectivity 0.48/0.96, Raman 0.21-1.48, THz 0.11 cm-1)",
    num_samples=1,  # Co2Mo3O8 single crystals (ab- and ac-plane cuts)
    num_spectra=43,  # 7 absorption + 4 reflectivity + 30 Raman + 2 THz
    num_spectral_values=234123,
    spectral_target_relationship="Phonon frequencies, polarisation selection rules (A1/E1/E2) and temperature-dependent splittings/new modes below TN (~40 K) in Raman and IR test spin-group vs magnetic-space-group symmetry predictions and ab initio phonons; low-energy electronic (Co2+ multiplet) modes at 87/118/303/363 cm-1",
    source_file="17663262.pdf (Schilberth, Kondakor, Ukolov, Pawbake, Vasin, Ercem, Prodan, Tsurkan, Tsirlin, Faugeras, Lemmens, Penc, Kezsmarki, Bordacs & Deisenhofer 2025 arXiv:2508.09793); Phonons_in_CMO.zip: Absorption_<T>K.txt (7), Reflectivity_EIIa/EIIc_<T>K.txt (4), Raman_<laser>_<config>_<T>K.txt (30), THz_<T>K_EIIa.dat (2)",
    confidence=0.85,
)

R["17674612"] = dict(
    modality="Synthetic stellar spectra from PHOENIX model atmospheres (Goettingen library), resolution reduced to R = 5000 - modelled, not measured",
    spectral_range_original_min=300.012, spectral_range_original_max=2499.78, spectral_range_original_unit="nm",
    num_spectral_channels=31803, spectral_resolution=5000, spectral_resolution_unit="resolving power R = lambda/dlambda",
    sampling_interval=0.0577, sampling_interval_unit="nm (median; constant-R grid)",
    num_samples=19992,  # unique (Teff, log g, [Fe/H], [alpha/Fe]) models; one folder duplicated
    num_spectra=20487,  # files incl. 495 duplicates in 'FeH-0.5_alpha+1.0 (1)'
    num_spectral_values=651548061,  # 20,487 x 31,803
    spectral_target_relationship="Stellar parameters (Teff 2300-12000 K, log g 0-6, [Fe/H] -3.0 to +1.0, [alpha/Fe] -0.2 to +1.2) -> LTE PHOENIX ACES spectra (flux erg cm-2 s-1 nm-1) used as templates for fitting observed spectra and training spectral emulators",
    source_file="17674612.pdf (Husser, Wende-von Berg, Dreizler, Homeier, Reiners, Barman & Hauschildt 2013 A&A 553:A6, arXiv:1303.5632); 38 folders FeH<z>_alpha<a>_phoenixMedRes_R05000/ with 20,487 LTE_T<Teff>_logg<g>_..._R05000.txt (wavelength nm, flux)",
    confidence=0.85,
)

R["17732891"] = dict(
    modality="Portable ATR-FTIR spectroscopy (Agilent 4300 handheld, diamond ATR) of intact Scots pine needle, phloem and shoot tissue - averaged second-derivative spectra",
    spectral_range_original_min=677, spectral_range_original_max=3150, spectral_range_original_unit="cm-1",
    num_spectral_channels=899, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=2, sampling_interval_unit="cm-1 (approx.; trimmed regions)",
    num_samples=1130,  # tree x tissue x year averages (34 families, 3 tissues, 2023-2024, 4 orchards)
    num_spectra=1130,
    num_spectral_values=1015870,
    spectral_target_relationship="Savitzky-Golay 2nd-derivative FT-IR spectra -> PCA and sPLS-DA classify relative resistance of Pinus sylvestris families to Diplodia sapinea (lesion-length phenotypes); key regions: cell-wall polysaccharides 1000-1050/1140-1160, phenolics/proteins 1570-1680, lipids/cutin 2950-3140 cm-1",
    source_file="17732891.pdf (Sherwood et al. 2026 Front. For. Glob. Change, doi:10.3389/ffgc.2026.1755489); FTIR_Diplodia_avr_2der.csv (1,130 rows: metadata + 899 X<wavenumber> columns), Lesion data_R_TRIM.csv, Lesion_stats_R_TRIM.csv, R script",
    confidence=0.8,
)

R["17938435"] = dict(
    modality="Confocal Raman mapping (Renishaw inVia, 785 nm, WiRE .wdf) of dried biochemical mixture spots for a ground-truth explainable-AI experiment",
    spectral_range_original_min=97.896, spectral_range_original_max=3200.0, spectral_range_original_unit="cm-1",
    sampling_interval=1.10, sampling_interval_unit="cm-1 (16 truncated maps 349.5-1850.1 cm-1, 1,356 pts; 4 full maps 97.9-3200 cm-1 at 0.96 cm-1, 3,189 pts)",
    num_samples=16,  # 4 x 4 mixture spots (labels i_j)
    num_spectra=21072,  # 16 maps x ~1,005 spectra + 4 maps x ~1,240 spectra
    num_images=32,  # optical JPG views (with/without axes)
    num_spectral_values=37665312,
    spectral_target_relationship="Raman spectra of biomolecule mixtures with known composition (designed discriminating peaks, e.g. ~1001-1002 cm-1) -> CNN/ResNet classifiers; Spec-ReX causal-responsibility attribution maps compared with SHAP and Grad-CAM for peak localisation",
    source_file="17938435.pdf (Blake, Kelly, Kapllani-Mucaj, Wang, Thomas & Chockler 2026 Research Square rs-8338382, 'Causal Responsibility Based Explainable AI for Vibrational Spectroscopy Applied to Cancer Diagnostics'); LabData-...zip: 20 Renishaw .wdf maps (16 *_map_truncated + 4 map_i_1) + 32 jpg",
    confidence=0.75,
)

R["17939074"] = dict(
    modality="UV-Vis absorption of iron/bipyridine/trifluoroacetate photoelectrocatalyst solutions + 1H/13C/19F NMR (Bruker 300-600 MHz) of trifluoromethylated products (+ CV)",
    spectral_range_original_min=298, spectral_range_original_max=800, spectral_range_original_unit="nm",
    num_spectral_channels=252, sampling_interval=2, sampling_interval_unit="nm",
    num_samples=26,  # 4 catalyst mixtures + 22 NMR product folders
    num_spectra=80,  # 15 UV-Vis + 65 NMR FIDs
    num_spectral_values=3780,  # UV-Vis points
    spectral_target_relationship="MLCT band of [Fe(L1)3]2+ (542 nm, Beer-Lambert dilution series) and spectral changes of Fe(OTf)2/L1/NaO2CCF3/TFA mixtures under 405 nm light identify dual-role iron species (photoactive Fe-carboxylate + redox mediator); 19F/1H/13C NMR quantify CF3 product yields",
    source_file="17939074.pdf (Fernandez-Garcia, Cuadros, Bosque et al. 2026 Nat. Commun., doi:10.1038/s41467-026-69922-y); 'Raw Data - PhotoelectroCF3.zip': Raw-Data-UV-Vis.xlsx (3 sheets), Raw-Data-CV.xlsx, NMR Data/ 22 compound folders with Bruker fid/acqus/pdata (65 experiments); __MACOSX junk",
    confidence=0.75,
)

R["17989158"] = dict(
    modality="ATR-FTIR spectroscopy (Bruker Tensor 27, Ge crystal) of Keroplatus testaceus larval silk and Bombyx mori silk references (+ proteomics, qPCR, AlphaFold, mechanical tests, genome reads)",
    spectral_range_original_min=798.42, spectral_range_original_max=3997.89, spectral_range_original_unit="cm-1",
    num_spectral_channels=1660, sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=4,  # B. mori degummed, non-degummed, ND-s; K. testaceus
    num_spectra=16,  # 4 measurement positions per material (+ 4 averaged source-data spectra)
    num_spectral_values=26560,
    spectral_target_relationship="Amide I (1600-1700 cm-1) and amide II (1530-1550 cm-1) band shapes distinguish beta-sheet-rich B. mori fibroin from the proline-rich, PPII/disordered K. testaceus silk proteins identified by proteomics and secondary-structure prediction",
    source_file="17989158.pdf (Zurovec, Kmet, Opelka, Lopes et al. 2025 Research Square rs-8281234); raw_data.zip (FTIR.zip: 'FTIR raw data.xlsx' + 'Source data Fig.7.xlsx'; Alphafold, proteomics, qPCR, SDS-gel, mechanical, PPII prediction zips); source_data.zip; 2 FASTQ (6 GB each); movie zip unreadable (.part 0 bytes)",
    confidence=0.75,
)

R["18112037"] = dict(
    modality="Ground-based UV-VIS Multifilter Rotating Shadowband Radiometer (MFRSR) + AERONET retrievals of Saharan dust spectral AOD, single-scattering albedo and imaginary refractive index at 5 UV-blue wavelengths",
    spectral_range_original_min=325, spectral_range_original_max=440, spectral_range_original_unit="nm",
    num_spectral_channels=5,
    num_samples=1449,  # 30-min retrieval windows at Izana (Aug 2019 - Jul 2023)
    num_spectra=1449,  # each with AOD, SSA, REFR, REFI, asymmetry spectra at 325/332/340/380/440 nm
    num_spectral_values=7245,  # 1,449 x 5 wavelengths per retrieved quantity
    spectral_target_relationship="MFRSR total/diffuse irradiance ratios + AERONET AOD and size distribution -> radiative-transfer look-up-table retrieval of spectral imaginary refractive index k and SSA (325-440 nm) for dust (k increases toward UV), compared with AERONET SSA at 440 nm",
    source_file="18112037.pdf (Jethva, Krotkov, Torres, Mok, Labow, Lind, Eck, Gao, Janson, Simpson et al. 2025 EGUsphere-2025-4890); 23 monthly UV-VISMFRSR_Head582_Izana_Aerosol_Absorption_<yyyymm>.txt (52 fields), README.pdf, Figure.jpeg, DailyPlots.zip (115 jpg)",
    confidence=0.55,
)

R["18186126"] = dict(
    modality="Time-resolved IR difference spectroscopy (fs-pumped QCL/OPA probe with MCT array, rapid-scan and slow-scan FTIR Bruker Vertex 80v) of LOV photoreceptor proteins BsLOV, YF1 and PAL",
    spectral_range_original_min=1260.47, spectral_range_original_max=1800.51, spectral_range_original_unit="cm-1",
    sampling_interval=1.187, sampling_interval_unit="cm-1 (rapid-scan; ~4.1 cm-1 MCT-array pixels, 1.93 cm-1 slow scan)",
    num_samples=3,  # BsLOV, YF1, PAL
    num_spectra=426,  # time-resolved difference spectra (ps-ms, ms-s, s-h windows)
    num_spectral_values=29272,  # raw TR-IR (wavenumber, log time, dA) points
    spectral_target_relationship="FMN and protein marker bands (C4=O ~1627/1664/1675 cm-1, triplet 3FMN, adduct A390, signalling state) vs log time from picoseconds to hours -> global lifetime analysis (DAS) resolves the complete photocycle and signal propagation from the LOV domain to effector domains in YF1 (histidine kinase) and PAL (RNA-binding)",
    source_file="18186126.pdf (Herzog, Janke, Fischer, Heckmeier, Wei, Nag, Hartmann, Mulder et al. 2026 Phys. Chem. Chem. Phys. 28:2847); PCCP_Herzog2026_Data.zip: Fig2-Fig5, FigS2-S3 .dat (TR-IR maps, fits, residuals, DAS, kinetic traces, light-minus-dark spectra)",
    confidence=0.8,
)

R["18205062"] = dict(
    modality="ATR-FTIR (PerkinElmer Spectrum Two) of glucose-coated FeO@Fe3O4 nanoparticles + X-band EPR (Bruker ELEXSYS II-E500) DMPO spin-trapping time series of radical generation (+ XRD, TEM, toxicity data)",
    spectral_range_original_min=400, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1 (as-prepared; coated/glucose 2 cm-1); EPR 3300-3450 G, 2,000 pts, 9.456 GHz",
    num_samples=8,  # 3 FTIR samples (as-synthesised, glucose-coated, glucose) + 5 EPR conditions
    num_spectra=149,  # 3 FTIR + 146 EPR
    num_spectral_values=299203,
    spectral_target_relationship="Fe-O (~580 cm-1), glucose O-H/C-H/C-O bands confirm coating; DMPO spin-adduct EPR signal growth vs time at pH 5/7 shows Fenton-like *OH generation by bare nanoparticles rerouted to *OOH by the glucose coating (tunable catalytic reactivity), related to toxicity in 3D HepG2 spheroids",
    source_file="18205062.pdf (Morales Ovalle, Rozman, Winkler, Lima Jr. et al. 2026 Sci. Rep., doi:10.1038/s41598-026-52667-5); FeO_Fe3O4-Raw_data-FTIR.zip (3 .sp + .ASC), -EPR.zip (146 Bruker DSC/DTA + .dat), -XRD, -TEM (1.3 GB dm3/ser), -Synthesis; Raw Data - toxicity.zip; Readme.txt",
    confidence=0.8,
)

R["18311840"] = dict(
    modality="UV-Vis-NIR transmission and 45-degree reflectance spectroscopy (B&W Tek i-trometer BRC642E, halogen source) of continuous and pulsed low-power DC-sputtered Ti thin films on borosilicate glass",
    spectral_range_original_min=179.27, spectral_range_original_max=1129.24, spectral_range_original_unit="nm",
    num_spectral_channels=2048, spectral_resolution=0.6, spectral_resolution_unit="nm",
    sampling_interval=0.46, sampling_interval_unit="nm (polynomial pixel calibration; analysed range 350-950 nm)",
    num_samples=17,  # films by deposition time (continuous 30 s-20 min, pulsed 30 s-90 min) + clean substrates
    num_spectra=64,  # non-dark measurements (0/45/90 deg T, 45 deg R, halogen references) + 64 dark spectra
    num_spectral_values=131072,
    spectral_target_relationship="Transmittance and reflectance vs film thickness (sub-nm to 105 nm) -> optical evolution from island growth to continuous metallic Ti, compared with AFM roughness, XPS oxidation and four-point resistivity for continuous vs pulsed room-temperature sputtering",
    source_file="18311840.pdf (Reider, Kronthaler, Zappa, Menzel, Laimer & Scheier 2025 Surfaces 8:36); Spectroscopy.zip: Ti_continuous/ and Ti_pulsed/ 128 BWSpec4 txt (pixel, wavelength, dark, reference, raw, %TR, absorbance); AFM data.zip (1.6 GB .nid); XPS and resistivity xlsx",
    confidence=0.8,
)

R["18340583"] = dict(
    modality="NIR-MIR reflectance spectroscopy (Bruker Invenio-R FTIR in the CAPSULA thermal-vacuum chamber) of hexahydrite (MgSO4.6H2O) during pumping to high vacuum",
    spectral_range_original_min=399.21, spectral_range_original_max=14996.3, spectral_range_original_unit="cm-1",
    num_spectral_channels=7570, spectral_resolution=4, spectral_resolution_unit="cm-1",
    sampling_interval=1.93, sampling_interval_unit="cm-1",
    num_samples=1,  # hexahydrite powder, 50-75 um grain size
    num_spectra=16,  # pressure/time steps (room P -> 1e-3 mbar -> re-exposure) + 1 standard-deviation column
    num_spectral_values=121120,
    spectral_target_relationship="Reflectance (normalised at 5450 cm-1) of H2O/OH combination and overtone bands (1.45, 1.95 um), fundamental O-H and SO4 modes vs decreasing pressure at 300 K -> dehydration/amorphisation of hexahydrite under vacuum, relevant to hydrated salts on Europa/Ganymede (JUICE MAJIS); Raman (SENTERRA II) after exposure in the paper",
    source_file="18340583.pdf (De Angelis, Furnari, Ferrari, La Francesca, Carli, Piccioni, Rubino, Stefani & Tosi 2026 JGR Planets, doi:10.1029/2026JE009723); reflectance.txt (wavenumber + 16 condition columns + SD)",
    confidence=0.85,
)

R["18415008"] = dict(
    modality="Computed GW-BSE optical absorption spectra (BerkeleyGW, phonon-displaced Monte Carlo configurations at 0/300 K) of bismuth-ellagate MOF SU-101 (bare vs water-bound) + experimental UV-Vis diffuse reflectance, PL and FTIR",
    spectral_range_original_min=0, spectral_range_original_max=8, spectral_range_original_unit="eV",
    num_spectral_channels=801, sampling_interval=0.01, sampling_interval_unit="eV (computed; averaged spectra 0-7 eV; experimental DRS 200-800 nm, PL 400-600 nm, FTIR 399-3999 cm-1)",
    num_samples=2,  # activated (bare) and water-bound SU-101
    num_spectra=148,  # 129 BSE absorption + 8 averaged spectra + 11 experimental spectra
    num_spectral_values=108937,  # computed spectra only
    spectral_target_relationship="Exciton-phonon coupling: thermal phonon displacements renormalise the GW gap and broaden/red-shift the BSE eps2 absorption onset, more strongly for water-bound SU-101; averaged 300 K spectra compared with measured absorption/PL to explain hydration-dependent photocatalytic behaviour",
    source_file="18415008.pdf (Mourino, Alvertis, Smith, Domingues, Ebrahim, Champagne, Neaton & Smit 2026 Nat. Commun., doi:10.1038/s41467-026-76097-z); su101_data.tar: gwbse/ (absorption_eh*.dat eps2/eps1/JDOS, avgd_abs), phonons, bands, balign, relax, cifs, exp/ (DRS csv, PL csv/xlsx/opj, FTIR .dpt), post_processing; 3 phonon-mode GIFs",
    confidence=0.75,
)

R["18427774"] = dict(
    modality="Mid-infrared spectra (transmission KBr-pellet FTIR and ATR-FTIR; Bruker, PerkinElmer, Agilent/Varian, Shimadzu instruments) of peat samples compiled in the Peatland Mid-Infrared Database (pmird 1.1.0)",
    spectral_range_original_min=650, spectral_range_original_max=4000, spectral_range_original_unit="cm-1",
    sampling_interval=1, sampling_interval_unit="cm-1 (prepared csv; native .spc/.0 grids vary by source dataset)",
    num_samples=11216,  # peat samples from 26 datasets (MIR spectra for a subset)
    num_spectra=5537,  # MIR measurements in mir_metadata
    spectral_target_relationship="Peat MIR spectra (e.g. carbohydrate 1030, aromatic 1510/1610, aliphatic 2850/2920, carboxyl 1720 cm-1) linked to C, N, H, O, S, elemental, isotopic, humification, macrofossil and degradation properties -> spectral prediction models of peat chemistry; metadata quantify noise and water-vapour/CO2 artefacts",
    source_file="18427774.pdf (Teickner, Agethen, Berger, Boelsen, Borken, Bragazza, Broder, De La Cruz, Diaconu, ... Knorr, 'Peatland Mid-Infrared Database 1.0.0', EarthArXiv preprint submitted to Sci. Data); files_v1.1.0.zip: pmird_as_csv/ (50 tables incl. mir_metadata, samples, data), pmird_prepared_data/ (27 study folders: 4,411 spectra as csv/.spc/.0), MySQL dump, Rmd scripts, Dockerfile",
    confidence=0.8,
)
