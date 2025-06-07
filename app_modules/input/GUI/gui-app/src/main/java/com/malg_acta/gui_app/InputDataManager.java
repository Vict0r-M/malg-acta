package com.malg_acta.gui_app;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class InputDataManager {
    private final String clientsFilePath = "..\\..\\..\\data\\clients.json";
    private final String concreteFilePath = "..\\..\\..\\data\\concrete_class.json";
    private LoggerPanel logger;
    
    public InputDataManager(LoggerPanel logger) {
        this.logger = logger;
    }
    
    public List<String> loadClientsFromJson() {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(new File(clientsFilePath), 
                mapper.getTypeFactory().constructCollectionType(List.class, String.class));
        } catch (IOException e) {
            logger.logError("Eroare la citirea clientilor");
            return new ArrayList<>();
        }
    }
    
    public void saveClientsToJson(List<String> clients) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(new File(clientsFilePath), clients);
            logger.logInfo("Lista clienților a fost salvată.");
        } catch (IOException e) {
            logger.logError("Eroare la salvarea listei de clienți: " + e.getMessage());
        }
    }
    
    public List<String> loadConcreteFromJson() {
        ObjectMapper mapper = new ObjectMapper();
        try {
            return mapper.readValue(new File(concreteFilePath), 
                mapper.getTypeFactory().constructCollectionType(List.class, String.class));
        } catch (IOException e) {
            logger.logError("Eroare la citirea clasei betonului");
            return new ArrayList<>();
        }
    }
    
    public void saveConcreteToJson(List<String> concrete) {
        ObjectMapper mapper = new ObjectMapper();
        try {
            mapper.writerWithDefaultPrettyPrinter().writeValue(new File(concreteFilePath), concrete);
            logger.logInfo("Lista clasa beton a fost salvată.");
        } catch (IOException e) {
            logger.logError("Eroare la salvarea listei de clasă beton: " + e.getMessage());
        }
    }
}