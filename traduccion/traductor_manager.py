from transformers import MarianMTModel, MarianTokenizer


class Traductor:
    def __init__(self, modelo = "Helsinki-NLP/opus-mt-es-es"):
        """
        Inicializa el modelo y el tokenizador para la traducción es-en.
        """
        self.modelo = modelo
        self.tokenizer = MarianTokenizer.from_pretrained(modelo)
        self.model = MarianMTModel.from_pretrained(modelo)

    def traducir(self, texto):
        """
        Traduce un texto del español al inglés.
        """
        # Tokenización del texto
        texto_tokenizado = self.tokenizer(texto, return_tensors="pt", padding=True, truncation=True)

        # Generación de la traducción
        traduccion_ids = self.model.generate(**texto_tokenizado)

        # Decodificación del texto traducido
        texto_traducido = self.tokenizer.decode(traduccion_ids[0], skip_special_tokens=True)

        return texto_traducido
    
    def cambiar_modelo(self, modelo):
        self.cargar_modelo(modelo)
        print(f"Modelo dentro de traductor_manager:{self.modelo}")
        
    def cargar_modelo(self, modelo):
        self.model = modelo
        self.tokenizer = MarianTokenizer.from_pretrained(modelo)
        self.model = MarianMTModel.from_pretrained(modelo)
        

 