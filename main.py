import asyncio
import threading
from voz_a_texto.captura_audio import AudioManager
from voz_a_texto.stt import TranscriptorATexto
from traduccion.traductor_manager import Traductor
from texto_a_voz.conversor_voz import TranscriptorAAudio
from comandos.atajos_comandos import EjecucionComandos


cola_audios = asyncio.Queue()
cola_textos = asyncio.Queue()
cola_traducciones = asyncio.Queue()
audio_ready_event = asyncio.Event()
traductor = Traductor()
transcriptor_audio = TranscriptorAAudio()


async def tomando_audio():
    print("Configurando la captura de audio...")
    loop = asyncio.get_running_loop()
    configurador_audio = AudioManager(cola_audios, loop)
    hilo_captura_audio = threading.Thread(target=configurador_audio.escucha)
    hilo_captura_audio.daemon = True
    hilo_captura_audio.start()
    print("Hilo de captura de audio iniciado.")


async def transcribir_audio():
    print("Transcriptor configurado, esperando audio...")
    transcriptor = TranscriptorATexto()
    comando = EjecucionComandos(traductor, transcriptor_audio)
    loop = asyncio.get_running_loop()
    while True:
        datos_audio = await cola_audios.get()
        if datos_audio:
            texto = await transcriptor.transcribe_audio(datos_audio, loop)
            comando.revisar_comando(texto)
            if texto.strip():
                print(f"Texto transcribido: {texto}")
                await cola_textos.put(texto)


async def traducir_texto():
    print("Configurando el traductor...")
    # traductor = Traductor(modelos=["Helsinki-NLP/opus-mt-es-en", "Helsinki-NLP/opus-mt-en-fr"])

    loop = asyncio.get_running_loop()
    while True:
        texto = await cola_textos.get()
        if texto.strip():
            # texto_traducido = await loop.run_in_executor(None, traductor.traducir_secuencial, texto)
            texto_traducido = await loop.run_in_executor(None, traductor.traducir, texto)
            print(f"Texto traducido: {texto_traducido}")
            await cola_traducciones.put(texto_traducido)


async def convertir_texto_a_audio(transcriptor_audio):
    print("Transcriptor a audio configurado, esperando texto traducido...")
    while True:
        texto_traducido = await cola_traducciones.get()
        if texto_traducido.strip():
            await transcriptor_audio.texto_a_audio(texto_traducido)


async def main():
    transcriptor_audio.iniciar_modelo()

    tasks = [
        asyncio.create_task(tomando_audio()),
        asyncio.create_task(transcribir_audio()),
        asyncio.create_task(traducir_texto()),
        asyncio.create_task(convertir_texto_a_audio(transcriptor_audio)),
        asyncio.create_task(transcriptor_audio.reproducir_audios())
    ]

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("Tareas canceladas. Finalizando limpiamente.")

if __name__ == "__main__":
    asyncio.run(main())
