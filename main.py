import asyncio
import base64
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, status, Header, Depends
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_async
from dotenv import load_dotenv

# Cargar variables de entorno (para la API Key)
load_dotenv()

app = FastAPI(title="Scraping Microservice PRO")

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
    wait_time: Optional[int] = 5  # Tiempo de espera adicional tras login

@app.post("/scrape", dependencies=[Depends(verify_api_key)])
async def scrape_data(request: ScrapeRequest):
    """
    Endpoint PRO con:
    - Seguridad por API Key.
    - Modo Stealth (anti-bot).
    - Captura de pantalla automática en caso de error.
    """
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )
        
        # User-Agent persistente y de calidad
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        page = await context.new_page()
        
        # Aplicar modo Stealth para evadir detecciones avanzadas
        await stealth_async(page)
        
        try:
            # Ir a la URL solicitada
            await page.goto(str(request.target_url), wait_until="networkidle", timeout=30000)
            
            # Lógica de Login específica para el ejemplo dummy
            if "the-internet.herokuapp.com/login" in str(request.target_url):
                try:
                    await page.fill("#username", request.username)
                    await page.fill("#password", request.password)
                    await page.click("button[type='submit']")
                    
                    # Esperar a que el mensaje de éxito aparezca
                    success_selector = ".flash.success"
                    await page.wait_for_selector(success_selector, timeout=10000)
                    
                    success_message = await page.inner_text(success_selector)
                    
                    # Pequeña pausa opcional para asegurar carga de datos tras login
                    if request.wait_time:
                        await asyncio.sleep(request.wait_time)
                    
                    return {
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "message": success_message.strip(),
                        "url": page.url
                    }
                except PlaywrightTimeoutError:
                    # Captura de pantalla si el login falla (para debugging)
                    screenshot_bytes = await page.screenshot(full_page=True)
                    screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            "error": "Login failed or element not found",
                            "screenshot": screenshot_b64
                        }
                    )
            
            # Comportamiento general para otras URLs (extraer título y meta descripción)
            content = await page.title()
            return {
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "page_title": content,
                "url": page.url
            }

        except PlaywrightTimeoutError:
            # Captura de pantalla en timeout
            screenshot_bytes = await page.screenshot(full_page=True)
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail={
                    "error": "Request timed out",
                    "screenshot": screenshot_b64
                }
            )
        except Exception as e:
            # Error genérico con captura si es posible
            try:
                screenshot_bytes = await page.screenshot(full_page=True)
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            except:
                screenshot_b64 = None

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": str(e),
                    "screenshot": screenshot_b64
                }
            )
        finally:
            await browser.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
