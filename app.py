import cv2
import numpy as np
import utiles
from flask import Flask, flash, redirect, render_template, request, Response, jsonify
from tensorflow.keras.models import load_model
from keras.preprocessing import image
from keras.preprocessing.image import load_img, img_to_array 
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array,load_img
from base64 import b64encode
import os
from model_config import get_model

FRAMES_VIDEO = 20.0
RESOLUCION_VIDEO = (640, 480)
# Marca de agua
# https://docs.opencv.org/master/d6/d6e/group__imgproc__draw.html#ga5126f47f883d730f633d74f07456c576
UBICACION_FECHA_HORA = (0, 15)
FUENTE_FECHA_Y_HORA = cv2.FONT_HERSHEY_PLAIN
ESCALA_FUENTE = 1
COLOR_FECHA_HORA = (255, 255, 255)
GROSOR_TEXTO = 1
TIPO_LINEA_TEXTO = cv2.LINE_AA
fourcc = cv2.VideoWriter_fourcc(*'XVID')
archivo_video = None
grabando = False

model = load_model("detection_model.h5")


face_haar_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

app = Flask(__name__,static_folder='static',template_folder='templates')

acurracy = 0.0

camara = cv2.VideoCapture(0)
camara.set(3, 1920)
camara.set(4, 1080)
def gen_frame(begin):
    if begin == 1:
        global camara
        camara = cv2.VideoCapture(0)
        camara.set(3, 1920)
        camara.set(4, 1080)
        while begin == 1:
            global frame
            success, frame = camara.read()
            if not success:
                break
            else:#agarro el frame y lo comviert a imagen
                gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)#diferencio los colores de caras con la mascarilla
                faces_detected = face_haar_cascade.detectMultiScale(gray_img, 1.32, 5)#cantidad de caras
                for (x, y, w, h) in faces_detected:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), thickness=3)
                    roi_gray = gray_img[y:y + w, x:x + h]  # cropping region of interest i.e. face area from  image
                    roi_gray = cv2.resize(roi_gray, (224, 224))
                    img_pixels = image.img_to_array(roi_gray)
                    img_pixels = np.expand_dims(img_pixels, axis=0)
                    img_pixels /= 255

                    predictions = model.predict(img_pixels)
                    print("PREDICTIONS", predictions)
                    # find max indexed array
                    max_index = np.argmax(predictions[0])
                    print("Porcentaje", predictions[0][max_index] * 100)
                    acurracy = predictions[0][max_index] * 100
                    acurracy = round(acurracy, 2)
                    categories = ('incorrect', 'withMask', 'withoutMask')
                    predicted_category = categories[max_index]
                    print(predicted_category)

                    cv2.putText(frame, predicted_category + " " + str(acurracy), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    #cv2.putText(frame, acurracy, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                #resized_img = cv2.resize(frame, (1000, 700))
                #a=cv2.imshow('MASK Category', resized_img)
                ret, img = cv2.imencode('.jpg', frame)
                img = img.tobytes()
                yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
                
    else:
        camara.release()

@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    return response


@app.route("/")
def home():
    return render_template("index.html", begin=0,capture_btn = False, captured_img = None)

@app.route("/start_video", methods=["POST","GET"])
def start_video():
    return render_template('index.html', begin = 1, capture_btn = True, captured_img = None)

@app.route('/end_video', methods=["POST","GET"])
def end_video():
    return render_template('index.html', begin= 0, capture_btn = False, captured_img = None)

app.config["CACHE_TYPE"] = "null"
@app.route('/capture', methods=["POST", "GET"])
def capture():
    global frame
    #print(frame, frame.shape)
    cv2.imwrite('./static/captured.jpg', frame)
    image_bn = open('./static/captured.jpg', 'rb').read()
    image = b64encode(image_bn).decode('utf-8')
    return jsonify({'status':1, 'image': image})

@app.route('/video_feed/<int:begin>', methods=["POST","GET"])
def video_feed(begin):
    return Response(gen_frame(begin), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/delete_img', methods=["POST", "GET"])
def delete_img():
    os.remove("./static/captured.jpg")
    return render_template('index.html', begin = 1, capture_btn = True, captured_img = None)

@app.route('/retry', methods=['POST', 'GET'])
def retry():
    os.remove("./static/captured.jpg")
    os.remove("./static/pred_img.jpg")
    return render_template('index.html', begin = 1, capture_btn = True, captured_img = None)  

if __name__=='__main__':
    app.run(debug=True)
