 Afghanistan number Plate Detection system
In this project I train model using YOLOV8n to detect Afghanistan License plate and then crop the deted part and save it in database with entry and exit time.
to use this project please download all requirements.txt or if you use the docker build dockerfile images:
*** docker installation
```
git pull https://github.com/sifatullahkarwan/Afghanistan_vehicles_plate_detection/new/main?filename=README.md
cd scripts/
docke build .
```
Features
Real-time license plate detection using YOLOv8n

Persian (Jalali) date and 12-hour format support

Entry/Exit logging to SQLite database

Gradio web interface for:

Running detection

Searching by ID

Viewing weekly or full detection history

Docker support for easy deployment
