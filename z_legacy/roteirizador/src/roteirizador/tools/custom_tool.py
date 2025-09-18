from geopy.geocoders import Nominatim
from crewai_tools import BaseTool

class Geocoder:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="crew_distance_calc")
        self.cache = {}

    def resolve(self, cep: str) -> tuple:
        if cep in self.cache:
            return self.cache[cep]
        loc = self.geolocator.geocode(cep)
        if loc:
            coord = (loc.latitude, loc.longitude)
            self.cache[cep] = coord
            return coord
        return None

class GeocodeTool(BaseTool):
    name = "geocode_tool"
    description = "Converte um CEP em coordenadas geográficas (latitude, longitude)."

    def __init__(self):
        super().__init__()
        self.geocoder = Geocoder()

    def _run(self, cep: str) -> str:
        coord = self.geocoder.resolve(cep)
        if coord:
            return f"{coord[0]}, {coord[1]}"
        return "Não foi possível localizar o CEP"
