import numpy as np
from scipy.signal import savgol_filter

np.set_printoptions( precision = 4 )

#probando crear el arreglo donde se concatenen los datos y como se ordenan
for i in range(1,10):
    
    if i % 2 == 0:
        c = (np.zeros((2,2))*i)
        pass # Even
    else:
        c = (np.ones((2,2))*i)
        pass # Odd
    
    
    b = np.array (np.reshape (c,2*2, order='C'))
    
    if i == 1:
        a = b
    else:
        a = np.column_stack((a, b))

#solo para dar ayor cantidad de datos y variables
a = np.column_stack((a, np.reshape(np.ones((2,2)), 4, order='C') ))
a = np.column_stack((a, a ))

y = savgol_filter(a, 5, 2)

print 'a'
print a

print 'y'
print y
