"""
===========================================================================================
@file       dcm_parser_cimage.py
@details    Definition der Klassenstruktur für das DICOM-Handling 
@author     M. Manzke
@date       05.11.2024 - Initial Version
@note       29.10.2025 - Add extract_dicom_metadata() -> Meta dta Parser
===========================================================================================
"""   
from __future__ import annotations
from typing import Any, Dict, List, Union
import pydicom
from pydicom.dataset import Dataset
from pydicom.dataelem import DataElement
from pydicom import dcmread
import numpy as np

exeption_list = [['DERIVED', 'SECONDARY', 'PATIENT_INFO'], 
                 ['ORIGINAL', 'PRIMARY', 'LOCALIZER'], 
                 ['DERIVED','SECONDARY','DOSE_INFO'],
                 ['DERIVED','SECONDARY','EXECUTED_SURVIEW'],
                 ['DERIVED','SECONDARY','REF_SURVIEW']]

"""
===========================================================================================
@class      CImage
@details    
@author     M. Manzke
@date       05.11.2024 - Initial Version
@note       
===========================================================================================
"""   
class CImage:
    """
    ===========================================================================================
    @fn         CImage.__init__()
    @details    Class constructor
    @author     M. Manzke
    @date       05.11.2024 
    @note       
    ===========================================================================================
    """   
    def __init__(self, path, _res_file_path, _logfile, ananomize_file=False):
        self.valid = False
        self.data = dcmread(path)
                
        self._modality = self.data.Modality
        self._study_description = ""
        self._series_description = ""
        self._man_modelname = ""
        self._manufacturer = ""

        self._study_reason = ""
        self._study_comments = ""
        self._cur_patient_location = ""
        self._patient_history = ""
        
        self._institutename = ""
        self._instituteaddress = ""
        self._physicianname = ""
        self._performing_physician = ""
        self._stationname = ""
        self._operatorsname = ""
        self._patientname = ""
        self._patientID = ""
        self._patientbirth = ""
        self._patientsex = ""
        self._patientsize = ""
        self._patientweight = ""
        self._patient_address = ""
        
        if ['0008','1030'] in self.data:
            self._study_description = self.data[('0008','1030')].value
        
        if ['0008','103E'] in self.data:
            self._series_description = self.data[('0008','103E')].value

        if ['0008','0060'] in self.data:
            self._modality = self.data[('0008','0060')].value

        if ['0008','0070'] in self.data:
            self._manufacturer = self.data[('0008','0070')].value

        if ['0008','0080'] in self.data:
            self._institutename = self.data[('0008','0080')].value

        if ['0008','0081'] in self.data:
            self._instituteaddress = self.data[('0008','0081')].value

        if ['0008','0090'] in self.data:
            self._physicianname = self.data[('0008','0090')].value

        if ['0008','1010'] in self.data:
            self._stationname = self.data[('0008','1010')].value

        if ['0008','1050'] in self.data:
            self._performing_physician = self.data[('0008','1050')].value

        if ['0008','1070'] in self.data:
            self._operatorsname = self.data[('0008','1070')].value
            self.data[('0008','1070')].value = "Anonym Operator"
        
        if ['0010','0010'] in self.data:
            self._patientname = self.data[('0010','0010')].value

        if ['0010','0020'] in self.data:
            self._patientID = self.data[('0010','0020')].value

        if ['0010','1040'] in self.data:
            self._patient_address = self.data[('0010','1040')].value

        if ['0038','0300'] in self.data:
            self._patientLocation = self.data[('0038','0300')].value

        if ['0010','0030'] in self.data:
           self. _patientbirth = self.data[('0010','0030')].value

        if ['0010','0040'] in self.data:
            self._patientsex = self.data[('0010','0040')].value

        if ['0010','1020'] in self.data:
            self._patientsize = self.data[('0010','1020')].value
            
        if ['0010','1030'] in self.data:
            self._patientweight = self.data[('0010','1030')].value

        if ['0032','1030'] in self.data:
            self._study_reason = self.data[('0032','1030')].value

        if ['0032','4000'] in self.data:
            self._study_comments = self.data[('0032','4000')].value

        if ['0038','0300'] in self.data:
            self._cur_patient_location = self.data[('0038','0300')].value

        if ['0010','21B0'] in self.data:
            self._patient_history = self.data[('0010','21B0')].value

        if ['0008','0008'] in self.data:
            if self.data[('0008','0008')].value not in exeption_list:
                if self._modality != "SEG":
                    try:
                        slice_thickness = 1.0
                        if self._modality == 'CT' or self._modality == 'MRT' or self._modality == 'MR':
                            slice_thickness = np.abs(self.data.ImagePositionPatient[2] - self.data.ImagePositionPatient[2])
                            self.voxelsize = [self.data.PixelSpacing[0], self.data.PixelSpacing[1],slice_thickness]

                        if self._modality == 'CT':
                            self.slope = self.data.RescaleSlope
                            self.intercept = self.data.RescaleIntercept
                    except:
                        print("ERROR: %s"%(path))
                        slice_thickness = 0
                        self.valid = False
                        return None
                        #slice_thickness = np.abs(data.SliceLocation - data.SliceLocation)
                    
                    self.data.SliceThickness = slice_thickness
                else:
                    self.data.SliceThickness = 0

                self.pat_name = self.data.PatientName
                # if debug:
                #     self.pat_age = data.PatientAge
                #     print(self.pat_age)
                    
                self.pat_id = self.data.PatientID
                self.studydate = self.data.StudyDate
                self.imagesize = [self.data.Rows, self.data.Columns, 1]
                slicethickness = self.data.SliceThickness #data[('0028','0050')].value
                self.datatype = "uint" + str(self.data.BitsAllocated) #str(data[('0028','0100')].value)
                self.valid = True
            else:
                print("NOT VALID: %s"%(self.data[('0008','0008')].value))
                self.valid = False
                return None
        else:
            print("ERROR: Tag does not exist!")
            self.valid = False
            return None

        if (ananomize_file==True):
            try: 

                if ['0018','A001'] in self.data:
                    self.data[('0018','A001')]._value._list[0][('0008', '0070')].value = "Anonymized Manufacturer"
                    self.data[('0018','A001')]._value._list[0][('0008', '0080')].value = "Anonymized Institutename"

                if ['0400','0561'] in self.data:
                    if hasattr(self.data[('0400','0561')]._value, '_list'):
                        
                        try:
                            self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0008', '0050')].value = "0123456789" 
                        except Exception as e:
                            print(e)
                            _logfile.write("ERROR: %s\n"%(path))
                            _logfile.flush()
                            _logfile.write("EXCEPTION %s\n"%(e))
                            _logfile.flush()

                        try:
                            self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0008', '0090')].value = "Anonymized Physician" 
                        except Exception as e:
                            print(e)
                            _logfile.write("ERROR: %s\n"%(path))
                            _logfile.flush()
                            _logfile.write("EXCEPTION %s\n"%(e))
                            _logfile.flush()

                        try:
                            self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0010', '0010')].value = "Anonymized Patient" 
                        except Exception as e:
                            print(e)
                            _logfile.write("ERROR: %s\n"%(path))
                            _logfile.flush()
                            _logfile.write("EXCEPTION %s\n"%(e))
                            _logfile.flush()

                        try:
                            self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0010', '0020')].value = "Anonymized PatID" 
                        except Exception as e:
                            print(e)
                            _logfile.write("ERROR: %s\n"%(path))
                            _logfile.flush()
                            _logfile.write("EXCEPTION %s\n"%(e))
                            _logfile.flush()

                        #if [('0038', '0300')] in self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0]:
                        try:
                            self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0038', '0300')].value = "Anonymized Pat Location" 
                        except Exception as e:
                            print(e)
                            _logfile.write("ERROR: %s\n"%(_res_file_path))
                            _logfile.flush()
                            _logfile.write("EXCEPTION: %s\n"%(e))
                            _logfile.flush()

                        try:
                            self.data[('0400','0561')]._value._list[0][('0400','0564')].value = "Anonymized Source of Previous Values"
                        except Exception as e:
                            print(e)
                            _logfile.write("ERROR: %s\n"%(path))
                            _logfile.flush()
                            _logfile.write("EXCEPTION %s\n"%(e))
                            _logfile.flush()
                
            except OSError as error: 
                print(error)
            
            self.data.remove_private_tags()

            if ['0008','0080'] in self.data:
                self.data[('0008','0080')].value = "Anonymized Institute"
                self._institutename = self.data[('0008','0080')].value

            if ['0008','0081'] in self.data:
                self.data[('0008','0081')].value = "Anonymized Instituteaddress"
                self._instituteaddress = self.data[('0008','0081')].value

            if ['0008','0090'] in self.data:
                self.data[('0008','0090')].value = "Anonymized Physician"
                self._physicianname = self.data[('0008','0090')].value

            if ['0008','1010'] in self.data:
                self.data[('0008','1010')].value = "Anonymized Station"
                self._stationname = self.data[('0008','1010')].value

            if ['0008','1050'] in self.data:
                self.data[('0008','1050')].value = "Anomized perf. Physician"
                self._performing_physician = self.data[('0008','1050')].value
                
            if ['0008','1070'] in self.data:
                self.data[('0008','1070')].value = "Anonymized Operator"
                self._operatorsname = self.data[('0008','1070')].value

            if ['0010','0010'] in self.data:
                self.data[('0010','0010')].value = "Anonymized Patient"
                self._patientname = self.data[('0010','0010')].value

            if ['0010','1040'] in self.data:
                self.data[('0010','1040')].value = "Anonymized Patient Address"
                self._patient_address = self.data[('0010','1040')].value

            if ['0010','0030'] in self.data:
                self._patientbirth = self.data[('0010','0030')].value 

            if ['0010','0040'] in self.data:
                self.data[('0010','0040')].value = "O"
                self._patientsex = self.data[('0010','0040')].value

            if ['0010','1020'] in self.data:
                self.data[('0010','1020')].value = "1.80"
                self._patientsize = self.data[('0010','1020')].value
                
            if ['0010','1030'] in self.data:
                self.data[('0010','1030')].value = "80"
                self._patientweight = self.data[('0010','1030')].value

            if ['0032','1030'] in self.data:
                self.data[('0032','1030')].value = "Anonymized Reason"
                self._study_reason = self.data[('0032','1030')].value

            if ['0032','4000'] in self.data:
                self.data[('0032','4000')].value = "Anonymized Patient Comments"
                self._study_comments = self.data[('0032','4000')].value

            if ['0038','0300'] in self.data:
                self.data[('0038','0300')].value = "Anonymized Patient Location"
                self._cur_patient_location = self.data[('0038','0300')].value

            if ['0010','21B0'] in self.data:
                self.data[('0010','21B0')].value = "Anonymized Patient History" 
                self._patient_history = self.data[('0010','21B0')].value

            print("Save %s"%(_res_file_path))
            self.data.save_as(_res_file_path)    

    """
    ===========================================================================================
    @fn         CImage.extract_dicom_metadata()
    @details    Class member 
    @author     M. Manzke
    @date       30.10.2025 
    @param[in]  include_private : bool  Ob private Tags (Hersteller-spezifisch) mit ausgegeben werden sollen.
    @param[in]  include_pixel_data : bool Ob das PixelData-Feld (7FE0,0010) mit ausgegeben werden soll.
    @param[in]  max_value_length : int Längere Werte werden für die Ausgabe auf diese Länge gekürzt (reine Darstellung).
    @return     List[Dict[str, Any]]:
                Liste mit Einträgen (je Tag) u.a.:
                - "path": Pfad inkl. Sequenzindex (z.B. "SharedFunctionalGroupsSequence[0].MRScaleSlope")
                - "tag": Tag im Format "(gggg,eeee)"
                - "group": int, "element": int
                - "vr": Value Representation (z.B. "LO", "DS", "SQ", ...)
                - "name": DICOM-Name (Fallback: Keyword)
                - "keyword": DICOM-Keyword
                - "value": Darstellung des Werts (gekürzt)
                - "vm": Value Multiplicity (Anzahl)
                - "private": bool (ob privater Tag)
    @note       
    ===========================================================================================
    """  
    def extract_dicom_metadata(
        self,
        include_private: bool = True,
        include_pixel_data: bool = False,
        max_value_length: int = 200,
    ) -> List[Dict[str, Any]]:
      
        results: List[Dict[str, Any]] = []

        def _format_tag(tag: Union[int, pydicom.tag.Tag]) -> str:
            t = pydicom.tag.Tag(tag)
            return f"({t.group:04X},{t.element:04X})"

        def _is_private(elem: DataElement) -> bool:
            # Private Tags haben eine ungerade Gruppen-ID
            return (elem.tag.group % 2) == 1

        def _value_to_str(elem: DataElement) -> str:
            if elem.VR == "SQ":
                return "<Sequence>"
            if elem.tag == pydicom.tag.Tag(0x7FE00010) and not include_pixel_data:
                return "<PixelData omitted>"
            try:
                v = elem.value
                # Mehrwertige Values (z.B. DS mit mehreren Werten) als kommagetrennte Liste
                if isinstance(v, (list, tuple)):
                    s = ", ".join(str(x) for x in v)
                else:
                    s = str(v)
            except Exception as e:
                s = f"<unprintable: {e}>"

            if max_value_length is not None and len(s) > max_value_length:
                s = s[:max_value_length] + "…"
            return s

        def _name_or_keyword(elem: DataElement) -> str:
            # Vorzugsweise offizieller Name; sonst Keyword; sonst leer
            return getattr(elem, "name", None) or getattr(elem, "keyword", "") or ""

        def _keyword(elem: DataElement) -> str:
            return getattr(elem, "keyword", "") or ""

        def _walk(dset: Dataset, base_path: str = "") -> None:
            for elem in dset:
                # Private Tags ggf. überspringen
                if _is_private(elem) and not include_private:
                    continue

                # PixelData ggf. überspringen (falls nicht schon via stop_before_pixels verhindert)
                if elem.tag == pydicom.tag.Tag(0x7FE00010) and not include_pixel_data:
                    val_str = "<PixelData omitted>"
                else:
                    val_str = _value_to_str(elem)

                entry = {
                    "path": (base_path + "." if base_path else "") + (_keyword(elem) or _name_or_keyword(elem) or _format_tag(elem.tag)),
                    "tag": _format_tag(elem.tag),
                    "group": int(elem.tag.group),
                    "element": int(elem.tag.element),
                    "vr": elem.VR,
                    "name": _name_or_keyword(elem),
                    "keyword": _keyword(elem),
                    "value": val_str,
                    "vm": elem.VM,
                    "private": _is_private(elem),
                }
                results.append(entry)

                # Sequenzen rekursiv ablaufen
                if elem.VR == "SQ":
                    try:
                        seq = elem.value  # List[Dataset]
                        for i, item in enumerate(seq):
                            _walk(item, base_path=entry["path"] + f"[{i}]")
                    except Exception as e:
                        results.append({
                            "path": entry["path"],
                            "tag": _format_tag(elem.tag),
                            "group": int(elem.tag.group),
                            "element": int(elem.tag.element),
                            "vr": elem.VR,
                            "name": _name_or_keyword(elem),
                            "keyword": _keyword(elem),
                            "value": f"<sequence read error: {e}>",
                            "vm": elem.VM,
                            "private": _is_private(elem),
                        })

        _walk(self.data, base_path="")
        return results

    """
    ===========================================================================================
    @fn         CImage.get_patient_and_physician()
    @details    Class member 
    @author     M. Manzke
    @date       05.11.2024 
    @param[in]  _file_path
    @param[in]  _logfile
    @return     Statische Liste
                    _file_path, 
                    self._study_description,
                    self._series_description,
                    self._institutename, 
                    self._instituteaddress, 
                    self._physicianname, 
                    self._performing_physician,
                    self._stationname, 
                    self._operatorsname, 
                    self._patientname, 
                    self._patientbirth, 
                    self._patientsex, 
                    self._patientsize, 
                    self._patientweight,
                    self._patient_address,
                    patlocation,
                    accession_num,
                    physician,
                    patient,
                    patid,
                    source_of_previous_vals, 
                    manufacturer,
                    institute, 
                    self._study_reason,
                    self._study_comments,
                    self._cur_patient_location,
                    self._patient_history
    @note       
    ===========================================================================================
    """  
    def get_patient_and_physician(self, _file_path, _logfile):
        
        manufacturer = "n.d."
        institute = "n.d."
        accession_num = "default"
        physician = "n.d."
        patient = "n.d."
        patid = "n.d."
        patlocation = "n.d."
        source_of_previous_vals = "n.d."

        if ['0018','A001'] in self.data:
            manufacturer = self.data[('0018','A001')]._value._list[0][('0008', '0070')].value = "Anonymized Manufacturer"
            institute = self.data[('0018','A001')]._value._list[0][('0008', '0080')].value = "Anonymized Institutename"       

        if ['0400','0561'] in self.data:
            if hasattr(self.data[('0400','0561')]._value, '_list'):
                try:
                    accession_num = self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0008', '0050')].value #= "0123456789" 
                except Exception as e:
                    print(e)
                    _logfile.write("ERROR: %s\n"%(_file_path))
                    _logfile.flush()
                    _logfile.write("EXCEPTION %s\n"%(e))
                    _logfile.flush()

                try:
                    physician = self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0008', '0090')].value #= "Anonymized Physician" 
                except Exception as e:
                    print(e)
                    _logfile.write("ERROR: %s\n"%(_file_path))
                    _logfile.flush()
                    _logfile.write("EXCEPTION %s\n"%(e))
                    _logfile.flush()

                try:
                    patient = self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0010', '0010')].value #= "Anonymized Patient" 
                except Exception as e:
                    print(e)
                    _logfile.write("ERROR: %s\n"%(_file_path))
                    _logfile.flush()
                    _logfile.write("EXCEPTION %s\n"%(e))
                    _logfile.flush()

                try:
                    patid = self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0010', '0020')].value #= "Anonymized PatID" 
                except Exception as e:
                    print(e)
                    _logfile.write("ERROR: %s\n"%(_file_path))
                    _logfile.flush()
                    _logfile.write("EXCEPTION %s\n"%(e))
                    _logfile.flush()
                
                if [('0038', '0300')] in self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0]:
                    patlocation = self.data[('0400','0561')]._value._list[0][('0400', '0550')]._value._list[0][('0038', '0300')].value, #= "Anonymized Pat Location"
                else:
                    patlocation = "n.d."

                try:
                    source_of_previous_vals = self.data[('0400','0561')]._value._list[0][('0400','0564')].value
                except Exception as e:
                    print(e)
                    _logfile.write("ERROR: %s\n"%(_file_path))
                    _logfile.flush()
                    _logfile.write("EXCEPTION %s\n"%(e))
                    _logfile.flush()

            # else:
            #     accession_num = "n.d."
            #     physician = "n.d."
            #     patient = "n.d."
            #     patid = "n.d."
            #     patlocation = "n.d."
            #     source_of_previous_vals = "n.d."

            return [_file_path, 
                    self._study_description,
                    self._series_description,
                    self._institutename, 
                    self._instituteaddress, 
                    self._physicianname, 
                    self._performing_physician,
                    self._stationname, 
                    self._operatorsname, 
                    self._patientname, 
                    self._patientbirth, 
                    self._patientsex, 
                    self._patientsize, 
                    self._patientweight,
                    self._patient_address,
                    patlocation,
                    accession_num,
                    physician,
                    patient,
                    patid,
                    source_of_previous_vals, 
                    manufacturer,
                    institute, 
                    self._study_reason,
                    self._study_comments,
                    self._cur_patient_location,
                    self._patient_history
                    ]
        else:
            return [_file_path, 
                    self._study_description,
                    self._series_description,
                    self._institutename, 
                    self._instituteaddress, 
                    self._physicianname, 
                    self._performing_physician,
                    self._stationname, 
                    self._operatorsname, 
                    self._patientname, 
                    self._patientbirth, 
                    self._patientsex, 
                    self._patientsize, 
                    self._patientweight,
                    self._patient_address,
                    "n.d.", 
                    "n.d.",
                    "n.d.",
                    "n.d.",
                    "n.d.",
                    source_of_previous_vals,
                    manufacturer,
                    institute,
                    self._study_reason,
                    self._study_comments,
                    self._cur_patient_location,
                    self._patient_history
                    ]
            
    
        
  