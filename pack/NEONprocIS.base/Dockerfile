
FROM rhub/r-minimal:4.0 as intermediate

RUN apk update && \
    apk add autoconf bash cmake g++ gcc make git musl-dev curl-dev linux-headers libxml2-dev openssl-dev libgit2-dev && \
    git clone https://github.com/apache/arrow.git && \
    cd arrow/cpp && \
    mkdir release && \
    cd release && \
    cmake .. -DARROW_PARQUET=ON -DARROW_WITH_SNAPPY=ON -DARROW_WITH_ZSTD=ON -DARROW_WITH_ZLIB=ON && \
    make 

FROM rhub/r-minimal:4.0

COPY --from=intermediate /root/arrow/cpp/release/release/ /root/arrow/cpp/release/release/

RUN apk update \
    && apk add --no-cache bash gcc g++ musl-dev curl-dev linux-headers libxml2-dev openssl-dev libgit2-dev \
    && installr -d arrow devtools