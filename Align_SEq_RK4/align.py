## Field free molecular alignment
# Schrodinger Equation Implementation
# Tragically slow
# Craig Benko, 2014.07.31

# General libraries
# from pylab import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import ode
import time
from numpy.linalg import norm

# My libraries, if using ipython, restart if these are modified.
from boltzmann import Boltzmann
from pulse import pulse
from cosfun import *
from molecules import *
from const import *

# close old plots.
plt.close('all')

# start time
timer = time.time()

## tuneable parameters
molecule = 'N2'
pulse_FWHM = 100e-15 #FWHM duration of the intesity of the pulse in seconds
I = .1 #in 10**14 W cm**-2
TemperatureK = 90  #in Kelvin


##Calculated Parameters
#molecular parameters
B = B_dict[molecule]*1.98648e-23 #rotational constant in ground state in Joules
D = D_dict[molecule]*1.98648e-23 #centrifugal distorion in ground state in Joules
delta_alpha =  d_alpha_dict[molecule] #anisotropic polarizability
Jmax = Jmax_dict[molecule] #approximate max J
Temperature = k*TemperatureK/B
Jweight = Boltzmann(Temperature, 70, molecule) #Boltzmann distribution

#laser parameters
sigma = pulse_FWHM*B/hbar
E0 = 2.74*10**10*I**.5 # electric field amplitude
strength=0.5*4*np.pi*epsilon0*delta_alpha*E0**2/B #in rotational constan

## RHS of the Schrodinger Equation
def rhs(t, x, Mparm):
    dx = np.array(zeros(Jmax, dtype = 'complex'))
    Delta_omega = pulse(t, strength, sigma)
    for k in range(Jmax):
        if k == 0 or k == 1:
            dx[k] = -1j*(x[k]*(k*(k+1) - D/B*k**2*(k+1)**2 - Delta_omega) -
                Delta_omega*x[k]*c2(k,Mparm) -
                Delta_omega*x[k+2]*cp2(k,Mparm))
        elif k == Jmax - 2 or k == Jmax-1:
            dx[k] = -1j*(x[k]*(k*(k+1) - D/B*k**2*(k+1)**2 - Delta_omega) -
                Delta_omega*x[k-2]*cm2(k,Mparm) -
                Delta_omega*x[k]*c2(k,Mparm))
        else:
            dx[k] = -1j*(x[k]*(k*(k+1) - D/B*k**2*(k+1)**2 - Delta_omega) -
                Delta_omega*x[k-2]*cm2(k,Mparm) -
                Delta_omega*x[k+2]*cp2(k,Mparm) -
                Delta_omega*x[k]*c2(k,Mparm))
    return dx

def advance(t, dt, x, M):
    k1 = rhs(t,x,M)
    k2 = rhs(t+.5*dt, x+.5*dt*k1,M)
    k3 = rhs(t+.5*dt, x+.5*dt*k2,M)
    k4 = rhs(t+dt, x + dt*k3,M)
    x += dt/6*(k1+2*k2+2*k3+k4)
    return x

## Initialize
tend = 2*sigma; dt = .04*sigma;t = 0
tt = np.linspace(0,5,1000)
cos2 = np.zeros(tt.size,dtype = 'complex')
Cstor = np.zeros((Jmax,int(2*Jmax+1), Jmax), dtype = 'complex')
start = np.zeros(Jmax, dtype = 'complex')

## Integrate Schrodinger Eq. Loop over all initial wavefunctions |J,M>
for J in range(Jmax):
    print(J)
    for M in range(J+1):
        #initialize
        t = 0
        init = 0*start
        init[J] = 1
        psi = advance(0, dt, init, M)
        #integrate
        while t < tend:
            t+=dt
            psi = advance(t,dt,psi, M)

        #store
        Cstor[J,M,:] = psi/norm(psi)**.5
        Cstor[J,-M,:] = psi/norm(psi)**.5

## Expectation value, incoherent, thermal average.
for J in range(Jmax):
    for M in range(-J,J+1):
        for jj in range(Jmax-2):
            w = 4*jj+6
            phi = np.angle(Cstor[J,M,jj])-np.angle(Cstor[J,M,jj+2])
            cos2 += Jweight[J]/(2*J+1)*(abs(Cstor[J,M,jj])**2*c2(jj,M) +
                    abs(Cstor[J,M,jj])*abs(Cstor[J,M,jj+2])*cp2(jj,M)*np.cos(w*tt+phi))

## End program
elapsed = time.time() - timer
print('\n Program took ' + str(round(elapsed)) + ' s to run. \n')
print('\n' + molecule+' at '+ str(I) + ' x 10$^{14}$ W cm$^{-2}$ at ' + str(TemperatureK) + ' K\n')

#Plot result, <cos**2\theta>
plt.figure()
plt.plot(tt*hbar/B*10**12,np.real(cos2),'k-')
plt.xlabel('Time [ps]')
plt.ylabel('<cos$^2\Theta$>')
plt.title(molecule+' at '+ str(I) + ' x 10$^{14}$ W cm$^{-2}$ at ' + str(TemperatureK) + ' K')
plt.grid()
plt.ylim(0,1)
plt.show()
