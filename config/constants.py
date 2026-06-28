APP_TITLE = "EcoPulse Analytics"
APP_SUBTITLE = "Plataforma analítica modular para calidad del aire urbano"

NAVIGATION_PAGES = [
    "Inicio",
    "Monitoreo en Vivo",
    "Ciudad Comparativa",
    "Glosario",
]

PRIMARY_POLLUTANTS = [
    "pm2_5",
    "pm10",
    "no2",
    "o3",
    "so2",
    "co",
    "nh3",
]

DEFAULT_CITIES = [
    "San José, CR",
    "Alajuela, CR",
    "Cartago, CR",
    "Heredia, CR",
    "Guanacaste, CR",
    "Puntarenas, CR",
    "Limón, CR",
]

COMPARISON_DEFAULT_CITIES = [
    "San José, CR",
    "Santiago, CL",
    "Ciudad de México, MX",
    "Bogotá, CO",
    "Buenos Aires, AR",
    "Washington D.C., US"
]

RISK_STATES = {
    "good": {"label": "Bueno", "color": "#2E7D32"},
    "fair": {"label": "Aceptable", "color": "#C0CA33"},
    "moderate": {"label": "Moderado", "color": "#FB8C00"},
    "poor": {"label": "Malo", "color": "#E53935"},
    "very_poor": {"label": "Muy malo", "color": "#8E24AA"},
    "hazardous": {"label": "Peligroso", "color": "#4A148C"},
    "unknown": {"label": "Desconocido", "color": "#757575"},
}
