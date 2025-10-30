"""
===========================================================================================
@file       dcm_parser_main_extended.py
@details    Erweiterte Hauptdatei mit integrierter Metadaten-Analyse
@author     M. Manzke
@date       30.10.2025
@note       Integriert dcm_parser_analyzer für umfassende DICOM-Analyse
===========================================================================================
"""   

import os
import json
import pandas as pd
from collections import defaultdict
from dcm_parser_cimage import CImage
from dcm_parser_analyzer import DICOMMetadataAnalyzer

"""
===========================================================================================
@fn         print_meta_data()
@details    Hilfsfunktion zur Command Line Print der Metadaten
@author     M. Manzke
@date       29.10.2025
@return     void
@note  
===========================================================================================
"""   
def print_meta_data(meta):
    for m in meta:
        print(f'{m["path"]} {m["tag"]} [{m["vr"]}] = {m["value"]}')

"""
===========================================================================================
@fn         meta_data_to_json()
@details    Hilfsfunktion zur Erzeugung von JSON-Objekten aus DICOM Metadaten
@author     M. Manzke
@date       29.10.2025
@return     json_string
@note  
===========================================================================================
"""     
def meta_data_to_json(meta):
    json_string = json.dumps(meta, indent=4)
    return json_string

"""
===========================================================================================
@fn         parse_study_dirs()
@details    Durchsucht rekursiv eine Verzeichnisstruktur nach DICOM-Dateien 
            und erstellt anonymisierte Kopien mit identischer Ordner- und Dateistruktur.
@param[in]  root_dir: Quellverzeichnis mit DICOM-Dateien (beliebige Struktur)
@param[in]  out_dir: Zielverzeichnis für anonymisierte Dateien
@param[in]  ananomize_dcm: optionaler Parameter zur Erstellung einer anonymisierten Verzeichnisstruktur
@author     M. Manzke
@date       05.11.2024
@return     Liste mit [Pfad zur Excel-Datei, DataFrame]
@note  
===========================================================================================
"""     
def parse_study_dirs(root_dir, out_dir, ananomize_dcm=False) -> None:
    
    if os.path.exists(root_dir):

        print("Open Log File")
        logfile = open(os.path.join(root_dir, "log.txt"), "w")
        
        # Header der Validierungs-Excel-Dateien
        _val_columns = ['file', 
                        'Study Description', 
                        'Series Description', 
                        'Institute', 
                        'Inst Address', 
                        'Physicianname', 
                        'Performing Physician', 
                        'Stationname', 
                        'Opetratorsname', 
                        'Patientname', 
                        'Patientbirth', 
                        'Patientsex', 
                        'Patientsize', 
                        'Patientweight',
                        'Patientaddress',
                        'PatLocation',
                        'AccessionNum',
                        'Physician',
                        'Patientname',
                        'patID',
                        'source_of_previous_vals',
                        'manufacturer',
                        'institute',
                        'study_reason',
                        'study_comments',
                        'patient_location',
                        'patient_history'
                        ]
        
        print(_val_columns)

        _original_list = []
        _ananomized_list = []

        # Dictionary zur Gruppierung nach DICOM-Metadaten
        series_dict = defaultdict(lambda: {'files': [], 'orgDCM': None, 'relative_path': None})
        print(series_dict)
        
        print("Suche rekursiv nach DICOM-Dateien...")
        
        # Rekursiv alle .dcm Dateien finden und dabei Original-Struktur beibehalten
        dicom_file_count = 0
        for dirpath, dirnames, filenames in os.walk(root_dir):
            print(dirpath)
            for filename in filenames:
                if filename.endswith('.dcm'):
                    dicom_file_count += 1
                    source_file = os.path.join(dirpath, filename)
                    
                    # Relativen Pfad zur root_dir ermitteln
                    rel_dir = os.path.relpath(dirpath, root_dir)
                    target_dir = os.path.join(out_dir, rel_dir)
                    target_file = os.path.join(target_dir, filename)
                    
                    if ananomize_dcm == True:
                        create_folder(target_dir)
                    
                    try:
                        print(source_file)
                        
                        # Original-Daten lesen und speichern
                        orgDCM = CImage(source_file, "dummypath", logfile, False)
                        _meta = orgDCM.extract_dicom_metadata()
                        json_data = meta_data_to_json(_meta)
                        
                        # Speichere JSON-Metadaten neben der DICOM-Datei
                        json_path = source_file.replace(".dcm", ".json")
                        with open(json_path, "w", encoding='utf-8') as text_file:
                            print(json_data, file=text_file)
                        

                        _original_row = orgDCM.get_patient_and_physician(source_file, logfile)
                        _original_list.append(_original_row)
                        print(_original_row)
                        
                        if ananomize_dcm == True:
                            # Anonymisierte Kopie erstellen
                            anoDCM = CImage(source_file, target_file, logfile, True)
                            _ananomized_row = anoDCM.get_patient_and_physician(target_file, logfile)
                            _ananomized_list.append(_ananomized_row)
                            print(_ananomized_row)
                            del anoDCM
                        
                        # Für Statistik: Gruppierung nach DICOM-Metadaten
                        if orgDCM.valid:
                            patient_id = orgDCM._patientID if orgDCM._patientID else "UNKNOWN_PATIENT"
                            
                            # SeriesInstanceUID aus DICOM-Daten holen
                            series_uid = ""
                            if hasattr(orgDCM.data, 'SeriesInstanceUID'):
                                series_uid = str(orgDCM.data.SeriesInstanceUID)
                            elif ['0020','000E'] in orgDCM.data:
                                series_uid = str(orgDCM.data[('0020','000E')].value)
                            else:
                                series_uid = rel_dir
                            
                            key = (patient_id, series_uid)
                            series_dict[key]['files'].append(source_file)
                            
                            if series_dict[key]['orgDCM'] is None:
                                series_dict[key]['orgDCM'] = orgDCM
                                series_dict[key]['relative_path'] = rel_dir
                            else:
                                del orgDCM
                        else:
                            del orgDCM
                            
                    except Exception as e:
                        print(f"Fehler bei {source_file}: {e}")
                        logfile.write(f"ERROR: {source_file}\n")
                        logfile.write(f"EXCEPTION: {e}\n")
                        logfile.flush()
        
        if dicom_file_count == 0:
            logfile.close()
            raise ValueError("Es wurden keine DICOM-Dateien gefunden.")
        
        # Daten für DataFrame vorbereiten
        data = []
        patient_set = set()
        
        print(f"\nErstelle Statistik für {len(series_dict)} Serien...")
        
        for (patient_id, series_uid), series_info in series_dict.items():
            patient_set.add(patient_id)
            orgDCM = series_info['orgDCM']
            rel_path = series_info['relative_path']
            file_count = len(series_info['files'])
            
            # Pseudo-IDs erstellen
            hash_input = (patient_id + series_uid).encode('utf-8')
            pseudo_id = hash_input
            hash_patient = patient_id.encode('utf-8')
            patid = hash_patient
            
            # Extrahiere Patient und Serie Namen aus relativem Pfad
            path_parts = rel_path.split(os.sep)
            patient_name = path_parts[0] if len(path_parts) > 0 else "unknown"
            series_name = path_parts[1] if len(path_parts) > 1 else "unknown"
            
            if orgDCM is not None:
                data.append([
                    pseudo_id,
                    patid,
                    orgDCM._modality,
                    orgDCM._manufacturer,
                    orgDCM._man_modelname,
                    orgDCM._series_description,
                    patient_name,
                    series_name,
                    file_count,
                    series_info['files'][0] if series_info['files'] else ""
                ])
                del orgDCM
            else:
                data.append([
                    pseudo_id,
                    patid,
                    "nd",
                    "nd",
                    "nd",
                    "nd",
                    patient_name,
                    series_name,
                    file_count,
                    series_info['files'][0] if series_info['files'] else ""
                ])
        
        if len(data) == 0:
            logfile.close()
            raise ValueError("Es wurden keine Patientenordner gefunden.")
        
        logfile.close()
        
        # DataFrame erstellen
        df = pd.DataFrame(data, columns=[
            'id', 'patid', 'modality', 'manufacturer', 'device', 
            'seriesdescription', 'patient', 'series', 'numimages', 'seriespath'
        ])
        df["id"] = df.index
        
        print(f"\nAnzahl der gefundenen Patienten: {len(patient_set)}")
        
        # Excel-Dateien speichern
        out_path = os.path.join(out_dir, "parsed_series.xlsx")
        df.to_excel(out_path)
        
        df_all_original_files = pd.DataFrame(_original_list, columns=_val_columns)
        df_all_original_files.to_excel(os.path.join(out_dir, "original_patient_info.xlsx"))

        if (len(_ananomized_list) > 0):
            df_all_ananomized_files = pd.DataFrame(_ananomized_list, columns=_val_columns)
            df_all_ananomized_files.to_excel(os.path.join(out_dir, "ananomized_patient_info.xlsx"))
        
        return [out_path, df]
    else:
        print(f"Der Eingabepfad {root_dir} existiert nicht.")

"""
===========================================================================================
@fn         create_folder()
@details    Hilfsfunktion zum Erstellen von Ordnern
@author     M. Manzke
@date       05.11.2024
@return     void
@note  
===========================================================================================
"""     
def create_folder(path):
    """Hilfsfunktion zum Erstellen von Ordnern"""
    if not os.path.exists(path):
        os.makedirs(path)

"""
===========================================================================================
@fn         run_complete_analysis()
@details    Führt komplette DICOM-Analyse durch: Parsing + Metadaten-Extraktion + Analyse
@param[in]  input_path: Quellverzeichnis mit DICOM-Dateien
@param[in]  output_path: Zielverzeichnis für Outputs
@param[in]  anonymize: Ob anonymisierte Kopien erstellt werden sollen
@param[in]  run_analysis: Ob erweiterte Analyse durchgeführt werden soll
@author     M. Manzke
@date       30.10.2025
@return     void
@note  
===========================================================================================
"""
def run_complete_analysis(input_path, output_path, anonymize=False, run_analysis=True):
    """
    Führt komplette Analyse durch
    """
    print("\n" + "="*70)
    print("DICOM METADATEN PARSER & ANALYZER")
    print("="*70)
    
    # Schritt 1: Parse DICOM-Dateien und extrahiere Metadaten
    print("\n[SCHRITT 1/2] Parse DICOM-Dateien und extrahiere Metadaten...")
    out_path, df = parse_study_dirs(input_path, output_path, anonymize)
    
    print(f"\n✓ Parsing abgeschlossen. {len(df)} Serien verarbeitet.")
    print(f"✓ Ergebnisse gespeichert in: {output_path}")
    
    # Schritt 2: Erweiterte Analyse der Metadaten
    if run_analysis:
        print("\n[SCHRITT 2/2] Starte erweiterte Metadaten-Analyse...")
        
        analyzer = DICOMMetadataAnalyzer(input_path)
        
        # Generiere vollständigen Bericht
        analysis_output = os.path.join(output_path, "analysis_report")
        analyzer.generate_full_report(output_dir=analysis_output)
        
        print(f"\n✓ Analyse abgeschlossen.")
        print(f"✓ Analysebericht gespeichert in: {analysis_output}")
    
    print("\n" + "="*70)
    print("✅ ALLE SCHRITTE ERFOLGREICH ABGESCHLOSSEN")
    print("="*70)


"""
===========================================================================================
@fn         main()
@details    Hauptfunktion
@author     M. Manzke
@date       30.10.2025
@return     void
@note  
===========================================================================================
"""     
def main(): 
    """
    Beispiel-Hauptfunktion
    
    Verwendungsoptionen:
    
    1. Nur Parsing (ohne Anonymisierung, ohne Analyse):
       run_complete_analysis(input_path, output_path, anonymize=False, run_analysis=False)
    
    2. Parsing + Anonymisierung (ohne Analyse):
       run_complete_analysis(input_path, output_path, anonymize=True, run_analysis=False)
    
    3. Parsing + Analyse (ohne Anonymisierung):
       run_complete_analysis(input_path, output_path, anonymize=False, run_analysis=True)
    
    4. Alles (Parsing + Anonymisierung + Analyse):
       run_complete_analysis(input_path, output_path, anonymize=True, run_analysis=True)
    """
    
    input_path = "..\\data\\"
    output_path = "..\\data_ano\\"
    input_path = "D:\\01_EINRICHTUNGEN\\07_DZKJ\\05_PROJEKTE\\SPINEeX\\DATEN\\"
    output_path = "D:\\01_EINRICHTUNGEN\\07_DZKJ\\05_PROJEKTE\\SPINEeX\\DATEN_ANO\\"
    
    # Führe komplette Analyse durch (mit Anonymisierung und Analyse)
    run_complete_analysis(
        input_path=input_path,
        output_path=output_path,
        anonymize=True,
        run_analysis=True
    )
    
    # Alternative: Nur Analyse auf bereits geparsten Daten
    # analyzer = DICOMMetadataAnalyzer(input_path)
    # analyzer.generate_full_report(output_dir=os.path.join(output_path, "analysis_report"))


if __name__ == "__main__":
    main()