###################################################
# Dockerfile for setting up curvelops environment
# and serving it in jupyter notebook.

# Building this Dockerfile requires the source code
# for FFTW 2.1.5 and CurveLab 2.1.3 to be placed in
# the same directory.
#
# Please ensure you own a CurveLab license as per
# required by the authors. See the CurveLab website
# for more information. All CurveLab rights are
# reserved to Emmanuel Candes, Laurent Demanet,
# David Donoho and Lexing Ying.
#
# Author: Carlos Costa c.dacostaf@gmail.com
#
# Date: 17/04/2021
#
###################################################

FROM ubuntu:latest

# Install tools required for building FFTW, CurveLab and curvelops
RUN apt-get update && apt-get install -y gcc g++ python3 python3-pip wget unzip

# Install FFTW 2.1.5
COPY ./fftw-2.1.5 /opt/fftw-2.1.5
WORKDIR /opt/fftw-2.1.5/
RUN ./configure --with-pic --prefix=/opt/fftw-2.1.5
RUN make
RUN make install

# Install CurveLab 2.1.3
COPY ./CurveLab-2.1.3/ /opt/CurveLab-2.1.3/ 
WORKDIR /opt/CurveLab-2.1.3/
RUN make lib
RUN make test

# Install curvelops
WORKDIR /opt
RUN wget https://github.com/PyLops/curvelops/archive/main.zip
RUN unzip main.zip && mv curvelops-main curvelops
RUN FFTW=/opt/fftw-2.1.5 FDCT=/opt/CurveLab-2.1.3/ python3 -m pip install -e curvelops

# Remove source code
RUN rm -rf /opt/fftw-2.1.5/
RUN rm -rf /opt/CurveLab-2.1.3/

# Install useful Python packages not required by curvelops
RUN python3 -m pip install scikit-fmm matplotlib pyfftw spgl1 jupyter tqdm

# Uninstall packages
RUN apt-get remove --purge -y gcc g++ python3-pip wget unzip
RUN apt-get autoremove --purge -y

# Copy datafiles to home for jupyter user
RUN useradd -ms /bin/bash jupyter
RUN cp -r /opt/curvelops/examples /home/jupyter/
RUN cp -r /opt/curvelops/testdata /home/jupyter/ && chown -R jupyter /home/jupyter/
RUN rm -rf /opt/curvelops/examples /opt/curvelops/testdata

# Run Jupyter
USER jupyter
WORKDIR /home/jupyter
ENTRYPOINT ["jupyter", "notebook", "--ip='0.0.0.0'", "--port=5000", "--no-browser", "--allow-root"]


