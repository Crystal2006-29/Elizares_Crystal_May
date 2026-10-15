import requests 
url = "https://flask-palec-sethclaire-api.onrender.com/student" 
response = requests.get(url) 
if response.status_code == 200: 
    data = response.json() 
    print("Student ID:", data["student_id"]) 
    print("Name:", data["name"]) 
    print("Program:", data["program"]) 
    print("Year:", data["year"]) 
    print("Section:", data["section"])  
    
else: 
    print("Request failed.") 
    print("Status Code:", response.status_code)