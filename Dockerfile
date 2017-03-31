FROM armhf/ubuntu

ARG OPENCV_VERISON="3.2.0"

# install dependencies
RUN apt-get update && apt-get install -y build-essential \
	cmake \
	curl \
	gfortran \
	libatlas-base-dev \
	libavcodec-dev \
	libavformat-dev \
	libgtk-3-dev \
	libjasper-dev \
	libjpeg8-dev \
	libpng12-dev \
	libswscale-dev \
	libtiff5-dev \
	libv4l-dev \
	libx264-dev \
	libxvidcore-dev \
	pkg-config \
	python \
	python2.7-dev \
	python3 \
	python3.5-dev

# install python libraries for both python2 and python3
WORKDIR /tmp

RUN curl -O https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN pip3 install numpy
RUN pip3 install imutils
RUN python get-pip.py
RUN pip install numpy
RUN pip install imutils

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
RUN mv cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so

# link OpenCV bindings into python env
WORKDIR /usr/lib/python3/dist-packages
RUN ln -s /usr/local/lib/python3.5/dist-packages/cv2.so cv2.so

# do some cleanup
RUN rm -rf /tmp/opencv-3.2.0/build

# temp spot for python libraries
RUN pip3 install awscli

# add source files
WORKDIR /root
COPY ./src/ computervision/

CMD ["bash"]
