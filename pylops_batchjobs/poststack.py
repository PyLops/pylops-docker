import os
import sys
import numpy as np
import yaml
import segyio
import pylops
import matplotlib.pyplot as plt
from subprocess import call


def main(config):
    ##############
    # Config parse
    ##############
    with open(config, 'r') as stream:
        setup = yaml.load(stream)

        remotepath = setup['data']['remotepath']
        localpath = setup['data']['localpath']
        filename = setup['data']['filename']
        account = setup['data']['account']
        container = setup['data']['container']
        token = setup['data']['token']

        itmin, itmax = setup['prep']['itmin'], setup['prep']['itmax'] #500, 900
        nt_wav = setup['prep']['nt_wav'] #41  # lenght of wavelet in samples
        nfft = setup['prep']['nfft'] #2 ** 9  # lenght of fft
        jil, jxl, jt = setup['prep']['jil'], setup['prep']['jxl'], setup['prep']['jt'] #2, 2, 2

        niter = setup['proc']['niter']


    ##############
    # Data loading
    ##############
    print(os.system('echo Downloading data...') )
    if not os.path.isfile(localpath+filename):
        command = ["az",
                   "storage", "blob", "download",
                   "--account-name", account,
                   "--container-name", container,
                   "--name",
                   remotepath+filename,
                   "--file",
                   localpath + filename,
                   "--sas-token",
                   token]
        print('Downloading...')
        call(command)

    ##############
    # Reading data
    ##############
    print(os.system('echo Reading data...') )
    f = segyio.open(localpath+filename, ignore_geometry=True)

    traces = segyio.collect(f.trace)[:]
    traces = traces[:, itmin:itmax]
    ntraces, nt = traces.shape

    ################
    # Interpret data
    ################
    print(os.system('echo Interpreting data...') )
    t = f.samples
    il = f.attributes(segyio.TraceField.INLINE_3D)[:]
    xl = f.attributes(segyio.TraceField.CROSSLINE_3D)[:]

    # Define regular IL and XL axes
    il_unique = np.unique(il)
    xl_unique = np.unique(xl)

    il_min, il_max = min(il_unique), max(il_unique)
    xl_min, xl_max = min(xl_unique), max(xl_unique)

    dt = t[1] - t[0]
    dil = min(np.unique(np.diff(il_unique)))
    dxl = min(np.unique(np.diff(xl_unique)))

    ilines = np.arange(il_min, il_max + dil, dil)
    xlines = np.arange(xl_min, xl_max + dxl, dxl)
    nil, nxl = ilines.size, xlines.size

    ilgrid, xlgrid = np.meshgrid(np.arange(nil),
                                 np.arange(nxl),
                                 indexing='ij')

    # Look-up table
    traces_indeces = np.full((nil, nxl), np.nan)
    iils = (il - il_min) // dil
    ixls = (xl - xl_min) // dxl
    traces_indeces[iils, ixls] = np.arange(ntraces)
    traces_available = np.logical_not(np.isnan(traces_indeces))

    # Reorganize traces in regular grid
    d = np.zeros((nil, nxl, nt))
    d[ilgrid.ravel()[traces_available.ravel()],
      xlgrid.ravel()[traces_available.ravel()]] = traces

    # Subsampling
    d = d[::jil, ::jxl, ::jt]
    xlines = xlines[::jxl]
    ilines = ilines[::jil]
    t = t[::jt]
    dt = t[1] - t[0]
    nil, nxl, nt = d.shape

    # Display data
    plt.figure(figsize=(7, 9))
    plt.imshow(d[nil//2].T, cmap='RdYlBu', vmin=-5, vmax=5,
               extent=(xlines[0], xlines[-1], t[-1], t[0]))
    plt.title('Seismic data - section')
    plt.colorbar()
    plt.axis('tight')
    plt.savefig(localpath+'data.png')

    ####################
    # Wavelet estimation
    ####################
    print(os.system('echo Estimate wavelet...') )
    t_wav = np.arange(nt_wav) * (dt/1000)
    t_wav = np.concatenate((np.flipud(-t_wav[1:]), t_wav), axis=0)

    # Estimate wavelet spectrum
    wav_est_fft = np.mean(np.abs(np.fft.fft(d[::2, ::2], nfft, axis=-1)), axis=(0, 1))
    fwest = np.fft.fftfreq(nfft, d=dt/1000)

    # Create wavelet in time
    wav_est = np.real(np.fft.ifft(wav_est_fft)[:nt_wav])
    wav_est = np.concatenate((np.flipud(wav_est[1:]), wav_est), axis=0)
    wav_est = wav_est / wav_est.max()

    # Display wavelet
    fig, axs = plt.subplots(1, 2, figsize=(20, 5))
    fig.suptitle('Statistical wavelet estimate')
    axs[0].plot(fwest[:nfft//2], wav_est_fft[:nfft//2], 'k')
    axs[0].set_title('Frequency')
    axs[1].plot(t_wav, wav_est, 'k')
    axs[1].set_title('Time')
    plt.savefig(localpath+'wavest.png')

    ####################
    #  Colored inversion
    ####################
    print(os.system('echo Colored inversion...') )
    d = np.swapaxes(d, -1, 0)

    m_colored, r_colored = \
        pylops.avo.poststack.PoststackInversion(d, wav_est, m0=np.zeros_like(d), explicit=True,
                                                epsI=1e-3, simultaneous=False)
    m_colored_reg, r_colored_reg = \
        pylops.avo.poststack.PoststackInversion(d, wav_est, m0=m_colored, epsI=1e-4, epsR=1e2,
                                                **dict(iter_lim=niter, show=2))
    # Swap time axis back to last dimension
    d = np.swapaxes(d, 0, -1)
    m_colored = np.swapaxes(m_colored, 0, -1)
    m_colored_reg = np.swapaxes(m_colored_reg, 0, -1)
    r_colored = np.swapaxes(r_colored, 0, -1)
    r_colored_reg = np.swapaxes(r_colored_reg, 0, -1)

    # Visualize
    fig, axs = plt.subplots(3, 1, figsize=(15, 20))
    fig.suptitle('Colored inversion - iline section',
                 y=0.91, fontweight='bold', fontsize=18)
    axs[0].imshow(d[nil//2].T, cmap='seismic', vmin=-4, vmax=4,
                  extent=(xlines[0], xlines[-1], t[-1], t[0]))
    axs[0].set_title('Seismic data')
    axs[0].axis('tight')
    axs[1].imshow(m_colored[nil//2].T, cmap='seismic',
                  vmin=-0.7*m_colored.max(), vmax=0.7*m_colored.max(),
                  extent=(xlines[0], xlines[-1], t[-1], t[0]))
    axs[1].set_title('Trace-by-Trace')
    axs[1].axis('tight')
    axs[2].imshow(m_colored_reg[nil//2].T, cmap='seismic',
                  vmin=-0.7*m_colored.max(), vmax=0.7*m_colored.max(),
                  extent=(xlines[0], xlines[-1], t[-1], t[0]))
    axs[2].set_title('Spatially regularized')
    axs[2].axis('tight')
    plt.savefig(localpath+'coloredinv.png')


if __name__ == "__main__":
    config = sys.argv[1]
    #config = 'data/config.yml'
    main(config)
