"""Plugin manager - handles dynamic loading and lifecycle of all plugins"""

#%% Dependencies:

import importlib
from typing import Any, Dict, Type, List

#%% Plugin Manager:

class PluginManager:
    """
    Manages dynamic loading of plugins from external configuration
    Handles plugin discovery, loading, instantiation, and lifecycle management
    """

    def __init__(self, ctx: Any, plugin_config: Any):
        """Initialize plugin manager with context and plugin configuration"""

        self.ctx = ctx
        self.plugin_config = plugin_config

        # Plugin storage:
        self._plugin_configs = {}  # Processed configuration
        self._loaded_classes = {}  # Cache for loaded plugin classes

        # Process plugin configuration:
        self._process_plugin_config()

        self.ctx.logger.info(f"PluginManager initialized with {len(self._plugin_configs)} plugin categories")


    def _process_plugin_config(self) -> None:
        """Process plugin configuration object"""

        try:
            # Convert Box object to dictionary if needed:
            if hasattr(self.plugin_config, 'to_dict'):
                self._plugin_configs = self.plugin_config.to_dict()
            else:
                self._plugin_configs = dict(self.plugin_config)

            self.ctx.logger.info("Plugin configuration processed successfully")
            self._log_plugin_summary()

        except Exception as e:
            error_msg = f"Failed to process plugin configuration: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.ConfigurationError(error_msg)


    def _log_plugin_summary(self) -> None:
        """Log summary of loaded plugin configuration"""

        for category, plugins in self._plugin_configs.items():
            if isinstance(plugins, dict):
                total_count = len(plugins)
                self.ctx.logger.info(f"Plugin category '{category}': {total_count} plugins available")


    def get_available_plugins(self, category: str   # Plugin category
                             ) -> Dict[str, Dict]:  # Dictionary mapping plugin names to their metadata
        """Get metadata for all available plugins in a category"""

        if category not in self._plugin_configs:
            self.ctx.logger.warning(f"Plugin category '{category}' not found")
            return {}

        available = {}
        plugins = self._plugin_configs[category]

        if not isinstance(plugins, dict):
            self.ctx.logger.warning(f"Invalid plugin category format: {category}")
            return {}

        for name, config in plugins.items():
            if isinstance(config, dict):
                available[name] = {'description': config.get('description', ''),
                                   'module': config.get('module', ''),
                                   'class': config.get('class', '')}

        return available


    def get_strategy(self, category: str,  # Plugin category (e.g., "input")
                     strategy_name: str    # Name of strategy (e.g., "gui", "cli")
                    ) -> Any:              # Instance of the requested strategy
        """Get strategy instance by category and name (main API method)"""

        try:
            self.ctx.logger.info(f"Loading strategy: {category}.{strategy_name}")

            # Validate category exists:
            if category not in self._plugin_configs:
                available_categories = list(self._plugin_configs.keys())
                error_msg = f"Unknown plugin category '{category}'. Available: {available_categories}"
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.PluginError(error_msg)

            # Validate strategy exists in category:
            if strategy_name not in self._plugin_configs[category]:
                available_strategies = list(self._plugin_configs[category].keys())
                error_msg = f"Unknown strategy '{strategy_name}' in category '{category}'. Available: {available_strategies}"
                self.ctx.logger.error(error_msg)
                raise self.ctx.errors.PluginError(error_msg)

            # Load and return strategy instance:
            plugin_class = self._load_plugin_class(category, strategy_name)
            instance = plugin_class()

            self.ctx.logger.info(f"Strategy {category}.{strategy_name} loaded successfully")
            return instance

        except Exception as e:
            if isinstance(e, self.ctx.errors.PluginError):
                raise
            error_msg = f"Failed to get strategy {category}.{strategy_name}: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.PluginError(error_msg)


    def _load_plugin_class(self, category: str,  # Plugin category
                           strategy_name: str    # Strategy name within category
                          ) -> Type:             # Plugin class ready for instantiation
        """Dynamically import and load plugin class with caching"""

        cache_key = f"{category}.{strategy_name}"

        # Return cached class if available:
        if cache_key in self._loaded_classes:
            self.ctx.logger.info(f"Using cached plugin class: {cache_key}")
            return self._loaded_classes[cache_key]

        # Get plugin configuration:
        plugin_config = self._plugin_configs[category][strategy_name]

        # Validate required configuration fields:
        required_fields = ['module', 'class']
        missing_fields = [field for field in required_fields if field not in plugin_config]
        if missing_fields:
            error_msg = f"Plugin {cache_key} missing required fields: {missing_fields}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.PluginError(error_msg)

        try:
            module_name = plugin_config['module']
            class_name = plugin_config['class']

            self.ctx.logger.info(f"Importing plugin: {module_name}.{class_name}")

            # Dynamic import:
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, class_name)

            # Cache the loaded class:
            self._loaded_classes[cache_key] = plugin_class

            self.ctx.logger.info(f"Plugin class loaded successfully: {cache_key}")
            return plugin_class

        except ImportError as e:
            error_msg = f"Failed to import plugin module '{module_name}': {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.PluginError(error_msg)

        except AttributeError as e:
            error_msg = f"Plugin class '{class_name}' not found in module '{module_name}': {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.PluginError(error_msg)


    def create_plugin(self, category: str,  # Plugin category
                      strategy_name: str    # Strategy name within category
                     ) -> Any:              # Fresh instance of the requested plugin
        """Create plugin instance by category and name (alternative API)"""

        plugin_class = self._load_plugin_class(category, strategy_name)
        return plugin_class()


    def register_plugin_runtime(self, category: str,    # Plugin category
                                strategy_name: str,     # Strategy name
                                module: str,            # Python module path
                                class_name: str,        # Class name within module
                                description: str = ""   # Optional description
                               ) -> None:
        """Register a plugin at runtime for dynamic discovery"""

        try:
            # Ensure category exists:
            if category not in self._plugin_configs:
                self._plugin_configs[category] = {}

            # Register plugin:
            self._plugin_configs[category][strategy_name] = {'module': module,
                                                             'class': class_name,
                                                             'description': description,
                                                             'runtime_registered': True}

            self.ctx.logger.info(f"Registered runtime plugin: {category}.{strategy_name}")

        except Exception as e:
            error_msg = f"Failed to register runtime plugin {category}.{strategy_name}: {str(e)}"
            self.ctx.logger.error(error_msg)
            raise self.ctx.errors.PluginError(error_msg)


    def list_categories(self) -> List[str]:
        """Get list of all available plugin categories"""

        return list(self._plugin_configs.keys())


    def list_plugins(self, category: str  # Plugin category
                    ) -> List[str]:       # List of plugin names in the category
        """Get list of all plugin names in a category"""

        if category not in self._plugin_configs:
            return []

        plugins = self._plugin_configs[category]
        if not isinstance(plugins, dict):
            return []

        return list(plugins.keys())


    def plugin_exists(self, category: str,  # Plugin category
                      strategy_name: str    # Strategy name
                     ) -> bool:             # True if plugin exists in configuration
        """Check if a specific plugin exists"""

        if category not in self._plugin_configs:
            return False

        if strategy_name not in self._plugin_configs[category]:
            return False

        return isinstance(self._plugin_configs[category][strategy_name], dict)


    def get_plugin_info(self, category: str,  # Plugin category
                        strategy_name: str    # Strategy name
                       ) -> Dict[str, Any]:   # Dictionary with plugin information
        """Get detailed information about a specific plugin"""

        if category not in self._plugin_configs:
            return {}

        if strategy_name not in self._plugin_configs[category]:
            return {}

        plugin_config = self._plugin_configs[category][strategy_name]
        if not isinstance(plugin_config, dict):
            return {}

        cache_key = f"{category}.{strategy_name}"

        return {'category': category,
                'name': strategy_name,
                'module': plugin_config.get('module', ''),
                'class': plugin_config.get('class', ''),
                'description': plugin_config.get('description', ''),
                'runtime_registered': plugin_config.get('runtime_registered', False),
                'loaded': cache_key in self._loaded_classes}


    def cleanup(self) -> None:
        """Clean shutdown of plugin manager"""

        try:
            self.ctx.logger.info("Shutting down plugin manager...")

            # Clear all caches:
            self._loaded_classes.clear()

            self.ctx.logger.info("Plugin manager shutdown completed")

        except Exception as e:
            self.ctx.logger.warning(f"Error during plugin manager cleanup: {str(e)}")


    def __enter__(self):
        """Context manager entry"""

        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup"""

        self.cleanup()

#%%