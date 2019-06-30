###################################################
# Dockerfile for setting up pylops environment and
# running poststack inversion it in batch job mode
#
# Author: Matteo Ravasi matteoravasi@gmail.com
#
# Date: 11/06/2019
#
###################################################
FROM ubuntu:latest

# Run a system update to get it up to speed
# Then install python3 and pip3
RUN apt-get update && apt-get install -y python3 \
    python3-pip

# Install basic dependencies
RUN pip3 install --upgrade pip
RUN pip3 install numpy scipy numba matplotlib azure-cli

# Install basic dependencies
RUN pip3 install pyfftw scikit-fmm spgl1 pyyaml

# Install pylops
RUN pip3 install pylops segyio

# Create a new system user
RUN useradd -ms /bin/bash batchjobs

# Link python and pip for azure-cli to work
RUN ln -s /usr/bin/python3 /usr/bin/python & \
    ln -s /usr/bin/pip3 /usr/bin/pip

# Change to this new user
USER batchjobs

# Set the container working directory to the user home folder
WORKDIR /home/batchjobs

# Copy all python jobs in working directory
COPY poststack.py /home/batchjobs

# Set env variable
ENV JOB=$JOB
ENV CONFIG=$CONFIG

# Start script
CMD python3 ${JOB}.py ${CONFIG}