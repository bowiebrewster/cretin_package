import generator_object, write_run_plot, serial_sim_tools, animate, plt_file, to_generator_string
import matplotlib.pyplot as plt

from importlib import reload
for obj in [generator_object, to_generator_string, write_run_plot, serial_sim_tools, animate, plt_file]:
    reload(obj)
    
#name = 'Howard_scott36_4_2'
#hmm = write_run_plot.extra_plot(name, multiplot=True)

#rho_t_x = hmm['mass density']

rho_t_x['time_diff'] = (rho_t_x['time']-2e-9).abs()
min_diff = rho_t_x['time_diff'].min()
closest_rows = rho_t_x[rho_t_x['time_diff'] == min_diff ]
X = closest_rows['ir'].to_numpy()

Y = closest_rows['zrho'].to_numpy()
X1, Y1 = X[125:140], Y[125:140]
plt.plot(X1,Y1)