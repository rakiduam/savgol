# library(reticulate)
reticulate::use_condaenv(condaenv = 'py27', conda = "/home/fanr/miniconda3/envs/py27", required = TRUE)

reticulate::use_condaenv('py27')

reticulate::repl_python()
