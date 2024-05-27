import asyncio
from traduccion.traductor_manager import Traductor


class EjecucionComandos:

    def __init__(self, traductor, transcriptor_audio):
        self.texto = ""
        self.traductor = traductor
        self.transcriptor_audio = transcriptor_audio

    def revisar_comando(self, texto):
        if "detener" in texto.lower():
            print("deteniendo la ejecución...")
            raise asyncio.CancelledError

        if "francés" in (texto.lower()):
            print("Traduciendo al francés...")
            self.transcriptor_audio.set_hablante(
                "D:\\ProyectoTraductor\\Traductor_en_tiempo_real\\speakers\\es_fr\\f10_script2_clean_segment_8.wav_fr_173.wav", "fr")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-fr")

        if "español" in (texto.lower()):
            print("Traduciendo al español...")
            self.transcriptor_audio.set_hablante(
                "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_es\m4_script2_clean_segment_0.wav_es_2748.wav", "es")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-es")

        if "árabe" in (texto.lower()):
            print("Traduciendo al arabe...")
            self.transcriptor_audio.set_hablante(
                "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_ar\m4_script2_clean_segment_0.wav_ar_2693.wav", "ar")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-ar")

        if "chino" in (texto.lower()):
            print("Traduciendo al chino...")
            self.transcriptor_audio.set_hablante(
                "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_cn\\f1_script1_clean_segment_0.wav_zh-cn_308.wav", "zh-cn")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-tw")

        if "ruso" in (texto.lower()):
            print("Traduciendo al ruso...")
            self.transcriptor_audio.set_hablante(
                "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_ru\m6_script1_clean_segment_30.wav_ru_3075.wav", "ru")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-ru")

        if "alemán" in (texto.lower()):
            print("Traduciendo al aleman...")
            self.transcriptor_audio.set_hablante(
                "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_ru\m4_script2_clean_segment_0.wav_ru_2739.wav", "de")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-de")

        if "inglés" in (texto.lower()):
            print("Traduciendo al inglés...")
            self.transcriptor_audio.set_hablante(
                "D:\\ProyectoTraductor\\Traductor_en_tiempo_real\\speakers\\es_en\\2.wav", "en")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-en")

        if "italiano" in (texto.lower()):
            print("Traduciendo al italiano...")
            self.transcriptor_audio.set_hablante(
                "D:\ProyectoTraductor\Traductor_en_tiempo_real\speakers\es_it\m2_script1_clean_segment_7.wav_it_2395.wav", "it")
            self.traductor.cambiar_modelo("Helsinki-NLP/opus-mt-es-it")

        if "pausar audio" in (texto.lower()):
            print("Pausando el audio...")
            self.transcriptor_audio.pausar_audio()

        if "activar audio" in (texto.lower()):
            print("Reproduciendo el audio...")
            self.transcriptor_audio.reanudar_audio()
