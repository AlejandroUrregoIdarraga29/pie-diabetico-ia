
#include <Arduino.h>
#include <SPI.h>

// ESP32-S3 y MCP4822: SIN CAMBIOS
constexpr uint8_t PIN_CS = 10;
constexpr uint8_t PIN_SCK = 12;
constexpr uint8_t PIN_MOSI = 11;

// MCP4822: SIN CAMBIOS
constexpr uint16_t DAC_A = 0x3000;
constexpr uint16_t DAC_B = 0xB000;

constexpr uint16_t NIVEL_A = 2048;
constexpr uint16_t NIVEL_B = 1024;

// Tiempos originales: SIN CAMBIOS
constexpr uint32_t T_A_MS = 200;
constexpr uint32_t GAP_MS = 100;
constexpr uint32_t T_B_MS = 400;
constexpr uint32_t REPOSO_MS = 1300;

// Control desde Raspberry Pi
constexpr uint32_t TIMEOUT_MS = 5000;

bool generacionActiva = false;
uint32_t ultimoContacto = 0;

void escribirDAC(uint16_t canal, uint16_t valor) {
    valor = constrain(valor, 0, 4095);

    SPI.beginTransaction(
        SPISettings(1000000, MSBFIRST, SPI_MODE0)
    );

    digitalWrite(PIN_CS, LOW);
    SPI.transfer16(canal | valor);
    digitalWrite(PIN_CS, HIGH);

    SPI.endTransaction();
}

void salidasCero() {
    escribirDAC(DAC_A, 0);
    escribirDAC(DAC_B, 0);
}

void detenerGeneracion(const char* motivo) {
    generacionActiva = false;
    salidasCero();
    Serial0.println(motivo);
}

void revisarComandos() {
    while (Serial0.available()) {
        char comando = Serial0.read();

        if (comando == 's') {
            ultimoContacto = millis();

            if (!generacionActiva) {
                generacionActiva = true;
                Serial0.println("GENERACION ACTIVADA");
            }
        }

        else if (comando == 'h') {
            if (generacionActiva) {
                ultimoContacto = millis();
            }
        }

        else if (comando == 'p') {
            detenerGeneracion("GENERACION DETENIDA");
        }
    }

    if (generacionActiva &&
        (uint32_t)(millis() - ultimoContacto) >= TIMEOUT_MS) {
        detenerGeneracion("DETENIDA: SIN COMUNICACION");
    }
}

// Espera sin perder la capacidad de detener
bool esperarControlado(uint32_t duracionMs) {
    uint32_t inicio = millis();

    while ((uint32_t)(millis() - inicio) < duracionMs) {
        revisarComandos();

        if (!generacionActiva) {
            return false;
        }

        delay(1);
    }

    return true;
}

void setup() {
    // Puerto USB-UART de la ESP32-S3
    Serial0.begin(115200);

    pinMode(PIN_CS, OUTPUT);
    digitalWrite(PIN_CS, HIGH);

    SPI.begin(PIN_SCK, -1, PIN_MOSI, PIN_CS);

    // Arranque seguro: sin pulsos
    salidasCero();

    Serial0.println("NOVA LUZ");
    Serial0.println("MCP4822 LISTO");
    Serial0.println("ESPERANDO COMANDO");
    Serial0.println("s = INICIAR");
    Serial0.println("p = DETENER");
    Serial0.println("h = MANTENER COMUNICACION");
}

void loop() {
    revisarComandos();

    if (!generacionActiva) {
        delay(1);
        return;
    }

    // Fase positiva: A > B
    escribirDAC(DAC_B, 0);
    escribirDAC(DAC_A, NIVEL_A);

    if (!esperarControlado(T_A_MS)) return;

    // Intervalo sin tension diferencial
    salidasCero();

    if (!esperarControlado(GAP_MS)) return;

    // Fase negativa: B > A
    escribirDAC(DAC_A, 0);
    escribirDAC(DAC_B, NIVEL_B);

    if (!esperarControlado(T_B_MS)) return;

    // Reposo
    salidasCero();

    if (!esperarControlado(REPOSO_MS)) return;

    Serial0.println("Ciclo bifasico completado");
}
