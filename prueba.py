import sounddevice as sd
import numpy as np

# Listar todos los dispositivos de audio disponibles
print(sd.query_devices())

# Seleccionar el dispositivo de salida específico por su índice o nombre
# Cambia esto por el nombre del dispositivo específico
device_name = "11 Altavoces (Realtek High Definition Audio)"
sd.default.device = device_name

# Reproducir un tono de prueba en el dispositivo seleccionado
duration = 5  # segundos
frequency = 440  # Hz
sample_rate = 44100  # Hz

t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * frequency * t)

sd.play(audio, samplerate=sample_rate)
sd.wait()  # Espera a que la reproducción termine
