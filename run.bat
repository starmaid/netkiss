echo serving on http://localhost:80

start cmd /c py .\app\manager.py

timeout 5

start cmd /c py .\app\app.py