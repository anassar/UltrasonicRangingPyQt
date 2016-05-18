#!/usr/bin/python

import sys
import time 
import random
import math
from threading import Thread
from PyQt4 import QtGui, QtCore

class UltrasonicRanging(QtGui.QWidget):
    
    def __init__(self):
        super(UltrasonicRanging, self).__init__()
        self.cx        = 650
        self.cy        = 650
        self.radius    = 500
        self.scanAngle = 0
        self.l2r       = False
        self.ranges    = []
        for i in range(0, 20):
            self.ranges.append( self.getNextRadius() )
        self.initUI()
        
    def initUI(self):
        self.setGeometry(50, 50, 800, 400)
        self.setWindowTitle('Ultrasonic Ranging')
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        p = self.palette()
        p.setColor(self.backgroundRole(), QtCore.Qt.white)
        self.setPalette(p)
        self.drawRadar(qp)
        qp.end()
        
    def drawRadar(self, qp):
        self.drawGrid   (qp)
        self.drawScanRay(qp)
        self.drawRanges (qp)
        self.updateScanAngle()


    def drawGrid(self, qp):
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        qp.setBrush(QtGui.QColor(0, 200, 0))
        qp.setPen(pen)
        qp.setOpacity(0.2)
        qp.setRenderHint( QtGui.QPainter.Antialiasing )

        # Draw radial grid lines
        for i in range(0, 11):
            line = QtCore.QLineF(self.cx, self.cy, 0, 0)
            line.setAngle(15*(i+1))
            line.setLength( self.radius )
            qp.drawLine(line);

        # Draw grid arcs
        # Angle must be specified in 1/16th of a degree
        startAngle =  0 * 16
        spanAngle = 180 * 16
        diam = 2*self.radius
        for i in range(0, 10):
            rect = QtCore.QRectF(150.0 + i*50, 150.0 + i*50, diam - i*100, diam - i*100)
            qp.drawChord(rect, startAngle, spanAngle);

    def drawScanRay(self, qp):
        angle = self.scanAngle
        alpha = 1
        for i in range(0, 50):
            if ( angle > 180 ):
                break
            if ( angle <   0 ):
                break
            ScanRay = QtCore.QLineF(self.cx, self.cy, 0, 0)
            ScanRay.setAngle( angle );
            ScanRay.setLength( self.radius )
            qp.setOpacity( alpha )
            pen = QtGui.QPen(QtCore.Qt.yellow, 2, QtCore.Qt.DotLine)
            qp.setPen(pen)
            qp.drawLine( ScanRay );
            alpha = alpha - 0.02
            if ( self.l2r ):
                angle = angle + 30.0/50.0
            else:
                angle = angle - 30.0/50.0



    def drawRanges(self, qp):
        alpha = 1.0
        scale = 1.0
        N = len(self.ranges)
        eps = 180.0/N
        pen = QtGui.QPen(QtCore.Qt.blue, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        for i in range(0, 100):
            angle = 0
            qp.setOpacity( alpha )
            for i in range(0, N):
                r1 = self.ranges[i-1]
                r2 = self.ranges[i]
                if ( r1 > self.radius and r2 > self.radius ):
                    angle = angle + eps
                    r1 = r2
                    continue
                rr1 = scale*r1; rr2 = scale*r2
                if ( rr1 > self.radius ):
                    rr1 = self.radius
                if ( rr2 > self.radius ):
                    rr2 = self.radius
                x1 = self.cx + rr1*math.cos(math.pi * (angle    )/180.0)
                y1 = self.cy - rr1*math.sin(math.pi * (angle    )/180.0)
                x2 = self.cx + rr2*math.cos(math.pi * (angle+eps)/180.0)
                y2 = self.cy - rr2*math.sin(math.pi * (angle+eps)/180.0)
                line = QtCore.QLineF( x1, y1, x2, y2 )
                qp.drawLine( line );
                angle = angle + 180.0/N
            alpha = alpha*0.957
            scale = scale*1.004



    def updateScanAngle(self):
        N = len(self.ranges)
        i = int( math.floor((self.scanAngle/180.0)*N) )
        if ( self.l2r ):
            self.scanAngle = self.scanAngle - 5
            if ( self.scanAngle < 0 ):
                self.l2r = False
                self.scanAngle = 0
        else:
            i = int( math.ceil((self.scanAngle/180.0)*N) )
            self.scanAngle = self.scanAngle + 5
            if ( self.scanAngle > 180 ):
                self.l2r = True
                self.scanAngle = 180
        j = int( math.floor((self.scanAngle/180.0)*N) )
        if (i!=j):
            self.ranges[j] = self.getNextRadius()


    def getNextRadius(self):
        return ( self.radius/2.0 * ( 0.5 + random.uniform(0, 0.5) ) )


def repaintRadar( r ):
    while(True):
        time.sleep(0.05)
        r.update()


def main():
    app = QtGui.QApplication(sys.argv)
    r = UltrasonicRanging()
    thr = Thread(target = repaintRadar, args = (r, ))
    try:
        thr.start()
    except:
        print "Error: unable to start thread"
    sys.exit(app.exec_())
    
if __name__ == '__main__':
    main()
