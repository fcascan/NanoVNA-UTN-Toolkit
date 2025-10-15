import os
import logging
import skrf as rf
import numpy as np

class KitsCalibrator:
    """
    Class to handle VNA calibration using OSM 3-term method.
    """
    def __init__(self, calibration_dir):
        """
        Initialize the calibrator with the folder where the S1P error files are saved.

        Parameters
        ----------
        calibration_dir : str
            Path to the folder containing S1P error files.
        """
        self.calibration_dir = calibration_dir
        logging.info(f"[Calibrator] Initialized with calibration directory: {calibration_dir}")

    def osm_calibrate_s11(self, s11_med, selected_kit):
        """
        Calibrate measured S11 using OSM error terms.

        Parameters
        ----------
        s11_med : np.array
            Measured S11 from the VNA.

        Returns
        -------
        s11_cal : np.array
            Calibrated S11 array.
        """
        logging.info("[Calibrator] Loading error terms from S1P files...")

        # Construct full paths to error S1P files with literal names
        error_dir = os.path.join(self.calibration_dir, selected_kit)
        directivity_file = os.path.join(error_dir, "directivity.s1p")
        reflection_tracking_file = os.path.join(error_dir, "reflection_tracking.s1p")
        source_match_file = os.path.join(error_dir, "source_match.s1p")

        # Read S1P files using skrf
        directivity = rf.Network(directivity_file).s[:,0,0]
        reflection_tracking = rf.Network(reflection_tracking_file).s[:,0,0]
        source_match = rf.Network(source_match_file).s[:,0,0]

        # Compute delta_e (for 2-term calibration, source match is ignored)
        delta_e = reflection_tracking * directivity - source_match

        logging.info("[Calibrator] Calculating calibrated S11 using OSM formula...")
        s11_cal = (s11_med - directivity) / (s11_med * reflection_tracking - delta_e)
        return s11_cal

    def normalization_calibrate_s21(self, s21_med, selected_kit):
        """
        Calibrate measured S21 using normalization (THRU) error term.

        Parameters
        ----------
        s21_med : np.array
            Measured S21 from the VNA.

        Returns
        -------
        s21_cal : np.array
            Calibrated S21 array.
        """
        logging.info("[Calibrator] Loading transmission tracking error from S2P file...")

        # Path to normalization error file
        error_dir = os.path.join(self.calibration_dir, selected_kit)
        transmission_tracking_file = os.path.join(error_dir, "transmission_tracking.s2p")

        # Read S2P file using skrf and extract S21
        transmission_tracking = rf.Network(transmission_tracking_file).s[:,1,0]

        # Calibrate S21 by dividing by the error term
        s21_cal = s21_med / transmission_tracking

        logging.info("[Calibrator] Calculated calibrated S21 using normalization.")
        return s21_cal

    def one_port_n_calibrate(self, s11_med, s21_med, selected_kit):
        """
        Calibrate S11 and S21 using the 1-Port+N method.
        S11 is calibrated using OSM error terms from osm_dir.
        S21 is calibrated using normalization (THRU) error term from thru_dir.

        Parameters
        ----------
        s11_med : np.array
            Measured S11 from the VNA.
        s21_med : np.array
            Measured S21 from the VNA.
        osm_dir : str
            Path to OSM error folder.
        thru_dir : str
            Path to THRU error folder.

        Returns
        -------
        s11_cal : np.array
            Calibrated S11 array.
        s21_cal : np.array
            Calibrated S21 array.
        """
        logging.info("[Calibrator] Calibrating S11 and S21 using 1-Port+N method...")

        # Calibrate S11 using OSM errors from osm_dir
        error_dir_osm = os.path.join(self.calibration_dir, selected_kit)
        directivity_file = os.path.join(error_dir_osm, "directivity.s1p")
        reflection_tracking_file = os.path.join(error_dir_osm, "reflection_tracking.s1p")
        source_match_file = os.path.join(error_dir_osm, "source_match.s1p")

        directivity = rf.Network(directivity_file).s[:,0,0]
        reflection_tracking = rf.Network(reflection_tracking_file).s[:,0,0]
        source_match = rf.Network(source_match_file).s[:,0,0]
        delta_e = reflection_tracking * directivity - source_match
        
        s11_cal = (s11_med - directivity) / (s11_med * reflection_tracking - delta_e)

        # Calibrate S21 using normalization error from thru_dir
        error_dir_norm = os.path.join(self.calibration_dir, selected_kit)
        transmission_tracking_file = os.path.join(error_dir_norm, "transmission_tracking.s2p")
        transmission_tracking = rf.Network(transmission_tracking_file).s[:,1,0]

        s21_cal = s21_med / transmission_tracking

        return s11_cal, s21_cal

    def enhanced_response_calibrate(self, s11_med, s21_med, selected_kit):
        """
        Calibrate S11 and S21 using the 1-Port+N method.
        S11 is calibrated using OSM error terms from osm_dir.
        S21 is calibrated using normalization (THRU) error term from thru_dir.

        Parameters
        ----------
        s11_med : np.array
            Measured S11 from the VNA.
        s21_med : np.array
            Measured S21 from the VNA.
        osm_dir : str
            Path to OSM error folder.
        thru_dir : str
            Path to THRU error folder.

        Returns
        -------
        s11_cal : np.array
            Calibrated S11 array.
        s21_cal : np.array
            Calibrated S21 array.
        """
        logging.info("[Calibrator] Calibrating S11 and S21 using 1-Port+N method...")

        # Calibrate S11 using OSM errors from osm_dir
        error_dir_osm = os.path.join(self.calibration_dir, selected_kit)
        directivity_file = os.path.join(error_dir_osm, "directivity.s1p")
        reflection_tracking_file = os.path.join(error_dir_osm, "reflection_tracking.s1p")
        source_match_file = os.path.join(error_dir_osm, "source_match.s1p")

        directivity = rf.Network(directivity_file).s[:,0,0]
        reflection_tracking = rf.Network(reflection_tracking_file).s[:,0,0]
        source_match = rf.Network(source_match_file).s[:,0,0]
        delta_e = reflection_tracking * directivity - source_match
        
        s11_cal = (s11_med - directivity) / (s11_med * reflection_tracking - delta_e)

        # Calibrate S21 using normalization error from thru_dir
        error_dir_norm = os.path.join(self.calibration_dir, selected_kit)
        transmission_tracking_file = os.path.join(error_dir_norm, "transmission_tracking.s2p")
        transmission_tracking = rf.Network(transmission_tracking_file).s[:,1,0]

        s21_cal = (s21_med / transmission_tracking) * (reflection_tracking/(source_match*s11_med - delta_e))

        return s11_cal, s21_cal

    def kits_selected(self, selected_method, selected_kit, s11_med, s21_med):
        """
        Determine the calibration method based on user selection.

        Parameters
        ----------
        selected_method : str
            The selected calibration method.

        Returns
        -------
        method : str    
            The determined calibration method.
        """
        
        if selected_method == "OSM (Open - Short - Match)":
            s11 = self.osm_calibrate_s11(s11_med, selected_kit)
            s21 = s21_med
        elif selected_method == "Normalization":
            s11 = s11_med
            s21 = self.normalization_calibrate_s21(s21_med, selected_kit)
        elif selected_method == "1-Port+N":
            s11, s21 = self.one_port_n_calibrate(s11_med, s21_med, selected_kit)
        elif selected_method == "Enhanced-Response":
            s11, s21 = self.enhanced_response_calibrate(s11_med, s21_med, selected_kit)

        return s11, s21

