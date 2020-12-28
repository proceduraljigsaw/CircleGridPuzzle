# Copyright (c) 2020 ProceduralJigsaw
#
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT

import random
import os
import sys
import math
import tkinter as tk
from tkinter import filedialog,ttk
import svgwrite
import itertools
import numpy as np
from numpy.random import uniform
from extraclasses import Cell,DiagCon,Cellgrid,CircleArc

class SliderDesc():
    def __init__(self, text, minv, maxv, res, col, var, colspan=None):
        self.text = text
        self.min = minv
        self.max = maxv
        self.res = res
        self.col = col
        self.var = var
        self.colspan = colspan


class ButtonDesc():
    def __init__(self, text, command, col, textvar=None, colspan=None):
        self.text = text
        self.command = command
        self.textvar = textvar
        self.col = col
        self.colspan = colspan


class MazeGui():
    def __init__(self, root):
        self.root = root
        self.dframe = tk.Frame(self.root, width=800, height=800, borderwidth=2)
        self.aframe = tk.Frame(self.root, height=1000)
        self.aframe.pack(side="left")


        self.ncol = tk.IntVar(value=20) 
        self.nrow = tk.IntVar(value=20)  
        self.frame = tk.IntVar(value=10) 
        self.circlerad = tk.IntVar(value=10) 
        self.minpl = tk.IntVar(value=4) 
        self.maxpl = tk.IntVar(value=50) 
        self.progress = tk.IntVar(value=0)

        self.width = self.ncol.get()*2*self.circlerad.get()+2*self.frame.get()
        self.height = self.nrow.get()*2*self.circlerad.get()+2*self.frame.get()
        self.canvas = tk.Canvas(self.dframe, bg="white", width=self.width, height=self.height,borderwidth=0, highlightthickness=0)
        grid_sliders = [
            SliderDesc("Columns", 5, 80, 1, 0, self.ncol),
            SliderDesc("Rows", 5,80, 1, 1, self.nrow),
            SliderDesc("Circle rad", 3, 50, 1, 0, self.circlerad),
            SliderDesc("Frame", 0,100, 1, 1, self.frame),
            SliderDesc("Min piece circles", 2, 50, 1, 0, self.minpl),
            SliderDesc("Max piece circles", 2,100, 1, 1, self.maxpl)]
            
        gen_btns = [ButtonDesc("Generate", self.generate, 0,colspan=2),
                    ButtonDesc("Export SVG", self.exportsvg, 0,colspan=2),
                    ButtonDesc("Export colored SVG", self.exportsvgcolored, 0,colspan=2),
                    ButtonDesc("Export SVG no overlap", self.exportsvg_nooverlap, 0,colspan=2),]
     
        self.grid_scales, _ = self.__scale_layout_group("Grid Settings", self.aframe, 150, grid_sliders)
        self.gen_buttons, _ = self.__button_layout_group( "Buttons", self.aframe, 100, gen_btns)
        prlab = tk.Label(self.aframe,text="Generation progress")
        prlab.grid()

        self.genprogress = ttk.Progressbar(self.aframe,length=200,mode='determinate',variable=self.progress)
        self.genprogress.grid()
        self.plabel = tk.Label(self.aframe,text="Piece count: N/A")
        self.plabel.grid()

        self.dframe.pack(side="right")
        self.canvas.pack()
        self.pieces =[]
        self.grid = None
    
    def __button_layout_group(self, groupname, frame, length, descriptors):

        l = tk.LabelFrame(frame, text=groupname)
        l.grid(sticky='WE', padx=5, pady=5, columnspan=2)
        l.grid_columnconfigure(0,minsize=length)
        l.grid_columnconfigure(1,minsize=length)
        cur_row = 0
        groupitems = []
        for bt in descriptors:
            sc = tk.Button(l, text=bt.text,
                           textvariable=bt.textvar, command=bt.command)
            if not bt.col:
                cur_row += 1
            sc.grid(row=cur_row, column=bt.col, columnspan=bt.colspan,
                    sticky='WE', padx=5, pady=5),
            groupitems.append(sc)
        return groupitems, l

    def __scale_layout_group(self, groupname, frame, length, descriptors, command=None):
        l = tk.LabelFrame(frame, text=groupname)
        l.grid(sticky='WE', padx=5, pady=5, columnspan=2)
        cur_row = 0
        groupitems = []
        for sl in descriptors:
            sc = tk.Scale(l, length=length, label=sl.text, from_=sl.min, to=sl.max, resolution=sl.res,
                          variable=sl.var, orient=tk.HORIZONTAL, command=command if command else None)
            if not sl.col:
                cur_row += 1
            sc.grid(row=cur_row, column=sl.col, columnspan=sl.colspan)
            groupitems.append(sc)
        return groupitems, l

    def setframesize(self):
        try:
            self.width = self.ncol.get()*2*self.circlerad.get()+2*self.frame.get()
            self.height = self.nrow.get()*2*self.circlerad.get()+2*self.frame.get()
            self.canvas.delete("all")
            self.canvas.pack_forget()
            self.canvas = tk.Canvas(self.dframe, bg="white", width=self.width, height=self.height,borderwidth=0, highlightthickness=0)
            self.canvas.pack()
        except:
            pass
    def createpiece(self,npiece, minv = 20, maxv = 100):
        target_nv= random.randint(minv,maxv-minv)
        myvertices = []
        myconnections =[]
        #Choose starting vertex
        vi = random.choice(self.grid.notvisitedvertices)
        myvertices.append(vi)
        self.grid.notvisitedvertices.remove(vi)
 
        while(len(myvertices)< target_nv):
            candidate_connections = [DiagCon(v,(v[0]+i,v[1]+j)) for v in myvertices for i in [-1,1] for j in [-1,1] if ((v[0]+i,v[1]+j) in self.grid.notvisitedvertices) and not ((v[0]+i,v[1]+j) in myvertices)]
            allowed_connections = [c for c in candidate_connections if c.cell in self.grid.emptycells]
            if(not allowed_connections):
                break
            nc = random.choice(allowed_connections)
            myconnections.append(nc)
            myvertices.append(nc.p2)
            self.grid.markvertex(nc.p2,npiece)
            self.grid.notvisitedvertices.remove(nc.p2)
            self.grid.emptycells.remove(nc.cell)
    
        if myconnections:
            self.grid.markvertex(vi,npiece)
            self.pieces.append(myconnections)
            return npiece+1
        else:
            return npiece
    
    def regenerate(self):
        self.grid.reset()
        np = 1
        for p in self.pieces:
            for c in p:
                self.grid.markvertex(c.p1,np)
                if(c.p1) in self.grid.notvisitedvertices:
                    self.grid.notvisitedvertices.remove(c.p1)
                if c.p2_taken:
                    self.grid.markvertex(c.p2,np)
                    if(c.p2) in self.grid.notvisitedvertices:
                        self.grid.notvisitedvertices.remove(c.p2)
                self.grid.emptycells.remove(c.cell)
            np = np+1

    def removesmallpieces(self, minpiece=4):
        removal = [p for p in self.pieces if len(p)<minpiece]
        for p in removal:
            self.pieces.remove(p)
        self.regenerate()

    def fillholes(self):
        filledcells =[]
        for ec in self.grid.emptycells:
            if not ec in filledcells:
                vertices = ec.vertices()
                occupants = [self.grid.vertexgrid[v] for v in vertices]
                holes = [vertices[idx] for idx, val in enumerate(occupants) if val ==0]
                repetitions = [occupants.count(o) for o in occupants]
                if(holes):
                    hole = holes[0]
                    choices = [idx for idx, val in enumerate(repetitions) if val ==1 and occupants[idx] and abs(vertices[idx][0]-hole[0]) and abs(vertices[idx][1]-hole[1])]
                    if(0 < len(choices)<4):
                        choice = random.choice(choices)
                        connection = DiagCon(vertices[choice],hole)
                        self.grid.markvertex(hole,occupants[choice])
                        self.pieces[occupants[choice]-1].append(connection)
                        filledcells.append(ec)
                else: #no hole, 
                    choices = [idx for idx, val in enumerate(repetitions) if val ==1]
                    if choices:
                        choice =random.choice(choices)
                        v = vertices[choice]
                        candidate_connections = [DiagCon(v,(v[0]+i,v[1]+j),False) for i in [-1,1] for j in [-1,1] if ((v[0]+i,v[1]+j) in vertices)]
                        cchoice = candidate_connections[0]
                        self.pieces[occupants[choice]-1].append(cchoice)
                        filledcells.append(ec)

        for c in filledcells:
            self.grid.emptycells.remove(c)

    @staticmethod
    def addconnectionarcs(con, connections,arcs,rad, border,canvas= None, first = False):
        #first the transition arc from P1 to P2
        if con.quadrant == 0:
            newarc = CircleArc((con.p1[0]+1,con.p1[1]),rad,border,1,'+')
        elif con.quadrant ==1:
            newarc = CircleArc((con.p1[0],con.p1[1]-1),rad,border,2,'+')
        elif con.quadrant ==2:
            newarc = CircleArc((con.p1[0]-1,con.p1[1]),rad,border,3,'+')
        else:
            newarc = CircleArc((con.p1[0],con.p1[1]+1),rad,border,0,'+')
        arcs.append(newarc)
        if canvas:
            newarc.painttocanvas(canvas,border,"red")

        if(con.p2_taken):
            #Now go to P2, and check if there are any connections in the three remaining quadrants
            p2quads = [(con.quadrant+3) %4,(con.quadrant+4) %4,(con.quadrant+5) %4] 
            for q in p2quads:
                possiblecontaken = DiagCon.frompointquad(con.p2,q,True)
                possibleconnottaken = DiagCon.frompointquad(con.p2,q,False)
                if (possiblecontaken in connections):
                    MazeGui.addconnectionarcs(possiblecontaken,connections,arcs,rad,border,canvas)
                elif (possibleconnottaken in connections):
                    MazeGui.addconnectionarcs(possibleconnottaken,connections,arcs,rad,border,canvas)
                else:
                    newarc=CircleArc(con.p2,rad,border,q,'-')
                    arcs.append(newarc)
                    if canvas:
                        newarc.painttocanvas(canvas,border)
        else:
            newarc = CircleArc(con.p2,rad,border,(con.quadrant+2)%4,'+')
            arcs.append(newarc)
            if canvas:
                newarc.painttocanvas(canvas,border)

        #Final transition arc the transition arc from P2 to P1
        if con.quadrant == 0:
            newarc = CircleArc((con.p1[0],con.p1[1]-1),rad,border,3,'+')
        elif con.quadrant ==1:
            newarc = CircleArc((con.p1[0]-1,con.p1[1]),rad,border,0,'+')
        elif con.quadrant ==2:
            newarc = CircleArc((con.p1[0],con.p1[1]+1),rad,border,1,'+')
        else:
            newarc = CircleArc((con.p1[0]+1,con.p1[1]),rad,border,2,'+')
        arcs.append(newarc)
        if canvas:
            newarc.painttocanvas(canvas,border,"red")

        if first:
        #Check if something from P1 is missing
            p1quads = [(con.quadrant+1)%4, (con.quadrant+2)%4, (con.quadrant+3)%4]
            for q in p1quads:
                possiblecontaken = DiagCon.frompointquad(con.p1,q,True)
                possibleconnottaken = DiagCon.frompointquad(con.p1,q,False)
                if (possiblecontaken in connections):
                    MazeGui.addconnectionarcs(possiblecontaken,connections,arcs,rad,border,canvas)
                elif (possibleconnottaken in connections):
                    MazeGui.addconnectionarcs(possibleconnottaken,connections,arcs,rad,border,canvas)
                else:
                    newarc=CircleArc(con.p1,rad,border,q,'-')
                    arcs.append(newarc)
                    if canvas:
                        newarc.painttocanvas(canvas,border,"green")
      
    def generate(self):
   
        ncol = self.ncol.get()
        nrow = self.nrow.get()
        border = self.frame.get()
        cradius = self.circlerad.get()
        self.setframesize()
        self.canvas.delete('all')
        self.grid=Cellgrid(nrow,ncol)
        self.pieces =[]
        npiece =1
        nv=  ncol*nrow
        while(self.grid.notvisitedvertices):
            npiece = self.createpiece(npiece,self.minpl.get(),self.maxpl.get())
            self.progress.set(int((1-len(self.grid.notvisitedvertices)/nv)*100))
            self.aframe.update()
        self.removesmallpieces(self.minpl.get())
        for _ in range(0,self.minpl.get()):
            self.fillholes()

        #paint the thing
        borderpts =[(1,1),(1,self.height-1),(self.width-1,self.height-1),(self.width-1,1),(1,1)]
        for p1,p2 in zip(borderpts[0:-1],borderpts[1:]):
            self.canvas.create_line(p1[0],p1[1],p2[0],p2[1],fill="black",width=2)

        for p in self.pieces:
            r = random.randint(0,255)
            g = random.randint(0,255)
            b = random.randint(0,255)
            fillstring = "#{:02x}{:02x}{:02x}".format(r,g,b)

            for c in p:
                c1 = (cradius+border+2*cradius*c.p1[0],border+cradius+2*cradius*c.p1[1])
                c2 = (cradius+border+2*cradius*c.p2[0],border+cradius+2*cradius*c.p2[1])
                self.canvas.create_oval(c1[0]-cradius, c1[1]-cradius, c1[0]+cradius, c1[1]+cradius, outline=fillstring,fill=fillstring)
                if(c.p2_taken):
                    self.canvas.create_oval(c2[0]-cradius, c2[1]-cradius, c2[0]+cradius, c2[1]+cradius, outline=fillstring,fill=fillstring)
                    self.canvas.create_line(c1[0],c1[1],c2[0],c2[1],fill=fillstring,width=cradius)
                else:
                    c2n = (c2[0]-c1[0],c2[1]-c1[1])
                    scale_factor = (2*cradius)-(cradius/math.sqrt(2.0))
                    scale_factor = abs(scale_factor)/abs(c2n[0])
                    c2n = (c2n[0]*scale_factor,c2n[1]*scale_factor)
                    c2n = (c2n[0]+c1[0],c2n[1]+c1[1])
                    self.canvas.create_line(*c1,*c2n,fill=fillstring,width=cradius)

            arcs =[]
            MazeGui.addconnectionarcs(p[0],p,arcs,cradius,border,self.canvas,first=True)
        self.plabel.config(text="Piece count: "+str(int(len(self.pieces))))
    def exportsvg(self):
        border = self.frame.get()
        cradius = self.circlerad.get()
        if self.pieces:
            filename = filedialog.asksaveasfilename(title="Save SVG", filetypes=(("svg files", "*.svg"), ("all files", "*.*")))
            if filename:
                if not filename.endswith(".svg"):
                    filename += ".svg"
                dwg = svgwrite.Drawing(filename, size=(str(self.width)+'mm', str(self.height)+'mm'), viewBox=('0 0 {} {}'.format(self.width, self.height)))
                for p in self.pieces:
                    arcs =[]
                    MazeGui.addconnectionarcs(p[0],p,arcs,cradius,border,None,first=True)
                    path= svgwrite.path.Path(d=None,stroke="red", fill ="none", stroke_width="0.1")
                    move="M"+str(arcs[0].startpoint[0])+','+str(arcs[0].startpoint[1])
                    path.push(move)
                    for a in arcs:
                        path.push_arc(a.endpoint,90,cradius,large_arc=False,absolute=True,angle_dir=a.sign)
                    path.push("Z") #close path
                    dwg.add(path)
                dwg.add(dwg.polyline([(0,0),(0,self.height),(self.width,self.height),(self.width,0),(0,0)],stroke="red", fill ="none", stroke_width="0.1"))
                dwg.save()

    def exportsvgcolored(self):
        border = self.frame.get()
        cradius = self.circlerad.get()
        if self.pieces:
            filename = filedialog.asksaveasfilename(title="Save SVG", filetypes=(("svg files", "*.svg"), ("all files", "*.*")))
            if filename:
                if not filename.endswith(".svg"):
                    filename += ".svg"
                dwg = svgwrite.Drawing(filename, size=(str(self.width)+'mm', str(self.height)+'mm'), viewBox=('0 0 {} {}'.format(self.width, self.height)))
                for p in self.pieces:
                    arcs =[]
                    r = random.randint(0,255)
                    g = random.randint(0,255)
                    b = random.randint(0,255)
                    fillstring = "#{:02x}{:02x}{:02x}".format(r,g,b)
                    MazeGui.addconnectionarcs(p[0],p,arcs,cradius,border,None,first=True)
                    path= svgwrite.path.Path(d=None,stroke="black", fill =fillstring, stroke_width="1")
                    move="M"+str(arcs[0].startpoint[0])+','+str(arcs[0].startpoint[1])
                    path.push(move)
                    for a in arcs:
                        path.push_arc(a.endpoint,90,cradius,large_arc=False,absolute=True,angle_dir=a.sign)
                    path.push("Z") #close path
                    dwg.add(path)
                dwg.add(dwg.polyline([(0,0),(0,self.height),(self.width,self.height),(self.width,0),(0,0)],stroke="black", fill ="none", stroke_width="1"))
                dwg.save()

    def exportsvg_nooverlap(self):
        border = self.frame.get()
        cradius = self.circlerad.get()
        if self.pieces:
            filename = filedialog.asksaveasfilename(title="Save SVG", filetypes=(("svg files", "*.svg"), ("all files", "*.*")))
            if filename:
                if not filename.endswith(".svg"):
                    filename += ".svg"
                dwg = svgwrite.Drawing(filename, size=(str(self.width)+'mm', str(self.height)+'mm'), viewBox=('0 0 {} {}'.format(self.width, self.height)))
                allarcs = []
                for p in self.pieces:
                    inpath= False
                    arcs = []
                    MazeGui.addconnectionarcs(p[0],p,arcs,cradius,border,None,first=True)
                    for a in arcs:
                        if a in allarcs:
                            if inpath:
                                dwg.add(path)
                                inpath = False
                        else:
                            allarcs.append(a)
                            if(not inpath):
                                path= svgwrite.path.Path(d=None,stroke="red", fill ="none", stroke_width="0.1")
                                move="M"+str(a.startpoint[0])+','+str(a.startpoint[1])
                                path.push(move)
                                inpath=True
                            path.push_arc(a.endpoint,90,cradius,large_arc=False,absolute=True,angle_dir=a.sign)
                    if inpath:
                        dwg.add(path)

                dwg.add(dwg.polyline([(0,0),(0,self.height),(self.width,self.height),(self.width,0),(0,0)],stroke="red", fill ="none", stroke_width="0.1"))
                dwg.save()

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    root = tk.Tk()
    root.title("Circle Grid Puzzle Generator")
    if ( sys.platform.startswith('win')):
        root.iconbitmap(resource_path('gridicon.ico'))
    app = MazeGui(root)
    root.mainloop()


if __name__ == "__main__":
    # execute only if run as a script
    main()
