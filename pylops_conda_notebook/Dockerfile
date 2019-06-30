###################################################
# Dockerfile for setting up pylops conda environment and
# serving it in jupyter notebook.
#
# Author: Matteo Ravasi matteoravasi@gmail.com
#
# Date: 27/05/2019
#
###################################################
FROM continuumio/miniconda3

# Create conda environment
ADD environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

# Pull the environment name out of the environment.yml
#RUN echo "source activate $(head -1 /tmp/environment.yml | cut -d' ' -f2)" > ~/.bashrc
#ENV PATH /opt/conda/envs/$(head -1 /tmp/environment.yml | cut -d' ' -f2)/bin:$PATH

# Add environment to the path
ENV PATH /opt/conda/envs/pylops/bin:$PATH

# Activate environment
RUN /bin/bash -c "source activate pylops"

# Set the container working directory to the user home folder
WORKDIR /home/jupyter

# Start the jupyter notebook
ENTRYPOINT ["jupyter", "notebook", "--ip='0.0.0.0'", "--port=8888", "--no-browser", "--allow-root"]