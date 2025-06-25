FROM python:3.10

# Create a directory for the application
WORKDIR /app

# Install package dependencies
RUN apt-get update && apt-get install -y build-essential libboost-all-dev cmake g++ checkinstall libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev

# Install Python 2 from source
RUN wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz && tar xzf Python-2.7.18.tgz && cd Python-2.7.18 && ./configure --enable-optimizations && make install
RUN curl https://bootstrap.pypa.io/pip/2.7/get-pip.py -o get-pip.py && python2 get-pip.py && pip2 install numpy

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip3 install -r requirements.txt

# Copy the application code into the container
COPY . .

# Install the application
RUN export SETUPTOOLS_SCM_PRETEND_VERSION="1.0.0" && pip3 install -e .

# Install the merging tool
RUN ./dt4dds_benchmark/workflows/bin/tool_ngmerge/install.sh

# Install the clustering algorithms
RUN ./dt4dds_benchmark/clustering/bin/install_all.sh

# Install the codecs
RUN ./dt4dds_benchmark/codecs/bin/install_all.sh

# Fix the standard python binding
RUN ln -sf /usr/local/bin/python3 /usr/local/bin/python

# Go into data directory
RUN mkdir /data
WORKDIR /data