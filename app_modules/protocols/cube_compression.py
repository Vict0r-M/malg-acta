"""Cube compression testing protocol implementation"""

#%% Dependencies:

from typing import Dict, Any, List

#%% Main Class:

class CubeCompressionProtocol:
    """
    Implementation of cube compression testing protocol.
    
    Handles validation, specimen processing, and calculations for
    cube compression testing according to standard procedures.
    """
    
    def __init__(self, ctx: Any) -> None:
        """Initialize protocol with context"""
        
        self.ctx = ctx
        self.config = ctx.config
        self.logger = ctx.logger
        self.protocol_config = self.config.protocols.cube_compression_testing
    
    def validate_requirements(self, input_data: Any) -> bool:
        """
        Validate that input data meets protocol requirements.
        
        Args:
            input_data: InputData object with user input
            
        Returns:
            True if valid, False otherwise
        """
        
        try:
            # Check protocol matches:
            if input_data.protocol != "cube_compression_testing":
                self.logger.error("Protocol mismatch: expected cube_compression_testing")
                return False
            
            # Check set size is reasonable:
            if input_data.set_size <= 0 or input_data.set_size > 10:
                self.logger.error(f"Invalid set size: {input_data.set_size}")
                return False
            
            # Check required fields are present:
            required_fields = ['client', 'concrete_class', 'sampling_date', 
                             'testing_date', 'set_id']
            
            for field in required_fields:
                if not getattr(input_data, field, '').strip():
                    self.logger.error(f"Required field missing: {field}")
                    return False
            
            self.logger.info("Input data validation passed for cube compression protocol")
            return True
            
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            return False
    
    def create_specimens_from_demo_data(self, demo_data: Dict[str, Any], 
                                       set_size: int) -> List[Any]:
        """
        Create specimen objects from demo data.
        
        Args:
            demo_data: Demo data loaded from JSON
            set_size: Number of specimens to create
            
        Returns:
            List of SpecimenData objects
        """
        
        try:
            # Import models here to avoid circular imports:
            from ..models.scale_data import ScaleData
            from ..models.press_data import PressData  
            from ..models.specimen_data import SpecimenData
            
            specimens = []
            protocol_data = demo_data.get("cube_compression_testing", {})
            specimen_templates = protocol_data.get("specimens", [])
            
            if not specimen_templates:
                self.logger.error("No specimen data found in demo data")
                return []
            
            # Create specimens up to set_size, cycling through templates if needed:
            for i in range(set_size):
                template = specimen_templates[i % len(specimen_templates)]
                
                # Create scale data:
                scale_data = None
                if template.get("scale_data"):
                    scale_template = template["scale_data"]
                    scale_data = ScaleData(
                        mass=scale_template["mass"],
                        mass_unit=scale_template.get("mass_unit", "kg"),
                        mass_decimals=scale_template.get("mass_decimals", 3)
                    )
                
                # Create press data:
                press_data = None
                if template.get("press_data"):
                    press_template = template["press_data"]
                    press_data = PressData(
                        load=press_template["load"],
                        strength=press_template["strength"],
                        load_unit=press_template.get("load_unit", "N"),
                        strength_unit=press_template.get("strength_unit", "N/mm²"),
                        load_decimals=press_template.get("load_decimals", 0),
                        strength_decimals=press_template.get("strength_decimals", 2)
                    )
                
                # Create specimen:
                specimen = SpecimenData(
                    scale_data=scale_data,
                    press_data=press_data
                )
                
                specimens.append(specimen)
            
            self.logger.info(f"Created {len(specimens)} specimens from demo data")
            return specimens
            
        except Exception as e:
            self.logger.error(f"Failed to create specimens: {str(e)}")
            return []
    
    def process_set(self, set_data: Any) -> Dict[str, Any]:
        """
        Process a complete set according to cube compression protocol.
        
        Args:
            set_data: SetData object with input data and specimens
            
        Returns:
            Dictionary with processed results
        """
        
        try:
            input_data = set_data.input_data
            specimens = set_data.specimens
            
            self.logger.info(f"Processing set with {len(specimens)} specimens")
            
            # Validate all specimens have required measurements:
            valid_specimens = []
            for i, specimen in enumerate(specimens):
                if not self._validate_specimen(specimen, i + 1):
                    continue
                valid_specimens.append(specimen)
            
            if not valid_specimens:
                self.logger.error("No valid specimens found in set")
                return {}
            
            # Calculate statistics:
            stats = self._calculate_statistics(valid_specimens)
            
            # Prepare results:
            results = {
                "input_data": {
                    "protocol": input_data.protocol,
                    "client": input_data.client,
                    "concrete_class": input_data.concrete_class,
                    "sampling_date": input_data.sampling_date,
                    "testing_date": input_data.testing_date,
                    "sampling_location": input_data.sampling_location,
                    "project_name": input_data.project_name,
                    "set_id": input_data.set_id,
                    "set_size": len(valid_specimens),
                    "sample_age_days": input_data.get_sample_age()
                },
                "specimens": self._serialize_specimens(valid_specimens),
                "statistics": stats,
                "protocol_info": {
                    "name": "Cube Compression Testing",
                    "specimen_dimensions": self.protocol_config.specimen_dimensions,
                    "compression_area": self.protocol_config.compression_area
                }
            }
            
            self.logger.info("Set processing completed successfully")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to process set: {str(e)}")
            return {}
    
    def _validate_specimen(self, specimen: Any, specimen_num: int) -> bool:
        """Validate individual specimen has required measurements"""
        
        try:
            # Check for scale data (required for cube compression):
            if not specimen.scale_data:
                self.logger.warning(f"Specimen {specimen_num}: missing scale data")
                return False
            
            # Check for press data (required for cube compression):
            if not specimen.press_data:
                self.logger.warning(f"Specimen {specimen_num}: missing press data")
                return False
            
            # Validate measurement values:
            if specimen.scale_data.mass <= 0:
                self.logger.warning(f"Specimen {specimen_num}: invalid mass")
                return False
            
            if specimen.press_data.load <= 0 or specimen.press_data.strength <= 0:
                self.logger.warning(f"Specimen {specimen_num}: invalid press measurements")
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Specimen {specimen_num} validation error: {str(e)}")
            return False
    
    def _calculate_statistics(self, specimens: List[Any]) -> Dict[str, Any]:
        """Calculate statistical values for the specimen set"""
        
        try:
            if not specimens:
                return {}
            
            # Collect values:
            masses = [s.scale_data.mass for s in specimens if s.scale_data]
            loads = [s.press_data.load for s in specimens if s.press_data]
            strengths = [s.press_data.strength for s in specimens if s.press_data]
            
            # Calculate densities:
            densities = []
            for specimen in specimens:
                if specimen.scale_data:
                    # Density = mass(kg) / volume(m³)
                    # Volume = 0.15m × 0.15m × 0.15m = 0.003375 m³
                    volume_m3 = 0.003375  # m³ for 150mm cube
                    density = specimen.scale_data.mass / volume_m3  # kg/m³
                    densities.append(density)
            
            stats = {
                "specimen_count": len(specimens),
                "mass": {
                    "average": sum(masses) / len(masses) if masses else 0,
                    "min": min(masses) if masses else 0,
                    "max": max(masses) if masses else 0,
                    "unit": "kg"
                },
                "load": {
                    "average": sum(loads) / len(loads) if loads else 0,
                    "min": min(loads) if loads else 0,
                    "max": max(loads) if loads else 0,
                    "unit": "N"
                },
                "strength": {
                    "average": sum(strengths) / len(strengths) if strengths else 0,
                    "min": min(strengths) if strengths else 0,
                    "max": max(strengths) if strengths else 0,
                    "unit": "N/mm²"
                },
                "density": {
                    "average": sum(densities) / len(densities) if densities else 0,
                    "min": min(densities) if densities else 0,
                    "max": max(densities) if densities else 0,
                    "unit": "kg/m³"
                }
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Statistics calculation error: {str(e)}")
            return {}
    
    def _serialize_specimens(self, specimens: List[Any]) -> List[Dict[str, Any]]:
        """Serialize specimens for output"""
        
        serialized = []
        for specimen in specimens:
            specimen_data = {}
            
            if specimen.scale_data:
                specimen_data["scale_data"] = {
                    "mass": specimen.scale_data.mass,
                    "mass_unit": specimen.scale_data.mass_unit,
                    "formatted": specimen.scale_data.get_formatted_mass()
                }
            
            if specimen.press_data:
                specimen_data["press_data"] = {
                    "load": specimen.press_data.load,
                    "strength": specimen.press_data.strength,
                    "load_unit": specimen.press_data.load_unit,
                    "strength_unit": specimen.press_data.strength_unit,
                    "formatted_load": specimen.press_data.get_formatted_load(),
                    "formatted_strength": specimen.press_data.get_formatted_strength()
                }
            
            serialized.append(specimen_data)
        
        return serialized

#%%