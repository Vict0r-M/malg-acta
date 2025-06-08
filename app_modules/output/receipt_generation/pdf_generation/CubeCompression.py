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
    tests = raw_data["tests"]
    weights = [round(float(test["scale_data"]) / 1000, 2) for test in tests]
    forces = [round(float(test["compression_data"]["kN"]) * 1000, 2) for test in tests]
    pressures = [round(float(test["compression_data"]["MPa"]), 2) for test in tests]
    cube_volume = 0.003375
    densities = [round(weight / cube_volume, 2) for weight in weights]

    return {
        "weights": weights,
        "forces": forces,
        "pressures": pressures,
        "densities": densities,
        "averages": {
            "weight": round(sum(weights) / len(weights), 2),
            "force": round(sum(forces) / len(forces), 2),
            "pressure": round(sum(pressures) / len(pressures), 2),
            "density": round(sum(densities) / len(densities), 2),
        }
    }

def build_row(label_parts, values, label_width=4):
    return label_parts + values

def create_pdf_with_reportlab(raw_data, processed_data):
    client = raw_data["client"]
    set_id = raw_data["set_id"]
    sampling_date = raw_data["sampling_date"]
    testing_date = raw_data["testing_date"]
    test_count = len(raw_data["tests"])
    total_cols = 4 + test_count + 1  # 4 label columns + test values + average

    weights = processed_data["weights"]
    forces = processed_data["forces"]
    pressures = processed_data["pressures"]
    densities = processed_data["densities"]
    averages = processed_data["averages"]

    filename = "cube_compression.pdf"
    target_path = os.path.join("..", "..", "data", "receipts", "pdf_receipts", filename)

    doc = SimpleDocTemplate(target_path, pagesize=A4, topMargin=10*mm, bottomMargin=10*mm,
                            leftMargin=10*mm, rightMargin=10*mm)

    table_data = []

    # Header rows (merged across total columns)
    table_data.append(["PILOT 4, Model 50 - C4642 Serial Nr. 12010780"] + [""] * (total_cols - 1))
    table_data.append(["Rezultatele încercării:"] + [""] * (total_cols - 1))
    table_data.append(["Indicativ Proba", "", "", ""] + [f"{i+1}" for i in range(test_count)] + ["Media"])

    # Data rows
    table_data.append(build_row(["Data confecționării", "", "", ""], [sampling_date] * test_count + [sampling_date]))
    table_data.append(build_row(["Data încercării", "", "", ""], [testing_date] * test_count + [testing_date]))
    table_data.append(build_row(["Dimensiunile cubului", "", "", "x [mm]"], ["150"] * test_count + ["150"]))
    table_data.append(build_row(["", "", "", "y [mm]"], ["150"] * test_count + ["150"]))
    table_data.append(build_row(["", "", "", "z [mm]"], ["150"] * test_count + ["150"]))
    table_data.append(build_row(["Suprafața de compresiune [mm²]", "", "", ""], ["22500"] * test_count + ["22500"]))
    table_data.append(build_row(["Greutatea cubului [Kg]", "", "", ""], [str(w) for w in weights] + [str(averages["weight"])]))
    table_data.append(build_row(["Densitatea specifică aparentă [Kg/m³]", "", "", ""], [str(d) for d in densities] + [str(averages["density"])]))
    table_data.append(build_row(["Sarcina de rupere la compresiune [N]", "", "", ""], [str(f) for f in forces] + [str(averages["force"])]))
    table_data.append(build_row(["Rezistența de rupere la compresiune [N/mm²]", "", "", ""], [str(p) for p in pressures] + [str(averages["pressure"])]))

    col_widths = [20*mm] * total_cols
    row_heights = [5.5*mm] * len(table_data)

    table = Table(table_data, colWidths=col_widths, rowHeights=row_heights)

    table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.black),

        # Merge header rows
        ('SPAN', (0, 0), (total_cols-1, 0)),
        ('SPAN', (0, 1), (total_cols-1, 1)),
        ('SPAN', (0, 2), (3, 2)),

        # Dimensiuni cubului spans
        ('SPAN', (0, 5), (3, 7)),

        # Other multi-column labels
        ('SPAN', (0, 3), (3, 3)),
        ('SPAN', (0, 4), (3, 4)),
        ('SPAN', (0, 8), (3, 8)),
        ('SPAN', (0, 9), (3, 9)),
        ('SPAN', (0, 10), (3, 10)),
        ('SPAN', (0, 11), (3, 11)),
        ('SPAN', (0, 12), (3, 12)),

        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LEFTPADDING', (0, 0), (-1, -1), 2),
        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
    ]))

    doc.build([table])
    print(f"PDF generated at: {target_path}")
    return target_path

if __name__ == "__main__":
    with open("concrete_test_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)[0]
    processed = process_test_data(data)
    create_pdf_with_reportlab(data, processed)
