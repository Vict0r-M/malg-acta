import org.apache.poi.ss.usermodel.*;
import org.apache.poi.ss.util.CellRangeAddress;
import org.apache.poi.xssf.usermodel.*;

import java.io.*;
import java.util.*;

public class BeamFlexural {
    public static void main(String[] args) throws Exception {
        File csvFile = new File("press_data.csv");

        XSSFWorkbook workbook = new XSSFWorkbook();
        XSSFSheet sheet = workbook.createSheet("Concrete Test");
        DataFormat format = workbook.createDataFormat();

        // Fonts and styles
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

        // Read data from parser
        BufferedReader reader = new BufferedReader(new FileReader(csvFile));
        String indicativSerie = reader.readLine().split(",")[1];
        String dataConfectionarii = reader.readLine().split(",")[1];
        String dataIncercarii = reader.readLine().split(",")[1];

        List<double[]> dataRows = new ArrayList<>();

        // Greutate row
        String[] greutateTokens = reader.readLine().split(",");
        double[] greutateData = new double[3];
        for (int i = 0; i < 3; i++) {
            greutateData[i] = Double.parseDouble(greutateTokens[i + 1]);
        }
        dataRows.add(greutateData);

        // kN row
        String[] kNTokens = reader.readLine().split(",");
        double[] kNData = new double[3];
        for (int i = 0; i < 3; i++) {
            kNData[i] = Double.parseDouble(kNTokens[i + 1]);
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

        // Cube dimensions - fixed
        int dimStartRow = 5;
        String[] dimLabels = {"x [mm]", "y [mm]", "z [mm]"};
        double[] dimValues = {150, 150, 600};

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
                cell.setCellValue(dimValues[i]); 
                cell.setCellStyle(centered);
            }


            XSSFCell avgCell = row.createCell(5);
            avgCell.setCellFormula(String.format("AVERAGE(C%d:E%d)", dimStartRow + i + 1, dimStartRow + i + 1));
            avgCell.setCellStyle(centered);
        }

        // Compression force
        int row9 = 8;
        XSSFRow forceRow = sheet.createRow(row9);
        forceRow.createCell(0).setCellValue("Sarcina de rupere la compresiune [N]");
        forceRow.getCell(0).setCellStyle(centered);
        sheet.addMergedRegion(new CellRangeAddress(row9, row9, 0, 1));
        for (int i = 0; i < 3; i++) {
            XSSFCell cell = forceRow.createCell(i + 2);
            cell.setCellValue(dataRows.get(1)[i]);
            cell.setCellStyle(centered);
        }
        XSSFCell forceAvg = forceRow.createCell(5);
        forceAvg.setCellFormula("AVERAGE(C9:E9)");
        forceAvg.setCellStyle(intStyle);

        // Strength
        int row10 = 9;
        XSSFRow strengthRow = sheet.createRow(row10);
        strengthRow.createCell(0).setCellValue("Rezistența de rupere la compresiune [N/mm²]");
        strengthRow.getCell(0).setCellStyle(centered);
        sheet.addMergedRegion(new CellRangeAddress(row10, row10, 0, 1));
        for (int i = 0; i < 3; i++) {
            char col = (char) ('C' + i);
            XSSFCell cell = strengthRow.createCell(i + 2);
            // 150x150 = 22500 mm² area
            cell.setCellFormula(String.format("PRODUCT(%c9,450/POWER(%c6,3))", col,col));
            cell.setCellStyle(twoDecimalStyle);
        }
        XSSFCell strengthAvg = strengthRow.createCell(5);
        strengthAvg.setCellFormula("AVERAGE(C10:E10)");
        strengthAvg.setCellStyle(twoDecimalStyle);

        // Borders
        for (int r = 0; r <= row10; r++) {
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
                if (r == row10) style.setBorderBottom(BorderStyle.THICK);
                if (c == 0 || c == 2) style.setBorderLeft(BorderStyle.THICK);
                if (c == 5) style.setBorderRight(BorderStyle.THICK);
                cell.setCellStyle(style);
            }
        }

        // Row heights
        float targetHeightPerRow = 16f;
        for (int i = 0; i <= row10; i++) {
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

        // Output file
        try (FileOutputStream out = new FileOutputStream("..\\..\\data\\receipts\\excel_receipts\\beam_flexural_receipt.xlsx")) {
            workbook.write(out);
        }
        workbook.close();

        System.out.println("receipt created");
    }
}
