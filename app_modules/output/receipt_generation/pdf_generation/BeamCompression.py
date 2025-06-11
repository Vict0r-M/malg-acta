import json
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Get the project root dynamically
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent

# Register DejaVuSans font with proper path resolution
font_dir = Path(__file__).parent
pdfmetrics.registerFont(TTFont('DejaVuSans', str(font_dir / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', str(font_dir / "DejaVuSans-Bold.ttf")))

def process_test_data(raw_data):
    """Process raw test data for beam compression testing"""
    tests = raw_data["tests"]
    
    # Beam compression typically uses 6 specimens (no weight data)
    forces = []
    strengths = []
    
    for test in tests:
        if test.get("compression_data") and test["compression_data"].get("kN"):
            force = round(float(test["compression_data"]["kN"]) * 1000, 2)
            forces.append(force)
            
            # For compression testing, calculate strengths using force/area
            # Where area is 150mm x 150mm = 22,500 mm²
            area = 150 * 150  # mm²
            strength = round(force / area, 2)
            strengths.append(strength)
        else:
            forces.append(0.0)
            strengths.append(0.0)
    
    # Pad to 6 specimens if needed
    while len(forces) < 6:
        forces.append(0.0)
        strengths.append(0.0)
    
    # Truncate to 6 if more
    forces = forces[:6]
    strengths = strengths[:6]

    return {
        "forces": forces,
        "strengths": strengths,
        "areas": [22500] * 6,  # All beams have same area
        "averages": {
            "force": round(sum(f for f in forces if f > 0) / len([f for f in forces if f > 0]), 2) if any(f > 0 for f in forces) else 0.0,
            "strength": round(sum(s for s in strengths if s > 0) / len([s for s in strengths if s > 0]), 2) if any(s > 0 for s in strengths) else 0.0,
            "area": 22500
        }
    }

def build_row(label_parts, values, label_width=2):
    """Helper function to build table rows"""
    return label_parts + values

def create_pdf_with_reportlab(raw_data, processed_data):
    """Create compact PDF report for beam compression testing"""
    set_id = raw_data["set_id"]
    sampling_date = raw_data["sampling_date"]
    testing_date = raw_data["testing_date"]
    test_count = 6  # Beam compression uses 6 specimens
    total_cols = 2 + test_count + 1  # 2 label columns + test values + average

    forces = processed_data["forces"]
    strengths = processed_data["strengths"]
    areas = processed_data["areas"]
    averages = processed_data["averages"]

    filename = "beam_compression.pdf"
    
    # Use dynamic path resolution:
    target_path = PROJECT_ROOT / "data" / "receipts" / "pdf_receipts" / filename
    target_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(target_path), pagesize=A4, topMargin=10*mm, bottomMargin=10*mm,
                            leftMargin=10*mm, rightMargin=10*mm)

    table_data = []

    # Header rows (merged across total columns)
    table_data.append(["PILOT 4, MODEL 50 - C4642 Nr. Serial"] + [""] * (total_cols - 1))
    table_data.append(["Rezultatele încercării:"] + [""] * (total_cols - 1))
    table_data.append([f"Indicativ serie {set_id}", ""] + [f"{i+1}" for i in range(test_count)] + ["Media"])

    # Data rows - compact format
    table_data.append(build_row(["Data confecționării", ""], [sampling_date] * test_count + [sampling_date]))
    table_data.append(build_row(["Data încercării", ""], [testing_date] * test_count + [testing_date]))
    
    # Cube dimensions - for compression, all dimensions are 150mm (cubic)
    table_data.append(build_row(["Dimensiunile cubului [mm]", "x [mm]"], ["150"] * test_count + ["150"]))
    table_data.append(build_row(["", "y [mm]"], ["150"] * test_count + ["150"]))
    table_data.append(build_row(["", "z [mm]"], ["150"] * test_count + ["150"]))
    
    # Compression area (150 x 150 = 22,500 mm²)
    table_data.append(build_row(["Suprafața de compresiune [mm²]", ""], [str(a) for a in areas] + [str(averages["area"])]))
    
    # Force and strength data
    table_data.append(build_row(["Sarcina de rupere la compresiune [N]", ""], [str(f) if f > 0 else "" for f in forces] + [str(averages["force"]) if averages["force"] > 0 else ""]))
    table_data.append(build_row(["Rezistența de rupere la compresiune [N/mm²]", ""], [str(s) if s > 0 else "" for s in strengths] + [str(averages["strength"]) if averages["strength"] > 0 else ""]))

    # Column widths: 60mm, 14mm for labels, then 18mm for each data column, 18mm for average
    col_widths = [60*mm, 14*mm] + [18*mm] * test_count + [18*mm]
    row_heights = [4.0*mm] * len(table_data)  # Slightly smaller to match Java 12pt

    table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)

    table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.black),

        # Header formatting
        ('FONTNAME', (0, 0), (0, 1), 'DejaVuSans-Bold'),
        ('SPAN', (0, 0), (total_cols-1, 0)),  # First header row
        ('SPAN', (0, 1), (total_cols-1, 1)),  # Second header row
        ('SPAN', (0, 2), (1, 2)),  # Indicativ serie span

        # Data confectionarii and incercarii spans
        ('SPAN', (0, 3), (1, 3)),
        ('SPAN', (2, 3), (total_cols-1, 3)),
        ('SPAN', (0, 4), (1, 4)),
        ('SPAN', (2, 4), (total_cols-1, 4)),

        # Dimensiuni cubului spans - merge the first column across 3 rows
        ('SPAN', (0, 5), (0, 7)),

        # Other spans
        ('SPAN', (0, 8), (1, 8)),  # Compression area
        ('SPAN', (0, 9), (1, 9)),  # Force
        ('SPAN', (0, 10), (1, 10)),  # Strength

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),

        # Thick borders
        ('LINEBEFORE', (0, 0), (0, -1), 1.2, colors.black),   # Left edge
        ('LINEAFTER', (-1, 0), (-1, -1), 1.2, colors.black),  # Right edge
        ('LINEABOVE', (0, 0), (-1, 0), 1.2, colors.black),    # Top edge
        ('LINEBELOW', (0, -1), (-1, -1), 1.2, colors.black),  # Bottom edge
        ('LINEBELOW', (0, 1), (-1, 1), 1.2, colors.black),    # Below second header
        ('LINEBEFORE', (2, 0), (2, -1), 1.2, colors.black),   # Before data columns
    ]))

    doc.build([table])
    print(f"Beam compression PDF generated at: {target_path}")
    return str(target_path)

if __name__ == "__main__":
    with open("concrete_test_data2.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)[0]
    
    processed = process_test_data(sample_data)
    create_pdf_with_reportlab(sample_data, processed)