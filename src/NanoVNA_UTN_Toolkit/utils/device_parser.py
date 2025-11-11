"""
Device information parser utilities.
"""
import re


def parse_device_info(info_text):
    """Parse device information from firmware string."""
    info = {
        'board': 'Unknown',
        'version': 'Unknown',
        'build_time': 'Unknown',
        'copyright': '',
        'architecture': 'Unknown',
        'platform': 'Unknown',
        'parameters': {},
        'full_text': info_text or ''
    }
    
    if not info_text:
        return info
    
    lines = info_text.split('\n')
    hardware_version = None
    firmware_version = None
    
    # Parse lines looking for standard format first (preserves original logic)
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Parse standard fields (ORIGINAL LOGIC - DO NOT MODIFY)
        if line.startswith('Board:'):
            info['board'] = line.replace('Board:', '').strip()
        elif line.startswith('Version:'):
            version_line = line.replace('Version:', '').strip()
            # Extract just the version number/info
            info['version'] = version_line
            
            # Parse parameters from version line if present
            if '[' in version_line and ']' in version_line:
                param_part = version_line[version_line.find('[') + 1:version_line.find(']')]
                params = {}
                for param in param_part.split(', '):
                    if ':' in param:
                        key, value = param.split(':', 1)
                        params[key.strip()] = value.strip()
                    else:
                        # Handle parameters like "p:101" 
                        if param.strip():
                            params[param.strip()] = ''
                info['parameters'] = params
                
        elif line.startswith('Build Time:'):
            info['build_time'] = line.replace('Build Time:', '').strip()
        elif line.startswith('Architecture:'):
            info['architecture'] = line.replace('Architecture:', '').strip()
        elif line.startswith('Platform:'):
            info['platform'] = line.replace('Platform:', '').strip()
        elif 'Copyright' in line:
            info['copyright'] = line
            
        # Handle NanoVNA-V2/SAA-2N format (HW:/FW: format) - just parse, don't override
        elif line.startswith('HW:'):
            hardware_version = line.replace('HW:', '').strip()
        elif line.startswith('FW:'):
            firmware_version = line.replace('FW:', '').strip()
    
    # If we have HW/FW format and no other format was detected, populate the basic info
    # but let the extended device info provide the proper device type identification
    if hardware_version and firmware_version and info['board'] == 'Unknown' and info['version'] == 'Unknown':
        info['board'] = f"Hardware: {hardware_version}"
        info['version'] = f"Firmware: {firmware_version}"
        info['platform'] = "NanoVNA Compatible"
    
    return info


def extract_extended_device_info(vna_device, quick_mode=True):
    """Extract additional device information from VNA device object.
    
    Args:
        vna_device: The VNA device object
        quick_mode: If True, only extract fast/cached information to avoid delays
    """
    extended_info = {
        'serial_number': 'Not available',
        'features': [],
        'board_revision': 'Unknown',
        'device_type': 'Unknown',
        'bandwidth': 'Unknown'
    }
    
    if not vna_device:
        return extended_info
    
    try:
        # Get device type (always fast)
        extended_info['device_type'] = type(vna_device).__name__
        
        # Try to get features (usually fast, from cached info)
        if hasattr(vna_device, 'features') and vna_device.features:
            extended_info['features'] = list(vna_device.features)
        elif hasattr(vna_device, 'get_features') and not quick_mode:
            try:
                features = vna_device.get_features()
                if features:
                    extended_info['features'] = list(features)
            except Exception:
                pass
        
        # Try to get board revision (check cached first)
        if hasattr(vna_device, 'board_revision') and vna_device.board_revision:
            extended_info['board_revision'] = str(vna_device.board_revision)
        elif hasattr(vna_device, 'read_board_revision') and not quick_mode:
            try:
                # Only try if not in quick mode, as this can be slow
                rev = vna_device.read_board_revision()
                if rev:
                    extended_info['board_revision'] = str(rev)
            except Exception:
                pass
        
        # Try to get serial number (check cached first)
        if hasattr(vna_device, 'SN') and vna_device.SN and vna_device.SN != "NOT SUPPORTED":
            extended_info['serial_number'] = vna_device.SN
        elif hasattr(vna_device, 'getSerialNumber') and not quick_mode:
            try:
                # Only try if not in quick mode, as this can be very slow
                # Use a simple approach without complex timeout on Windows
                sn = vna_device.getSerialNumber()
                if sn and sn.strip() and sn.strip() != "NOT SUPPORTED":
                    extended_info['serial_number'] = sn.strip()
            except Exception:
                pass  # Serial number not available
        
        # Try to get bandwidth info (usually fast)
        if hasattr(vna_device, 'bandwidth'):
            extended_info['bandwidth'] = str(vna_device.bandwidth)
        elif 'Bandwidth' in extended_info['features']:
            extended_info['bandwidth'] = 'Configurable'
            
    except Exception as e:
        # Don't let extended info extraction break the main functionality
        import logging
        logging.getLogger(__name__).debug(f"Error extracting extended device info: {e}")
    
    return extended_info
