"""
Compatibility layer for NanoVNA-UTN-Toolkit.
This module provides compatibility wrappers and patches for the NanoVNASaver library
without modifying the original files.
"""
import sys
import importlib
import logging
from typing import Any, Optional, Type, TypeVar, Union

# Import the original modules
from ..Hardware.Hardware import get_VNA as original_get_VNA
from ..Hardware import VNA as OriginalVNA

# Import our unified version compatibility
from ..utils import version_compat as vc
from ..utils.version import Version as UTNVersion

# Type variable for VNA subclasses
V = TypeVar('V', bound=OriginalVNA.VNA)

logger = logging.getLogger(__name__)

# Store original functions and classes for reference
_original_VNA = OriginalVNA.VNA
_original_get_VNA = original_get_VNA

# Patch the VNA class to ensure proper connection handling
class PatchedVNA(_original_VNA):
    def __init__(self, iface):
        # Initialize the parent class first
        super().__init__(iface)
        
        # Initialize our custom attributes
        self._patched_connected = False
        self._original_version = None
        self._vna = None  # Reference to real device
        
        # Ensure the serial connection is properly initialized
        if hasattr(self, 'serial') and self.serial is not None:
            self.serial.timeout = 0.5  # Set a reasonable timeout
        
        logger.debug(f"Initialized PatchedVNA with interface: {iface}")
    
    @property
    def datapoints(self):
        """Delegate datapoints access to the real device if available."""
        if hasattr(self, '_vna') and self._vna is not None:
            return self._vna.datapoints
        # Fallback to parent class behavior
        return getattr(self, '_datapoints', 101)
    
    @datapoints.setter
    def datapoints(self, value):
        """Delegate datapoints setting to the real device if available."""
        if hasattr(self, '_vna') and self._vna is not None:
            self._vna.datapoints = value
        else:
            # Fallback to setting on ourselves
            self._datapoints = value
    
    def connect(self) -> bool:
        """Ensure the VNA is properly connected."""
        logger.debug("PatchedVNA.connect() called")
        try:
            if not hasattr(self, 'serial') or self.serial is None:
                logger.error("No serial interface available")
                return False
                
            if not self.serial.is_open:
                logger.debug("Opening serial connection")
                self.serial.open()
            
            self._patched_connected = True
            logger.debug("Connection marked as established")
            return True
        except Exception as e:
            logger.error(f"Error in PatchedVNA.connect(): {e}")
            self._patched_connected = False
            return False
    
    def connected(self) -> bool:
        """Check if the VNA is connected."""
        # Ensure the attribute exists
        if not hasattr(self, '_patched_connected'):
            self._patched_connected = False
            
        try:
            # Check both our flag and the parent's connected status
            parent_connected = super().connected() if hasattr(super(), 'connected') else False
            return self._patched_connected and parent_connected
        except Exception as e:
            logger.error(f"Error in PatchedVNA.connected(): {e}")
            return False
    
    def read_fw_version(self) -> UTNVersion:
        """Read firmware version with compatibility layer."""
        if not hasattr(self, '_original_version') or self._original_version is None:
            try:
                # Get the original version using the parent class method
                orig_version = super().read_fw_version()
                # Convert to our version format
                self._original_version = vc.convert_to_utn_version(orig_version)
                logger.debug(f"Read firmware version: {self._original_version}")
            except Exception as e:
                logger.error(f"Error reading firmware version: {e}")
                # Return a default version on error
                self._original_version = UTNVersion.parse("0.0.0")
        
        return self._original_version
    
    def setSweep(self, start_freq, stop_freq):
        """Override setSweep to ensure proper configuration."""
        logger.debug(f"PatchedVNA.setSweep: {start_freq} - {stop_freq} Hz")
        try:
            # Call parent setSweep
            result = super().setSweep(start_freq, stop_freq)
            
            # Also set on the real device if available
            if hasattr(self, '_vna') and self._vna is not None:
                self._vna.setSweep(start_freq, stop_freq)
                logger.debug(f"PatchedVNA: Also set sweep on real device")
            
            return result
        except Exception as e:
            logger.error(f"Error in PatchedVNA.setSweep: {e}")
            raise

# Patch the get_VNA function
def patched_get_VNA(iface) -> OriginalVNA.VNA:
    """Get a VNA instance with proper connection handling."""
    # Ensure the port is open before creating the VNA instance
    if not iface.is_open:
        iface.open()
    
    # Create the VNA instance using the original function
    vna = _original_get_VNA(iface)
    
    # Ensure the VNA is properly connected
    if not vna.connected():
        if hasattr(vna, 'connect') and callable(vna.connect):
            vna.connect()
    
    # Wrap the VNA instance in our patched class if not already wrapped
    if not isinstance(vna, PatchedVNA):
        # Create a new instance of our patched class with the same attributes
        patched_vna = PatchedVNA(iface)
        # Store reference to the real VNA device for forcing mechanism
        patched_vna._vna = vna
        # Copy all attributes from the original VNA to our patched version
        # EXCEPT datapoints - we need to preserve forcing mechanism
        for attr in dir(vna):
            if not attr.startswith('__') and attr != 'datapoints':
                try:
                    setattr(patched_vna, attr, getattr(vna, attr))
                except AttributeError:
                    pass
        
        # Instead of copying datapoints, make it delegate to the real device
        # This ensures that our forcing mechanism works correctly
        logger.debug(f"PatchedVNA wrapping real device with datapoints delegation")
        
        vna = patched_vna
    
    return vna

# Apply patches
def apply_patches() -> None:
    """Apply all compatibility patches."""
    # Patch the VNA class
    OriginalVNA.VNA = PatchedVNA
    
    # Patch the get_VNA function
    import NanoVNA_UTN_Toolkit.Hardware.Hardware as hardware_module
    
    # Store the original function if not already stored
    if not hasattr(hardware_module, '_original_get_VNA'):
        hardware_module._original_get_VNA = original_get_VNA
    
    # Apply our patched version
    hardware_module.get_VNA = patched_get_VNA
    
    logger.info("Compatibility patches applied successfully")

# Apply patches when this module is imported
apply_patches()
