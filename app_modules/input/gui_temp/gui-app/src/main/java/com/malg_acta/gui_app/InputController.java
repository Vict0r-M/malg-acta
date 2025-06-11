package com.malg_acta.gui_app;

import com.fasterxml.jackson.databind.ObjectMapper;
import javafx.scene.control.*;
import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Stack;

public class InputController {

    private LoggerPanel logger;
    private InputDataManager dataManager;
    
    // Form data
    private List<String> clients = new ArrayList<>();
    private List<String> concrete = new ArrayList<>();
    private final Stack<List<String>> clientHistory = new Stack<>();
    private final Stack<List<String>> concreteHistory = new Stack<>();
    
    public InputController(LoggerPanel logger) {
        this.logger = logger;
        this.dataManager = new InputDataManager(logger);
        loadInitialData();
    }
    
    private void loadInitialData() {
        clients = dataManager.loadClientsFromJson();
        concrete = dataManager.loadConcreteFromJson();
    }
    
    // === Client Management ===
    public void addClient(String newClient, ComboBox<String> clientCombo) {
        if (!newClient.isEmpty() && !clients.contains(newClient)) {
            clientHistory.push(new ArrayList<>(clients));
            clients.add(newClient);
            clientCombo.getItems().add(newClient);
            dataManager.saveClientsToJson(clients);
            logger.logInfo("Client adăugat: " + newClient);
        } else if (clients.contains(newClient)) {
            logger.logError("Client deja existent!");
        }
    }
    
    public void deleteClient(String selectedClient, ComboBox<String> clientCombo) {
        if (clients.contains(selectedClient)) {
            clientHistory.push(new ArrayList<>(clients));
            clients.remove(selectedClient);
            clientCombo.getItems().remove(selectedClient);
            dataManager.saveClientsToJson(clients);
            logger.logInfo("Client șters: " + selectedClient);
        } else {
            logger.logError("Clientul nu există în listă.");
        }
    }
    
    public void undoClientChanges(ComboBox<String> clientCombo) {
        if (!clientHistory.isEmpty()) {
            clients = clientHistory.pop();
            clientCombo.getItems().setAll(clients);
            dataManager.saveClientsToJson(clients);
            logger.logInfo("Ultima modificare a fost anulată.");
        } else {
            logger.logError("Nu există modificări de anulat.");
        }
    }
    
    // === Concrete Management ===
    public void addConcrete(String newConcrete, ComboBox<String> concreteCombo) {
        if (!newConcrete.isEmpty() && !concrete.contains(newConcrete)) {
            concreteHistory.push(new ArrayList<>(concrete));
            concrete.add(newConcrete);
            concreteCombo.getItems().add(newConcrete);
            dataManager.saveConcreteToJson(concrete);
            logger.logInfo("Clasă beton adăugată: " + newConcrete);
        } else if (concrete.contains(newConcrete)) {
            logger.logError("Clasă beton deja existentă!");
        }
    }
    
    public void deleteConcrete(String selectedConcrete, ComboBox<String> concreteCombo) {
        if (concrete.contains(selectedConcrete)) {
            concreteHistory.push(new ArrayList<>(concrete));
            concrete.remove(selectedConcrete);
            concreteCombo.getItems().remove(selectedConcrete);
            dataManager.saveConcreteToJson(concrete);
            logger.logInfo("Clasă beton ștearsă: " + selectedConcrete);
        } else {
            logger.logError("Clasa beton nu există în listă.");
        }
    }
    
    public void undoConcreteChanges(ComboBox<String> concreteCombo) {
        if (!concreteHistory.isEmpty()) {
            concrete = concreteHistory.pop();
            concreteCombo.getItems().setAll(concrete);
            dataManager.saveConcreteToJson(concrete);
            logger.logInfo("Ultima modificare a fost anulată.");
        } else {
            logger.logError("Nu există modificări de anulat.");
        }
    }
    
    // === Form Validation ===
    public boolean validateData(ToggleGroup protocolGroup, ComboBox<String> clientCombo, 
    					   ComboBox<String> concreteClassCombo, DatePicker samplingDatePicker, 
    					   TextArea obiectivArea, TextArea elementArea, 
    					   TextField setIdField, TextField setSizeField, ToggleGroup printGroup,
                           CheckBox pdfCheck, CheckBox excelCheck, CheckBox wordCheck) {
        
        DataValidator validator = new DataValidator(logger);
        boolean valid = validator.validateAllFields(
        		protocolGroup, clientCombo, concreteClassCombo, samplingDatePicker, 
        		obiectivArea, elementArea, setIdField, setSizeField, 
                printGroup, pdfCheck, excelCheck, wordCheck);
        
        if (valid) {
            logger.logInfo("Date validate!");
            saveData(protocolGroup, clientCombo, concreteClassCombo, samplingDatePicker, 
            		obiectivArea, elementArea, setIdField, setSizeField, 
                    printGroup, pdfCheck, excelCheck, wordCheck);
            
        }
        return valid;
    }
    
    private final Object dataLock = new Object();
    private DataClassGUI currentData = null;
    
    private DataClassGUI getData(ToggleGroup protocolGroup, ComboBox<String> clientCombo, ComboBox<String> concreteClassCombo,
    		DatePicker samplingDatePicker, TextArea obiectivArea, TextArea elementArea, TextField setIdField, 
    		TextField setSizeField, ToggleGroup printGroup, CheckBox pdfCheck, CheckBox excelCheck, CheckBox wordCheck) {

		DataClassGUI data = new DataClassGUI();
		data.protocol = ((RadioButton) protocolGroup.getSelectedToggle()).getText();
		data.client = clientCombo.getEditor().getText();
		data.concrete_class = concreteClassCombo.getEditor().getText();
		data.sampling_date = samplingDatePicker.getValue().format(DateTimeFormatter.ofPattern("dd.MM.yyyy"));
		data.testing_date = LocalDate.now().format(DateTimeFormatter.ofPattern("dd.MM.yyyy"));
		data.project_title = obiectivArea.getText();
		data.element = elementArea.getText();
		data.set_id = setIdField.getText();
		data.set_size = Integer.parseInt(setSizeField.getText());		
		data.should_print = ((RadioButton) printGroup.getSelectedToggle()).getText().equals("Da"); 
		
		data.output_format.pdf = pdfCheck.isSelected();
	    data.output_format.excel = excelCheck.isSelected();
	    data.output_format.word = wordCheck.isSelected();
	    
	    // Store the current data in a thread-safe way
	    synchronized (dataLock) {
	        this.currentData = data;
	    }
	    
		return data;
		}
    
    /**
     * Get data from InputController (thread-safe)
     * @return DataClassGUI object with current form data, or null if no data available
     */
    public String getData() {
        synchronized (dataLock) {
            return currentData.toJSON();
        }
    }
    
 // Alternative method if you want to return Object type as in your example
    /**
     * Get data from InputController (thread-safe) - returns Object
     * @return DataClassGUI object as Object, or null if no data available
     */
    public Object getDataAsObject() {
        synchronized (dataLock) {
            return currentData;
        }
    }

    // Method to get data directly from UI components (if you have access to them)
    /**
     * Get current data directly from UI components (thread-safe)
     * Note: This requires the UI components to be passed as parameters
     */
    public DataClassGUI getCurrentData(ToggleGroup protocolGroup, ComboBox<String> clientCombo, ComboBox<String> concreteClassCombo,
    		DatePicker samplingDatePicker, TextArea obiectivArea, TextArea elementArea, TextField setIdField, 
    		TextField setSizeField, ToggleGroup printGroup, CheckBox pdfCheck, CheckBox excelCheck, CheckBox wordCheck) {
    	
        
        synchronized (dataLock) {
            return getData(protocolGroup, clientCombo, concreteClassCombo, samplingDatePicker, 
            		obiectivArea, elementArea, setIdField, setSizeField, 
                    printGroup, pdfCheck, excelCheck, wordCheck);
        }
    }
    
    private void saveData(ToggleGroup protocolGroup, ComboBox<String> clientCombo, ComboBox<String> concreteClassCombo,
    		DatePicker samplingDatePicker, TextArea obiectivArea, TextArea elementArea, TextField setIdField, 
    		TextField setSizeField, ToggleGroup printGroup, CheckBox pdfCheck, CheckBox excelCheck, CheckBox wordCheck) {
        
        DataClassGUI data = getData(protocolGroup, clientCombo, concreteClassCombo, samplingDatePicker, 
        		obiectivArea, elementArea, setIdField, setSizeField, 
                printGroup, pdfCheck, excelCheck, wordCheck);
        
        try {
            ObjectMapper mapper = new ObjectMapper();
            mapper.writerWithDefaultPrettyPrinter().writeValue(new File("..\\..\\..\\data\\output_gui.json"), data);
            logger.logInfo("Datele au fost salvate în fișierul output.json");
        } catch (IOException e) {
            logger.logError("Eroare la salvarea în fișier JSON.");
        }
    }
    
    // Getters
    public List<String> getClients() { return clients; }
    public List<String> getConcrete() { return concrete; }
}


