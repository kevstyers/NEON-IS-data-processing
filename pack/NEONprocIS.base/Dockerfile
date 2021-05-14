FROM rhub/r-minimal:4.0 as intermediate1

# Build arrow
RUN apk update && \
    apk add autoconf bash cmake g++ gcc make git musl-dev curl-dev linux-headers libxml2-dev openssl-dev libgit2-dev && \
    git clone https://github.com/apache/arrow.git && \
    cd arrow/cpp && \
    mkdir release && \
    cd release && \
    cmake .. -DARROW_PARQUET=ON -DARROW_WITH_SNAPPY=ON -DARROW_WITH_ZSTD=ON -DARROW_WITH_ZLIB=ON && \
    make 

FROM alexmasterov/alpine-libv8:7.0 as intermediate2

FROM rhub/r-minimal:4.0

COPY --from=intermediate1 /root/arrow/cpp/release/release/ /root/arrow/cpp/release/release/
COPY --from=intermediate2 /usr/local/v8/ /usr/local/v8/
COPY V8_3.4.2.tar.gz /
COPY ./ /pack/NEONprocIS.base/

RUN apk update && \
    apk add --no-cache bash gcc g++ musl-dev curl-dev linux-headers libxml2-dev openssl-dev libgit2-dev

RUN R -e 'utils::install.packages("devtools", repos="http://cran.us.r-project.org")' && \
    R -e 'utils::install.packages("renv", repos="http://cran.us.r-project.org")'

# Install V8
ENV LD_LIBRARY_PATH=/usr/local/v8/lib
RUN MAKEFLAGS='LDFLAGS=-L/usr/local/v8/lib -Wl,-rpath /usr/local/v8/lib'
RUN R CMD INSTALL /V8_3.4.2.tar.gz --configure-vars='INCLUDE_DIR=/usr/local/v8/include LIB_DIR=/usr/local/v8/lib' && \
    rm -rf /V8_3.4.2.tar.gz

ENV LIBARROW_BINARY=true
ENV ARROW_USE_PKG_CONFIG=false
ENV LIBARROW_MINIMAL=false
RUN R -e 'renv::consent(provided=TRUE); renv::restore("/pack/NEONprocIS.base/")' && \
    R -e 'renv::install("/pack/NEONprocIS.base")' && \
    rm -rf /pack

# Set environment variables for logging
ENV LOG_TO=stdout
ENV LOG_FORMAT=plain
ENV LOG_LEVEL=info 
