package com.malg_acta.gui_app;

import javafx.application.Platform;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.VBox;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import javafx.scene.paint.Color;

public class LoggerPanel extends VBox {
	
    private final TextFlow textFlow;
    private final ScrollPane scrollPane;

    public LoggerPanel() {
        textFlow = new TextFlow();
        scrollPane = new ScrollPane(textFlow);
        scrollPane.setContent(textFlow);
        scrollPane.setFitToWidth(true);
        scrollPane.setPrefHeight(100);
        //scrollPane.setHbarPolicy(ScrollPane.ScrollBarPolicy.NEVER);
        scrollPane.setVbarPolicy(ScrollPane.ScrollBarPolicy.AS_NEEDED);
        //scrollPane.setNodeOrientation(NodeOrientation.LEFT_TO_RIGHT);

        this.getChildren().add(scrollPane);
    }

    public void logInfo(String message) {
        appendMessage("[INFO] ", message, Color.GREEN);
    }

    public void logError(String message) {
        appendMessage("[ERROR] ", message, Color.RED);
    }
    public void clear() {
        Platform.runLater(() -> textFlow.getChildren().clear());
    }
    
    private void appendMessage(String prefix, String message, Color color) {
        Platform.runLater(() -> {
            Text prefixText = new Text(prefix);
            prefixText.setFill(color);
            prefixText.setStyle("-fx-font-weight: bold");

            Text msgText = new Text(message + "\n");
            // msgText.setFill(color);
            textFlow.getChildren().addAll(prefixText, msgText);
            scrollPane.setVvalue(1.0); // keep scrolled to bottom
        });
  
    }    
}
