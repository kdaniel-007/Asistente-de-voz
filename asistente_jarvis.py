import customtkinter as ctk
import pyttsx3
from threading import Thread, Event
import PyPDF2
from docx import Document
from tkinter import filedialog, messagebox
import re

class AsistenteJARVIS:
    def __init__(self):
        # Configurar motor de texto a voz
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.texto_completo = ""
        self.oraciones = []  # Lista de oraciones
        self.posicion_actual = 0
        self.leyendo = False
        self.pausado = False
        self.stop_event = Event()

        # Configurar la voz predeterminada
        self.engine.setProperty('voice', self.voices[0].id)  # Establece la primera voz disponible
        self.engine.setProperty('rate', 150)  # Velocidad predeterminada

        # Crear ventana principal
        self.ventana = ctk.CTk()
        self.ventana.title("Asistente Virtual J.A.R.V.I.S.")
        self.ventana.geometry("700x700")

        # Widgets principales
        self.titulo = ctk.CTkLabel(self.ventana, text="Asistente Virtual J.A.R.V.I.S.", font=("Arial", 24))
        self.titulo.pack(pady=20)

        self.texto_area = ctk.CTkTextbox(self.ventana, height=200, width=600)
        self.texto_area.pack(pady=10)

        # Contenedor para los botones
        self.frame_botones = ctk.CTkFrame(self.ventana)
        self.frame_botones.pack(pady=20)

        self.boton_cargar = ctk.CTkButton(self.frame_botones, text="Cargar Documento", command=self.cargar_documento)
        self.boton_cargar.grid(row=0, column=0, padx=10, pady=10)

        self.boton_leer = ctk.CTkButton(self.frame_botones, text="Leer Documento", command=self.iniciar_lectura)
        self.boton_leer.grid(row=0, column=1, padx=10, pady=10)

        self.boton_pausar = ctk.CTkButton(self.frame_botones, text="Pausar", command=self.pausar_lectura)
        self.boton_pausar.grid(row=1, column=0, padx=10, pady=10)

        self.boton_reanudar = ctk.CTkButton(self.frame_botones, text="Reanudar", command=self.reanudar_lectura)
        self.boton_reanudar.grid(row=1, column=1, padx=10, pady=10)

        # Configuración de voz y velocidad
        self.frame_configuracion = ctk.CTkFrame(self.ventana)
        self.frame_configuracion.pack(pady=20)

        self.label_voz = ctk.CTkLabel(self.frame_configuracion, text="Seleccionar Voz:")
        self.label_voz.grid(row=0, column=0, padx=10)

        # Crear lista de voces disponibles en el sistema
        voces_disponibles = [voice.name for voice in self.voices]

        # Menú desplegable para seleccionar voz
        self.selector_voz = ctk.CTkOptionMenu(self.frame_configuracion, values=voces_disponibles, command=self.cambiar_voz)
        self.selector_voz.grid(row=0, column=1, padx=10)
        self.selector_voz.set(self.voices[0].name)  # Voz predeterminada

        self.label_velocidad = ctk.CTkLabel(self.frame_configuracion, text="Velocidad de Voz:")
        self.label_velocidad.grid(row=1, column=0, padx=10)

        self.slider_velocidad = ctk.CTkSlider(self.frame_configuracion, from_=50, to=300, command=self.cambiar_velocidad)
        self.slider_velocidad.set(150)
        self.slider_velocidad.grid(row=1, column=1, padx=10)

    def cambiar_voz(self, nombre_voz):
        for voice in self.voices:
            if voice.name == nombre_voz:
                self.engine.setProperty('voice', voice.id)
                break

    def cambiar_velocidad(self, valor):
        self.engine.setProperty('rate', int(valor))

    def cargar_documento(self):
        ruta = filedialog.askopenfilename(filetypes=[("Archivos PDF", "*.pdf"),
                                                     ("Documentos Word", "*.docx"),
                                                     ("Archivos de texto", "*.txt")])
        if ruta:
            try:
                texto = self.extraer_texto(ruta)
                self.texto_area.delete("1.0", "end")
                self.texto_area.insert("1.0", texto)
                self.texto_completo = texto
                self.oraciones = re.split(r'(?<=[.!?]) +', texto)
                self.posicion_actual = 0
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el documento: {e}")

    def extraer_texto(self, ruta):
        if ruta.endswith(".pdf"):
            return self.leer_pdf(ruta)
        elif ruta.endswith(".docx"):
            return self.leer_docx(ruta)
        elif ruta.endswith(".txt"):
            with open(ruta, "r", encoding="utf-8") as archivo:
                return archivo.read()
        else:
            raise ValueError("Formato no soportado. Usa PDF, DOCX o TXT.")

    def leer_pdf(self, ruta):
        texto = ""
        with open(ruta, "rb") as archivo:
            lector = PyPDF2.PdfReader(archivo)
            for pagina in lector.pages:
                texto += pagina.extract_text()
        return texto

    def leer_docx(self, ruta):
        doc = Document(ruta)
        return "\n".join(parrafo.text for parrafo in doc.paragraphs)

    def iniciar_lectura(self):
        if not self.texto_completo:
            messagebox.showwarning("Advertencia", "Primero carga un documento.")
            return
        if self.leyendo:
            messagebox.showinfo("Información", "Ya estoy leyendo.")
            return
        self.leyendo = True
        self.stop_event.clear()
        self._hilo_lectura = Thread(target=self.leer_texto)
        self._hilo_lectura.start()

    def leer_texto(self):
        for i in range(self.posicion_actual, len(self.oraciones)):
            if self.stop_event.is_set():
                self.posicion_actual = i
                break
            self.engine.say(self.oraciones[i])
            self.engine.runAndWait()
        self.leyendo = False

    def pausar_lectura(self):
        if self.leyendo:
            self.stop_event.set()
            self.engine.stop()
            self.pausado = True

    def reanudar_lectura(self):
        if self.pausado:
            self.stop_event.clear()
            self.pausado = False
            self.leyendo = True
            self._hilo_lectura = Thread(target=self.leer_texto)
            self._hilo_lectura.start()

    def iniciar(self):
        self.ventana.mainloop()

# Iniciar el asistente
if __name__ == "__main__":
    asistente = AsistenteJARVIS()
    asistente.iniciar()