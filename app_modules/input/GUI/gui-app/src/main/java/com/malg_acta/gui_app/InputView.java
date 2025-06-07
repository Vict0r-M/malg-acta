package com.malg_acta.gui_app;

import javafx.collections.FXCollections;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.control.*;
import javafx.scene.layout.*;

public class InputView {

	private AppController appController;
    private InputController controller;
    private LoggerPanel logger;
    private ComboBoxHelper comboBoxHelper;
    
    private ToggleGroup protocolGroup;
    private ComboBox<String> clientCombo;
    private DatePicker samplingDatePicker;
    private ComboBox<String> concreteClassCombo;
    
    // UI Components
    private TextArea obiectivArea = new TextArea();
    private TextArea elementArea = new TextArea();
    
    public InputView(InputController controller, LoggerPanel logger, AppController appController) {
        this.controller = controller;
        this.logger = logger;
        this.comboBoxHelper = new ComboBoxHelper(controller);
        this.appController = appController;
    }
    
    public GridPane createLayout() {
        GridPane formGrid = new GridPane();
        formGrid.setHgap(40);
        formGrid.setVgap(10);
        formGrid.setAlignment(Pos.TOP_LEFT);
        
        // Setup column constraints
        ColumnConstraints col1 = new ColumnConstraints();
        col1.setPercentWidth(50);
        ColumnConstraints col2 = new ColumnConstraints();
        col2.setPercentWidth(50);
        formGrid.getColumnConstraints().addAll(col1, col2);
        
        // Create left and right grids
        GridPane leftGrid = createLeftGrid();
        GridPane rightGrid = createRightGrid();
        
        formGrid.add(leftGrid, 0, 0);
        formGrid.add(rightGrid, 1, 0);
        
        return formGrid;
    }
    
    private GridPane createLeftGrid() {
        GridPane leftGrid = new GridPane();
        leftGrid.setVgap(10);
        int row = 0;
        
        // Protocol section
        Label protocolLabel = new Label("Protocol pentru:");
        ToggleGroup protocolGroup = new ToggleGroup();
        RadioButton cubeCompression = new RadioButton("Rezistență la Compresiune Cuburi");
        RadioButton cubeFrost = new RadioButton("Gelivitate Cuburi");
        RadioButton beamCompression = new RadioButton("Rezistență la Compresiune Prisme");
        RadioButton beamFlexural = new RadioButton("Rezistență la Încovoiere Prisme");
        
        cubeCompression.setToggleGroup(protocolGroup);
        cubeFrost.setToggleGroup(protocolGroup);
        beamCompression.setToggleGroup(protocolGroup);
        beamFlexural.setToggleGroup(protocolGroup);
        
        VBox protocolBox = new VBox(5, cubeCompression, cubeFrost, beamCompression, beamFlexural);
        
        leftGrid.add(protocolLabel, 0, row);
        leftGrid.add(protocolBox, 0, ++row);
        
        // Client section
        Label clientLabel = new Label("Beneficiar:");
        ComboBox<String> clientCombo = new ComboBox<>(FXCollections.observableArrayList(controller.getClients()));
        clientCombo.setEditable(true);
        comboBoxHelper.setupComboBox(clientCombo, "clients");
        
        Button addClientButton = new Button("Adaugă Client");
        Button deleteClientButton = new Button("Șterge Client");
        Button undoClientButton = new Button("Undo");
        
        setupClientButtons(addClientButton, deleteClientButton, undoClientButton, clientCombo);
        HBox clientButtons = new HBox(10, addClientButton, deleteClientButton, undoClientButton);
        
        leftGrid.add(clientLabel, 0, ++row);
        leftGrid.add(clientCombo, 0, ++row);
        leftGrid.add(clientButtons, 0, ++row);
        
        // Date section
        Label samplingDateLabel = new Label("Data Prelevării:");
        DatePicker samplingDatePicker = new DatePicker();
        samplingDatePicker.setConverter(DatePickerUtils.createDatePickerConverter());
        
        leftGrid.add(samplingDateLabel, 0, ++row);
        leftGrid.add(samplingDatePicker, 0, ++row);
        
        // Concrete class section
        Label concreteClassLabel = new Label("Clasa Betonului:");
        ComboBox<String> concreteClassCombo = new ComboBox<>(FXCollections.observableArrayList(controller.getConcrete()));
        concreteClassCombo.setEditable(true);
        comboBoxHelper.setupComboBox(concreteClassCombo, "concreteClasses");
        
        Button addConcreteButton = new Button("Adaugă Clasă");
        Button deleteConcreteButton = new Button("Șterge Clasă");
        Button undoConcreteButton = new Button("Undo");
        
        setupConcreteButtons(addConcreteButton, deleteConcreteButton, undoConcreteButton, concreteClassCombo);
        HBox concreteButtons = new HBox(10, addConcreteButton, deleteConcreteButton, undoConcreteButton);
        
        leftGrid.add(concreteClassLabel, 0, ++row);
        leftGrid.add(concreteClassCombo, 0, ++row);
        leftGrid.add(concreteButtons, 0, ++row);
        
        this.protocolGroup = protocolGroup;  // Make these instance variables
        this.clientCombo = clientCombo;
        this.samplingDatePicker = samplingDatePicker;
        this.concreteClassCombo = concreteClassCombo;
        
        return leftGrid;
    }
    
    private GridPane createRightGrid() {
        GridPane rightGrid = new GridPane();
        rightGrid.setVgap(10);
        int row = 0;
        
        // Set ID section
        Label setIdLabel = new Label("Indicativ:");
        TextField setIdField = new TextField();
        rightGrid.add(setIdLabel, 0, row);
        rightGrid.add(setIdField, 0, ++row);
        
        // Set size section
        Label setSizeLabel = new Label("Număr Epruvete:");
        TextField setSizeField = new TextField();
        rightGrid.add(setSizeLabel, 0, ++row);
        rightGrid.add(setSizeField, 0, ++row);
        
        // Print option section
        Label shouldPrintLabel = new Label("Imprimare Bon:");
        ToggleGroup printGroup = new ToggleGroup();
        RadioButton printYes = new RadioButton("Da");
        RadioButton printNo = new RadioButton("Nu");
        printYes.setToggleGroup(printGroup);
        printNo.setToggleGroup(printGroup);
        HBox printBox = new HBox(10, printYes, printNo);
        
        rightGrid.add(shouldPrintLabel, 0, ++row);
        rightGrid.add(printBox, 0, ++row);
        
        // Obiectiv section
        Label obiectivLabel = new Label("Obiectiv:");
        obiectivArea.setPromptText("Introduceți descrierea obiectivului...");
        obiectivArea.setWrapText(true);
        obiectivArea.setPrefRowCount(3);
        
        rightGrid.add(obiectivLabel, 0, ++row);
        rightGrid.add(obiectivArea, 0, ++row);
        
        // Element section
        Label elementLabel = new Label("Element:");
        elementArea.setPromptText("Introduceți descrierea elementului...");
        elementArea.setWrapText(true);
        elementArea.setPrefRowCount(3);
        
        rightGrid.add(elementLabel, 0, ++row);
        rightGrid.add(elementArea, 0, ++row);
        
        // Output format section
        Label outputFormatLabel = new Label("Format Bon:");
        CheckBox pdfCheck = new CheckBox("PDF");
        CheckBox excelCheck = new CheckBox("Excel");
        CheckBox wordCheck = new CheckBox("Word");
        HBox outputFormatBox = new HBox(10, pdfCheck, excelCheck, wordCheck);
        
        rightGrid.add(outputFormatLabel, 0, ++row);
        rightGrid.add(outputFormatBox, 0, ++row);
        
        // Submit button
        Button submitButton = new Button("Incepe testarea");
        setupSubmitButton(submitButton, rightGrid, setIdField, setSizeField, 
                         printGroup, pdfCheck, excelCheck, wordCheck);
        
        rightGrid.add(submitButton, 0, ++row);
        
        return rightGrid;
    }
    
    private void setupClientButtons(Button addButton, Button deleteButton, Button undoButton, ComboBox<String> combo) {
        addButton.setOnAction(e -> controller.addClient(combo.getEditor().getText().trim(), combo));
        deleteButton.setOnAction(e -> controller.deleteClient(combo.getValue().trim(), combo));
        undoButton.setOnAction(e -> controller.undoClientChanges(combo));
    }
    
    private void setupConcreteButtons(Button addButton, Button deleteButton, Button undoButton, ComboBox<String> combo) {
        addButton.setOnAction(e -> controller.addConcrete(combo.getEditor().getText().trim(), combo));
        deleteButton.setOnAction(e -> controller.deleteConcrete(combo.getValue().trim(), combo));
        undoButton.setOnAction(e -> controller.undoConcreteChanges(combo));
    }
    
    private void setupSubmitButton(Button submitButton, GridPane rightGrid, TextField setIdField,
            					TextField setSizeField, ToggleGroup printGroup, CheckBox pdfCheck, CheckBox excelCheck, CheckBox wordCheck) {
        
        submitButton.setOnAction(event -> {
        	System.out.println("=== SUBMIT BUTTON PRESSED ===");
        	
            // Get references to all form components
            GridPane formGrid = (GridPane) rightGrid.getParent();
            GridPane leftGrid = (GridPane) formGrid.getChildren().get(0);
            // Your existing validation logic
            
            boolean isValid = controller.validateData(protocolGroup, clientCombo, concreteClassCombo, samplingDatePicker, 
            		obiectivArea, elementArea, setIdField, setSizeField, 
                    printGroup, pdfCheck, excelCheck, wordCheck);
            
            // Only trigger callback if validation passed
            if (isValid) {
                System.out.println("Data submitted successfully, triggering Python callback...");
                
                // Trigger the Python callback through AppController
                if (appController != null) {
                    appController.triggerDataSubmittedCallback();
                } else {
                    System.out.println("AppController reference is null - callback not triggered");
                }
            } else {
                System.out.println("Data validation failed, callback not triggered");
            }
            
        });
    }
}