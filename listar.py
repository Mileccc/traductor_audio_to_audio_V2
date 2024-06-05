import sounddevice as sd
import numpy as np

# Listar todos los dispositivos de audio disponibles
devices = sd.query_devices()

# Imprimir todos los dispositivos de salida de audio
for i, device in enumerate(devices):
    if device['max_output_channels'] > 0:
        print(f"Device ID {i}: {device['name']}")

# Seleccionar el dispositivo de salida específico por su ID
device_id = 11  # Cambia esto por el ID de tu dispositivo específico
sd.default.device = device_id

# Reproducir un tono de prueba en el dispositivo seleccionado
duration = 5  # segundos
frequency = 440  # Hz
sample_rate = 44100  # Hz

t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
audio = 0.5 * np.sin(2 * np.pi * frequency * t)

print(f"Reproduciendo en el dispositivo: {devices[device_id]['name']}")
sd.play(audio, samplerate=sample_rate)
sd.wait()  # Espera a que la reproducción termine
