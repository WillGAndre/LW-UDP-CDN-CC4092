
use tokio::net::UdpSocket;
use std::io;

use serde_json::json;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct Client {
    externalip : String,
    region : String,
}


#[tokio::main]
async fn main()  {


    let port = match std::env::var("PORT"){
        Ok(port) => port,
        _ => String::from("8080")
    };

    let address = format!("0.0.0.0:{}", port);

    let sock = UdpSocket::bind(address.clone()).await.unwrap();
    let mut buf = [0; 1024];


    loop {
        let (len, addr) = sock.recv_from(&mut buf).await.unwrap();
        println!("{:?} bytes received from {:?}", len, addr);

        let c: Client = serde_json::from_str(&buf)?;

    }
}
