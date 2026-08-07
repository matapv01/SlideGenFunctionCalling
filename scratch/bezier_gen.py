import math

def cubic_bezier(t, p0, p1, p2, p3):
    x = (1-t)**3 * p0[0] + 3*(1-t)**2 * t * p1[0] + 3*(1-t) * t**2 * p2[0] + t**3 * p3[0]
    y = (1-t)**3 * p0[1] + 3*(1-t)**2 * t * p1[1] + 3*(1-t) * t**2 * p2[1] + t**3 * p3[1]
    return x, y

def get_organic_blob_points():
    pts = []
    # Top edge
    pts.append((0, 0))
    pts.append((700, 0))
    
    # Curve 1 (from 700,0 to 300,250)
    # Control points: P1=(700, 200), P2=(450, 220)
    for i in range(1, 21):
        t = i / 20.0
        x, y = cubic_bezier(t, (700, 0), (700, 200), (450, 220), (300, 250))
        pts.append((x, y))
        
    # Curve 2 (from 300,250 to 0,550)
    # Control points: P1=(150, 280), P2=(50, 450)
    for i in range(1, 21):
        t = i / 20.0
        x, y = cubic_bezier(t, (300, 250), (150, 280), (50, 450), (0, 550))
        pts.append((x, y))
        
    return " ".join([f"{int(x)},{int(y)}" for x, y in pts])

print(get_organic_blob_points())
