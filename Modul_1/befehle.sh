#!/bin/bash
# Modul 1, Aufgabe 3

# Zeilen mit ISSN auswählen, und ggf. leider auch Seiten- und Jahresangaben in diesem Format
grep -E '[0-9]{4}\-[0-9]{3,4}' 2022-11-28-Article_list_dirty.tsv > issn.hi1

# Einleitende Wendung ISSN löschen
sed -i 's/[<Ii][Ss][Ss][Nn]:* *//g' issn.hi1

# Spalten getrennt auswählen und in Hilfsdateien ausgeben ... nicht sehr elegant, aber ich habs nicht anders hinbekommen  
grep -i 'IMPORTANT*' issn.hi1 | cut -f7,14 > issn.hi2
grep -iv 'IMPORTANT*' issn.hi1 | cut -f5,12 > issn.hi3

# Hilfsdateien zusammenführen, CR entfernen, sortieren, und Mehrfacheinträge zusammenfassen 
cat issn.hi2 issn.hi3 | tr -d '\r' | sort | uniq > 2022-11-28-Dates_and_ISSNs.tsv
