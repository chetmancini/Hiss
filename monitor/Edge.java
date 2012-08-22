package monitor;

public class Edge {
	private Vertex A;
	private Vertex B;
	private String code;
	private float weight;
	
	/**
	 * Edge Constructor 
	 * @param A
	 * @param B
	 * @param code
	 * @param weight
	 */
	public Edge(Vertex A, Vertex B, String code, float weight){
		this.A = A;
		this.B = B;
		this.code = code;
		this.weight = weight;
	}
	
	/**
	 * Edge Constructor
	 * @param A
	 * @param B
	 * @param code
	 */
	public Edge(Vertex A, Vertex B, String code){
		this.A = A;
		this.B = B;
		this.code = code;
		this.weight = 1.0f;
	}
	
	/**
	 * Edge Constructor
	 * @param A
	 * @param B
	 */
	public Edge(Vertex A, Vertex B){
		this.A = A;
		this.B = B;
	}
	
	/**
	 * Get A Vertex (Sender)
	 * @return
	 */
	public Vertex getA(){
		return this.A;
	}
	
	/**
	 * Get B Vertex (receiver)
	 * @return
	 */
	public Vertex getB(){
		return this.B;
	}
	
	/**
	 * Get the code for this edge.
	 */
	public String getCode(){
		return this.code;
	}
	
	/**
	 * Get weight
	 * @return
	 */
	public float getWeight(){
		return this.weight;
	}
}
