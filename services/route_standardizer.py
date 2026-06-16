def standardize_route(origin_city, dest_city):
    # Generate a 3-letter IATA-like code from the first 3 letters
    origin_iata = origin_city[:3].upper()
    dest_iata = dest_city[:3].upper()
    
    # Create canonical route ID (alphabetical order)
    if origin_iata < dest_iata:
        route_id = f"{origin_iata}-{dest_iata}"
    else:
        route_id = f"{dest_iata}-{origin_iata}"
        
    return route_id, origin_iata, dest_iata
