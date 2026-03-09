import streamlit as st
import numpy as np
import math
import os
import datetime
from fpdf import FPDF

# ============================================================
# DATA TABLES (from "DATA", "FL KG", "BOTAS" sheets)
# ============================================================

# --- Pipe/Plate Materials: { name: (SMYS_metric_MPa, SMYS_us_psi) } ---
PIPE_MATERIALS = {
    "N/A": (0, 0),
    "ASTM A 240 TYPE 304": (205, 30000),
    "ASTM A 240 TYPE 304 L": (170, 25000),
    "API 5L GrB": (245, 35500),
    "API 5L X42": (290, 42100),
    "API 5L X46": (320, 46400),
    "API 5L X52": (360, 52200),
    "API 5L X56": (390, 56600),
    "API 5L X60/L415NE": (415, 60200),
    "API 5L X65": (450, 65300),
    "API 5L X70": (485, 70300),
    "ASTM A105": (245, 36000),
    "ASTM A106 GrB": (240, 35000),
    "ASTM A234 WPB": (round(35000/148.5, 2), 35000),
    "ASTM A333 Gr6": (round(35000/148.5, 2), 35000),
    "ASTM A516 Gr60": (220, 32000),
    "ASTM A516 Gr70": (260, 38000),
    "ASTM A671 CC60": (220, 32000),
    "ASTM A860 WPHY42": (290, 42000),
    "ASTM A860 WPHY46": (315, 46000),
    "ASTM A860 WPHY52": (360, 52000),
    "ASTM A860 WPHY60": (415, 60000),
    "ASTM A860 WPHY65": (450, 65000),
    "ASTM A860 WPHY70": (485, 70000),
    "EN 10028-2 P265GH (t <= 16mm)": (265, 35500),
    "EN 10028-2 P265GH (16 < t <= 40mm)": (255, 33200),
    "EN 10028-2 P265GH (40 < t <= 60mm)": (245, 31900),
    "EN 10028-2 P265GH (60 < t <=100 mm)": (215, 28000),
    "EN 10028-2 P295GH (t <= 16mm)": (295, 38400),
    "EN 10028-2 P295GH (16 < t <= 40mm)": (290, 37500),
    "EN 10028-2 P295GH (40 < t <= 60mm)": (285, 37100),
    "EN 10028-2 P295GH (60 < t <=100 mm)": (260, 33800),
    "EN 10028-2 P355GH (t <= 16mm)": (355, 46200),
    "EN 10028-2 P355GH (16 < t <= 40mm)": (345, 45500),
    "EN 10028-2 P355GH (40 < t <= 60mm)": (335, 45500),
    "EN 10028-2 P355GH (60 < t <=100 mm)": (315, 41000),
    "EN 10028-3 P355NH (t <= 16mm)": (355, 51500),
    "EN 10028-3 P355NH (16 < t <= 40mm)": (345, 50000),
    "EN 10028-3 P355NH (40 < t <= 60mm)": (335, 48500),
    "EN 10028-3 P355NH (60 < t <=100 mm)": (315, 45500),
    "EN 10028-3 P355NL1 (t <= 16mm)": (355, 51500),
    "EN 10028-3 P355NL1 (16 < t <= 40mm)": (345, 50000),
    "EN 10028-3 P355NL1 (40 < t <= 60mm)": (335, 48500),
    "EN 10028-3 P355NL1 (60 < t <=100 mm)": (315, 45500),
    "EN 10028-3 P355NL2 (t <= 16mm)": (355, 51500),
    "EN 10028-3 P355NL2 (16 < t <= 40mm)": (345, 50000),
    "EN 10028-3 P355NL2 (40 < t <= 60mm)": (335, 48500),
    "EN 10028-3 P355NL2 (60 < t <=100 mm)": (315, 45500),
    "EN 10028-3 P460NL1 (t <= 16mm)": (460, 66500),
    "EN 10028-3 P460NL1 (16 < t <= 40mm)": (445, 64500),
    "EN 10028-3 P460NL1 (40 < t <= 60mm)": (430, 62500),
    "EN 10028-3 P460NL1 (60 < t <=100 mm)": (400, 58000),
    "EN 10028-3 P460NL2 (t <= 16mm)": (460, 66500),
    "EN 10028-3 P460NL2 (16 < t <= 40mm)": (445, 64500),
    "EN 10028-3 P460NL2 (40 < t <= 60mm)": (430, 62500),
    "EN 10028-3 P460NL2 (60 < t <=100 mm)": (400, 58000),
    "EN 10216-2 P265GH (t <= 16mm)": (265, 35500),
    "EN 10216-2 P265GH (16 < t <= 40mm)": (255, 33200),
    "EN 10216-2 P265GH (40 < t <= 60mm)": (245, 31900),
    "EN 10216-3 P355NH (t <= 20mm)": (355, 51500),
    "EN 10216-3 P355NH (20 < t <= 40mm)": (345, 50000),
    "EN 10216-3 P355NH (40 < t <= 50mm)": (335, 48500),
    "EN 10216-3 P355NH (50 < t <= 65 mm)": (325, 47000),
    "EN 10216-3 P355NL1 (t <= 20mm)": (355, 51500),
    "EN 10216-3 P355NL1 (20 < t <= 40mm)": (345, 50000),
    "EN 10216-3 P355NL1 (40 < t <= 50mm)": (335, 48500),
    "EN 10216-3 P355NL1 (50 < t <= 65 mm)": (325, 47000),
    "EN 10216-3 P355NL2 (t <= 20mm)": (355, 51500),
    "EN 10216-3 P355NL2 (20 < t <= 40mm)": (345, 50000),
    "EN 10216-3 P355NL2 (40 < t <= 50mm)": (335, 48500),
    "EN 10216-3 P355NL2 (50 < t <= 65 mm)": (325, 47000),
    "EN 10216-3 P460NH (t <= 12mm)": (460, 66500),
    "EN 10216-3 P460NH (12 < t <= 20mm)": (450, 65500),
    "EN 10216-3 P460NH (20 < t <= 40mm)": (440, 64000),
    "EN 10216-3 P460NH (40 < t <= 50mm)": (425, 61500),
    "EN 10216-3 P460NH (50 < t <= 65 mm)": (410, 59500),
    "EN 10216-3 P460NL1 (t <= 20mm)": (460, 66500),
    "EN 10216-3 P460NL1 (12 < t <= 20mm)": (450, 65500),
    "EN 10216-3 P460NL1 (20 < t <= 40mm)": (440, 64000),
    "EN 10216-3 P460NL1 (40 < t <= 50mm)": (425, 61500),
    "EN 10216-3 P460NL1 (50 < t <= 65 mm)": (410, 59500),
    "EN 10216-3 P460NL2 (t <= 20mm)": (460, 66500),
    "EN 10216-3 P460NL2 (12 < t <= 20mm)": (450, 65500),
    "EN 10216-3 P460NL2 (20 < t <= 40mm)": (440, 64000),
    "EN 10216-3 P460NL2 (40 < t <= 50mm)": (425, 61500),
    "EN 10216-3 P460NL2 (50 < t <= 65 mm)": (410, 59500),
    "EN 10025-2 S355JR (<16 mm)": (355, 51500),
    "EN 10025-2 S355JR (16 < t < 40 mm)": (345, 50000),
    "EN 10025-2 S355JR (40 < t < 63 mm)": (335, 48500),
    "EN 10025-2 S355JR (63 < t < 80 mm)": (325, 47000),
    "ASTM A53 Gr A ": (205, 29500),
    "ASTM A53 Gr B ": (240, 35000),
    "EN 10025-2 L450QB": (450, 65500),
}

# --- Flange Materials: { name: (SMYS_metric, SMYS_us) } ---
FLANGE_MATERIALS = {
    "ASTM A105": (245, 36000),
    "ASTM A182": (0, 40000),
    "ASTM A350LF2 CL1": (260, 37700),
    "ASTM A694F42": (290, 42000),
    "ASTM A694F46": (315, 46000),
    "ASTM A694F52": (360, 52000),
    "ASTM A694F56": (385, 56000),
    "ASTM A694F60": (415, 60000),
    "ASTM A694F65": (450, 65000),
    "ASTM A182 F304": (205, 30000),
    "ASTM A182 F304 L": (170, 25000),
}

# --- Pipe OD Lookup: { inch: mm } ---
PIPE_OD_LOOKUP = {
    3: 88.9, 4: 114.3, 6: 168.3, 8: 219.1, 10: 273.1, 12: 323.9,
    14: 355.6, 16: 406.4, 18: 457.0, 20: 508.0, 22: 558.8, 24: 609.6,
    28: 711.2, 30: 762.0, 32: 812.8, 36: 914.1, 40: 1016.0, 42: 1067.0,
    48: 1219.0, 50: 1270.0, 52: 1320.8, 54: 1371.6, 56: 1422.4,
    58: 1473.2, 60: 1524.0, 62: 1574.8, 64: 1625.6, 66: 1676.4,
    68: 1727.2, 70: 1778.0, 72: 1828.8, 74: 1879.6, 76: 1930.4,
    78: 1981.2, 80: 2032.0,
}

# --- Nozzle nominal diameters => Hot Tap ID and Linestop ID ---
NOZZLE_DATA = {
    3: {"hot_tap_id": 63, "linestop_id": 78},
    4: {"hot_tap_id": 87.3, "linestop_id": 102},
    6: {"hot_tap_id": 138.9126, "linestop_id": 154},
    8: {"hot_tap_id": 185.7248, "linestop_id": 202},
    10: {"hot_tap_id": 241.3, "linestop_id": 254},
    12: {"hot_tap_id": 292.1, "linestop_id": 304},
    14: {"hot_tap_id": 323.85, "linestop_id": 336.5},
    16: {"hot_tap_id": 373.0752, "linestop_id": 387.3},
    18: {"hot_tap_id": 382.5748, "linestop_id": 438},
    20: {"hot_tap_id": 431.8, "linestop_id": 485.7},
    22: {"hot_tap_id": 482.6, "linestop_id": 537},
    24: {"hot_tap_id": 533.4, "linestop_id": 587},
    28: {"hot_tap_id": 635, "linestop_id": 689},
    30: {"hot_tap_id": 685.8, "linestop_id": 740},
    32: {"hot_tap_id": 736.6, "linestop_id": 790.4},
    34: {"hot_tap_id": 787.4, "linestop_id": 841},
    36: {"hot_tap_id": 838.2, "linestop_id": 891},
    40: {"hot_tap_id": 939.8, "linestop_id": 994},
    42: {"hot_tap_id": 990.6, "linestop_id": 1044},
    48: {"hot_tap_id": 1143, "linestop_id": 1197},
}

# --- Tee / Nozzle Data (from FL KG L-S columns) ---
TEE_DATA = {
    0.5: {"od": 0.84, "wt": 0.15, "wt_lbs": 0.15, "wt_kgs": 0.0681},
    0.75: {"od": 1.05, "wt": 0.15, "wt_lbs": 0.16, "wt_kgs": 0.07264},
    1: {"od": 1.32, "wt": 0.18, "wt_lbs": 0.28, "wt_kgs": 0.12712},
    1.5: {"od": 1.9, "wt": 0.20, "wt_lbs": 0.61, "wt_kgs": 0.27694},
    2: {"od": 2.38, "wt": 0.22, "wt_lbs": 1.2, "wt_kgs": 0.5448},
    2.5: {"od": 2.88, "wt": 0.28, "wt_lbs": 2, "wt_kgs": 0.908},
    3: {"od": 3.5, "wt": 0.30, "wt_lbs": 3.3, "wt_kgs": 1.4982},
    4: {"od": 4.5, "wt": 0.34, "wt_lbs": 6.2, "wt_kgs": 2.8148},
    5: {"od": 5.56, "wt": 0.38, "wt_lbs": 10.5, "wt_kgs": 4.767},
    6: {"od": 6.62, "wt": 0.43, "wt_lbs": 17, "wt_kgs": 7.718},
    8: {"od": 8.62, "wt": 0.50, "wt_lbs": 34.3, "wt_kgs": 15.5722},
    10: {"od": 10.75, "wt": 0.50, "wt_lbs": 53.5, "wt_kgs": 24.289},
    12: {"od": 12.75, "wt": 0.50, "wt_lbs": 77.6, "wt_kgs": 35.2304},
    14: {"od": 14, "wt": 0.50, "wt_lbs": 100, "wt_kgs": 45.4},
    16: {"od": 16, "wt": 0.50, "wt_lbs": 134, "wt_kgs": 60.836},
    18: {"od": 18, "wt": 0.50, "wt_lbs": 170, "wt_kgs": 77.18},
    20: {"od": 20, "wt": 0.50, "wt_lbs": 209, "wt_kgs": 94.886},
    24: {"od": 24, "wt": 0.50, "wt_lbs": 302, "wt_kgs": 137.108},
    30: {"od": 30, "wt": 0.50, "wt_lbs": 475.1, "wt_kgs": 215.6954},
    36: {"od": 36, "wt": 0.50, "wt_lbs": 686.1, "wt_kgs": 311.4894},
    42: {"od": 42, "wt": 0.50, "wt_lbs": 936.1, "wt_kgs": 424.9894},
    48: {"od": 48, "wt": 0.50, "wt_lbs": 1250, "wt_kgs": 567.5},
}

# --- Flange Weight Data: { class: { size_inch: (WN_kg, BLD_kg) } } ---
FL_WN = {}
FL_BLD = {}

_fl_150_sizes = [0.5,0.75,1,1.5,2,2.5,3,4,5,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48]
_fl_150_wn = [0.908,0.908,1.362,1.816,2.724,3.632,4.54,6.81,8.626,10.896,17.706,23.608,36.32,49.94,63.56,68.1,81.72,102.15,118.04,138.533,160.666,184.438,209.849,236.9,265.59,295.92,327.889,361.498,396.746,433.633,472.16]
_fl_150_bld = [0.454,0.908,0.908,1.362,2.27,3.178,4.086,7.718,9.08,11.804,20.43,31.78,49.94,63.56,81.72,99.88,129.39,161.17,195.22,229.112,265.716,305.031,347.058,391.796,439.245,489.406,542.278,597.861,656.156,717.162,780.88]
FL_WN["150#"] = dict(zip(_fl_150_sizes, _fl_150_wn))
FL_BLD["150#"] = dict(zip(_fl_150_sizes, _fl_150_bld))

_fl_300_sizes = _fl_150_sizes
_fl_300_wn = [0.908,1.362,1.816,3.178,4.086,5.448,6.81,11.35,14.528,19.068,30.418,41.314,63.56,81.72,113.5,145.28,181.6,211.11,263.32,309.035,358.408,411.438,468.124,528.469,592.47,660.129,731.444,806.418,885.048,967.335,1053.28]
_fl_300_bld = [0.454,1.362,1.362,2.724,3.632,5.448,7.264,12.258,15.89,22.7,36.774,56.296,83.99,113.5,133.93,179.33,229.27,290.56,358.66,420.927,488.176,560.406,637.618,719.811,806.985,899.141,996.278,1098.397,1205.496,1317.577,1434.64]
FL_WN["300#"] = dict(zip(_fl_300_sizes, _fl_300_wn))
FL_BLD["300#"] = dict(zip(_fl_300_sizes, _fl_300_bld))

_fl_600_sizes = _fl_150_sizes
_fl_600_wn = [0.908,1.816,1.816,3.632,5.448,8.172,10.442,19.068,30.872,36.774,54.48,86.26,102.15,127.12,177.06,215.65,267.86,326.88,376.82,442.24,512.894,588.781,669.902,756.257,847.845,944.667,1046.722,1154.011,1266.534,1384.29,1507.28]
_fl_600_bld = [0.908,1.362,1.816,3.632,4.54,6.81,9.08,18.614,30.872,39.044,63.56,104.42,133.93,161.17,224.73,286.02,367.74,454.0,567.5,666.024,772.431,886.719,1008.889,1138.941,1276.875,1422.691,1576.389,1737.969,1907.431,2084.774,2270.0]
FL_WN["600#"] = dict(zip(_fl_600_sizes, _fl_600_wn))
FL_BLD["600#"] = dict(zip(_fl_600_sizes, _fl_600_bld))

_fl_900_sizes = [0.5,0.75,1,1.5,2,2.5,3,4,5,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48]
_fl_900_wn = [2.27,2.724,4.086,5.902,11.35,16.344,14.074,24.062,39.044,49.94,79.45,118.04,147.55,181.6,224.73,308.72,376.82,None,681,799.229,926.917,1064.063,1210.667,1366.729,1532.25,1707.229,1891.667,2085.563,2288.917,2501.729,2724.0]
_fl_900_bld = [1.816,2.724,3.632,5.902,11.35,15.89,13.166,24.516,39.498,52.21,90.8,131.66,188.41,236.08,272.4,385.9,488.05,None,919.35,1078.959,1251.338,1436.484,1634.4,1845.084,2068.538,2304.759,2553.75,2815.509,3090.038,3377.334,3677.4]
FL_WN["900#"] = dict(zip(_fl_900_sizes, _fl_900_wn))
FL_BLD["900#"] = dict(zip(_fl_900_sizes, _fl_900_bld))

# --- Dropdown option lists (from DATA sheet) ---
REINFORCEMENT_TYPES = ["Nipel / Nipple", "Yaka Takviyeli / Pad Reinforcement", "Tam Semerli / Full Encirclement", "Weldoletli / Weldolet"]
FITTING_TYPES = ["Hot Tap", "Linestop"]
COMPLETION_TYPES = ["Aktif Tapa / Active Plug", "Pasif Tapa / Passive Plug", "Tapasiz / No Plug", "Disli Tapa / Threaded Plug"]
GUIDEBAR_TYPES = ["Standard", "No", "Nipple", "Flow Through"]
NOZZLE_TYPES = ["Tee", "Straight", "Tee+Nipple"]
STANDARDS = ["ASME B31.4", "ASME B31.8"]
SPECIFICATIONS = [
    "ZORLU ENERJI TR24Z-ST-M-111-0002",
    "GTCL",
    "IGDAS TKS A132-12",
    "BOTAS 4 - NGTL 0 - PL - P - 002-5010-R1",
]

# --- Plug weight data (active plug height per branch size) ---
ACTIVE_PLUG_HEIGHTS = {4: 22, 6: 35, 8: 35, 10: 36.7, 12: 36.7}
PASSIVE_PLUG_HEIGHTS = {
    4: 70, 5: 81, 6: 81, 8: 81, 10: 81, 12: 82, 14: 82, 16: 82,
    18: 82, 20: 82, 22: 82, 24: 120, 26: 120, 28: 130, 30: 130,
    32: 150, 34: 150, 36: 150, 38: 140, 40: 150,
}

STEEL_DENSITY = 7900  # kg/m3


# ============================================================
# HELPER FUNCTIONS & PDF CLASS
# ============================================================

def get_pressure_class(pressure_bar):
    if pressure_bar < 21:
        return "150#"
    elif pressure_bar < 52:
        return "300#"
    elif pressure_bar < 102:
        return "600#"
    elif pressure_bar < 150:
        return "900#"
    else:
        return "XXXXXXX"

def lookup_pipe_od_mm(inch):
    return PIPE_OD_LOOKUP.get(inch, None)

def get_smys(material_name):
    if material_name in PIPE_MATERIALS:
        return PIPE_MATERIALS[material_name]
    if material_name in FLANGE_MATERIALS:
        return FLANGE_MATERIALS[material_name]
    return (0, 0)

def get_nozzle_hole_id(branch_inch, fitting_type):
    if branch_inch in NOZZLE_DATA:
        if fitting_type == "Hot Tap":
            return NOZZLE_DATA[branch_inch]["hot_tap_id"]
        else:
            return NOZZLE_DATA[branch_inch]["linestop_id"]
    return 0

def get_flange_wn_kg(pressure_class, branch_inch):
    data = FL_WN.get(pressure_class, {})
    return data.get(branch_inch, 0) or 0

def get_flange_bld_kg(pressure_class, branch_inch):
    data = FL_BLD.get(pressure_class, {})
    return data.get(branch_inch, 0) or 0

def get_nozzle_weight_kg(branch_inch):
    if branch_inch in TEE_DATA:
        return TEE_DATA[branch_inch]["wt_kgs"]
    return 0

def get_plug_height(completion_type, branch_inch):
    if completion_type == "Aktif Tapa / Active Plug":
        return ACTIVE_PLUG_HEIGHTS.get(branch_inch, 0)
    elif completion_type == "Pasif Tapa / Passive Plug":
        return PASSIVE_PLUG_HEIGHTS.get(branch_inch, 0)
    elif completion_type == "Tapasiz / No Plug":
        return 0
    return 0

class PDFReport(FPDF):
    def header(self):
        """This runs automatically every time a new page is created."""
        logo_path = "logo.png"
        
        if os.path.exists(logo_path):
            # Place the logo at the top left
            self.image(logo_path, x=10, y=8, w=40)
            # Push the starting Y-coordinate down so text doesn't overlap the logo
            self.set_y(30)
        else:
            self.set_y(15)

    def footer(self):
        """This runs automatically at the bottom of every page."""
        # Position cursor 15 mm from the bottom
        self.set_y(-15)
        self.set_font("Helvetica", style="I", size=8)
        self.set_text_color(128, 128, 128) # Grey
        # Print the certification and page numbers
        self.multi_cell(0, 4, f"We hereby certify that these calculations are based on the specification referenced above and conform to the standards referenced therein (ASME B31.8). | Page {self.page_no()}", align="C")

def create_pdf_report(project_info, params, results):
    """Generates a detailed ASME B31.8 compliant PDF report with formulas."""
    pdf = PDFReport()
    pdf.add_page()
    
    def section_title(title):
        pdf.ln(5)
        pdf.set_font("Helvetica", style="B", size=12)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 8, f" {title}", new_x="LMARGIN", new_y="NEXT", border=1, fill=True)
        pdf.ln(2)

    def row(label, value, formula=""):
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.cell(60, 6, label, border=0)
        pdf.set_font("Helvetica", style="", size=10)
        pdf.cell(40, 6, str(value), border=0)
        if formula:
            pdf.set_font("Courier", style="I", size=9)
            pdf.cell(0, 6, str(formula), border=0, new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.ln(6)

    # --- Header (Main Title) ---
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "PROTAP Hot-Tap / Linestop Calculation Report", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("Helvetica", style="I", size=11)
    pdf.cell(0, 6, "Branch Connection Reinforcement Calculation based on ASME B31.8", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # --- Overall Result Banner ---
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=14)
    if results['control_in2'] < 0:
        pdf.set_text_color(0, 128, 0) # Green
        pdf.cell(0, 10, f"OVERALL RESULT: {results['result']}", new_x="LMARGIN", new_y="NEXT", align="C", border=1)
    else:
        pdf.set_text_color(255, 0, 0) # Red
        pdf.cell(0, 10, f"OVERALL RESULT: {results['result']}", new_x="LMARGIN", new_y="NEXT", align="C", border=1)
    pdf.set_text_color(0, 0, 0) # Reset to black

    # --- 1. Project Information ---
    section_title("1. Project Information")
    for key, value in project_info.items():
        row(str(key) + ":", str(value))
        
    # --- 2. Design Inputs ---
    section_title("2. Design Parameters & Inputs")
    p_psi = params['design_pressure_bar'] * 14.5
    row("Design Pressure (P):", f"{params['design_pressure_bar']} bar ({p_psi:.1f} psi)")
    row("Design Factor (F):", params['design_factor_F'])
    row("Longitudinal Factor (E):", params['design_factor_E'])
    row("Temp Derating (T):", params['design_factor_T'])
    row("Corrosion Allow (c):", f"{params['corrosion_allowance_mm']} mm")
    row("Header OD (Dh):", f"{results['header_od_mm']:.1f} mm")
    row("Branch OD (Db):", f"{results['Db_mm']:.1f} mm")
    row("Nominal Hole Dia (d):", f"{results['db_mm']:.1f} mm")

    # --- 3. Material Properties ---
    section_title("3. Material Specifications (SMYS)")
    row("Header Material:", f"{results['header_SMYS_psi']:,.0f} psi", params['header_material'])
    row("Branch Material:", f"{results['nozzle_SMYS_psi']:,.0f} psi", params['nozzle_tee_material'])
    row("Reinf. Material:", f"{results['reinforcement_SMYS_psi']:,.0f} psi", params['reinforcement_material'])

    # --- 4. Required Thickness Calculations ---
    section_title("4. Required Wall Thickness Calculations")
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.multi_cell(0, 5, "ASME B31.8 Formula: t = (P * D) / (2 * S * F * E * T)")
    pdf.ln(2)
    row("Req. Header WT (th):", f"{results['t_required_mm']:.2f} mm", "th = P * Dh / (2 * Sh * F * E * T)")
    row("Actual Header WT (Th):", f"{params['header_wt_mm']:.2f} mm")
    row("Req. Branch WT (tb):", f"{results['tb_mm']:.2f} mm", "tb = P * Db / (2 * Sb * F * E * T)")
    row("Actual Branch WT (Tb):", f"{params['nozzle_tee_wt_mm']:.2f} mm")

    # --- 5. Area Replacement Method (ASME B31.8) ---
    section_title("5. Area Replacement (ASME B31.8)")
    row("Req. Reinforcement (Ar):", f"{results['Ar_mm2']:.2f} mm2", "Ar = d * th")
    
    # A1
    pdf.ln(2)
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.multi_cell(0, 5, "Available Area in Header (A1) = (Th - th - c) * d")
    row("Header Area (A1):", f"{results['A1_mm2']:.2f} mm2")
    
    # A2
    pdf.ln(2)
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.multi_cell(0, 5, "Available Area in Branch (A2') = 2 * Lb * (Tb - tb - c) * (Sb / Sh)")
    row("Branch Area (A2'):", f"{results['A2_prime_mm2']:.2f} mm2")
    
    # A3
    pdf.ln(2)
    pdf.set_font("Helvetica", style="I", size=9)
    pdf.multi_cell(0, 5, "Available Area in Reinforcement (A3') = Pad Area * (Sr / Sh)")
    row("Reinf. Area (A3'):", f"{results['A3_prime_mm2']:.2f} mm2")
    
    # Check
    pdf.ln(3)
    pdf.set_font("Helvetica", style="B", size=10)
    pdf.cell(60, 6, "Total Available (A1+A2'+A3'):", border=0)
    total_avail = results['A1_mm2'] + results['A2_prime_mm2'] + results['A3_prime_mm2']
    pdf.cell(40, 6, f"{total_avail:.2f} mm2", border=0)
    pdf.ln(6)
    row("Control (Ar - Total):", f"{results['control_mm2']:.2f} mm2", "Must be <= 0")

    # --- 6. Additional Checks & Weights ---
    if pdf.get_y() > 230:
        pdf.add_page()
        
    section_title("6. Final Checks & Estimated Weights")
    row("Flange WT Check:", results['flange_check'])
    row("Plug Shear Allowable:", f"{results['plug_S_allowable']:.1f} MPa")
    row("Min Plug Thickness:", f"{results['plug_min_thickness_mm']:.2f} mm")
    pdf.ln(2)
    row("Est. Total Weight:", f"{results['total_weight_kg']:.2f} kg", "Includes flanges, nozzle, plug, and reinf.")

    return bytes(pdf.output())


# ============================================================
# MAIN CALCULATION ENGINE
# ============================================================

def run_calculation(params):
    r = {} 

    # Input Extraction
    header_od_inch = params["header_od_inch"]
    branch_od_inch = params["branch_od_inch"]
    design_pressure_bar = params["design_pressure_bar"]
    design_factor_F = params["design_factor_F"]
    design_factor_E = params["design_factor_E"]
    design_factor_T = params["design_factor_T"]

    header_material = params["header_material"]
    flange_material = params["flange_material"]
    nozzle_tee_material = params["nozzle_tee_material"]
    nozzle_ext_material = params["nozzle_ext_material"]
    reinforcement_material = params["reinforcement_material"]
    corrosion_allowance_mm = params["corrosion_allowance_mm"]

    reinforcement_type = params["reinforcement_type"]
    fitting_type = params["fitting_type"]
    nozzle_type = params["nozzle_type"]
    completion_type = params["completion_type"]
    guide_bar = params["guide_bar"]

    header_wt_mm = params["header_wt_mm"]
    flange_wt_mm = params["flange_wt_mm"]
    nozzle_tee_wt_mm = params["nozzle_tee_wt_mm"]
    nozzle_ext_wt_mm = params.get("nozzle_ext_wt_mm", 0)
    reinforcement_wt_mm = params["reinforcement_wt_mm"]

    # Derived / Lookup Values
    r["pressure_class"] = get_pressure_class(design_pressure_bar)
    r["header_od_mm"] = lookup_pipe_od_mm(header_od_inch)
    r["branch_od_mm"] = lookup_pipe_od_mm(branch_od_inch)

    if r["header_od_mm"] is None or r["branch_od_mm"] is None:
        return {"error": "Invalid pipe size selected. Please check Header and Branch OD."}

    header_wt_in = header_wt_mm / 25.4
    flange_wt_in = flange_wt_mm / 25.4
    nozzle_tee_wt_in = nozzle_tee_wt_mm / 25.4
    nozzle_ext_wt_in = nozzle_ext_wt_mm / 25.4
    reinforcement_wt_in = reinforcement_wt_mm / 25.4
    corrosion_allowance_in = corrosion_allowance_mm / 25.4

    header_od_in = header_od_inch
    branch_od_in = branch_od_inch

    Dh_mm = r["header_od_mm"]
    Dh_in = Dh_mm / 25.4
    Db_lookup_mm = r["branch_od_mm"]

    _, Sh_psi = get_smys(header_material)
    Sh_metric = get_smys(header_material)[0]
    _, Sf_psi = get_smys(flange_material)
    Sb_metric, Sb_psi = get_smys(nozzle_tee_material)
    Sext_metric, Sext_psi = get_smys(nozzle_ext_material) if nozzle_type == "Tee+Nipple" else (0, 0)
    Sr_metric, Sr_psi = get_smys(reinforcement_material)

    r["header_SMYS_metric"] = Sh_metric
    r["header_SMYS_psi"] = Sh_psi
    r["flange_SMYS_psi"] = Sf_psi
    r["nozzle_SMYS_metric"] = Sb_metric
    r["nozzle_SMYS_psi"] = Sb_psi
    r["reinforcement_SMYS_metric"] = Sr_metric
    r["reinforcement_SMYS_psi"] = Sr_psi

    # PIPE CALCULATION
    P_bar = design_pressure_bar
    P_psi = P_bar * 14.5
    F = design_factor_F
    E = design_factor_E
    T = design_factor_T
    Th_mm = header_wt_mm
    Th_in = header_wt_in

    if Sh_psi > 0 and F > 0 and E > 0 and T > 0:
        t_required_in = P_psi * Dh_in / (2 * Sh_psi * F * E * T)
    else:
        t_required_in = 0
    t_required_mm = t_required_in * 25.4
    r["t_required_mm"] = t_required_mm
    r["t_required_in"] = t_required_in

    if reinforcement_type == "Tam Semerli / Full Encirclement":
        excess_header_mm = 0
    elif Th_mm - t_required_mm - corrosion_allowance_mm < 0:
        excess_header_mm = 0
    else:
        excess_header_mm = Th_mm - t_required_mm - corrosion_allowance_mm
    excess_header_in = excess_header_mm / 25.4
    r["excess_header_mm"] = excess_header_mm
    r["excess_header_in"] = excess_header_in

    if Th_in > 0:
        S_hoop_psi = P_psi * Dh_in / (2 * Th_in * 1)
    else:
        S_hoop_psi = 0
    r["hoop_stress_psi"] = S_hoop_psi
    r["S_over_Sh"] = S_hoop_psi / Sh_psi if Sh_psi > 0 else 0

    r["fitting_required"] = reinforcement_type

    # HOT-TAP FITTING CALCULATION
    nozzle_nd_id = get_nozzle_hole_id(branch_od_inch, fitting_type)
    if fitting_type == "Hot Tap":
        Db_mm = Db_lookup_mm
    else:
        Db_mm = max(nozzle_nd_id + 2 * nozzle_tee_wt_mm + 3, Db_lookup_mm)

    Db_in = Db_mm / 25.4
    r["Db_mm"] = Db_mm
    r["Db_in"] = Db_in

    Th_net_mm = Th_mm - corrosion_allowance_mm
    Th_net_in = Th_net_mm / 25.4
    r["Th_net_mm"] = Th_net_mm

    if fitting_type == "Hot Tap":
        db_mm = Db_lookup_mm - 2 * nozzle_tee_wt_mm
    else:
        db_mm = max(nozzle_nd_id, Db_lookup_mm - 2 * nozzle_tee_wt_mm)
    db_in = db_mm / 25.4
    r["db_mm"] = db_mm
    r["db_in"] = db_in

    th_in = t_required_in
    th_mm = t_required_mm
    r["th_mm"] = th_mm

    Ar_in2 = db_in * th_in
    Ar_mm2 = Ar_in2 * 25.4 ** 2
    r["Ar_mm2"] = Ar_mm2
    r["Ar_in2"] = Ar_in2

    r["reinf_material"] = reinforcement_material
    r["reinf_SMYS_metric"] = Sr_metric
    r["reinf_SMYS_psi"] = Sr_psi

    # A1: Header area
    A1_excess_in = excess_header_in
    A1_ND_in = db_in
    if reinforcement_type == "Tam Semerli / Full Encirclement":
        A1_in2 = 0
    elif A1_excess_in < 0:
        A1_in2 = 0
    else:
        A1_in2 = A1_ND_in * A1_excess_in
    A1_mm2 = A1_in2 * 25.4 ** 2
    r["A1_mm2"] = A1_mm2
    r["A1_in2"] = A1_in2

    # A2: Nozzle area
    if nozzle_type == "Tee+Nipple":
        Tb_mm = nozzle_ext_wt_mm
        Sb_calc_psi = Sext_psi
        Sb_calc_metric = Sext_metric
    else:
        Tb_mm = nozzle_tee_wt_mm
        Sb_calc_psi = Sb_psi
        Sb_calc_metric = Sb_metric

    Tb_net_mm = Tb_mm - corrosion_allowance_mm
    Tb_net_in = Tb_net_mm / 25.4
    r["Tb_net_mm"] = Tb_net_mm

    Tr_mm = reinforcement_wt_mm - corrosion_allowance_mm
    Tr_in = Tr_mm / 25.4
    r["Tr_mm"] = Tr_mm

    Lb_mm = min(2.5 * Th_mm, 2.5 * Tb_net_mm + Tr_mm)
    Lb_in = Lb_mm / 25.4
    r["Lb_mm"] = Lb_mm

    if Sb_calc_metric > 0:
        tb_in = P_psi * Db_in / 2 / Sb_calc_metric / 148.5 / F / E / T
    else:
        tb_in = 0
    tb_mm = tb_in * 25.4
    r["tb_mm"] = tb_mm

    excess_nozzle_in = Tb_net_in - tb_in
    excess_nozzle_mm = excess_nozzle_in * 25.4
    r["excess_nozzle_mm"] = excess_nozzle_mm

    A2_in2 = Lb_in * excess_nozzle_in * 2
    A2_mm2 = A2_in2 * 25.4 ** 2
    r["A2_mm2"] = A2_mm2
    r["A2_in2"] = A2_in2

    if Sb_calc_metric > 0 and Sh_metric > 0:
        mat_ratio_A2 = Sb_calc_metric / Sh_metric
    else:
        mat_ratio_A2 = 1
    if mat_ratio_A2 >= 1:
        mat_ratio_A2 = 1
    A2_prime_in2 = A2_in2 * mat_ratio_A2
    A2_prime_mm2 = A2_prime_in2 * 25.4 ** 2
    r["A2_prime_mm2"] = A2_prime_mm2

    # A3: Reinforcement Pad / Sleeve area
    Lr_mm = 2 * db_mm
    Lr_in = Lr_mm / 25.4
    r["Lr_mm"] = Lr_mm

    if reinforcement_type == "Tam Semerli / Full Encirclement":
        A3_in2 = (Tr_in - t_required_in) * (Lr_in - db_in)
    else:
        A3_in2 = Tr_in * (Lr_in - db_in) + (Lr_in - db_in) * excess_header_in

    A3_mm2 = A3_in2 * 25.4 ** 2
    r["A3_mm2"] = A3_mm2

    if Sr_metric > 0 and Sh_metric > 0:
        mat_ratio_A3 = Sr_metric / Sh_metric
    elif Sr_psi > 0 and Sh_psi > 0:
        mat_ratio_A3 = Sr_psi / Sh_psi
    else:
        mat_ratio_A3 = 1
    if mat_ratio_A3 > 1:
        mat_ratio_A3 = 1
    if reinforcement_type != "Nipel / Nipple":
        A3_prime_in2 = A3_in2 * mat_ratio_A3
    else:
        A3_prime_in2 = 0
    A3_prime_mm2 = A3_prime_in2 * 25.4 ** 2
    r["A3_prime_mm2"] = A3_prime_mm2

    # CONTROL
    P44 = 0
    control_in2 = Ar_in2 - A1_in2 - A2_prime_in2 - A3_prime_in2 - P44
    control_mm2 = control_in2 * 25.4 ** 2
    r["control_mm2"] = control_mm2
    r["control_in2"] = control_in2

    if control_in2 < 0:
        r["result"] = "UYGUN/SUITABLE!"
    else:
        r["result"] = "UYGUN DEGIL/NOT SUITABLE!"

    # FLANGE CHECK
    if Sf_psi > 0 and F > 0 and E > 0 and T > 0:
        flange_req = P_psi * Db_in / 2 / Sf_psi / F / E / T
    else:
        flange_req = 0
    flange_check = flange_wt_in - corrosion_allowance_in > flange_req
    r["flange_check"] = "OK" if flange_check else "NOT OK"

    r["nozzle_check"] = "OK" if control_mm2 < 0 else "NOT OK"

    # WEIGHT CALCULATION
    pc = r["pressure_class"]
    wn_flange_kg = get_flange_wn_kg(pc, branch_od_inch)
    bld_flange_kg = get_flange_bld_kg(pc, branch_od_inch)
    nozzle_kg = get_nozzle_weight_kg(branch_od_inch)

    if reinforcement_type == "Nipel / Nipple":
        reinf_kg = 0
    elif reinforcement_type == "Yaka Takviyeli / Pad Reinforcement":
        reinf_kg = math.pi * reinforcement_wt_mm * (Lr_mm ** 2 - Db_mm ** 2) * STEEL_DENSITY / 1e9 / 4
    elif reinforcement_type == "Tam Semerli / Full Encirclement":
        reinf_kg = (math.pi * reinforcement_wt_mm * Lr_mm * (Dh_mm + reinforcement_wt_mm) * STEEL_DENSITY / 1e9
            - math.pi * reinforcement_wt_mm * Db_mm ** 2 / 4 / 1e9)
    else:
        reinf_kg = 0

    plug_height = get_plug_height(completion_type, branch_od_inch)
    if completion_type == "Tapasiz / No Plug":
        plug_kg = 0
    else:
        plug_kg = math.pi * db_mm ** 2 * plug_height * STEEL_DENSITY / 1e9 / 4

    total_weight = wn_flange_kg + bld_flange_kg + nozzle_kg + reinf_kg + plug_kg

    r["wn_flange_kg"] = wn_flange_kg
    r["bld_flange_kg"] = bld_flange_kg
    r["nozzle_kg"] = nozzle_kg
    r["reinf_kg"] = reinf_kg
    r["plug_kg"] = plug_kg
    r["total_weight_kg"] = total_weight

    # PLUG CALCULATION
    plug_Re = 355  # MPa (C45E)
    plug_C = 0.3
    plug_F_factor = F
    plug_S_allowable = plug_Re * plug_F_factor  # MPa
    if plug_S_allowable > 0:
        plug_min_thickness = db_mm * math.sqrt(plug_C * P_bar / 10 / plug_S_allowable / F)
    else:
        plug_min_thickness = 0
    r["plug_min_thickness_mm"] = plug_min_thickness
    r["plug_S_allowable"] = plug_S_allowable

    return r


# ============================================================
# STREAMLIT APP
# ============================================================

st.set_page_config(page_title="PROTAP Calculation Tool", layout="wide")
st.title("🔧 PROTAP Hot-Tap / Linestop Calculation")
st.markdown("**ASME B31.8 - Branch Connection Reinforcement Calculation**")
st.markdown("---")

# ---- SIDEBAR: Project Info ----
with st.sidebar:
    st.header("📋 Project Information")
    project_name = st.text_input("Sheet Name", value="25-425 PU SRB")
    location = st.text_input("Location", value="SERBIA")
    client = st.text_input("Client / Owner", value="EIC")
    client_ref = st.text_input("Client Ref", value="")
    protap_ref = st.text_input("PROTAP Ref", value="25-425 PU ROU")
    standard = st.selectbox("Standard", STANDARDS, index=1)
    specification = st.selectbox("Specification", [""] + SPECIFICATIONS)

# ---- MAIN: Input Section ----
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Pipeline Data")
    available_sizes = sorted(PIPE_OD_LOOKUP.keys())
    header_od_inch = st.selectbox("Header OD (inch)", available_sizes, index=available_sizes.index(32))
    branch_od_inch = st.selectbox("Branch OD (inch)", available_sizes, index=available_sizes.index(20))
    design_pressure = st.number_input("Design Pressure (bar)", value=63.0, min_value=0.1, step=1.0)
    design_factor_F = st.number_input("Design Factor (F)", value=0.5, min_value=0.01, max_value=1.0, step=0.01)
    design_factor_E = st.number_input("Design Factor (E)", value=1.0, min_value=0.01, max_value=1.0, step=0.01)
    design_factor_T = st.number_input("Design Factor (T)", value=1.0, min_value=0.01, max_value=1.0, step=0.01)

with col2:
    st.subheader("Materials & Wall Thickness")
    all_pipe_materials = list(PIPE_MATERIALS.keys())
    all_flange_materials = list(FLANGE_MATERIALS.keys())

    header_material = st.selectbox("Header Material", all_pipe_materials, index=all_pipe_materials.index("API 5L X60/L415NE"))
    header_wt = st.number_input("Header WT (mm)", value=14.2, min_value=0.1, step=0.1)

    flange_material = st.selectbox("Flange Material", all_flange_materials, index=0)
    flange_wt = st.number_input("Flange WT (mm)", value=15.0, min_value=0.1, step=0.1)

    nozzle_tee_material = st.selectbox("Nozzle / Tee Material (min)", all_pipe_materials,
                     index=all_pipe_materials.index("EN 10028-3 P355NL1 (t <= 16mm)"))
    nozzle_tee_wt = st.number_input("Nozzle / Tee WT (mm)", value=15.0, min_value=0.1, step=0.1)

with col3:
    st.subheader("Additional Parameters")
    nozzle_type = st.selectbox("Nozzle Type", NOZZLE_TYPES, index=NOZZLE_TYPES.index("Straight"))

    nozzle_ext_material_name = "N/A"
    nozzle_ext_wt = 0.0
    if nozzle_type == "Tee+Nipple":
        nozzle_ext_material_name = st.selectbox("Nozzle Extension Material", all_pipe_materials, index=0)
        nozzle_ext_wt = st.number_input("Nozzle Extension WT (mm)", value=0.0, min_value=0.0, step=0.1)
    else:
        st.text("Nozzle Extension: N/A")

    reinforcement_material = st.selectbox("Reinforcement Material", all_pipe_materials,
                       index=all_pipe_materials.index("EN 10028-3 P355NL1 (16 < t <= 40mm)"))
    reinforcement_wt = st.number_input("Reinforcement WT (mm)", value=28.5, min_value=0.1, step=0.1)

    corrosion_allowance = st.number_input("Corrosion Allowance (mm)", value=0.0, min_value=0.0, step=0.1)

st.markdown("---")
col_a, col_b = st.columns(2)
with col_a:
    reinforcement_type = st.selectbox("Reinforcement Type", REINFORCEMENT_TYPES, index=REINFORCEMENT_TYPES.index("Tam Semerli / Full Encirclement"))
    fitting_type = st.selectbox("Fitting Type", FITTING_TYPES, index=0)
with col_b:
    completion_type = st.selectbox("Completion Type", COMPLETION_TYPES, index=COMPLETION_TYPES.index("Pasif Tapa / Passive Plug"))
    guide_bar = st.selectbox("Guide Bar", GUIDEBAR_TYPES, index=0)

st.markdown("---")

# ---- RUN CALCULATION ----
if st.button("🔨 Calculate", type="primary", use_container_width=True):
    params = {
        "header_od_inch": header_od_inch,
        "branch_od_inch": branch_od_inch,
        "design_pressure_bar": design_pressure,
        "design_factor_F": design_factor_F,
        "design_factor_E": design_factor_E,
        "design_factor_T": design_factor_T,
        "header_material": header_material,
        "flange_material": flange_material,
        "nozzle_tee_material": nozzle_tee_material,
        "nozzle_ext_material": nozzle_ext_material_name,
        "reinforcement_material": reinforcement_material,
        "corrosion_allowance_mm": corrosion_allowance,
        "reinforcement_type": reinforcement_type,
        "fitting_type": fitting_type,
        "nozzle_type": nozzle_type,
        "completion_type": completion_type,
        "guide_bar": guide_bar,
        "header_wt_mm": header_wt,
        "flange_wt_mm": flange_wt,
        "nozzle_tee_wt_mm": nozzle_tee_wt,
        "nozzle_ext_wt_mm": nozzle_ext_wt,
        "reinforcement_wt_mm": reinforcement_wt,
    }

    # Store calculation in session state so download button doesn't wipe it
    st.session_state['calc_results'] = run_calculation(params)
    st.session_state['calc_params'] = params
    st.session_state['is_calculated'] = True


if st.session_state.get('is_calculated', False):
    results = st.session_state['calc_results']
    saved_params = st.session_state['calc_params']

    if "error" in results:
        st.error(results["error"])
    else:
        # ---- RESULT BANNER ----
        if results["result"] == "UYGUN/SUITABLE!":
            st.success(f"## ✅ RESULT: {results['result']}")
        else:
            st.error(f"## ❌ RESULT: {results['result']}")

        # ---- Detailed Results ----
        st.markdown("---")
        r1, r2, r3 = st.columns(3)

        with r1:
            st.subheader("📐 Pipe Calculation")
            st.metric("Pressure Class", results["pressure_class"])
            st.metric("Header OD", f"{results['header_od_mm']:.1f} mm")
            st.metric("Branch OD (Db)", f"{results['Db_mm']:.1f} mm")
            st.metric("Required WT (t)", f"{results['t_required_mm']:.2f} mm")
            st.metric("Excess Header Thickness", f"{results['excess_header_mm']:.2f} mm")
            st.metric("Hoop Stress (S)", f"{results['hoop_stress_psi']:.1f} psi")
            st.metric("S / Sh", f"{results['S_over_Sh']:.4f}")

        with r2:
            st.subheader("🔩 Reinforcement Areas")
            st.metric("Area to be Reinforced (Ar)", f"{results['Ar_mm2']:.2f} mm²")
            st.metric("Header Area (A1)", f"{results['A1_mm2']:.2f} mm²")
            st.metric("Nozzle Area (A2')", f"{results['A2_prime_mm2']:.2f} mm²")
            st.metric("Reinforcement Area (A3')", f"{results['A3_prime_mm2']:.2f} mm²")
            control_val = results['control_mm2']
            st.metric("Ar - (A1+A2'+A3')", f"{control_val:.2f} mm²",
                   delta=f"{'Sufficient' if control_val < 0 else 'Insufficient'}",
                   delta_color="normal" if control_val < 0 else "inverse")

        with r3:
            st.subheader("⚖️ Weight Estimate")
            st.metric("WN Flange", f"{results['wn_flange_kg']:.2f} kg")
            st.metric("BL Flange", f"{results['bld_flange_kg']:.2f} kg")
            st.metric("Nozzle", f"{results['nozzle_kg']:.3f} kg")
            st.metric("Reinforcement", f"{results['reinf_kg']:.2f} kg")
            st.metric("Plug", f"{results['plug_kg']:.2f} kg")
            st.metric("**TOTAL WEIGHT**", f"{results['total_weight_kg']:.2f} kg")

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🔍 Additional Checks")
            fc = results["flange_check"]
            nc = results["nozzle_check"]
            if fc == "OK":
                st.success(f"Flange Check: **{fc}**")
            else:
                st.error(f"Flange Check: **{fc}**")
            if nc == "OK":
                st.success(f"Nozzle Check: **{nc}**")
            else:
                st.error(f"Nozzle Check: **{nc}**")

        with c2:
            st.subheader("🔩 Plug Data")
            st.write(f"Plug Material: **C45E**")
            st.write(f"Allowable Shear (S): **{results['plug_S_allowable']:.1f} MPa**")
            st.write(f"Min Plug Thickness: **{results['plug_min_thickness_mm']:.2f} mm**")
            st.write(f"Nominal Hole Diameter (db): **{results['db_mm']:.1f} mm**")
            st.write(f"Reinforcement Length (Lr): **{results['Lr_mm']:.1f} mm**")

        # ---- Intermediate Calculation Details (Expandable) ----
        with st.expander("📊 Show All Intermediate Values"):
            st.json({
                "Pressure (bar)": saved_params["design_pressure_bar"],
                "Pressure (psi)": saved_params["design_pressure_bar"] * 14.5,
                "Header OD (mm)": results["header_od_mm"],
                "Header OD (in)": results["header_od_mm"] / 25.4,
                "Branch OD Db (mm)": results["Db_mm"],
                "Branch OD Db (in)": results["Db_in"],
                "Nominal Hole db (mm)": results["db_mm"],
                "Nominal Hole db (in)": results["db_in"],
                "Required WT t (mm)": results["t_required_mm"],
                "Required WT t (in)": results["t_required_in"],
                "Excess Header (mm)": results["excess_header_mm"],
                "Th net (mm)": results["Th_net_mm"],
                "Tb net (mm)": results["Tb_net_mm"],
                "Tr (mm)": results["Tr_mm"],
                "Lb (mm)": results["Lb_mm"],
                "tb (mm)": results["tb_mm"],
                "Excess Nozzle (mm)": results["excess_nozzle_mm"],
                "Ar (mm2)": results["Ar_mm2"],
                "A1 (mm2)": results["A1_mm2"],
                "A2 (mm2)": results["A2_mm2"],
                "A2' (mm2)": results["A2_prime_mm2"],
                "A3 (mm2)": results["A3_mm2"],
                "A3' (mm2)": results["A3_prime_mm2"],
                "Control Ar-(A1+A2'+A3') (mm2)": results["control_mm2"],
                "Lr (mm)": results["Lr_mm"],
                "Header SMYS (MPa)": results["header_SMYS_metric"],
                "Header SMYS (psi)": results["header_SMYS_psi"],
                "Nozzle SMYS (MPa)": results["nozzle_SMYS_metric"],
                "Nozzle SMYS (psi)": results["nozzle_SMYS_psi"],
                "Reinforcement SMYS (MPa)": results["reinforcement_SMYS_metric"],
                "Reinforcement SMYS (psi)": results["reinforcement_SMYS_psi"],
                "Hoop Stress (psi)": results["hoop_stress_psi"],
                "S/Sh": results["S_over_Sh"],
            })

        st.markdown("---")
        st.caption("PROTAP Calculation Tool - Based on ASME B31.8 Branch Connection Reinforcement")
        st.caption("We hereby certify that these calculations are based on the specification referenced above and conform to the standards referenced therein.")
        
        # ---- PDF REPORT GENERATION ----
        st.markdown("### 📄 Export Report")
        
        # 1. Package the project info, including the dynamic date
        project_data = {
            "Date": datetime.date.today().strftime("%d %B %Y"),  # e.g., 09 March 2026
            "Project Name": project_name,
            "Location": location,
            "Client": client,
            "Client Ref": client_ref,
            "PROTAP Ref": protap_ref,
            "Standard": standard,
            "Specification": specification
        }
        
        # 2. Generate the PDF bytes
        pdf_bytes = create_pdf_report(project_data, saved_params, results)
        
        # 3. Display the download button
        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=f"PROTAP_Calc_{protap_ref.replace(' ', '_')}.pdf",
            mime="application/pdf",
            type="primary"
        )
