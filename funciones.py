## FUNCIONES


def forward_slash(x):
    """
    transforma slash
    """
    return((x.replace("\\","/")))


######################################################################

import os
import errno


def prueba_dir(x):
    """
    chequea existencia de carpetas, sino las crea
    """
    try:
        os.makedirs(x)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
