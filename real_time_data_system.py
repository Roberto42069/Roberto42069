"""
🚀 REVOLUTIONARY Real-Time Data System for SAI Roboto
Created by Roberto Villarreal Martinez

This module provides real-time access to time, weather, and other live data sources.
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import os

class RealTimeDataEngine:
    """
    REVOLUTIONARY: Real-time data access for SAI capabilities
    """
    
    def __init__(self):
        self.weather_api_key = os.environ.get("OPENWEATHER_API_KEY")
        self.weather_cache = {}
        self.cache_duration = 600  # 10 minutes cache
        self.data_sources = {
            "time": True,
            "weather": bool(self.weather_api_key),
            "timezone": True,
            "system_info": True
        }
        
        print("🚀 REVOLUTIONARY: Real-Time Data Engine initialized!")
        print(f"📡 Available data sources: {[k for k, v in self.data_sources.items() if v]}")
        
        if not self.weather_api_key:
            print("⚠️ Weather API key not found. Set OPENWEATHER_API_KEY for weather data.")
    
    def get_current_time(self, timezone_name: str = "America/Chicago") -> Dict[str, Any]:
        """Get current time with detailed information"""
        try:
            now = datetime.now(timezone.utc)
            
            # Convert to specified timezone if possible
            try:
                import pytz
                if timezone_name != "UTC":
                    tz = pytz.timezone(timezone_name)
                    now = now.astimezone(tz)
            except:
                pass  # Fallback to UTC
            
            return {
                "success": True,
                "current_time": now.isoformat(),
                "formatted_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "human_readable": now.strftime("%A, %B %d, %Y at %I:%M %p"),
                "timezone": timezone_name,
                "timestamp": now.timestamp(),
                "day_of_week": now.strftime("%A"),
                "day_of_year": now.timetuple().tm_yday,
                "week_of_year": now.strftime("%U"),
                "is_weekend": now.weekday() >= 5,
                "hour_24": now.hour,
                "minute": now.minute,
                "second": now.second
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_time": datetime.now().isoformat()
            }
    
    def get_weather_data(self, city: str = "San Antonio", country_code: str = "US") -> Dict[str, Any]:
        """Get current weather data"""
        if not self.weather_api_key:
            return {
                "success": False,
                "error": "Weather API key not configured",
                "message": "Set OPENWEATHER_API_KEY environment variable for weather data"
            }
        
        # Check cache first
        cache_key = f"{city}_{country_code}"
        if cache_key in self.weather_cache:
            cached_data = self.weather_cache[cache_key]
            if time.time() - cached_data["cached_at"] < self.cache_duration:
                cached_data["from_cache"] = True
                return cached_data
        
        try:
            # OpenWeatherMap API
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": f"{city},{country_code}",
                "appid": self.weather_api_key,
                "units": "metric"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            weather_info = {
                "success": True,
                "city": data["name"],
                "country": data["sys"]["country"],
                "temperature": data["main"]["temp"],
                "temperature_fahrenheit": (data["main"]["temp"] * 9/5) + 32,
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "main_weather": data["weather"][0]["main"],
                "wind_speed": data["wind"]["speed"],
                "wind_direction": data["wind"].get("deg", 0),
                "cloudiness": data["clouds"]["all"],
                "visibility": data.get("visibility", "N/A"),
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
                "last_updated": datetime.now().isoformat(),
                "cached_at": time.time(),
                "from_cache": False
            }
            
            # Cache the result
            self.weather_cache[cache_key] = weather_info
            
            return weather_info
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Network error: {str(e)}",
                "message": "Could not fetch weather data"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Error processing weather data"
            }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        try:
            import platform
            import psutil
            
            return {
                "success": True,
                "platform": platform.platform(),
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free
                },
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "uptime_seconds": time.time() - psutil.boot_time()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "basic_info": {
                    "timestamp": datetime.now().isoformat(),
                    "platform": "Unknown"
                }
            }
    
    def get_comprehensive_context(self, city: str = "San Antonio", timezone_name: str = "America/Chicago") -> Dict[str, Any]:
        """Get comprehensive real-time context for SAI decision making"""
        
        time_data = self.get_current_time(timezone_name)
        weather_data = self.get_weather_data(city)
        system_data = self.get_system_info()
        
        # Create contextual insights
        context = {
            "data_timestamp": datetime.now().isoformat(),
            "time_context": time_data,
            "weather_context": weather_data,
            "system_context": system_data,
            "availability": self.data_sources,
            "contextual_insights": self._generate_contextual_insights(time_data, weather_data)
        }
        
        return context
    
    def _generate_contextual_insights(self, time_data: Dict, weather_data: Dict) -> Dict[str, str]:
        """Generate intelligent contextual insights from real-time data"""
        insights = {}
        
        # Time-based insights
        if time_data.get("success"):
            hour = time_data.get("hour_24", 12)
            is_weekend = time_data.get("is_weekend", False)
            
            if 5 <= hour < 12:
                insights["time_of_day"] = "morning"
                insights["energy_level"] = "high"
            elif 12 <= hour < 17:
                insights["time_of_day"] = "afternoon"
                insights["energy_level"] = "moderate"
            elif 17 <= hour < 21:
                insights["time_of_day"] = "evening"
                insights["energy_level"] = "moderate"
            else:
                insights["time_of_day"] = "night"
                insights["energy_level"] = "low"
            
            insights["week_context"] = "weekend" if is_weekend else "weekday"
        
        # Weather-based insights
        if weather_data.get("success"):
            temp = weather_data.get("temperature", 20)
            description = weather_data.get("description", "").lower()
            
            if temp < 0:
                insights["temperature_feeling"] = "freezing"
            elif temp < 10:
                insights["temperature_feeling"] = "cold"
            elif temp < 20:
                insights["temperature_feeling"] = "cool"
            elif temp < 25:
                insights["temperature_feeling"] = "comfortable"
            elif temp < 30:
                insights["temperature_feeling"] = "warm"
            else:
                insights["temperature_feeling"] = "hot"
            
            if "rain" in description or "drizzle" in description:
                insights["weather_mood"] = "cozy_indoor"
            elif "snow" in description:
                insights["weather_mood"] = "winter_wonderland"
            elif "clear" in description or "sunny" in description:
                insights["weather_mood"] = "bright_energetic"
            elif "cloud" in description:
                insights["weather_mood"] = "contemplative"
            else:
                insights["weather_mood"] = "neutral"
        
        return insights
    
    def get_data_summary(self) -> str:
        """Get a human-readable summary of available real-time data"""
        time_info = self.get_current_time("America/Chicago")
        weather_info = self.get_weather_data("San Antonio", "US")
        
        summary_parts = []
        
        # Time summary
        if time_info.get("success"):
            summary_parts.append(f"Current time: {time_info.get('human_readable', 'Unknown')}")
        
        # Weather summary
        if weather_info.get("success"):
            temp = weather_info.get("temperature")
            desc = weather_info.get("description")
            city = weather_info.get("city")
            summary_parts.append(f"Weather in {city}: {temp}°C, {desc}")
        
        # System summary
        system_info = self.get_system_info()
        if system_info.get("success"):
            cpu = system_info.get("cpu_percent", 0)
            memory = system_info.get("memory_percent", 0)
            summary_parts.append(f"System: CPU {cpu}%, Memory {memory}%")
        
        return " | ".join(summary_parts) if summary_parts else "Real-time data temporarily unavailable"

def get_real_time_data_system():
    """Factory function to get the real-time data system"""
    return RealTimeDataEngine()