from abc import ABC, abstractmethod
import numpy as np
import cv2
import base64

class SegmenterInterface(ABC):
    @abstractmethod
    def predict(self, image_bytes: bytes) -> tuple[np.ndarray, int, str]:
        pass

class CommandEmitterInterface(ABC):
    @abstractmethod
    def send_command(self, command: str) -> bool:
        pass

# --- IMPLEMENTACIONES MOCK (SIMULADORES) ---

class MockSegmenter(SegmenterInterface):
    def predict(self, image_bytes: bytes) -> tuple[np.ndarray, int, str]:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            img = np.zeros((256, 256, 3), dtype=np.uint8)
            
        h, w, _ = img.shape

        # Máscara sintética en el centro
        mask = np.zeros((h, w), dtype=np.uint8)
        ymin, ymax = int(h * 0.4), int(h * 0.6)
        xmin, xmax = int(w * 0.4), int(w * 0.6)
        mask[ymin:ymax, xmin:xmax] = 1
        area_px = int(np.sum(mask))

        # Generar Overlay Rojo
        overlay = img.copy()
        overlay[mask == 1] = [0, 0, 255] # BGR (Rojo)
        combined = cv2.addWeighted(img, 0.7, overlay, 0.3, 0)

        _, buffer = cv2.imencode('.png', combined)
        overlay_base64 = base64.b64encode(buffer).decode('utf-8')

        return mask, area_px, f"data:image/png;base64,{overlay_base64}"

class MockCommandEmitter(CommandEmitterInterface):
    def send_command(self, command: str) -> bool:
        print(f"[MOCK EMITTER] Comando enviado al hardware simulado: {command}")
        return True