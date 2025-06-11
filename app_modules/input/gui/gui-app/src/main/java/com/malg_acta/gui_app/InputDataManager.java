package com.malg_acta.gui_app;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class InputDataManager {
    private final String clientsFilePath;
    private final String concreteFilePath;
    private LoggerPanel logger;
    
    public InputDataManager(LoggerPanel logger) {
        this.logger = logger;
        
        // Get the current working directory (should be malg-acta project root when run from main.py)
        String projectRoot = System.getProperty("user.dir");
        
        // Build cross-platform paths using Paths utility
        this.clientsFilePath = Paths.get(projectRoot, "data", "clients.json").toString();
        this.concreteFilePath = Paths.get(projectRoot, "data", "concrete_classes.json").toString();
        
        // Log the paths for debugging
        logger.logInfo("Project root: " + projectRoot);
        logger.logInfo("Clients file path: " + clientsFilePath);
        logger.logInfo("Concrete classes file path: " + concreteFilePath);
    }
    
    public List<String> loadClientsFromJson() {
        ObjectMapper mapper = new ObjectMapper();
        try {
            File clientsFile = new File(clientsFilePath);
            if (!clientsFile.exists()) {
                logger.logWarning("Clients file not found at: " + clientsFilePath + " - creating empty list");
                return new ArrayList<>();
            }
            
            List<String> clients = mapper.readValue(clientsFile, 
                mapper.getTypeFactory().constructCollectionType(List.class, String.class));
            logger.logInfo("Successfully loaded " + clients.size() + " clients from file");
            return clients;
            
        } catch (IOException e) {
            logger.logError("Eroare la citirea clientilor: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    public void saveClientsToJson(List<String> clients) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            File clientsFile = new File(clientsFilePath);
            
            // Ensure parent directory exists
            clientsFile.getParentFile().mkdirs();
            
            mapper.writerWithDefaultPrettyPrinter().writeValue(clientsFile, clients);
            logger.logInfo("Lista clienților a fost salvată (" + clients.size() + " items)");
            
        } catch (IOException e) {
            logger.logError("Eroare la salvarea listei de clienți: " + e.getMessage());
        }
    }
    
    public List<String> loadConcreteFromJson() {
        ObjectMapper mapper = new ObjectMapper();
        try {
            File concreteFile = new File(concreteFilePath);
            if (!concreteFile.exists()) {
                logger.logWarning("Concrete classes file not found at: " + concreteFilePath + " - creating empty list");
                return new ArrayList<>();
            }
            
            List<String> concrete = mapper.readValue(concreteFile, 
                mapper.getTypeFactory().constructCollectionType(List.class, String.class));
            logger.logInfo("Successfully loaded " + concrete.size() + " concrete classes from file");
            return concrete;
            
        } catch (IOException e) {
            logger.logError("Eroare la citirea clasei betonului: " + e.getMessage());
            return new ArrayList<>();
        }
    }
    
    public void saveConcreteToJson(List<String> concrete) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            File concreteFile = new File(concreteFilePath);
            
            // Ensure parent directory exists
            concreteFile.getParentFile().mkdirs();
            
            mapper.writerWithDefaultPrettyPrinter().writeValue(concreteFile, concrete);
            logger.logInfo("Lista clasa beton a fost salvată (" + concrete.size() + " items)");
            
        } catch (IOException e) {
            logger.logError("Eroare la salvarea listei de clasă beton: " + e.getMessage());
        }
    }
}