##!/home/ume/anaconda3/bin/python3
# #!/usr/bin/env python3

# Modul 6 - Projektaufgabe
# Ugly is better than nothing - Generieren von Titelaufnahmen aus den
# METS/MODS-Daten digitalisierter Handschriften zur Übernahme in den K10plus
# Ulrike Mehringer, 2023

import urllib.request
import xml.etree.ElementTree as ET
import datetime
import re
import os
import tkinter as tk
from tkinter import ttk


#Funktion Eingabe Projekname
def project_input():
    global od_project    # Ich ENTSCHULDIGE mich!!
    od_project = entry1.get()
    delete_input()
    entry1.focus_set()
    mets_to_k10plus()
    print("fertig")
    

#Funktion Eingabe löschen
def delete_input():
    entry1.delete(0,tk.END)
    

# Funktion gnd_to_ppn: Personennormsatz-ID (PPN) über die GND-Nummer im K10Plus abrufen
def gnd_to_ppn(gnd_nr):  
## Normsatz aus K10Plus auslesen
    url = "http://sru.k10plus.de/opac-de-627!rec=2?&operation=searchRetrieve&query=pica.nid="+gnd_nr+"&maximumRecords=1&recordSchema=mods"
    person_xml = "../data/person.xml"
    urllib.request.urlretrieve(url,person_xml)  
## XML parsen
    person_tree = ET.parse(person_xml)
    person_root = person_tree.getroot()    
## K10Plus-PPN aus person_xml auslesen
    rec_id = person_root.find('.//{http://www.loc.gov/mods/v3}recordIdentifier')   
## Variable für die Textausgabe
    person_ppn = rec_id.text
    return(person_ppn)


# Hauptfunktion METS/MODS-Daten des OpenDigi-Projekts einlesen, verändern, ausgeben
def mets_to_k10plus():
    # METS/MODS-Daten des OpenDigi-Projekts einlesen
    url = "https://idb.ub.uni-tuebingen.de/opendigi/"+od_project+"/mets"
    od_xml = "../data/"+od_project+".xml"
    urllib.request.urlretrieve(url,od_xml)

    # Zieldatei anlegen
    if os.path.exists("../data/"+od_project+".txt"):
        os.remove("../data/"+od_project+".txt")
    
    project_file = open("../data/"+od_project+".txt",'a')

    # XML parsen
    od_tree = ET.parse(od_xml)
    od_root = od_tree.getroot()

    # Einzelne Felder

    # Bibliografische Gattung und Status, Feld 0500
    od_smap = od_root.find(".//{http://www.loc.gov/METS/}structMap")

    if od_smap.attrib['TYPE']=='PHYSICAL':
        od_struc = od_root.findall(".//{http://www.loc.gov/METS/}div")
        for i in range(0,len(od_struc)):
            if od_struc[i].attrib["TYPE"]=="multivolume_work":
                od_logi = "Ofu"
                break
            else:
                od_logi = "Oau"
        ### hier Funktion einfügen: die url der GA auslesen, GA einlesen, schaun ob PPN-Digi vorhanden: 
        ### ja: ppn merken für 4160
        ### nein: ist blöd
    else:
        od_logi = ("Ocu")
    
    project_file.write('0500 '+od_logi)

    # Entstehungsdatum, Feld 1100, 1100 $n
    od_date = od_root.findall(".//{http://www.loc.gov/mods/v3}dateIssued")
    od_date_norm = od_date[0].text
    od_date_subm = "["+od_date[1].text+"]"

    if re.search(r"[oO]. *[dDJ].",od_date_subm):
        od_date_norm = "[1XXX]"
        od_date_subm = "[Entstehungdatum nicht ermittelbar]"

    project_file.write('\n1100 '+od_date_norm+'$n'+od_date_subm)

    # Jahr der Digitalisierung, Feld 1109
    today = datetime.date.today()
    today_year = today.strftime("%Y")

    project_file.write('\n1109 '+today_year)

    # Sprache, Feld 1500
    od_lang = od_root.find(".//{http://www.loc.gov/mods/v3}languageTerm").text

    if re.search(r"; *",od_lang):
        od_lang = str_replace("; ","$a",od_lang)
    
    project_file.write('\n1500 '+od_lang)

    # PIDs: URN und DOI, Felder 2050, 2051 und 4950
    od_pid = od_root.findall(".//{http://www.loc.gov/mods/v3}identifier")

    for i in range(0,len(od_pid)):
        if od_pid[i].attrib["type"]=="urn":
            od_urn = od_pid[i].text
            project_file.write('\n2050 '+od_urn)
            project_file.write('\n4950 http://nbn-resolving.de/'+od_urn+'$xR$3Volltext$534')
        elif od_pid[i].attrib["type"]=="doi":
            od_doi = od_pid[i].text
            project_file.write('\n2051 '+od_doi)
            project_file.write('\n4950 https://doi.org/'+od_doi+'$xR')

    project_file.write('\n4950 http://idb.ub.uni-tuebingen.de/opendigi/'+od_project+'$xD$3Volltext$4LF$534')
        
    # Personen, Feld 3000, 3010
    # Rollenkürzel Extension
    role_ext = {'aut':'VerfasserIn$4aut',
                'rcp':'AdressatIn$4rcp',
                'ill':'IllustratorIn$4ill',
                'oth':'Sonstige Person, Familie und Körperschaft$4oth',
                'asn':'Sonstige Person, Familie und Körperschaft$4oth',
                'prt':'DruckerIn$4prt',
                'hnr':'GefeierteR$4hnr',
                'edt':'HerausgeberIn$4edt',
                'cmp':'KomponistIn$4cmp',
                'ctb':'MitwirkendeR$4ctb',
                'ths':'Praeses$4pra',
                'dis':'RespondentIn$4rsp',
                'trl':'ÜbersetzerIn$4trl',
                'col':'ZusammenstellendeR$4com',
                'edtk':'Sonstige Person, Familie und Körperschaft$4oth'}

    # alle Personnamen
    od_name = od_root.findall(".//{http://www.loc.gov/mods/v3}name")

    for i in range(0,len(od_name)):

        # Rollenkürzel
        od_name_role = od_root.findall('.//{http://www.loc.gov/mods/v3}roleTerm')[i].text
    
        # Namen mit/ohne GND-Nummer, persönliche Namen, fingierte Rolle [Schreiber]
        y = str(od_name[i].attrib)
        if 'valueURI' in y:
            gnd_url = od_name[i].attrib['valueURI']
            gnd_nr = str(re.findall(r'/gnd/(.*)',gnd_url))
            name_ppn = gnd_to_ppn(gnd_nr)
            project_file.write('\n3010 !'+name_ppn+'!$B'+role_ext[od_name_role])
        else:
            od_name_display = od_root.findall(".//{http://www.loc.gov/mods/v3}displayForm")[i].text
            # persönliche und moderne Namen
            if ',' in od_name_display:
                project_file.write('\n3010 '+od_name_display+'$B'+role_ext[od_name_role])
            else:
                project_file.write('\n3010 $P'+od_name_display+'$B'+role_ext[od_name_role])
            
            
    # Signatur, Feld 4000 und 4065 $a
    od_shelf = od_root.find(".//{http://www.loc.gov/mods/v3}shelfLocator").text
    project_file.write('\n4065 XA-DE$cUB Tübingen$a'+od_shelf)

    # Titel, Feld 4000
    od_title = od_root.find(".//{http://www.loc.gov/mods/v3}title").text
    project_file.write('\n4000 '+od_title+" - Tübingen, Universitätsbibliothek, "+od_shelf)

    # Entstehungsort, Feld 4046 (Feld 4040?)
    od_place = od_root.find(".//{http://www.loc.gov/mods/v3}placeTerm").text

    if re.search(r"[oO]. *[oO.]",od_place):
        od_place = "[Entstehungsort nicht ermittelbar]"
    
    project_file.write('\n4046 '+od_place+'$h'+od_date_subm)

    # Festtext an die Ausgabedatei anhängen
    project_file.write('\n0501 Text$btxt')
    project_file.write('\n0502 Computermedien$bc')
    project_file.write('\n0503 Online-Ressource$bcr')
    project_file.write('\n1101 crxcn---apaup')
    project_file.write('\n1131 !10457187X!')
    project_file.write('\n1505 $erda')
    project_file.write('\n4022 Online-Ausgabe')
    project_file.write('\n4048 Tübingen$nUniversitätsbibliothek')
    project_file.write('\n4201 Kurzaufnahme einer Handschrift')
    project_file.write('\n4233 $aaa$c2023$5DE-21\n')

    # Zeilenweise sortieren und in Datei ausgeben
    project_file = open("../data/"+od_project+".txt",'r')
    data = project_file.readlines()
    data.sort()

    if os.path.exists("../data/"+od_project+"-sort.txt"):
        os.remove("../data/"+od_project+"-sort.txt")
    
    project_sort = open('../data/'+od_project+'-sort.txt','a')
    for i in range(0,len(data)):
        project_sort.write(data[i])
    
    #Exemplarsatz
    project_sort.write('\nE* l01')
    project_sort.write('\n7100 $Dn')
    project_sort.write('\n8012 ditu$adbok$ahssa')
    
    project_file.close()
    project_sort.close()

    print("fertig")


# Hauptfenster definieren und auf einer Variablen ablegen, um später darauf zuzugreifen
window = tk.Tk()
window.title('Ugly is better than nothing')
window.geometry('1000x600')
window.minsize(width=600,height=400)

# Style-Database initialisieren und Theme festlegen
style = ttk.Style()
style.theme_use('classic')

# Label-Widget zur Ausgabe von Textbausteinen mit Layoutmanager pack
intro_text = 'Dwork-Projektname eingeben:'
label1 = ttk.Label(window,text=intro_text,font=('arial',20),padding=80)
label1.pack(fill='x')

# Entry-widget zur Einabe
entry1 = ttk.Entry(window,width=40,font=('arial',20))
entry1.focus_set()
entry1.pack()

# Button erzeugen
button1 = ttk.Button(window,text='K10Plus Titelaufnahme',padding=30,command=project_input)
button1.pack(side='left',expand=True)

button2 = ttk.Button(window,text='Eingabe löschen',padding=30,command=delete_input)
button2.pack(side='left',expand=True)

button3 = ttk.Button(window,text='Beenden',padding=30,command=window.destroy)
button3.pack(side='left',expand=True)

# Eventloop starten
window.mainloop()
