import generator_object, write_run_plot, serial_sim_tools, animate, plt_file, to_generator_string


from importlib import reload
for obj in [generator_object, to_generator_string, write_run_plot, serial_sim_tools, animate, plt_file]:
    reload(obj)

def spectrum_tin(n, l, T):

    gen = generator_object.User_input()
    
    rho, T_ev = 1, T
    z = 12. #
    N0, N1 = 1, 1  # We are operating in 1d wih 500 nodes
    Rmin, Rmax = 0, 30.e-4 #node min max max = 10^-6m = 30 micron 


    gen.materials_atom(index = 1, element = "sn")
    gen.materials_atom_isorange('all', n_max = n, lmax = l)
    gen.materials_atom_modeltype(['dca'])
    gen.materials_region([N0,N1], elec_temp = T_ev)
    gen.materials_region_rho(rho)
    gen.materials_region_element(initial_ion_population = 1.0, index = 1)

    gen.geometry(type='slab')
    gen.geometry_nodes(coordinate = "r", scaling_type = "lin", nodes = [1, 1], nodes_range = [Rmin, Rmax])

    gen.radiation_ebins(n_boundaries = 201, start = 0.01, end = 2*10**(3))
    gen.radiation_angles(n_rays = 3)

    gen.controls(t_start = 0., t_end = 0., restart = True)

    gen.popular_switches(continuum_transfer_evolves_temp = True,
                         mesh_treatment = 'staggered centering (node + zones)')
    gen.other_switches(control_calc_thermal_conduct = 'include thermal conduction', 
                       population_calculation = "time dependent diffusion", 
                       temperature_calculation = 'use electronic heating rates for time-dependent')
    
    gen.sources_rswitch(radiation_transfer_algorithm1d= 'do transport using integral formalism', assume_NLTE= True)


    gen.add_plot(title='ocupation density for specified element', xvars={'iso':[1]}, 
        yvars={'yisofrac':[1,1]})  
    gen.add_plot(title='EMISSIO',xvars={'energy': []},  # No specific values given, so leaving it empty
        yvars={'cemis': [0, 1]})
    gen.add_plot(title='ABSORPTION',xvars={'energy': []},  # No specific values given, so leaving it empty
        yvars={'ckappa': [0, 1]})
    gen.add_plot(title='photon energies emmision',xvars={'ebins': []},  # No specific values given, so leaving it empty
        yvars={'cemis': [0, 1]})
    gen.add_plot(title='photon energies absorbtion',xvars={'ebins': []},  # No specific values given, so leaving it empty
        yvars={'ckappa': [0, 1] })

    return gen



def temp_loop(n, l):
    trials = []
    name = 'spectral_tin'
    N, M = 4, 1 # this is the multiplot group size and number of groups

    for i in range(M*N):
        
        name_i = name+str(i)
        #remove(name_i)
        trials.append(name_i)
        tev = 0.01*2**i
        #gen2 = spectrum_tin(n, l, tev)

        #write_run_plot.write(name = name_i, object = gen2, longprint=False, plot_duplicates=False)
        #write_run_plot.run(name = name_i, object = gen2, longprint=False, plot_duplicates=False)
        #write_run_plot.extra_plot(name = name_i)

        if (i>0 and i%N == 0):
            serial_sim_tools.plot_all(f'trials_mutiplot{int(i/N)}', trials)
            trials = []

        elif i == M*N -1:
            global bs
            bs = serial_sim_tools.plot_all(f'trials_mutiplot{int(i/N)+1}', trials)

temp_loop(4,2)
