"""Output interface - unified bridge for PDF and Excel generation using plugin architecture"""

#%% Dependencies:

from typing import Any, Protocol, List
from pathlib import Path

#%% Output Strategy Protocol:

class OutputStrategy(Protocol):
    """Protocol defining what any output plugin must implement"""

    def setup(self, ctx: Any, config: Any) -> None:
        """Setup strategy with context and configuration"""
        ...


    def generate_receipt(self, set_data: Any,  # Complete SetData instance with input_data and specimens
                         output_format: str    # "PDF" or "Excel"
                        ) -> Path:             # Path to generated receipt file
        """Generate receipt for the given set data"""
        ...


    def cleanup(self) -> None:
        """Cleanup resources when application shuts down"""
        ...

#%% Output Interface:

class OutputInterface:
    """Provides clean API for receipt generation with plugin-based strategies"""

    def __init__(self, ctx: Any,        # Context object containing config, logger, errors, typing
                 plugin_manager: Any):  # PluginManager instance for loading output strategies
        """Initialize output interface"""

        self.ctx = ctx
        self.plugin_manager = plugin_manager
        self.strategies = {}

        try:
            # Load available output strategies:
            self._load_strategies()
            self.ctx.logger.info("OutputInterface initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize output interface: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ConfigurationError(error_msg)


    def _load_strategies(self) -> None:
        """Load and setup output strategies"""

        try:
            # Load receipt generator strategy:
            receipt_strategy = self.plugin_manager.get_strategy("output", "receipt_generator")
            receipt_strategy.setup(self.ctx, self.ctx.config)
            self.strategies["receipt_generator"] = receipt_strategy

            self.ctx.logger.info("Output strategies loaded successfully")

        except Exception as e:
            error_msg = f"Failed to load output strategies: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ConfigurationError(error_msg)


    def generate_receipts(self, set_data: Any  # Complete SetData instance
                         ) -> List[Path]:      # List of paths to generated receipt files
        """Generate receipts in all requested formats"""

        try:
            output_formats = set_data.input_data.output_format
            protocol = set_data.input_data.protocol
            set_id = set_data.input_data.set_id

            self.ctx.logger.info(f"Generating receipts for {protocol}, set {set_id}")
            self.ctx.logger.info(f"Requested formats: {', '.join(output_formats)}")

            generated_files = []
            receipt_strategy = self.strategies["receipt_generator"]

            for format_type in output_formats:
                self.ctx.logger.info(f"Generating {format_type} receipt...")

                try:
                    file_path = receipt_strategy.generate_receipt(set_data, format_type)
                    generated_files.append(file_path)
                    self.ctx.logger.info(f"{format_type} receipt generated: {file_path.name}")

                except Exception as e:
                    error_msg = f"Failed to generate {format_type} receipt: {str(e)}"
                    self.ctx.logger.error(error_msg)
                    raise self.ctx.errors.OutputError(error_msg)

            self.ctx.logger.info(f"Successfully generated {len(generated_files)} receipt files")
            return generated_files

        except self.ctx.errors.OutputError:
            raise  # Re-raise output errors
        except Exception as e:
            error_msg = f"Receipt generation failed: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.OutputError(error_msg)


    def cleanup(self) -> None:
        """Clean shutdown of output interface and strategies"""

        try:
            self.ctx.logger.info("Shutting down output interface...")

            for strategy_name, strategy in self.strategies.items():
                try:
                    strategy.cleanup()
                except Exception as e:
                    self.ctx.logger.warning(f"Error cleaning up {strategy_name}: {str(e)}")

            self.strategies.clear()
            self.ctx.logger.info("Output interface shutdown completed")

        except Exception as e:
            self.ctx.logger.warning(f"Error during output interface cleanup: {str(e)}")


    def __enter__(self):
        """Context manager entry"""

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""

        self.cleanup()

#%%