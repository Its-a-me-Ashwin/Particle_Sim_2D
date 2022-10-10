import cv2
import os
import glob
import numpy as np

class Box:
    def __init__(self,size=[256,256],acc=[0.0,0.0]):
        self.shape = size
        self.points = list()
        self.max = 50
        self._dt = 0.1
        self.accl = [0,25.0]
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
            p._update(self._dt,accl=self.accl)
            if debug:
                print(p)
        if draw:
            self.canvas(hits)

    def _handleColisionSweepAndPrube(self):
        sorted_list = sorted(self.points, key=lambda x: x.position[0])
        active = []
        range_min, range_max = 0.0, 0.0
        for idx in range(sorted_list):
            if len(active) == 0:
                active.append(sorted_list[idx])
            else:
                if sorted_list[idx].position[0] < range_max and sorted_list[idx].position[0] > range_min:
                    ## Posible collision
                    for i in range(len(active)-1):
                        for j in range(1+i,len(active)):
                            if Point._checkIfHit(active[i],active[j]):
                                pass
                else:
                    ## Remove from list
                    active = []
            
            if len(active) == 0:
                range_min = 0.0
                range_max = 0.0
            if len(active) == 1:
                range_min = active[0].position[0] - active[0].radius
                range_max = active[0].position[0] + active[0].radius
            else: 
                for a in active:
                    if range_min > a.position[0] - a.radius:
                        range_min = a.position[0] - a.radius
                    if range_max < a.position[0] + a.radius:
                        range_max = a.position[0] + a.radius

        pass

    def _checkIfHit(self,i,j):
        return np.linalg.norm(self.points[i].position-self.points[j].position) <= self.points[i].radius + self.points[j].radius
    
    def _handleColisionNavie(self):
        hits = []
        for i in range(len(self.points)-1):
            for j in range(1+i,len(self.points)):
                if self._checkIfHit(i,j):
                    # Oh no math
                    m21 = (2 * self.points[i].mass) / (self.points[i].mass + self.points[j].mass)
                    m22 = (2 * self.points[j].mass) / (self.points[i].mass + self.points[j].mass)

                    m11 = (self.points[i].mass - self.points[j].mass) / (self.points[i].mass + self.points[j].mass)

                    self.points[i].velocity = m11*self.points[i].velocity + m22*self.points[j].velocity
                    self.points[j].velocity = (-m11)*self.points[j].velocity + m21*self.points[i].velocity
                    #self.points[i].velocity,self.points[j].velocity = self.points[j].velocity,self.points[i].velocity 
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
        self.mass = np.random.rand(2) * 10
        self.position = np.random.rand(2) * 256
        self.velocity = np.random.rand(2) * 50
        self.radius = 2

    def __repr__(self):
        p = "Pos:" + str(self.position[0]) +" : "+ str(self.position[1])
        v = "Vel:" + str(self.velocity[0]) +" : "+ str(self.velocity[1]) + "\n"
        return p + v

    @classmethod
    def _checkIfHit(self,i,j):
        return np.linalg.norm(i.position-j.position) <= i.radius + j.radius

    def _simpleColision(self,dt):
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

    def _complexColision(self,dt):
        ## Avoidstunneling for single collisions
        position = self.position + self.velocity*dt
        tc = 0.0
        if position[0] < 0:
            tc = (self.radius - position[0]) / (self.position[0] - position[0])
            self.velocity[0] *= -1.0
        elif self.position[0] > 256:
            tc = (256 + self.radius - position[0]) / (self.position[0] - position[0])
            self.velocity[0] *= -1.0
        if self.position[1] < 0:
            tc = (self.radius - position[1]) / (self.position[1] - position[1])
            self.velocity[1] *= -1.0
        elif self.position[1] > 256:
            tc = (256 + self.radius - position[1]) / (self.position[1] - position[1])
            self.velocity[1] *= -1.0
        print(position[0],self.position[0],tc)
        ta = (1-tc)*dt
        if ta > dt: ta = dt
        self.position += self.velocity*ta


        

    def _update(self,dt,accl=[0.0,0.0]):
        # Ignore size of particle
        self.velocity[0] += accl[0]*dt
        self.velocity[1] += accl[1]*dt
        self._simpleColision(dt)
        #self._complexColision(dt)


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
    for i in range(500):
        B._update(draw=True)
    B._convertToVid()