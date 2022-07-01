import pymysql
import datetime as dt
import time, random
import numpy as np
from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import matplotlib.pyplot as plt
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.utils import draw_outputs, convert_boxes

from deep_sort import preprocessing
from deep_sort import nn_matching
from deep_sort.detection import Detection
from deep_sort.tracker import Tracker
from tools import generate_detections as gdet
from PIL import Image

flags.DEFINE_string('classes', './data/labels/coco.names', 'path to classes file')
flags.DEFINE_string('weights', './weights/yolov3.tf',
                    'path to weights file')
flags.DEFINE_boolean('tiny', False, 'yolov3 or yolov3-tiny')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_string('video', './data/video/test.mp4',
                    'path to video file or number for webcam)')
flags.DEFINE_string('output', None, 'path to output video')
flags.DEFINE_string('output_format', 'XVID', 'codec used in VideoWriter when saving video to file')
flags.DEFINE_integer('num_classes', 80, 'number of classes in the model')

# DB Connection and Cursor
conn = pymysql.connect(host= '127.0.0.1', user='root', password='as19778797', db='fishbowl',port = 3306, charset='utf8')
cur = conn.cursor(pymysql.cursors.DictCursor)

fish_moving = {}

dict_tracks = {"fish":{}}

def get_patterns(center,track_id):
    #This function stores all tracked fish and their moving patterns
    if str(track_id) in dict_tracks["fish"]:
        dict_tracks["fish"][str(track_id)].append(center)
    elif str(track_id) not in dict_tracks["fish"]:
        dict_tracks["fish"][str(track_id)] = []
        dict_tracks["fish"][str(track_id)].append(center)
    if len(dict_tracks["fish"][str(track_id)]) > 60:
        del dict_tracks["fish"][str(track_id)][:10]
            
    return dict_tracks["fish"][str(track_id)]

    
def main(_argv):
    # Definition of the parameters
    max_cosine_distance = 0.5
    nn_budget = None
    nms_max_overlap = 1.0
    
    #initialize deep sort
    model_filename = 'model_data/mars-small128.pb'
    encoder = gdet.create_box_encoder(model_filename, batch_size=1)
    metric = nn_matching.NearestNeighborDistanceMetric("cosine", max_cosine_distance, nn_budget)
    tracker = Tracker(metric)

    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    if len(physical_devices) > 0:
        tf.config.experimental.set_memory_growth(physical_devices[0], True)

    if FLAGS.tiny:
        yolo = YoloV3Tiny(classes=FLAGS.num_classes)
    else:
        yolo = YoloV3(classes=FLAGS.num_classes)

    yolo.load_weights(FLAGS.weights)
    logging.info('weights loaded')

    class_names = [c.strip() for c in open(FLAGS.classes).readlines()]
    logging.info('classes loaded')

    try:
        vid = cv2.VideoCapture(int(FLAGS.video))
    except:
        vid = cv2.VideoCapture(FLAGS.video)

    out = None

    if FLAGS.output:
        # by default VideoCapture returns float instead of int
        width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(vid.get(cv2.CAP_PROP_FPS))
        codec = cv2.VideoWriter_fourcc(*FLAGS.output_format)
        out = cv2.VideoWriter(FLAGS.output, codec, fps, (width, height))
        list_file = open('detection.txt', 'w')
        frame_index = -1 
    
    #fps = 0.0
    count = 0

    
    
    old_detection = {}
    
    old_detections = []
    
    detection_flag = 0
    
    missing_count = 0
    
    while True:
        _, img = vid.read()

        if img is None:
            logging.warning("Empty Frame")
            time.sleep(0.1)
            count+=1
            if count < 3:
                continue
            else: 
                break

        img_in = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_in = tf.expand_dims(img_in, 0)
        img_in = transform_images(img_in, FLAGS.size)

        t1 = time.time()
        boxes, scores, classes, nums = yolo.predict(img_in)
        classes = classes[0]
        names = []
        for i in range(len(classes)):
            names.append(class_names[int(classes[i])])
        names = np.array(names)
        converted_boxes = convert_boxes(img, boxes[0])
        features = encoder(img, converted_boxes)    
        detections = [Detection(bbox, score, class_name, feature) for bbox, score, class_name, feature in zip(converted_boxes, scores[0], names, features)]
        
        #initialize color map
        cmap = plt.get_cmap('tab20b')
        colors = [cmap(i)[:3] for i in np.linspace(0, 1, 20)]

        # run non-maxima suppresion
        boxs = np.array([d.tlwh for d in detections])
        scores = np.array([d.confidence for d in detections])
        classes = np.array([d.class_name for d in detections])
        indices = preprocessing.non_max_suppression(boxs, classes, nms_max_overlap, scores)
        detections = [detections[i] for i in indices]

        

        new_detection = {}
        t_id = 0
        
        # All objects detected
        #if len(detections) == 3:
        #    detection_flag = 1
        
        # Missing object
        #if detection_flag == 1 and len(detections) < 3:
        #    missing_count += 1
        #    if missing_count == 5:
        #        detections.append(old_detections)
        #        missing_count = 0
                
                
        # Call the tracker
        tracker.predict()
        tracker.update(detections)
        
        for track in tracker.tracks:
            if not track.is_confirmed() or track.time_since_update > 1:
                continue 
            bbox = track.to_tlbr()
            class_name = track.get_class()
            
            # Center Point
            c_curr = int ( (bbox[2] - bbox[0]) / 2 + bbox[0] ) , int ( (bbox[3] - bbox[1]) / 2 + bbox[1] )
            
            if old_detection != None:
                #for nKey, nValue in new_detection.items():
                for oKey, oValue in old_detection.items():
                    #Bounding box showing(old)
                    if abs(c_curr[0]-oValue[0]) + abs(c_curr[1]-oValue[1]) < 40:
                        color = colors[int(oKey) % len(colors)]
                        color = [i * 255 for i in color]
                        cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
                        cv2.rectangle(img, (int(bbox[0]), int(bbox[1]-30)), (int(bbox[0])+(len(class_name)+len(str(oKey)))*17, int(bbox[1])), color, -1)
                        cv2.putText(img, class_name + "-" + str(oKey) + str(c_curr),(int(bbox[0]), int(bbox[1]-10)),0, 0.75, (255,255,255),2)
                        
                        #store patterns of individual fish
                        pattern = get_patterns(c_curr,oKey)
                        pre_p = c_curr
                        
                        #Draw the patterns on the screen
                        for p in pattern[-50::5]:
                            cv2.circle(img,p,5,color,-1)
                            if pre_p != c_curr:
                                cv2.line(img,pre_p,p,color,2)
                                #distance of two center points
                                distance = ( (pre_p[0] - p[0])**2 + (pre_p[0] -  pre_p[1])**2 )**(1/2)

                                #Saving distance
                                if str(oKey) in fish_moving:
                                    fish_moving[str(oKey)].append(distance)
                                elif str(oKey) not in fish_moving:
                                    fish_moving[str(oKey)] = []
                                    fish_moving[str(oKey)].append(distance)
                                    
                                if len(fish_moving[str(oKey)]) > 600:
                                    #Saving point of DB
                                    x = dt.datetime.now()
                                    date = x.strftime("%x")
                                    time_ = x.strftime("%X")
                                    ID = str(oKey)
                                    Mobility = str(round( sum(fish_moving[str(oKey)])/100000, 2))
                                    data = (date, time_, ID, Mobility)
                                    sql = "INSERT INTO fish_mobility (Date, Time, fish_ID, fish_mobility) VALUES(%s, %s, %s, %s);"
                                    try:
                                        cur.execute(sql, data)
                                        conn.commit()
                                        print('DB INSERTED')
                                    except:
                                        print('SQL Error')
                                    
                                    fish_moving[str(oKey)].clear()
                                    
                            pre_p = p
                            
                        #ID key given, swap ID
                        #if track.track_id != None and track.track_id != oKey:
                            #track.track_id = oKey
                        t_id = oKey

                    else:
                        #Bounding box showing(new)
                        color = colors[int(track.track_id) % len(colors)]
                        color = [i * 255 for i in color]
                        cv2.rectangle(img, (int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])), color, 2)
                        cv2.rectangle(img, (int(bbox[0]), int(bbox[1]-30)), (int(bbox[0])+(len(class_name)+len(str(track.track_id)))*17, int(bbox[1])), color, -1)
                        cv2.putText(img, class_name + "-" + str(track.track_id) + str(c_curr),(int(bbox[0]), int(bbox[1]-10)),0, 0.75, (255,255,255),2)
                        
                        #store patterns of individual fish
                        pattern = get_patterns(c_curr,track.track_id)
                        pre_p = c_curr
                        
                        #Draw the patterns on the screen
                        for p in pattern[-50::5]:
                            cv2.circle(img,p,5,color,-1)
                            if pre_p != c_curr:
                                cv2.line(img,pre_p,p,color,2)
                                #distance of two center points
                                distance = ( (pre_p[0] - p[0])**2 + (pre_p[0] -  pre_p[1])**2 )**(1/2)
                                
                                #Saving distance
                                if str(track.track_id) in fish_moving:
                                    fish_moving[str(track.track_id)].append(distance)
                                elif str(track.track_id) not in fish_moving:
                                    fish_moving[str(track.track_id)] = []
                                    fish_moving[str(track.track_id)].append(distance)
                                if len(fish_moving[str(track.track_id)]) > 600:
                                    #Saving point of DB
                                    x = dt.datetime.now()
                                    date = x.strftime("%x")
                                    time_ = x.strftime("%X")
                                    ID = str(track.track_id)
                                    Mobility = str(round( sum(fish_moving[str(track.track_id)])/100000, 2))
                                    data = (date, time_, ID, Mobility)
                                    sql = "INSERT INTO fish_mobility (Date, Time, fish_ID, fish_mobility) VALUES(%s, %s, %s, %s);"
                                    try:
                                        cur.execute(sql, data)
                                        conn.commit()
                                        print('DB INSERTED')
                                    except:
                                        print('SQL Error')

                                    fish_moving[str(track.track_id)].clear()
                                    
                            pre_p = p
                            
                        #ID key given
                        t_id = track.track_id
                        
            new_detection[t_id] = [((int(bbox[2]) - int(bbox[0]))/2 + int(bbox[0])), (int(bbox[3])-int(bbox[1]))/2 + int(bbox[1])]

            
            
        old_detection = new_detection.copy()
        
        #if len(detections) == 3:
        #    old_detections = detections
        
            
        ### UNCOMMENT BELOW IF YOU WANT CONSTANTLY CHANGING YOLO DETECTIONS TO BE SHOWN ON SCREEN
        #for det in detections:
        #    bbox = det.to_tlbr() 
        #    cv2.rectangle(img,(int(bbox[0]), int(bbox[1])), (int(bbox[2]), int(bbox[3])),(255,0,0), 2)
        
        # print fps on screen 
        fps  = ( fps + (1./(time.time()-t1)) ) / 2
        cv2.putText(img, "FPS: {:.2f}".format(fps), (0, 30), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 2)
        cv2.imshow('output', img)
        if FLAGS.output:
            out.write(img)
            frame_index = frame_index + 1
            list_file.write(str(frame_index)+' ')
            if len(converted_boxes) != 0:
                for i in range(0,len(converted_boxes)):
                    list_file.write(str(converted_boxes[i][0]) + ' '+str(converted_boxes[i][1]) + ' '+str(converted_boxes[i][2]) + ' '+str(converted_boxes[i][3]) + ' ')
            list_file.write('\n')

        # press q to quit
        if cv2.waitKey(1) == ord('q') or ord('Q'):
            break
        
    vid.release()
    conn.close()
    if FLAGS.output:
        out.release()
        list_file.close()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
