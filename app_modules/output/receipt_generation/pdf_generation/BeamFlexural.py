import json
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVuSans font
pdfmetrics.registerFont(TTFont('DejaVuSans', r"receipt_generation\pdf_generation\DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont('DejaVuSans-Bold', r"receipt_generation\pdf_generation\DejaVuSans-Bold.ttf"))

def process_test_data(raw_data):
    """Process raw test data for beam flexural testing"""
    tests = raw_data["tests"]
    weights = [round(float(test["scale_data"]) / 1000, 2) for test in tests]
    forces = [round(float(test["compression_data"]["kN"]) * 1000, 2) for test in tests]
    
    # Calculate strengths using the Java formula: force * 450 / (dimension^3)
    # Where dimension is 150mm for cube side
    dimension = 150  # mm
    strengths = [round(force * 450 / (dimension ** 3), 2) for force in forces]

    return {
        "weights": weights,
        "forces": forces,
        "strengths": strengths,
        "averages": {
            "weight": round(sum(weights) / len(weights), 2),
            "force": round(sum(forces) / len(forces), 2),
            "strength": round(sum(strengths) / len(strengths), 2),
        }
    }

def build_row(label_parts, values, label_width=2):
    """Helper function to build table rows"""
    return label_parts + values

def create_pdf_with_reportlab(raw_data, processed_data):
    """Create compact PDF report for beam flexural testing"""
    set_id = raw_data["set_id"]
    sampling_date = raw_data["sampling_date"]
    testing_date = raw_data["testing_date"]
    test_count = len(raw_data["tests"])
    total_cols = 2 + test_count + 1  # 2 label columns + test values + average

    weights = processed_data["weights"]
    forces = processed_data["forces"]
    strengths = processed_data["strengths"]
    averages = processed_data["averages"]

    filename = "beam_flexural.pdf"
    target_path = os.path.join("..", "..", "data", "receipts", "pdf_receipts", filename)

    doc = SimpleDocTemplate(target_path, pagesize=A4, topMargin=10*mm, bottomMargin=10*mm,
                            leftMargin=10*mm, rightMargin=10*mm)

    table_data = []

    # Header rows (merged across total columns)
    table_data.append(["PILOT 4, MODEL 50 - C4642 Nr. Serial"] + [""] * (total_cols - 1))
    table_data.append(["Rezultatele încercării:"] + [""] * (total_cols - 1))
    table_data.append([f"Indicativ serie {set_id}", ""] + [f"{i+1}" for i in range(test_count)] + ["Media"])

    # Data rows - compact format like Java version
    table_data.append(build_row(["Data confecționării", ""], [sampling_date] * test_count + [sampling_date]))
    table_data.append(build_row(["Data încercării", ""], [testing_date] * test_count + [testing_date]))
    
    # Cube dimensions - single row with x, y, z merged
    table_data.append(build_row(["Dimensiunile cubului [mm]", "x [mm]"], ["150"] * test_count + ["150"]))
    table_data.append(build_row(["", "y [mm]"], ["150"] * test_count + ["150"]))
    table_data.append(build_row(["", "z [mm]"], ["600"] * test_count + ["600"]))
    
    # Force and strength data
    table_data.append(build_row(["Sarcina de rupere la compresiune [N]", ""], [str(f) for f in forces] + [str(averages["force"])]))
    table_data.append(build_row(["Rezistența de rupere la compresiune [N/mm²]", ""], [str(s) for s in strengths] + [str(averages["strength"])]))

    col_widths = [60*mm, 14*mm] + [18*mm] * test_count + [18*mm]
    row_heights = [4.8*mm] * len(table_data)

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

        # Force and strength spans
        ('SPAN', (0, 8), (1, 8)),
        ('SPAN', (0, 9), (1, 9)),

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
    print(f"Compact beam flexural PDF generated at: {target_path}")
    return target_path

def read_csv_data(csv_file_path):
    """Read data from CSV file in the format expected by Java code"""
    data = {}
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        # Parse CSV structure matching Java code
        data['set_id'] = lines[0].strip().split(',')[1]
        data['sampling_date'] = lines[1].strip().split(',')[1]
        data['testing_date'] = lines[2].strip().split(',')[1]
        
        # Parse weight data (line 4, convert from grams to kg)
        weight_tokens = lines[3].strip().split(',')
        weights_kg = [float(token) for token in weight_tokens[1:4]]
        
        # Parse kN data (line 5)
        kn_tokens = lines[4].strip().split(',')
        kn_values = [float(token) for token in kn_tokens[1:4]]
        
        # Build tests structure
        data['tests'] = []
        for i in range(3):
            test_data = {
                'scale_data': str(int(weights_kg[i] * 1000)),  # Convert back to grams
                'compression_data': {
                    'kN': str(kn_values[i]),
                    'MPa': 'calculated'  # Not used in this calculation
                }
            }
            data['tests'].append(test_data)
    
    return data

if __name__ == "__main__":
    with open("concrete_test_data.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)[0]
    
    processed = process_test_data(sample_data)
    create_pdf_with_reportlab(sample_data, processed)