def get_bbox(level="arrival"):
    if level == "arrival":
        # Focused on SFO approaches (Runways 28L/28R)
        return (-122.6, -122.0, 37.4, 37.8)
    elif level == "balanced":
        return (-123.5, -121.5, 36.5, 38.5)
    elif level == "max1credit":
        return (-127.5, -117.5, 35.0, 40.0)
    else:
        raise ValueError("Unknown bbox level")
    