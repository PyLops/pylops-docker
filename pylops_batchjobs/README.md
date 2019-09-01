# PyLops Docker image for batch jobs
Running PyLops applications as short-lived jobs in containers can be performed using
this container and a single `config.yml` file containing application specific details.

The container is set up to contain a working Python environment with PyLops and dependencies
and a set of python scripts that run different applications in the same fashion - parse a
`config.yml`, read some input file from a storage, run a pylops algorithm, save the output file back
to the storage.

Such a setup is very general and indipendent on the choosen Cloud provider. In the following we
present working solutions for different clouds and detail the currently available applications and
how the input `config.yml` should be set up by the user.

## Using Azure containers
This container is avaiable in docker hub under the name of `mrava87/pylops:batchjobs`.

To create an Azure container, run following these steps once (either in Azure command line or in your
local command line using `azure-cli`.

1. Create storage space directly in the portal

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
az container create --resource-group $RESOURCEGROUP  --name $AZCONTAINERNAME --image $DOCKERIMAGE \
  --memory 1 --cpu 2 --restart-policy Never --secure-environment-variables VAR1=var1 VAR2=var2 \
  VAR3=var3 \
  --azure-file-volume-account-name $STORAGENAME \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name $SHARENAME \
  --azure-file-volume-mount-path path_in_container_to_mount_file_share
```

Note that once the container is working you can run it as many times as you need with different config
files by repeating step 3 and by running:
```
az container start  --resource-group $RESOURCEGROUP  --name $AZCONTAINERNAME

```


## Applications

Here is a list of applications currently available in `mrava87/pylops:batchjobs` and a description
of the requirements for both input file(s) and `config.yml` file.


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
az container create  --resource-group $RESOURCEGROUP  --name pylops --image mrava87/pylops:batchjobs \
  --memory 8 --cpu 4 --restart-policy Never --secure-environment-variables JOB=poststack CONFIG=data/config.yml \
  --azure-file-volume-account-name $$STORAGENAME \
  --azure-file-volume-account-key $STORAGE_KEY \
  --azure-file-volume-share-name $SHARENAME \
  --azure-file-volume-mount-path /home/batchjobs/data/
```

In both cases, if the input file is already present in the `localpath` of the container,
`remotepath`, `account` and `container` can be left empty.

Alternatively if you want to directly retrieve the file from another storage space (for example from
Volve data village), you need to also add your *$TOKEN* to ``secure-environment-variables`` in the az command when
creating the azure container.

Instructions on how to retrive the token for the Volve data village can be found
at https://github.com/equinor/segyio-notebooks/blob/master/notebooks/pylops/01_seismic_inversion.ipynb.

