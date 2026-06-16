def get_data_dictionary():
    """
    Returns the metadata registry (FR-106 Data Dictionary) for Phase 1.
    """
    return {
        "Date": "Flight date (YYYY-MM-DD).",
        "Departure_City": "City from which the flight departs.",
        "Arrival_City": "City where the flight arrives.",
        "Passengers": "Number of passengers on the flight.",
        "Seat_Capacity": "Total seating capacity of the aircraft.",
        "Revenue_USD": "Total revenue generated from ticket sales."
    }
