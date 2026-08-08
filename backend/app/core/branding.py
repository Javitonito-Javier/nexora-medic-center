"""
Configuración Centralizada de Marca - Nexora Labs
Permite personalizar la instancia para diferentes clientes (Multi-tenant branding).
"""
from pydantic_settings import BaseSettings

class BrandingConfig(BaseSettings):
    # Identidad Principal
    APP_NAME: str = "Nexora Labs Medic Center"
    APP_SHORT_NAME: str = "Nexora Medic"
    TAGLINE: str = "Gestión Clínica Inteligente"
    
    # Personalización Visual (Se puede sobreescribir por cliente)
    PRIMARY_COLOR: str = "#0F4C81"  # Azul Clásico Nexora
    SECONDARY_COLOR: str = "#20B2AA" # Light Sea Green
    LOGO_URL: str = "/static/logo_nexora.png"
    
    # Información Legal
    COMPANY_NAME: str = "Nexora Labs S.A."
    SUPPORT_EMAIL: str = "soporte@nexoralabs.com"
    SUPPORT_PHONE: str = "+504 2233-4455"
    
    # Modo Multi-Cliente
    IS_MULTI_TENANT: bool = True
    
    class Config:
        env_file = ".env"

branding = BrandingConfig()
