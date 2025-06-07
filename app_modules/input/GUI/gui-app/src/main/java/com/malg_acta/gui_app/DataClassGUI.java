package com.malg_acta.gui_app;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonValue;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.databind.JsonSerializer;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializerProvider;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

public class DataClassGUI {

    @JsonProperty("protocol")
    public String protocol;
    
    @JsonProperty("client")
    public String client;

    @JsonProperty("concrete_class")
    public String concrete_class;
    
    @JsonProperty("sampling_date")
    public String sampling_date;
       
    @JsonProperty("testing_date")
    public String testing_date;
    
    @JsonProperty("project_title")
    public String project_title;
    
    @JsonProperty("element")
    public String element;
    
    @JsonProperty("set_id")
    public String set_id;
    
    @JsonProperty("set_size")
    public int set_size;
       
    @JsonProperty("should_print")
    public boolean should_print;
    
    @JsonProperty("output_format")
    public OutputFormats output_format;
    
    // Default constructor
    public DataClassGUI() {
        this.output_format = new OutputFormats();
    }
    
    // Method to convert this object to JSON string
    public String toJSON() {
        try {
            ObjectMapper mapper = new ObjectMapper();
            return mapper.writeValueAsString(this);
        } catch (Exception e) {
            e.printStackTrace();
            return "{}";
        }
    }
    
    // Constructor with all parameters
    public DataClassGUI(String protocol, String client, String concrete_class,  
                      String sampling_date, String testing_date, String project_title,
                      String element,String set_id, int set_size,
                      boolean should_print, OutputFormats output_format) {
        this.protocol = protocol;
        this.client = client;
        this.sampling_date = sampling_date;
        this.concrete_class = concrete_class;
        this.set_id = set_id;
        this.set_size = set_size;
        this.testing_date = testing_date;
        this.project_title = project_title;
        this.element = element;
        this.should_print = should_print;
        this.output_format = output_format != null ? output_format : new OutputFormats();
    }
    
    // Getters and Setters - removed the Romanian/camelCase getters to avoid duplication
    public String getProtocol() { return protocol; }
    public void setProtocol(String protocol) { this.protocol = protocol; }
    
    public String getClient() { return client; }
    public void setClient(String client) { this.client = client; }
    
    public String getSampling_date() { return sampling_date; }
    public void setSampling_date(String sampling_date) { this.sampling_date = sampling_date; }
    
    public String getConcrete_class() { return concrete_class; }
    public void setConcrete_class(String concrete_class) { this.concrete_class = concrete_class; }
    
    public String getSet_id() { return set_id; }
    public void setSet_id(String set_id) { this.set_id = set_id; }
    
    public int getSet_size() { return set_size; }
    public void setSet_size(int set_size) { this.set_size = set_size; }
    
    public String getTesting_date() { return testing_date; }
    public void setTesting_date(String testing_date) { this.testing_date = testing_date; }
    
    public String getProject_title() { return project_title; }
    public void setProject_title(String project_title) { this.project_title = project_title; }
    
    public String getElement() { return element; }
    public void setElement(String element) { this.element = element; }
    
    public boolean isShould_print() { return should_print; }
    public void setShould_print(boolean should_print) { this.should_print = should_print; }
    
    public OutputFormats getOutput_format() { return output_format; }
    public void setOutput_format(OutputFormats output_format) { this.output_format = output_format; }
    
    @Override
    public String toString() {
        return "FormDataGUI{" +
                "protocol='" + protocol + '\'' +
                ", client='" + client + '\'' +
                ", concrete_class='" + concrete_class + '\'' +
                ", sampling_date='" + sampling_date + '\'' +
                ", testing_date='" + testing_date + '\'' +
                ", project_title='" + project_title + '\'' +
                ", element='" + element + '\'' +
                ", set_id='" + set_id + '\'' +
                ", set_size=" + set_size +
                ", should_print=" + should_print +
                ", output_formats=" + output_format +
                '}';
    }
    
    // Inner class for output formats
    public static class OutputFormats {
        // Keep boolean fields for internal use but don't serialize them
        @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
        public boolean pdf;
        
        @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
        public boolean excel;
        
        @JsonProperty(access = JsonProperty.Access.WRITE_ONLY)
        public boolean word;
        
        public OutputFormats() {
            this.pdf = false;
            this.excel = false;
            this.word = false;
        }
        
        public OutputFormats(boolean pdf, boolean excel, boolean word) {
            this.pdf = pdf;
            this.excel = excel;
            this.word = word;
        }
        
        // Getters and Setters for internal use
        public boolean isPdf() { return pdf; }
        public void setPdf(boolean pdf) { this.pdf = pdf; }
        
        public boolean isExcel() { return excel; }
        public void setExcel(boolean excel) { this.excel = excel; }
        
        public boolean isWord() { return word; }
        public void setWord(boolean word) { this.word = word; }
        
        @JsonValue
        public String[] getSelectedFormats() {
            List<String> selectedFormats = new ArrayList<>();
            
            if (pdf) {
                selectedFormats.add("PDF");
            }
            if (excel) {
                selectedFormats.add("Excel");
            }
            if (word) {
                selectedFormats.add("Word");
            }
            
            return selectedFormats.toArray(new String[0]);
        }
        @Override
        public String toString() {
            return "OutputFormats{" +
                    "selectedFormats=" + getSelectedFormats() +
                    '}';
        }
    }
}