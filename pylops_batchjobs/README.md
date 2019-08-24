# PyLops Docker image for batch jobs
Running PyLops applications as short-lived jobs in containers can be performed using
this container and a single `config.yml` file containing application specific details.


## Using Azure containers
This container is avaiable in docker hub under the name of `mrava87/pylops:batchjobs`.

We can run it in azure following these steps.

1. Create storage space

2. Create file share in storage

```
# get details from storage for file share where input data and config files will be stored...
export AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string --resource-group $RESOURCEGROUP --name $STORAGENAME --output tsv)

# create file share
az storage share create --name $SHARENAME

STORAGE_KEY=$(az storage account keys list \
  --resource-group $RESOURCEGROUP \
  --account-name $STORAGENAME \
  --query "[0].value" \
  --output tsv)
```

3. Upload `config.yml` (and possibly the input files)
```
az storage file upload -s $SHARENAME --source local_file_path
```

and list files

```
az storage file list -s $SHARENAME -o table
```

4. Create and run container only once
```
az container create --resource-group $RESOURCEGROUP  --name $CONTAINERNAME --image $DOCKERIMAGE \
  --memory 1 --cpu 2 --restart-policy Never --secure-environment-variables VAR1=var1 VAR2=var2 \
  VAR3=var3 \
  --azure-file-volume-account-name $STORAGENAME \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name $SHARENAME \
  --azure-file-volume-mount-path path_in_container_to_mount_file_share
```


## Applications

### Poststack
Perform post-stack seismic inversion with statistical wavelet.

Create a `config.yml` file containing the following information:
```
data:
  remotepath: path in third-party storage
  account: storage account name
  container: name of container in storage account
  localpath: path in container
  filename: name of file

prep:
  itmin: start sample in time/depth axis for inversion
  itmax: end sample in time/depth axis for inversion
  nt_wav: number of samples of statistical wavelet
  nfft: number of samples of fft for statistical wavelet computation
  jil: jump in inline for data subsampling
  jxl: jump in crossline for data subsampling
  jt: jump in time/depth for data subsampling

proc:
  niter: number of iterations of inversion scheme
```

Use `docker-compose.yml` to run this container locally. On Azure, type

```
az container create  --resource-group $RESOURCEGROUP  --name $CONTAINERNAME --image mrava87/pylops:batchjobs \
  --memory 8 --cpu 4 --restart-policy Never --secure-environment-variables JOB=poststack CONFIG=data/config.yml \
  TOKEN=$TOKEN \
  --azure-file-volume-account-name $$STORAGENAME \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name $SHARENAME \
  --azure-file-volume-mount-path /home/batchjobs/data/
```

In both cases, if the input file is already present in the `localpath` of the container,
`remotepath`, `account` and `container` can be left empty. Alternatively to retrieve the file (for example from
Volve data village), you need to first add your *$TOKEN* to the ``docker-compose.yml`` file or in the az command.
Instructions on how to retrive the token can be found at https://github.com/equinor/segyio-notebooks/blob/master/notebooks/pylops/01_seismic_inversion.ipynb.

