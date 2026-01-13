from curl_cffi import requests as crequests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import time
import random
import concurrent.futures # IMPORTED FOR BATCHING

# --- Configuration ---
BATCH_SIZE = 5 # How many articles to download at the same time
OUTPUT_FILE = "Non_Elsevier_scraped_content.txt"
FAILED_LOG_FILE = "failed_Non_Elsevier_scraped_content_articles.txt"
EMAIL_FOR_UNPAYWALL = "howard.kuo@vernus.ai" 

# _TEST_SOURCE_DATA = [
#     ("35358937", "Ultrason Sonochem", "10.1016/j.ultsonch.2022.105986"),
#     ("39135289", "J Cosmet Dermatol", "10.1111/jocd.16528"),
#     ("40611782", "Mol Pharm", "10.1021/acs.molpharmaceut.4c01357"),
#     ("37207857", "Int J Pharm", "10.1016/j.ijpharm.2023.123055"),
#     ("37578286", "Mol Pharm", "10.1021/acs.molpharmaceut.3c00240")]
# # --- Your Data Source ---
SOURCE_DATA = [
    ("39135289", "J Cosmet Dermatol", "10.1111/jocd.16528"),
    ("40611782", "Mol Pharm", "10.1021/acs.molpharmaceut.4c01357"),
    ("37578286", "Mol Pharm", "10.1021/acs.molpharmaceut.3c00240"),
    ("33960250", "Drug Deliv", "10.1080/10717544.2021.1917729"),
    ("36843571", "Drug Deliv", "10.1080/10717544.2023.2183834"),
    ("36342775", "Cannabis Cannabinoid Res", "10.1089/can.2022.0176"),
    ("26090563", "Hum Vaccin Immunother", "10.1080/21645515.2015.1046660"),
    ("21725708", "AAPS PharmSciTech", "10.1208/s12249-011-9653-7"),
    ("20521179", "AAPS PharmSciTech", "10.1208/s12249-010-9457-1"),
    ("29468287", "Cardiovasc Intervent Radiol", "10.1007/s00270-018-1899-y"),
    ("30104454", "IET Nanobiotechnol", "10.1049/iet-nbt.2018.0006"),
    ("31935675", "IET Nanobiotechnol", "10.1049/iet-nbt.2019.0148"),
    ("35302741", "ACS Nano", "10.1021/acsnano.2c00199"),
    ("34601826", "Adv Healthc Mater", "10.1002/adhm.202101427"),
    ("19238556", "AAPS PharmSciTech", "10.1208/s12249-009-9192-7"),
    ("23403891", "Int J Nanomedicine", "10.2147/IJN.S35661"),
    ("23971048", "Biomed Res Int", "10.1155/2013/909045"),
    ("33328205", "Eur J Hosp Pharm", "10.1136/ejhpharm-2020-002534"),
    ("27099474", "Drug Des Devel Ther", "10.2147/DDDT.S103169"),
    ("19224372", "AAPS PharmSciTech", "10.1208/s12249-009-9190-9"),
    ("30591529", "J Pharmacol Exp Ther", "10.1124/jpet.118.254672"),
    ("25168449", "AAPS PharmSciTech", "10.1208/s12249-014-0199-3"),
    ("29520477", "Pharm Res", "10.1007/s11095-018-2349-x"),
    ("21887603", "AAPS PharmSciTech", "10.1208/s12249-011-9680-4"),
    ("23838466", "Hum Vaccin Immunother", "10.4161/hv.25639"),
    ("30296381", "Mol Pharm", "10.1021/acs.molpharmaceut.8b00802"),
    ("37272488", "Drug Deliv", "10.1080/10717544.2023.2219864"),
    ("24222270", "AAPS PharmSciTech", "10.1208/s12249-013-0048-9"),
    ("26788510", "Biomed Res Int", "10.1155/2015/818656"),
    ("26741303", "J Aerosol Med Pulm Drug Deliv", "10.1089/jamp.2015.1235"),
    ("29890855", "Drug Deliv", "10.1080/10717544.2018.1474970"),
    ("19184624", "AAPS PharmSciTech", "10.1208/s12249-009-9186-5"),
    ("18446484", "AAPS PharmSciTech", "10.1208/s12249-008-9036-x"),
    ("26391114", "J Drug Target", "10.3109/1061186X.2015.1087529"),
    ("24320221", "Mol Pharm", "10.1021/mp4005029"),
    ("25212898", "AAPS PharmSciTech", "10.1208/s12249-014-0214-8"),
    ("19340587", "AAPS PharmSciTech", "10.1208/s12249-009-9218-1"),
    ("39513340", "Drug Deliv", "10.1080/10717544.2024.2425158"),
    ("18431654", "AAPS PharmSciTech", "10.1208/s12249-008-9070-8"),
    ("34962186", "Drug Deliv", "10.1080/10717544.2021.2015483"),
    ("18446472", "AAPS PharmSciTech", "10.1208/s12249-007-9022-8"),
    ("20661674", "AAPS PharmSciTech", "10.1208/s12249-010-9478-9"),
    ("29500761", "AAPS PharmSciTech", "10.1208/s12249-018-0973-8"),
    ("21800216", "AAPS PharmSciTech", "10.1208/s12249-011-9663-5"),
    ("26083534", "ACS Nano", "10.1021/acsnano.5b01696"),
    ("18431660", "AAPS PharmSciTech", "10.1208/s12249-008-9063-7"),
    ("28283000", "Drug Deliv", "10.1080/10717544.2017.1284946"),
    ("23244299", "Mol Pharm", "10.1021/mp300319m"),
    ("23862723", "J Microencapsul", "10.3109/02652048.2013.814728"),
    ("28155336", "Drug Deliv", "10.1080/10717544.2016.1225854"),
    ("36299245", "Drug Deliv", "10.1080/10717544.2022.2136783"),
    ("32298275", "PLoS One", "10.1371/journal.pone.0230993"),
    ("19280350", "AAPS PharmSciTech", "10.1208/s12249-009-9193-6"),
    ("19629708", "AAPS PharmSciTech", "10.1208/s12249-009-9284-4"),
    ("38992340", "Drug Deliv", "10.1080/10717544.2024.2372279"),
    ("23118537", "Int J Nanomedicine", "10.2147/IJN.S36071"),
    ("30785266", "ACS Appl Mater Interfaces", "10.1021/acsami.9b00581"),
    ("21879393", "AAPS PharmSciTech", "10.1208/s12249-011-9675-1"),
    ("20652776", "AAPS PharmSciTech", "10.1208/s12249-010-9486-9"),
    ("18446479", "AAPS PharmSciTech", "10.1208/s12249-007-9016-6"),
    ("20405254", "AAPS PharmSciTech", "10.1208/s12249-010-9432-x"),
    ("32009480", "Drug Deliv", "10.1080/10717544.2020.1716881"),
    ("32031478", "Pharm Dev Technol", "10.1080/10837450.2020.1725893"),
    ("21246564", "J Pharm Sci", "10.1002/jps.22488"),
    ("24889733", "AAPS PharmSciTech", "10.1208/s12249-014-0147-2"),
    ("18622692", "Pharm Res", "10.1007/s11095-008-9594-3"),
    ("25114933", "Biomed Res Int", "10.1155/2014/984756"),
    ("20464537", "AAPS PharmSciTech", "10.1208/s12249-010-9440-x"),
    ("31840214", "Braz J Microbiol", "10.1007/s42770-019-00203-1"),
    ("12916940", "AAPS PharmSciTech", "10.1208/pt030325"),
    ("18181525", "AAPS PharmSciTech", "10.1208/pt0804104"),
    ("16594643", "AAPS J", "10.1208/aapsj070488"),
    ("21225383", "AAPS PharmSciTech", "10.1208/s12249-011-9583-4"),
    ("16408861", "AAPS PharmSciTech", "10.1208/pt060474"),
    ("21547911", "J Pharm Sci", "10.1002/jps.22475"),
    ("18446481", "AAPS PharmSciTech", "10.1208/s12249-008-9037-9"),
    ("20490959", "AAPS PharmSciTech", "10.1208/s12249-010-9445-5"),
    ("24058284", "ScientificWorldJournal", "10.1155/2013/153695"),
    ("18459055", "AAPS PharmSciTech", "10.1208/s12249-008-9082-4"),
    ("24297071", "Pharm Res", "10.1007/s11095-013-1252-8"),
    ("21793213", "Macromol Biosci", "10.1002/mabi.201100107"),
    ("20446072", "AAPS PharmSciTech", "10.1208/s12249-010-9438-4"),
    ("30343605", "Drug Deliv", "10.1080/10717544.2018.1516006"),
    ("18473177", "AAPS PharmSciTech", "10.1208/s12249-008-9080-6"),
    ("21842308", "AAPS PharmSciTech", "10.1208/s12249-011-9672-4"),
    ("22114474", "Int J Nanomedicine", "10.2147/IJN.S23985"),
    ("25367002", "AAPS PharmSciTech", "10.1208/s12249-014-0238-0"),
    ("25652729", "AAPS PharmSciTech", "10.1208/s12249-014-0280-y"),
    ("19148763", "AAPS PharmSciTech", "10.1208/s12249-008-9172-3"),
    ("18496755", "AAPS PharmSciTech", "10.1208/s12249-008-9089-x"),
    ("12916956", "AAPS PharmSciTech", "10.1208/pt030103"),
    ("16796363", "AAPS PharmSciTech", "10.1208/pt070246"),
    ("19936939", "AAPS PharmSciTech", "10.1208/s12249-009-9331-1"),
    ("18548338", "Pharm Res", "10.1007/s11095-008-9626-z"),
    ("29631468", "Drug Deliv", "10.1080/10717544.2018.1458923"),
    ("14727854", "AAPS PharmSciTech", "10.1208/pt010105"),
    ("20414757", "AAPS PharmSciTech", "10.1208/s12249-010-9426-8"),
    ("19479386", "AAPS PharmSciTech", "10.1208/s12249-009-9257-7"),
    ("24019468", "Proc Natl Acad Sci U S A", "10.1073/pnas.1310214110"),
    ("19148761", "AAPS PharmSciTech", "10.1208/s12249-008-9178-x"),
    ("23166436", "Int J Nanomedicine", "10.2147/IJN.S37277"),
    ("14727897", "AAPS PharmSciTech", "10.1208/pt010432"),
    ("18446474", "AAPS PharmSciTech", "10.1208/s12249-007-9023-7"),
    ("28850287", "Nutr Clin Pract", "10.1177/0884533617722759"),
    ("20931307", "AAPS PharmSciTech", "10.1208/s12249-010-9528-3"),
    ("23919086", "Int J Nanomedicine", "10.2147/IJN.S43474"),
    ("20496017", "AAPS PharmSciTech", "10.1208/s12249-010-9455-3"),
    ("19710954", "Mol Vis", "No DOI"),
    ("23882140", "Int J Nanomedicine", "10.2147/IJN.S45186"),
    ("14621964", "AAPS PharmSciTech", "10.1208/pt040332"),
    ("23658485", "Int J Nanomedicine", "10.2147/IJN.S41775"),
    ("20845090", "AAPS PharmSciTech", "10.1208/s12249-010-9507-8"),
    ("16517688", "Appl Environ Microbiol", "10.1128/AEM.72.3.2280-2282.2006"),
    ("18431669", "AAPS PharmSciTech", "10.1208/s12249-008-9053-9"),
    ("29768224", "IET Nanobiotechnol", "10.1049/iet-nbt.2017.0189"),
    ("22923993", "Int J Nanomedicine", "10.2147/IJN.S33993"),
    ("21614634", "Pharm Res", "10.1007/s11095-011-0474-x"),
    ("26967650", "J Vis Exp", "10.3791/53489"),
    ("14727903", "AAPS PharmSciTech", "10.1208/pt010317"),
    ("19184450", "AAPS PharmSciTech", "10.1208/s12249-008-9183-0"),
    ("22919267", "Mol Vis", "No DOI"),
    ("20856831", "Int J Nanomedicine", "10.2147/ijn.s12485"),
    ("18181537", "AAPS PharmSciTech", "10.1208/pt0804116"),
    ("25716330", "AAPS PharmSciTech", "10.1208/s12249-015-0308-y"),
    ("23600657", "Drug Dev Ind Pharm", "10.3109/03639045.2012.763137"),
    ("41373162", "J Food Sci", "10.1111/1750-3841.70761"),
    ("23641156", "Int J Nanomedicine", "10.2147/IJN.S43299"),
    ("40709743", "J Cosmet Dermatol", "10.1111/jocd.70302"),
    ("21968952", "Cancer Chemother Pharmacol", "10.1007/s00280-011-1749-y"),
    ("25580455", "ScientificWorldJournal", "10.1155/2014/274823"),
    ("16796361", "AAPS PharmSciTech", "10.1208/pt070244"),
    ("22275831", "Int J Nanomedicine", "10.2147/IJN.S27639"),
    ("31735104", "Drug Deliv", "10.1080/10717544.2019.1682720"),
    ("21753875", "Int J Nanomedicine", "10.2147/IJN.S20903"),
    ("30361239", "J Pharmacol Exp Ther", "10.1124/jpet.118.252809"),
    ("17622106", "AAPS PharmSciTech", "10.1208/pt0802028"),
    ("22072866", "Int J Nanomedicine", "10.2147/IJN.S18039"),
    ("25861680", "ScientificWorldJournal", "10.1155/2015/541510"),
    ("17025257", "AAPS PharmSciTech", "10.1208/pt070377"),
    ("35047632", "Biomed Res Int", "10.1155/2022/3549061"),
    ("28530194", "IET Nanobiotechnol", "10.1049/iet-nbt.2016.0116"),
    ("24363199", "AAPS J", "10.1208/s12248-013-9557-4"),
    ("19609836", "AAPS PharmSciTech", "10.1208/s12249-009-9286-2"),
    ("15760111", "AAPS J", "10.1208/aapsj060326"),
    ("23723698", "Int J Nanomedicine", "10.2147/IJN.S43892"),
    ("41092225", "Chem Biodivers", "10.1002/cbdv.202502124"),
    ("30534567", "Biomed Res Int", "10.1155/2018/9035452"),
    ("19504745", "AAPS PharmSciTech", "10.1208/s12249-009-9242-1"),
    ("23690685", "Int J Nanomedicine", "10.2147/IJN.S42002"),
    ("24961388", "J Pharm Sci", "10.1002/jps.24053"),
    ("18170981", "AAPS J", "10.1208/aapsj0903041"),
    ("38941109", "Ther Deliv", "10.1080/20415990.2024.2363635"),
    ("34565260", "Drug Deliv", "10.1080/10717544.2021.1979131"),
    ("28691021", "Biomed Res Int", "10.1155/2017/2723418"),
    ("36846914", "Drug Deliv", "10.1080/10717544.2023.2184311"),
    ("14727880", "AAPS PharmSciTech", "10.1208/pt020205"),
    ("40702891", "J Agric Food Chem", "10.1021/acs.jafc.5c04690"),
    ("22965661", "AAPS PharmSciTech", "10.1208/s12249-012-9847-7"),
    ("22114484", "Int J Nanomedicine", "10.2147/IJN.S22335"),
    ("35174738", "Drug Deliv", "10.1080/10717544.2022.2039805"),
    ("34964414", "Drug Deliv", "10.1080/10717544.2021.2021323"),
    ("31714057", "ACS Nano", "10.1021/acsnano.9b07214"),
    ("36786136", "Curr Drug Deliv", "10.2174/1567201820666230214091509"),
    ("23984361", "Biomed Res Int", "10.1155/2013/410686"),
    ("30095427", "IET Nanobiotechnol", "10.1049/iet-nbt.2017.0104"),
    ("19936938", "AAPS PharmSciTech", "10.1208/s12249-009-9340-0"),
    ("23326192", "Int J Nanomedicine", "10.2147/IJN.S37338"),
    ("24646020", "Nanomedicine (Lond)", "10.2217/nnm.14.4"),
    ("34590195", "AAPS PharmSciTech", "10.1208/s12249-021-02108-5"),
    ("19360857", "J Pharm Sci", "10.1002/jps.21719"),
    ("22760454", "AAPS PharmSciTech", "10.1208/s12249-012-9821-4"),
    ("33517791", "Drug Deliv", "10.1080/10717544.2021.1879314"),
    ("19641997", "AAPS PharmSciTech", "10.1208/s12249-009-9287-1"),
    ("25700978", "AAPS PharmSciTech", "10.1208/s12249-015-0305-1"),
    ("22187363", "AAPS PharmSciTech", "10.1208/s12249-011-9742-7"),
    ("34060397", "Drug Deliv", "10.1080/10717544.2021.1931561"),
    ("18720016", "AAPS PharmSciTech", "10.1208/s12249-008-9131-z"),
    ("29983563", "Int J Nanomedicine", "10.2147/IJN.S159839"),
    ("20509056", "AAPS PharmSciTech", "10.1208/s12249-010-9453-5"),
    ("21720510", "Int J Nanomedicine", "10.2147/IJN.S18821"),
    ("20824513", "AAPS PharmSciTech", "10.1208/s12249-010-9510-0"),
    ("23334925", "J Pharm Sci", "10.1002/jps.23450"),
    ("39838580", "J Cosmet Dermatol", "10.1111/jocd.16786"),
    ("25050379", "Biomed Res Int", "10.1155/2014/932017"),
    ("39879378", "Mol Pharm", "10.1021/acs.molpharmaceut.4c01374"),
    ("30706304", "Drug Deliv Transl Res", "10.1007/s13346-019-00619-0"),
    ("36803136", "Drug Deliv", "10.1080/10717544.2023.2179128"),
    ("19381824", "AAPS PharmSciTech", "10.1208/s12249-009-9234-1"),
    ("30724654", "Pharm Dev Technol", "10.1080/10837450.2019.1578372"),
    ("33355019", "Drug Deliv", "10.1080/10717544.2020.1862365"),
    ("21556344", "Int J Nanomedicine", "10.2147/IJN.S17524"),
    ("36588399", "Drug Deliv", "10.1080/10717544.2022.2164094"),
    ("24792826", "Pharm Res", "10.1007/s11095-014-1370-y"),
    ("39563603", "J Cosmet Dermatol", "10.1111/jocd.16685"),
    ("22888246", "Int J Nanomedicine", "10.2147/IJN.S33398"),
    ("22403491", "Int J Nanomedicine", "10.2147/IJN.S28761"),
    ("30363745", "Biomed Res Int", "10.1155/2018/6763057"),
    ("25511810", "AAPS PharmSciTech", "10.1208/s12249-014-0258-9"),
    ("30302631", "Pharm Res", "10.1007/s11095-018-2495-1"),
    ("33558284", "Antimicrob Agents Chemother", "10.1128/AAC.02106-20"),
    ("39400156", "Microbiol Spectr", "10.1128/spectrum.01378-24"),
    ("22072884", "Int J Nanomedicine", "10.2147/IJN.S22337"),
    ("31833006", "Braz J Microbiol", "10.1007/s42770-019-00201-3"),
    ("23439784", "Int J Nanomedicine", "10.2147/IJN.S29392"),
    ("30822166", "Drug Deliv", "10.1080/10717544.2019.1568622"),
    ("25591953", "AAPS PharmSciTech", "10.1208/s12249-014-0278-5"),
    ("26330329", "Cancer Chemother Pharmacol", "10.1007/s00280-015-2851-3"),
    ("36708105", "Drug Deliv", "10.1080/10717544.2023.2173337"),
    ("19876741", "AAPS PharmSciTech", "10.1208/s12249-009-9328-9"),
    ("23054984", "AAPS PharmSciTech", "10.1208/s12249-012-9855-7"),
    ("22267925", "Int J Nanomedicine", "10.2147/IJN.S25824"),
    ("36050870", "Drug Deliv", "10.1080/10717544.2022.2118399"),
    ("21735345", "AAPS PharmSciTech", "10.1208/s12249-011-9659-1"),
    ("21181511", "AAPS PharmSciTech", "10.1208/s12249-010-9568-8"),
    ("28831842", "Drug Deliv", "10.1080/10717544.2017.1365392"),
    ("19882250", "AAPS PharmSciTech", "10.1208/s12249-009-9315-1"),
    ("33840320", "Drug Deliv", "10.1080/10717544.2021.1909179"),
    ("30294884", "Adv Mater", "10.1002/adma.201804693"),
    ("39143900", "Nanomedicine (Lond)", "10.1080/17435889.2024.2386923"),
    ("38949622", "Ther Deliv", "10.1080/20415990.2024.2363136"),
    ("24554238", "AAPS PharmSciTech", "10.1208/s12249-014-0096-9"),
    ("30627887", "AAPS PharmSciTech", "10.1208/s12249-018-1287-6"),
    ("24668136", "AAPS PharmSciTech", "10.1208/s12249-014-0103-1"),
    ("38687316", "Indian J Pharmacol", "10.4103/ijp.ijp_370_23"),
    ("31111044", "Biomed Res Int", "10.1155/2019/2382563"),
    ("24410445", "Biomacromolecules", "10.1021/bm4015232"),
    ("21904451", "Int J Nanomedicine", "10.2147/IJN.S23597"),
    ("23797305", "AAPS PharmSciTech", "10.1208/s12249-013-9996-3"),
    ("19757079", "AAPS PharmSciTech", "10.1208/s12249-009-9306-2"),
    ("23935362", "Int J Nanomedicine", "10.2147/IJN.S48214"),
    ("33370213", "J Ocul Pharmacol Ther", "10.1089/jop.2020.0085"),
    ("31573544", "IET Nanobiotechnol", "10.1049/iet-nbt.2018.5248"),
    ("23180162", "AAPS J", "10.1208/s12248-012-9433-7"),
    ("19536653", "AAPS PharmSciTech", "10.1208/s12249-009-9268-4"),
    ("29600438", "Pharm Res", "10.1007/s11095-018-2391-8"),
    ("23775389", "AAPS PharmSciTech", "10.1208/s12249-013-9990-9"),
    ("19381825", "AAPS PharmSciTech", "10.1208/s12249-009-9233-2"),
    ("24901206", "Drug Deliv", "10.3109/10717544.2014.923068"),
    ("33787445", "Drug Deliv", "10.1080/10717544.2021.1902023"),
    ("4037770", "Antimicrob Agents Chemother", "10.1128/AAC.28.1.103"),
    ("22350738", "AAPS PharmSciTech", "10.1208/s12249-012-9762-y"),
    ("33501873", "Drug Deliv", "10.1080/10717544.2021.1872741"),
    ("36036168", "Drug Deliv", "10.1080/10717544.2022.2115165"),
    ("29581972", "Biomed Res Int", "10.1155/2018/4057959"),
    ("19333762", "AAPS PharmSciTech", "10.1208/s12249-009-9213-6"),
    ("25825339", "Br J Pharmacol", "10.1111/bph.13149"),
    ("40145792", "Adv Sci (Weinh)", "10.1002/advs.202414559"),
    ("19415505", "AAPS PharmSciTech", "10.1208/s12249-009-9235-0"),
    ("34145458", "J Burn Care Res", "10.1093/jbcr/irab118"),
    ("23049254", "Int J Nanomedicine", "10.2147/IJN.S34612"),
    ("23269869", "Int J Nanomedicine", "10.2147/IJN.S38927"),
    ("19778268", "J Aerosol Med Pulm Drug Deliv", "10.1089/jamp.2009.0766"),
    ("39454183", "Mol Pharm", "10.1021/acs.molpharmaceut.4c00686"),
    ("29181835", "Drug Deliv Transl Res", "10.1007/s13346-017-0435-y"),
    ("26993989", "JPEN J Parenter Enteral Nutr", "10.1177/0148607116640275"),
    ("29101176", "Am J Physiol Heart Circ Physiol", "10.1152/ajpheart.00471.2017"),
    ("31242332", "Biopharm Drug Dispos", "10.1002/bdd.2194"),
    ("22130789", "AAPS PharmSciTech", "10.1208/s12249-011-9721-z"),
    ("34694732", "IET Nanobiotechnol", "10.1049/nbt2.12010"),
    ("24504495", "AAPS PharmSciTech", "10.1208/s12249-014-0072-4"),
    ("15760075", "AAPS PharmSciTech", "10.1208/pt050342"),
    ("23137392", "Pharm Dev Technol", "10.3109/10837450.2012.737806"),
    ("24550699", "ScientificWorldJournal", "10.1155/2014/268107"),
    ("35764754", "Pharm Res", "10.1007/s11095-022-03317-8"),
    ("14727869", "AAPS PharmSciTech", "10.1208/pt020310"),
    ("17025252", "AAPS PharmSciTech", "10.1208/pt070372"),
    ("17408212", "AAPS PharmSciTech", "10.1208/pt0801012"),
    ("22150673", "J Pharm Pharmacol", "10.1111/j.2042-7158.2011.01376.x"),
    ("21748539", "AAPS PharmSciTech", "10.1208/s12249-011-9661-7"),
    ("31811762", "IET Nanobiotechnol", "10.1049/iet-nbt.2019.0035"),
    ("20632449", "World J Gastroenterol", "10.3748/wjg.v16.i27.3437"),
    ("20939702", "J Microencapsul", "10.3109/02652048.2010.520093"),
    ("36369759", "Drug Deliv", "10.1080/10717544.2022.2144545"),
    ("16584158", "AAPS PharmSciTech", "10.1208/pt070127"),
    ("35507250", "Appl Biochem Biotechnol", "10.1007/s12010-022-03812-z"),
    ("19381834", "AAPS PharmSciTech", "10.1208/s12249-009-9220-7"),
    ("22114486", "Int J Nanomedicine", "10.2147/IJN.S24547"),
    ("19337417", "Int J Nanomedicine", "10.2147/ijn.s3938"),
    ("25080136", "J Vis Exp", "10.3791/51874"),
    ("23025592", "Mol Pharm", "10.1021/mp3004379"),
    ("38802678", "Drug Deliv Transl Res", "10.1007/s13346-024-01620-y"),
    ("8726020", "Antimicrob Agents Chemother", "10.1128/AAC.40.6.1467"),
    ("17025242", "AAPS PharmSciTech", "10.1208/pt070361"),
    ("18956141", "Pharm Res", "10.1007/s11095-008-9744-7"),
    ("35708451", "Drug Deliv", "10.1080/10717544.2022.2083725"),
    ("35039793", "Biomed Res Int", "10.1155/2022/1558860"),
    ("32378175", "Drug Deliv Transl Res", "10.1007/s13346-020-00758-9"),
    ("27960411", "ACS Appl Mater Interfaces", "10.1021/acsami.6b08153"),
    ("29119735", "J Zhejiang Univ Sci B", "10.1631/jzus.B1600389"),
    ("31534201", "Acta Pharmacol Sin", "10.1038/s41401-019-0288-7"),
    ("24224161", "Biomed Res Int", "10.1155/2013/387863"),
    ("21980233", "Int J Nanomedicine", "10.2147/IJN.S20165")
]


# --- Helper Functions (Stateless) ---

def get_pdf_link_unpaywall(doi):
    """Strategy A: Ask Unpaywall for a free legal link."""
    if not doi: return None
    api_url = f"https://api.unpaywall.org/v2/{doi}?email={EMAIL_FOR_UNPAYWALL}"
    try:
        r = crequests.get(api_url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get('is_oa') and data.get('best_oa_location'):
                pdf_url = data['best_oa_location'].get('url_for_pdf')
                if pdf_url: return pdf_url
    except Exception:
        pass
    return None

def get_pdf_link_meta_tag(doi):
    """Strategy B: Visit the page and scrape the <meta name="citation_pdf_url"> tag."""
    if not doi: return None
    url = f"https://doi.org/{doi}"
    try:
        response = crequests.get(url, impersonate="chrome120", allow_redirects=True, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Standard academic meta tag
            meta_tag = soup.find("meta", attrs={"name": "citation_pdf_url"})
            if meta_tag and meta_tag.get("content"):
                return meta_tag.get("content")
                
            # Fallback: simple PDF anchor check
            for a in soup.find_all("a", href=True):
                href = a['href'].lower()
                if href.endswith(".pdf") and "suppl" not in href:
                    if href.startswith("http"): return a['href']
                    return response.url.rstrip("/") + "/" + a['href'].lstrip("/")
    except Exception:
        pass
    return None

def download_and_extract(pdf_url):
    """Downloads PDF binary and extracts text."""
    try:
        r = crequests.get(pdf_url, impersonate="chrome120", timeout=30)
        if r.status_code == 200 and r.content.startswith(b"%PDF"):
            with io.BytesIO(r.content) as f:
                reader = PdfReader(f)
                text = []
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted: text.append(extracted)
                return "\n".join(text)
    except Exception:
        pass
    return None

# --- New Worker Function for Concurrency ---

def process_single_article(data):
    """
    Worker function to process ONE article.
    Returns a tuple: (status, pmid, publisher, doi, content_or_error)
    """
    pmid, publisher, doi = data
    
    # 1. Validation
    if not doi or doi == "None":
        return ("SKIP", pmid, publisher, doi, "No DOI")
    
    # 2. Random Sleep (Politeness inside worker)
    # Even in parallel, this helps stagger the hits slightly
    time.sleep(random.uniform(1, 3)) 

    # 3. Try Unpaywall
    pdf_url = get_pdf_link_unpaywall(doi)
    
    # 4. Try Meta Tag
    if not pdf_url:
        pdf_url = get_pdf_link_meta_tag(doi)

    # 5. Download & Extract
    if pdf_url:
        content = download_and_extract(pdf_url)
        if content:
            return ("SUCCESS", pmid, publisher, doi, content)
    
    return ("FAIL", pmid, publisher, doi, "Could not access/extract PDF")

# --- Main Execution ---

if __name__ == "__main__":
    print(f"Starting Concurrent Scraping for {len(SOURCE_DATA)} articles...")
    print(f"Batch Size (Max Workers): {BATCH_SIZE}")

    success_count = 0
    failed_articles = [] 

    # We open the file once. The main thread will handle writing to avoid race conditions.
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f, \
         concurrent.futures.ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:

        # Submit all tasks
        # future_to_doi keeps track of which task is which
        future_to_article = {executor.submit(process_single_article, item): item for item in SOURCE_DATA}

        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_article):
            status, pmid, publisher, doi, result_payload = future.result()

            if status == "SUCCESS":
                # result_payload is the content string
                header = f"\n\n{'='*50}\nPMID: {pmid}\nDOI: {doi}\nPUBLISHER: {publisher}\n{'='*50}\n"
                f.write(header)
                f.write(result_payload)
                f.flush() # Ensure it's written to disk immediately
                print(f"    [SUCCESS] {doi}")
                success_count += 1
            
            elif status == "FAIL":
                print(f"    [FAILED] {doi}")
                failed_articles.append((pmid, publisher, doi))
            
            elif status == "SKIP":
                print(f"    [SKIPPED] PMID {pmid} (No DOI)")
                failed_articles.append((pmid, publisher, "No DOI"))

    # --- Final Reporting ---
    with open(FAILED_LOG_FILE, "w", encoding="utf-8") as log:
        log.write("PMID, Publisher, DOI\n")
        for item in failed_articles:
            log.write(f"{item[0]}, {item[1]}, {item[2]}\n")

    print("\n" + "="*30)
    print(f"SCRAPING COMPLETE")
    print(f"Total Processed: {len(SOURCE_DATA)}")
    print(f"Successful:      {success_count}")
    print(f"Failed:          {len(failed_articles)}")
    print(f"Content File:    {OUTPUT_FILE}")
    print(f"Failure Log:     {FAILED_LOG_FILE}")
    print("="*30)



#     ==============================
# SCRAPING COMPLETE
# Total Processed: 423
# Successful:      154
# Failed:          269
# Content File:    Non_Elsevier_scraped_content.txt
# Failure Log:     failed_Non_Elsevier_scraped_content_articles.txt

#     ==============================
