package com.malg_acta.cli_app;

import java.util.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import java.io.File;
import java.io.IOException;
import java.util.Scanner;

public class InputCLI {
    private static final Scanner scanner = new Scanner(System.in);
    private static final DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy");

    public static void main(String[] args) {
        System.out.println("=== Formular Testare Beton ===");
        System.out.println("1. Rezistenta la Compresiune Cuburi");
        System.out.println("2. Gelivitate Cuburi");
        System.out.println("3. Rezistenta la Compresiune Prisme");
        System.out.println("4. Rezistenta la Incovoiere Prisme");
        System.out.print("Alegeti protocolul (1-4): ");
        int choice = Integer.parseInt(scanner.nextLine());

        String protocol = "";

        switch (choice) {
            case 1:
                protocol = "Rezistenta la Compresiune Cuburi";
                break;
            case 2:
                protocol = "Gelivitate Cuburi";
                break;
            case 3:
                protocol = "Rezistenta la Compresiune Prisme";
                break;
            case 4:
                protocol = "Rezistenta la Incovoiere Prisme";
                break;
        }
        
        System.out.print("Beneficiar: ");
        String client = scanner.nextLine();

        LocalDate samplingDate = null;
        while (samplingDate == null) {
            System.out.print("Data Prelevarii (ZZ.LL.AAAA): ");
            try {
                samplingDate = LocalDate.parse(scanner.nextLine(), dateFormatter);
            } catch (DateTimeParseException e) {
                System.out.println("Format invalid. Reincercati.");
            }
        }

        LocalDate testingDate = LocalDate.now();

        System.out.print("Clasa Betonului: ");
        String concreteClass = scanner.nextLine();

        System.out.print("Indicativ: ");
        String setId = scanner.nextLine();

        System.out.print("Numar Epruvete: ");
        int setSize = Integer.parseInt(scanner.nextLine());

        System.out.print("Imprimare Bon (da/nu): ");
        String printInput = scanner.nextLine();
        boolean shouldPrint = printInput.toLowerCase().equals("da");

        System.out.print("Obiectiv: ");
        String projectTitle = scanner.nextLine();

        System.out.print("Element: ");
        String element = scanner.nextLine();

        System.out.println("Format Bon (ex: PDF, Excel, Word): ");
        String formatInput = scanner.nextLine();
        List<String> outputFormat = Arrays.asList(formatInput.split(","));
        // Trim whitespace from each format
        outputFormat.replaceAll(String::trim);

        System.out.println("\n--- Confirmare ---");
        System.out.printf("Protocol: %s\nClient: %s\nData Prelevarii: %s\nData Testarii: %s\nClasa: %s\nIndicativ: %s\nNumar Epruvete: %d\nImprimare Bon: %s\nFormat Bon: %s\n",
                protocol, client, samplingDate.format(dateFormatter), testingDate.format(dateFormatter), 
                concreteClass, setId, setSize, shouldPrint, outputFormat);
        
        // Confirmation prompt
        System.out.print("\nConfirmati datele? (da/nu): ");
        String confirm = scanner.nextLine().trim().toLowerCase();

        if (confirm.equals("da")) {
            DataClassCLI data = new DataClassCLI(protocol, client, concreteClass, 
                    samplingDate.format(dateFormatter), testingDate.format(dateFormatter), 
                    projectTitle, element, setId, setSize, shouldPrint, outputFormat);
            saveToJson(data);
            System.out.println("Date exportate cu succes.");
        } else {
            System.out.println("Exportul datelor a fost anulat.");
        }   
    }
    
    private static void saveToJson(DataClassCLI data) {
        ObjectMapper mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
        try {
            mapper.writeValue(new File("..\\..\\..\\data\\output_cli.json"), data);
        } catch (IOException e) {
            System.err.println("Eroare la salvarea fisierului JSON: " + e.getMessage());
        }
    }
}