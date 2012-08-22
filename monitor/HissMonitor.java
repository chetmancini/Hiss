package monitor;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Container;
import java.awt.Dimension;
import java.awt.Paint;
import java.awt.Stroke;
import java.util.Iterator;
import java.util.Scanner;
import java.util.HashSet;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentLinkedQueue;

import javax.swing.JFrame;

import org.apache.commons.collections15.Transformer;

import edu.uci.ics.jung.algorithms.layout.CircleLayout;
import edu.uci.ics.jung.algorithms.layout.Layout;
import edu.uci.ics.jung.graph.Graph;
import edu.uci.ics.jung.graph.UndirectedSparseMultigraph;
import edu.uci.ics.jung.graph.DirectedSparseMultigraph;
import edu.uci.ics.jung.visualization.BasicVisualizationServer;
import edu.uci.ics.jung.visualization.decorators.ToStringLabeller;

/**
 * Hiss monitor
 * Modified from code by Josh Endries
 * @author Chet Mancini
 */
public class HissMonitor {
    
    /**
     * JFrame to use
     */
    protected JFrame frame = new JFrame("Monitor");
    
    /**
     * Window size.
     */
    public static final int Width = 1000;
    public static final int Height = 800;
    public static final int LayoutUpdateDelayMillis = 500;
    
    /**
     * Map of vertices accessible by their UID.
     */
    private ConcurrentHashMap<String, Vertex> vertices = 
        new ConcurrentHashMap<String, Vertex>();

    private HashSet<String> existingEdges = new HashSet<String>();
    
    /**
     * Edges don't persist, so they live in a queue.
     */
    private ConcurrentLinkedQueue<Edge> edgeQueue = 
        new ConcurrentLinkedQueue<Edge>();
    
    /**
     * Scanner for reading in from system.in.
     */
    private Scanner scan = new Scanner(System.in);
    
    /**
     * The amount of milliseconds for which an edge appears on the graph.
     */
    public static final int EdgeDelay = 500;

    /**
     * Each edge needs a unique name.
     */
    private int edgeCounter = 0;
    private final int maxedges = 100;
    
    /**
     * Create a new monitor and start the updater threads.
     */
    public HissMonitor() {
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setVisible(true);
        Thread t = new Thread(
            new StaticLayoutUpdater(), "StaticLayoutUpdater");
        t.start();
        mainloop();
    }
    
    /**
     * Main logic.
     */
    public void mainloop(){
        while(true){
            String nextLine = scan.next();
            if (nextLine.length() == 0){
                continue;
            }

            String[] arr = nextLine.split("#");
            //New node.
            if (arr[0].equals("New")){
                Vertex toadd = new Vertex(arr[1], arr[2]);
                vertices.put(arr[2], toadd);
            // Dead node
            }else if(arr[0].equals("Dead")){
                vertices.remove(arr[1]);
            //Add a message
            }else if(arr[0].equals("Msg")){
                if(arr.length == 4){
                    String key = arr[1]+arr[2];
                    if (!existingEdges.contains(key)){
                        Edge toAdd = new Edge(
                            vertices.get(arr[1]), 
                            vertices.get(arr[2]), 
                            arr[3]);

                        edgeQueue.add(toAdd);
                        existingEdges.add(key);
                    }

                }else if(arr.length == 5){

                    Edge toAdd = new Edge(
                            vertices.get(arr[1]), 
                            vertices.get(arr[2]),
                            arr[3],
                            Float.parseFloat(arr[4]));

                    edgeQueue.add(toAdd);
                }
            // Update load by weight of vertices.
            }else if(arr[0].equals("Load")){
                if(arr.length==3){
                    String uid = arr[1];
                    int load = Integer.parseInt(arr[2]);
                    vertices.get(uid).setLoad(load);
                }
            }
        }
    }

    private String getNextEdgeName(String code){
        this.edgeCounter++;
        if (this.edgeCounter > this.maxedges){
            this.edgeCounter = 0;
        }
        return "(" + code + ") " + this.edgeCounter;
    }
    
    /**
     * Transform the given edge (by name) so that its color matches others 
     * that were generated from the same protocol.
     */
    private final Transformer<String, Paint> edgeGossipTransformer = 
        new Transformer<String, Paint>() {

        @Override
        public Paint transform(String s) {
            if (s.equals("V")) {
                return Color.BLUE;
            } else if (s.equals("AG")) {
                return Color.RED;
            } else {
                return Color.BLACK;
            }
        }
    };

    
    /**
     * Edge command transformer
     */
    private final Transformer<String, Stroke> edgeCommandTransformer = 
        new Transformer<String, Stroke>() {

        @Override
        public Stroke transform(String s) {
            //Vertex tochange = vertices.get(s);
            return new BasicStroke(1.0f);
        }
    };
    
    /**
     * Transform the given edge (based on name) so that certain commands 
     * (replication) have thicker
     * edges than normal communication for that protocol.
     */
    private final Transformer<String, Stroke> vertexStrokeTransformer = 
        new Transformer<String, Stroke>() {

        @Override
        public Stroke transform(String s) {
            Stroke bs;
            if (s.startsWith("mr")) {
                float dash[] = {10.0f};
                bs = new BasicStroke(
                    9.0f, 
                    BasicStroke.CAP_BUTT, 
                    BasicStroke.JOIN_MITER, 
                    10.0f, 
                    dash, 
                    0.0f);
            } else {
                bs = new BasicStroke(1.0f);
            }
            return bs;
        }
    };
    

    
    /**
     * Run through all the nodes and edges in the map and create 
     * graph edges and vertices for them.
     * 
     * @return The filled-in graph.
     */
    public Graph<String, String> getGraph() {
        Graph<String, String> graph = 
            new DirectedSparseMultigraph<String, String>();
        
        Iterator<String> vi = vertices.keySet().iterator();
        while (vi.hasNext()){
            graph.addVertex(vertices.get(vi.next()).getName());
        }

        while(edgeQueue.size()>0){
            Edge toAdd = edgeQueue.poll();
            graph.addEdge(
                getNextEdgeName(toAdd.getCode()), 
                toAdd.getA().getName(), 
                toAdd.getB().getName());
        }
        existingEdges.clear();
        return graph;
    }
    
    /**
     * Retrieve the "viewer" (visualization handler) for the provided graph.
     * 
     * @param graph The graph to visualize.
     * @return The viewer.
     */
    public BasicVisualizationServer<String, String> getViewer(
        Graph<String, String> graph) {

        Dimension d = new Dimension(Width, Height);
        Layout<String, String> layout = 
            new CircleLayout<String, String>(graph);
        layout.setSize(d);
        layout.initialize();
        BasicVisualizationServer<String, String> vv = 
            new BasicVisualizationServer<String, String>(layout);
        vv.setPreferredSize(d);
        vv.getRenderContext().setVertexLabelTransformer(
            new ToStringLabeller<String>());
        // vv.getRenderContext().setEdgeDrawPaintTransformer(
        //     edgeGossipTransformer);
        // vv.getRenderContext().setEdgeStrokeTransformer(
        //     edgeCommandTransformer);
        // vv.getRenderContext().setVertexStrokeTransformer(
        //     vertexStrokeTransformer);
        return vv;
    }
        
    
    /**
     * Updates the graph when it contains a static layout.
     *
     * @author Josh Endries (josh@endries.org)
     *
     */
    protected class StaticLayoutUpdater implements Runnable {
        private boolean running = false;
        
        @Override
        public void run() {
            running = true;
            while (running) {
                Graph<String, String> graph = getGraph();
                BasicVisualizationServer<String, String> vv = getViewer(graph);
		        Container content = frame.getContentPane();
                content.removeAll();
                content.add(vv);
                frame.pack();
                
                try {
                    Thread.sleep(LayoutUpdateDelayMillis);
                } catch (InterruptedException e) {
                    running = false;
                }
            }
        }
    }
    
    /**
     * Main method. Create a monitor and run it.
     */
    public static void main(String[] args){
        HissMonitor monitor = new HissMonitor();
    }

}
