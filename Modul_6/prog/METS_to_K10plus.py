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


#Funktion Eingabe OpenDigi-Projektname, METS/MODS-Daten einlesen
def input_prj(*event):
    
    # Umlaute in Eingabe abfangen (als Projektname in OpenDigi nicht zulässig)
    if re.search("[äÄöÖüÜß]",entry_prj.get()):
        # delete_input()
        error_window()
    else:
        od_project = entry_prj.get()
        od_project = od_project.replace(" ","")
        if (len(od_project)!=0):
            # Download METS/MODS-Daten des OpenDigi-Projekts, 
            # dabei Eingabe nicht-existierender Projektnamen abfangen
            url = "https://idb.ub.uni-tuebingen.de/opendigi/"+od_project+"/mets"
            od_xml = "../data/"+od_project+".xml"
            try:
                urllib.request.urlretrieve(url,od_xml)
                mets_to_k10plus(od_project)
                delete_input()
                entry_prj.focus_set()
            except urllib.error.HTTPError as err:
                error_window()
                window.mainloop()
                            
                            
def error_window():
    # Fenster für Fehlermeldeung definieren
    window_error = tk.Tk()
    window_error.title("Fehlermeldung")
    window_error.geometry("450x250")
    # Label-Widget für Textausgabe
    label_error = ttk.Label(window_error,text="Projektname existiert nicht",font=("arial",20),padding=50)
    label_error.pack()
    # Button zum Schließen
    button_error = ttk.Button(window_error,text="OK",padding=30,command=window_error.destroy)
    button_error.pack()
    # Eventloop starten
    window_error.mainloop()
    

#Funktion Eingabe löschen
def delete_input():
    entry_prj.delete(0,tk.END)
    entry_prj.focus_set()
    

# Funktion gnd_to_ppn: K10Plus-ID (PPN) über die GND-Nummer im K10Plus abrufen
def gnd_to_ppn(gnd_nr):  
    # Normsatz aus K10Plus auslesen
    url = "http://sru.k10plus.de/opac-de-627!rec=2?&operation=searchRetrieve&query=pica.nid="+gnd_nr+"&maximumRecords=1&recordSchema=mods"
    gnd_xml = "../data/gnd.xml"
    
    try:
        urllib.request.urlretrieve(url,gnd_xml) 
        # XML parsen
        gnd_tree = ET.parse(gnd_xml)
        gnd_root = gnd_tree.getroot()    
        # K10Plus-PPN aus gnd_xml auslesen
        k10plus_ppn = gnd_root.find(".//{http://www.loc.gov/mods/v3}recordIdentifier")
        if k10plus_ppn is None:
            k10plus_ppn ="nn"
        else:
            k10plus_ppn = k10plus_ppn.text
    except urllib.error.HTTPError as err:
        k10plus_ppn = "nn"
        
    return(k10plus_ppn)

    
# Funktion mw_ppn: swb-ppn einer vorhandenen Gesamtaufnahme auslesen
def mw_ppn(od_mptr_url):  
    # METS-Daten der Gesamtaufnahme
    mptr_xml = "../data/mptr.xml"
    urllib.request.urlretrieve(od_mptr_url,mptr_xml) 
    # XML parsen
    mptr_tree = ET.parse(mptr_xml)
    mptr_root = mptr_tree.getroot()    
    # K10Plus-PPN aus mptr_xml auslesen
    mptr_id = mptr_root.findall(".//{http://www.loc.gov/mods/v3}recordIdentifier")
    for i in range(0,len(mptr_id)):
        if mptr_id[i].attrib["source"]=="swb-ppn":
            mptr_ppn = mptr_id[i].text
        if "mptr_ppn" not in locals():
            mptr_ppn = "***"
    # Variable für die Textausgabe übergeben
    return(mptr_ppn)
    

# Funktion METS/MODS-Daten des OpenDigi-Projekts bearbeiten und ausgeben
def mets_to_k10plus(od_project):
    
    # Ausgabedatei anlegen
    if os.path.exists("../data/"+od_project+".txt"):
        os.remove("../data/"+od_project+".txt")
    
    project_file = open("../data/"+od_project+".txt","a")

    # XML parsen
    od_xml = "../data/"+od_project+".xml"
    od_tree = ET.parse(od_xml)
    od_root = od_tree.getroot()

    # Einzelne Felder
    
    # PPN Digitalisat, Feld 0100
    od_id = od_root.findall(".//{http://www.loc.gov/mods/v3}recordIdentifier")
    
    for i in range(0,len(od_id)):
        if od_id[i].attrib["source"]=="swb-ppn":
            od_swbppn = od_id[i].text
            project_file.write("0100 *** PPN FÜR DIGITALISAT BEREITS VORHANDEN: "+str(od_swbppn)+"***\n")

    # Bibliografische Gattung und Status, Feld 0500
    od_smap = od_root.find(".//{http://www.loc.gov/METS/}structMap")

    if od_smap.attrib["TYPE"]=="PHYSICAL":
        od_struc = od_root.findall(".//{http://www.loc.gov/METS/}div")
        for i in range(0,len(od_struc)):
            if od_struc[i].attrib["TYPE"]=="multivolume_work":
                od_logi = "Ofu"
                # Werte zur weiteren Bearbeitung der zugehörigen Gesamtaufnahme: Titel, METS-Daten, SWB-PPN
                od_mw_title = str(od_struc[i].attrib["LABEL"])
                od_mptr = od_root.find(".//{http://www.loc.gov/METS/}mptr")
                od_mptr_url = od_mptr.attrib["{http://www.w3.org/1999/xlink}href"]
                od_mptr_prj = re.search(r"opendigi/(.+?)/mets",od_mptr_url).group(1)
                od_mw_ppn = str(mw_ppn(od_mptr_url))
                break
            else:
                od_logi = "Oau"
    else:
        od_logi = ("Ocu")
    
    project_file.write("0500 "+od_logi)

    # Entstehungsdatum, Feld 1100 und Unterfeld 1100 $n
    od_date = od_root.findall(".//{http://www.loc.gov/mods/v3}dateIssued")
    
    for i in range(0,len(od_date)):
        if "keyDate" in od_date[i].attrib:
            od_date_norm = str(od_date[i].text)[0:4]
        else:
            od_date_subm = str(od_date[i].text)
            if re.search(r"[oO]. *[dDJ].",od_date_subm):
                    od_date_norm = "[1XXX]"
                    od_date_subm = "[Entstehungdatum nicht ermittelbar]"
                           
    project_file.write("\n1100 "+od_date_norm+"$n"+od_date_subm)

    # Jahr der Digitalisierung, Felder 1109 und 4233
    today = datetime.date.today()
    today_year = today.strftime("%Y")

    project_file.write("\n1109 "+today_year)
    project_file.write("\n4233 $aaa$c"+today_year+"$5DE-21")

    # Sprache, Feld 1500
    od_lang = str(od_root.find(".//{http://www.loc.gov/mods/v3}languageTerm").text)
    
    if re.search(r" *; *",od_lang):
        od_lang = re.sub(" *; *","$a",od_lang)
    
    project_file.write("\n1500 "+od_lang)

    # PIDs: URN und DOI, Felder 2050, 2051 und 4950
    od_pid = od_root.findall(".//{http://www.loc.gov/mods/v3}identifier")

    for i in range(0,len(od_pid)):
        if od_pid[i].attrib["type"]=="urn":
            od_urn = str(od_pid[i].text)
            project_file.write("\n2050 "+od_urn)
            project_file.write("\n4950 http://nbn-resolving.de/"+od_urn+"$xR$3Volltext$534")
        elif od_pid[i].attrib["type"]=="doi":
            od_doi = str(od_pid[i].text)
            project_file.write("\n2051 "+od_doi)
            project_file.write("\n4950 https://doi.org/"+od_doi+"$xR")
            
    project_file.write("\n4950 http://idb.ub.uni-tuebingen.de/opendigi/"+od_project+"$xD$3Volltext$4LF$534")
                            
    # Personen, Feld 3010 und Unterfelder 3010 $B und $4
    # Rollenkürzel Extension
    role_ext = {"aut":"VerfasserIn$4aut",
                "rcp":"AdressatIn$4rcp",
                "ill":"IllustratorIn$4ill",
                "oth":"Sonstige Person, Familie und Körperschaft$4oth",
                "asn":"Sonstige Person, Familie und Körperschaft$4oth",
                "prt":"DruckerIn$4prt",
                "hnr":"GefeierteR$4hnr",
                "edt":"HerausgeberIn$4edt",
                "cmp":"KomponistIn$4cmp",
                "ctb":"MitwirkendeR$4ctb",
                "ths":"Praeses$4pra",
                "dis":"RespondentIn$4rsp",
                "trl":"ÜbersetzerIn$4trl",
                "col":"ZusammenstellendeR$4com",
                "edtk":"Sonstige Person, Familie und Körperschaft$4oth"}

    # alle Personnamen
    od_name = od_root.findall(".//{http://www.loc.gov/mods/v3}name")

    for i in range(0,len(od_name)):

        # Rollenkürzel
        od_name_role = str(od_root.findall(".//{http://www.loc.gov/mods/v3}roleTerm")[i].text)
                
        # Vorliegenden Namensform
        od_name_display = str(od_root.findall(".//{http://www.loc.gov/mods/v3}displayForm")[i].text)
            
        # Namen mit/ohne GND-Nummer, persönliche Namen, fingierte Rolle [Schreiber]
        y = str(od_name[i].attrib)
        if "valueURI" in y:
            gnd_url = od_name[i].attrib["valueURI"]
            gnd_nr = str(re.findall(r"/gnd/(.*)",gnd_url))
            name_ppn = gnd_to_ppn(gnd_nr)
            if name_ppn == "nn":
                project_file.write("\n3010 "+od_name_display+"$B"+role_ext[od_name_role])
            else:
                project_file.write("\n3010 !"+str(name_ppn)+"!$B"+role_ext[od_name_role])
        else:        
            # Funktionsbezeichnung [Schreiber] in Fußnote verschieben
            if "[" in od_name_display:
                od_foot = re.search(r"\[(.+?)\]",od_name_display).group(1)
                od_name_display = re.sub(r" *\[.*?\]","",od_name_display)
                project_file.write("\n4201 "+od_foot+": "+od_name_display)                          
            
            # persönliche und moderne Namen
            if ',' in od_name_display:
                project_file.write("\n3010 "+od_name_display+"$B"+role_ext[od_name_role])
            else:
                project_file.write("\n3010 $P"+od_name_display+"$B"+role_ext[od_name_role])
            
            
    # Signatur, Felder 4000 und 4065 $a
    od_shelf = str(od_root.find(".//{http://www.loc.gov/mods/v3}shelfLocator").text)
    project_file.write("\n4065 XA-DE$cUB Tübingen$a"+od_shelf)

    # Titel, Feld 4000
    od_title = str(od_root.find(".//{http://www.loc.gov/mods/v3}title").text)
    od_subtitle = od_root.find(".//{http://www.loc.gov/mods/v3}subTitle")
        
    project_file.write("\n4000 "+od_title+" - Tübingen, Universitätsbibliothek, "+od_shelf)
    if od_subtitle is not None:
        project_file.write("$d"+str(od_subtitle.text))

    # Entstehungsort, Feld 4046
    od_place = od_root.find(".//{http://www.loc.gov/mods/v3}placeTerm")
    if od_place is None:
        od_place = "[Entstehungsort nicht ermittelbar]"
    else:
        od_place = str(od_place.text)
        od_place = re.sub(r" \[u. *a.\]","",od_place)
        if re.search(r"[oO]. *[oO].*",od_place):
           od_place = "[Entstehungsort nicht ermittelbar]"
               
    project_file.write("\n4046 "+od_place+"$h"+od_date_subm)
    if od_place != "[Entstehungsort nicht ermittelbar]":
        project_file.write("\n4040 *** !PPN! *** $4prp")
        
    # Umfang von elektronischer Ressource und Original, Felder 4060 und 4068
    if od_smap.attrib["TYPE"]=="PHYSICAL":
        od_struc = od_root.findall(".//{http://www.loc.gov/METS/}div")
        for i in range(0,len(od_struc)):
            if od_struc[i].attrib["TYPE"]=="page":
                od_page = od_struc[i].attrib["ORDER"]
                od_folio = od_struc[i].attrib["ORDERLABEL"]
                od_folio = re.sub(r"[a-z]","",od_folio)
        project_file.write("\n4060 "+od_folio+" Blatt")
        project_file.write("\n4068 1 Online-Ressource ("+od_page+" Seiten)")
          
    # Verknüpfung zur Gesamtaufnahme, Felder 4150 und 4160
    if od_logi == "Ofu":
        od_vol_no = str(od_root.find(".//{http://www.loc.gov/mods/v3}partName").text)
        project_file.write("\n4150 "+od_mw_title+"$l"+od_vol_no)
        project_file.write("\n4160 !"+od_mw_ppn+"!$l"+od_vol_no)
        
    # Einzelschlagwörter, Feld 5580
    # Bei Sachschlagwörtern liefert der K10Plus leider nicht-existierende PPNs zurück / mods:topic  ---> melden?
    # geographische Schlagwörter funktionieren / mods:geographic : 
    od_geo = od_root.findall(".//{http://www.loc.gov/mods/v3}geographic")
    
    for i in range(0,len(od_geo)):
        y = str(od_geo[i].attrib)
        if "valueURI" in y:
            gnd_url = od_geo[i].attrib["valueURI"]
            gnd_nr = str(re.findall(r"/gnd/(.*)",gnd_url))
            geo_ppn = gnd_to_ppn(gnd_nr)
            if geo_ppn != "nn":
                project_file.write("\n5580 !"+str(geo_ppn)+"!")

    # Festtext an die Ausgabedatei anhängen
    project_file.write("\n0501 Text$btxt")
    project_file.write("\n0502 Computermedien$bc")
    project_file.write("\n0503 Online-Ressource$bcr")
    project_file.write("\n1101 crxcn---apaup")
    project_file.write("\n1131 !10457187X!")
    project_file.write("\n1505 $erda")
    project_file.write("\n4022 Online-Ausgabe")
    project_file.write("\n4048 Tübingen$nUniversitätsbibliothek")
    project_file.write("\n4201 Kurzaufnahme einer Handschrift\n")

    # Zeilenweise sortieren und in Datei ausgeben
    project_file = open("../data/"+od_project+".txt","r")
    data = project_file.readlines()
    data.sort()

    if os.path.exists("../data/"+od_project+"-sort.txt"):
        os.remove("../data/"+od_project+"-sort.txt")
    
    project_sort = open("../data/"+od_project+"-sort.txt","a")
    for i in range(0,len(data)):
        project_sort.write(data[i])
    
    #Exemplarsatz
    project_sort.write("\nE* l01")
    project_sort.write("\n7100 $Dn")
    project_sort.write("\n8012 ditu$adbok$ahssa")
    
    project_file.close()
    project_sort.close()
    
    if "od_mptr_prj" in locals():
        od_project = od_mptr_prj
        mets_to_k10plus(od_project)
        
    print("fertig")

# Hauptfenster definieren und auf einer Variablen ablegen, um später darauf zuzugreifen
window = tk.Tk()
window.title("Ugly is better than nothing")
window.geometry("1000x600")
window.minsize(width=600,height=400)

# Style-Database initialisieren und Theme festlegen
style = ttk.Style()
style.theme_use("classic")

# Label-Widget zur Ausgabe von Textbausteinen mit Layoutmanager pack
intro_text = "OpenDigi-Projektname eingeben:"
label_intro = ttk.Label(window,text=intro_text,font=("arial",20),padding=80)
label_intro.pack(fill="x")

# Entry-widget zur Einabe
entry_prj = ttk.Entry(window,width=40,font=("arial",20))
entry_prj.focus_set()
entry_prj.pack()

# Buttons erzeugen
button_send = ttk.Button(window,text="K10Plus Titelaufnahme",padding=30,command=input_prj)
button_send.pack(side="left",expand=True)

button_del = ttk.Button(window,text="Eingabe löschen",padding=30,command=delete_input)
button_del.pack(side="left",expand=True)

button_close = ttk.Button(window,text="Beenden",padding=30,command=window.destroy)
button_close.pack(side="left",expand=True)

window.bind("<Return>",input_prj)

# Eventloop starten
window.mainloop()
