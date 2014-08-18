import numpy as np
cimport numpy as np
cimport cython
from integrator import *
from laser import *
import matplotlib.pyplot as plt
from const import *
class expectation_values(integrator):
    '''
    Evaluation of thermally averaged, time-dependent expectation values.
    '''

    def cos2(self, np.ndarray[np.complex64_t, ndim = 3] Cstor, np.ndarray[np.float_t, ndim = 1, negative_indices = False] Jweight):
        # Type defs
        cdef np.ndarray[np.complex64_t, ndim = 1, negative_indices = False] cos2
        cdef np.ndarray[np.float_t, ndim = 1] tt
        cdef int J, M, jj
        cdef float w, phi
        # Init
        tt = np.linspace(0,5,1000)
        cos2 = np.zeros(tt.size,dtype = 'complex64')
        for J in range(self.Jmax):
            for M in range(-J,J+1):
                for jj in range(self.Jmax-2):
                    w = 4*jj+6
                    phi = np.angle(Cstor[J,M,jj])-np.angle(Cstor[J,M,jj+2])
                    cos2 += Jweight[J]/(2*J+1)*(abs(Cstor[J,M,jj])**2*self.c2(jj,M) +
                            abs(Cstor[J,M,jj])*abs(Cstor[J,M,jj+2])*self.cp2(jj,M)*np.cos(w*tt+phi))
        return tt, cos2

    def cos2plot(self, tt, cos2, molecule):
        plt.figure()
        plt.plot(tt*hbar/self.B*10**12,np.real(cos2),'k-')
        plt.xlabel('Time [ps]')
        plt.ylabel('<cos$^2\Theta$>')
        plt.grid()
        plt.ylim(0,1)
        plt.show()
        return 0
