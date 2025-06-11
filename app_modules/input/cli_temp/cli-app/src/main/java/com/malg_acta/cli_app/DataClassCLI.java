package com.malg_acta.cli_app;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class DataClassCLI {
    @JsonProperty("protocol")
    private String protocol;
    
    @JsonProperty("client")
    private String client;
    
    @JsonProperty("concrete_class")
    private String concreteClass;
    
    @JsonProperty("sampling_date")
    private String samplingDate;
    
    @JsonProperty("testing_date")
    private String testingDate;
    
    @JsonProperty("project_title")
    private String projectTitle;
    
    @JsonProperty("element")
    private String element;
    
    @JsonProperty("set_id")
    private String setId;
    
    @JsonProperty("set_size")
    private int setSize;
    
    @JsonProperty("should_print")
    private boolean shouldPrint;
    
    @JsonProperty("output_format")
    private List<String> outputFormat;

    public DataClassCLI() {
        // Default constructor for Jackson
    }

    public DataClassCLI(String protocol, String client, String concreteClass, 
                       String samplingDate, String testingDate, String projectTitle, 
                       String element, String setId, int setSize, boolean shouldPrint, 
                       List<String> outputFormat) {
        this.protocol = protocol;
        this.client = client;
        this.concreteClass = concreteClass;
        this.samplingDate = samplingDate;
        this.testingDate = testingDate;
        this.projectTitle = projectTitle;
        this.element = element;
        this.setId = setId;
        this.setSize = setSize;
        this.shouldPrint = shouldPrint;
        this.outputFormat = outputFormat;
    }

    // Getters and Setters
    public String getProtocol() { return protocol; }
    public void setProtocol(String protocol) { this.protocol = protocol; }

    public String getClient() { return client; }
    public void setClient(String client) { this.client = client; }

    public String getConcreteClass() { return concreteClass; }
    public void setConcreteClass(String concreteClass) { this.concreteClass = concreteClass; }

    public String getSamplingDate() { return samplingDate; }
    public void setSamplingDate(String samplingDate) { this.samplingDate = samplingDate; }

    public String getTestingDate() { return testingDate; }
    public void setTestingDate(String testingDate) { this.testingDate = testingDate; }

    public String getProjectTitle() { return projectTitle; }
    public void setProjectTitle(String projectTitle) { this.projectTitle = projectTitle; }

    public String getElement() { return element; }
    public void setElement(String element) { this.element = element; }

    public String getSetId() { return setId; }
    public void setSetId(String setId) { this.setId = setId; }

    public int getSetSize() { return setSize; }
    public void setSetSize(int setSize) { this.setSize = setSize; }

    public boolean isShouldPrint() { return shouldPrint; }
    public void setShouldPrint(boolean shouldPrint) { this.shouldPrint = shouldPrint; }

    public List<String> getOutputFormat() { return outputFormat; }
    public void setOutputFormat(List<String> outputFormat) { this.outputFormat = outputFormat; }
}