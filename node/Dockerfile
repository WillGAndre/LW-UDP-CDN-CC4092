FROM rust

COPY . /app
WORKDIR /app

RUN cargo build --release 
RUN echo "-- running cmd --"

CMD ["./target/release/node"]
