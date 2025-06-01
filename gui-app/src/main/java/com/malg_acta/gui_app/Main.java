package com.malg_acta.gui_app;

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        System.out.println("=== Selectati Interfata ===");
        System.out.println("1. Interfata Linie de Comanda (CLI)");
        System.out.println("2. Interfata Grafica (GUI)");
        System.out.print("Alegeti optiunea (1-2): ");

        Scanner scanner = new Scanner(System.in);
        String option = scanner.nextLine().trim();

        switch (option) {
            case "1":
                InputCLI.main(args);
                break;
            case "2":
                InputGUI.main(args);
                break;
            default:
                System.out.println("Optiune invalida.");
                break;
        }
    }
}
