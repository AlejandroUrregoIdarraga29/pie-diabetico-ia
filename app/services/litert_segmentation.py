
import base64
from pathlib import Path
from threading import Lock

import cv2
import numpy as np

from app.services.interfaces import SegmenterInterface


class LiteRTSegmentationService(SegmenterInterface):
    """Segmentación real mediante U-Net exportada a TFLite."""

    def __init__(self, model_path: str):
        try:
            from ai_edge_litert.interpreter import Interpreter
        except ImportError:
            try:
                from tflite_runtime.interpreter import Interpreter
            except ImportError as exc:
                raise RuntimeError(
                    "LiteRT no está instalado en este entorno."
                ) from exc

        path = Path(model_path)
        if not path.is_file():
            raise FileNotFoundError(f"Modelo no encontrado: {path}")

        self.interpreter = Interpreter(model_path=str(path))
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()[0]
        self.output_details = self.interpreter.get_output_details()[0]
        self.lock = Lock()

        shape = self.input_details["shape"]

        if len(shape) != 4 or shape[0] != 1 or shape[3] != 3:
            raise ValueError(f"Entrada incompatible: {shape}")

        if self.input_details["dtype"] != np.float32:
            raise ValueError("El modelo requiere una entrada float32.")

        self.height = int(shape[1])
        self.width = int(shape[2])

    def predict(self, image_bytes: bytes) -> tuple[np.ndarray, int, str]:
        # 1. Decodificar la fotografía.
        image_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image_bgr = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        if image_bgr is None:
            raise ValueError("No se pudo decodificar la imagen enviada.")

        # 2. Preparar entrada RGB normalizada, como en inferencia_raspberry.py.
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(
            image_rgb,
            (self.width, self.height),
            interpolation=cv2.INTER_LINEAR,
        )

        input_tensor = np.expand_dims(
            resized.astype(np.float32) / 255.0,
            axis=0,
        )

        # 3. Ejecutar la inferencia real con LiteRT.
        with self.lock:
            self.interpreter.set_tensor(
                self.input_details["index"],
                input_tensor,
            )
            self.interpreter.invoke()
            prediction = self.interpreter.get_tensor(
                self.output_details["index"]
            ).copy()

        # 4. Convertir probabilidades a máscara binaria.
        probabilities = prediction[0, :, :, 0]
        mask_small = (probabilities >= 0.5).astype(np.uint8)

        # 5. Adaptar máscara a la resolución original.
        original_height, original_width = image_bgr.shape[:2]

        mask = cv2.resize(
            mask_small,
            (original_width, original_height),
            interpolation=cv2.INTER_NEAREST,
        )

        area_px = int(np.count_nonzero(mask))

        # 6. Generar overlay rojo compatible con la página de Johan.
        overlay = image_bgr.copy()
        overlay[mask == 1] = (0, 0, 255)

        combined = cv2.addWeighted(
            image_bgr, 0.7, overlay, 0.3, 0
        )

        success, buffer = cv2.imencode(".png", combined)

        if not success:
            raise RuntimeError("No se pudo generar el overlay PNG.")

        overlay_base64 = base64.b64encode(buffer).decode("utf-8")
        overlay_uri = f"data:image/png;base64,{overlay_base64}"

        return mask, area_px, overlay_uri
