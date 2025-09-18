#!/usr/bin/env python3
"""
CEP to Coordinates Geocoder
Takes a CEP (Brazilian postal code) from terminal input and returns coordinates.
"""
import sys
from geopy.geocoders import Nominatim
import time

def get_coordinates(cep):
    """
    Get coordinates for a Brazilian CEP using Nominatim geocoder.
    
    Args:
        cep (str): Brazilian postal code (CEP)
    
    Returns:
        tuple: (latitude, longitude) or (None, None) if not found
    """
    # Initialize geocoder
    geolocator = Nominatim(user_agent='simple_geocoder')
    
    try:
        # Clean CEP format (remove dashes, ensure8 digits)
        cep_clean = str(cep).replace('-', '').strip().zfill(8)
        
        print(f"Looking up coordinates for CEP: {cep_clean}")
        
        # Geocode the CEP
        location = geolocator.geocode(
            {'postalcode': cep_clean, 'country': 'Brazil'}, 
            timeout=10
        )
        
        if location:
            coords = (location.latitude, location.longitude)
            print(f"✅ Found coordinates: {coords}")
            return coords
        else:
            print("❌ No coordinates found for this CEP")
            return (None, None)
            
    except Exception as e:
        print(f"❌ Error geocoding CEP: {e}")
        return (None, None)

def main():
    """
    Function to handle terminal input and output in a loop.
    """
    print("🌍 Simple CEP to Coordinates Geocoder")
    print("=" * 40)
    print("Enter 'quit' or 'exit' to stop the program.")
    print()
    
    while True:
        # Get CEP from user input
        cep = input("Enter CEP (Brazilian postal code): ").strip()
        
        # Check for exit commands
        if cep.lower() in ('quit', 'exit', 'q'):
            print("👋 Goodbye!")
            break
        
        if not cep:
            print("❌ No CEP provided. Please enter a valid CEP or 'quit' to exit.")
            continue
        
        # Get coordinates
        coords = get_coordinates(cep)
        
        if coords[0] is not None and coords[1] is not None:
            print(f"\n📍 Results for CEP {cep}:")
            print(f"Latitude:  {coords[0]}")
            print(f"Longitude: {coords[1]}")
        else:
            print(f"\n❌ Could not find coordinates for CEP {cep}")
        
        print("\n" + "-" * 40)

if __name__ == "__main__":
    main() 