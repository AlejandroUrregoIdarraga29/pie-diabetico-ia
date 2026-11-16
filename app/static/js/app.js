let currentSessionId = null;

document.getElementById('threshold-range').addEventListener('input', (e) => {
    document.getElementById('threshold-val').textContent = parseFloat(e.target.value).toFixed(2);
});

document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const patientCode = document.getElementById('patient-code').value;
    const fileInput = document.getElementById('image-file').files[0];

    const formData = new FormData();
    formData.append('patient_code', patientCode);
    formData.append('file', fileInput);

    const response = await fetch('/api/v1/sessions/', { method: 'POST', body: formData });
    const data = await response.json();

    if (response.ok) {
        currentSessionId = data.session_id;
        document.getElementById('area-val').textContent = `${data.area_pixels} px²`;
        document.getElementById('session-status').textContent = data.status;
        const archivoOriginal = document.querySelector('input[type="file"]').files[0];

if (archivoOriginal) {
    document.getElementById('original-img').src =
        URL.createObjectURL(archivoOriginal);
}
        document.getElementById('preview-img').src = data.overlay_image;        document.getElementById('results-card').style.display = 'block';
    }
});

async function sendDecision(decisionType) {
    if (!currentSessionId) return;

    const threshold = parseFloat(document.getElementById('threshold-range').value);
    const notes = document.getElementById('doctor-notes').value;

    const response = await fetch(`/api/v1/sessions/${currentSessionId}/decision`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: decisionType, threshold: threshold, notes: notes })
    });

    if (response.ok) {
        alert(`Decisión '${decisionType}' enviada correctamente al hardware simulado.`);
    }
}

document.getElementById('btn-approve').addEventListener('click', () => {
    if (confirm("¿Confirma que desea APROBAR la segmentación e iniciar el procedimiento?")) {
        sendDecision("APPROVED");
    }
});

document.getElementById('btn-reject').addEventListener('click', () => sendDecision("REJECTED"));

document.getElementById('btn-emergency-stop').addEventListener('click', () => {
    alert("🚨 PARADA DE EMERGENCIA ENVIADA AL HARDWARE.");
});



/* ===== Guardar valoración clínica 2.1 ===== */


/* ===== Guardar valoración clínica 2.1 ===== */

document.getElementById('btn-save-assessment').addEventListener('click', async () => {
    const feedback = document.getElementById('assessment-feedback');
    const button = document.getElementById('btn-save-assessment');
    const form = document.getElementById('clinical-form');

    if (!currentSessionId) {
        feedback.textContent = 'Primero debes procesar una fotografía.';
        feedback.style.color = '#d9730d';
        return;
    }

    const formData = new FormData(form);
    const assessment = {};

    const numericFields = [
        'age',
        'local_temperature_c',
        'pain_level',
        'wound_length_mm',
        'wound_width_mm',
        'wound_depth_mm',
        'treatment_duration_days',
        'treatment_cost'
    ];

    const booleanFields = [
        'immunosuppressive_treatment',
        'necrosis',
        'surrounding_redness',
        'maceration'
    ];

    for (const [key, value] of formData.entries()) {
        if (value === '') {
            assessment[key] = null;
        } else if (numericFields.includes(key)) {
            assessment[key] = Number(value);
        } else if (booleanFields.includes(key)) {
            assessment[key] = value === 'true';
        } else {
            assessment[key] = value;
        }
    }

    button.disabled = true;
    feedback.textContent = 'Guardando valoración clínica...';
    feedback.style.color = '#5b6f87';

    try {
        const response = await fetch(
            `/api/v1/sessions/${currentSessionId}/assessment`,
            {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(assessment)
            }
        );

        if (!response.ok) {
            let detail = `Error HTTP ${response.status}`;
            try {
                const errorData = await response.json();
                detail += ': ' + JSON.stringify(errorData.detail);
            } catch (_) {}
            throw new Error(detail);
        }

        const result = await response.json();

        feedback.textContent =
            '✓ Valoración clínica guardada correctamente. Sesión: ' +
            result.session_id;

        feedback.style.color = '#14884a';

    } catch (error) {
        feedback.textContent =
            'No se pudo guardar la valoración: ' + error.message;

        feedback.style.color = '#d92d20';

    } finally {
        button.disabled = false;
    }
});

// Captura de fotografía con cámara IMX219 de Raspberry Pi
const cameraButton = document.getElementById('btn-capturar-camara');

if (cameraButton) {
    cameraButton.addEventListener('click', async () => {
        const feedback = document.getElementById('camera-feedback');
        const imageInput = document.getElementById('image-file');

        cameraButton.disabled = true;
        feedback.textContent = 'Capturando fotografía...';

        try {
            const response = await fetch('/api/v1/camera/capture', {
                method: 'GET',
                cache: 'no-store'
            });

            if (!response.ok) {
                throw new Error(
                    `No se pudo capturar la fotografía (HTTP ${response.status}).`
                );
            }

            const imageBlob = await response.blob();

            if (!imageBlob.type.startsWith('image/')) {
                throw new Error('La cámara no devolvió una imagen válida.');
            }

            const imageFile = new File(
                [imageBlob],
                'captura_imx219.jpg',
                { type: 'image/jpeg' }
            );

            const transfer = new DataTransfer();
            transfer.items.add(imageFile);
            imageInput.files = transfer.files;

            // Actualizar el nombre del archivo seleccionado.
            imageInput.dispatchEvent(new Event('change', {
                bubbles: true
            }));

            feedback.textContent = 'Fotografía capturada correctamente.';
            feedback.style.color = '#16803c';

        } catch (error) {
            feedback.textContent = error.message;
            feedback.style.color = '#c0392b';

        } finally {
            cameraButton.disabled = false;
        }
    });
}
