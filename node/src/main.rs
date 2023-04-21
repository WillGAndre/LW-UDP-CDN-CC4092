use gcp_auth::{AuthenticationManager, CustomServiceAccount};
use reqwest::Client;
use std::path::PathBuf;
use std::env;
use std::fs::File;
use std::io::Cursor;

use std::convert::Infallible;
use std::net::SocketAddr;

use tokio::net::UdpSocket;
use std::io;

use serde_json::json;
use serde::{Deserialize, Serialize};

static KEY: &str = "AIzaSyCQ65jgh0Xzkdg2u-ev5TZJz7CtUlqghYo";
static BUCKETNAME: &str = "bucketasc";
static ACCOUNTCREDS : &str = "accountCreds.json";

#[derive(Serialize, Deserialize)]
struct Attributes {
    externalip : String,
    region : String,
}


#[tokio::main]
async fn main()  {
    
    println!("getting node external ip and region");
    let extip = get_node_extip().await.unwrap();
    let reg = get_node_region().await.unwrap();
    println!("ip : {} Region : {}", extip, reg);

    let attributes = Attributes {
        externalip : extip,
        region : reg
    };

    //collect args
    // let _args: Vec<String> = env::args().collect();
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

        let serialized = serde_json::to_string(&attributes).unwrap();

        let len = sock.send_to(&serialized.as_bytes(), addr).await.unwrap();
        println!("MSG - {} - SENT", serialized);
    }
}



async fn get_node_extip() -> Result<String, reqwest::Error>{
    let url = "http://metadata/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip";
    let client = Client::new();
    let res = client
        .get(url)
        .header("Metadata-Flavor", "Google")
        .send().await.unwrap();
    let response = res.text().await;
    return response;
}

async fn get_node_region() -> Result<String, reqwest::Error>{
    let url = " http://metadata.google.internal/computeMetadata/v1/instance/zone";
    let client = Client::new();
    let res = client
        .get(url)
        .header("Metadata-Flavor", "Google")
        .send().await.unwrap();
    let response = res.text().await;
    return response;
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

async fn bucket_request_example() -> String{

    let token = get_token().await;
    let req = get_bucket_info(token.clone()).await.unwrap();
    let req2 = list_bucket(token.clone()).await.unwrap();
    //let req3 = get_bucket_info(token).await.unwrap();

    println!("{}", req);
    println!("{}", req2);
    //println!("{:?}", req3);
    return "asd".to_string();
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

// Lists all objects in the bucket
async fn list_bucket(token: String) -> Result<String, reqwest::Error>{
    let url = format!("https://storage.googleapis.com/storage/v1/b/{}/o?key={}", BUCKETNAME, KEY);
    let client = Client::new();
    let res = client
        .get(url)
        .bearer_auth(token)
        .send().await.unwrap();
    let response = res.text().await;
    return response;
}


//Read file from string path
// fn parse_file(path : String) -> Vec<u8>{
//     let mut bytes: Vec<u8> = Vec::new();
//     for byte in File::open(format!("{}", path)).bytes() {
//         bytes.push(byte)
//     }
//     return bytes;
// }

// // Upload a new object to the bucket
// async fn upload_bucket(file: Vec<u8>, token: String) -> Result<String, reqwest::Error>{
//     let name : String = "nameofobject";

//     //MEDIA ONLY, can be multipart
//     let upload_type : String = "media";

//     let url = format!("https://storage.googleapis.com/storage/v1/b/{}/?name={}&key={}", BUCKETNAME, name, KEY);
//     let client = Client::new();
//     let res = client
//         .post(url)
//         .bearer_auth(token)
//         .send().await.unwrap();
//     let response = res.text().await;
//     return response;
// }

// async fn download_bucket(obj_name: String, destination_path: String, token: String) -> String{
//     let mut downloaded : Vec<u8> = Vec::new();

//     let url = format!("GET https://storage.googleapis.com/storage/v1/b/{}/o/{}?key={}", BUCKETNAME, obj_name, KEY);
//     let client = Client::new();
//     let res = client
//         .post(url)
//         .bearer_auth(token)
//         .send().await.unwrap();
//     let response = res.bytes().await;
//     let mut content = Cursor::new(response);
//     let mut file = std::fs::File::create(file_name);
//     std::io::copy(&mut content, &mut file);
//     "".to_string()
// }

async fn delete_from_bucket(obj_name: String, token: String ) -> Result<String, reqwest::Error>{
    let url = format!("https://storage.googleapis.com/storage/v1/b/{}/?key={}", BUCKETNAME, KEY);
    let client = Client::new();
    let res = client
        .delete(url)
        .bearer_auth(token)
        .send().await.unwrap();
    let response = res.text().await;
    return response;
}
