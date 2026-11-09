from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parent
RESULTADOS_PC = BASE_DIR / "resultados" / "raspberry"
# Si la Raspberry guardó sus .npy en otra ruta o los tienes en una carpeta,
# ajusta RUTA_RASPBERRY. Por defecto asumimos los .npy generados en el repositorio.
RESULTADOS_RASP = BASE_DIR / "resultados" / "raspberry"

def comparar_inferencias():
    archivos_pc = sorted(RESULTADOS_PC.glob("*_probabilidades.npy"))
    
    if not archivos_pc:
        print("❌ No se encontraron archivos _probabilidades.npy en PC.")
        return

    print(f"=== COMPARANDO {len(archivos_pc)} IMÁGENES (PC vs. Raspberry) ===\n")
    print(f"{'Imagen':<12} | {'Max Dif. Prob':<15} | {'Píxeles Coincidentes':<22} | {'IoU Binario':<12}")
    print("-" * 70)

    coincidencias_totales = []

    for ruta_pc in archivos_pc:
        nombre_img = ruta_pc.stem.replace("_probabilidades", "")
        ruta_rasp = RESULTADOS_RASP / ruta_pc.name

        prob_pc = np.load(ruta_pc)

        # Si el archivo de la Raspberry existe en otra carpeta o sufijo, lo cargamos.
        # En caso de comparar la matriz contra el threshold estándar 0.5:
        mascara_pc = (prob_pc[0, :, :, 0] >= 0.5).astype(np.uint8)

        if ruta_rasp.exists():
            prob_rasp = np.load(ruta_rasp)
            mascara_rasp = (prob_rasp[0, :, :, 0] >= 0.5).astype(np.uint8)

            dif_max = np.max(np.abs(prob_pc - prob_rasp))
            coincidencia_pixeles = np.mean(mascara_pc == mascara_rasp) * 100
            
            # Cálculo de Intersection over Union (IoU)
            intersection = np.logical_and(mascara_pc, mascara_rasp).sum()
            union = np.logical_or(mascara_pc, mascara_rasp).sum()
            iou = 1.0 if union == 0 else intersection / union

            coincidencias_totales.append(coincidencia_pixeles)

            print(f"{nombre_img:<12} | {dif_max:<15.6f} | {coincidencia_pixeles:<21.2f}% | {iou:<12.4f}")
        else:
            print(f"{nombre_img:<12} | Archivo de la Raspberry Pi no encontrado en la ruta.")

    if coincidencias_totales:
        promedio = np.mean(coincidencias_totales)
        print("-" * 70)
        print(f"Coincidencia binaria promedio: {promedio:.2f}%\n")
        if promedio >= 99.0:
            print("✅ CRITERIO DE ACEPTACIÓN CUMPLIDO: Modelo TFLite equivalente entre PC y Raspberry Pi.")
        else:
            print("⚠️ Hay discrepancias significativas entre las máscaras binarias.")

if __name__ == "__main__":
    comparar_inferencias()