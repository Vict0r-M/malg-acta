package com.malg_acta.gui_app;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.ScrollPane;
import javafx.scene.layout.VBox;
import javafx.stage.Stage;
import java.util.concurrent.CountDownLatch;

import com.malg_acta.gui_app.LoggerPanel.LogLevel;

import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;

public class AppController extends Application {

    private LoggerPanel logger;
    private InputController inputController;
    private InputView inputView;
    private Stage primaryStage;
    private static AppController instance;
    private static CountDownLatch startupLatch = new CountDownLatch(1);
    private Runnable onDataSubmittedCallback;
    private volatile boolean callbackRegistered = false;    
    
    // Static method to get the application instance
    public static AppController getInstance() {
        return instance;
    }
    
    // Launch the application in a separate thread
    public static void launchApp() {
        Thread appThread = new Thread(() -> {
            Application.launch(AppController.class);
        });
        appThread.setDaemon(true); // Important: makes thread exit when main program exits
        appThread.start();
        
        // Wait for the application to start
        try {
            startupLatch.await(); // Wait until GUI is ready
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    @Override
    public void start(Stage primaryStage) {
        this.primaryStage = primaryStage;
        instance = this; // Store instance for external access
        
        
        // Initialize controller and view
        logger = new LoggerPanel();
        inputController = new InputController(logger);
        inputView = new InputView(inputController, logger, this);
        
        // Create main layout
        VBox fullLayout = new VBox(20);
        fullLayout.setPadding(new Insets(20));
        fullLayout.getChildren().addAll(
            inputView.createLayout(),
            new Label("Log:"),
            logger
        );
        
        ScrollPane mainScrollPane = new ScrollPane(fullLayout);
        mainScrollPane.setFitToWidth(true);
        Scene scene = new Scene(mainScrollPane, 1000, 800);
        mainScrollPane.setStyle("-fx-font-size: 16px");
        
        primaryStage.setTitle("Achiziție de date - Controlled by Python");
        primaryStage.setScene(scene);
        primaryStage.setMaximized(true);
        primaryStage.show();
        
        // Signal that the application has started
        startupLatch.countDown();
    }
    
    // === Methods that can be called from Python ===
    
    /**
     * Get the InputController (thread-safe)
     */
    public InputController getInputController() {
        return inputController;
    }
    
    /**
     * Get data from InputController (thread-safe)
     */
    public Object getData() {
        if (inputController != null) {
            return inputController.getData();
        }
        return null;
    }    
    /**
     * Update the GUI from external thread (Python)
     * This runs the action on the JavaFX Application Thread
     */
    public void runOnFXThread(Runnable action) {
        if (Platform.isFxApplicationThread()) {
            action.run();
        } else {
            Platform.runLater(action);
        }
    }
    
    /**
     * Update GUI and wait for completion
     */
    public void runOnFXThreadAndWait(Runnable action) {
        if (Platform.isFxApplicationThread()) {
            action.run();
        } else {
            CompletableFuture<Void> future = new CompletableFuture<>();
            Platform.runLater(() -> {
                try {
                    action.run();
                    future.complete(null);
                } catch (Exception e) {
                    future.completeExceptionally(e);
                }
            });
            
            try {
                future.get(); // Wait for completion
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }
    }
    
    /**
     * Add a log message to the GUI
     */
    public void addLogMessage(LoggerPanel.LogEntry log) {
        // Since LoggerPanel already handles Platform.runLater internally,
        // you can call this directly without wrapping in runOnFXThread
        logger.addLogEntry(log);
    }    
    /**
     * Set the window title
     */
    public void setWindowTitle(String title) {
        runOnFXThread(() -> {
            if (primaryStage != null) {
                primaryStage.setTitle(title);
            }
        });
    }
    
    /**
     * Close the application
     */
    public void closeApplication() {
        runOnFXThread(() -> {
            if (primaryStage != null) {
                primaryStage.close();
            }
        });
    }
    
    /**
     * Check if the application is running
     */
    public boolean isRunning() {
        return primaryStage != null && primaryStage.isShowing();
    }
    
    /**
     * Get log messages as string
     */
    public String getLogMessages() {
        // Implement based on your LoggerPanel
        return logger.toString();
    }
    
 // Method to register the callback from Python
    public void setOnDataSubmittedCallback(Runnable callback) {
        this.onDataSubmittedCallback = callback;
        this.callbackRegistered = true;
        System.out.println("Callback registered successfully from Python");
    }
    
 // Method to trigger the callback
    public void triggerDataSubmittedCallback() {
        if (callbackRegistered && onDataSubmittedCallback != null) {
            // Run callback in a separate thread to avoid blocking JavaFX thread
            Platform.runLater(() -> {
                new Thread(() -> {
                    try {
                        onDataSubmittedCallback.run();
                    } catch (Exception e) {
                        System.err.println("Error in Python callback: " + e.getMessage());
                        e.printStackTrace();
                    }
                }).start();
            });
        }
    }

    /**
     * Log a message with timestamp from Python
     */
    public void logMessage(String level, String message, String timestamp) {
        if (logger != null) {
            LoggerPanel.LogLevel logLevel;
            try {
                logLevel = LoggerPanel.LogLevel.valueOf(level.toUpperCase());
            } catch (IllegalArgumentException e) {
                logLevel = LoggerPanel.LogLevel.INFO;
            }
            
            // Try to parse timestamp, use current time if parsing fails
            java.time.LocalDateTime dateTime;
            try {
                if (timestamp.contains("T")) {
                    // Full ISO datetime
                    dateTime = java.time.LocalDateTime.parse(timestamp);
                } else if (timestamp.matches("\\d{2}:\\d{2}:\\d{2}")) {
                    // Time only - combine with today's date
                    java.time.LocalTime time = java.time.LocalTime.parse(timestamp);
                    dateTime = java.time.LocalDate.now().atTime(time);
                } else {
                    // Fallback to current time
                    dateTime = java.time.LocalDateTime.now();
                }
            } catch (Exception e) {
                System.err.println("Failed to parse timestamp: " + timestamp + ", using current time");
                dateTime = java.time.LocalDateTime.now();
            }
            
            LoggerPanel.LogEntry logEntry = new LoggerPanel.LogEntry(
                logLevel,
                message,
                dateTime
            );
            
            addLogMessage(logEntry);
        }
    }

    
    // Standard main method for standalone running
    public static void main(String[] args) {
        launch(args);
    }    
}
