import re
from playwright.sync_api import Page, expect


def test_faceId_login(page: Page) -> None:
    page.goto("https://gestion360.ngrok.io/")
    page.get_by_role("button", name="Face Id").click()


def test_iniciarSesion_login(page: Page) -> None:
    page.goto("https://gestion360.ngrok.io/")
    page.get_by_role("textbox", name="Usuario").click()
    page.get_by_role("textbox", name="Usuario").fill("admin")
    page.get_by_text("ContraseñaShow password text").click()
    page.get_by_role("textbox", name="Contraseña").fill("1234")
    page.get_by_role("button", name="Iniciar Sesión").click()

def test_inicio_turno(page: Page) -> None:
    page.goto("https://gestion360.ngrok.io/")
    page.get_by_role("button", name="Face Id").click()
    page.get_by_test_id("stMainBlockContainer").get_by_test_id("stBaseButton-secondary").click()
    page.get_by_test_id("stMainBlockContainer").get_by_test_id("stBaseButton-secondary").click()
    page.get_by_test_id("stSidebarUserContent").get_by_test_id("stBaseButton-secondary").click()



def test_registro_usuario(page: Page) -> None:
    page.goto("https://gestion360.ngrok.io/")
    page.get_by_role("textbox", name="Usuario").click()
    page.get_by_role("textbox", name="Usuario").fill("admin")
    page.get_by_text("ContraseñaShow password text").click()
    page.get_by_role("textbox", name="Contraseña").fill("1234")
    page.get_by_role("button", name="Iniciar Sesión").click()
    page.get_by_role("textbox", name="Nombre").click()
    page.get_by_role("textbox", name="Nombre").fill("prueba")
    page.locator("div").filter(has_text=re.compile(r"^Cédula$")).first.click()
    page.get_by_test_id("stSelectboxVirtualDropdown").get_by_text("Cédula").click()
    page.get_by_role("textbox", name="Número de Documento").click()
    page.get_by_role("textbox", name="Número de Documento").fill("1098306275")
    page.locator("div").filter(has_text=re.compile(r"^usuario$")).first.click()
    page.get_by_test_id("stSelectboxVirtualDropdown").get_by_text("administrador").click()
    page.get_by_test_id("stMainBlockContainer").get_by_test_id("stBaseButton-secondary").click()

def test_verificar_usuario(page: Page) -> None:
    page.goto("https://gestion360.ngrok.io/")
    page.get_by_role("textbox", name="Usuario").click()
    page.get_by_role("textbox", name="Usuario").fill("admin")
    page.get_by_text("ContraseñaShow password text").click()
    page.get_by_role("textbox", name="Contraseña").fill("1234")
    page.get_by_role("button", name="Iniciar Sesión").click()
    page.locator("label").filter(has_text="Verificar Registro").locator("div").first.click()
    page.get_by_role("button", name="🔍 Verificar Rostro").click()

def test_editar_usuario(page: Page) -> None:
    page.goto("https://gestion360.ngrok.io/")
    page.get_by_role("textbox", name="Usuario").click()
    page.get_by_role("textbox", name="Usuario").fill("admin")
    page.get_by_text("ContraseñaShow password text").click()
    page.get_by_role("textbox", name="Contraseña").fill("1234")
    page.get_by_role("button", name="Iniciar Sesión").click()
    page.locator("label").filter(has_text="Mostrar todos los usuarios").locator("div").nth(1).click()
    page.locator("div").filter(has_text=re.compile(r"^Angie Gomez \(1097406490\)$")).first.click()
    page.get_by_text("prueba (1098306275)").click()
    page.get_by_role("textbox", name="Nombre").click()
    page.get_by_role("textbox", name="Nombre").fill("seb")
    page.get_by_test_id("stBaseButton-secondaryFormSubmit").click()


