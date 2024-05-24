from selenium import webdriver
from seleniumwire import webdriver as wire_webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from values import OperationType, Office, Province, Country, DocumentType

# import winsound
from selenium.webdriver.common.alert import Alert
import captcha
import base64
from PIL import Image
from io import BytesIO
import time as ts
import zipfile


# PROXY_HOST = 'geo.iproyal.com'
# PROXY_PASS = '3ZJOBdtMrxEuATla_country-es_session-f9bXq6Bh_lifetime-5m'
# PROXY_USER = 'o0CD9ajN0nnmAjPa'
# PROXY_PORT = '12321'
# PROXY = PROXY_HOST+':'+PROXY_PASS+'@'+PROXY_USER+':'+PROXY_PORT

# # Proxy authentication string
# PROXY_AUTH = f'{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}'

# # Selenium Wire proxy options
# proxy_options = {
#     'proxy': {
#         'https': f'http://{PROXY_AUTH}',
#         'http': f'http://{PROXY_AUTH}',
#     }
# }

# s = Service(ChromeDriverManager().install())
# options = webdriver.ChromeOptions()
# options.add_argument("--log-level=3")

# driver = wire_webdriver.Chrome(service=s, options=options, seleniumwire_options=proxy_options)


PROXY_HOST = "geo.iproyal.com"
PROXY_PORT = "12321"
PROXY_USER = "o0CD9ajN0nnmAjPa"
PROXY_PASS = "3ZJOBdtMrxEuATla_country-es_session-f9bXq6Bh_lifetime-1m"

manifest_json = """
{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {
        "scripts": ["background.js"]
    },
    "minimum_chrome_version":"22.0.0"
}
"""

background_js = f"""
var config = {{
        mode: "fixed_servers",
        rules: {{
          singleProxy: {{
            scheme: "http",
            host: "{PROXY_HOST}",
            port: parseInt({PROXY_PORT})
          }},
          bypassList: ["localhost"]
        }}
      }};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

function callbackFn(details) {{
    return {{
        authCredentials: {{
            username: "{PROXY_USER}",
            password: "{PROXY_PASS}"
        }}
    }};
}}

chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {{urls: ["<all_urls>"]}},
            ['blocking']
);
"""

pluginfile = "proxy_auth_plugin.zip"

with zipfile.ZipFile(pluginfile, "w") as zp:
    zp.writestr("manifest.json", manifest_json)
    zp.writestr("background.js", background_js)

# Set up Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--log-level=3")
chrome_options.add_extension(pluginfile)

# Initialize the Chrome driver with options
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=chrome_options)

# Province
province = Province.MADRID
# Office
office = Office.NULL  # Office.NULL when the select is empty

# Datos a modificar para cada cliente

# Operation Type
operation_type = (
    OperationType.MADRID_ASILO_PRIMERA_CITA
)  # OperationType.NULL when the select is empty
# Document Type
document_type = DocumentType.PASSPORT
# Personal data
document_number = "260241296"
name = "CARMEN GABRIELA BARRIENTOS VASQUEZ"
birth_year = "1994"
nationality = Country.GUATEMALA
expiration_date = "23/07/2022"

phone = "687727870"
email = "almodovarrodriguez@hotmail.com"


def main():
    not_secure()

    send_request()

    while not check_is_available_appointment():
        send_request()

    if office.value == "":
        select_first_office()

    fill_phone_and_email()

    while not check_is_available_appointment():
        main()

    print("\n--------------------Cita Disponible--------------------")

    # winsound.PlaySound("./sounds/alarm.wav", winsound.SND_FILENAME)

    select_free_appointment_and_resolve_captcha()


def not_secure():
    driver.get(get_url())

    try:
        WebDriverWait(driver, 2).until(
            ec.element_to_be_clickable((By.ID, "details-button"))
        ).click()
        driver.find_element(By.ID, "proceed-link").click()
    except (NoSuchElementException, TimeoutException):
        pass


def send_request():
    driver.get(get_url())

    select_office_and_operation()

    # Click button "Entrar"
    driver.execute_script("document.forms[0].submit()")

    WebDriverWait(driver, 2).until(ec.presence_of_element_located((By.ID, "btnEnviar")))

    fill_personal_data()

    # Click button "Aceptar"
    driver.execute_script("enviar('solicitud')")


def check_is_available_appointment():
    available_first = False
    available_second = False

    try:
        WebDriverWait(driver, 2).until(
            ec.presence_of_element_located(
                (By.XPATH, "//p[text()='En este momento no hay citas disponibles.']")
            )
        )
    except TimeoutException:
        available_first = True
    try:
        WebDriverWait(driver, 2).until(
            ec.presence_of_element_located(
                (By.XPATH, "//span[text()='En este momento no hay citas disponibles.']")
            )
        )
    except TimeoutException:
        available_second = True

    if available_first and available_second:
        return True

    ts.sleep(180)
    return False


def get_url():
    return "https://icp.administracionelectronica.gob.es" + province.value


def select_office_and_operation():
    if office.value != "":
        WebDriverWait(driver, 2).until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//select[@id='sede']//option[@value='" + office.value + "']",
                )
            )
        )
        dropdown_offices = Select(driver.find_element(By.ID, "sede"))
        dropdown_offices.select_by_value(office.value)

    try:
        WebDriverWait(driver, 2).until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//select[@id='tramiteGrupo[0]']//option[@value='"
                    + operation_type.value
                    + "']",
                )
            )
        )

        dropdown_operation = Select(driver.find_element(By.ID, "tramiteGrupo[0]"))
        dropdown_operation.select_by_value(operation_type.value)
    except (NoSuchElementException, TimeoutException):
        pass

    try:
        WebDriverWait(driver, 2).until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//select[@id='tramiteGrupo[1]']//option[@value='"
                    + operation_type.value
                    + "']",
                )
            )
        )

        dropdown_operation = Select(driver.find_element(By.ID, "tramiteGrupo[1]"))
        dropdown_operation.select_by_value(operation_type.value)
    except (NoSuchElementException, TimeoutException):
        pass

    driver.execute_script("envia()")


def fill_personal_data():
    error = True

    while error:
        try:
            WebDriverWait(driver, 2).until(
                ec.element_to_be_clickable((By.ID, document_type.value))
            ).click()
            error = False
        except ElementClickInterceptedException:
            error = True

    fill_input("txtIdCitado", document_number)
    fill_input("txtDesCitado", name)
    fill_input("txtAnnoCitado", birth_year)
    fill_input("txtFecha", expiration_date)

    try:
        WebDriverWait(driver, 2).until(
            ec.element_to_be_clickable(
                (
                    By.XPATH,
                    "//select[@id='txtPaisNac']//option[@value='"
                    + nationality.value
                    + "']",
                )
            )
        )

        dropdown_nationality = Select(driver.find_element(By.ID, "txtPaisNac"))
        dropdown_nationality.select_by_value(nationality.value)
    except TimeoutException:
        pass

    driver.execute_script("envia()")


def select_first_office():
    WebDriverWait(driver, 2).until(ec.presence_of_element_located((By.ID, "idSede")))

    dropdown_office = Select(driver.find_element(By.ID, "idSede"))

    try:
        dropdown_office.select_by_index(2)
    except NoSuchElementException:
        try:
            dropdown_office.select_by_index(1)
        except NoSuchElementException:
            pass

    driver.execute_script("enviar()")


def fill_phone_and_email():
    fill_input("txtTelefonoCitado", phone)
    fill_input("emailUNO", email)
    fill_input("emailDOS", email)

    driver.execute_script("enviar()")


def select_free_appointment_and_resolve_captcha():
    download_captcha()

    print("\nResolviendo captcha...")

    captcha_result = None

    try:
        captcha_result = captcha.captcha_resolver()
    except Exception as e:
        print(e)

    print("\nCaptcha: " + captcha_result.get("code"))

    fill_input("captcha", captcha_result.get("code"))

    error = True

    while error:
        try:
            WebDriverWait(driver, 2).until(
                ec.presence_of_element_located((By.XPATH, "//span[text()='LIBRE']"))
            ).click()
            error = False
        except ElementClickInterceptedException:
            error = True

    Alert(driver).accept()


def download_captcha():
    try:
        WebDriverWait(driver, 2).until(
            ec.presence_of_element_located((By.XPATH, "//img[@alt='captcha']"))
        )
    except TimeoutException:
        pass
    else:
        img = driver.find_element(By.XPATH, "//img[@alt='captcha']")

        image_data = img.get_property("src").split(",")[1]

        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image.save("./captcha/captcha.png", "PNG")


def fill_input(id, data):
    try:
        input_data = driver.find_element(By.ID, id)
        input_data.clear()
        input_data.send_keys(data)
    except NoSuchElementException:
        pass


def exit_script():
    driver.quit()
    exit()


main()
