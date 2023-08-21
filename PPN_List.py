##!/home/ume/anaconda3/bin/python3
# #!/usr/bin/env python3

# Modul 6 - Projektaufgabe
# Ugly is better than nothing - Generieren von Titelaufnahmen aus den
# METS/MODS-Daten digitalisierter Handschriften zur Übernahme in den K10plus
# Ulrike Mehringer, 2023

# Teil 2: Liste "Projektname - PPN des Digitalisats" für die manuelle Eingabe in Dwork

import urllib.request
import xml.etree.ElementTree as ET
import datetime
import re
import os
import pandas as pd

# Dataframes

df_name = pd.DataFrame(columns=["Projektname"])
df_ppn = pd.DataFrame(columns=["PPN"])
df_date = pd.DataFrame(columns=["Datum"])

# Katalogsätze aus K10Plus auslesen

# für später:
# today = datetime.date.today()
# today_year_month = today.strftime("%Y-%m")


datum = "2022-09-*"
url = "http://sru.k10plus.de/opac-de-627?operation=searchRetrieve&query=pica.abl=hssa%20and%20pica.aiw=Handschrift%20and%20pica.aed="+datum+"&maximumRecords=100&recordSchema=mods"
list_xml = "../data/list.xml"
    
try:
    urllib.request.urlretrieve(url,list_xml) 
    # XML parsen
    list_tree = ET.parse(list_xml)
    list_root = list_tree.getroot()
    
    # OpenDigi-Projektname
    record_url = list_root.findall(".//{http://www.loc.gov/mods/v3}url")
    
    for i in range(0,len(record_url)):
        y = str(record_url[i].attrib)
        if "usage" in y:
            rec_url = record_url[i].text
            record_prj = re.search(r"opendigi/(.*)",rec_url).group(1)
            df_name = df_name.append({"Projektname":record_prj},ignore_index=True)
                
    # PPN Digitalisat
    record_ppn = list_root.findall(".//{http://www.loc.gov/mods/v3}recordIdentifier")
    for i in range(0,len(record_ppn)):
        rec_ppn = record_ppn[i].text
        df_ppn = df_ppn.append({"PPN":rec_ppn},ignore_index=True)
          
    # Datum
    record_date = list_root.findall(".//{http://www.loc.gov/mods/v3}recordCreationDate")
    for i in range(0,len(record_date)):
        rec_date = record_date[i].text
        df_date = df_date.append({"Datum":rec_date},ignore_index=True)
        
except urllib.error.URLError as err:
    print("Liste konnte nicht abgerufen werden.")

df = df_name.join(df_ppn)
df_liste = df.join(df_date)

print(df_liste)


# Ausgabedatei anlegen
if os.path.exists("../data/ppn_list.txt"):
    os.remove("../data/ppn_list.txt")
    
with open ("../data/ppn_list.txt","a") as file:
    df_liste_string = df_liste.to_string(header=True,index=True)
    file.write(df_liste_string)
    
file.close()