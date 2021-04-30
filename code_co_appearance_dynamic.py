# Powered by Python 3.8
# To cancel the modifications performed by the script
# on the current graph, click on the undo button.
# Some useful keyboard shortcuts:
#   * Ctrl + D: comment selected lines.
#   * Ctrl + Shift + D: uncomment selected lines.
#   * Ctrl + I: indent selected lines.
#   * Ctrl + Shift + I: unindent selected lines.
#   * Ctrl + Return: run script.
#   * Ctrl + F: find selected text.
#   * Ctrl + R: replace selected text.
#   * Ctrl + Space: show auto-completion dialog.
from tulip import tlp
import tulipgui as tlpg
import pandas as pd
import time

######################
## THIS SCRIPT ONLY WORKS WELL IF THE FIRST PANEL IS A NODE-LINK DIAGRAM
##############################

def updateRenderingParameter(filterElements, graph):
    v = tlpg.tlpgui.getViewsOfGraph(graph)
    nldv = v[0]
    p = nldv.getRenderingParameters()
    p.setDisplayFilteringProperty(filterElements)
    nldv.setRenderingParameters(p)

# The updateVisualization(centerViews = True) function can be called
# during script execution to update the opened views
# The pauseScript() function can be called to pause the script execution.
# To resume the script execution, you will have to click on the
# "Run script " button.
# The runGraphScript(scriptFile, graph) function can be called to launch
# another edited script on a tlp.Graph object.
# The scriptFile parameter defines the script name to call
# (in the form [a-zA-Z0-9_]+.py)
# The main(graph) function must be defined
# to run the script on the current graph
def main(graph):
    viewColor = graph['viewColor']
    viewIcon = graph['viewIcon']
    viewLabel = graph['viewLabel']
    viewLayout = graph['viewLayout']
    viewMetric = graph['viewMetric']
    viewShape = graph['viewShape']
    viewShape.setAllNodeValue(tlp.NodeShape.Icon)
    viewLabelColor = graph['viewLabelColor']
    viewLabelColor.setAllNodeValue(255,255,255)
    viewLabelBorderColor = graph['viewLabelBorderColor']
    viewLabelBorderColor.setAllNodeValue(255,255,255)
    
    #colors from ColorBrewer site
    categories={
    '4887': {'name':'Media','color':(166,206,227) , 'icon':"fa-newspaper"},
    '8680': {'name':'Ideology','color':(31,120,180) , 'icon':"md-head-question"},
    '8681': {'name':'Movements and Historical Events','color':(178,223,138) , 'icon':"md-castle"},
    '8682': {'name':'People','color':(51,160,44) , 'icon':"md-human"},
    '8683': {'name':'Emotions','color':(251,154,153) , 'icon':"fa-smile"},
    '8684': {'name':'Institutions','color':(227,26,28) , 'icon':"md-office-building"},
    '8685': {'name':'Actions','color':(253,191,111) , 'icon':"md-facebook-workplace"},
    '8686': {'name':'Values','color':(255,127,0) , 'icon':"md-thumbs-up"},
    '8687': {'name':'Places','color':(202,178,214) , 'icon':"fa-map"},
    '8689': {'name':'Problems','color':(106,61,154) , 'icon':"fa-puzzle-piece"},
    '8690': {'name':'Political Process','color':(255,255,143) , 'icon':"md-pinwheel"},
    '8692': {'name':'Resource needs and necessities','color':(177,89,40) , 'icon':"fa-download"}
    }
    
    
    graph.clear()
    previous_g=None
    
    appearance = graph.getIntegerProperty("co-appearance")
    codeId = graph.getIntegerProperty("codeId")
    
    filterElements = graph.getBooleanProperty("hidden")
    filterElements.setAllEdgeValue(True)
    filterElements.setAllNodeValue(True)
 #   updateRenderingParameter(filterElements, graph)

    #layout algorithm parameters
    ds = tlp.getDefaultPluginParameters("FM^3 (OGDF)")
    ds['New initial placement']=False

    #####################
    threshold=5
    #####################

    posts = pd.read_csv('posts.csv', sep=',', usecols=['post_id', 'created_at'], parse_dates=['created_at'])
    posts = posts.sort_values(by="created_at", ascending=True)
    annotations = pd.read_csv('annotations.csv', sep=',', usecols=['post_id', 'code_id'])
    codes = pd.read_csv('codes.csv', sep=',', usecols=['id', 'ancestry', 'name'])
    
    updateVisualization()
    sub=1
    for i in posts.index:
        p = posts['post_id'][i]
        print("Post #"+str(p)+" created ", posts['created_at'][i])
        pcodes = annotations.query('post_id=='+str(p), inplace=False)
        if(pcodes.empty):
            print("No codes. Skipping...")
            continue
        allcodes = pcodes['code_id'].values
        print("Associated codes: ",allcodes)

        nodes=[]
        #add nodes        
        for c in allcodes:
            #print("Dealing with code #"+str(c))
            nIt = codeId.getNodesEqualTo(c)
            n = tlp.node()
            if(nIt.hasNext()): #code already in the graph
                n = nIt.next()
            else:
                n = graph.addNode()
                codesdf=codes.query('id=='+str(c), inplace=False)
                if(codesdf.empty):
                    print("WARNING: code #"+str(c)+" does not exist")
                    pauseScript()
                else:
                    viewLabel[n]=codesdf['name'].values[0]
                    #set color following the category (first ancestor)
                    if(not codesdf['ancestry'].isnull().values.any()):
                        ancestor = codesdf['ancestry'].str.split('/')
                        key = ancestor.values[0][0]
                        if key in categories:
                            viewColor[n]=categories[ancestor.values[0][0]]['color']
                            viewIcon[n]=categories[ancestor.values[0][0]]['icon']
                        else:
                            print("WARNING: ancestry #"+key+" for code #"+str(c)+" is not a category")
                codeId[n]=c
            nodes.append(n)
        #add edges
        new_elt_above_threshold=False
        for i in range(len(allcodes)):
            for j in range(i+1, len(allcodes)):
                e = graph.existEdge(nodes[i], nodes[j], False)
                if(e.isValid()):
                    appearance[e]+=1
                    if(appearance[e]==threshold): #add edge to the graph if it is not already visible
                        new_elt_above_threshold=True
                        filterElements[e]=False
                        (s, t) = graph.ends(e)
                        filterElements[s]=False
                        filterElements[t]=False
                else:
                    e=graph.addEdge(nodes[i], nodes[j])
                    appearance[e]=1
            
            
        if(new_elt_above_threshold):
      #      graph.applyLayoutAlgorithm("FM^3 (OGDF)", viewLayout, ds)
        #    updateRenderingParameter(filterElements, graph)
     #       updateVisualization()
       #     print("Displaying ", str(filterElements.numberOfNonDefaultValuatedNodes()), " nodes and ", str(filterElements.numberOfNonDefaultValuatedEdges()), " edges")
            #create a subgraph
            #revert filterElements property
            select = graph.getBooleanProperty("sel_revert")
            select.copy(filterElements)
            select.reverse()
            g = graph.addSubGraph(select, "sub #"+str(sub)+" after adding post #"+str(p))
            l = g.getLocalLayoutProperty("viewLayout")

            if(previous_g !=None):
                previous_l = previous_g.getLayoutProperty("viewLayout")
                #copy viewLayout of the previous subgraph
                for n in g.getNodes():
                    if previous_g.isElement(n):
                        l[n]=previous_l[n]
            previous_g=g
            sub_appearance = g.getLocalIntegerProperty("co-appearance")
            for e in g.getEdges():
                sub_appearance[e]=appearance[e]
            ds = tlp.getDefaultPluginParameters("GEM (Frick)")
            ds['initial layout']=l
            g.applyLayoutAlgorithm("GEM (Frick)", l, ds)
            
            sub+=1
          #  time.sleep(1)
