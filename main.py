
import asyncio
import multiprocessing
import time
import signal
import sys
import queue
from voz_a_texto.captura_audio import AudioManager
from voz_a_texto.stt import TranscriptorATexto
from traduccion.traductor_manager import Traductor
# from texto_a_voz.conversor_voz import TranscriptorAAudio
from comandos.atajos_comandos import EjecucionComandos
# from texto_a_voz.reproducir_audio import Reproductor
from texto_a_voz.conversor_server import TranscriptorAAudio


def salida(signum, frame, evento_terminacion_procesos, lista):
    print("Señal de terminación capturada, cerrando todo...")
    evento_terminacion_procesos.set()
    for proceso in lista:
        proceso.terminate()
    for proceso in lista:
        proceso.join()
    print("Todos los procesos y el hilo han sido terminados correctamente.")
    sys.exit(0)

# ********************AUDIO ENTRADA ************************


async def funcion_audio_entrada(evento_terminacion_procesos, cola_verificacion):
    colo_audio_micro = queue.Queue()

    microfono = AudioManager(evento_terminacion_procesos, colo_audio_micro)
    audio_a_texto = TranscriptorATexto(
        colo_audio_micro, cola_verificacion, evento_terminacion_procesos)

    microfono.start()
    await audio_a_texto.run()
    microfono.join()


def audio_entrada(evento_terminacion_procesos, cola_verificacion):
    asyncio.run(funcion_audio_entrada(
        evento_terminacion_procesos, cola_verificacion))

# ********************TRATAR TEXTO ************************


def funcion_tratar_texto(cola_verificacion, evento_terminacion_procesos, cola_traduccion, cola_traduccion_a_audio, evento_activacion_audio):
    comandos = EjecucionComandos(
        evento_terminacion_procesos, cola_verificacion, cola_traduccion, evento_activacion_audio)
    traductor = Traductor(
        cola_traduccion, cola_traduccion_a_audio, evento_terminacion_procesos)

    comandos.start()
    traductor.start()
    comandos.join()
    traductor.join()


def tratar_texto(cola_verificacion, evento_terminacion_procesos, cola_traduccion, cola_traduccion_a_audio, evento_activacion_audio):
    funcion_tratar_texto(
        cola_verificacion, evento_terminacion_procesos, cola_traduccion, cola_traduccion_a_audio, evento_activacion_audio)

# ********************AUDIO SALIDA ************************


def funcion_audio_salida(evento_terminacion_procesos, cola_traduccion_a_audio, evento_activacion_audio):
    cola_audios_final = queue.Queue()
    texto_a_audio = TranscriptorAAudio(
        evento_terminacion_procesos, cola_traduccion_a_audio, evento_activacion_audio)

    texto_a_audio.start()
    texto_a_audio.join()


def audio_salida(evento_terminacion_procesos, cola_traduccion_a_audio, evento_activacion_audio):
    funcion_audio_salida(
        evento_terminacion_procesos, cola_traduccion_a_audio, evento_activacion_audio)


def main():
    # EVENTOS
    evento_terminacion_procesos = multiprocessing.Event()
    evento_activacion_audio = multiprocessing.Event()

    # COLAS
    cola_verificacion = multiprocessing.Queue()
    cola_traduccion = multiprocessing.Queue()
    cola_traduccion_a_audio = multiprocessing.Queue()

    # PROCESOS
    proceso_audio_entrada = multiprocessing.Process(
        target=audio_entrada, args=(evento_terminacion_procesos, cola_verificacion))
    proceso_tratar_texto = multiprocessing.Process(
        target=tratar_texto, args=(cola_verificacion, evento_terminacion_procesos, cola_traduccion, cola_traduccion_a_audio, evento_activacion_audio))
    proceso_audio_salida = multiprocessing.Process(
        target=audio_salida, args=(evento_terminacion_procesos, cola_traduccion_a_audio, evento_activacion_audio))

    lista_procesos = [proceso_audio_entrada,
                      proceso_tratar_texto, proceso_audio_salida]

    signal.signal(signal.SIGINT, lambda s, f: salida(
        s, f, evento_terminacion_procesos, lista_procesos))
    signal.signal(signal.SIGTERM, lambda s, f: salida(
        s, f, evento_terminacion_procesos, lista_procesos))

    for proceso in lista_procesos:
        proceso.start()

    try:
        while not evento_terminacion_procesos.is_set():
            time.sleep(5)
            for proceso in lista_procesos:
                if not proceso.is_alive():
                    evento_terminacion_procesos.set()
                    print(f"Proceso {proceso.name} ha terminado")
    except KeyboardInterrupt:
        print("SAliendo por interrupción de teclado..")
    finally:
        for proceso in lista_procesos:
            proceso.terminate()
        for proceso in lista_procesos:
            proceso.join()
        print("Todos los procesos y el hilo han sido terminados correctamente.")


if __name__ == "__main__":
    main()
