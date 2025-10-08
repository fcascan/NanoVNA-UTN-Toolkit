"""
LaTeX PDF Exporter for NanoVNA measurement data.

This module provides functionality to export S-parameter data to PDF using LaTeX.
"""

import os
import tempfile
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pathlib import Path
from datetime import datetime
import skrf as rf
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMessageBox, QFileDialog
from pylatex import Document, Section, Subsection, Command, Figure, NewPage
from pylatex.utils import NoEscape


class LatexExporter:
    """
    Exports NanoVNA measurement data to PDF using LaTeX.
    
    Creates a professional PDF report with:
    - Cover page with project information
    - S11 section: Magnitude, Phase, Smith Chart
    - S21 section: Magnitude, Phase
    """
    
    def __init__(self, parent_widget=None):
        """
        Initialize the LaTeX exporter.
        
        Args:
            parent_widget: Parent widget for dialog boxes (optional)
        """
        self.parent_widget = parent_widget
    
    def export_to_pdf(self, freqs, s11_data, s21_data, measurement_name=None):
        """
        Export S-parameter data to PDF using LaTeX.
        
        Args:
            freqs: Frequency array in Hz
            s11_data: S11 parameter data (complex array)
            s21_data: S21 parameter data (complex array)
            measurement_name: Optional measurement name for the report
            
        Returns:
            bool: True if export successful, False otherwise
        """
        if freqs is None or s11_data is None or s21_data is None:
            self._show_warning("Missing Data", "S11, S21 or frequencies are not available.")
            return False

        filename, _ = QFileDialog.getSaveFileName(
            self.parent_widget, 
            "Export LaTeX PDF", 
            "", 
            "PDF Files (*.pdf)"
        )
        if not filename:
            return False

        file_path = Path(filename).with_suffix('')
        pdf_path = str(file_path) + ".pdf"

        try:
            with tempfile.TemporaryDirectory() as tmpdirname:
                image_files = self._generate_plots(freqs, s11_data, s21_data, tmpdirname)
                self._create_latex_document(image_files, file_path, tmpdirname, file_path.name)

            self._show_info("Success", f"LaTeX PDF exported successfully to:\\n{pdf_path}")
            return True

        except Exception as e:
            self._show_error("Error generating LaTeX PDF", str(e))
            return False
    
    def _generate_plots(self, freqs, s11_data, s21_data, output_dir):
        """
        Generate all required plots for the PDF report.
        
        Args:
            freqs: Frequency array
            s11_data: S11 data
            s21_data: S21 data
            output_dir: Directory to save plot images
            
        Returns:
            dict: Dictionary mapping plot names to file paths
        """
        image_files = {}

        # Smith Diagram
        fig, ax = plt.subplots(figsize=(10, 10))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ntw = rf.Network(frequency=freqs, s=s11_data[:, np.newaxis, np.newaxis], z0=50)
        ntw.plot_s_smith(ax=ax, draw_labels=True)
        ax.legend([Line2D([0], [0], color='blue')], ['S11'], loc='upper left', bbox_to_anchor=(-0.17, 1.14))
        smith_path = os.path.join(output_dir, "smith.png")
        fig.savefig(smith_path, dpi=300)
        plt.close(fig)
        image_files['smith'] = smith_path

        # Magnitude S11
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.plot(freqs * 1e-6, 20 * np.log10(np.abs(s11_data)), color='blue')
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel("|S11|")
        ax.set_title("Magnitude S11")
        ax.grid(True, linestyle='--', alpha=0.5)
        mag_s11_path = os.path.join(output_dir, "magnitude_s11.png")
        fig.savefig(mag_s11_path, dpi=300)
        plt.close(fig)
        image_files['mag_s11'] = mag_s11_path

        # Phase S11
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.plot(freqs * 1e-6, np.angle(s11_data, deg=True), color='blue')
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel("Phase S11 [deg]")
        ax.set_title("Phase S11")
        ax.grid(True, linestyle='--', alpha=0.5)
        phase_s11_path = os.path.join(output_dir, "phase_s11.png")
        fig.savefig(phase_s11_path, dpi=300)
        plt.close(fig)
        image_files['phase_s11'] = phase_s11_path

        # Magnitude S21
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.plot(freqs * 1e-6, 20 * np.log10(np.abs(s21_data)), color='red')
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel("|S21|")
        ax.set_title("Magnitude S21")
        ax.grid(True, linestyle='--', alpha=0.5)
        mag_s21_path = os.path.join(output_dir, "magnitude_s21.png")
        fig.savefig(mag_s21_path, dpi=300)
        plt.close(fig)
        image_files['mag_s21'] = mag_s21_path

        # Phase S21
        fig, ax = plt.subplots(figsize=(6, 4))
        fig.patch.set_facecolor("white")
        ax.set_facecolor("white")
        ax.plot(freqs * 1e-6, np.angle(s21_data, deg=True), color='red')
        ax.set_xlabel("Frequency [MHz]")
        ax.set_ylabel("Phase S21 [deg]")
        ax.set_title("Phase S21")
        ax.grid(True, linestyle='--', alpha=0.5)
        phase_s21_path = os.path.join(output_dir, "phase_s21.png")
        fig.savefig(phase_s21_path, dpi=300)
        plt.close(fig)
        image_files['phase_s21'] = phase_s21_path

        return image_files
    
    def _create_latex_document(self, image_files, file_path, tmpdirname, measurement_name):
        """
        Create the LaTeX document with all sections and images.
        
        Args:
            image_files: Dictionary of image file paths
            file_path: Output file path
            tmpdirname: Temporary directory name
            measurement_name: Name of the measurement
        """
        doc = Document(
            documentclass='article',
            document_options='12pt',
            geometry_options={'paper': 'a4paper', 'margin': '2cm'}
        )
        doc.preamble.append(Command('usepackage', 'graphicx'))

        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Read calibration info from config
        calibration_method, calibrated_parameter, measurement_number = self._get_calibration_info(
            measurement_name
        )

        # Cover page
        self._create_cover_page(doc, current_datetime, measurement_name, measurement_number, 
                               calibration_method, calibrated_parameter)

        # S11 Section
        s11_images = {
            "Magnitude": "mag_s11",
            "Phase": "phase_s11",
            "Smith Diagram": "smith"
        }
        with doc.create(Section("S11")):
            for subname, key in s11_images.items():
                with doc.create(Subsection(subname)):
                    doc.append(NoEscape(r'\begin{center}'))
                    doc.append(NoEscape(r'\includegraphics[width=0.8\linewidth]{' +
                                        image_files[key].replace("\\", "/") + '}'))
                    doc.append(NoEscape(r'\end{center}'))

        # S21 Section
        s21_images = {
            "Magnitude": "mag_s21",
            "Phase": "phase_s21"
        }
        with doc.create(Section("S21")):
            for subname, key in s21_images.items():
                with doc.create(Subsection(subname)):
                    doc.append(NoEscape(r'\begin{center}'))
                    doc.append(NoEscape(r'\includegraphics[width=0.8\linewidth]{' +
                                        image_files[key].replace("\\", "/") + '}'))
                    doc.append(NoEscape(r'\end{center}'))

        # Generate PDF
        doc.generate_pdf(str(file_path), compiler="pdflatex", clean_tex=False)
    
    def _create_cover_page(self, doc, current_datetime, measurement_name, measurement_number, 
                          calibration_method, calibrated_parameter):
        """Create the cover page for the PDF."""
        doc.append(NoEscape(r'\begin{titlepage}'))
        doc.append(NoEscape(r'\begin{center}'))

        doc.append(NoEscape(r'\vspace*{2cm}'))
        doc.append(NoEscape(r'\Huge \textbf{NanoVNA Report} \\[1.2cm]'))
        doc.append(NoEscape(r'\LARGE NanoVNA UTN Toolkit \\[0.8cm]'))
        doc.append(NoEscape(r'\large ' + current_datetime))

        doc.append(NoEscape(r'\vspace{3cm}'))
        doc.append(NoEscape(r'\begin{flushleft}'))
        doc.append(NoEscape(r'\Large \textbf{Measurement Details:} \\[0.5cm]'))
        doc.append(NoEscape(r'\normalsize'))
        doc.append(NoEscape(r'\begin{itemize}'))
        doc.append(NoEscape(rf'\item \textbf{{Measurement Name:}} {measurement_name}'))
        doc.append(NoEscape(rf'\item \textbf{{Measurement Number:}} {measurement_number}'))
        doc.append(NoEscape(rf'\item \textbf{{Calibration Method:}} {calibration_method}'))
        doc.append(NoEscape(rf'\item \textbf{{Calibrated Parameter:}} {calibrated_parameter}'))
        doc.append(NoEscape(rf'\item \textbf{{Date and Time:}} {current_datetime}'))
        doc.append(NoEscape(r'\end{itemize}'))
        doc.append(NoEscape(r'\end{flushleft}'))
        doc.append(NoEscape(r'\end{center}'))
        doc.append(NoEscape(r'\end{titlepage}'))

    def _get_calibration_info(self, measurement_name):
        """
        Get calibration information from config files.
        
        Args:
            measurement_name: Name of the measurement
            
        Returns:
            tuple: (calibration_method, calibrated_parameter, measurement_number)
        """
        try:
            # Note: This assumes a specific directory structure relative to UI
            # In a real application, you might want to make this configurable
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config_dir = os.path.join(base_dir, "calibration", "config")
            os.makedirs(config_dir, exist_ok=True)

            config_path = os.path.join(config_dir, "calibration_config.ini")
            settings = QSettings(config_path, QSettings.Format.IniFormat)
            calibration_method = settings.value("Calibration/Method", "---")
            calibrated_parameter = settings.value("Calibration/Parameter", "---")

            # Handle measurement numbering
            measurement_number = 1
            tracking_file = os.path.join(base_dir, "calibration", "config", "measurement_numbers.ini")
            tracking_settings = QSettings(tracking_file, QSettings.Format.IniFormat)
            
            if tracking_settings.contains(measurement_name):
                measurement_number = int(tracking_settings.value(measurement_name))
            else:
                all_numbers = [int(tracking_settings.value(k)) for k in tracking_settings.allKeys()]
                if all_numbers:
                    measurement_number = max(all_numbers) + 1
                tracking_settings.setValue(measurement_name, measurement_number)
                tracking_settings.sync()
                
            return calibration_method, calibrated_parameter, measurement_number
        except Exception:
            # Fallback values if config reading fails
            return "---", "---", 1
    
    def _show_warning(self, title, message):
        """Show warning message box."""
        if self.parent_widget:
            QMessageBox.warning(self.parent_widget, title, message)
    
    def _show_info(self, title, message):
        """Show information message box."""
        if self.parent_widget:
            QMessageBox.information(self.parent_widget, title, message)
    
    def _show_error(self, title, message):
        """Show error message box."""
        if self.parent_widget:
            QMessageBox.critical(self.parent_widget, title, message)