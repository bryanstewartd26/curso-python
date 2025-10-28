from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Ruta al driver
service = Service("C:\\drivers\\chromedriver.exe")

# Opciones del navegador (puedes dejarlas vacías por ahora)
options = Options()

# Crear el navegador
driver = webdriver.Chrome(service=service, options=options)

# Probar
driver.get("https://google.com")
