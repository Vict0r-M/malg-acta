package com.malg_acta.gui_app;

import javafx.scene.control.*;
import java.time.format.DateTimeParseException;

public class DataValidator {

    private LoggerPanel logger;
    
    public DataValidator(LoggerPanel logger) {
        this.logger = logger;
    }
    
    public boolean validateAllFields(ToggleGroup protocolGroup, ComboBox<String> clientCombo, 
			   ComboBox<String> concreteClassCombo, DatePicker samplingDatePicker, 
			   TextArea obiectivArea, TextArea elementArea, 
			   TextField setIdField, TextField setSizeField, ToggleGroup printGroup,
            CheckBox pdfCheck, CheckBox excelCheck, CheckBox wordCheck) {
        
        boolean valid = true;
        
        // Protocol validation
        if (protocolGroup.getSelectedToggle() == null) {
            logger.logError("Trebuie selectat un protocol.");
            valid = false;
        }
       
        // Client validation
        if (clientCombo.getEditor().getText().trim().isEmpty()) {
            logger.logError("Trebuie selectat sau introdus un beneficiar.");
            valid = false;
        }
        
        // Date validation
        if (samplingDatePicker.getValue() == null) {
            logger.logError("Trebuie selectată o dată validă pentru prelevare.");
            valid = false;
        }
        
        // Concrete class validation
        if (concreteClassCombo.getEditor().getText().trim().isEmpty()) {
            logger.logError("Trebuie selectată sau introdusă o clasă de beton.");
            valid = false;
        }
        
        // Set ID validation
        if (setIdField.getText().trim().isEmpty()) {
            logger.logError("Indicativul trebuie completat.");
            valid = false;
        }
        
        // Set size validation
        if (!validateSetSize(setSizeField.getText().trim())) {
            valid = false;
        }
        
        // Print option validation
        if (printGroup.getSelectedToggle() == null) {
            logger.logError("Trebuie selectată opțiunea de imprimare bon.");
            valid = false;
        }
        
        // Output format validation
        if (!pdfCheck.isSelected() && !excelCheck.isSelected() && !wordCheck.isSelected()) {
            logger.logError("Trebuie selectat cel puțin un format de bon.");
            valid = false;
        }
        
        return valid;
    }
    
    private boolean validateSetSize(String sizeText) {
        try {
            int size = Integer.parseInt(sizeText);
            if (size <= 0) {
                logger.logError("Numărul de epruvete trebuie să fie un număr mai mare decât 0.");
                return false;
            }
            return true;
        } catch (NumberFormatException e) {
            logger.logError("Numărul de epruvete trebuie să fie un număr valid.");
            return false;
        }
    }
}
