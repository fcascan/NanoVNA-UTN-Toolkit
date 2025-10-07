"""
Device detection worker for threaded operations.
"""
import time
from PySide6.QtCore import QObject, Signal

from ..Hardware.Hardware import get_interfaces, get_VNA
from ..utils.device_parser import parse_device_info, extract_extended_device_info


class DeviceWorker(QObject):
    """Worker class for device detection operations in a separate thread."""
    
    # Signals to communicate with the main thread
    status_update = Signal(str)
    progress_update = Signal(int)
    device_found = Signal(object, dict)  # device, parsed_info
    device_error = Signal(str)
    finished = Signal()
    
    def __init__(self):
        super().__init__()
        self.should_stop = False
    
    def stop(self):
        """Signal the worker to stop."""
        self.should_stop = True
    
    def detect_devices(self):
        """Detect VNA devices in a separate thread."""
        try:
            if self.should_stop:
                return
                
            self.status_update.emit("Starting device search...")
            self.progress_update.emit(10)
            
            if self.should_stop:
                return
                
            # Step 1: Get interfaces
            self.status_update.emit("Searching for available serial interfaces...")
            self.progress_update.emit(20)
            time.sleep(0.1)  # Small delay to show progress
            
            interfaces = get_interfaces()
            
            if self.should_stop:
                return
                
            if not interfaces:
                self.progress_update.emit(100)
                self.status_update.emit("No serial interfaces detected")
                self.device_error.emit("No NanoVNA device detected.")
                self.finished.emit()
                return
            
            self.progress_update.emit(40)
            self.status_update.emit(f"Found {len(interfaces)} interface(s). Checking devices...")
            
            # Step 2: Try to connect to each interface
            for i, iface in enumerate(interfaces):
                if self.should_stop:
                    return
                    
                progress = 40 + (i + 1) * (50 / len(interfaces))
                self.progress_update.emit(int(progress))
                self.status_update.emit(f"Testing connection on {iface.port}...")
                time.sleep(0.1)
                
                try:
                    # Try to get VNA from interface
                    vna = get_VNA(iface)
                    
                    if self.should_stop:
                        return
                        
                    if vna:
                        self.progress_update.emit(80)
                        self.status_update.emit("Reading firmware information...")
                        time.sleep(0.05)  # Reduced delay
                        
                        # Get device info
                        try:
                            info_text = vna.readFirmware()
                            self.progress_update.emit(90)
                            parsed_info = parse_device_info(info_text)
                            
                            self.status_update.emit("Reading device capabilities...")
                            # Get extended device information in quick mode to avoid delays
                            extended_info = extract_extended_device_info(vna, quick_mode=True)
                            
                            self.progress_update.emit(95)
                            # Merge extended info into parsed_info
                            if extended_info['serial_number'] != 'Not available':
                                parsed_info['serial_number'] = extended_info['serial_number']
                            if extended_info['features']:
                                parsed_info['features'] = extended_info['features']
                            if extended_info['board_revision'] != 'Unknown':
                                parsed_info['board_revision'] = extended_info['board_revision']
                            if extended_info['device_type'] != 'Unknown':
                                parsed_info['device_type'] = extended_info['device_type']
                            if extended_info['bandwidth'] != 'Unknown':
                                parsed_info['bandwidth'] = extended_info['bandwidth']
                            
                            self.progress_update.emit(100)
                            self.status_update.emit("Device connected successfully")
                            self.device_found.emit(vna, parsed_info)
                            self.finished.emit()
                            return
                        except Exception as e:
                            self.status_update.emit(f"Error reading firmware: {str(e)}")
                            continue
                            
                except Exception as e:
                    self.status_update.emit(f"Error on {iface.port}: {str(e)}")
                    continue
            
            # If we get here, no device was successfully connected
            self.progress_update.emit(100)
            self.status_update.emit("Could not connect to any device")
            self.device_error.emit("Could not establish connection with any detected device.")
            
        except Exception as e:
            self.progress_update.emit(100)
            self.status_update.emit(f"Critical error: {str(e)}")
            self.device_error.emit(f"Critical error during detection: {str(e)}")
        finally:
            self.finished.emit()
