###################################################
# Dockerfile for setting up pylops environment and
# serving it in jupyter notebook.
#
# Author: Matteo Ravasi matteoravasi@gmail.com
#
# Date: 23/01/2019
#
###################################################
FROM ubuntu:latest

# Run a system update to get it up to speed
# Then install python3 and pip3
RUN apt-get update && apt-get install -y python3 \
    python3-pip

# Install basic dependencies
RUN pip3 install --upgrade pip
RUN pip3 install jupyter numpy scipy numba matplotlib

# Install basic dependencies
RUN pip3 install pyfftw scikit-fmm spgl1

# Install pylops
RUN pip3 install  pylops

# Create a new system user
RUN useradd -ms /bin/bash jupyter

# Change to this new user
USER jupyter

# Set the container working directory to the user home folder
WORKDIR /home/jupyter

# Start the jupyter notebook
ENTRYPOINT ["jupyter", "notebook", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root"]