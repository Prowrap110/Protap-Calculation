import streamlit as st
import numpy as np
import math
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
# HELPER FUNCTIONS
# ============================================================

def get_pressure_class(pressure_bar):
    """Determine pressure class from design pressure in bar (TEMPLATE!B9 logic)."""
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
    """Lookup pipe OD in mm from inch value."""
    return PIPE_OD_LOOKUP.get(inch, None)

def get_smys(material_name):
    """Return (SMYS_metric_MPa, SMYS_us_psi) for a material name."""
    if material_name in PIPE_MATERIALS:
        return PIPE_MATERIALS[material_name]
    if material_name in FLANGE_MATERIALS:
        return FLANGE_MATERIALS[material_name]
    return (0, 0)

def get_nozzle_hole_id(branch_inch, fitting_type):
    """Get the nozzle nominal hole diameter depending on fitting type."""
    if branch_inch in NOZZLE_DATA:
        if fitting_type == "Hot Tap":
            return NOZZLE_DATA[branch_inch]["hot_tap_id"]
        else:
            return NOZZLE_DATA[branch_inch]["linestop_id"]
    return 0

def get_flange_wn_kg(pressure_class, branch_inch):
    """Get WN flange weight in kg."""
    data = FL_WN.get(pressure_class, {})
    return data.get(branch_inch, 0) or 0

def get_flange_bld_kg(pressure_class, branch_inch):
    """Get BLD flange weight in kg."""
    data = FL_BLD.get(pressure_class, {})
    return data.get(branch_inch, 0) or 0

def get_nozzle_weight_kg(branch_inch):
    """Get nozzle (tee) weight in kg from TEE_DATA."""
    if branch_inch in TEE_DATA:
        return TEE_DATA[branch_inch]["wt_kgs"]
    return 0

def get_plug_height(completion_type, branch_inch):
    """Get plug height in mm for weight calculation."""
    if completion_type == "Aktif Tapa / Active Plug":
        return ACTIVE_PLUG_HEIGHTS.get(branch_inch, 0)
    elif completion_type == "Pasif Tapa / Passive Plug":
        return PASSIVE_PLUG_HEIGHTS.get(branch_inch, 0)
    elif completion_type == "Tapasiz / No Plug":
        return 0
    return 0

def create_pdf_report(project_info, params, results):
    """Generates a detailed ASME B31.8 compliant PDF report with formulas."""
    pdf = FPDF()
    pdf.add_page()
    
    # --- Helper functions for formatting ---
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

    # --- Header ---
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.cell(0, 10, "PROTAP Hot-Tap / Linestop Calculation Report", new_x="LMARGIN", new_y="NEXT", align="C")
    
    pdf.set_font("Helvetica", style="I", size=11)
    pdf.cell(0, 6, "Branch Connection Reinforcement Calculation based on ASME B31.8", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # --- Overall Result Banner ---
    pdf.ln(5)
    pdf.set_font("Helvetica", style="B", size=14)
    if results['control_in2'] < 0:
        pdf.set_text_color(0, 128, 0) # Green for Suitable
        pdf.cell(0, 10, f"OVERALL RESULT: {results['result']}", new_x="LMARGIN", new_y="NEXT", align="C", border=1)
    else:
        pdf.set_text_color(255, 0, 0) # Red for Not Suitable
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
    row("Req. Branch WT (tb
