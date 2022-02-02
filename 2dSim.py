import cv2
import os
import glob
import numpy as np

class Box:
    def __init__(self,size=[256,256]):
        self.shape = size
        self.points = list()
        self.max = 10
        self._dt = 0.1
        self.color = [255,255,255]
        if not os.path.exists('./tempVid'):
            os.makedirs('./tempVid')
        self.frame = 0

    def addPoint(self,point):
        if self.max < len(self.points):
            return
        self.points.append(point)

    def _update(self,draw=False,debug=False):
        hits = self._handleColisionNavie()
        for p in self.points:
            p._update(self._dt)
            if debug:
                print(p)
        if draw:
            self.canvas(hits)

    def _handleColision(self):
        return

    def _checkIfHit(self,i,j):
        return np.linalg.norm(self.points[i].position-self.points[j].position) <= 4
    
    def _handleColisionNavie(self):
        hits = []
        for i in range(len(self.points)-1):
            for j in range(1+i,len(self.points)):
                if self._checkIfHit(i,j):
                    # Oh no math
                    self.points[i].velocity,self.points[j].velocity = self.points[j].velocity,self.points[i].velocity 
                    hits.extend([i,j])
        return hits
    
    def canvas(self,hits=[]):
        canvas = np.zeros(self.shape,dtype=np.uint8)
        for p in range(len(self.points)):
            if p not in hits:
                canvas = cv2.circle(canvas, (int(self.points[p].position[0]),int(self.points[p].position[1])),self.points[p].radius,self.color,-1)
            else:
                for h in hits:
                    canvas = cv2.circle(canvas, (int(self.points[p].position[0]),int(self.points[p].position[1])),self.points[p].radius*5,[255,0,0],-1)
        try:
            cv2.imwrite(os.path.join('./tempVid',str(self.frame)+'.jpg'),canvas)
            self.frame += 1
        except Exception as e:
            print(e)
        if self.frame > 200:
            try:
                self._convertToVid()
                self.frame = 0
            except Exception as e:
                print(e)

    def _convertToVid (self):
        img_array = []
        for filename in glob.glob('./tempVid/*.jpg'):
            img = cv2.imread(filename)
            height, width, layers = img.shape
            size = (width,height)
            img_array.append(img)
         
         
        out = cv2.VideoWriter('sim.avi',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
         
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release()        

        for filename in os.listdir('./tempVid'):
            file_path = os.path.join('./tempVid', filename)
            try:
                if file_path.endswith('jpg'):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def __del__(self):
        # Remove all temp files. disabled
        if False:
             for filename in os.listdir('./tempVid'):
                file_path = os.path.join('./tempVid', filename)
                try:
                    if file_path.endswith('jpg'):
                        os.unlink(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
        
class Point:
    def __init__(self):
        # Equal mass
        self.position = np.random.rand(2) * 256
        self.velocity = np.random.rand(2) * 50
        self.radius = 2

    def __repr__(self):
        p = "Pos:" + str(self.position[0]) +" : "+ str(self.position[1])
        v = "Vel:" + str(self.velocity[0]) +" : "+ str(self.velocity[1]) + "\n"
        return p + v

    def _update(self,dt):
        # Ignore size of particle
        if self.position[0] < 0:
            self.position[0] = 0.0
            self.velocity[0] *= -1.0
        elif self.position[0] > 256:
            self.position[0] = 256.0
            self.velocity[0] *= -1.0
        if self.position[1] < 0:
            self.position[1] = 0.0
            self.velocity[1] *= -1.0
        elif self.position[1] > 256:
            self.position[1] = 256.0
            self.velocity[1] *= -1.0
        self.position += self.velocity*dt


if __name__ == '__main__':
    B = Box()
    P1 = Point()
    P2 = Point()
    P3 = Point()
    P4 = Point()
    P5 = Point()
    P6 = Point()

    P11 = Point()
    P21 = Point()
    P31 = Point()
    P41 = Point()
    P51 = Point()
    P61 = Point()
    B.addPoint(P1)
    B.addPoint(P2)
    B.addPoint(P3)
    B.addPoint(P4)
    B.addPoint(P5)
    B.addPoint(P6)

    B.addPoint(P11)
    B.addPoint(P21)
    B.addPoint(P31)
    B.addPoint(P41)
    B.addPoint(P51)
    B.addPoint(P61)
    for i in range(200):
        B._update(draw=True)
