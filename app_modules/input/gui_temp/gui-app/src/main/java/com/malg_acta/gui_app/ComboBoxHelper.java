package com.malg_acta.gui_app;

import javafx.collections.FXCollections;
import javafx.collections.ObservableList;
import javafx.event.Event;
import javafx.event.EventHandler;
import javafx.scene.control.ComboBox;
import javafx.scene.control.skin.ComboBoxListViewSkin;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyEvent;
import javafx.scene.input.MouseEvent;
import java.util.List;

public class ComboBoxHelper {

    private InputController controller;
    private String comboboxFilter = "";
    
    public ComboBoxHelper(InputController controller) {
        this.controller = controller;
    }
    
    public void setupComboBox(ComboBox<String> comboBox, String option) {
        // Fix spacebar bug using custom skin
        ComboBoxListViewSkin<String> comboBoxListViewSkin = new ComboBoxListViewSkin<>(comboBox);
        
        comboBoxListViewSkin.getPopupContent().addEventFilter(KeyEvent.ANY, (event) -> {
            if (event.getCode() == KeyCode.SPACE) {
                // Allow spaces when filtering
                if (event.getEventType() == KeyEvent.KEY_PRESSED) {
                    comboboxFilter += " ";
                }
                // Prevent popup from closing
                event.consume();
            }
        });
        
        comboBox.setSkin(comboBoxListViewSkin);
        
        // Show all options when dropdown opens
        comboBox.setOnShown(new EventHandler<Event>() {
            @Override
            public void handle(Event event) {
                List<String> options = getOptionsForType(option);
                comboBox.getItems().setAll(FXCollections.observableArrayList(options));
            }
        });
        
        // Reset filter when dropdown closes
        comboBox.setOnHidden(new EventHandler<Event>() {
            @Override
            public void handle(Event event) {
                comboboxFilter = "";
                event.consume();
            }
        });
        
        // Open dropdown on left click
        comboBox.getEditor().addEventHandler(MouseEvent.MOUSE_PRESSED, new EventHandler<MouseEvent>() {
            @Override
            public void handle(final MouseEvent mouseEvent) {
                if (mouseEvent.isPrimaryButtonDown() && !comboBox.isShowing()) {
                    comboBox.show();
                }
            }
        });
        
        // Handle key press events for filtering
        comboBox.getEditor().addEventHandler(KeyEvent.KEY_PRESSED, new EventHandler<KeyEvent>() {
            @Override
            public void handle(final KeyEvent keyEvent) {
                handleKeyPressed(keyEvent, comboBox, option);
            }
        });
    }
    
    private void handleKeyPressed(KeyEvent event, ComboBox<String> comboBox, String option) {
        List<String> options = getOptionsForType(option);
        ObservableList<String> filteredList = FXCollections.observableArrayList();
        KeyCode code = event.getCode();
        
        // Sync filter with current editor text
        comboboxFilter = comboBox.getEditor().getText();
        
        // Open dropdown if hidden
        if (!comboBox.isShowing()) {
            comboBox.show();
        }
        
        // Handle different key types
        if (code.isLetterKey() || code.isDigitKey()) {
            comboboxFilter += event.getText();
        } else if (code == KeyCode.BACK_SPACE) {
            if (comboboxFilter.length() > 0) {
                comboboxFilter = comboboxFilter.substring(0, comboboxFilter.length() - 1);
            }
        }
        
        // Filter options
        if (comboboxFilter.length() == 0) {
            filteredList = FXCollections.observableArrayList(options);
        } else {
            String userInput = comboboxFilter.toLowerCase();
            options.stream()
                   .filter(el -> el.toString().toLowerCase().contains(userInput))
                   .forEach(filteredList::add);
        }
        
        // Update dropdown with filtered items
        comboBox.getItems().setAll(filteredList);
    }
    
    private List<String> getOptionsForType(String option) {
        return "clients".equals(option) ? controller.getClients() : controller.getConcrete();
    }
}