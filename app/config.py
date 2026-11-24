from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    ENV_MODE: str = "development"
    USE_MOCKS: bool = True
    DATABASE_URL: str = "sqlite:///./data/pie_diabetico.db"
    MODEL_PATH: str = "modelos/unet_fuseg_baseline.tflite"
    PORT: int = 8000
    MQTT_HOST: str = "192.168.1.53"
    MQTT_PORT: int = 1883
    MQTT_TOPIC_TEST: str = "nova_luz/test"
    MQTT_ENABLED: bool = False

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()