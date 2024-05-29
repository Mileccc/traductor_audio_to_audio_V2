import asyncio
import threading
from queue import Empty
from traduccion.traductor_manager import Traductor
import re


class EjecucionComandos(threading.Thread):

    def __init__(self, evento_terminacion_procesos, cola_verificacion, cola_traduccion, evento_activacion_audio):
        super().__init__()
        self.cola_verificacion = cola_verificacion
        self.evento_terminacion_procesos = evento_terminacion_procesos
        self.cola_traduccion = cola_traduccion
        self.evento_activacion_audio = evento_activacion_audio
        self.variantes_frances = ["francés", "frances", "frances,", "frances."]
        self.variantes_espanol = ["español", "espanol", "espanol,", "espanol."]
        self.variantes_arabe = ["árabe", "arabe", "arabe,", "arabe."]
        self.variantes_chino = ["chino", "chino,", "chino."]
        self.variantes_ruso = ["ruso", "ruso,",
                               "ruso.", "russo", "russo,", "russo."]
        self.variantes_aleman = ["alemán", "aleman", "aleman,", "aleman."]
        self.variantes_ingles = ["inglés", "ingles", "ingles,", "ingles."]
        self.variantes_italiano = ["italiano", "italiano,", "italiano."]

    def run(self):
        while not self.evento_terminacion_procesos.is_set():
            try:
                texto = self.cola_verificacion.get(timeout=60)
                texto = re.sub(r'\.\.\.|[.,]', '', texto)
                self.revisar_comando(texto)
            except Empty:
                continue

    def revisar_comando(self, texto):
        if "detener" in texto.lower():
            self.evento_terminacion_procesos.set()
            return

        comando_detectado = False

        if any(variacion in texto.lower() for variacion in self.variantes_frances):
            self.cola_traduccion.put({
                "path_hablante": "es_fr/f10_script2_clean_segment_8.wav_fr_173.wav",
                "idioma": "fr",
                "modelo": "Helsinki-NLP/opus-mt-es-fr",
                "texto": texto
            })
            comando_detectado = True

        if any(variacion in texto.lower() for variacion in self.variantes_espanol):
            self.cola_traduccion.put({
                "path_hablante": "es_es/m4_script2_clean_segment_0.wav_es_2748.wav",
                "idioma": "es",
                "modelo": "Helsinki-NLP/opus-mt-es-es",
                "texto": texto
            })
            comando_detectado = True

        if any(variacion in texto.lower() for variacion in self.variantes_arabe):
            self.cola_traduccion.put({
                "path_hablante": "es_ar/m4_script2_clean_segment_0.wav_ar_2693.wav",
                "idioma": "ar",
                "modelo": "Helsinki-NLP/opus-mt-es-ar",
                "texto": texto
            })
            comando_detectado = True

        if any(variacion in texto.lower() for variacion in self.variantes_chino):
            self.cola_traduccion.put({
                "path_hablante": "es_cn/f1_script1_clean_segment_0.wav_zh-cn_308.wav",
                "idioma": "zh-cn",
                "modelo": "Helsinki-NLP/opus-mt-es-tw",
                "texto": texto
            })
            comando_detectado = True

        if any(variacion in texto.lower() for variacion in self.variantes_ruso):
            self.cola_traduccion.put({
                "path_hablante": "es_ru/m6_script1_clean_segment_30.wav_ru_3075.wav",
                "idioma": "ru",
                "modelo": "Helsinki-NLP/opus-mt-es-ru",
                "texto": texto
            })
            comando_detectado = True

        if any(variacion in texto.lower() for variacion in self.variantes_aleman):
            self.cola_traduccion.put({
                "path_hablante": "es_de/m9_script2_clean_segment_4.wav_de_3678.wav",
                "idioma": "de",
                "modelo": "Helsinki-NLP/opus-mt-es-de",
                "texto": texto
            })
            comando_detectado = True

        if any(variacion in texto.lower() for variacion in self.variantes_ingles):
            self.cola_traduccion.put({
                "path_hablante": "es_en/2.wav",
                "idioma": "en",
                "modelo": "Helsinki-NLP/opus-mt-es-en",
                "texto": texto
            })
            comando_detectado = True

        if any(variacion in texto.lower() for variacion in self.variantes_italiano):
            self.cola_traduccion.put({
                "path_hablante": "es_it/m2_script1_clean_segment_7.wav_it_2395.wav",
                "idioma": "it",
                "modelo": "Helsinki-NLP/opus-mt-es-it",
                "texto": texto
            })
            comando_detectado = True

        if "pausar audio" in texto.lower():
            print("Pausando el audio...")
            self.evento_activacion_audio.set()
            print("Audio pausado añadido a la cola.")
            comando_detectado = True

        if "activar audio" in texto.lower():
            print("Activando el audio...")
            self.evento_activacion_audio.clear()

            comando_detectado = True

        if not comando_detectado:
            self.cola_traduccion.put({
                "path_hablante": "",
                "idioma": "",
                "modelo": "",
                "texto": texto
            })
