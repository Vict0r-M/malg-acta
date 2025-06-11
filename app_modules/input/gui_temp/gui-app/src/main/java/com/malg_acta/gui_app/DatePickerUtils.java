package com.malg_acta.gui_app;

import javafx.util.StringConverter;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.Locale;

public class DatePickerUtils {

    
    public static StringConverter<LocalDate> createDatePickerConverter() {
        // Set Romanian locale
        Locale.setDefault(new Locale("ro"));
        
        // Define the date format
        DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("dd.MM.yyyy");
        
        return new StringConverter<LocalDate>() {
            @Override
            public String toString(LocalDate date) {
                return (date != null) ? date.format(dateFormatter) : "";
            }
            
            @Override
            public LocalDate fromString(String string) {
                if (string != null && !string.isEmpty()) {
                    try {
                        return LocalDate.parse(string, dateFormatter);
                    } catch (DateTimeParseException e) {
                        return null;
                    }
                }
                return null;
            }
        };
    }
    
    public static boolean isValidDate(String dateStr) {
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy");
            LocalDate.parse(dateStr, formatter);
            return true;
        } catch (DateTimeParseException e) {
            return false;
        }
    }
    
    public static String formatDate(LocalDate date) {
        if (date == null) return "";
        return date.format(DateTimeFormatter.ofPattern("dd.MM.yyyy"));
    }
    
    public static LocalDate parseDate(String dateStr) {
        if (dateStr == null || dateStr.isEmpty()) return null;
        try {
            return LocalDate.parse(dateStr, DateTimeFormatter.ofPattern("dd.MM.yyyy"));
        } catch (DateTimeParseException e) {
            return null;
        }
    }
}