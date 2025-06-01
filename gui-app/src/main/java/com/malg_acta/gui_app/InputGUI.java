package com.malg_acta.gui_app;

import javafx.application.Application;
import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseEvent;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;

import javafx.scene.control.ComboBox;
import javafx.scene.control.skin.ComboBoxListViewSkin;

import java.io.File;
import java.io.IOException;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.Locale;
import java.util.Stack;

import javafx.util.StringConverter;

public class InputGUI extends Application {

    // TextFlow for logging messages with color support
    private TextFlow logArea = new TextFlow();
    private TextArea obiectivTextArea = new TextArea();
    private TextArea elementTextArea = new TextArea();
    private List<String> clients = new ArrayList<>();
    private final String clientsFilePath = "clients.json";    
    private final Stack<List<String>> clientHistory = new Stack<>();
    private List<String> concrete = new ArrayList<>();
    private final String concreteFilePath = "concrete_class.json";    
    private final Stack<List<String>> concreteHistory = new Stack<>();
    private String comboboxFilter = "";
    
    @Override
    public void start(Stage primaryStage) {
        //main layout
        VBox root = new VBox(15);
        root.setPadding(new Insets(20));

        GridPane formGrid = new GridPane();
        formGrid.setHgap(40);
        formGrid.setVgap(10);
        formGrid.setAlignment(Pos.TOP_LEFT);

        ColumnConstraints col1 = new ColumnConstraints();
        col1.setPercentWidth(40);
        ColumnConstraints col2 = new ColumnConstraints();
        col2.setPercentWidth(60);
        formGrid.getColumnConstraints().addAll(col1, col2);

        GridPane leftGrid = new GridPane();
        leftGrid.setVgap(10);
        GridPane rightGrid = new GridPane();
        rightGrid.setVgap(10);

        int leftRow = 0;
        int rightRow = 0;
       
        // protocol radio buttons
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

        // client dropdown
        Label clientLabel = new Label("Beneficiar:");
        clients = loadClientsFromJson(clientsFilePath);
        ComboBox<String> clientCombo = new ComboBox<>(FXCollections.observableArrayList(clients));
        clientCombo.setEditable(true);
        
        AddComboBoxEvents(clientCombo, "clients");
        
        Button addClientButton = new Button("Adaugă Client");
        Button deleteClientButton = new Button("Șterge Client");
        Button undoClientButton = new Button("Undo");

        // event handlers for the client dropdowns
        AddClientButtonEventHandler(addClientButton, clientCombo);
        DeleteClientButtonEventHandler(deleteClientButton, clientCombo);
        UndoClientButtonEventHandler(undoClientButton, clientCombo);
        
        HBox clientButtons = new HBox(10, addClientButton, deleteClientButton, undoClientButton);

        // sampling date
        Label samplingDateLabel = new Label("Data Prelevării:");
        DatePicker samplingDatePicker = new DatePicker();
        
        // set date converter
        samplingDatePicker.setConverter(this.DatePickerConverter());
                
        // concrete class dropdown
        Label concreteClassLabel = new Label("Clasa Betonului:");
        concrete = loadConcreteFromJson(concreteFilePath);
        ComboBox<String> concreteClassCombo = new ComboBox<>(FXCollections.observableArrayList(concrete));
        concreteClassCombo.setEditable(true);  
        
        AddComboBoxEvents(concreteClassCombo, "concreteClasses");
        
        Button addConcreteButton = new Button("Adaugă Clasă");
        Button deleteConcreteButton = new Button("Șterge Clasă");
        Button undoConcreteButton = new Button("Undo");
        
        //event handlers for the concrete class dropdown
        AddConcreteButtonEventHandler(addConcreteButton, concreteClassCombo);
        DeleteConcreteButtonEventHandler(deleteConcreteButton, concreteClassCombo);
        UndoConcreteButtonEventHandler(undoConcreteButton, concreteClassCombo);
        
        HBox concreteButtons = new HBox(10, addConcreteButton, deleteConcreteButton, undoConcreteButton);

        // set ID
        Label setIdLabel = new Label("Indicativ:");
        TextField setIdField = new TextField();

        //set size
        Label setSizeLabel = new Label("Număr Epruvete:");
        TextField setSizeField = new TextField();

        // should print radio buttons
        Label shouldPrintLabel = new Label("Imprimare Bon:");
        ToggleGroup printGroup = new ToggleGroup();
        RadioButton printYes = new RadioButton("Da");
        RadioButton printNo = new RadioButton("Nu");

        printYes.setToggleGroup(printGroup);
        printNo.setToggleGroup(printGroup);

        HBox printBox = new HBox(10, printYes, printNo);

        // obiectiv section
        Label obiectivLabel = new Label("Obiectiv:");
        TextArea obiectivArea = new TextArea();
        obiectivArea.setPromptText("Introduceți descrierea obiectivului...");
        obiectivArea.setWrapText(true);
        obiectivArea.setPrefRowCount(3);

        // element section
        Label elementLabel = new Label("Element:");
        TextArea elementArea = new TextArea();
        elementArea.setPromptText("Introduceți descrierea elementului...");
        elementArea.setWrapText(true);
        elementArea.setPrefRowCount(3);        
        
        //output format checkboxes
        Label outputFormatLabel = new Label("Format Bon:");
        CheckBox pdfCheck = new CheckBox("PDF");
        CheckBox excelCheck = new CheckBox("Excel");
        CheckBox wordCheck = new CheckBox("Word");

        HBox outputFormatBox = new HBox(10, pdfCheck, excelCheck, wordCheck);

        // log area
        Label logLabel = new Label("Log:");

        // Wrap the log area with a ScrollPane to allow scrolling
        ScrollPane logScrollPane = new ScrollPane();
        logScrollPane.setContent(logArea); // Add the TextFlow to the ScrollPane
        logScrollPane.setPrefHeight(150); // Set preferred height of the log area
        logScrollPane.setFitToWidth(true); // Make the log content fit to width of the ScrollPane

        // submit button to trigger validation
        Button submitButton = new Button("Trimite Formular");
        
        // event handler for the submit button
        submitButton.setOnAction(event -> validateForm(
            protocolGroup, clientCombo, samplingDatePicker,
            concreteClassCombo, setIdField, setSizeField,
            printGroup, pdfCheck, excelCheck, wordCheck
        ));

        // add all elements to root layout
        root.getChildren().addAll(
            protocolLabel, protocolBox,
            clientLabel, clientCombo, clientButtons,
            samplingDateLabel, samplingDatePicker,
            concreteClassLabel, concreteClassCombo, concreteButtons,
            setIdLabel, setIdField,
            setSizeLabel, setSizeField,
            shouldPrintLabel, printBox,
            obiectivLabel, obiectivArea,
            elementLabel, elementArea,
            outputFormatLabel, outputFormatBox,
            submitButton,
            logLabel, logScrollPane // Use ScrollPane for log area
        	);

        // Define 4 column constraints for better alignment
        formGrid.getColumnConstraints().addAll(
            new ColumnConstraints(150),  // label 1
            new ColumnConstraints(300),  // input 1
            new ColumnConstraints(150),  // label 2
            new ColumnConstraints(300)   // input 2
        );
        
        leftGrid.add(protocolLabel, 0, leftRow);
        leftGrid.add(protocolBox, 0, ++leftRow);

        leftGrid.add(clientLabel, 0, ++leftRow);
        leftGrid.add(clientCombo, 0, ++leftRow);
        leftGrid.add(clientButtons, 0, ++leftRow);

        leftGrid.add(samplingDateLabel, 0, ++leftRow);
        leftGrid.add(samplingDatePicker, 0, ++leftRow);

        leftGrid.add(concreteClassLabel, 0, ++leftRow);
        leftGrid.add(concreteClassCombo, 0, ++leftRow);
        leftGrid.add(concreteButtons, 0, ++leftRow);

        rightGrid.add(setIdLabel, 0, rightRow);
        rightGrid.add(setIdField, 0, ++rightRow);

        rightGrid.add(setSizeLabel, 0, ++rightRow);
        rightGrid.add(setSizeField, 0, ++rightRow);

        rightGrid.add(shouldPrintLabel, 0, ++rightRow);
        rightGrid.add(printBox, 0, ++rightRow);

        rightGrid.add(obiectivLabel, 0, ++rightRow);
        rightGrid.add(obiectivArea, 0, ++rightRow);

        rightGrid.add(elementLabel, 0, ++rightRow);
        rightGrid.add(elementArea, 0, ++rightRow);

        rightGrid.add(outputFormatLabel, 0, ++rightRow);
        rightGrid.add(outputFormatBox, 0, ++rightRow);

        rightGrid.add(submitButton, 0, ++rightRow);

        formGrid.add(leftGrid, 0, 0);
        formGrid.add(rightGrid, 1, 0);

        VBox fullLayout = new VBox(20);
        fullLayout.setPadding(new Insets(20));
        fullLayout.getChildren().addAll(formGrid, new Label("Log:"), new ScrollPane(logArea));

        ScrollPane mainScrollPane = new ScrollPane(fullLayout);
        mainScrollPane.setFitToWidth(true);
        Scene scene = new Scene(mainScrollPane, 1000, 800);

        primaryStage.setTitle("Formular Testare Beton");
        primaryStage.setScene(scene);
        primaryStage.setMaximized(true);
        primaryStage.show();
    }
    
    private void AddClientButtonEventHandler(Button btn, ComboBox<String> clientCombo) {
    	btn.setOnAction(e -> {
            String newClient = clientCombo.getEditor().getText().trim();
            if (!newClient.isEmpty() && !clients.contains(newClient)) {
            	clientHistory.push(new ArrayList<String>(clients));
                clients.add(newClient);
                clientCombo.getItems().add(newClient);
                saveClientsToJson(clientsFilePath, clients);
                logInfo("Client adăugat: " + newClient);
            }
            else if (clients.contains(newClient)) {
            	logError("Client deja existent!");
            }
        });
    }
    
    private void DeleteClientButtonEventHandler(Button btn, ComboBox<String> clientCombo) {
    	btn.setOnAction(e -> {
    		String selectedClient = clientCombo.getValue().trim();
            if (clients.contains(selectedClient)) {
            	clientHistory.push(new ArrayList<String>(clients));
                clients.remove(selectedClient);
                clientCombo.getItems().remove(selectedClient);
                saveClientsToJson(clientsFilePath, clients);
                logInfo("Client șters: " + selectedClient);
            } else {
                logError("Clientul nu există în listă.");
            }
        });
    }
    
    private void UndoClientButtonEventHandler(Button btn, ComboBox<String> clientCombo) {
    	btn.setOnAction(e -> {
    		if (!clientHistory.isEmpty()) {
                clients = clientHistory.pop();
                clientCombo.getItems().setAll(clients);
                saveClientsToJson(clientsFilePath, clients);
                logInfo("Ultima modificare a fost anulată.");
            } else {
                logError("Nu există modificări de anulat.");
            }
        });
    }
    
    private void AddConcreteButtonEventHandler(Button btn, ComboBox<String> concreteCombo) {
    	btn.setOnAction(e -> {
    		String newConcrete = concreteCombo.getEditor().getText().trim();
            if (!newConcrete.isEmpty() && !concrete.contains(newConcrete)) {
            	concreteHistory.push(new ArrayList<String>(concrete));
            	concrete.add(newConcrete);
            	concreteCombo.getItems().add(newConcrete);
                saveConcreteToJson(concreteFilePath, concrete);
                logInfo("Clasă beton adăugată: " + newConcrete);
            }
            else if (concrete.contains(newConcrete)) {
            	logError("Clasă beton deja existentă!");
            }
        });
    }
    
    private void DeleteConcreteButtonEventHandler(Button btn, ComboBox<String> concreteCombo) {
    	btn.setOnAction(e -> {
    		String selectedConcrete = concreteCombo.getValue().trim();
            if (concrete.contains(selectedConcrete)) {
            	concreteHistory.push(new ArrayList<String>(concrete));
            	concrete.remove(selectedConcrete);
            	concreteCombo.getItems().remove(selectedConcrete);
                saveConcreteToJson(concreteFilePath, concrete);
                logInfo("Clasă beton ștearsă: " + selectedConcrete);
            } else {
                logError("Clasa beton nu există în listă.");
            }
        });
    }
    
    private void UndoConcreteButtonEventHandler(Button btn, ComboBox<String> concreteCombo) {
    	btn.setOnAction(e -> {
    		if (!concreteHistory.isEmpty()) {
                concrete = concreteHistory.pop();
                concreteCombo.getItems().setAll(concrete);
                saveConcreteToJson(concreteFilePath, concrete);
                logInfo("Ultima modificare a fost anulată.");
            } else {
                logError("Nu există modificări de anulat.");
            }
        });
    }
    
    private void AddComboBoxEvents(ComboBox<String> comboBox, String option) {    	
    	// using a combobox skin to fix a bug that causes the popup to close when the "SPACEBAR" key is pressed
        ComboBoxListViewSkin<String> comboBoxListViewSkin = new ComboBoxListViewSkin<String>(comboBox);
        
        comboBoxListViewSkin.getPopupContent().addEventFilter(KeyEvent.ANY, (event) -> {
        	if (event.getCode() == KeyCode.SPACE) {
        		// allow spaces when filtering
        		if (event.getEventType() == KeyEvent.KEY_PRESSED) {
        			comboboxFilter += " ";
        		}
        		
        		// this prevents the popup from closing
                event.consume();
            }
        });
        
        comboBox.setSkin(comboBoxListViewSkin);
        
        // always show all the options when the dropdown is opened
        comboBox.setOnShown(new EventHandler<Event>() {
			@Override
			public void handle(Event event) {
				// we have to get the list of values every time since it might have changed (additions/deletions)
				List<String> options = option == "clients" ? clients : concrete;
				comboBox.getItems().setAll(FXCollections.observableArrayList(options));
			}
    	});
        
        // reset the filter when the dropdown is closed
        // this is needed since both comboboxes use the same filter variables
        comboBox.setOnHidden(new EventHandler<Event>() {
			@Override
			public void handle(Event event) {
				comboboxFilter = "";
				event.consume();
			}
    	});
        
        // open the dropdown on left click
    	comboBox.getEditor().addEventHandler(MouseEvent.MOUSE_PRESSED, new EventHandler<MouseEvent>() {
            @Override
            public void handle(final MouseEvent mouseEvent) {
            	if (mouseEvent.isPrimaryButtonDown() && !comboBox.isShowing()) {
            		comboBox.show();
            	}
            }
    	});
    	
    	// handle key press events (autocomplete/filtering)
    	comboBox.getEditor().addEventHandler(KeyEvent.KEY_PRESSED, new EventHandler<KeyEvent>() {
            @Override
            public void handle(final KeyEvent keyEvent) {
            	HandleOnKeyPressed(keyEvent, comboBox, option);
            }
    	});
    }
    
    private void HandleOnKeyPressed(KeyEvent event, ComboBox<String> comboBox, String option) {
    	List<String> options = option == "clients" ? clients : concrete;
    	ObservableList<String> filteredList = FXCollections.observableArrayList();
		KeyCode code = event.getCode();
		
		// make sure the filter contains the current value entered in the editor (it might have been cleared out if the dropdown was previously closed)
		comboboxFilter = comboBox.getEditor().getText();
		
		// open the dropdown if hidden (eg. when the keyboard was used to navigate to the control and it wasn't previously opened by a click event)
		if (!comboBox.isShowing()) {
			comboBox.show();
    	}
		
		if (code.isLetterKey() || code.isDigitKey()) {
			comboboxFilter += event.getText();
		}
		else {
			switch(code) {
				case BACK_SPACE:
					if(comboboxFilter.length() > 0) {
						comboboxFilter = comboboxFilter.substring(0, comboboxFilter.length() - 1);
					}
				    break;
				default:
					break;
			}
		}
		
		// empty filter -> reset the values
		if (comboboxFilter.length() == 0) {
			filteredList = FXCollections.observableArrayList(options);
		} else {
			String userInput = comboboxFilter.toLowerCase();
			options.stream().filter(el -> el.toString().toLowerCase().contains(userInput)).forEach(filteredList::add);
		}
		
		// update the dropdown with the filtered items/options
		comboBox.getItems().setAll(filteredList);
    }
    
    private StringConverter<LocalDate> DatePickerConverter() {
    	// Set Romanian locale
        Locale.setDefault(new Locale("ro")); // This affects the whole JVM

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

    // === Validation Function ===
    private void validateForm(ToggleGroup protocolGroup, ComboBox<String> clientCombo, DatePicker samplingDatePicker,
                               ComboBox<String> concreteClassCombo, TextField setIdField, TextField setSizeField,
                               ToggleGroup printGroup, CheckBox pdfCheck, CheckBox excelCheck, CheckBox wordCheck) {
        //logArea.getChildren().clear(); // Clear log area before each validation
        boolean valid = true;

        // Protocol must be selected
        if (protocolGroup.getSelectedToggle() == null) {
            logError("Trebuie selectat un protocol.");
            valid = false;
        }

        // Client must be selected or typed
        if (clientCombo.getEditor().getText().trim().isEmpty()) {
            logError("Trebuie selectat sau introdus un beneficiar.");
            valid = false;
        }

        // Sampling date must respect DD.MM.YYYY
        if (samplingDatePicker.getValue() == null) {
            logError("Trebuie selectată o dată validă pentru prelevare.");
            valid = false;
        }

        // Concrete class must be selected or typed
        if (concreteClassCombo.getEditor().getText().trim().isEmpty()) {
            logError("Trebuie selectată sau introdusă o clasă de beton.");
            valid = false;
        }

        // Set ID must be typed
        if (setIdField.getText().trim().isEmpty()) {
            logError("Indicativul trebuie completat.");
            valid = false;
        }

        // Set size must be a number > 0
        try {
            int size = Integer.parseInt(setSizeField.getText().trim());
            if (size <= 0) {
                logError("Numărul de epruvete trebuie să fie un număr mai mare decât 0.");
                valid = false;
            }
        } catch (NumberFormatException e) {
            logError("Numărul de epruvete trebuie să fie un număr valid.");
            valid = false;
        }

        // Should print must be selected
        if (printGroup.getSelectedToggle() == null) {
            logError("Trebuie selectată opțiunea de imprimare bon.");
            valid = false;
        }

        // At least one output format must be selected
        if (!pdfCheck.isSelected() && !excelCheck.isSelected() && !wordCheck.isSelected()) {
            logError("Trebuie selectat cel puțin un format de bon.");
            valid = false;
        }

        if (valid) {
            logInfo("Formular validat cu succes!");
            FormData data = new FormData();
            
            // data.protocol = ((RadioButton) protocolGroup.getSelectedToggle()).getText();
            data.beneficiar = clientCombo.getEditor().getText();
            data.probe_date = samplingDatePicker.getValue().format(DateTimeFormatter.ofPattern("dd.MM.yyyy"));
            data.clasa_betonului = concreteClassCombo.getEditor().getText();
            data.internal_code = setIdField.getText();
            data.numar_teste = Integer.parseInt(setSizeField.getText());
            data.try_date = LocalDate.now().format(DateTimeFormatter.ofPattern("dd.MM.yyyy"));
            // data.obiectiv = obiectivTextArea.getText();
            // data.element = elementTextArea.getText();
            try {
                ObjectMapper mapper = new ObjectMapper();
                mapper.writerWithDefaultPrettyPrinter().writeValue(new File("output.json"), data);
                logInfo("Datele au fost salvate în fișierul output.json");
            } catch (IOException e) {
                logError("Eroare la salvarea în fișier JSON.");
                System.out.println(e.getMessage());
            }
        }
    }

    // === Helper Methods ===
    private boolean isValidDate(String dateStr) {
        try {
            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("dd.MM.yyyy");
            LocalDate.parse(dateStr, formatter);
            return true;
        } catch (DateTimeParseException e) {
            return false;
        }
    }

    private void logInfo(String message) {
        Text infoText = new Text("[INFO] " + message + "\n");
        infoText.setFill(Color.GREEN); // Set color to green for info
        logArea.getChildren().add(infoText);
    }

    private void logError(String message) {
        Text errorText = new Text("[ERROR] " + message + "\n");
        errorText.setFill(Color.RED); // Set color to red for errors
        logArea.getChildren().add(errorText);
    }
    
    private List<String> loadClientsFromJson(String filePath) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(new File(filePath), mapper.getTypeFactory().constructCollectionType(List.class, String.class));
        } catch (IOException e) {
            logError("Eroare la citirea clientilor");
            return new ArrayList<>();
        }
    }
    
    private void saveClientsToJson(String filePath, List<String> clients) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(new File(filePath), clients);
            logInfo("Lista clienților a fost salvată.");
        } catch (IOException e) {
            logError("Eroare la salvarea listei de clienți: " + e.getMessage());
        }
    }
 
    private List<String> loadConcreteFromJson(String filePath) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(new File(filePath), mapper.getTypeFactory().constructCollectionType(List.class, String.class));
        } catch (IOException e) {
            logError("Eroare la citirea clasei betonului");
            return new ArrayList<>();
        }
    }
    
    private void saveConcreteToJson(String filePath, List<String> concrete) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(new File(filePath), concrete);
            logInfo("Lista clasa beton a fost salvată.");
        } catch (IOException e) {
            logError("Eroare la salvarea listei de clasa beton: " + e.getMessage());
        }
    }
    
    public static void main(String[] args) {
        launch(args);
    }
    	
}
