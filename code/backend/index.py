from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from flask import g
import threading
import argparse
import datetime
import imutils
import time
import cv2
import face_recognition
import numpy as np
from picamera.array import PiRGBArray
from picamera import PiCamera
import sqlite3
from uuid import uuid4
from flask_cors import CORS
import io
import time
from flask import request
from flask import make_response, send_from_directory
import os
import RPi.GPIO as GPIO
import discord
import asyncio

buzzer = 23

GPIO.setmode(GPIO.BCM)

GPIO.setup(buzzer,GPIO.OUT)

DATABASE = 'db/camera.db'

camera = PiCamera()
camera.framerate = 30
camera.resolution = (640, 368)
rawCapture = PiRGBArray(camera)

app = Flask(__name__)
CORS(app)


outputFrame = None
lock = threading.Lock()
face_detection_lock = threading.Lock()

frame_rate_face_detect = 60

# vs = VideoStream(src=0).start()
time.sleep(2.0)

process_this_frame = True

  
face_locations = []
face_names = []

discord_messages = []

client = discord.Client()

async def dispatch_notifications(client):
  while(True):
    if len(discord_messages) > 0:
      message = discord_messages.pop()
      user = client.get_user(124579779788800000)
      await user.send(message)
    await asyncio.sleep(1)

client.loop.create_task(dispatch_notifications(client))

@client.event
async def on_ready():
  print('We have logged in into discord as {0.user}'.format(client))


def get_db():
  db = getattr(g, '_database', None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
  return db

def discord_notification():
  client.run('token')

def bell_sound():
  GPIO.output(buzzer,GPIO.HIGH)
  time.sleep(1.5)

  GPIO.output(buzzer,GPIO.LOW)
  time.sleep(0.3)

  GPIO.output(buzzer,GPIO.HIGH)
  time.sleep(0.5)

  GPIO.output(buzzer,GPIO.LOW)
  time.sleep(0.3)

  GPIO.output(buzzer,GPIO.HIGH)
  time.sleep(0.2)


  GPIO.output(buzzer,GPIO.LOW)

def doorbell(face_names):
  bell_sound()
  if len(face_names) > 1:
    message = ', '.join(face_names) + ' stehen vor deiner Tür.'
  else:
    message = ', '.join(face_names) + ' steht vor deiner Tür.'

  discord_messages.append(message)

def generate_jpeg():
  # grab global references to the output frame and lock variables
  global outputFrame, lock
  # loop over frames from the output stream
  while True:
    # wait until the lock is acquired
    with lock:
      # check if the output frame is available, otherwise skip
      # the iteration of the loop
      if outputFrame is None:
        continue
      # encode the frame in JPEG format
      (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
      # ensure the frame was successfully encoded

      if not flag:
        continue
    # yield the output frame in the byte format
    yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
      bytearray(encodedImage) + b'\r\n')


def face_detection(image):
  global face_detection_lock, face_locations, face_names
  small_frame = cv2.resize(image, (0, 0), fx=0.25, fy=0.25)
  rgb_small_frame = small_frame[:, :, ::-1]

  with face_detection_lock:
    with app.app_context():
      known_faces = query_db('select * from faces where known = ?', [1])
      unknown_faces = query_db('select * from faces where known = ?', [0])

      known_faces_encodings = []
      unknown_faces_encodings = []

      for face in known_faces:
        known_faces_encodings.append(np.load('faces/' + face[0] + '.npy'))

      for face in unknown_faces:
        unknown_faces_encodings.append(np.load('faces/' + face[0] + '.npy'))

      face_locations = face_recognition.face_locations(rgb_small_frame)
      face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations, model="small")
      face_names = []

      needs_to_ring = False

      for index, face_encoding in enumerate(face_encodings):
        known_matches = face_recognition.compare_faces(known_faces_encodings, face_encoding)
        unkown_matches = face_recognition.compare_faces(unknown_faces_encodings, face_encoding)

        name = "Unknown"

        if len(known_matches) > 0:
          print("I'm known")
          face_distances = face_recognition.face_distance(known_faces_encodings, face_encoding)
          best_match_index = np.argmin(face_distances)

          if known_matches[best_match_index]:
            name = known_faces[best_match_index][1]
            face_id = known_faces[best_match_index][0]
            counter = known_faces[best_match_index][3]
            last_seen = time.time()

            if (known_faces[best_match_index][4] and time.time() - known_faces[best_match_index][4] > 3600):
              needs_to_ring = True
              counter = counter + 1

            query_db('UPDATE faces SET counter = ?, last_seen = ? where id = ?', [counter, last_seen, face_id])
            face_names.append(name)
            get_db().commit()
            continue

        if len(unkown_matches) > 0:
          print("I'm unkown but already saved")
          face_distances = face_recognition.face_distance(unknown_faces_encodings, face_encoding)
          best_match_index = np.argmin(face_distances)

          if unkown_matches[best_match_index]:
            face_id = unknown_faces[best_match_index][0]
            counter = unknown_faces[best_match_index][3]
            last_seen = time.time()

            if (unknown_faces[best_match_index][4] and time.time() - unknown_faces[best_match_index][4] > 3600):
              needs_to_ring = True
              counter = counter + 1

            query_db('UPDATE faces SET counter = ?, last_seen = ? where id = ?', [counter, last_seen, face_id])

            face_names.append(name)
            get_db().commit()
            continue

        print("I'm unkown")
        needs_to_ring = True
        face_id = str(uuid4())
        np.save('faces/' + face_id + '.npy', face_encoding)
        top, right, bottom, left = face_locations[index]
        cv2.imwrite('faces/' + face_id + '.jpg', image[top*4:bottom*4, left*4:right*4]) 
        query_db('INSERT INTO faces (id, name, known, counter, last_seen) VALUES (?, ?, ?, ?, ?)', [face_id, name, 0, 1, time.time()])
        get_db().commit()
        face_names.append(name)
      
      if needs_to_ring:
        t = threading.Thread(target=doorbell, args=(face_names,))
        t.daemon = True
        t.start()

def query_db(query, args=(), one=False, only_execute=False):
  cur = get_db().execute(query, args)
  if not only_execute:
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv
  else:
    return cur.lastrowid

def video_stream():

  global outputFrame, lock, process_this_frame, face_locations, face_names

  current_frame = 0

  for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    current_frame += 1

    #if process_this_frame:
    t = threading.Thread(target=face_detection, args=(image.copy(), ))
    t.daemon = True
    t.start()

    process_this_frame = False
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(image, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(image, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # lock
    with lock:
      outputFrame = image.copy()
      rawCapture.truncate(0)



@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, '_database', None)
  if db is not None:
    db.close()

@app.route("/video_feed")
def video_feed():
  return Response(generate_jpeg(),
    mimetype = "multipart/x-mixed-replace; boundary=frame")


@app.route("/face-images/<face_image>")
def face_images(face_image):
  return send_from_directory('faces', face_image)


@app.route('/faces', methods=['GET'])
def get_faces():
  known = request.args.get('known')
  faces = []

  if known:
    faces = query_db('SELECT id, name, known, counter, last_seen FROM faces where known = ?', [known])
  else:
    faces = query_db('SELECT id, name, known, counter, last_seen FROM faces', [])

  result = []

  for face in faces:
    result.append({
      "id": face[0],
      "name": face[1],
      "known": face[2],
      "counter": face[3],
      "last_seen": face[4],
      "image": request.host_url + 'face-images/' + face[0] + '.jpg'
    })

  return make_response({
    "data": result
  }, 200)


@app.route('/notification/test', methods=['GET'])
def test_notfication():
  discord_notification()
  return make_response({}, 204)

@app.route('/faces/<face_id>', methods=['DELETE'])
def delete_face(face_id):
  query_db('DELETE FROM faces where id = ?', [face_id])
  get_db().commit()
  os.remove('faces/' + face_id + '.jpg')
  os.remove('faces/' + face_id + '.npy')
  return make_response({}, 204)

@app.route('/remember/<face_id>', methods=['POST'])
def remember(face_id):
  if 'name' in request.form.keys():
    name = request.form['name']

    face = query_db('SELECT * FROM faces where id = ?', [face_id], True)

    if face:
      query_db('UPDATE faces SET name = ?, known = ? where id = ?', [name, 1, face_id])
      get_db().commit()
      return make_response({
        "message": "successfully remembered"
      }, 200)
    else:
      return make_response({
        "message": "face not found"
      }, 404)
  else:
    return make_response({
      "message": "name has to be given"
    }, 400)

@app.route('/')
def index():
  return render_template("index.html")

def init_db():
  with app.app_context():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
      db.cursor().executescript(f.read())
    db.commit()

def run_app():
  app.run(host="0.0.0.0", port="5000", debug=True, threaded=True, use_reloader=False)

if __name__ == '__main__':
  # construct the argument parser and parse command line arguments
  # start a thread that will video stream
  t = threading.Thread(target=video_stream)
  t.daemon = True
  t.start()

  # start a thread that will face detect

  # start the flask app
  appT = threading.Thread(target=run_app)
  appT.daemon = True
  appT.start()
  client.run('token')

# release the video stream pointer
#vs.stop()


GPIO.cleanup()