import org.apache.poi.ss.usermodel.*;
import org.apache.poi.ss.util.CellRangeAddress;
import org.apache.poi.xssf.usermodel.*;

import java.io.*;
import java.nio.file.*;
import java.util.*;

public class CubeCompression {
    public static void main(String[] args) throws Exception {
        File csvFile = new File("press_data.csv");

        XSSFWorkbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = workbook.createSheet("Concrete Test");
        DataFormat format = workbook.createDataFormat();

        // Fonts and styles
        XSSFFont arial9 = workbook.createFont();
        arial9.setFontName("Arial");
        arial9.setFontHeightInPoints((short) 9);

        XSSFFont boldFont = workbook.createFont();
        boldFont.setBold(true);

        XSSFCellStyle boldStyle = workbook.createCellStyle();
        boldStyle.setFont(boldFont);

        XSSFCellStyle centeredBold = workbook.createCellStyle();
        centeredBold.setFont(boldFont);
        centeredBold.setAlignment(HorizontalAlignment.CENTER);
        centeredBold.setVerticalAlignment(VerticalAlignment.CENTER);
        centeredBold.setWrapText(true);

        XSSFCellStyle centered = workbook.createCellStyle();
        centered.setAlignment(HorizontalAlignment.CENTER);
        centered.setVerticalAlignment(VerticalAlignment.CENTER);
        centered.setWrapText(true);

        XSSFCellStyle intStyle = workbook.createCellStyle();
        intStyle.setAlignment(HorizontalAlignment.CENTER);
        intStyle.setVerticalAlignment(VerticalAlignment.CENTER);
        intStyle.setWrapText(true);
        intStyle.setDataFormat(format.getFormat("0"));

        XSSFCellStyle oneDecimalStyle = workbook.createCellStyle();
        oneDecimalStyle.setAlignment(HorizontalAlignment.CENTER);
        oneDecimalStyle.setVerticalAlignment(VerticalAlignment.CENTER);
        oneDecimalStyle.setWrapText(true);
        oneDecimalStyle.setDataFormat(format.getFormat("0.0"));

        XSSFCellStyle twoDecimalStyle = workbook.createCellStyle();
        twoDecimalStyle.setAlignment(HorizontalAlignment.CENTER);
        twoDecimalStyle.setVerticalAlignment(VerticalAlignment.CENTER);
        twoDecimalStyle.setWrapText(true);
        twoDecimalStyle.setDataFormat(format.getFormat("0.00"));

        XSSFCellStyle threeDecimalStyle = workbook.createCellStyle();
        threeDecimalStyle.setAlignment(HorizontalAlignment.CENTER);
        threeDecimalStyle.setVerticalAlignment(VerticalAlignment.CENTER);
        threeDecimalStyle.setWrapText(true);
        threeDecimalStyle.setDataFormat(format.getFormat("0.000"));

        // Read data from CSV file
        BufferedReader reader = new BufferedReader(new FileReader(csvFile));
        String indicativSerie = reader.readLine().split(",")[1];
        String dataConfectionarii = reader.readLine().split(",")[1];
        String dataIncercarii = reader.readLine().split(",")[1];

        List<double[]> dataRows = new ArrayList<>();

        // Greutate row - handle empty cells
        String[] greutateTokens = reader.readLine().split(",");
        double[] greutateData = new double[3];
        for (int i = 0; i < 3; i++) {
            if (i + 1 < greutateTokens.length && !greutateTokens[i + 1].trim().isEmpty()) {
                try {
                    greutateData[i] = Double.parseDouble(greutateTokens[i + 1].trim());
                } catch (NumberFormatException e) {
                    greutateData[i] = Double.NaN;
                }
            } else {
                greutateData[i] = Double.NaN;
            }
        }
        dataRows.add(greutateData);

        // kN row - handle empty cells
        String[] kNTokens = reader.readLine().split(",");
        double[] kNData = new double[3];
        for (int i = 0; i < 3; i++) {
            if (i + 1 < kNTokens.length && !kNTokens[i + 1].trim().isEmpty()) {
                try {
                    kNData[i] = Double.parseDouble(kNTokens[i + 1].trim());
                } catch (NumberFormatException e) {
                    kNData[i] = Double.NaN;
                }
            } else {
                kNData[i] = Double.NaN;
            }
        }
        dataRows.add(kNData);

        reader.close();

        // Header content
        String[][] headerTable = {
            {"PILOT 4, MODEL 50 - C4642 Nr. Serial", "", "", "", "", ""},
            {"Rezultatele încercării:", "", "", "", "", ""},
            {"", "", "", "", "", ""},
            {"Data confecționării", "", dataConfectionarii, dataConfectionarii, dataConfectionarii, dataConfectionarii},
            {"Data încercării", "", dataIncercarii, dataIncercarii, dataIncercarii, dataIncercarii}
        };

        for (int rowIdx = 0; rowIdx < headerTable.length; rowIdx++) {
            XSSFRow row = sheet.createRow(rowIdx);

            if (rowIdx == 2) {
                sheet.addMergedRegion(new CellRangeAddress(rowIdx, rowIdx, 0, 1));
                XSSFCell indicativCell = row.createCell(0);
                indicativCell.setCellValue("Indicativ serie " + indicativSerie);
                indicativCell.setCellStyle(centered);

                String[] labels = {"1", "2", "3", "Media"};
                for (int i = 0; i < labels.length; i++) {
                    XSSFCell cell = row.createCell(i + 2);
                    cell.setCellValue(labels[i]);
                    cell.setCellStyle(centered);
                }
                continue;
            }

            for (int colIdx = 0; colIdx < headerTable[rowIdx].length; colIdx++) {
                XSSFCell cell = row.createCell(colIdx);
                cell.setCellValue(headerTable[rowIdx][colIdx]);
                cell.setCellStyle(rowIdx <= 1 ? boldStyle : centered);
            }

            if (rowIdx == 0 || rowIdx == 1) {
                sheet.addMergedRegion(new CellRangeAddress(rowIdx, rowIdx, 0, 5));
            }
            if (rowIdx == 3 || rowIdx == 4) {
                sheet.addMergedRegion(new CellRangeAddress(rowIdx, rowIdx, 0, 1));
                sheet.addMergedRegion(new CellRangeAddress(rowIdx, rowIdx, 2, 5));
            }
        }

        // Thick border below second row
        XSSFRow secondRow = sheet.getRow(1);
        for (int col = 0; col <= 5; col++) {
            XSSFCell cell = secondRow.getCell(col);
            if (cell == null) cell = secondRow.createCell(col);
            XSSFCellStyle style = workbook.createCellStyle();
            style.cloneStyleFrom(cell.getCellStyle());
            style.setBorderBottom(BorderStyle.THICK);
            cell.setCellStyle(style);
        }

        // Cube dimensions
        int dimStartRow = 5;
        String[] dimLabels = {"x [mm]", "y [mm]", "z [mm]"};
        double[] dimValues = {150, 150, 150};

        sheet.addMergedRegion(new CellRangeAddress(dimStartRow, dimStartRow + 2, 0, 0));
        for (int i = 0; i < 3; i++) {
            XSSFRow row = sheet.createRow(dimStartRow + i);
            if (i == 0) {
                XSSFCell cell = row.createCell(0);
                cell.setCellValue("Dimensiunile cubului [mm]");
                cell.setCellStyle(centered);
            } else {
                row.createCell(0).setCellStyle(centered);
            }

            XSSFCell dimCell = row.createCell(1);
            dimCell.setCellValue(dimLabels[i]);
            dimCell.setCellStyle(centered);

            for (int j = 0; j < 3; j++) {
                XSSFCell cell = row.createCell(j + 2);
                cell.setCellValue(dimValues[j]);
                cell.setCellStyle(centered);
            }

            XSSFCell avgCell = row.createCell(5);
            avgCell.setCellFormula(String.format("AVERAGE(C%d:E%d)", dimStartRow + i + 1, dimStartRow + i + 1));
            avgCell.setCellStyle(centered);
        }

        // Compressive area
        int row9 = 8;
        XSSFRow areaRow = sheet.createRow(row9);
        areaRow.createCell(0).setCellValue("Suprafața de compresiune [mm²]");
        areaRow.getCell(0).setCellStyle(centered);
        sheet.addMergedRegion(new CellRangeAddress(row9, row9, 0, 1));
        for (int i = 0; i < 3; i++) {
            char col = (char) ('C' + i);
            XSSFCell cell = areaRow.createCell(i + 2);
            cell.setCellFormula("PRODUCT(" + col + "6:" + col + "7)");
            cell.setCellStyle(centered);
        }
        XSSFCell areaAvg = areaRow.createCell(5);
        areaAvg.setCellFormula("AVERAGE(C9:E9)");
        areaAvg.setCellStyle(centered);

        // Cube weight
        int row10 = 9;
        XSSFRow weightRow = sheet.createRow(row10);
        weightRow.createCell(0).setCellValue("Greutatea cubului [kg]");
        weightRow.getCell(0).setCellStyle(centered);
        sheet.addMergedRegion(new CellRangeAddress(row10, row10, 0, 1));
        for (int i = 0; i < 3; i++) {
            XSSFCell cell = weightRow.createCell(i + 2);
            if (!Double.isNaN(dataRows.get(0)[i])) {
                cell.setCellValue(dataRows.get(0)[i]);
                cell.setCellStyle(threeDecimalStyle);
            } else {
                cell.setCellStyle(centered);
            }
        }
        XSSFCell weightAvg = weightRow.createCell(5);
        weightAvg.setCellFormula("AVERAGE(C10:E10)");
        weightAvg.setCellStyle(threeDecimalStyle);

        // Density
        int row11 = 10;
        XSSFRow densityRow = sheet.createRow(row11);
        densityRow.createCell(0).setCellValue("Densitatea specifică aparentă [kg/m³]");
        densityRow.getCell(0).setCellStyle(centered);
        sheet.addMergedRegion(new CellRangeAddress(row11, row11, 0, 1));
        for (int i = 0; i < 3; i++) {
            char col = (char) ('C' + i);
            XSSFCell cell = densityRow.createCell(i + 2);
            if (!Double.isNaN(dataRows.get(0)[i])) {
                cell.setCellFormula(String.format("%c10/PRODUCT(%c6:%c8)*POWER(10,9)", col, col, col));
                cell.setCellStyle(oneDecimalStyle);
            } else {
                cell.setCellStyle(centered);
            }
        }
        XSSFCell densityAvg = densityRow.createCell(5);
        densityAvg.setCellFormula("AVERAGE(C11:E11)");
        densityAvg.setCellStyle(oneDecimalStyle);

        // Compression force
        int row12 = 11;
        XSSFRow forceRow = sheet.createRow(row12);
        forceRow.createCell(0).setCellValue("Sarcina de rupere la compresiune [N]");
        forceRow.getCell(0).setCellStyle(centered);
        sheet.addMergedRegion(new CellRangeAddress(row12, row12, 0, 1));
        for (int i = 0; i < 3; i++) {
            XSSFCell cell = forceRow.createCell(i + 2);
            if (!Double.isNaN(dataRows.get(1)[i])) {
                cell.setCellValue(dataRows.get(1)[i]);
                cell.setCellStyle(centered);
            } else {
                cell.setCellStyle(centered);
            }
        }
        XSSFCell forceAvg = forceRow.createCell(5);
        forceAvg.setCellFormula("AVERAGE(C12:E12)");
        forceAvg.setCellStyle(intStyle);

        // Strength
        int row13 = 12;
        XSSFRow strengthRow = sheet.createRow(row13);
        strengthRow.createCell(0).setCellValue("Rezistența de rupere la compresiune [N/mm²]");
        strengthRow.getCell(0).setCellStyle(centered);
        sheet.addMergedRegion(new CellRangeAddress(row13, row13, 0, 1));
        for (int i = 0; i < 3; i++) {
            char col = (char) ('C' + i);
            XSSFCell cell = strengthRow.createCell(i + 2);
            if (!Double.isNaN(dataRows.get(1)[i])) {
                cell.setCellFormula(String.format("%c12/%c9", col, col));
                cell.setCellStyle(twoDecimalStyle);
            } else {
                cell.setCellStyle(centered);
            }
        }
        XSSFCell strengthAvg = strengthRow.createCell(5);
        strengthAvg.setCellFormula("AVERAGE(C13:E13)");
        strengthAvg.setCellStyle(twoDecimalStyle);

        // Borders
        for (int r = 0; r <= row13; r++) {
            XSSFRow row = sheet.getRow(r);
            if (row == null) continue;
            for (int c = 0; c <= 5; c++) {
                XSSFCell cell = row.getCell(c);
                if (cell == null) {
                    cell = row.createCell(c);
                    cell.setCellStyle(centered);
                }
                XSSFCellStyle style = workbook.createCellStyle();
                style.cloneStyleFrom(cell.getCellStyle());
                if (r == 0) style.setBorderTop(BorderStyle.THICK);
                if (r == row13) style.setBorderBottom(BorderStyle.THICK);
                if (c == 0 || c == 2) style.setBorderLeft(BorderStyle.THICK);
                if (c == 5) style.setBorderRight(BorderStyle.THICK);
                cell.setCellStyle(style);
            }
        }

        float targetHeightPerRow = 12f;
        for (int i = 0; i <= row13; i++) {
            XSSFRow row = sheet.getRow(i);
            if (row != null) {
                row.setHeightInPoints(targetHeightPerRow);
            }
        }

        // Column widths
        sheet.setColumnWidth(0, 28 * 256);
        sheet.setColumnWidth(1, 14 * 256);
        sheet.setColumnWidth(2, 10 * 256);
        sheet.setColumnWidth(3, 10 * 256);
        sheet.setColumnWidth(4, 10 * 256);
        sheet.setColumnWidth(5, 12 * 256);

        // Create cross-platform output path
        Path currentDir = Paths.get(System.getProperty("user.dir"));
        Path outputDir = currentDir.resolve("data").resolve("receipts").resolve("excel_receipts");
        
        // Create directories if they don't exist
        Files.createDirectories(outputDir);
        
        Path outputFile = outputDir.resolve("cube_compression_receipt.xlsx");

        // Output file
        try (FileOutputStream out = new FileOutputStream(outputFile.toFile())) {
            workbook.write(out);
        }
        workbook.close();

        System.out.println("Excel receipt created at: " + outputFile.toString());
    }
}