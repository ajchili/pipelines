from numpy import cos, linspace
from bokeh.plotting import figure
from bokeh.io import output_notebook, show

output_notebook()

x = linspace(-12, 12, 400)
y = cos(x)

p = figure(width=500, height=500)
p.circle(x, y, size=7, color="firebrick", alpha=0.5)
show(p)
