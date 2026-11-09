from abc import ABC, abstractmethod
import numpy as np

class SegmenterInterface(ABC):
    @abstractmethod
    def predict(self, image_bytes: bytes) -> tuple[np.ndarray, int]:
        pass

class CommandEmitterInterface(ABC):
    @abstractmethod
    def send_command(self, command: str) -> bool:
        pass

# Implementación Mock para PC
class MockSegmenter(SegmenterInterface):
    def predict(self, image_bytes: bytes) -> tuple[np.ndarray, int]:
        mask = np.zeros((256, 256), dtype=np.uint8)
        mask[100:150, 100:150] = 1
        return mask, 2500

class MockCommandEmitter(CommandEmitterInterface):
    def send_command(self, command: str) -> bool:
        print(f"[MOCK EMITTER] Comando enviado al hardware: {command}")
        return True