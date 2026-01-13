# 7. Multi-Source Academic Data Acquisition System AcademicScraperPipeline(Availableuponrequest)

# Summary: Engineered a high-efficiency extraction pipeline to bypass anti-bot measures (Cloudflare/Akamai) using curl_cffi for TLS fingerprint impersonation. Orchestrated a hybrid retrieval strategy utilizing the Unpaywall API to resolve legal Open Access endpoints and BeautifulSoup for fallback metadata parsing. Optimized data throughput by implementing io.BytesIO for in-memory PDF streaming, eliminating disk I/O latency during text extraction with pypdf.

# curl_cffi, BeautifulSoup, Unpaywall API, In-Memory Processing (io.BytesIO), pypdf, ETL Pipelines

from curl_cffi import requests as crequests
from bs4 import BeautifulSoup
from pypdf import PdfReader
import io
import time
import random

# --- Your Data Source (Full List) ---
# Format: (PMID, Publisher, DOI)
# I have included your full list here.

SOURCE_DATA = [
    ("36509402", "Elsevier", "10.1016/j.actbio.2022.12.004"),
    ("27513481", "Other", "10.20960/nh.252"),
    ("29513965", "Unknown", None), # Will be skipped
    ("12746058", "Taylor & Francis", "10.1080/713840366"),
    ("21372412", "Other", "10.1248/cpb.59.321"),
    ("23470348", "Other", "10.2478/v10007-012-0022-1"),
    ("39550011", "Elsevier", "10.1016/j.ijpharm.2024.124947"),
    ("33129978", "Elsevier", "10.1016/j.aohep.2020.10.006"),
    ("29306033", "Elsevier", "10.1016/j.aquatox.2017.12.007"),
    ("37478742", "Elsevier", "10.1016/j.jcis.2023.07.055"),
    ("29624255", "Unknown", None),
    ("25371296", "Other", "10.3109/10717544.2014.974001"),
    ("33540029", "Elsevier", "10.1016/j.ijpharm.2021.120304"),
    ("26755411", "Other", "10.3109/10717544.2015.1128496"),
    ("27477648", "Other", "10.1248/cpb.c16-00035"),
    ("24467601", "Other", "10.3109/10717544.2013.878857"),
    ("38838633", "Elsevier", "10.1016/j.jcis.2024.05.087"),
    ("37717666", "Elsevier", "10.1016/j.ejps.2023.106585"),
    ("31619647", "Other", "10.3177/jnsv.65.S54"),
    ("37164692", "Other", "10.1248/bpb.b23-00066"),
    ("27785790", "Other", "10.1111/anae.13625"),
    ("18379061", "Other", "10.1248/bpb.31.673"),
    ("32135181", "Elsevier", "10.1016/j.jid.2020.01.032"),
    ("6202310", "Other", "10.1093/bja/56.6.617"),
    ("24758140", "Other", "10.3109/10717544.2014.904021"),
    ("38897552", "Elsevier", "10.1016/j.ejpb.2024.114372"),
    ("19555306", "Taylor & Francis", "10.1080/10717540802481380"),
    ("30612003", "Elsevier", "10.1016/j.biopha.2018.12.079"),
    ("39043472", "Other", "10.62958/j.cjap.2024.016"),
    ("29762040", "ACS", "10.1021/acs.molpharmaceut.8b00097"),
    ("35013036", "Other", "10.5650/jos.ess21265"),
    ("32894823", "Other", "10.17219/acem/124439"),
    ("40175119", "Other", "10.5650/jos.ess24118"),
    ("39147577", "Other", "10.62958/j.cjap.2024.021"),
    ("39863284", "Elsevier", "10.1016/j.jvir.2025.01.040"),
    ("36852769", "Taylor & Francis", "10.1080/03639045.2023.2183724"),
    ("32573485", "Other", "10.1515/znc-2019-0229"),
    ("25013958", "Other", "10.3109/10717544.2014.936987"),
    ("39151830", "Elsevier", "10.1016/j.jconrel.2024.08.021"),
    ("11824591", "Other", "10.1248/cpb.50.87"),
    ("27128623", "Taylor & Francis", "10.1080/10717544.2016.1183720"),
    ("27107899", "Elsevier", "10.1016/j.ijpharm.2016.04.027"),
    ("21824447", "Other", "10.18433/j38p4v"),
    ("27566966", "Elsevier", "10.1016/j.ultsonch.2016.08.026"),
    ("20930400", "Other", "10.1248/cpb.58.1332"),
    ("39024835", "Elsevier", "10.1016/j.biopha.2024.117109"),
    ("24032657", "Other", "10.3109/10717544.2013.835007"),
    ("30365396", "Other", "10.18433/jpps30097"),
    ("30888204", "Taylor & Francis", "10.1080/21691401.2019.1581791"),
    ("28943530", "Other", "10.1248/bpb.b17-00162"),
    ("24601827", "Other", "10.3109/10717544.2014.893381"),
    ("23846143", "Other", "10.2478/acph-2013-0019"),
    ("40588105", "Elsevier", "10.1016/j.ejps.2025.107186"),
    ("31366828", "Other", "10.1248/cpb.c18-00930"),
    ("39708842", "Elsevier", "10.1016/j.ejps.2024.106993"),
    ("18763160", "Taylor & Francis", "10.1080/10717540802006864"),
    ("26704935", "Elsevier", "10.1016/j.jconrel.2015.12.022"),
    ("11085363", "Other", "10.1248/bpb.23.1341"),
    ("21130164", "Elsevier", "10.1016/j.ejps.2010.11.014"),
    ("22008038", "Other", "10.3109/10717544.2011.604686"),
    ("21838542", "Other", "10.3109/10717544.2011.600784"),
    ("33341050", "Elsevier", "10.1016/j.biopha.2020.111109"),
    ("24111887", "Other", "10.3109/10717544.2013.838716"),
    ("27689622", "Taylor & Francis", "10.1080/10717544.2016.1223210"),
    ("38977205", "Elsevier", "10.1016/j.ejps.2024.106844"),
    ("39904478", "Elsevier", "10.1016/j.ijpharm.2025.125309"),
    ("24439913", "Elsevier", "10.1016/j.ultsonch.2013.12.017"),
    ("40973007", "Elsevier", "10.1016/j.ejps.2025.107279"),
    ("41038586", "Elsevier", "10.1016/j.ejps.2025.107306"),
    ("38914398", "Elsevier", "10.1016/j.ijbiomac.2024.133295"),
    ("18451523", "Other", "10.1248/bpb.31.939"),
    ("11400868", "Taylor & Francis", "10.1080/107175401750177061"),
    ("24901205", "Other", "10.3109/10717544.2014.920430"),
    ("29709912", "Other", "10.1248/bpb.b17-00964"),
    ("26743668", "Other", "10.5650/jos.ess15183"),
    ("29413597", "Elsevier", "10.1016/j.colsurfb.2018.01.023"),
    ("32650196", "Elsevier", "10.1016/j.jcis.2020.06.024"),
    ("29730982", "Other", "10.7399/fh.10954"),
    ("33487621", "Other", "10.5582/ddt.2020.03118"),
    ("28503949", "Taylor & Francis", "10.1080/21691401.2017.1324465"),
    ("27430384", "Other", "10.5650/jos.ess16018"),
    ("25013957", "Other", "10.3109/10717544.2014.933284"),
    ("40967823", "Other", "10.1248/cpb.c25-00382"),
    ("32249259", "Other", "10.5650/jos.ess19250"),
    ("33352447", "Elsevier", "10.1016/j.biopha.2020.111114"),
    ("31545268", "Elsevier", "10.1016/j.biopha.2019.109373"),
    ("18379059", "Other", "10.1248/bpb.31.662"),
    ("25437926", "Other", "10.1213/ANE.0000000000000558"),
    ("31522563", "Taylor & Francis", "10.1080/09546634.2019.1668907"),
    ("21945905", "Other", "10.2478/v10007-011-0022-6"),
    ("38954935", "Elsevier", "10.1016/j.colsurfb.2024.114051"),
    ("21048336", "Other", "10.1248/cpb.58.1455"),
    ("10319428", "Other", "10.1248/cpb.47.492"),
    ("39986492", "Elsevier", "10.1016/j.ijpharm.2025.125384"),
    ("33667681", "Elsevier", "10.1016/j.ejpb.2021.02.012"),
    ("20304048", "Elsevier", "10.1016/j.ejps.2010.03.008"),
    ("40905433", "Taylor & Francis", "10.1080/14737167.2025.2556693"),
    ("32908093", "Other", "10.5650/jos.ess20070"),
    ("24177312", "Elsevier", "10.1016/j.jconrel.2013.10.027"),
    ("38763662", "Elsevier", "10.1016/j.foodres.2024.114412"),
    ("19952537", "Other", "10.1248/yakushi.129.1559"),
    ("3618992", "Other", "10.1111/j.1365-2044.1987.tb03080.x"),
    ("19555307", "Taylor & Francis", "10.1080/10717540802481646"),
    ("24329559", "Other", "10.3109/10717544.2013.866992"),
    ("30713269", "Other", "10.1248/cpb.c18-00614"),
    ("36306910", "Elsevier", "10.1016/j.ijbiomac.2022.10.207"),
    ("40054206", "Elsevier", "10.1016/j.foodchem.2025.143650"),
    ("18446567", "Taylor & Francis", "10.1080/10717540802006377"),
    ("27187792", "Other", "10.3109/10717544.2015.1077290"),
    ("40210050", "Elsevier", "10.1016/j.ijbiomac.2025.142957"),
    ("15499171", "Other", "10.2133/dmpk.19.62"),
    ("21835676", "Elsevier", "10.1016/j.ultsonch.2011.07.001"),
    ("24892633", "Other", "10.3109/10717544.2014.916764"),
    ("21134863", "Other", "10.2478/v10007-010-0022-y"),
    ("2076565", "Other", "10.1248/cpb.38.2797"),
    ("32563983", "Elsevier", "10.1016/j.biopha.2020.110369"),
    ("41213486", "Elsevier", "10.1016/j.ijpharm.2025.126366"),
    ("18758114", "Other", "10.1248/cpb.56.1335"),
    ("31539730", "Elsevier", "10.1016/j.ultsonch.2019.05.021"),
    ("12843625", "Other", "10.1248/bpb.26.994"),
    ("8882240", "Other", "10.1111/j.1365-2044.1996.tb12607.x"),
    ("39147549", "Elsevier", "10.1016/j.foodres.2024.114743"),
    ("18515228", "Other", "10.2478/v10007-008-0001-8"),
    ("28508377", "Springer", "10.1007/s13346-017-0390-7"),
    ("12176247", "Elsevier", "10.1016/s0378-5173(02)00158-8"),
    ("16547393", "Other", "10.2133/dmpk.21.45"),
    ("24390494", "Other", "10.1248/cpb.c13-00599"),
    ("16508155", "Other", "10.1248/bpb.29.508"),
    ("27133178", "Taylor & Francis", "10.1080/21691401.2016.1175444"),
    ("19952534", "Other", "10.1248/yakushi.129.1537"),
    ("27887040", "Taylor & Francis", "10.1080/21691401.2016.1260579"),
    ("29137746", "Elsevier", "10.1016/j.ultsonch.2017.09.042"),
    ("24524408", "Other", "10.3109/10717544.2014.883117"),
    ("31685768", "Other", "10.1248/bpb.b19-00368"),
    ("30012897", "Other", "10.5650/jos.ess17253"),
    ("33910724", "Elsevier", "10.1016/j.carbpol.2021.118060"),
    ("26806649", "Elsevier", "10.1016/j.ijbiomac.2016.01.064"),
    ("10746166", "Other", "10.1248/bpb.22.1331"),
    ("27777121", "Elsevier", "10.1016/j.exer.2016.10.016"),
    ("21415545", "Other", "10.1248/bpb.34.300"),
    ("28428486", "Other", "10.1248/bpb.b17-00026"),
    ("38908413", "Elsevier", "10.1016/j.ejps.2024.106835"),
    ("22374516", "Elsevier", "10.1016/j.ijpharm.2012.02.028"),
    ("27725389", "Other", "10.1248/yakushi.15-00237"),
    ("27019055", "Other", "10.3109/21691401.2016.1161639"),
    ("26708427", "Elsevier", "10.1016/j.ijbiomac.2015.12.029"),
    ("16556571", "Taylor & Francis", "10.1080/10717540500455983"),
    ("23449203", "Other", "10.1248/cpb.c12-00983"),
    ("23153669", "Elsevier", "10.1016/j.ejpb.2012.10.016"),
    ("33512160", "ACS", "10.1021/acs.jafc.0c06409"),
    ("41033375", "Elsevier", "10.1016/j.ijpharm.2025.126229"),
    ("16223691", "Elsevier", "10.1016/j.ultsonch.2004.10.004"),
    ("31292338", "Other", "10.5650/jos.ess18209"),
    ("34111547", "Elsevier", "10.1016/j.ijpharm.2021.120783"),
    ("22954686", "Elsevier", "10.1016/j.ultsonch.2012.08.010"),
    ("25743195", "Other", "10.1248/cpb.c14-00696"),
    ("33039443", "Elsevier", "10.1016/j.neuint.2020.104875"),
    ("39074648", "Elsevier", "10.1016/j.ijpharm.2024.124536"),
    ("40541033", "Elsevier", "10.1016/j.colsurfb.2025.114879"),
    ("8792425", "Other", "10.1023/a:1016001111731"),
    ("17497355", "Taylor & Francis", "10.1080/10717540601067760"),
    ("25857682", "Other", "10.3109/13880209.2015.1021817"),
    ("33249282", "Elsevier", "10.1016/j.biopha.2020.110980"),
    ("24262758", "Elsevier", "10.1016/j.ultsonch.2013.10.021"),
    ("40373720", "Elsevier", "10.1016/j.foodchem.2025.144697"),
    ("27012878", "Other", "10.3109/21691401.2016.1161637"),
    ("40623608", "Elsevier", "10.1016/j.ijpharm.2025.125934"),
    ("28403666", "Taylor & Francis", "10.1080/21691401.2017.1313262"),
    ("39142152", "Elsevier", "10.1016/j.jcis.2024.07.233"),
    ("26459167", "Elsevier", "10.1016/j.ijbiomac.2015.10.025"),
    ("25058033", "Other", "10.3109/21691401.2014.937869"),
    ("26172934", "ACS", "10.1021/acsnano.5b02702"),
    ("40263879", "Elsevier", "10.1016/j.foodres.2025.116091"),
    ("23258559", "Other", "10.5301/JABFM.2012.10438"),
    ("7703979", "Other", "10.1248/bpb.17.1526"),
    ("31259710", "Other", "10.2478/acph-2018-0035"),
    ("17497356", "Taylor & Francis", "10.1080/10717540601067786"),
    ("12843667", "Other", "10.1271/bbb.67.1376"),
    ("7537555", "Other", "10.1271/bbb.59.492"),
    ("26011936", "Other", "10.1515/acph-2015-0012"),
    ("22129882", "Other", "10.1248/yakushi.131.1835"),
    ("26521854", "Other", "10.1248/cpb.c15-00516"),
    ("21684851", "Other", "10.2478/v10007-011-0013-7"),
    ("25985724", "Other", "10.3109/21691401.2015.1042109"),
    ("18712624", "Taylor & Francis", "10.1080/10717540802328599"),
    ("8477513", "Other", "10.1248/cpb.41.599"),
    ("32105903", "Elsevier", "10.1016/j.jcis.2020.02.066"),
    ("9364682", "Elsevier", "10.1016/s0264-410x(97)00109-6"),
    ("38775552", "Other", "10.1590/0001-3765202420220448"),
    ("22497819", "Elsevier", "10.1016/j.farma.2011.10.005"),
    ("14519968", "Other", "10.1271/bbb.67.1864"),
    ("1540464", "Other", "10.1093/bja/68.2.193"),
    ("17107927", "Taylor & Francis", "10.1080/10717540600559478"),
    ("15750277", "Other", "10.2169/internalmedicine.44.149"),
    ("20226857", "Elsevier", "10.1016/j.ejpb.2010.03.005"),
    ("18374553", "Elsevier", "10.1016/j.ejpb.2008.01.021"),
    ("38328971", "Other", "10.20960/nh.04931"),
    ("22928732", "Other", "10.3109/10717544.2012.704094"),
    ("25711493", "Other", "10.3109/21691401.2015.1012261"),
    ("21696294", "Other", "10.3109/10717544.2011.589088"),
    ("25475215", "Other", "10.1039/c4nr05593d"),
    ("6335003", "Other", "10.1111/j.1365-2044.1984.tb06425.x"),
    ("31639085", "Other", "10.2478/acph-2019-0054"),
    ("26133712", "Other", "10.1248/bpb.b15-00110"),
    ("21099145", "Other", "10.5650/jos.59.667"),
    ("31084795", "Elsevier", "10.1016/j.ultsonch.2019.03.018"),
    ("20045959", "Other", "10.1248/cpb.58.16"),
    ("19003738", "Other", "10.1024/0300-9831.78.3.156"),
    ("18379060", "Other", "10.1248/bpb.31.668"),
    ("26406153", "Other", "10.3109/10717544.2015.1088597"),
    ("16141605", "Other", "10.2133/dmpk.20.257"),
    ("24673611", "Other", "10.3109/10717544.2014.900154"),
    ("39919823", "Other", "10.1055/a-2517-4967"),
    ("27477645", "Other", "10.1248/cpb.c15-00782"),
    ("25564964", "Other", "10.3109/10717544.2014.996833"),
    ("20513974", "Other", "10.5650/jos.59.395"),
    ("16141604", "Other", "10.2133/dmpk.20.244"),
    ("27689408", "Taylor & Francis", "10.1080/10717544.2016.1223225"),
    ("25148542", "Other", "10.3109/10717544.2014.950768"),
    ("20942639", "Other", "10.3109/10717544.2010.522613"),
    ("20354345", "Other", "10.3177/jnsv.56.41"),
    ("24492583", "Other", "10.1248/cpb.c13-00051"),
    ("35662634", "Elsevier", "10.1016/j.ejps.2022.106229"),
    ("25331709", "Other", "10.3109/21691401.2014.966192"),
    ("17473473", "Other", "10.1248/cpb.55.800"),
    ("3874642", "Other", "10.1093/bja/57.8.736"),
    ("16858422", "Nature", "10.1038/sj.jid.5700485"),
    ("23124565", "Other", "10.1248/cpb.c12-00502"),
    ("34763088", "Elsevier", "10.1016/j.ejps.2021.106058"),
    ("38179768", "Other", "10.31083/j.fbl2812349"),
    ("32353451", "Elsevier", "10.1016/j.jid.2020.04.009"),
    ("24321014", "Other", "10.3109/10717544.2013.861659"),
    ("16204978", "Other", "10.1248/cpb.53.1246"),
    ("24401095", "Other", "10.3109/10717544.2013.861883"),
    ("21028951", "Other", "10.3109/10717544.2010.528068"),
    ("25293973", "Other", "10.3109/10717544.2014.966925"),
    ("20299769", "Other", "10.5650/jos.59.223"),
    ("38789398", "Wiley", "10.1002/1873-3468.14936"),
    ("18165187", "Other", "10.2478/v10007-007-0034-4"),
    ("40704749", "Taylor & Francis", "10.1080/10837450.2025.2537128"),
    ("24892623", "Other", "10.3109/10717544.2014.923067"),
    ("20045958", "Other", "10.1248/cpb.58.11"),
    ("38775525", "Other", "10.1590/1519-6984.281236"),
    ("19839411", "Other", "10.2478/v10007-007-0009-5"),
    ("18175953", "Other", "10.1248/bpb.31.118"),
    ("19647057", "Elsevier", "10.1016/j.ijpharm.2009.07.025"),
    ("24670090", "Other", "10.3109/10717544.2014.898109"),
    ("18379176", "Other", "10.1248/yakushi.128.595"),
    ("40767668", "Other", "10.1590/1519-6984.292718"),
    ("14600407", "Other", "10.1248/bpb.26.1591"),
    ("26882014", "Other", "10.3109/10717544.2016.1141260"),
    ("41183677", "Elsevier", "10.1016/j.xphs.2025.104053"),
    ("24641773", "Other", "10.3109/21691401.2014.887018"),
    ("24786482", "Other", "10.3109/10717544.2014.907842"),
    ("23846146", "Other", "10.2478/acph-2013-0013"),
    ("12095048", "Other", "10.1034/j.1600-6143.2002.020116.x"),
    ("25781700", "Other", "10.1515/acph-2015-0009"),
    ("35263632", "Elsevier", "10.1016/j.ejps.2022.106159"),
    ("30797146", "Elsevier", "10.1016/j.biopha.2019.108622"),
    ("24724963", "Other", "10.3109/10717544.2014.898713"),
    ("25465045", "Other", "10.3109/21691401.2014.984301"),
    ("26375019", "Other", "10.1590/0001-3765201520130436"),
    ("18773122", "Other", "10.1358/mf.2008.30.4.1185802"),
    ("38797251", "Elsevier", "10.1016/j.ijpharm.2024.124267"),
    ("27600884", "Taylor & Francis", "10.1080/21691401.2016.1226178"),
    ("24601856", "Other", "10.3109/10717544.2014.891270"),
    ("41213305", "Elsevier", "10.1016/j.ejps.2025.107372"),
    ("28029520", "Elsevier", "10.1016/j.ultsonch.2016.10.020"),
    ("27773233", "Elsevier", "10.1016/j.ultsonch.2016.05.037"),
    ("16556573", "Taylor & Francis", "10.1080/10717540500309172"),
    ("25781702", "Other", "10.1515/acph-2015-0003"),
    ("36669582", "Elsevier", "10.1016/j.ijpharm.2023.122622"),
    ("34216586", "Elsevier", "10.1016/j.chemphyslip.2021.105113"),
    ("16401589", "Taylor & Francis", "10.1080/10717540500313109"),
    ("24865289", "Other", "10.3109/10717544.2014.920432"),
    ("15736829", "Taylor & Francis", "10.1080/10717540490494096"),
    ("24350612", "Other", "10.3109/10717544.2013.868557"),
    ("29428792", "Elsevier", "10.1016/j.ejpb.2018.02.013"),
    ("26079529", "Other", "10.3109/10717544.2015.1054051"),
    ("41109647", "Elsevier", "10.1016/j.ijpharm.2025.126284"),
    ("31935474", "Elsevier", "10.1016/j.ijpharm.2019.119003"),
    ("24512268", "Other", "10.3109/10717544.2013.878003"),
    ("20816012", "Other", "10.18433/j3830g"),
    ("20046073", "Other", "10.1248/yakushi.130.103"),
    ("31675660", "Elsevier", "10.1016/j.ultsonch.2019.104832"),
    ("39303769", "Elsevier", "10.1016/j.ejps.2024.106912"),
    ("35853596", "Elsevier", "10.1016/j.ejps.2022.106263"),
    ("40318398", "Elsevier", "10.1016/j.colsurfb.2025.114733"),
    ("9853281", "Other", "10.1046/j.1523-1755.1998.00194.x"),
    ("29337676", "Other", "10.1515/acph-2017-0036"),
    ("26027464", "Other", "10.1248/cpb.c14-00326"),
    ("31677372", "Other", "10.2478/acph-2020-0012"),
    ("39213974", "Elsevier", "10.1016/j.foodchem.2024.141006"),
    ("34963181", "Other", "10.1055/a-1699-3284"),
    ("40499600", "Elsevier", "10.1016/j.ijpharm.2025.125823"),
    ("18175978", "Other", "10.1248/cpb.56.70"),
    ("24512464", "Other", "10.3109/10717544.2014.885616"),
    ("27889158", "Elsevier", "10.1016/j.fm.2016.10.031"),
    ("16019888", "Taylor & Francis", "10.1080/02652040400026350"),
    ("28732987", "Elsevier", "10.1016/j.ultsonch.2017.05.021"),
    ("21812751", "Other", "10.3109/10717544.2011.595842"),
    ("21652183", "Elsevier", "10.1016/j.colsurfb.2011.05.019"),
    ("20460789", "Other", "10.1248/cpb.58.639"),
    ("33647402", "Elsevier", "10.1016/j.ejps.2021.105778"),
    ("37979632", "Elsevier", "10.1016/j.ijpharm.2023.123614"),
    ("25519291", "Other", "10.5650/jos.ess14175"),
    ("27854145", "Other", "10.3109/10717544.2016.1153747"),
    ("17878111", "Other", "10.2478/v10007-007-0025-5"),
    ("27196716", "Other", "10.3109/21691401.2016.1161640"),
    ("14993814", "Other", "10.1248/bpb.27.418"),
    ("29130769", "Taylor & Francis", "10.1080/21691401.2017.1397002"),
    ("24625264", "Other", "10.3109/10717544.2014.893382"),
    ("19941406", "Other", "10.3109/10717540903431586"),
    ("16188728", "Taylor & Francis", "10.1080/10717540500176829"),
    ("18239299", "Other", "10.1248/cpb.56.156"),
    ("25177016", "Other", "10.1248/cpb.c14-00231"),
    ("40820521", "Other", "10.62958/j.cjap.2025.020"),
    ("11163825", "Elsevier", "10.1016/s0015-0282(00)01636-8"),
    ("30032652", "Taylor & Francis", "10.1080/21691401.2018.1489826"),
    ("16681722", "Other", "10.1111/j.1525-1438.2006.00557.x"),
    ("24266589", "Other", "10.3109/10717544.2013.859186"),
    ("29458210", "Elsevier", "10.1016/j.ijpharm.2018.02.020"),
    ("26585010", "Elsevier", "10.1016/j.ultsonch.2015.09.015"),
    ("19845760", "Other", "10.1111/j.1600-0625.2009.01001.x"),
    ("20863928", "Elsevier", "10.1016/S0034-7094(10)70059-3"),
    ("26935492", "Other", "10.17219/acem/22636"),
    ("21804203", "Other", "10.1248/bpb.34.1179"),
    ("25748382", "Other", "10.5650/jos.ess14177"),
    ("39134099", "Elsevier", "10.1016/j.ejpb.2024.114453"),
    ("39818363", "Elsevier", "10.1016/j.ejps.2025.107015"),
    ("39344380", "Other", "10.31083/j.fbe1603025"),
    ("40010735", "Other", "10.5582/ddt.2025.01000"),
    ("25301684", "Other", "10.3109/21691401.2014.962741"),
    ("25315488", "Elsevier", "10.1016/j.jconrel.2014.10.007"),
    ("40113103", "Elsevier", "10.1016/j.ejps.2025.107077"),
    ("24467620", "Other", "10.3109/10717544.2013.879398"),
    ("40562285", "Elsevier", "10.1016/j.ijpharm.2025.125886"),
    ("25766929", "Other", "10.5650/jos.ess14194"),
    ("23371771", "Springer", "10.1007/s10856-013-4874-9"),
    ("28867749", "Other", "10.5582/ddt.2017.01029"),
    ("24725029", "Other", "10.3109/10717544.2014.898347"),
    ("35623483", "Elsevier", "10.1016/j.ijpharm.2022.121853"),
    ("26923781", "Other", "10.3109/10717544.2016.1145306"),
    ("22387278", "Elsevier", "10.1016/j.ijpharm.2012.02.025"),
    ("40480519", "Elsevier", "10.1016/j.jconrel.2025.113932"),
    ("1997061", "Other", "10.1093/bja/66.1.66"),
    ("7772431", "Other", "10.1093/bja/74.5.553"),
    ("40360092", "Elsevier", "10.1016/j.ijpharm.2025.125711"),
    ("40185335", "Elsevier", "10.1016/j.jconrel.2025.113677"),
    ("27002986", "Other", "10.3109/21691401.2016.1160915"),
    ("34375652", "Elsevier", "10.1016/j.exppara.2021.108142"),
    ("17364873", "Taylor & Francis", "10.1080/10717540600740045"),
    ("28604104", "Taylor & Francis", "10.1080/21691401.2017.1337024"),
    ("11999123", "Other", "10.1211/0022357021778736"),
    ("20686252", "Other", "10.1248/cpb.58.1015"),
    ("30316975", "Elsevier", "10.1016/j.ejps.2018.10.007"),
    ("25579428", "Other", "10.18433/j3vp5h"),
    ("17994359", "Taylor & Francis", "10.1080/10717540701202960"),
    ("24845480", "Other", "10.3109/10717544.2014.914601"),
    ("26964971", "Elsevier", "10.1016/j.ultsonch.2016.01.035"),
    ("29863060", "Other", "10.1248/cpb.c17-00542"),
    ("16442757", "Elsevier", "10.1016/j.ijpharm.2005.10.050"),
    ("35833564", "Taylor & Francis", "10.1080/09546634.2022.2071823"),
    ("40716630", "Elsevier", "10.1016/j.ejphar.2025.177992"),
    ("18382923", "Taylor & Francis", "10.1080/02652040701814140"),
    ("33582449", "Elsevier", "10.1016/j.biopha.2021.111368"),
    ("18686080", "Taylor & Francis", "10.1080/10717540500398092"),
    ("23537465", "Other", "10.3109/10717544.2012.762434"),
    ("31893542", "Elsevier", "10.1016/j.ijpharm.2019.118997"),
    ("23700941", "Other", "10.2298/vsp1304374m"),
    ("38747835", "Other", "10.1590/0001-3765202420230373"),
    ("25544603", "Other", "10.3109/10717544.2014.948643"),
    ("19409465", "Elsevier", "10.1016/j.ijpharm.2009.04.024"),
    ("40057137", "Elsevier", "10.1016/j.ejps.2025.107061"),
    ("17701526", "Taylor & Francis", "10.1080/10717540701202937"),
    ("24601855", "Other", "10.3109/10717544.2014.891273"),
    ("25853479", "Other", "10.3109/10717544.2015.1028603"),
    ("21914965", "Other", "10.2133/dmpk.DMPK-11-RG-041"),
    ("27327352", "Taylor & Francis", "10.1080/21691401.2016.1196457"),
    ("26631576", "Other", "10.3109/21691401.2015.1111229"),
    ("36752024", "Taylor & Francis", "10.1080/02652048.2023.2175924"),
    ("27803472", "Other", "10.1248/cpb.c16-00562"),
    ("41197747", "Elsevier", "10.1016/j.ejps.2025.107364"),
    ("24670098", "Other", "10.3109/10717544.2014.898715"),
    ("38384041", "Other", "10.4103/jcrt.jcrt_278_22"),
    ("33627576", "Other", "10.5582/ddt.2021.01004"),
    ("37788730", "Elsevier", "10.1016/j.ijpharm.2023.123473"),
    ("29113501", "Taylor & Francis", "10.1080/21691401.2017.1396996"),
    ("24735249", "Other", "10.3109/10717544.2014.903011"),
    ("31663388", "Taylor & Francis", "10.1080/21691401.2019.1683567"),
    ("19555305", "Taylor & Francis", "10.1080/10717540802481349"),
    ("29806500", "Taylor & Francis", "10.1080/21691401.2018.1477789"),
    ("24344769", "Other", "10.3109/10717544.2013.867382"),
    ("41203220", "Elsevier", "10.1016/j.ijpharm.2025.126354"),
    ("28323508", "Taylor & Francis", "10.1080/21691401.2017.1301459"),
    ("29038068", "Elsevier", "10.1016/j.ijpharm.2017.09.072"),
    ("15198214", "Other", "10.2460/ajvr.2004.65.752"),
    ("30604270", "Other", "10.1208/s12249-018-1215-9"),
    ("28163220", "Elsevier", "10.1016/j.ijpharm.2017.02.006"),
    ("35183717", "Elsevier", "10.1016/j.ejpb.2022.02.010"),
    ("12396737", "Taylor & Francis", "10.1080/15227950290097633"),
    ("18720135", "Taylor & Francis", "10.1080/10717540802039089"),
    ("16423801", "Taylor & Francis", "10.1080/10717540500313430"),
    ("24990503", "Other", "10.1248/cpb.c14-00110"),
    ("18027181", "Taylor & Francis", "10.1080/10717540701606467"),
    ("20482471", "Other", "10.3109/10717544.2010.483256"),
    ("22866544", "Other", "10.3923/pjbs.2012.141.146"),
    ("11474795", "Other", "10.1023/a:1011009117586"),
    ("19160026", "Springer", "10.1007/s10856-008-3666-0"),
    ("32585150", "Elsevier", "10.1016/j.actatropica.2020.105595"),
    ("26745070", "Other", "10.7314/apjcp.2015.16.18.8259"),
    ("30226777", "ACS", "10.1021/acs.molpharmaceut.8b00609"),
    ("37553758", "Other", "10.1111/bcp.15875"),
    ("16025842", "Taylor & Francis", "10.1080/10717540590925726"),
    ("41173289", "Elsevier", "10.1016/j.ejps.2025.107318"),
    ("25637670", "Elsevier", "10.1016/j.tox.2015.01.017"),
    ("16891457", "Other", "10.1158/1535-7163.MCT-06-0289")
]

OUTPUT_FILE = "Non_Elsevier_scraped_content.txt"
FAILED_LOG_FILE = "failed_Non_Elsevier_scraped_content_articles.txt"
EMAIL_FOR_UNPAYWALL = "howard.kuo@vernus.ai" # Required for Unpaywall API

# --- Helper Functions ---

def get_pdf_link_unpaywall(doi):
    """
    Strategy A: Ask Unpaywall for a free legal link.
    """
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
    """
    Strategy B: Visit the page and scrape the <meta name="citation_pdf_url"> tag.
    """
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

# --- Main Execution ---

print(f"Starting Scraping for {len(SOURCE_DATA)} articles...")

success_count = 0
failed_articles = [] # List to store (PMID, Publisher, DOI) of failed attempts

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for pmid, publisher, doi in SOURCE_DATA:
        
        # Immediate fail for missing DOIs
        if not doi or doi == "None":
            print(f"Skipping PMID {pmid} (No DOI)")
            failed_articles.append((pmid, publisher, "No DOI"))
            continue
            
        print(f"\nProcessing: {doi}...")
        
        # 1. Try Unpaywall
        pdf_url = get_pdf_link_unpaywall(doi)
        
        # 2. Try Direct Meta Tag Scraping if Unpaywall failed
        if not pdf_url:
            pdf_url = get_pdf_link_meta_tag(doi)

        # 3. Download
        extracted_content = None
        if pdf_url:
            extracted_content = download_and_extract(pdf_url)

        # 4. Save or Log Failure
        if extracted_content:
            header = f"\n\n{'='*50}\nPMID: {pmid}\nDOI: {doi}\nPUBLISHER: {publisher}\n{'='*50}\n"
            f.write(header)
            f.write(extracted_content)
            print(f"    [SUCCESS] Saved.")
            success_count += 1
        else:
            print(f"    [FAILED] Could not access PDF.")
            failed_articles.append((pmid, publisher, doi))
            
        # Random sleep to avoid bans
        time.sleep(random.uniform(2, 4))

# --- Final Reporting ---

# Write failed articles to file
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