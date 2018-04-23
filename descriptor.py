import numpy as np

def compute_descriptor(V):
    """ Return a list of descriptors of the signal V """
    signal = abs(np.fft.fft(V))
    freq = np.fft.fftfreq(len(V))
    fr_max = freq[np.argmax(signal)]

    descriptors = [np.mean(V), np.std(V), np.min(V), np.max(signal)]
    descriptors.append(fr_max)

    return np.array(descriptors)