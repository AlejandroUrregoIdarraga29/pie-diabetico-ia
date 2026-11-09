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