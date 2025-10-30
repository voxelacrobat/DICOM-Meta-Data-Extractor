"""
===========================================================================================
@file       dcm_parser_analyzer.py
@details    Analysemodul für DICOM-Metadaten: Graph-basierte und statistische Auswertung
@author     M. Manzke
@note       Implementation developed with Claude (Anthropic)
@date       30.10.2025 - Initial Version
===========================================================================================
"""

import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
from collections import defaultdict, Counter
from typing import List, Dict, Any, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("Warning: networkx not installed. Graph-based analysis will be limited.")

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("Warning: plotly not installed. Interactive visualizations will be limited.")


class DICOMMetadataAnalyzer:
    """
    Klasse zur Analyse von DICOM-Metadaten aus JSON-Dateien
    """
    
    def __init__(self, root_dir: str):
        """
        Initialisiert den Analyzer
        
        Args:
            root_dir: Verzeichnis mit DICOM-Dateien und zugehörigen JSON-Metadaten
        """
        self.root_dir = root_dir
        self.metadata_list = []
        self.df = None
        self.stats = {}
        
    def load_metadata_files(self) -> int:
        """
        Lädt alle JSON-Metadaten-Dateien aus dem Verzeichnis
        
        Returns:
            Anzahl geladener JSON-Dateien
        """
        print(f"Durchsuche {self.root_dir} nach JSON-Metadaten...")
        
        json_count = 0
        for dirpath, dirnames, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if filename.endswith('.json'):
                    json_path = os.path.join(dirpath, filename)
                    try:
                        with open(json_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            
                        # Füge Dateipfad-Info hinzu
                        dcm_path = json_path.replace('.json', '.dcm')
                        self.metadata_list.append({
                            'json_path': json_path,
                            'dcm_path': dcm_path,
                            'metadata': metadata
                        })
                        json_count += 1
                        
                    except Exception as e:
                        print(f"Fehler beim Laden von {json_path}: {e}")
        
        print(f"✓ {json_count} JSON-Metadaten-Dateien geladen")
        return json_count
    
    def extract_tag_value(self, metadata: List[Dict], tag: str, default="n.a.") -> Any:
        """
        Extrahiert einen Wert für einen bestimmten DICOM-Tag
        
        Args:
            metadata: Liste der Metadaten-Einträge
            tag: Tag im Format "(GGGG,EEEE)" oder Keyword
            default: Rückgabewert falls Tag nicht gefunden
            
        Returns:
            Wert des Tags oder default
        """
        for entry in metadata:
            if entry.get('tag') == tag or entry.get('keyword') == tag:
                value = entry.get('value', default)
                # "<...>" Werte als n.a. behandeln
                if isinstance(value, str) and value.startswith('<'):
                    return default
                return value
        return default
    
    def create_dataframe(self) -> pd.DataFrame:
        """
        Erstellt einen strukturierten DataFrame aus allen Metadaten
        
        Returns:
            DataFrame mit extrahierten DICOM-Informationen
        """
        print("Erstelle strukturierten DataFrame...")
        
        data = []
        for item in self.metadata_list:
            metadata = item['metadata']
            
            row = {
                'FilePath': item['dcm_path'],
                'PatientID': self.extract_tag_value(metadata, 'PatientID'),
                'PatientName': self.extract_tag_value(metadata, 'PatientName'),
                'PatientBirthDate': self.extract_tag_value(metadata, 'PatientBirthDate'),
                'PatientSex': self.extract_tag_value(metadata, 'PatientSex'),
                'StudyDate': self.extract_tag_value(metadata, 'StudyDate'),
                'StudyTime': self.extract_tag_value(metadata, 'StudyTime'),
                'StudyDescription': self.extract_tag_value(metadata, 'StudyDescription'),
                'StudyInstanceUID': self.extract_tag_value(metadata, 'StudyInstanceUID'),
                'SeriesInstanceUID': self.extract_tag_value(metadata, 'SeriesInstanceUID'),
                'SeriesDescription': self.extract_tag_value(metadata, 'SeriesDescription'),
                'SeriesNumber': self.extract_tag_value(metadata, 'SeriesNumber'),
                'Modality': self.extract_tag_value(metadata, 'Modality'),
                'Manufacturer': self.extract_tag_value(metadata, 'Manufacturer'),
                'ManufacturerModelName': self.extract_tag_value(metadata, 'ManufacturerModelName'),
                'InstitutionName': self.extract_tag_value(metadata, 'InstitutionName'),
                'StationName': self.extract_tag_value(metadata, 'StationName'),
                'BodyPartExamined': self.extract_tag_value(metadata, 'BodyPartExamined'),
                'SliceThickness': self.extract_tag_value(metadata, 'SliceThickness'),
                'KVP': self.extract_tag_value(metadata, 'KVP'),
                'ReferringPhysicianName': self.extract_tag_value(metadata, 'ReferringPhysicianName'),
            }
            data.append(row)
        
        self.df = pd.DataFrame(data)
        print(f"✓ DataFrame mit {len(self.df)} Einträgen erstellt")
        return self.df
    
    def compute_basic_statistics(self) -> Dict[str, Any]:
        """
        Berechnet grundlegende Statistiken
        
        Returns:
            Dictionary mit statistischen Kennzahlen
        """
        if self.df is None:
            self.create_dataframe()
        
        print("\n" + "="*70)
        print("GRUNDLEGENDE STATISTIKEN")
        print("="*70)
        
        self.stats = {
            'total_files': len(self.df),
            'unique_patients': self.df['PatientID'].nunique(),
            'unique_studies': self.df['StudyInstanceUID'].nunique(),
            'unique_series': self.df['SeriesInstanceUID'].nunique(),
            'modalities': self.df['Modality'].value_counts().to_dict(),
            'manufacturers': self.df['Manufacturer'].value_counts().to_dict(),
            'institutions': self.df['InstitutionName'].value_counts().to_dict(),
            'body_parts': self.df['BodyPartExamined'].value_counts().to_dict(),
        }
        
        print(f"\n📊 Gesamtanzahl DICOM-Dateien: {self.stats['total_files']}")
        print(f"👤 Eindeutige Patienten: {self.stats['unique_patients']}")
        print(f"🔬 Eindeutige Studien: {self.stats['unique_studies']}")
        print(f"📁 Eindeutige Serien: {self.stats['unique_series']}")
        
        print(f"\n🏥 Modalitäten:")
        for mod, count in self.stats['modalities'].items():
            print(f"   - {mod}: {count}")
        
        print(f"\n🏭 Hersteller:")
        for manu, count in list(self.stats['manufacturers'].items())[:5]:
            print(f"   - {manu}: {count}")
        
        return self.stats
    
    def find_duplicate_studies(self) -> pd.DataFrame:
        """
        Findet potenzielle Duplikat-Untersuchungen
        (gleicher Patient, gleiches Datum, gleiche Modalität)
        
        Returns:
            DataFrame mit potenziellen Duplikaten
        """
        if self.df is None:
            self.create_dataframe()
        
        print("\n" + "="*70)
        print("DUPLIKAT-ANALYSE")
        print("="*70)
        
        # Gruppiere nach Patient, Datum und Modalität
        duplicates = self.df.groupby(['PatientID', 'StudyDate', 'Modality']).size()
        duplicates = duplicates[duplicates > 1].reset_index(name='Count')
        
        if len(duplicates) > 0:
            print(f"\n⚠️  {len(duplicates)} potenzielle Duplikat-Untersuchungen gefunden:")
            for idx, row in duplicates.iterrows():
                print(f"   Patient: {row['PatientID']}, "
                      f"Datum: {row['StudyDate']}, "
                      f"Modalität: {row['Modality']}, "
                      f"Anzahl: {row['Count']}")
        else:
            print("\n✓ Keine Duplikat-Untersuchungen gefunden")
        
        return duplicates
    
    def analyze_temporal_distribution(self) -> pd.DataFrame:
        """
        Analysiert zeitliche Verteilung der Untersuchungen
        
        Returns:
            DataFrame mit zeitlicher Verteilung
        """
        if self.df is None:
            self.create_dataframe()
        
        print("\n" + "="*70)
        print("ZEITLICHE VERTEILUNG")
        print("="*70)
        
        # Konvertiere StudyDate zu DateTime
        df_temp = self.df.copy()
        df_temp['StudyDateTime'] = pd.to_datetime(
            df_temp['StudyDate'], 
            format='%Y%m%d', 
            errors='coerce'
        )
        
        df_temp = df_temp.dropna(subset=['StudyDateTime'])
        
        if len(df_temp) > 0:
            df_temp['Year'] = df_temp['StudyDateTime'].dt.year
            df_temp['Month'] = df_temp['StudyDateTime'].dt.month
            df_temp['YearMonth'] = df_temp['StudyDateTime'].dt.to_period('M')
            
            temporal_dist = df_temp.groupby('YearMonth').size().reset_index(name='Count')
            
            print(f"\n📅 Zeitraum: {df_temp['StudyDateTime'].min().date()} "
                  f"bis {df_temp['StudyDateTime'].max().date()}")
            print(f"📊 Untersuchungen pro Monat (Durchschnitt): "
                  f"{temporal_dist['Count'].mean():.1f}")
            
            return temporal_dist
        else:
            print("\n⚠️  Keine gültigen Datumswerte gefunden")
            return pd.DataFrame()
    
    def cluster_by_attributes(self) -> Dict[str, pd.DataFrame]:
        """
        Clustert Daten nach verschiedenen Attributen
        
        Returns:
            Dictionary mit Clustering-Ergebnissen
        """
        if self.df is None:
            self.create_dataframe()
        
        print("\n" + "="*70)
        print("ATTRIBUT-CLUSTERING")
        print("="*70)
        
        clusters = {}
        
        # Cluster 1: Modalität + Hersteller
        cluster_mod_manu = self.df.groupby(['Modality', 'Manufacturer']).size()
        cluster_mod_manu = cluster_mod_manu.reset_index(name='Count')
        cluster_mod_manu = cluster_mod_manu.sort_values('Count', ascending=False)
        clusters['modality_manufacturer'] = cluster_mod_manu
        
        print("\n🔍 Cluster: Modalität × Hersteller")
        print(cluster_mod_manu.head(10))
        
        # Cluster 2: Institution + Modalität
        cluster_inst_mod = self.df.groupby(['InstitutionName', 'Modality']).size()
        cluster_inst_mod = cluster_inst_mod.reset_index(name='Count')
        cluster_inst_mod = cluster_inst_mod.sort_values('Count', ascending=False)
        clusters['institution_modality'] = cluster_inst_mod
        
        print("\n🔍 Cluster: Institution × Modalität")
        print(cluster_inst_mod.head(10))
        
        # Cluster 3: Körperregion + Modalität
        cluster_body_mod = self.df.groupby(['BodyPartExamined', 'Modality']).size()
        cluster_body_mod = cluster_body_mod.reset_index(name='Count')
        cluster_body_mod = cluster_body_mod[cluster_body_mod['BodyPartExamined'] != 'n.a.']
        cluster_body_mod = cluster_body_mod.sort_values('Count', ascending=False)
        clusters['bodypart_modality'] = cluster_body_mod
        
        print("\n🔍 Cluster: Körperregion × Modalität")
        print(cluster_body_mod.head(10))
        
        return clusters
    
    def create_relationship_graph(self) -> None:
        """
        Erstellt einen Beziehungsgraphen zwischen DICOM-Entitäten
        (Patient -> Study -> Series -> Instance)
        """
        if not NETWORKX_AVAILABLE:
            print("\n⚠️  networkx nicht installiert. Graph-Erstellung übersprungen.")
            return
        
        if self.df is None:
            self.create_dataframe()
        
        print("\n" + "="*70)
        print("BEZIEHUNGSGRAPH-ANALYSE")
        print("="*70)
        
        G = nx.DiGraph()
        
        # Knoten und Kanten hinzufügen
        for idx, row in self.df.iterrows():
            patient_id = row['PatientID']
            study_uid = row['StudyInstanceUID']
            series_uid = row['SeriesInstanceUID']
            
            # Knoten
            G.add_node(f"P:{patient_id}", type='patient', label=patient_id)
            G.add_node(f"ST:{study_uid[:8]}...", type='study', 
                      label=row['StudyDescription'])
            G.add_node(f"SE:{series_uid[:8]}...", type='series', 
                      label=row['SeriesDescription'], modality=row['Modality'])
            
            # Kanten
            G.add_edge(f"P:{patient_id}", f"ST:{study_uid[:8]}...")
            G.add_edge(f"ST:{study_uid[:8]}...", f"SE:{series_uid[:8]}...")
        
        print(f"\n📊 Graph-Statistiken:")
        print(f"   Knoten: {G.number_of_nodes()}")
        print(f"   Kanten: {G.number_of_edges()}")
        print(f"   Dichte: {nx.density(G):.4f}")
        
        # Zentralitätsmaße
        if G.number_of_nodes() > 0:
            in_degree = dict(G.in_degree())
            top_nodes = sorted(in_degree.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"\n🎯 Top 5 Knoten nach Eingangsgrad:")
            for node, degree in top_nodes:
                print(f"   {node}: {degree}")
        
        return G
    
    def visualize_modality_distribution(self, output_path: str = None) -> None:
        """
        Visualisiert die Verteilung der Modalitäten
        
        Args:
            output_path: Pfad zum Speichern der Visualisierung
        """
        if self.df is None:
            self.create_dataframe()
        
        modalities = self.df['Modality'].value_counts()
        
        fig, ax = plt.subplots(figsize=(12, 6))
        modalities.plot(kind='bar', ax=ax, color='steelblue')
        ax.set_title('Verteilung der DICOM-Modalitäten', fontsize=16, fontweight='bold')
        ax.set_xlabel('Modalität', fontsize=12)
        ax.set_ylabel('Anzahl', fontsize=12)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ Visualisierung gespeichert: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_manufacturer_pie(self, output_path: str = None) -> None:
        """
        Erstellt ein Tortendiagramm der Hersteller-Verteilung
        
        Args:
            output_path: Pfad zum Speichern der Visualisierung
        """
        if self.df is None:
            self.create_dataframe()
        
        manufacturers = self.df['Manufacturer'].value_counts().head(10)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = plt.cm.Set3(range(len(manufacturers)))
        wedges, texts, autotexts = ax.pie(
            manufacturers, 
            labels=manufacturers.index,
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        ax.set_title('Hersteller-Verteilung (Top 10)', fontsize=16, fontweight='bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ Visualisierung gespeichert: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_temporal_trend(self, output_path: str = None) -> None:
        """
        Visualisiert zeitliche Trends der Untersuchungen
        
        Args:
            output_path: Pfad zum Speichern der Visualisierung
        """
        temporal_dist = self.analyze_temporal_distribution()
        
        if len(temporal_dist) == 0:
            print("⚠️  Keine zeitlichen Daten für Visualisierung verfügbar")
            return
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        temporal_dist['YearMonth'] = temporal_dist['YearMonth'].astype(str)
        ax.plot(temporal_dist['YearMonth'], temporal_dist['Count'], 
                marker='o', linewidth=2, markersize=6, color='darkblue')
        
        ax.set_title('Zeitlicher Trend der DICOM-Untersuchungen', 
                     fontsize=16, fontweight='bold')
        ax.set_xlabel('Jahr-Monat', fontsize=12)
        ax.set_ylabel('Anzahl Untersuchungen', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Rotiere x-Achsen-Labels
        plt.xticks(rotation=45, ha='right')
        
        # Zeige nur jeden n-ten Label
        n = max(1, len(temporal_dist) // 12)
        for i, label in enumerate(ax.xaxis.get_ticklabels()):
            if i % n != 0:
                label.set_visible(False)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ Visualisierung gespeichert: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def visualize_heatmap_modality_institution(self, output_path: str = None) -> None:
        """
        Erstellt eine Heatmap: Modalität × Institution
        
        Args:
            output_path: Pfad zum Speichern der Visualisierung
        """
        if self.df is None:
            self.create_dataframe()
        
        # Pivot-Tabelle erstellen
        heatmap_data = pd.crosstab(
            self.df['Modality'], 
            self.df['InstitutionName']
        )
        
        # Nur Top-Institutionen
        top_institutions = self.df['InstitutionName'].value_counts().head(10).index
        heatmap_data = heatmap_data[top_institutions]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.heatmap(heatmap_data, annot=True, fmt='d', cmap='YlOrRd', 
                   cbar_kws={'label': 'Anzahl'}, ax=ax)
        
        ax.set_title('Heatmap: Modalität × Institution (Top 10)', 
                     fontsize=16, fontweight='bold')
        ax.set_xlabel('Institution', fontsize=12)
        ax.set_ylabel('Modalität', fontsize=12)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ Visualisierung gespeichert: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def create_interactive_sankey(self, output_path: str = None) -> None:
        """
        Erstellt ein interaktives Sankey-Diagramm
        Patient -> Modalität -> Hersteller
        
        Args:
            output_path: Pfad zum Speichern der HTML-Datei
        """
        if not PLOTLY_AVAILABLE:
            print("\n⚠️  plotly nicht installiert. Interaktive Visualisierung übersprungen.")
            return
        
        if self.df is None:
            self.create_dataframe()
        
        # Begrenze auf Top-Einträge für Übersichtlichkeit
        top_patients = self.df['PatientID'].value_counts().head(10).index
        df_sankey = self.df[self.df['PatientID'].isin(top_patients)]
        
        # Erstelle Knoten und Links
        sources = []
        targets = []
        values = []
        labels = []
        
        # Patient -> Modalität
        patient_modal = df_sankey.groupby(['PatientID', 'Modality']).size().reset_index(name='count')
        
        patient_ids = list(patient_modal['PatientID'].unique())
        modalities = list(patient_modal['Modality'].unique())
        
        labels.extend([f"Patient {p}" for p in patient_ids])
        patient_idx_map = {p: i for i, p in enumerate(patient_ids)}
        
        labels.extend(modalities)
        modal_idx_map = {m: len(patient_ids) + i for i, m in enumerate(modalities)}
        
        for _, row in patient_modal.iterrows():
            sources.append(patient_idx_map[row['PatientID']])
            targets.append(modal_idx_map[row['Modality']])
            values.append(row['count'])
        
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=labels,
                color="blue"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values
            )
        )])
        
        fig.update_layout(
            title_text="Sankey-Diagramm: Patient → Modalität (Top 10 Patienten)",
            font_size=12,
            height=600
        )
        
        if output_path:
            fig.write_html(output_path)
            print(f"✓ Interaktive Visualisierung gespeichert: {output_path}")
        else:
            fig.show()
    
    def generate_full_report(self, output_dir: str = None) -> None:
        """
        Generiert einen vollständigen Analysebericht mit allen Visualisierungen
        
        Args:
            output_dir: Verzeichnis zum Speichern aller Outputs
        """
        if output_dir is None:
            output_dir = os.path.join(self.root_dir, "analysis_report")
        
        os.makedirs(output_dir, exist_ok=True)
        
        print("\n" + "="*70)
        print("GENERIERE VOLLSTÄNDIGEN ANALYSEBERICHT")
        print("="*70)
        
        # Lade Daten
        self.load_metadata_files()
        self.create_dataframe()
        
        # Statistiken
        stats = self.compute_basic_statistics()
        
        # Analysen
        duplicates = self.find_duplicate_studies()
        clusters = self.cluster_by_attributes()
        
        # Graph-Analyse
        if NETWORKX_AVAILABLE:
            G = self.create_relationship_graph()
        
        # Visualisierungen
        print("\n📊 Erstelle Visualisierungen...")
        
        self.visualize_modality_distribution(
            os.path.join(output_dir, "modality_distribution.png")
        )
        
        self.visualize_manufacturer_pie(
            os.path.join(output_dir, "manufacturer_pie.png")
        )
        
        self.visualize_temporal_trend(
            os.path.join(output_dir, "temporal_trend.png")
        )
        
        self.visualize_heatmap_modality_institution(
            os.path.join(output_dir, "heatmap_modality_institution.png")
        )
        
        if PLOTLY_AVAILABLE:
            self.create_interactive_sankey(
                os.path.join(output_dir, "sankey_patient_modality.html")
            )
        
        # Speichere Statistiken als JSON
        stats_path = os.path.join(output_dir, "statistics.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            # Konvertiere Counter/dict zu serialisierbarem Format
            stats_serializable = {}
            for key, value in stats.items():
                if isinstance(value, dict):
                    stats_serializable[key] = {str(k): v for k, v in value.items()}
                else:
                    stats_serializable[key] = value
            json.dump(stats_serializable, f, indent=4, ensure_ascii=False)
        
        print(f"\n✓ Statistiken gespeichert: {stats_path}")
        
        # Speichere Duplikate
        if len(duplicates) > 0:
            dup_path = os.path.join(output_dir, "duplicate_studies.csv")
            duplicates.to_csv(dup_path, index=False)
            print(f"✓ Duplikate gespeichert: {dup_path}")
        
        # Speichere Cluster
        for cluster_name, cluster_df in clusters.items():
            cluster_path = os.path.join(output_dir, f"cluster_{cluster_name}.csv")
            cluster_df.to_csv(cluster_path, index=False)
            print(f"✓ Cluster gespeichert: {cluster_path}")
        
        # Speichere DataFrame
        df_path = os.path.join(output_dir, "complete_dataframe.csv")
        self.df.to_csv(df_path, index=False)
        print(f"✓ Vollständiger DataFrame gespeichert: {df_path}")
        
        print("\n" + "="*70)
        print(f"✅ ANALYSEBERICHT VOLLSTÄNDIG ERSTELLT")
        print(f"📁 Ausgabeverzeichnis: {output_dir}")
        print("="*70)


def main():
    """
    Beispiel-Hauptfunktion zur Demonstration
    """
    # Beispiel-Verwendung
    input_path = "..\\data\\"
    
    analyzer = DICOMMetadataAnalyzer(input_path)
    analyzer.generate_full_report()


if __name__ == "__main__":
    main()