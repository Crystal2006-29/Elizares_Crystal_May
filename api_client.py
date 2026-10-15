import requests 
url = "https://elizares-crystal-may.onrender.com/course" 
response = requests.get(url) 
if response.status_code == 200: 
    data = response.json() 
    print("Course:", data["course"]) 
    print("Program:", data["program"])  
else: 
    print("Request failed.") 
    print("Status Code:", response.status_code)