import tkinter as tk
from tkinter import ttk
import requests
import threading
from geopy.geocoders import Nominatim

API_URL = "http://127.0.0.1:8000"
geolocator = Nominatim(user_agent="taxi_app_free")

# Dynamic location search for real-time dropdown suggestions
def update_pickup_suggestions(event):
    query = pickup_combo.get()
    if len(query) > 2:
        locations = geolocator.geocode(query, exactly_one=False, limit=5)
        suggestions = [loc.address for loc in locations] if locations else []
        pickup_combo["values"] = suggestions

def update_dropoff_suggestions(event):
    query = dropoff_combo.get()
    if len(query) > 2:
        locations = geolocator.geocode(query, exactly_one=False, limit=5)
        suggestions = [loc.address for loc in locations] if locations else []
        dropoff_combo["values"] = suggestions

def geocode_address(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return f"{location.latitude}, {location.longitude}"
        else:
            return "Location not found"
    except Exception as e:
        return f"Error: {e}"

def request_ride():
    pickup = pickup_combo.get()
    dropoff = dropoff_combo.get()
    pickup_coords = geocode_address(pickup)
    dropoff_coords = geocode_address(dropoff)

    data = {
        "caller_name": caller_name_entry.get(),
        "pickup": f"{pickup} ({pickup_coords})",
        "dropoff": f"{dropoff} ({dropoff_coords})"
    }
    def run():
        try:
            r = requests.post(f"{API_URL}/request_ride", json=data)
            caller_status_label.config(text=r.json().get("message", "Error requesting ride"))
        except Exception as e:
            caller_status_label.config(text=f"Error: {e}")
    threading.Thread(target=run).start()

def view_rides():
    def run():
        try:
            r = requests.get(f"{API_URL}/available_rides")
            rides_list.delete(0, tk.END)
            for ride in r.json().get("available_rides", []):
                rides_list.insert(tk.END, f"ID:{ride[0]} Caller:{ride[1]} From:{ride[2]} To:{ride[3]}")
        except Exception as e:
            driver_status_label.config(text=f"Error: {e}")
    threading.Thread(target=run).start()

def accept_ride():
    ride_id = ride_id_entry.get()
    driver_name = driver_name_entry.get()
    data = {"driver_name": driver_name}
    def run():
        try:
            r = requests.post(f"{API_URL}/accept_ride/{ride_id}", json=data)
            driver_status_label.config(text=r.json().get("message", "Error accepting ride"))
        except Exception as e:
            driver_status_label.config(text=f"Error: {e}")
    threading.Thread(target=run).start()

root = tk.Tk()
root.title("Taxi App - Real-Time Dropdown Suggestions")
root.geometry("450x600")

# Caller Frame
caller_frame = tk.LabelFrame(root, text="Caller", padx=10, pady=10)
caller_frame.pack(padx=10, pady=10, fill="both")

tk.Label(caller_frame, text="Caller Name:").pack()
caller_name_entry = tk.Entry(caller_frame)
caller_name_entry.pack()

tk.Label(caller_frame, text="Pickup Location:").pack()
pickup_combo = ttk.Combobox(caller_frame)
pickup_combo.pack()
pickup_combo.bind("<KeyRelease>", update_pickup_suggestions)

tk.Label(caller_frame, text="Dropoff Location:").pack()
dropoff_combo = ttk.Combobox(caller_frame)
dropoff_combo.pack()
dropoff_combo.bind("<KeyRelease>", update_dropoff_suggestions)

tk.Button(caller_frame, text="Request Ride", command=request_ride).pack(pady=5)

caller_status_label = tk.Label(caller_frame, text="")
caller_status_label.pack(pady=5)

# Driver Frame
driver_frame = tk.LabelFrame(root, text="Driver", padx=10, pady=10)
driver_frame.pack(padx=10, pady=10, fill="both")

tk.Button(driver_frame, text="View Available Rides", command=view_rides).pack(pady=5)

rides_list = tk.Listbox(driver_frame, width=55, height=10)
rides_list.pack(pady=5)

tk.Label(driver_frame, text="Ride ID to Accept:").pack()
ride_id_entry = tk.Entry(driver_frame)
ride_id_entry.pack()

tk.Label(driver_frame, text="Driver Name:").pack()
driver_name_entry = tk.Entry(driver_frame)
driver_name_entry.pack()

tk.Button(driver_frame, text="Accept Ride", command=accept_ride).pack(pady=5)

driver_status_label = tk.Label(driver_frame, text="")
driver_status_label.pack(pady=5)

root.mainloop()
