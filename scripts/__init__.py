# scripts/__init__.py

from abc import ABC, abstractmethod

class ScriptInterface(ABC):
    @abstractmethod
    def run(self, input_file=None, output_file=None, **kwargs):
        pass

    @abstractmethod
    def get_metadata(self):
        pass
