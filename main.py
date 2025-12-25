import asyncio
import base64
import os
from datetime import datetime
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, status, Header, Depends
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from dotenv import load_dotenv

# Importar el módulo completo para evitar confusiones de nombres
import playwright_stealth

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Scraping Microservice PRO v4 - Data Extraction")

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
    try:
        stealth_func = getattr(playwright_stealth, "stealth_async", None) or getattr(playwright_stealth, "stealth", None)
        if stealth_func and callable(stealth_func):
            if asyncio.iscoroutinefunction(stealth_func):
                await stealth_func(page)
            else:
                stealth_func(page)
            return True
    except Exception as e:
        print(f"Aviso: Falló stealth: {e}")
    return False

@app.post("/scrape", dependencies=[Depends(verify_api_key)])
async def scrape_data(request: ScrapeRequest):
    print(f"[{datetime.now()}] Iniciando Scrape v4: {request.target_url}")
    
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            await apply_stealth_safely(page)

            print(f"Navegando a {request.target_url}...")
            await page.goto(str(request.target_url), wait_until="networkidle", timeout=30000)
            
            scraped_data = []

            # Lógica específica para el CRM de Prueba (The Internet)
            if "the-internet.herokuapp.com/login" in str(request.target_url):
                print("Procesando Login...")
                await page.fill("#username", request.username)
                await page.fill("#password", request.password)
                await page.click("button[type='submit']")
                
                # Verificar éxito
                await page.wait_for_selector(".flash.success", timeout=10000)
                
                # Simular navegación a la "Sección de Clientes" (Challenging DOM tiene una tabla)
                print("Navegando a la tabla de datos (CRM SIM)...")
                await page.goto("https://the-internet.herokuapp.com/challenging_dom", wait_until="networkidle")
                
                # Extraer filas de la tabla
                rows = await page.query_selector_all("table tbody tr")
                for row in rows:
                    cols = await row.query_selector_all("td")
                    if len(cols) >= 6:
                        scraped_data.append({
                            "name": await cols[0].inner_text(),
                            "id": await cols[1].inner_text(),
                            "status": await cols[2].inner_text(),
                            "action": await cols[3].inner_text(),
                            "phone": "569" + "".join(filter(str.isdigit, await cols[1].inner_text()))[:8] # Generar cel realista
                        })
                
                return {
                    "status": "success",
                    "message": "Data extracted successfully from CRM Simulation",
                    "url": page.url,
                    "data": scraped_data
                }

            # Caso fallback
            return {
                "status": "completed",
                "page_title": await page.title(),
                "url": page.url,
                "data": []
            }

        except Exception as e:
            print(f"Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if browser:
                await browser.close()
