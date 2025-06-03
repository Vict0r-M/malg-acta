package com.malg_acta.gui_app;

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

        System.out.print("Clasa Betonului: ");
        String concreteClass = scanner.nextLine();

        System.out.print("Indicativ: ");
        String setId = scanner.nextLine();

        System.out.print("Numar Epruvete: ");
        String setSize = scanner.nextLine();

        System.out.print("Imprimare Bon (da/nu): ");
        String printOption = scanner.nextLine();

        System.out.print("Obiectiv: ");
        String obiectiv = scanner.nextLine();

        System.out.print("Element: ");
        String element = scanner.nextLine();

        System.out.println("Format Bon (ex: PDF, Excel, Word): ");
        String format = scanner.nextLine();

        System.out.println("\n--- Confirmare ---");
        System.out.printf("Protocol: %s\nClient: %s\nData: %s\nClasa: %s\nIndicativ: %s\nNumar Epruvete: %s\nImprimare Bon: %s\nFormat Bon: %s\n",
        		protocol, client, samplingDate.format(dateFormatter), concreteClass, setId, setSize, printOption, format);
        
        // Confirmation prompt
        System.out.print("\nConfirmati datele? (da/nu): ");
        String confirm = scanner.nextLine().trim().toLowerCase();

        if (confirm.equals("da")) {
            System.out.println("Date exportate cu succes.");
            FormDataCLI data = new FormDataCLI(protocol, client, samplingDate.format(dateFormatter), concreteClass, setId, setSize, printOption, obiectiv, element, format);
            saveToJson(data);

        } else {
            System.out.println("Exportul datelor a fost anulat.");
        }   
    }
    
    private static void saveToJson(FormDataCLI data) {
        ObjectMapper mapper = new ObjectMapper().enable(SerializationFeature.INDENT_OUTPUT);
        try {
            mapper.writeValue(new File("formular.json"), data);
        } catch (IOException e) {
            System.err.println("Eroare la salvarea fisierului JSON: " + e.getMessage());
        }
    }
}


