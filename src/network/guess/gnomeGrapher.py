#
# simple graph manipulation script
import os
import time
import javax.swing as swing
import java.awt as awt


EDGEWIDTH=0.5

def addShapes(ShapeDB):
    from java.awt.geom import GeneralPath
    from java.awt import Polygon
    import jarray

    xpoints = jarray.array((10,5,0,5),'i')
    ypoints = jarray.array((5,10,5,0),'i')
    diamond = Polygon(xpoints,ypoints,4);
    shapeDB.addShape(104,diamond)

    xpoints = jarray.array((55, 67, 109, 73, 83, 55, 27, 37, 1, 43),'i')
    ypoints = jarray.array((0, 36, 36, 54, 96, 72, 96, 54, 36, 36),'i')
    star = Polygon(xpoints,ypoints,10)
    shapeDB.addShape(105,star)
    
    triangle = GeneralPath()
    triangle.moveTo(5,0)
    triangle.lineTo(10,5)
    triangle.lineTo(0,5)
    triangle.lineTo(5,0)
    shapeDB.addShape(106,triangle)

class TimeGrapher:
    def __init__(self, g, bn="gnome_gedit.d."):
        self.edgewidth = 0.5
        self.running = 0
        self.graphFiles = [nn for nn in os.listdir(".") if nn.startswith(bn)]
        self.numFrames = len(self.graphFiles)
        print "There are %d animation frames" % (self.numFrames)
       
        self.data = range(0, self.numFrames)
        self.g = g
        self.nodedict = {}
        for tn in self.g.nodes:
            self.nodedict[tn.name] = tn
        self.personNodes = [tn for tn in g.nodes if tn.isPerson]
        self.fileNodes = [tn for tn in g.nodes if not tn.isPerson]
        self.corporateNodes = [tn for tn in self.personNodes if tn.isCommercial]
        self.corporateByCorp = {}
        
        self.showAA = 1
        self.showAF = 1
        self.showFF = 1
        
        for tn in self.corporateNodes:
            try:
                corps = tn.corporations.strip().split("-")
                for tc in corps:
                    if self.corporateByCorp.has_key(tc.strip()):
                        self.corporateByCorp[tc.strip()].append(tn)
                    else:
                        self.corporateByCorp[tc.strip()] = [tn]
            except:
                print "Weird node: %s" % (tn.name)
                    
        self.fileClasses = {}
        for tn in self.fileNodes:
            if tn.fileClass != None:
                if self.fileClasses.has_key(tn.fileClass.strip()):
                    self.fileClasses[tn.fileClass.strip()].append(tn)
                else:
                    self.fileClasses[tn.fileClass.strip()] = [tn]

        self.window = swing.JFrame("Animation Control")
        self.window.contentPane.layout = awt.BorderLayout()

        buttonPanel = swing.JPanel()
        buttonPanel.layout = swing.BoxLayout(buttonPanel, swing.BoxLayout.Y_AXIS)
        
        button = swing.JButton("Advance")
        button.actionPerformed = self.advanceAnimation
        self.slider = swing.JSlider(stateChanged=self.sliderChanged)
        self.slider.setPaintTicks(1)
        self.slider.setMajorTickSpacing(5)
        self.slider.setMinimum(0)
        self.frameLabel = swing.JLabel("Frame: XXXX")
        self.dateLabel = swing.JLabel("Date: XXXX")
        self.showingLabel = swing.JLabel("Showing: ")
        self.corpNonCorpLabel = swing.JLabel("Corp: XX / Non Corp: XX / Frac: XX")
        self.corpNonCorpEdgeLabel = swing.JLabel("Corp: XX / Non Corp: XX / Frac: XX")
        
        jp1 = swing.JPanel()
        jp2 = swing.JPanel()
        jp1.layout = awt.BorderLayout()
        jp2.layout = awt.BorderLayout()
        self.window.contentPane.add("North", jp1)
        self.window.contentPane.add("South", jp2)
        jp1.add("North", buttonPanel)
        buttonPanel.add(button)
        buttonPanel.add(self.dateLabel)
        buttonPanel.add(self.showingLabel)
        button = swing.JButton("Color Files By Class")
        button.actionPerformed = self.colorFilesByClass
        buttonPanel.add(button)
        button = swing.JButton("Hide Non Source Code")
        button.actionPerformed = self.hideNonCode
        buttonPanel.add(button)
        button = swing.JButton("Toggle Person-Person Links")
        button.actionPerformed = self.toggleAA
        buttonPanel.add(button)
        button = swing.JButton("Toggle Person-File Links")
        button.actionPerformed = self.toggleAF
        buttonPanel.add(button)
        button = swing.JButton("Toggle File-File Links")
        button.actionPerformed = self.toggleFF
        buttonPanel.add(button)
        button = swing.JButton("Shape Corporate Nodes")
        button.actionPerformed = self.shapeCorporate
        buttonPanel.add(button)
        button = swing.JButton("Center")
        button.actionPerformed = lambda x: center()
        buttonPanel.add(button)
        buttonPanel.add(self.corpNonCorpLabel)
        buttonPanel.add(self.corpNonCorpEdgeLabel)
        jp2.add("West", self.slider)
        jp2.add("East", self.frameLabel)
        self.initAnimation()
        self.window.pack()
        self.window.show()
        self.running = 1
        self.slider.setValue(0)

    def calculateCorpStats(self, arg=None):
        corp = {}
        nonCorp = {}
        corpCorpEdges = 0
        nonCorpNonCorpEdges = 0
        corpNonCorpEdges = 0
        for e in [tn for tn in self.g.edges if tn.node1.isPerson and tn.node2.isPerson and tn.node1 != tn.node2]:
            if e.node1.isCommercial:
                corp[e.node1.name] = 1
            else:
                nonCorp[e.node1.name] = 1
            if e.node2.isCommercial:
                corp[e.node2.name] = 1
            else:
                nonCorp[e.node2.name] = 1
            if e.node1.isCommercial and e.node2.isCommercial:
                corpCorpEdges = corpCorpEdges + 1
            elif not e.node1.isCommercial and not e.node2.isCommercial:
                nonCorpNonCorpEdges = nonCorpNonCorpEdges + 1
            else:
                corpNonCorpEdges = corpNonCorpEdges + 1

        try:
            frac = float(len(corp))/float(len(corp) + len(nonCorp))
        except:
            frac = 0
        
        self.corpNonCorpLabel.setText("Nodes Corp: %d / Non Corp: %d / Frac: %0.2f" % (len(corp), len(nonCorp), frac))
        self.corpNonCorpEdgeLabel.setText("Edges Corp: %d / Non Corp: %d / Inter: %d" % (corpCorpEdges, nonCorpNonCorpEdges, corpNonCorpEdges))

                
            
    def shapeCorporate(self, arg=None):
        self.corporateNodes.style = 105
        self.corporateNodes.size = 30
        
    def toggleAA(self, arg=None):
        self.showAA = not self.showAA
        self.sliderChanged(0)

    def toggleAF(self, arg=None):
        self.showAF = not self.showAF
        self.sliderChanged(0)
        
    def toggleFF(self, arg=None):
        self.showFF = not self.showFF
        self.sliderChanged(0)

    def updateShowingLabel(self):
        labelText = "Showing: "
        if self.showAA: labelText = labelText + " AA "
        if self.showAF: labelText = labelText + " AF "
        if self.showFF: labelText = labelText + " FF "
        self.showingLabel.setText(labelText)
        
    def colorFilesByClass(self, arg=None):
        colors = [orange, red, green, blue, yellow, magenta, cyan, pink, wildstrawberry, maroon, limegreen]
        kvs = self.fileClasses.keys()
        for tni in xrange(0,len(kvs)):
            self.fileClasses[kvs[tni]].color = colors[tni]
        
    def hideNonCode(self, arg=None):
        for tc in ["Compilation Helpers", "Support Files", "Translation Files", "User Interface", "Graphics", "Documentation", "UNKNOWN", "Shell Scripts"]:
            self.fileClasses[tc].visible = 0

    def initAnimation(self):
        self.slider.setMaximum(len(self.data)-1)
        self.gen = 0
        self.updateFrameLabel()

    def advanceAnimation(self,arg):
        self.advanceFrame()

    def sliderChanged(self, arg):
        if self.running == 0:
            return
        # it's probably bad to have the slider as the final arbiter of the value
        self.gen = self.slider.getValue()
        self.updateFrameLabel()
        self.drawNetwork(self.gen)
 
    def advanceFrame(self):
        self.gen = (self.gen + 1) % len(self.data)
        self.updateFrameLabel()
        self.slider.setValue(self.gen)

    def updateFrameLabel(self):
        self.frameLabel.setText("  Frame: %02d  " %(self.gen))

    def drawAllNetworks(self):
        self.g.remove(g.edges)
        edgedict = {}
        for fn in self.graphFiles:
            print "loading file: %s"
            for e in open(fn).readlines():
                if e.strip().startswith("#"):
                    continue
                connNodes, edgeWeight = [tn.strip() for tn in e.split(",")]
                src,dest = connNodes.split("-")
                if not edgedict.has_key("%s-%s" % (src, dest)):
                    # print "adding edge %s-%s" % (src, dest)
                    try:
                        edgedict["%s-%s" % (src, dest)] = g.addEdge(self.nodedict[src],self.nodedict[dest])
                    except:
                        pass
        
    def drawNetwork(self, gen):
        self.g.remove(g.edges)
        self.updateShowingLabel()
        edgedict = {}
        for e in open(self.graphFiles[gen]).readlines():
            if e.strip().startswith("#"):
                if e.strip().startswith("# StartDate: "):
                    dateString = "Date: %s" % (" ".join(e.strip().split(" ")[-2:]))
                    self.dateLabel.setText(dateString)
                continue
            connNodes, edgeWeight = [tn.strip() for tn in e.split(",")]
            src,dest = connNodes.split("-")
            if not edgedict.has_key("%s-%s" % (src, dest)):
                # print "adding edge %s-%s" % (src, dest)
                try:
                    showEdge = 0
                    if self.nodedict[src].isPerson and self.nodedict[dest].isPerson:
                        if self.showAA:
                            showEdge = 1
                    elif not self.nodedict[src].isPerson and not self.nodedict[dest].isPerson:
                        if self.showFF:
                            showEdge = 1
                    elif self.showAF:
                        showEdge = 1
                    if showEdge and self.nodedict[src].visible and self.nodedict[dest].visible:
                        edgedict["%s-%s" % (src, dest)] = g.addEdge(self.nodedict[src],self.nodedict[dest])
                        edgedict["%s-%s" % (src, dest)].width = self.edgewidth
                except:
                    pass
        self.calculateCorpStats()
        
    
    def makeMovie(self, prefix, exportPNG):
        for x in xrange(0, self.numFrames):
            self.drawNetwork(x)
            exportPNG("%s%03d.png" % (prefix, x))
            print "Frame %d of %d complete" % (x+1, self.numFrames + 1)
        # because of a bug in mplayer we need to double encode last frame
        x = self.numFrames
        exportPNG("%s%03d.png" % (prefix, x))
        print "Frame %d of %d complete" % (x+1, self.numFrames + 1)

    def animate(self):
        self.advanceFrame()
        time.sleep(10)
        
def initSystem(g):
    print "system initializing"
    personNodes = [tn for tn in g.nodes if tn.isPerson]
    fileNodes = [tn for tn in g.nodes if not tn.isPerson]

    personNodes.style = 2
    personNodes.color = red
    fileNodes.color = green
    ui.setExtendedState(Frame.MAXIMIZED_BOTH)
    print "system initialized"
    
#     # build the nodedict
#     nodedict = {}
#     for tn in g.nodes:
#         nodedict[tn.name] = tn

#         edgedict = {}
#         for fn in os.listdir("."):
#             if not fn.startswith("gnome_gedit.01"):
#                 continue
#             print "Processing file %s" % (fn)
#             for e in open(fn).readlines():
#                 if e.strip().startswith("#"):
#                     continue
#                 connNodes, edgeWeight = [tn.strip() for tn in e.split(",")]
#                 src,dest = connNodes.split("-")
#                 if not edgedict.has_key("%s-%s" % (src, dest)):
#                     # print "adding edge %s-%s" % (src, dest)
#                     try:
#                         edgedict["%s-%s" % (src, dest)] = addEdge(nodedict[src],nodedict[dest])
#                     except:
#                         pass

#         print "Done loading files"

#         print "starting layout"
#         try:
#             jSpringLayout(30)
#         except:
#             pass
#         print "layout done"
#         print "waiting 30 seconds to make sure we're done"
#         time.sleep(30)

#         print "removing edges"
#         print "saving graph"
#         exportGDF("gnome_gedit_positioned.gdf")
if __name__ == "main":
    initSystem(g)
    addShapes(shapeDB)
    print "starting time grapher"
    tg = TimeGrapher(g)


