import threading
import importlib
from typing import Any, Optional
import time

class LazyModule:
    """
    Thread-safe lazy loader for heavy modules
    Delays import until first access, then caches
    """
    def __init__(self, module_name: str):
        self._module_name = module_name
        self._module = None
        self._lock = threading.Lock()
        self._loading = False
    
    def _load(self):
        """Load module thread-safely"""
        if self._module is None:
            with self._lock:
                # Double-check locking pattern
                if self._module is None:
                    self._loading = True
                    try:
                        self._module = importlib.import_module(self._module_name)
                        print(f"✅ Lazy loaded: {self._module_name}")
                    except ImportError as e:
                        print(f"❌ Failed to load {self._module_name}: {e}")
                        self._module = None
                    finally:
                        self._loading = False
    
    def __getattr__(self, attr: str) -> Any:
        """Load module on first attribute access"""
        self._load()
        if self._module is None:
            raise ImportError(f"Could not load module: {self._module_name}")
        return getattr(self._module, attr)


# Lazy load heavy ML modules (can be imported by agents)
lazy_deepface = LazyModule('deepface')
lazy_librosa = LazyModule('librosa')
lazy_keybert = LazyModule('keybert')
lazy_spacy = LazyModule('spacy')
