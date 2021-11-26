import uuid
UPLOAD_FOLDER = 'data'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
from datetime import datetime


def obtener_uuid():
    return str(uuid.uuid4())


def fecha_y_hora():
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d %H:%M:%S | lovecodecam")
    return fecha


def fecha_y_hora_para_nombre_archivo():
    ahora = datetime.now()
    fecha = ahora.strftime("%Y-%m-%d_%H-%M-%S")
    return fecha

def allowed_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def processesing(arr):
  for i in arr:
    if(i[0]>i[1]):
      return 0
    else:
      return 1

def percentage(u,pre):
  sum=u[0][0]+u[0][1]
  return 100*u[0][pre]/sum

