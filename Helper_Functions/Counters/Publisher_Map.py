#Publisher_Map.py
#this specific use case-> 56_withpmcidstillmissing_196_upayrwall_failed_dois

import csv
from io import StringIO
from collections import Counter

# 1. The Raw Data
raw_data = """"10.1002/jps.22475", "Redirecting",
"10.1111/j.2042-7158.2011.01376.x", "Title Not Found",
"10.1021/acsnano.5b01696", "Title Not Found",
"10.3109/02652048.2010.520093", "Full article: Development and characterization of nanoparticulate formulation of a water soluble prodrug of dexamethasone by HIP complexation",
"10.1080/10837450.2020.1725893", "Full article: Improving solubility and oral bioavailability of a novel antimalarial prodrug: comparing spray-dried dispersions with self-emulsifying drug delivery systems",
"10.1021/acsami.6b08153", "Gemcitabine and Antisense-microRNA Co-encapsulated PLGA–PEG Polymer Nanoparticles for Hepatocellular Carcinoma Therapy | ACS Applied Materials & Interfaces",
"10.1089/jamp.2009.0766", "Characterization of Stability and Nasal Delivery Systems for Immunization with Nanoemulsion-Based Vaccines | Journal of Aerosol Medicine and Pulmonary Drug Delivery",
"10.2217/nnm.14.4", "Formulation Design Facilitates Magnetic Nanoparticle Delivery to Diseased Cells and Tissues: Nanomedicine: Vol 9 , No 3  - Get Access",
"10.1049/iet-nbt.2018.5248", "Fabrication of poly(D, L-lactic acid) nanoparticles as delivery system for sustained release of L-theanine",
"10.1177/0884533617722759", "Home Parenteral Nutrition and Intravenous Fluid Errors Discovered Through Novel Clinical Practice of Reconciling Compounding Records: A Case Series",
"10.1002/jps.24053", "Redirecting",
"10.1128/AEM.72.3.2280-2282.2006", "Synbiotic Microcapsules That Enhance Microbial Viability during Nonrefrigerated Storage and Gastrointestinal Transit | Applied and Environmental Microbiology",
"10.1080/17435889.2024.2386923", "Gallic acid loaded self-nano emulsifying hydrogel-based drug delivery system against onychomycosis: Nanomedicine: Vol 19 , No 25  - Get Access",
"10.1002/mabi.201100107", "Poly(methyl malate) Nanoparticles: Formation, Degradation, and Encapsulation of Anticancer Drugs",
"10.1021/mp300319m", "Nanoassembly of Surfactants with Interfacial Drug-Interactive Motifs as Tailor-Designed Drug Carriers",
"10.3109/10837450.2012.737806", "Design and evaluation of a novel nanoparticulate-based formulation encapsulating a HIP complex of lysozyme",
"10.1128/aac.28.1.103", "Comparison of topically applied 5-ethyl-2'-deoxyuridine and acyclovir in the treatment of cutaneous herpes simplex virus infection in guinea pigs",
"10.1049/iet-nbt.2018.0006", "Efavirenz oral delivery via lipid nanocapsules: formulation, optimisation, and ex‐vivo gut permeation study",
"10.1002/jps.23450", "Development and Evaluation of a Novel Microemulsion Formulation of Elacridar to Improve its Bioavailability",
"10.1093/jbcr/irab118", "Dermal Nanoemulsion Treatment Reduces Burn Wound Conversion and Improves Skin Healing in a Porcine Model of Thermal Burn Injury",
"10.3748/wjg.v16.i27.3437", "Transcatheter arterial chemoembolization with a fine-powder formulation of cisplatin for hepatocellular carcinoma",
"10.1089/can.2022.0176", "Application of Oil-in-Water Cannabidiol Emulsion for the Treatment of Rheumatoid Arthritis",
"10.1002/adhm.202101427", "Initial Formation of the Skin Layer of PLGA Microparticles",
"10.1021/bm4015232", "Gelation Chemistries for the Encapsulation of Nanoparticles in Composite Gel Microparticles for Lung Imaging and Drug Delivery",
"10.1002/jps.21719", "Silicone Oil- and Agitation-Induced Aggregation of a Monoclonal Antibody in Aqueous Solution",
"10.1089/jamp.2015.1235", "Effects of Emulsion Composition on Pulmonary Tobramycin Delivery During Antibacterial Perfluorocarbon Ventilation",
"10.1021/mp4005029", "Formulation and Characterization of Nanoemulsion Intranasal Adjuvants: Effects of Surfactant Composition on Mucoadhesion and Immunogenicity",
"10.1049/iet-nbt.2017.0104", "Formulation of garlic oil‐in‐water nanoemulsion: antimicrobial and physicochemical aspects",
"10.1002/jps.22488", "Histamine Release Associated with Intravenous Delivery of a Fluorocarbon-Based Sevoflurane Emulsion in Canines",
"10.1136/ejhpharm-2020-002534", "Formulation, long-term physicochemical and microbiological stability of 15% topical resorcinol for hidradenitis suppurativa",
"10.3109/03639045.2012.763137", "Development and<i>in vitro</i>evaluation of a nanoemulsion for transcutaneous delivery",
"10.1002/adma.201804693", "Biomimetic Nanoemulsions for Oxygen Delivery In Vivo",
"10.3109/10717544.2014.923068", "Formulation development of a novel targeted theranostic nanoemulsion of docetaxel to overcome multidrug resistance in ovarian cancer",
"10.1021/acs.molpharmaceut.8b00802", "In Vivo and Cellular Trafficking of Acetalated Dextran Microparticles for Delivery of a Host-Directed Therapy for <i>Salmonella enterica</i> Serovar Typhi Infection",
"10.1124/jpet.118.254672", "CNS Delivery and Anti-Inflammatory Effects of Intranasally Administered Cyclosporine-A in Cationic Nanoformulations",
"10.1159/000522380", "Comparative Bioavailability Study of Solid Self-Nanoemulsifying Drug Delivery System of Fenofibric Acid in Healthy Male Subjects",
"10.1124/jpet.118.252809", "Single Dose of a Polyanhydride Particle-Based Vaccine Generates Potent Antigen-Specific Antitumor Immune Responses",
"10.2147/DDDT.S103169", "A novel tetrandrine-loaded chitosan microsphere: characterization and in vivo evaluation",
"10.1177/0148607116640275", "A Comparison of Fish Oil Sources for Parenteral Lipid Emulsions in a Murine Model",
"10.4103/ijp.ijp_370_23", "Wound-healing effect of topical nanoemulsion-loaded cream and gel formulations of Hippophae rhamnoides L. (sea buckthorn) fruit oil and their acute dermal toxicity study on female SD rats",
"10.1080/10837450.2019.1578372", "Multiple linear regression applied to predicting droplet size of complex perfluorocarbon nanoemulsions for biomedical applications",
"10.1159/000511443", "Investigation of ex vivo Skin Penetration of Coenzyme Q10 from Microemulsions and Hydrophilic Cream",
"10.1208/s12249-015-0308-y", "Exploring Microstructural Changes in Structural Analogues of Ibuprofen-Hosted In Situ Gelling System and Its Influence on Pharmaceutical Performance",
"10.1080/20415990.2024.2363136", "Quality-by-design-based microemulsion of disulfiram for repurposing in melanoma and breast cancer therapy",
"10.3109/1061186X.2015.1087529", "Localized delivery of a lipophilic proteasome inhibitor into human skin for treatment of psoriasis",
"10.1208/s12249-018-1287-6", "Development of Theranostic Perfluorocarbon Nanoemulsions as a Model Non-Opioid Pain Nanomedicine Using a Quality by Design (QbD) Approach",
"10.1049/iet-nbt.2016.0116", "Solvent effect in the synthesis of hydrophobic drug‐loaded polymer nanoparticles",
"10.1021/acsnano.9b07214", "Once Daily Pregabalin Eye Drops for Management of Glaucoma",
"10.3109/02652048.2013.814728", "Microparticles prepared from sulfenamide-based polymers",
"10.1021/mp3004379", "Aerosolized Antimicrobial Agents Based on Degradable Dextran Nanoparticles Loaded with Silver Carbene Complexes",
"10.1049/iet-nbt.2017.0189", "Encapsulation of the reductase component of                     <i>p</i>                     ‐hydroxyphenylacetate hydroxylase in poly(lactide‐                     <i>co</i>                     ‐glycolide) nanoparticles by three different emulsification techniques",
"10.1049/iet-nbt.2019.0148", "Co‐encapsulating CoFe                     <sub>2</sub>                     O                     <sub>4</sub>                     and MTX for hyperthermia",
"10.1021/acsnano.2c00199", "Direct Observation of Emulsion Morphology, Dynamics, and Demulsification",
"10.3791/53489", "Facile Preparation of Internally Self-assembled Lipid Particles Stabilized by Carbon Nanotubes",
"10.3791/51874", "Quantitative and Qualitative Examination of Particle-particle Interactions Using Colloidal Probe Nanoscopy",
"10.1080/20415990.2024.2363635", "Development of fexofenadine self-microemulsifying delivery systems: an efficient way to improve intestinal permeability """

publisher_map = {
    '10.1021': 'American Chemical Society (ACS)',
    '10.1080': 'Taylor & Francis',
    '10.2147': 'Dove Medical Press (Taylor & Francis)',
    '10.3109': 'Taylor & Francis (formerly Informa)',
    '10.1007': 'Springer Nature',
    '10.1208': 'Springer (AAPS)',
    '10.1631': 'Springer (Zhejiang Univ)',
    '10.1038': 'Springer Nature',
    '10.1155': 'Hindawi (Wiley)',
    '10.1002': 'Wiley',
    '10.1111': 'Wiley',
    '10.1049': 'IET (Wiley)',
    '10.1089': 'Mary Ann Liebert',
    '10.1136': 'BMJ',
    '10.1124': 'ASPET',
    '10.1371': 'PLOS',
    '10.1128': 'American Society for Microbiology (ASM)',
    '10.3791': 'JoVE',
    '10.3748': 'Baishideng Publishing Group',
    '10.1177': 'SAGE Publications',
    '10.2174': 'Bentham Science',
    '10.2217': 'Future Medicine',
    '10.4103': 'Medknow (Wolters Kluwer)',
    '10.1093': 'Oxford University Press (OUP)'
}
# def get_publisher_from_doi(doi_string):
#     doi_string = doi_string.strip()
    
#     if "No DOI" in doi_string or not doi_string:
#         return "Unknown / No DOI"
    
#     # Extract prefix (e.g., 10.1021 from 10.1021/acs.molpharm)
#     try:
#         prefix = doi_string.split('/')[0]
#         return publisher_map.get(prefix, f"Other (Prefix: {prefix})")
#     except IndexError:
#         return "Invalid DOI Format"

# # 3. Processing the Data
# reader = csv.reader(StringIO(raw_data))
# publisher_counts = Counter()
# total_papers = 0

# for row in reader:
#     if len(row) >= 3:
#         total_papers += 1
#         doi = row[2]
#         publisher = get_publisher_from_doi(doi)
#         publisher_counts[publisher] += 1

# # 4. Printing Results
# print(f"Total Papers Counted: {total_papers}\n")
# print(f"{'Publisher':<45} | {'Count'}")
# print("-" * 55)

# # Sort by count (descending)
# for pub, count in publisher_counts.most_common():
#     print(f"{pub:<45} | {count}")
def get_publisher_from_doi(doi_string):
    doi_string = doi_string.strip()
    
    if "No DOI" in doi_string or not doi_string:
        return "Unknown / No DOI"
    
    # Extract prefix (e.g., 10.1021 from 10.1021/acs.molpharm)
    try:
        prefix = doi_string.split('/')[0]
        return publisher_map.get(prefix, f"Other (Prefix: {prefix})")
    except IndexError:
        return "Invalid DOI Format"

# 3. Processing the Data
# quotechar='"' handles the quotes around your data automatically
reader = csv.reader(StringIO(raw_data.strip()), quotechar='"', skipinitialspace=True)

publisher_counts = Counter()
total_papers = 0

for row in reader:
    # Ensure row is not empty
    if len(row) >= 1:
        total_papers += 1
        
        # CHANGED: DOI is now at index 0 in "DOI", "Title" format
        doi = row[0] 
        
        publisher = get_publisher_from_doi(doi)
        publisher_counts[publisher] += 1

# 4. Printing Results
print(f"Total Papers Counted: {total_papers}\n")
print(f"{'Publisher':<45} | {'Count'}")
print("-" * 55)

# Sort by count (descending)
for pub, count in publisher_counts.most_common():
    print(f"{pub:<45} | {count}")
# Total Papers Counted: 176

# Publisher                                     | Count
# -------------------------------------------------------
# Dove Medical Press (Taylor & Francis)         | 33
# Springer (AAPS)                               | 30
# Springer Nature                               | 18
# Hindawi (Wiley)                               | 17
# Taylor & Francis                              | 16
# American Chemical Society (ACS)               | 15
# Wiley                                         | 11
# IET (Wiley)                                   | 6
# Taylor & Francis (formerly Informa)           | 6
# Mary Ann Liebert                              | 4
# American Society for Microbiology (ASM)       | 4
# American Society for Microbiology (ASM)       | 4
# ASPET                                         | 2
# SAGE Publications                             | 2
# Unknown / No DOI                              | 2
# JoVE                                          | 2
# BMJ                                           | 1
# PLOS                                          | 1
# Bentham Science                               | 1
# Future Medicine                               | 1
# Medknow (Wolters Kluwer)                      | 1
# Oxford University Press (OUP)                 | 1
# Baishideng Publishing Group                   | 1
# Springer (Zhejiang Univ)                      | 1