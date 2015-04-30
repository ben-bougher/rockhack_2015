import webapp2
from os.path import join, dirname
from jinja2 import Environment, FileSystemLoader

import os

import numpy as np

import json

env = Environment(loader=FileSystemLoader(join(dirname(__file__),
                                               'templates')))


def hilbert(signal):
    """
    Performs the hilbert transform of a signal
    """

    S = np.fft.fft(signal)
    w = np.fft.fftfreq(signal.size)

    sigma = -1j*np.sign(w)

    return np.fft.ifft(sigma*S)
    

def rotate_phase(signal, phi):

    return signal*np.cos(phi) + np.real(hilbert(signal))*np.sin(phi)

    
    
    
def ricker(duration, dt, f):
    """
    Also known as the mexican hat wavelet, models the function:
    A =  (1-2 \pi^2 f^2 t^2) e^{-\pi^2 f^2 t^2}

    :param duration: The length in seconds of the wavelet.
    :param dt: is the sample interval in seconds (usually 0.001,
               0.002, 0.004)
    :params f: Center frequency of the wavelet (in Hz). If a list or tuple is
               passed, the first element will be used.

    :returns: ricker wavelets with center frequency f sampled at t.
    """


    freq = np.array(f)
     
    t = np.arange(-duration/2, duration/2 , dt)

    output = np.zeros((t.size, freq.size))
        
    for i in range(freq.size):
        pi2 = (np.pi ** 2.0)
        if ( freq.size == 1 ):
            fsqr = freq ** 2.0
        else:
            fsqr =  freq[i] ** 2.0
        tsqr = t ** 2.0
        pft = pi2 * fsqr * tsqr
        A = (1 - (2 * pft)) * np.exp(-pft)
        output[:,i] = A

    if freq.size == 1: output = output.flatten()
        
    return output / np.amax(output)


class WaveletHandler(webapp2.RequestHandler):

    """
    Handler for serving wavelet data
    """
    def get(self):

        # Read the parameters out of the http request
        f = float(self.request.get("f"))
        phase = float(self.request.get("phase"))

        # hard coded timescale
        duration = 1.0
        dt = .001

        # Make the wavelet and rotate the phase if need be
        wavelet = ricker(duration, dt, f)
        if phase != 0.0:
            wavelet = rotate_phase(wavelet, phase)
            
        t = np.arange(0,wavelet.size)*dt

        # Make the data structure, convert to lists as JSON won't
        # parse np arrays
        data = {"wavelet": wavelet.tolist(),
                "t": t.tolist()}

        self.response.write(json.dumps(data))
        
        
        

class ExplorerHandler(webapp2.RequestHandler):

    """
    Generates the htmlpage
    """
    def get(self):


        params = {"phase": 0.0,
                  "f": 30.0,
                  "min_f": 1.0,
                  "max_f": 60.0}
        
        template = env.get_template("xplore.html")
        
        html = template.render(params)

        self.response.write(html)
        
        
class MainHandler(webapp2.RequestHandler):

    def get(self):
        
        template = env.get_template("main.html")
        
        html = template.render()

        self.response.write(html)
        

app  = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/explore', ExplorerHandler),
    ('/wavelet', WaveletHandler)],
    debug=True)
