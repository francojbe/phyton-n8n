import asyncio
import base64
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Header, Depends
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

# Importar el módulo completo para evitar confusiones de nombres
import playwright_stealth

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Scraping Microservice PRO v3")

# Configuración de Seguridad
API_KEY_CREDENTIAL = os.getenv("SCRAPING_API_KEY", "scraping_secret_key_2025")

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY_CREDENTIAL:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return x_api_key

class ScrapeRequest(BaseModel):
    username: str
    password: str
    target_url: HttpUrl
    wait_time: Optional[int] = 2

async def apply_stealth_safely(page):
    """
    Aplica el modo stealth detectando la función correcta en el módulo.
    """
    try:
        # Buscar la función asíncrona o síncrona dentro del módulo
        stealth_func = getattr(playwright_stealth, "stealth_async", None) or getattr(playwright_stealth, "stealth", None)
        
        if stealth_func and callable(stealth_func):
            print(f"Aplicando stealth usando: {stealth_func.__name__}")
            if asyncio.iscoroutinefunction(stealth_func):
                await stealth_func(page)
            else:
                stealth_func(page)
            return True
    except Exception as e:
        print(f"Aviso: Falló la aplicación de stealth (no crítico): {e}")
    return False

@app.post("/scrape", dependencies=[Depends(verify_api_key)])
async def scrape_data(request: ScrapeRequest):
    print(f"[{datetime.now()}] Nuevo scrape solicitado para: {request.target_url}")
    
    async with async_playwright() as p:
        browser = None
        try:
            print("Lanzando navegador...")
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            # Aplicar stealth de forma segura
            await apply_stealth_safely(page)

            print(f"Navegando a {request.target_url}...")
            await page.goto(str(request.target_url), wait_until="networkidle", timeout=30000)
            
            # Ejemplo específico de login para pruebas
            if "the-internet.herokuapp.com/login" in str(request.target_url):
                print("Ejecutando lógica de login de prueba...")
                await page.fill("#username", request.username)
                await page.fill("#password", request.password)
                await page.click("button[type='submit']")
                
                success_selector = ".flash.success"
                await page.wait_for_selector(success_selector, timeout=10000)
                success_message = await page.inner_text(success_selector)
                
                if request.wait_time:
                    await asyncio.sleep(request.wait_time)
                
                return {
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                    "message": success_message.strip(),
                    "url": page.url
                }

            # Caso general (extraer título)
            title = await page.title()
            return {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "page_title": title,
                "url": page.url
            }

        except PlaywrightTimeoutError:
            print("Error: Timeout de Playwright")
            screenshot_b64 = None
            if browser:
                try:
                    screenshot = await page.screenshot(full_page=True)
                    screenshot_b64 = base64.b64encode(screenshot).decode()
                except: pass
            
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={"error": "Timeout", "screenshot": screenshot_b64}
            )
        except Exception as e:
            print(f"Error crítico durante el scrape: {str(e)}")
            screenshot_b64 = None
            if browser:
                try:
                    screenshot = await page.screenshot(full_page=True)
                    screenshot_b64 = base64.b64encode(screenshot).decode()
                except: pass
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": str(e), "screenshot": screenshot_b64}
            )
        finally:
            if browser:
                await browser.close()
            print("Sesión terminada.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
