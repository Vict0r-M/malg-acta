package com.malg_acta.gui_app;

import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.control.ScrollPane;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class LoggerPanel extends ScrollPane {

    private TextFlow textFlow;
    private List<LogEntry> logHistory;
    private int maxLogEntries = 1000; // Prevent memory issues
    private DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss");
    
    public LoggerPanel() {
        initialize();
    }
    
    private void initialize() {
        textFlow = new TextFlow();
        textFlow.setPadding(new Insets(10));
        logHistory = new ArrayList<>();
        
        // Configure ScrollPane
        setContent(textFlow);
        setPrefHeight(150);
        setFitToWidth(true);
        setStyle("-fx-background-color: #f8f8f8; -fx-border-color: #cccccc; -fx-border-width: 1px;");
        
        // Auto-scroll to bottom
        setVvalue(1.0);
        
        // Add welcome message
        logInfo("Logger initialized - Ready for operations");
    }
    
    public void logInfo(String message) {
        addLogEntry(LogLevel.INFO, message);
    }
    
    public void logError(String message) {
        addLogEntry(LogLevel.ERROR, message);
    }
    
    public void logWarning(String message) {
        addLogEntry(LogLevel.WARNING, message);
    }
    
    public void logDebug(String message) {
        addLogEntry(LogLevel.DEBUG, message);
    }
    
    private void addLogEntry(LogLevel level, String message) {
        // Ensure UI updates happen on JavaFX Application Thread
        Platform.runLater(() -> {
            LogEntry entry = new LogEntry(level, message, LocalDateTime.now());
            logHistory.add(entry);
            
            // Maintain max log entries
            if (logHistory.size() > maxLogEntries) {
                logHistory.remove(0);
                // Clear and rebuild text flow to prevent memory leaks
                rebuildTextFlow();
            } else {
                addEntryToTextFlow(entry);
            }
            
            // Auto-scroll to bottom
            setVvalue(1.0);
        });
    }

    // NEW METHOD: Accept a LogEntry object directly
    public void addLogEntry(LogEntry entry) {
        // Ensure UI updates happen on JavaFX Application Thread
        Platform.runLater(() -> {
            logHistory.add(entry);
            
            // Maintain max log entries
            if (logHistory.size() > maxLogEntries) {
                logHistory.remove(0);
                // Clear and rebuild text flow to prevent memory leaks
                rebuildTextFlow();
            } else {
                addEntryToTextFlow(entry);
            }
            
            // Auto-scroll to bottom
            setVvalue(1.0);
        });
    }    
    
    private void addEntryToTextFlow(LogEntry entry) {
        // Create timestamp
        Text timestamp = new Text("[" + entry.timestamp.format(timeFormatter) + "] ");
        timestamp.setFill(Color.GRAY);
        timestamp.setFont(Font.font("Monospace", FontWeight.NORMAL, 12));
        
        // Create level indicator
        Text levelText = new Text("[" + entry.level.name() + "] ");
        levelText.setFill(getLevelColor(entry.level));
        levelText.setFont(Font.font("System", FontWeight.BOLD, 12));
        
        // Create message
        Text messageText = new Text(entry.message + "\n");
        messageText.setFill(Color.BLACK);
        messageText.setFont(Font.font("System", FontWeight.NORMAL, 12));
        
        // Add to text flow
        textFlow.getChildren().addAll(timestamp, levelText, messageText);
    }
    
    private void rebuildTextFlow() {
        textFlow.getChildren().clear();
        for (LogEntry entry : logHistory) {
            addEntryToTextFlow(entry);
        }
    }
    
    private Color getLevelColor(LogLevel level) {
        switch (level) {
            case INFO: return Color.GREEN;
            case ERROR: return Color.RED;
            case WARNING: return Color.ORANGE;
            case DEBUG: return Color.BLUE;
            default: return Color.BLACK;
        }
    }
    
    public void clearLog() {
        Platform.runLater(() -> {
            textFlow.getChildren().clear();
            logHistory.clear();
            logInfo("Log cleared");
        });
    }
    
    public List<LogEntry> getLogHistory() {
        return new ArrayList<>(logHistory);
    }
    
    public void setMaxLogEntries(int maxEntries) {
        this.maxLogEntries = Math.max(100, maxEntries); // Minimum 100 entries
    }
    
    // Export log to string
    public String exportLog() {
        StringBuilder sb = new StringBuilder();
        for (LogEntry entry : logHistory) {
            sb.append("[").append(entry.timestamp.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"))).append("] ");
            sb.append("[").append(entry.level.name()).append("] ");
            sb.append(entry.message).append("\n");
        }
        return sb.toString();
    }
    
    // Inner classes
    public enum LogLevel {
        INFO, ERROR, WARNING, DEBUG
    }
    
    public static class LogEntry {
        public final LogLevel level;
        public final String message;
        public final LocalDateTime timestamp;
        
        public LogEntry(LogLevel level, String message, LocalDateTime timestamp) {
            this.level = level;
            this.message = message;
            this.timestamp = timestamp;
        }
        
        @Override
        public String toString() {
            return "[" + timestamp.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")) + "] " +
                   "[" + level.name() + "] " + message;
        }
    }
}
