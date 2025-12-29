# Estado del Proyecto: Scraping Microservice + n8n + Retell AI

Fecha: 29 de diciembre de 2025

## ✅ Lo que hemos logrado (Avances)

1. **Microservicio de Scraping (Motor)**:
   - Desarrollado en **Python 3.10+** con **FastAPI** y **Playwright Asíncrono**.
   - **Seguridad**: Implementada validación por `x-api-key`.
   - **Stealth Mode**: Integrado sistema para evitar detección de bots (invisibilidad).
   - **Debug Pro**: Sistema de captura de pantalla automática en base64 cuando falla un selector, devuelto en el JSON de error.
   - **Integración CRM Real**: Soporte añadido para **SuiteCRM 8** con selectores específicos para contactos (`tr.cdk-row`).

2. **Infraestructura (Cloud)**:
   - Repositorio GitHub conectado: `https://github.com/francojbe/phyton-n8n.git`
   - Despliegue exitoso en **Easypanel** (Docker).
   - Configuración de puerto (8000) y dominio operativa.

3. **Orquestación (n8n)**:
   - Conexión exitosa entre n8n y el microservicio.
   - Configuración del nodo **HTTP Request** funcional.
   - **Pruebas Locales**: Verificación exitosa de extracción de 20 contactos reales desde el demo de SuiteCRM.

---

## 🛠️ Lo que falta (Pendiente)

1. **Integración con Retell AI**:
   - Crear cuenta en Retell AI (aprovechar los $10 USD de prueba).
   - Diseñar el **System Prompt** (guion) del agente de voz de "Recuperadora".
   - Configurar el nodo HTTP en n8n para disparar las llamadas automáticas.

2. **Refinamiento de Datos**:
   - Limpieza automática de números de teléfono (quitar paréntesis y espacios) antes de enviar a Retell.

3. **Pruebas Finales (End-to-End)**:
   - Validación de todo el flujo: Scraper -> n8n -> Retell AI -> Actualización de estado.

---

## 🔑 Credenciales para Pruebas (Actuales)
- **Endpoint Local**: `http://127.0.0.1:8000/scrape`
- **Endpoint Cloud**: `https://recuperadora-phyton-scraping.nojauc.easypanel.host/scrape`
- **API Key**: `scraping_secret_key_2025`
- **SuiteCRM Demo**: `https://suite8demo.suiteondemand.com/#/Login` (User: `will` / Pass: `will`)

---
*Archivo actualizado para reflejar la integración con SuiteCRM 8.*
