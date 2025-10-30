"""
Export Dialog for Graphics Window
Provides functionality to export graph data and images in various formats.
"""

import io
import os
import numpy as np
import matplotlib.pyplot as plt
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QMessageBox, QApplication, QFileDialog)
from PySide6.QtCore import QTimer, QThread, Qt, QSettings
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class ExportDialog(QDialog):
    """Dialog for exporting graph data and images."""
    
    def __init__(self, parent=None, figure=None, left_graph=None, right_graph=None, freqs = None, show_markers_left=None, show_markers_right=None, 
        update_cursor_left = None, update_cursor_right = None):
        super().__init__(parent)

        self.left_graph = left_graph
        self.right_grap = right_graph
        self.freqs = freqs

        self.show_markers_left = show_markers_left 
        self.show_markers_right = show_markers_right

        self.update_cursor_left = update_cursor_left
        self.update_cursor_right = update_cursor_right

        ui_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(ui_dir, "graphics_windows", "ini", "config.ini")

        settings = QSettings(ruta_ini, QSettings.IniFormat)

        # QWidget
        background_color = settings.value("Dark_Light/QWidget/background-color", "#3a3a3a")

        # QTabWidget pane
        tabwidget_pane_bg = settings.value("Dark_Light/QTabWidget_pane/background-color", "#3b3b3b")

        # QTabBar
        tabbar_bg = settings.value("Dark_Light/QTabBar/background-color", "#2b2b2b")
        tabbar_color = settings.value("Dark_Light/QTabBar/color", "white")
        tabbar_padding = settings.value("Dark_Light/QTabBar/padding", "5px 12px")
        tabbar_border = settings.value("Dark_Light/QTabBar/border", "none")
        tabbar_border_tl_radius = settings.value("Dark_Light/QTabBar/border-top-left-radius", "6px")
        tabbar_border_tr_radius = settings.value("Dark_Light/QTabBar/border-top-right-radius", "6px")

        # QTabBar selected
        tabbar_selected_bg = settings.value("Dark_Light/QTabBar_selected/background-color", "#4d4d4d")
        tabbar_selected_color = settings.value("Dark_Light/QTabBar/color", "white")

        # QSpinBox
        spinbox_bg = settings.value("Dark_Light/QSpinBox/background-color", "#3b3b3b")
        spinbox_color = settings.value("Dark_Light/QSpinBox/color", "white")
        spinbox_border = settings.value("Dark_Light/QSpinBox/border", "1px solid white")
        spinbox_border_radius = settings.value("Dark_Light/QSpinBox/border-radius", "8px")

        # QGroupBox title
        groupbox_title_color = settings.value("Dark_Light/QGroupBox_title/color", "white")

        # QLabel
        label_color = settings.value("Dark_Light/QLabel/color", "white")

        # QLineEdit
        lineedit_bg = settings.value("Dark_Light/QLineEdit/background-color", "#3b3b3b")
        lineedit_color = settings.value("Dark_Light/QLineEdit/color", "white")
        lineedit_border = settings.value("Dark_Light/QLineEdit/border", "1px solid white")
        lineedit_border_radius = settings.value("Dark_Light/QLineEdit/border-radius", "6px")
        lineedit_padding = settings.value("Dark_Light/QLineEdit/padding", "4px")
        lineedit_focus_bg = settings.value("Dark_Light/QLineEdit_focus/background-color", "#454545")
        lineedit_focus_border = settings.value("Dark_Light/QLineEdit_focus/border", "1px solid #4d90fe")

        # QPushButton
        pushbutton_bg = settings.value("Dark_Light/QPushButton/background-color", "#3b3b3b")
        pushbutton_color = settings.value("Dark_Light/QPushButton/color", "white")
        pushbutton_border = settings.value("Dark_Light/QPushButton/border", "1px solid white")
        pushbutton_border_radius = settings.value("Dark_Light/QPushButton/border-radius", "6px")
        pushbutton_padding = settings.value("Dark_Light/QPushButton/padding", "4px 10px")
        pushbutton_hover_bg = settings.value("Dark_Light/QPushButton_hover/background-color", "#4d4d4d")
        pushbutton_pressed_bg = settings.value("Dark_Light/QPushButton_pressed/background-color", "#5c5c5c")

        # QMenu
        menu_bg = settings.value("Dark_Light/QMenu/background", "#3a3a3a")
        menu_color = settings.value("Dark_Light/QMenu/color", "white")
        menu_border = settings.value("Dark_Light/QMenu/border", "1px solid #3b3b3b")
        menu_item_selected_bg = settings.value("Dark_Light/QMenu::item:selected/background-color", "#4d4d4d")

        # QMenuBar
        menu_item_color = settings.value("Dark_Light/QMenu_item_selected/background-color", "4d4d4d")
        menubar_bg = settings.value("Dark_Light/QMenuBar/background-color", "#3a3a3a")
        menubar_color = settings.value("Dark_Light/QMenuBar/color", "white")
        menubar_item_bg = settings.value("Dark_Light/QMenuBar_item/background", "transparent")
        menubar_item_color = settings.value("Dark_Light/QMenuBar_item/color", "white")
        menubar_item_padding = settings.value("Dark_Light/QMenuBar_item/padding", "4px 10px")
        menubar_item_selected_bg = settings.value("Dark_Light/QMenuBar_item_selected/background-color", "#4d4d4d")

        self.setStyleSheet(f"""
            QWidget {{
                background-color: {background_color};
            }}
            QTabWidget::pane {{
                background-color: {tabwidget_pane_bg}; 
            }}
            QTabBar::tab {{
                background-color: {tabbar_bg}; 
                color: {tabbar_color};
                padding: {tabbar_padding};
                border: {tabbar_border}; 
                border-top-left-radius: {tabbar_border_tl_radius};
                border-top-right-radius: {tabbar_border_tr_radius};
            }}
            QMenu{{
                color_ {menubar_color};
                background-color_ {menu_item_color};
            }}
            QTabBar::tab:selected {{
                background-color: {tabbar_selected_bg};  
                color: {tabbar_selected_color};
            }}
            QSpinBox {{
                background-color: {spinbox_bg};
                color: {spinbox_color};
                border: {spinbox_border};
                border-radius: {spinbox_border_radius};
            }}
            QGroupBox:title {{
                color: {groupbox_title_color};  
            }}
            QLabel {{
                color: {label_color};  
            }}
            QLineEdit {{
                background-color: {lineedit_bg};
                color: {lineedit_color};
                border: {lineedit_border};
                border-radius: {lineedit_border_radius};
                padding: {lineedit_padding};
            }}
            QLineEdit:focus {{
                background-color: {lineedit_focus_bg};
                border: {lineedit_focus_border};
            }}
            QPushButton {{
                background-color: {pushbutton_bg};
                color: {pushbutton_color};
                border: {pushbutton_border};
                border-radius: {pushbutton_border_radius};
                padding: {pushbutton_padding};
            }}
            QPushButton:hover {{
                background-color: {pushbutton_hover_bg};
            }}
            QPushButton:pressed {{
                background-color: {pushbutton_pressed_bg};
            }}
            QMenuBar {{
                background-color: {menubar_bg};
                color: {menubar_color};
            }}
            QMenuBar::item {{
                background: {menubar_item_bg};
                color: {menubar_item_color};
                padding: {menubar_item_padding};
            }}
            QMenuBar::item:selected {{
                background: {menubar_item_selected_bg};
            }}
            QMenu {{
                background-color: {menu_bg};
                color: {menu_color};
                border: {menu_border};
            }}
            QMenu::item:selected {{
                background-color: {menu_item_color};
            }}
        """)

        self.figure = figure
        self.parent_window = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface for the export dialog."""
        self.setWindowTitle("Export Graph")
        self.setModal(True)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Preview section
        preview_label = QLabel("Preview:")
        layout.addWidget(preview_label)
        
        # Create and add preview image
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        self.preview_label.setMinimumHeight(300)
        
        # Generate static preview
        preview_pixmap = self.create_static_preview()
        if preview_pixmap:
            # Scale preview to fit while maintaining aspect ratio
            scaled_pixmap = preview_pixmap.scaled(
                self.preview_label.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)
        
        layout.addWidget(self.preview_label)
        
        # Buttons section
        buttons_layout = QHBoxLayout()
        
        # Copy to clipboard button
        copy_button = QPushButton("Copy to Clipboard")
        copy_button.clicked.connect(self.copy_to_clipboard)
        buttons_layout.addWidget(copy_button)
        
        # Save as image button
        save_image_button = QPushButton("Save as Image")
        save_image_button.clicked.connect(self.save_as_image)
        buttons_layout.addWidget(save_image_button)
        
        # Save as CSV button
        save_csv_button = QPushButton("Save as CSV")
        save_csv_button.clicked.connect(self.save_as_csv)
        buttons_layout.addWidget(save_csv_button)
        
        layout.addLayout(buttons_layout)
        
        # Close button
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        close_layout.addWidget(close_button)
        layout.addLayout(close_layout)

    def create_static_preview(self):
        """Create a static preview image of the graph with info boxes for active markers."""
        import io
        import numpy as np
        import matplotlib.pyplot as plt
        from PySide6.QtGui import QPixmap

        if not self.figure:
            return None

        import copy
        fig_copy = copy.deepcopy(self.figure)

        # Eliminar ejes pequeños (sliders, colorbars, etc.)
        axes_to_keep = [ax for ax in fig_copy.axes if ax.get_position().height > 0.1 and ax.get_position().width > 0.1]
        if not axes_to_keep:
            return None
        ax = axes_to_keep[0]

        actual_dir = os.path.dirname(os.path.dirname(__file__))  
        ruta_ini = os.path.join(actual_dir, "ui", "graphics_windows", "ini", "config.ini")
        settings = QSettings(ruta_ini, QSettings.IniFormat)

        # Determinar si la figura es la izquierda o la derecha
        if self.figure == getattr(self.parent_window, 'fig_left', None):
            active_markers = [
                (getattr(self.parent_window, 'cursor_left', None), 1, self.show_markers_left[0]),
                (getattr(self.parent_window, 'cursor_left_2', None), 2, self.show_markers_left[1])
            ]
            unit = settings.value("Graphic1/db_times", "dB")

            graph = settings.value("Tab1/GraphType1", "Magnitude")

            color = 'red'
        elif self.figure == getattr(self.parent_window, 'fig_right', None):
            active_markers = [
                (getattr(self.parent_window, 'cursor_right', None), 1, self.show_markers_right[0]),
                (getattr(self.parent_window, 'cursor_right_2', None), 2, self.show_markers_right[1])
            ]
            unit = settings.value("Graphic2/db_times", "dB")

            graph = settings.value("Tab2/GraphType2", "Magnitude")

            color = 'blue'
        else:
            return None

        # Filtrar marcadores activos
        active_markers = [(cursor, mid) for cursor, mid, show in active_markers if show and cursor is not None]
        if not active_markers:
            return None

        # Mantener estilo y fondo original, solo ajustando tamaño
        fig_copy.set_size_inches(6, 4)
        fig_copy.set_dpi(300)

        # Ocultar ejes pequeños (sliders)
        for ax_sub in fig_copy.axes:
            pos = ax_sub.get_position()
            if pos.height < 0.1 or pos.width < 0.1:
                ax_sub.set_visible(False)

        # --- Dibujar markers e info boxes ---
        box_height = 0.15
        ypos_start = 0.9

        if len(active_markers) == 1:
            ypos_step = box_height + 0.02
        else:
            ypos_step = box_height + 0.12 

        for i, (cursor, marker_id) in enumerate(active_markers):

            if graph == "Magnitude":
                x_data, y_data = cursor.get_data()
                if len(x_data) == 0 or len(y_data) == 0:
                    continue

                freq = x_data[0]
                magnitude = y_data[0]

                # Dibujar caja de información
                ypos = ypos_start - i * ypos_step
                info_text = (
                    f"Marker {marker_id}\n"
                    f"Freq: {x_data[0]:.2f}\n"
                    f"|S|: {magnitude:.3f}{unit}"
                )
                ax.text(   
                        0.05, ypos, info_text,
                    transform=ax.transAxes,
                    fontsize=8,
                    verticalalignment='top',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='black')
                )

            if graph == "Phase":
                x_data, y_data = cursor.get_data()
                if len(x_data) == 0 or len(y_data) == 0:
                    continue

                freq = x_data[0]
                magnitude = y_data[0]

                # Dibujar caja de información
                ypos = ypos_start - i * ypos_step
                info_text = (
                    f"Marker {marker_id}\n"
                    f"Freq: {x_data[0]:.2f}\n"
                    f"\phi: {magnitude:.3f}{"°"}"
                )
                ax.text(   
                        0.05, ypos, info_text,
                    transform=ax.transAxes,
                    fontsize=8,
                    verticalalignment='top',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='black')
                )

            # Dibujar marker sobre la gráfica original
            ax.plot(x_data, y_data, marker='o', color='red', markersize=6)


        # --- Exportar imagen a pixmap ---
        buf = io.BytesIO()
        fig_copy.savefig(buf, format='png', dpi=100, edgecolor='none')
        buf.seek(0)

        pixmap = QPixmap()
        if pixmap.loadFromData(buf.getvalue()):
            return pixmap
        return None


    def _prepare_figure_for_export(self, dpi=300, size_inches=(10, 8), remove_sliders=True):
        """
        Prepare a copy of the figure for export with proper styling and formatting.
        
        Args:
            dpi (int): DPI for the output figure
            size_inches (tuple): Size of the figure in inches (width, height)
            remove_sliders (bool): Whether to remove slider axes
            
        Returns:
            matplotlib.figure.Figure: Prepared figure copy ready for export
        """
        import copy
        
        # Create a deep copy to preserve all styles and colors
        fig_copy = copy.deepcopy(self.figure)
        
        # Set DPI and size
        fig_copy.set_dpi(dpi)
        fig_copy.set_size_inches(*size_inches)

        if hasattr(self.parent_window, 'cursor_left') and self.parent_window.cursor_left:
            x, y_complex = self.parent_window.cursor_left.get_data()  # y puede ser complejo
            magnitude = np.abs(y_complex[0])
            phase_deg = np.angle(y_complex[0], deg=True)
            
            # Dibujar el marcador
            ax.plot(x, magnitude, marker='o', color='red', markersize=8, label='M1')

            # Cuadro de info
            info_text = f"Freq: {x[0]:.2f}\n|S11|: {magnitude:.3f}\nPhase: {phase_deg:.2f}°"
            ax.text(0.05, 0.95, info_text, transform=ax.transAxes,
                    fontsize=8, verticalalignment='top',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'))
                
        # Handle slider removal and axis adjustments
        if remove_sliders:
            # Collect slider axes to remove
            axes_to_remove = []
            for ax in fig_copy.axes:
                if hasattr(ax, 'get_position'):
                    pos = ax.get_position()
                    if pos.height < 0.1 or pos.width < 0.1:  # Likely a slider
                        axes_to_remove.append(ax)
            
            # Remove slider axes
            for ax in axes_to_remove:
                fig_copy.delaxes(ax)
        
        # Adjust remaining axes
        for ax in fig_copy.axes:
            # Ensure Smith charts maintain aspect ratio
            if "Smith" in ax.get_title() or len(ax.patches) > 10:
                ax.set_aspect('equal')
            
            # Adjust position slightly (optional refinement)
            pos = ax.get_position()
            new_pos = [pos.x0, pos.y0 + 0.02, pos.width - 0.02, pos.height - 0.02]
            ax.set_position(new_pos)
            
            # For save_as_image compatibility: remove small axes if not already done
            if not remove_sliders and (pos.height < 0.1 or pos.width < 0.1):
                fig_copy.delaxes(ax)
        
        return fig_copy

    def copy_to_clipboard(self):
        """Copy the graph image to clipboard preserving all colors and styles."""
        try:
            # Use helper method to prepare figure with high DPI for clipboard
            fig_copy = self._prepare_figure_for_export(dpi=300, size_inches=(10, 8), remove_sliders=True)
            
            # Generate HIGH RESOLUTION capture preserving all original styling
            buf_clipboard = io.BytesIO()
            fig_copy.savefig(buf_clipboard, 
                           format='png', 
                           dpi=300,  # Force high DPI
                           bbox_inches='tight', 
                           edgecolor='none')
            buf_clipboard.seek(0)
            
            # Clean up the temporary figure
            plt.close(fig_copy)
            
            # Create QPixmap from the high-resolution data
            pixmap = QPixmap()
            if pixmap.loadFromData(buf_clipboard.getvalue()):
                # Verify we have a high-resolution image
                image_size = pixmap.size()
                print(f"High-res capture: {image_size.width()}x{image_size.height()}")
                
                # Copy to clipboard
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(pixmap)
                
                QMessageBox.information(self, "Copy", 
                    f"Graph copied to clipboard!")
            else:
                QMessageBox.warning(self, "Copy Error", "Failed to create image.")
            
        except Exception as e:
            import traceback
            print(f"Clipboard error: {e}")
            print(traceback.format_exc())
            QMessageBox.critical(self, "Copy Error", f"Failed to copy image to clipboard: {str(e)}")

    def save_as_image(self):
        """Save the graph as an image file."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Graph as Image", 
                "graph.png", 
                "PNG Files (*.png);;JPG Files (*.jpg);;PDF Files (*.pdf);;SVG Files (*.svg)"
            )
            
            if file_path:
                # Use helper method to prepare figure for saving
                fig_copy = self._prepare_figure_for_export(dpi=300, size_inches=(10, 8), remove_sliders=False)
                
                # Save the prepared figure
                fig_copy.savefig(file_path, dpi=300, edgecolor='none')
                plt.close(fig_copy)
                
                QMessageBox.information(self, "Save", f"Graph saved as: {file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save image: {str(e)}")

    def save_as_csv(self):
        """Save the graph data as CSV."""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Graph Data as CSV", 
                "graph_data.csv", 
                "CSV Files (*.csv)"
            )

            if not file_path:
                return  # Usuario canceló

            for i, ax in enumerate(self.figure.axes):
                print(f"\n=== Axis {i} ===")
                print(f"Title: {ax.get_title()}")
                print(f"Number of lines: {len(ax.lines)}")
                
                for j, line in enumerate(ax.lines):
                    print(f"  Line {j}: visible={line.get_visible()}")
                    print(f"    X data sample: {line.get_xdata()[:5]}")
                    print(f"    Y data sample: {line.get_ydata()[:5]}")
                    print(f"    Has attribute 'freqs'? {'freqs' in dir(line)}")
            csv_data = []
            headers = []

            for ax in self.figure.axes:
                # Ignorar ejes de sliders o muy pequeños
                if hasattr(ax, 'get_position'):
                    pos = ax.get_position()
                    if pos.height < 0.1 or pos.width < 0.1:
                        continue

                if self.left_graph == "Smith Diagram" or self.right_grap == "Smith Diagram":
                    if self.freqs is None:
                        QMessageBox.warning(self, "Save Error", "Frequency data is missing for Smith Diagram!")
                        return

                    headers = ['Frequency (Hz)', 'Re', 'Im']
                    csv_data = []

                    # Recorremos todas las líneas visibles y tomamos X=Re, Y=Im
                    for ax in self.figure.axes:
                        for line in ax.lines:
                            if line.get_visible():
                                x_data_re = line.get_xdata()   # parte real
                                y_data_im = line.get_ydata()   # parte imaginaria

                                # Zip con self.freqs
                                for f, re, im in zip(self.freqs, x_data_re, y_data_im):
                                    csv_data.append([f, re, im])
                else:
                    for i, line in enumerate(ax.lines):
                        if line.get_visible() and len(line.get_xdata()) > 1:
                            x_data = line.get_xdata()
                            y_data = line.get_ydata()
                            # Convert MHz a Hz
                            x_data_hz = [x * 1e6 for x in x_data]

                            if not headers:
                                headers = ['Freq (Hz)', 'Y']
                                csv_data = [[x, y] for x, y in zip(x_data_hz, y_data)]
                            else:
                                headers.extend([f'Freq_{i+1} (Hz)', f'Y_{i+1}'])
                                for j, (x, y) in enumerate(zip(x_data_hz, y_data)):
                                    if j < len(csv_data):
                                        csv_data[j].extend([x, y])

            # Depuración: imprimir el contenido
            print("CSV Headers:", headers)
            print("CSV Data Sample:", csv_data[:5])  # primeros 5 registros

            # Guardar CSV
            import csv
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                writer.writerows(csv_data)

            QMessageBox.information(self, "Save", f"Graph data saved as: {file_path}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save CSV: {str(e)}")
            print("Exception:", e)

