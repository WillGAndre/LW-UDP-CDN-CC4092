use gcp_auth::{AuthenticationManager, CustomServiceAccount};
use reqwest::Client;
use std::path::PathBuf;
use std::env;

use std::convert::Infallible;
use std::net::SocketAddr;
use hyper::{Body, Request, Response, Server};
use hyper::service::{make_service_fn, service_fn};

use tokio::net::UdpSocket;
use std::io;

static KEY: &str = "AIzaSyCQ65jgh0Xzkdg2u-ev5TZJz7CtUlqghYo";
static BUCKETNAME: &str = "bucketasc";
static ACCOUNTCREDS : &str = "accountCreds.json";


async fn handle(_req: Request<Body>) -> Result<Response<Body>, Infallible> {
    println!("{:?}", _req);


    let token = get_token().await;
    let req = get_bucket_info(token).await;

    Ok(Response::new(Body::from(req.unwrap())))
}


#[tokio::main]
async fn main()  {
    //collect args
    let _args: Vec<String> = env::args().collect();
    //dbg!(args);

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

        let len = sock.send_to(&buf[..len], addr).await.unwrap();
        println!("{:?} bytes sent", len);
    }


}

async fn get_token() -> String {

    let credentials_path = PathBuf::from(ACCOUNTCREDS);
    let service_account = CustomServiceAccount::from_file(credentials_path).unwrap();
    let authentication_manager = AuthenticationManager::from(service_account);
    let scopes = &["https://www.googleapis.com/auth/cloud-platform"];
    let token = authentication_manager.get_token(scopes).await.unwrap();
    //print token 
    //println!("{:?}", token.as_str());
    return String::from(token.as_str());
}


async fn get_bucket_info(token: String) -> Result<String, reqwest::Error>{
    let url = format!("https://storage.googleapis.com/storage/v1/b/{}/?key={}", BUCKETNAME, KEY);
    let client = Client::new();
    let res = client
        .get(url)
        .bearer_auth(token)
        .send().await.unwrap();
    let response = res.text().await;
    return response;

}