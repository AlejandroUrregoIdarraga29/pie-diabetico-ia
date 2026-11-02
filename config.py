from pathlib import Path

# Raíz del repositorio: la carpeta donde está este archivo
REPO_DIR = Path(__file__).resolve().parent

# Datos: submódulo wound-segmentation
DATA_DIR = (
    REPO_DIR / "wound-segmentation" / "data" / "Foot Ulcer Segmentation Challenge"
)

# Salidas (no se versionan)
MODELOS_DIR = REPO_DIR / "modelos"
RESULTADOS_DIR = REPO_DIR / "resultados"
REPORTS_DIR = REPO_DIR / "reports"


def asegurar_carpetas():
    for carpeta in (MODELOS_DIR, RESULTADOS_DIR, REPORTS_DIR):
        carpeta.mkdir(parents=True, exist_ok=True)


def exigir_archivos(carpeta, patron="*.png"):
    """Devuelve los archivos o termina con un error claro si no hay ninguno."""
    carpeta = Path(carpeta)
    if not carpeta.is_dir():
        raise SystemExit(
            f"ERROR: no existe {carpeta}. ¿Clonaste con --recurse-submodules?"
        )
    archivos = sorted(carpeta.glob(patron))
    if not archivos:
        raise SystemExit(f"ERROR: 0 archivos {patron} en {carpeta}")
    print(f"{carpeta}: {len(archivos)} archivos")
    return archivos

def binarizar(mascara):
    """Criterio único: cualquier píxel > 0 es úlcera (incluye el borde de la 0233)."""
    return (mascara > 0).astype("uint8")