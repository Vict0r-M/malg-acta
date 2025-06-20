"""Dissemination state - handles report generation and output"""

#%% Dependencies:

import time
from datetime import datetime
from typing import Any, Tuple, List

#%% Dissemination State:

class DisseminationState:
    """With receipt generation using output interface"""

    def __init__(self, input_interface: Any = None, output_interface: Any = None):
        """Initialize dissemination state with injected interfaces"""

        self.state_name = "dissemination_state"
        self.set_data = None
        self.output_generated = False
        self.input_interface = input_interface
        self.output_interface = output_interface


    def set_input_interface(self, input_interface: Any) -> None:
        """Set input interface reference after construction"""

        self.input_interface = input_interface


    def set_output_interface(self, output_interface: Any) -> None:
        """Set output interface reference after construction"""

        self.output_interface = output_interface


    def enter(self, ctx: Any,   # Context object
              data: Any = None  # Complete SetData instance from acquisition_state
             ) -> None:
        """Enter dissemination state with complete set data"""

        try:
            ctx.logger.info("Entering dissemination state - processing results")

            if not data or not hasattr(data, 'specimens'):
                raise ctx.errors.StateMachineError("Dissemination state requires complete set data")

            self.set_data = data
            self.output_generated = False

            # Validate set completion:
            if not self.set_data.is_complete():
                missing_count = self.set_data.input_data.set_size - len(self.set_data.specimens)
                ctx.logger.warning(f"Set incomplete: missing {missing_count} specimens")

            ctx.logger.info(f"Processing results for set {self.set_data.input_data.set_id}", target="user")
            ctx.logger.info("Generating reports...", target="user")

        except Exception as e:
            error_msg = f"Error entering dissemination state: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.StateMachineError(error_msg)


    def execute(self, ctx: Any        # Context object
               ) -> Tuple[str, Any]:  # (next_state_name, completion_data)
        """Execute dissemination logic - generate reports and handle output"""

        try:
            ctx.logger.info("Starting result processing and output generation")

            # Step 1: Calculate sample age and add to results:
            self._calculate_sample_age(ctx)

            # Step 2: Process test results and calculate statistics:
            results_summary = self._process_test_results(ctx)

            # Step 3: Generate receipts using output interface:
            generated_files = self._generate_receipts(ctx)

            # Step 4: Update registry (mock for 1.0.0):
            self._update_registry(ctx, results_summary)

            # Step 5: Handle printing if requested (skip for 1.0.0):
            if self.set_data.input_data.should_print:
                ctx.logger.info("Printing skipped in version 1.0.0", target="user")

            self.output_generated = True
            ctx.logger.info("Report generation completed successfully", target="user")
            ctx.logger.info(f"Set {self.set_data.input_data.set_id} processing complete", target="user")

            # Step 6: Unlock interface for next cycle (triggers CLI continue/exit prompt):
            if self.input_interface:
                self.input_interface.unlock_interface()

            # Return to idle state for next testing cycle:
            return ("idle_state", {"testing_completed": True, "results": results_summary, "files": generated_files})

        except ctx.errors.OutputError as e:
            # Handle output generation errors:
            ctx.logger.error(f"Output generation failed: {str(e)}", target="both")
            return ("error_state", {"error": e,
                                    "source_state": "dissemination_state",
                                    "set_data": self.set_data,
                                    "recoverable": True})

        except Exception as e:
            # Handle unexpected errors:
            ctx.logger.exception(f"Unexpected error in dissemination: {str(e)}")
            error_obj = ctx.errors.StateMachineError(f"Result processing failed: {str(e)}")
            return ("error_state", {"error": error_obj,
                                    "source_state": "dissemination_state",
                                    "set_data": self.set_data,
                                    "recoverable": False})


    def exit(self, ctx: Any) -> None:
        """Exit dissemination state"""

        try:
            ctx.logger.info("Exiting dissemination state")

            # Log completion summary:
            if self.output_generated and self.set_data:
                ctx.logger.info(f"Successfully processed {len(self.set_data.specimens)} specimens")

        except Exception as e:
            ctx.logger.warning(f"Error exiting dissemination state: {str(e)}")


    def can_transition_to(self, ctx: Any, target_state: str) -> bool:
        """Check if transition to target state is allowed from dissemination"""

        # From dissemination state, we typically go to:
        # - idle_state (normal completion)
        # - error_state (on output errors)
        allowed_transitions = ["idle_state", "error_state"]
        return target_state in allowed_transitions


    def _calculate_sample_age(self, ctx: Any) -> None:
        """Calculate and log sample age in days"""

        try:
            sample_age = self.set_data.input_data.get_sample_age(ctx)
            ctx.logger.info(f"Sample age calculated: {sample_age} days")

        except Exception as e:
            ctx.logger.warning(f"Failed to calculate sample age: {str(e)}")


    def _process_test_results(self, ctx: Any  # Context object
                             ) -> dict:       # Summary of test results
        """Process test results and calculate statistics"""

        try:
            ctx.logger.info("Processing test results...")

            protocol = self.set_data.input_data.protocol
            specimens = self.set_data.specimens

            results = {"protocol": protocol,
                       "set_id": self.set_data.input_data.set_id,
                       "client": self.set_data.input_data.client,
                       "concrete_class": self.set_data.input_data.concrete_class,
                       "specimen_count": len(specimens),
                       "testing_date": self.set_data.input_data.testing_date,
                       "specimens": []}

            # Process each specimen:
            for i, specimen in enumerate(specimens, 1):
                specimen_result = {"number": i}

                # Add scale data if present:
                if specimen.scale_data:
                    specimen_result["mass"] = specimen.scale_data.get_formatted_mass()

                # Add press data if present:
                if specimen.press_data:
                    specimen_result["load"] = specimen.press_data.get_formatted_load()
                    specimen_result["strength"] = specimen.press_data.get_formatted_strength()

                results["specimens"].append(specimen_result)

            # Calculate statistics if applicable:
            self._calculate_statistics(ctx, results, specimens)

            ctx.logger.info(f"Processed {len(specimens)} specimens for {protocol}")
            return results

        except Exception as e:
            error_msg = f"Failed to process test results: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.OutputError(error_msg)


    def _calculate_statistics(self, ctx: Any,  # Context object
                              results: dict,   # Results dictionary to update
                              specimens: list  # List of specimen data
                             ) -> None:
        """Calculate statistical summaries of test results"""

        try:
            # Extract strength values for statistical analysis:
            strengths = []
            for specimen in specimens:
                if specimen.press_data and specimen.press_data.strength:
                    strengths.append(specimen.press_data.strength)

            if strengths:
                # Calculate basic statistics:
                results["statistics"] = {"min_strength": f"{min(strengths):.2f} N/mm²",
                                         "max_strength": f"{max(strengths):.2f} N/mm²",
                                         "avg_strength": f"{sum(strengths)/len(strengths):.2f} N/mm²",
                                         "strength_count": len(strengths)}

                ctx.logger.info(f"Calculated statistics for {len(strengths)} strength measurements")

        except Exception as e:
            ctx.logger.warning(f"Failed to calculate statistics: {str(e)}")


    def _generate_receipts(self, ctx: Any  #  Context object
                          ) -> List[Any]:  # List of generated receipt files
        """Generate receipts using output interface"""

        try:
            if not self.output_interface:
                ctx.logger.warning("No output interface available - skipping receipt generation")
                return []

            ctx.logger.info("Generating receipts using output interface...")
            generated_files = self.output_interface.generate_receipts(self.set_data)

            ctx.logger.info(f"Successfully generated {len(generated_files)} receipt files", target="user")
            for file_path in generated_files:
                ctx.logger.info(f"Generated: {file_path.name}", target="user")

            return generated_files

        except Exception as e:
            error_msg = f"Failed to generate receipts: {str(e)}"
            ctx.logger.error(error_msg)
            raise ctx.errors.OutputError(error_msg)

#%%