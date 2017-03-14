FROM ubuntu:16.04

ARG OPENCV_VERISON="3.2.0"

# install dependencies
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y apt-utils
RUN apt-get install -y build-essential cmake pkg-config \
	libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev \
	libavcodec-dev libavformat-dev libswscale-dev libv4l-dev \
	libxvidcore-dev libx264-dev \
	libgtk-3-dev \
	libatlas-base-dev gfortran python python3 \
	python2.7-dev python3.5-dev curl wget

# install python libraries
WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install numpy
RUN python get-pip.py
RUN pip install numpy

# download opencv
RUN curl -sL https://github.com/Itseez/opencv/archive/$OPENCV_VERISON.tar.gz | tar xvz -C /tmp
RUN curl -sL https://github.com/Itseez/opencv_contrib/archive/$OPENCV_VERISON.tar.gz | tar xvz -C /tmp
RUN mkdir -p /tmp/opencv-3.2.0/build

WORKDIR /tmp/opencv-3.2.0/build

RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D INSTALL_C_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv_contrib-3.2.0/modules \
    -D PYTHON_EXECUTABLE=/usr/bin/python3 \
    -D BUILD_EXAMPLES=ON ..
RUN make
RUN make install

# configure
RUN ldconfig

# rename opencv output file
WORKDIR /usr/local/lib/python3.5/dist-packages
RUN mv cv2.cpython-35m-x86_64-linux-gnu.so cv2.so

# link OpenCV bindings into python env
WORKDIR /usr/lib/python3/dist-packages
RUN ln -s /usr/local/lib/python3.5/dist-packages/cv2.so cv2.so

CMD ["bash"]
