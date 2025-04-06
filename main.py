import pandas as pd
from selenium import webdriver
import time
from lxml import html
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps

def imageCreation(URL, ProductName, precioProducto):
    # --- CONFIGURACIÓN ---
    URL_IMAGEN = URL  # Reemplaza con tu URL real
    TEXTO_INFERIOR = ProductName
    TEXTO_INFERIOR2 = precioProducto
    ANCHO_FINAL = 540
    ALTO_FINAL = 540
    PADDING_SUPERIOR = 15
    ESPACIO_TEXTO = 15
    ESPACIO_TEXTO2 = 30
    BORDE_COLOR = "lightgray"
    BORDE_GROSOR = 4
    RADIO_ESQUINAS = 10

    # --- DESCARGAR Y CARGAR IMAGEN DESDE URL ---
    response = requests.get(URL_IMAGEN)
    original = Image.open(BytesIO(response.content)).convert("RGBA")

    # --- REDIMENSIONAR IMAGEN ---
    max_ancho = ANCHO_FINAL - 100
    max_alto = ALTO_FINAL // 2
    original.thumbnail((max_ancho, max_alto), Image.ANTIALIAS)

    # --- AGREGAR BORDE A LA IMAGEN ---
    with_borde = ImageOps.expand(original, border=BORDE_GROSOR, fill=BORDE_COLOR)

    # --- CONFIGURAR FUENTE ---
    try:
        fuente = ImageFont.truetype("Aptos.ttf", 30)
    except:
        fuente = ImageFont.load_default()

    # --- MEDIR TEXTO ---
    temp_img = Image.new("RGBA", (1, 1))
    draw_temp = ImageDraw.Draw(temp_img)
    bbox = draw_temp.textbbox((0, 0), TEXTO_INFERIOR, font=fuente)
    ancho_texto = bbox[2] - bbox[0]
    alto_texto = bbox[3] - bbox[1]

    # --- CREAR LIENZO DE 1080x1080 ---
    canvas = Image.new("RGBA", (ANCHO_FINAL, ALTO_FINAL), "white")

    # --- PEGAR IMAGEN ---
    x = (ANCHO_FINAL - with_borde.width) // 2
    y = PADDING_SUPERIOR
    canvas.paste(with_borde, (x, y))

    # --- DIBUJAR TEXTO DEBAJO DE LA IMAGEN ---
    draw = ImageDraw.Draw(canvas)

    # Coordenadas del primer texto (nombre del producto)
    x_texto = (ANCHO_FINAL - ancho_texto) // 2
    y_texto = y + with_borde.height + ESPACIO_TEXTO
    draw.text((x_texto, y_texto), TEXTO_INFERIOR, fill="black", font=fuente)

    # Medir segundo texto (precio)
    bbox2 = draw.textbbox((0, 0), TEXTO_INFERIOR2, font=fuente)
    ancho_texto2 = bbox2[2] - bbox2[0]
    alto_texto2 = bbox2[3] - bbox2[1]

    # Coordenadas del segundo texto (precio)
    x_texto2 = (ANCHO_FINAL - ancho_texto2) // 2
    y_texto2 = y_texto + alto_texto + 10  # padding de 10px entre textos

    # Validar espacio disponible
    if y_texto2 + alto_texto2 < ALTO_FINAL:
        draw.text((x_texto2, y_texto2), TEXTO_INFERIOR2, fill="black", font=fuente)

    # --- REDONDEAR ESQUINAS DE LA IMAGEN FINAL ---
    def redondear_esquinas(imagen, radio):
        mask = Image.new("L", imagen.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle([(0, 0), imagen.size], radius=radio, fill=255)
        imagen.putalpha(mask)
        return imagen

    canvas = redondear_esquinas(canvas, RADIO_ESQUINAS)

    # --- GUARDAR Y MOSTRAR ---
    canvas.convert("RGB").save("imagen_final.jpg", quality=95)
    canvas.show()


options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

link = "https://www.amazon.com.mx/gp/product/B0CDQDDLDS?ref=ppx_pt2_dt_b_prod_image&th=1&psc=1"

driver.get(link)

time.sleep(1)

#Bot Detection Exception
try:
    productPhotoComponent = driver.find_element(By.XPATH, "//div[@id = 'imgTagWrapperId']//img")
except:
    driver.find_element(By.XPATH, "//input[@id = 'captchacharacters']")

    print("Bot Detection System")
    
    tryanohterImage = driver.find_element(By.XPATH, "//div[@class = 'a-column a-span6 a-span-last a-text-right']//a")
    tryanohterImage.click()
    
    time.sleep(2)

    productPhotoComponentAux = driver.find_element(By.XPATH, "//div[@id = 'imgTagWrapperId']//img")
    productTitle = driver.find_element(By.XPATH, "//span[@id = 'productTitle']")
    precioProductoMain = driver.find_element(By.XPATH, "//div[@id = 'corePrice_feature_div']//div//div//span[@class = 'a-price aok-align-center']//span[@aria-hidden = 'true']//span[@class = 'a-price-whole']")
    precioProductoCents = driver.find_element(By.XPATH, "//div[@id = 'corePrice_feature_div']//div//div//span[@class = 'a-price aok-align-center']//span[@aria-hidden = 'true']//span[@class = 'a-price-fraction']")
    precioFinal = precioProductoMain.text + "." + precioProductoCents.text


photoURL = productPhotoComponentAux.get_attribute("src")
productName = productTitle.text
precioProducto = "$ " + str(precioFinal)

# print(productName)
# print(precioProducto)

imageCreation(photoURL, str(productName), precioProducto)

driver.quit()
