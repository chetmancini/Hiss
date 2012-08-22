package monitor;

/**
 * Vertex
 */
public class Vertex {

	private String name;
	private String uid;
	private String type;
	private float load;
	
	/**
	 * Constructor.
	 * @param name
	 * @param uid
	 */
	public Vertex(String name, String uid){
		this.name = name;
		this.uid = uid;
		this.load = 1.0f;
	}
	
	/**
	 * Get name
	 * @return
	 */
	public String getName(){
		return this.name;
	}
	
	/**
	 * Get uid.
	 * @return
	 */
	public String getUid(){
		return this.uid;
	}
	
	/**
	 * Gettype
	 * @return
	 */
	public String getType(){
		return this.type;
	}
	
	/**
	 * Get load.
	 * @return
	 */
	public float getLoad(){
		return this.load;
	}
	
	/**
	 * Set load.
	 * @param load
	 */
	public void setLoad(float load){
		this.load = load;
	}
}
