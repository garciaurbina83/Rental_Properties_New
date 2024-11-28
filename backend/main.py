from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

app = FastAPI(
    title="Rental Properties API",
    description="API para la gestión de propiedades de renta",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar los orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas base
@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Rental Properties"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
