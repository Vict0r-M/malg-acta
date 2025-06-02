"""Data storage managers for persistent data"""

#%% Dependencies:

import json
from pathlib import Path
from typing import List, Any

#%% Clients Manager:

class ClientsManager:
    """Manager for client persistence and operations"""
    
    def __init__(self, ctx: Any) -> None:
        """Initialize with context"""
        
        self.ctx = ctx
        self.config = ctx.config
        self.logger = ctx.logger
        self.clients_file = Path(self.config.data_paths.clients_file)
        
        # Ensure data directory exists:
        self.clients_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize with default clients if file doesn't exist:
        if not self.clients_file.exists():
            self._create_default_clients()
    
    def load_clients(self) -> List[str]:
        """Load clients from JSON file"""
        
        try:
            if self.clients_file.exists():
                with open(self.clients_file, 'r', encoding='utf-8') as f:
                    clients = json.load(f)
                self.logger.info(f"Loaded {len(clients)} clients")
                return clients
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load clients: {str(e)}")
            return []
    
    def save_clients(self, clients: List[str]) -> bool:
        """Save clients to JSON file"""
        
        try:
            with open(self.clients_file, 'w', encoding='utf-8') as f:
                json.dump(clients, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(clients)} clients")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save clients: {str(e)}")
            return False
    
    def add_client(self, client_name: str) -> bool:
        """Add new client to list"""
        
        try:
            clients = self.load_clients()
            
            if client_name.strip() and client_name not in clients:
                clients.append(client_name.strip())
                return self.save_clients(clients)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to add client: {str(e)}")
            return False
    
    def _create_default_clients(self) -> None:
        """Create default clients list"""
        
        default_clients = [
            "AGREMIN SRL",
            "CONSTRUCT DEMO SRL", 
            "BETON QUALITY SA",
            "MATERIALS TEST LTD"
        ]
        
        self.save_clients(default_clients)
        self.logger.info("Created default clients list")

#%% Concrete Classes Manager:

class ConcreteClassesManager:
    """Manager for concrete class persistence and operations"""
    
    def __init__(self, ctx: Any) -> None:
        """Initialize with context"""
        
        self.ctx = ctx
        self.config = ctx.config
        self.logger = ctx.logger
        self.concrete_file = Path(self.config.data_paths.concrete_classes_file)
        
        # Ensure data directory exists:
        self.concrete_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize with default concrete classes if file doesn't exist:
        if not self.concrete_file.exists():
            self._create_default_concrete_classes()
    
    def load_concrete_classes(self) -> List[str]:
        """Load concrete classes from JSON file"""
        
        try:
            if self.concrete_file.exists():
                with open(self.concrete_file, 'r', encoding='utf-8') as f:
                    concrete_classes = json.load(f)
                self.logger.info(f"Loaded {len(concrete_classes)} concrete classes")
                return concrete_classes
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load concrete classes: {str(e)}")
            return []
    
    def save_concrete_classes(self, concrete_classes: List[str]) -> bool:
        """Save concrete classes to JSON file"""
        
        try:
            with open(self.concrete_file, 'w', encoding='utf-8') as f:
                json.dump(concrete_classes, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(concrete_classes)} concrete classes")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save concrete classes: {str(e)}")
            return False
    
    def add_concrete_class(self, concrete_class: str) -> bool:
        """Add new concrete class to list"""
        
        try:
            concrete_classes = self.load_concrete_classes()
            
            if concrete_class.strip() and concrete_class not in concrete_classes:
                concrete_classes.append(concrete_class.strip())
                return self.save_concrete_classes(concrete_classes)
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to add concrete class: {str(e)}")
            return False
    
    def _create_default_concrete_classes(self) -> None:
        """Create default concrete classes list"""
        
        default_classes = [
            "C 16/20",
            "C 20/25", 
            "C 25/30",
            "C 30/37",
            "C 35/45",
            "C 40/50"
        ]
        
        self.save_concrete_classes(default_classes)
        self.logger.info("Created default concrete classes list")

#%% Registry Manager:

class RegistryManager:
    """Manager for testing registry persistence"""
    
    def __init__(self, ctx: Any) -> None:
        """Initialize with context"""
        
        self.ctx = ctx
        self.config = ctx.config
        self.logger = ctx.logger
        self.registry_file = Path(self.config.data_paths.registry_file)
        
        # Ensure data directory exists:
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_registry(self) -> List[dict]:
        """Load registry from JSON file"""
        
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    registry = json.load(f)
                self.logger.info(f"Loaded {len(registry)} registry entries")
                return registry
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Failed to load registry: {str(e)}")
            return []
    
    def save_registry(self, registry: List[dict]) -> bool:
        """Save registry to JSON file"""
        
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Saved {len(registry)} registry entries")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save registry: {str(e)}")
            return False
    
    def add_entry(self, entry: dict) -> bool:
        """Add new entry to registry"""
        
        try:
            registry = self.load_registry()
            registry.append(entry)
            return self.save_registry(registry)
            
        except Exception as e:
            self.logger.error(f"Failed to add registry entry: {str(e)}")
            return False

#%%