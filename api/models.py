from pydantic import BaseModel, Field
from datetime import datetime

class WeatherData(BaseModel):
    # Strict validation: realistic boundaries for weather metrics
    temperature: float = Field(..., description="Temperature in Celsius")
    
    humidity: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Relative humidity percentage (0-100)"
    )
    
    wind_speed: float = Field(
        ..., 
        ge=0, 
        description="Wind speed in meters per second (must be positive)"
    )
    
    cloud_cover: float = Field(
        ..., 
        ge=0, 
        le=100, 
        description="Cloud cover percentage (0-100)"
    )
    
    # Pydantic will automatically parse standard ISO-8601 strings from n8n
    timestamp: datetime = Field(..., description="Timestamp of the weather reading")