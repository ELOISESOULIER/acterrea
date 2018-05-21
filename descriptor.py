import numpy as np

def compute_descriptor(V):
    """ Return a list of descriptors of the signal V """

    descriptors = [np.mean(V), np.std(V), np.min(V), np.max(V)]

    signal = abs(np.fft.fft(V))
    freq = np.fft.fftfreq(len(V))

    fr_max = freq[np.argmax(signal)]
    descriptors.append(fr_max)
    ampl_max = np.max(signal)
    descriptors.append(ampl_max)

    return np.array(descriptors)