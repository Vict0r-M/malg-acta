module com.malg_acta.gui_app {
    requires javafx.controls;
	requires com.fasterxml.jackson.core;
	requires com.fasterxml.jackson.databind;
	requires javafx.base;
    exports com.malg_acta.gui_app;
    
    opens com.malg_acta.gui_app to com.fasterxml.jackson.databind;
}
