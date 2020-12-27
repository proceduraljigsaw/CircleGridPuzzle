# Copyright (c) 2020 ProceduralJigsaw
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import numpy as np
import tkinter as tk
import time
import random
from numpy.random import uniform
class Cell():
    def __init__(self, coords):
        self.coords = coords
    def vertices(self):
        return [self.coords, (self.coords[0]+1, self.coords[1]),(self.coords[0], self.coords[1]+1),(self.coords[0]+1, self.coords[1]+1)]
    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self is other or (self.coords == other.coords)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

class DiagCon():
    def __init__(self, p1, p2, p2_taken=True):
        self.p1 =p1
        self.p2 =p2
        self.p2_taken = p2_taken
        #slope is useless for now
        self.slope = (p2[1]-p1[1])/(p2[0]-p1[0])
        ccoords =(min([p2[0],p1[0]]),min([p2[1],p1[1]]))
        self.cell = Cell(ccoords)
        if(self.slope > 0):
            if p2[1]>p1[1]:
                self.quadrant = 3
            else:
                self.quadrant = 1
        else:
            if p2[1]>p1[1]:
                self.quadrant = 2
            else:
                self.quadrant = 0

    @classmethod
    def frompointquad(cls,p1,quadrant,p2_taken=True):
        self = cls.__new__(cls)
        self.p1 = p1
        self.quadrant = quadrant
        if quadrant == 0:
            p2 =(p1[0]+1,p1[1]-1)
        elif quadrant == 1:
            p2 =(p1[0]-1,p1[1]-1)
        elif quadrant ==2 :
            p2 =(p1[0]-1,p1[1]+1)
        else:
            p2 =(p1[0]+1,p1[1]+1)
        self.p2 =p2
        self.slope = (p2[1]-p1[1])/(p2[0]-p1[0])
        ccoords =(min([p2[0],p1[0]]),min([p2[1],p1[1]]))
        self.cell = Cell(ccoords)
        self.p2_taken = p2_taken
        return self

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self is other or (self.cell == other.cell and self.slope == other.slope and self.p2_taken == other.p2_taken)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

        """[summary]
            vertex(0,0)         vertex(1,0)
                        *------*
                        | CELL |
                        | (0,0)|
            vertex(0,1) *------* vertex(1,1)
        """
class Cellgrid():
    def __init__(self, nrow, ncol):
        self.nrow = nrow
        self.ncol = ncol
        self.notvisitedvertices = [(x,y)  for x in range(0,ncol) for y in range(0,nrow)]
        self.reset()

    def reset(self):
        ncol = self.ncol
        nrow = self.nrow
        self.vertexgrid = np.zeros((ncol,nrow), dtype=int)#([[0 for x in range(0,ncol)] for y in range(0,nrow)])
        self.emptycells =[Cell((x,y))  for x in range(0,ncol-1) for y in range(0,nrow-1)]

    def markvertex(self,v,num):
        self.vertexgrid[v]=num

        """
            Q1 Q0
            Q2 Q3
        """


class CircleArc():
    def __init__(self, gcp, rad, offs, quadrant, sign):
        cp = (gcp[0]*2*rad+rad+offs, gcp[1]*2*rad+rad+offs)
        self.cp = cp
        self.quadrant = quadrant
        self.rad = rad
        self.sign = sign
        if quadrant == 0:
            pa = (cp[0]+rad, cp[1])
            pb = (cp[0], cp[1]-rad)
        elif quadrant == 1:
            pa = (cp[0], cp[1]-rad)
            pb = (cp[0]-rad, cp[1])
        elif quadrant == 2:
            pa = (cp[0]-rad, cp[1])
            pb = (cp[0], cp[1]+rad)
        else:
            pa = (cp[0], cp[1]+rad)
            pb = (cp[0]+rad, cp[1])

        if self.sign == '-':
            self.startpoint = pa
            self.endpoint = pb
        else:
            self.startpoint = pb
            self.endpoint = pa

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self is other or (self.cp == other.cp and self.quadrant == other.quadrant)
        else:
            return False
            
    def painttocanvas(self,canvas,border,color="black",width=2):
        bwidth = int(round(max(width,self.rad/5),0))
        canvas.create_arc(self.cp[0]-self.rad, self.cp[1]-self.rad, self.cp[0]+self.rad, self.cp[1]+self.rad,start=90*(self.quadrant), width =bwidth, extent = 90, outline="black",style=tk.ARC)

