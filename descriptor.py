import numpy as np

def spectral_moment(V,i):
    
    fft = abs(np.fft.fft(V))
    freq = np.fft.fftfreq(len(V))
    
    sm = np.sum(fft*(freq**i))/np.sum(fft)
    
    return sm

def compute_descriptor(V):
    """ Return a list of descriptors of the signal V """

    descriptors = [np.mean(V), np.std(V), np.min(V), np.max(V)]

    signal = abs(np.fft.fft(V))
    freq = np.fft.fftfreq(len(V))

    fr_max = freq[np.argmax(signal)]
    descriptors.append(fr_max)
    ampl_max = np.max(signal)
    descriptors.append(ampl_max)
    
    mu1 = spectral_moment(V,1)
    mu2 = spectral_moment(V,2)
    mu3 = spectral_moment(V,3)
    mu4 = spectral_moment(V,4)
    
    SC = mu1 #spectral centroid
    descriptors.append(SC)
    SL = np.sqrt(mu2 - mu1**2) #spectral width
    descriptors.append(SL)
    SP = (-3*mu1**4 + 6*mu1*mu2 - 4*mu1*mu3 +mu4)/SL**4 - 3 #spectral platitude
    descriptors.append(SP)
    SA = (2*mu1**3 - 3*mu1*mu2 + mu3)/SL**3 #Spectral asymetry
    

    return np.array(descriptors)



    