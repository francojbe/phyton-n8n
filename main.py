import asyncio
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, HttpUrl
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

app = FastAPI(title="Scraping Microservice API-First")

class ScrapeRequest(BaseModel):
    username: str
    password: str
    target_url: HttpUrl

@app.post("/scrape")
async def scrape_data(request: ScrapeRequest):
    """
    Endpoint de scraping que realiza login en la URL objetivo.
    Ejemplo configurado para https://the-internet.herokuapp.com/login
    """
    
    async with async_playwright() as p:
        # Lanzamiento del navegador con flags anti-detección básica
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--single-process",
                "--disable-gpu"
            ]
        )
        
        # Crear contexto con User-Agent moderno para evitar bloqueos simples
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        try:
            # Ir a la URL solicitada
            await page.goto(str(request.target_url), wait_until="networkidle", timeout=30000)
            
            # Lógica de Login específica para el ejemplo dummy
            # Nota: En un entorno real, esto podría variar según 'target_url'
            if "the-internet.herokuapp.com/login" in str(request.target_url):
                try:
                    await page.fill("#username", request.username)
                    await page.fill("#password", request.password)
                    await page.click("button[type='submit']")
                    
                    # Esperar a que el mensaje de éxito aparezca
                    success_selector = ".flash.success"
                    await page.wait_for_selector(success_selector, timeout=10000)
                    
                    success_message = await page.inner_text(success_selector)
                    
                    return {
                        "status": "success",
                        "message": success_message.strip(),
                        "url": page.url
                    }
                except PlaywrightTimeoutError:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Login failed: Invalid credentials or success message not found."
                    )
            
            # Si no es la URL de prueba, devolvemos el título de la página como fallback
            content = await page.title()
            return {
                "status": "completed",
                "page_title": content,
                "url": page.url
            }

        except PlaywrightTimeoutError:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Request timed out while loading the page."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred: {str(e)}"
            )
        finally:
            await browser.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
