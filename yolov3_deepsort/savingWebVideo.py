import cv2
import urllib.request
import numpy as np

# Your URL
url='http://175.205.193.91:8081/cam-hi.jpg'
 
fourcc=cv2.VideoWriter_fourcc(*'XVID')

# Timer start
timer_ = 0

# filename, fourcc, fps, frameSize
out=cv2.VideoWriter('C:\\Users\\User\\Desktop\\yolov3_deepsort-master\\data\\video\\web_video.avi', fourcc, 5, (640,480))

if not (out.isOpened()):
   print("File isn't opend!!")
   cap.release()
   sys.exit()
    
while True:
    img_resp=urllib.request.urlopen(url)
    imgnp=np.array(bytearray(img_resp.read()),dtype=np.uint8)
    frame=cv2.imdecode(imgnp,cv2.IMREAD_UNCHANGED)

    cv2.imshow("Fish Stream", frame)
    width = 640
    height = 480
    dim = (width, height)
    frame1 = cv2.resize(frame, dim, interpolation = cv2.INTER_LINEAR)
    
    # Save
    out.write(frame1)
    
    timer_ += 1
    
    key=cv2.waitKey(1)
    if key == ord('q') or timer_ >= 50:
        break
    
out.release()
cv2.destroyAllWindows()
