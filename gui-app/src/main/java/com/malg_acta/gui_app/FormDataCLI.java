package com.malg_acta.gui_app;

public class FormDataCLI {
	
    public String protocol;
    public String client;
    public String samplingDate;
    public String concreteClass;
    public String setId;
    public String setSize;
    public String printOption;
    public String obiectiv;
    public String element;
    public String format;

    public FormDataCLI(String protocol, String client, String samplingDate, String concreteClass,
                    String setId, String setSize, String printOption, String obiectiv,
                    String element, String format) {
        this.protocol = protocol;
        this.client = client;
        this.samplingDate = samplingDate;
        this.concreteClass = concreteClass;
        this.setId = setId;
        this.setSize = setSize;
        this.printOption = printOption;
        this.obiectiv = obiectiv;
        this.element = element;
        this.format = format;
    }
}