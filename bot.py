import requests
import os
import time

# --- 1. Configuración de Secretos (GitHub los inyectará) ---
API_KEY = os.environ['PARSEHUB_API_KEY']
PROJECT_TOKEN = os.environ['PARSEHUB_PROJECT_TOKEN']
WEBHOOK_URL = os.environ['DISCORD_WEBHOOK']
ARCHIVO_HISTORIAL = "publicadas.txt"

# --- 2. Cargar historial de URLs ya publicadas ---
try:
    with open(ARCHIVO_HISTORIAL, 'r') as f:
        urls_publicadas = set(line.strip() for line in f)
except FileNotFoundError:
    urls_publicadas = set()
print(f"Cargadas {len(urls_publicadas)} URLs del historial.")

# --- 3. Obtener datos de ParseHub ---
# Esta URL obtiene los datos del *último run completado*
print("Obteniendo datos del último run completado de ParseHub...")
try:
    r = requests.get(f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data", params={"api_key": API_KEY})
    r.raise_for_status() # Lanza un error si la solicitud falla
    data = r.json()
except requests.exceptions.RequestException as e:
    print(f"Error al obtener datos de ParseHub: {e}")
    exit(1) # Salir con error

# IMPORTANTE: Asegúrate de que tu lista en ParseHub se llama 'noticias'
lista_de_noticias = data.get('noticias', []) 
if not lista_de_noticias:
    print("Error: No se encontró la lista 'noticias' en el JSON. Revisa tu script de ParseHub.")
    print(f"Datos recibidos: {data}")
    exit(1)

nuevas_noticias = []

# --- 4. Filtrar noticias nuevas ---
for noticia in lista_de_noticias:
    # IMPORTANTE: Asegúrate de que tu campo de URL se llama 'url'
    url = noticia.get('url') 
    
    if url and url not in urls_publicadas:
        nuevas_noticias.append(noticia)

# Invertimos la lista para publicar de más antigua a más nueva
nuevas_noticias.reverse()
print(f"Se encontraron {len(nuevas_noticias)} noticias nuevas.")

# --- 5. Publicar en Discord y guardar historial ---
if not nuevas_noticias:
    print("No hay nada nuevo que publicar.")
else:
    for noticia in nuevas_noticias:
        # IMPORTANTE: Asegúrate de que tus campos se llaman 'titulo' y 'url'
        titulo = noticia.get('titulo', 'Sin Título')
        url_noticia = noticia.get('url')

        mensaje = {
            "embeds": [{
                "title": titulo,
                "url": url_noticia,
                "color": 15258703 # Color Naranja UPS
            }]
        }
        requests.post(WEBHOOK_URL, json=mensaje)
        urls_publicadas.add(url_noticia) # Añadir al set para el siguiente paso

    # --- 6. Actualizar el archivo de historial localmente ---
    with open(ARCHIVO_HISTORIAL, 'w') as f:
        for url in urls_publicadas:
            f.write(f"{url}\n")
            
    print(f"Publicadas {len(nuevas_noticias)} noticias y actualizado el historial.")
