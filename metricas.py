"""Métricas únicas del proyecto (A3). Dice e IoU salen de las mismas máscaras binarias."""
import numpy as np

EPS = 1e-7


def conteos(y_true, y_pred):
    """Arrays binarios (0/1 o bool). Devuelve (tp, fp, fn)."""
    t = np.asarray(y_true).astype(bool)
    p = np.asarray(y_pred).astype(bool)
    return (
        int(np.sum(t & p)),
        int(np.sum(~t & p)),
        int(np.sum(t & ~p)),
    )


def desde_conteos(tp, fp, fn):
    return {
        "dice": (2 * tp + EPS) / (2 * tp + fp + fn + EPS),
        "iou": (tp + EPS) / (tp + fp + fn + EPS),
        "precision": (tp + EPS) / (tp + fp + EPS),
        "recall": (tp + EPS) / (tp + fn + EPS),
    }