use reqwest::Client;
use tokio::net::UdpSocket;


const port = match std::env::var("PORT"){
    Ok(port) => port,
    _ => String::from("8080")
};
static LBIP: &str = "1.1.1.1:1111";
static ADDRESS = format!("0.0.0.0:{}", port);

#[tokio::main]
async fn main()  {
    
    let extip = get_node_extip().await.unwrap();
    let reg = get_node_region().await.unwrap();
    println!("ip : {} Region : {}", extip, reg);

    let attributes = Attributes {
        externalip : extip,
        region : reg
    };


    let sock = UdpSocket::bind(address.clone()).await.unwrap();

    sendRegion(sock);

}

async fn sendRegion(UdpSocket sock) {
    let serialized = serde_json::to_string(&attributes).unwrap();

    let len = sock.send_to(&serialized.as_bytes(), LBIP).await.unwrap();
    println!("MSG - {} - SENT", serialized);
}

