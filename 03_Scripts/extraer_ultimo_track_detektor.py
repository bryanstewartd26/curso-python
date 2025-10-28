# extraer_ultimo_track_detektor.py
import re
import time
import random
from datetime import datetime
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

# ---------- CONFIG ----------
INPUT_EXCEL = r"C:\Users\Monitoreo2\Desktop\Python_Lab\03_Scripts\vehiculos.xlsx"     # columns: PLACA, USUARIO, CONTRASEÑA (may add LOGIN_URL)
OUTPUT_EXCEL = "reporte_detektor_tracks.xlsx"
LOGIN_PAGE = "https://co.tracking.detektorgps.com/AppEboras/login_co/login_co.html"
TIMEOUT = 12
PAUSA_MIN = 1.0
PAUSA_MAX = 2.5

# ---------- HELPERS ----------
def wait_random():
    time.sleep(random.uniform(PAUSA_MIN, PAUSA_MAX))

def find_first(driver, candidates, timeout=TIMEOUT):
    """Intenta varios selectores y devuelve el elemento encontrado o None."""
    for by, selector in candidates:
        try:
            return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, selector)))
        except Exception:
            continue
    return None

def find_presence(driver, candidates, timeout=TIMEOUT):
    for by, selector in candidates:
        try:
            return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))
        except Exception:
            continue
    return None

def extract_datetime_from_text(text):
    """Busca posibles fechas en el texto y devuelve datetime si encuentra."""
    # patrones comunes: 2025-10-25 18:30:45 o 25/10/2025 18:30 etc.
    patterns = [
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", "%Y-%m-%d %H:%M:%S"),
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})", "%Y-%m-%d %H:%M"),
        (r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})", "%d/%m/%Y %H:%M:%S"),
        (r"(\d{2}/\d{2}/\d{4} \d{2}:\d{2})", "%d/%m/%Y %H:%M"),
        (r"([A-Za-z]{3,10} \d{1,2}, \d{4} \d{1,2}:\d{2})", "%b %d, %Y %H:%M"),
    ]
    for pat, fmt in patterns:
        m = re.search(pat, text)
        if m:
            s = m.group(1)
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                continue
    return None

# ---------- SELECTORES (intentos múltiples para mayor robustez) ----------
USER_SELECTORS = [
    (By.ID, "username"), (By.ID, "Usuario"), (By.NAME, "username"),
    (By.XPATH, "//input[@placeholder='Usuario']"), (By.XPATH, "//input[contains(@placeholder,'Usu')]"),
    (By.CSS_SELECTOR, "input[type='text']"),
]

PASS_SELECTORS = [
    (By.ID, "password"), (By.ID, "clave"), (By.NAME, "password"),
    (By.XPATH, "//input[@placeholder='Clave']"), (By.CSS_SELECTOR, "input[type='password']"),
]

# Botón Acceder (en la pantalla principal) — en tu screenshot aparece un span con id concreto
SKYTRACK_ACCEDER_SELECTORS = [
    (By.ID, "idBtnProductSkytrack-btnInnerEl"),
    (By.XPATH, "//div[contains(.,'Skytrack')]//button[contains(.,'Acceder')]"),
    (By.XPATH, "//button[contains(.,'Acceder') and .//preceding::div[contains(.,'Skytrack')]]"),
    (By.XPATH, "//span[text()='Acceder']/ancestor::button[1]"),
]

# Menú (mostrar-menu)
MENU_SELECTOR = [(By.ID, "mostrar-menu"), (By.CSS_SELECTOR, "td#mostrar-menu")]

# En la ventana de opciones del mapa: input de "Alias / Placa" (intentos variados)
ALIAS_PLACA_SELECTORS = [
    (By.XPATH, "//label[contains(.,'Alias')]/following::input[1]"),
    (By.XPATH, "//input[contains(@placeholder,'Placa')]"),
    (By.XPATH, "//input[contains(@name,'placa') or contains(@id,'placa')]"),
    (By.CSS_SELECTOR, "input[type='text']"),
]

# Botón "Ult. Estado Unidad." o "Último Punto"
ULTIMO_PUNTO_SELECTORS = [
    (By.XPATH, "//button[contains(.,'Ult') and (contains(.,'Estado') or contains(.,'Punto'))]"),
    (By.XPATH, "//a[contains(.,'Ult') and (contains(.,'Estado') or contains(.,'Punto'))]"),
    (By.XPATH, "//input[@value='Ult. Estado Unidad.']"),
]

# Si hay un input tipo fecha/hora mostrado, buscámoslo con XPaths comunes
DATETIME_FIELD_SELECTORS = [
    (By.XPATH, "//input[contains(@class,'date') or contains(@class,'time') or contains(@class,'datetime')]"),
    (By.XPATH, "//span[contains(@class,'time') or contains(@class,'date')]"),
]

# ---------- MAIN ----------
def main():
    df = pd.read_excel(INPUT_EXCEL, dtype=str).fillna("")
    resultados = []

    # driver
    opts = Options()
    # opts.add_argument("--headless=new")  # descomenta para ejecución sin UI
    opts.add_experimental_option("detach", True)  # deja la ventana abierta al terminar (útil para debug)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

    for i, row in df.iterrows():
        placa = (row.get("PLACA") or row.get("placa") or "").strip()
        usuario = (row.get("USUARIO") or row.get("usuario") or "").strip()
        contrasena = (row.get("CONTRASEÑA") or row.get("contraseña") or row.get("password") or "").strip()
        login_url = row.get("LOGIN_URL") or LOGIN_PAGE

        resultado = {"placa": placa, "usuario": usuario, "fecha_detector": None, "error": None}

        try:
            # 1) Login
            driver.get(login_url)
            wait_random()

            user_elem = find_first(driver, USER_SELECTORS, timeout=8)
            pass_elem = find_first(driver, PASS_SELECTORS, timeout=8)

            if user_elem is None or pass_elem is None:
                resultado["error"] = "No se localizaron inputs de login (ajusta selectores)."
                resultados.append(resultado)
                continue

            user_elem.clear()
            user_elem.send_keys(usuario)
            pass_elem.clear()
            pass_elem.send_keys(contrasena)
            wait_random()

            # intentar submit: Enter o botón "Entrar"
            try:
                pass_elem.submit()
            except Exception:
                # botón rojo "Entrar"
                try:
                    btn = driver.find_element(By.XPATH, "//button[contains(.,'Entrar') or contains(.,'Acceder')]")
                    btn.click()
                except Exception:
                    pass

            # esperar que cargue la página principal
            WebDriverWait(driver, TIMEOUT).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            wait_random()

            # 3) Click en Skytrack -> Acceder
            skbtn = find_first(driver, SKYTRACK_ACCEDER_SELECTORS, timeout=8)
            if skbtn:
                try:
                    skbtn.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", skbtn)
                wait_random()
            else:
                # si no encontramos, intentamos navegar a la URL de skytrack si se conoce (no incluida aquí)
                pass


                    # Espera un momento a que se abra la nueva pestaña
            time.sleep(2)

            # Obtener todas las pestañas abiertas
            tabs = driver.window_handles
            print(f"🔍 Pestañas detectadas: {len(tabs)}")

            # Cambiar al último tab (la del menú)
            driver.switch_to.window(tabs[-1])
            print(f"✅ Cambiado al nuevo tab: {driver.current_url}")

            # Esperar carga completa del DOM del nuevo tab
            time.sleep(2)

            # Intentar abrir el menú
            driver.execute_script("document.getElementById('mostrar-menu').click()")
            print("✅ Menú desplegado exitosamente")



            # === Intentar buscar el campo de búsqueda de placa dentro del menu dinámico ===
            try:
                # preferimos el input con id 'busca_placa' que viste en el DOM
                busca_input = None
                try:
                    busca_input = WebDriverWait(driver, 6).until(EC.presence_of_element_located((By.ID, "busca_placa")))
                except Exception:
                    # fallback: buscar por clase o placeholder dentro del .menuDiv
                    try:
                        busca_input = driver.find_element(By.XPATH, "//input[@placeholder='Placa...' or contains(@id,'busca') or contains(@name,'busca')]")
                    except Exception:
                        busca_input = None

                if busca_input:
                    # escribir la placa ahí (es el buscador rápido del menú)
                    try:
                        busca_input.clear()
                        busca_input.send_keys(placa)
                        wait_random()
                        # presionar el boton > al lado (id="boton_buscar" según HTML)
                        # hay dos botones con id boton_buscar en tu HTML; intentamos localizar el correcto cercano al input
                        try:
                            # buscar el botón dentro del mismo formulario padre
                            boton = busca_input.find_element(By.XPATH, "./following::input[@type='button' and (contains(@class,'searchbutton') or @id='boton_buscar')][1]")
                        except Exception:
                            # fallback: buscar por id global
                            try:
                                boton = driver.find_element(By.ID, "boton_buscar")
                            except Exception:
                                boton = None

                        if boton:
                            # usar JS click (más robusto)
                            driver.execute_script("arguments[0].click();", boton)
                            print("[OK] Búsqueda por placa disparada desde menu (botón).")
                            wait_random()
                        else:
                            print("[WARN] No se encontró botón buscar cercano al input 'busca_placa'.")
                    except Exception as e:
                        print(f"[WARN] Error escribiendo en busca_placa o clic botón: {e}")
                else:
                    print("[INFO] No se detectó input 'busca_placa' en el menú; intentando alias_input normal.")
            except Exception as e:
                print(f"[WARN] Error intentando usar buscador rápido del menú: {e}")

            # 4) Esperar el panel de opciones mapa y encontrar el campo Alias / Placa (tu flujo actual)
            alias_input = find_first(driver, ALIAS_PLACA_SELECTORS, timeout=8)
            if alias_input:
                try:
                    # si el buscador rápido ya puso la placa y abrió result, quizás no sea necesario escribir aquí
                    # aun así intentamos escribir la placa para el flujo clásico
                    alias_input.clear()
                    alias_input.send_keys(placa)
                    wait_random()
                except Exception:
                    pass
            else:
                # fallback: tratar de encontrar cualquier input y escribir la placa
                try:
                    any_input = driver.find_element(By.XPATH, "//input")
                    any_input.clear()
                    any_input.send_keys(placa)
                    wait_random()
                except Exception:
                    pass

            # 5) Pulsar "Ult. Estado Unidad." o "Último Punto"
            ult_btn = find_first(driver, ULTIMO_PUNTO_SELECTORS, timeout=6)
            if ult_btn:
                try:
                    ult_btn.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", ult_btn)
                wait_random()
            else:
                # si no hay botón, es posible que haya un botón "Ultimo Punto" visible por texto
                try:
                    btn2 = driver.find_element(By.XPATH, "//button[contains(.,'Ultimo') or contains(.,'Último')]")
                    btn2.click()
                    wait_random()
                except Exception:
                    pass

            # 6) Intentar extraer la fecha/hora en varios lugares
            dt_found = None

            # 6a: buscar campos con clase/inputs conocidos
            for sel in DATETIME_FIELD_SELECTORS:
                try:
                    el = find_presence(driver, [sel], timeout=3)
                    if el:
                        txt = el.get_attribute("value") or el.text or ""
                        dt_found = extract_datetime_from_text(txt)
                        if dt_found:
                            break
                except Exception:
                    continue

            # 6b: si no, buscar en el body completo (snippet)
            if not dt_found:
                body = driver.find_element(By.TAG_NAME, "body").text
                dt_found = extract_datetime_from_text(body)

            # 6c: fallback guardar snippet si no parsea
            if isinstance(dt_found, datetime):
                resultado["fecha_detector"] = dt_found
            else:
                # intento de captura de texto cercano a la placa
                try:
                    # buscar por la placa en texto y extraer ventana alrededor
                    body = driver.find_element(By.TAG_NAME, "body").text
                    pos = body.find(placa)
                    snippet = body[max(0, pos-300): pos+300] if pos != -1 else body[:600]
                    dt_try = extract_datetime_from_text(snippet)
                    if dt_try:
                        resultado["fecha_detector"] = dt_try
                    else:
                        resultado["error"] = "No se pudo parsear fecha. Snippet: " + snippet[:400]
                except Exception as e:
                    resultado["error"] = f"Error buscando texto en body: {e}"

        except Exception as e:
            resultado["error"] = f"Excepción general: {str(e)[:400]}"

        resultados.append(resultado)
        # pausa antes de la siguiente cuenta
        wait_random()

    # finalizar
    try:
        driver.quit()
    except Exception:
        pass

    # guardar resultados
    out_df = pd.DataFrame(resultados)
    out_df.to_excel(OUTPUT_EXCEL, index=False)
    print("✅ Proceso terminado. Revisa:", OUTPUT_EXCEL)


if __name__ == "__main__":
    main()
