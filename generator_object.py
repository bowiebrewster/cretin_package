
import pandas as pd
import paths, json
from drop_methods_module import DropMethods
#this is a casual 1600 line python file what about it


class User_input():
    def __init__(self):
        # materials
        self.atoms = []
        self.regions = []

        # sources 
        self.sources = []
        self.sources_aprd = []

        # plots
        self.plots = []

        # histories 
        self.source_histories = []

        # laser
        self.lasers = []

        self.drop = DropMethods()

#################################################################################################################################################

    # materials
    def materials_atom(self, element : str, quantum_n_max : int = 10, iso_min : int = None, iso_max : int= None, index : int = None):
        element_input_requirement(element)

        self.modeltype_of_atom =[]
        self.atom0 = [element, quantum_n_max, iso_min, iso_max]
        self.atoms.append((self.atom0, self.modeltype_of_atom))

    def materials_atom_modeltype(self, type1 : str, type2 : str):
        string_input_requirement(type1, ['fly','term','dca','radonly','sublevel','johnson'])
        string_input_requirement(type2, ['fly','term','dca','radonly','sublevel','johnson'])
        self.modeltype_of_atom.append([type1, type2])

    def materials_region(self, nodes :list, elec_temp : float, ion_temp : float = None, rad_temp : float = None, qstart : bool = False):
        if ion_temp == None:
            ion_temp = elec_temp
        if rad_temp == None:
            rad_temp = elec_temp

        interger_input_requirement(len(nodes), [2,4,6])
        self.dimension = int(len(nodes)/2)
        
        self.elements_of_region, self.material_of_region, self.rho_of_region= [], [], []
        self.background_of_region, self.opacity_of_region, self.level_of_region  = [], [], []
        self.qstart = qstart
        

        # this works retroactively, I put the material_of_region list inside the self.region, if i later change 
        # the list it gets changed while its in the self.region
        self.region0 = [self.dimension, nodes, elec_temp, ion_temp, rad_temp]
        self.regions.append((self.region0, self.elements_of_region, self.material_of_region, self.rho_of_region, self.background_of_region, self.qstart))

    def materials_region_rho(self, rho : float):
        self.rho_of_region.append(rho)

    def materials_region_element(self,  initial_ion_population : float, index : int = None, isoelectric_sequence : list = None,
                                  use_lte:bool = False, electron_temp : float = None, ion_temp :float = None, ion_velocities :float = None):
        self.elements_of_region.append([index, initial_ion_population, isoelectric_sequence, use_lte, electron_temp, ion_temp, ion_velocities])

    def materials_region_material(self, rho : float, atom_n : float, charge_avg : float, charge_avg_squared: float):
        self.material_of_region.append([rho, atom_n, charge_avg, charge_avg_squared])

    def materials_region_background(self, ion_density: float, electron_density: float, avg_atomic_number : float,
                                     average_charge: float, average_charge_squared : float):
        self.background_of_region.append([ion_density, electron_density, avg_atomic_number, average_charge, average_charge_squared])

    def materials_region_opacity(self, form : str , p_vals : list, e_vals : list):
        # see page 26 of documentation for exact fomulas corresponding to forms
        string_input_requirement(form, ['constant', 'power-law','exponential','gaussian','cutoff'])
        self.opacity_of_region.append([form, p_vals, e_vals])

    def materials_region_level(self, index : int, isoelectronic_sequence : int, level : int, iso_range : list = None):
        list_input_requirement([iso_range])
        self.level_of_region.append([index, isoelectronic_sequence, level, iso_range])

    def geometry(self, type : str = 'plane'):
        string_input_requirement(type, ['none', 'plane', 'slab', 'cylinder', 'sphere', 'wedge', 'xy', 'rz', 'xyz'])
        if type == 'none' and self.dimension != 0:
            raise Exception("if type is none dimension should equal zero")
        elif type in ['plane','slab','cylinder','sphere','wedge'] and self.dimension != 1:
            raise Exception(f"if type is {type} dimension should equal 1")
        elif type in ['xy','rz'] and self.dimension != 2:
            raise Exception(f"if type is {type} dimension should equal 2")
        elif type == 'xyz' and self.dimension != 3:
            raise Exception(f"if type is {type} dimension should equal 3")
        self.geometry0 = type


    def geometry_nodes(self, coordinate : str, scaling_type: str, nodes : list, nodes_range : list, ratio : float = None, drmin : float = None, slope : float = None):
        if type(self.geometry) == type(''):
            raise Exception(f'geometry setting {self.geometry} makes nodes call obsolete')
        
        string_input_requirement(coordinate, ['r','x','y','x'])
        if coordinate == 'r' and self.dimension != 1:
            raise Exception("coordinate r is only compatible with 1d")

        string_input_requirement(scaling_type, ['lin','log','geom','exp'])
        self.geom_nodes = [coordinate, scaling_type, nodes, nodes_range, ratio, drmin, slope]

    def geometry_quad(self, node_1 : list, node_2: list, x_cors : list, y_cors :list, ratios: list):
        list_input_requirement([node_1, node_2, x_cors, y_cors, ratios])
        self.geom_quad = [node_1, node_2, x_cors, y_cors]

    def geometry_product_mesh(self, product_mesh: bool = False):
        self.prod_mesh = product_mesh

    def radiation_ebins(self, n_boundaries: int, start: float, end : float, ratio : float = None):
        self.rad_ebins  = [n_boundaries, start, end, ratio]

    def radiation_angles(self, n_rays : int, n_angles : int = None):
        self.rad_angles = [n_rays, n_angles]

    def radiation_line(self, index : int, model : int, lower_state : list, higher_state : list):
        self.rad_line = [index, model, lower_state, higher_state]
        self.rad_lbins = []

    def radiation_lbins(self, n_bins : int, energy_span_1 : float, ratio_width1: float, energy_span_2 : float = None, ratio_width2: float = None):
        self.rad_lbins.append([n_bins, energy_span_1, ratio_width1, energy_span_2, ratio_width2])

    def radiation_spectrum(self, n_energies : int, energy_range : list, ratio : float):
        self.rad_spectrum = [n_energies, energy_range, ratio]

    def radiation_aprd(self, voigt_parameters : list):
        self.sources_aprd.append(voigt_parameters)
    
    def sources_boundary(self, package: str, type : str, nodes : list, value : float , mult : float = None):
        string_input_requirement(package, ['radiation', 'conduction', 'hydro', 'velocity', 'pressure', 'divertor', 'current','all'])
        string_input_requirement(type, ['streaming', 'milne','value'])
        if len(nodes) not in [1,4,6]:
            raise Exception(""" the only allowed combinations are as follows:
            1) boundary package type [ir] (history id) multiplier value or
            2) boundary package type [k1 k2 l1 l2] (history id) value or
            3) boundary package type [k1 k2 l1 l2 m1 m2] (history id) value
            """)

        self.source_bound = [package, type, nodes, mult, value]

    def sources_source_laser(self, laser_wavelength : float, option_1 : str, option_2 : str, values : list, nodes : list):
        string_input_requirement(option_1, ['value', 'rate', 'integral', 'initial'])
        string_input_requirement(option_2, ['xfile', 'history', 'profile', 'svlist','constant'])
        
        self.sources.append(["laser", laser_wavelength, option_1, option_2, values, nodes])
    
    def sources_source_jbndry(self, index : int, E_range : list, option_1 : str, option_2 : str, values : list, nodes : list = None):
        string_input_requirement(option_1, ['value', 'rate', 'integral', 'initial'])
        string_input_requirement(option_2, ['xfile', 'history', 'profile', 'svlist','constant'])

        
        self.sources.append(['jbndry', index, E_range, option_1, option_2, values, nodes])

    def sources_source_jnu(self, E_range : list, option_1 : str, option_2 : str, values : list, nodes : list):
        string_input_requirement(option_1, ['value', 'rate', 'integral', 'initial'])
        string_input_requirement(option_2, ['xfile', 'history', 'profile', 'svlist','constant'])

        
        self.sources.append(['jnu', E_range, option_1, option_2, values, nodes])

    def sources_laser(self, index, laser_wavelength : float, option_1 : str, option_2:str, multiplier : float, id_value:float ,polarization_fraction: float = None):
        string_input_requirement(option_1, ['value', 'rate', 'integral', 'initial'])
        string_input_requirement(option_2, ['xfile', 'history', 'profile', 'svlist','constant'])
        self.lasray_lis = []
        self.lasers.append([index, laser_wavelength, option_1, option_2, multiplier, id_value, polarization_fraction, self.lasray_lis])

    def sources_lasray(self, entrance_position:float, entrance_direction_mu:float, entrance_direction_phi:float, fractional_power:float, res_frac:float = None):
        if not hasattr(self, 'lasray_lis'):
            raise Exception('lasray command must be added after laser command')
        else:
            self.lasray_lis.append([entrance_position, entrance_direction_mu, entrance_direction_phi, fractional_power, res_frac])


    def sources_history(self, id: int, value_multiplier : float = None, time_multiplier : float = None, pulse_type : str = None, p1 : float = None, p2 : float = None):

        if (not recursive_search(self.sources, 'history')) and (not recursive_search(self.lasers, 'history')):
            raise Exception('history command must bec attached to some earlier history input inside f.e source laser command')
        data = [id, value_multiplier, time_multiplier, pulse_type,p1, p2]
        self.source_histories.append(data)

    def sources_rswitch(self, c_is_inf : bool = None, assume_NLTE : bool = None, radiation_transfer_algorithm1d : str = None, 
                       radiation_transfer_algorithm2d : str = None, max_iter_intensities_temp : int = None, 
                       multi_group_acceleration : str = None, use_flux_limiting : bool = None):
        string0 = 'rswitch 5 0' if c_is_inf == True else None
        string1 = 'rswitch 20 1' if assume_NLTE == True else None
        rad_1d_dict = {'do flux-limited diffusion':.5,'do transport using Feautrier formalism':-1,'do transport using integral formalism':-2}
        rad_2d_dict = {'use iccg':1, 'use ilur':2}

        if radiation_transfer_algorithm1d != None and radiation_transfer_algorithm2d != None:
            raise Exception("Dimensionality incompatible")
        elif radiation_transfer_algorithm1d == None and radiation_transfer_algorithm2d == None:
            string2 = None
        elif radiation_transfer_algorithm1d != None and radiation_transfer_algorithm2d == None:
            string_input_requirement(radiation_transfer_algorithm1d, rad_1d_dict.keys())
            string2 = rad_1d_dict[radiation_transfer_algorithm1d]
        elif radiation_transfer_algorithm1d == None and radiation_transfer_algorithm2d != None:
            string_input_requirement(radiation_transfer_algorithm2d, rad_2d_dict.keys())
            string2 = rad_2d_dict[radiation_transfer_algorithm2d]
        else:
            raise Exception('Error in source rswitch radiation_transfer_algorithm1')
        
        string2 = 'rswitch 1 ' + str(string2) if string2 != None else None
        string3 = 'rswitch 3 ' + str(max_iter_intensities_temp) if max_iter_intensities_temp != None else None
        multi_group_acceleration_dict = {'no acceleration (or direct solution for 1 group)':0,'grey acceleration':1,
                                         'direct multigroup acceleratio':2,'direct solution (1-d only)':3,'diagonal ALI multigroup acceleration (1-d only)':4}

        if multi_group_acceleration == None:
            string4 = None
        else:
            string_input_requirement(multi_group_acceleration, multi_group_acceleration_dict.keys())
            string4 =  'rswitch 4 ' + str(multi_group_acceleration_dict[multi_group_acceleration])
                    
        string5 = 'rswitch 6 1' if use_flux_limiting == True else None

        self.source_rswitch0 = [value for key, value in locals().items() if 'string' in key]

    def controls(self, t_start : float, t_end : float, restart : bool = False, edits : bool = False):
        self.control = [t_start, t_end, restart, edits]

    def controls_history(self, id : int, value_mutiplier : float, time_multiplier, type : list = None):
        self.controls_hist = [id, value_mutiplier, time_multiplier, type]
        self.tv = []

    def controls_history_tv(self, time : float, value : float):
        self.tv.append([time, value])

    def popular_switches(
    self,
    include_degeneracy=None,
    timestep_type=None,
    continuum_transfer=None,
    continuum_transfer_evolves_temp=False,
    timestep_between_snapshot=None,
    kinematics=None,
    initialization_control=None,
    continuum_lowering_control=None,
    raytrace=None,
    temparture_calc_heating_rates=None,
    max_iterations_per_timestep=None):
        
        switch_mappings = {
        (151, "include_degeneracy"): {
            "no degeneracy": 0,
            "include electron degeneracy": 0.5,
            "ignore additional correction for ionizations": -0.5,
            "integrate collisional ionizations numerically": 1.5,
            "integrate collisional excitations numerically": 2.5,
        },
        (29, "timestep_type"): {
            "use constant timesteps": -1,
            "use_dynamic_timesteps": 1,
        },
        (36, "continuum_transfer"): {
            "do steady-state continuum transfer": 0.5,
            "do time-dependent continuum transfer": -0.5,
            "do steady-state and use Feautrier formalism": 1,
            "do steady-state and use integral formalism formalism": 2,
        },
        (25, "kinematics"): {
            "steady-state kinetics": 0,
            "time-dependent kinetics": 0.5,
            "use approx. LTE and QSS distributions to choose LTE or NLTE": 1.5,
            "calculate approx. LTE and QSS distribution": -1,
            "no kinetics": -1.5,
        },
        (28, "initialization_control"): {
            "LTE at fixed electron density": -1,
            "LTE at fixed ion density": 0,
            "steady-state w/ radiation transfer": 1,
            "steady-state kinetics w/o radiation transfer": 2,
            "no kinetics, broadcast boundary radiation": 3,
            "none": 4,
        },
        (55, "continuum_lowering_control"): {
            "approximate accounting for missing Rydberg levels": -1,
            "no continuum lowering": 0,
            "Stewart-Pyatt with formula for degeneracy lowering": 1,
            "Stewart-Pyatt with microfield degeneracy lowering": 2,
            "microfield degeneracy lowering w/o continuum lowering": 3,
            "SP/EK w/o degeneracy lowering": 5,
            "use maximum of SP/EK and approximate accounting": 10,}
        }

        switch_strings = switch_loop(switch_mappings, locals())
        
        if continuum_transfer_evolves_temp:
            switch_strings.append("switch 100 1")
        
        if timestep_between_snapshot is not None:
            switch_strings.append(f"switch 30 {timestep_between_snapshot}")

        if raytrace:
            switch_strings.append("switch 45 1")

        if temparture_calc_heating_rates is not None:
            temp1, heat1 = temparture_calc_heating_rates
            temp_calc_dict = {"temp calc = none": 0, "temp calc = time dependant": 1, "temp calc = steady state": -1}
            heating_type_dict = {
                "heating rates = electronic": 1,
                "heating rate uses internal energy rates": 2,
                "heating rate uses interal energy deltas": 3,
            }
            temp_calc_value = temp_calc_dict.get(temp1, None)
            heat_value = heating_type_dict.get(heat1, None)
            if temp_calc_value is not None and heat_value is not None:
                switch_strings.append(f"switch 31 {temp_calc_value * heat_value}")

        if max_iterations_per_timestep is not None:
            switch_strings.append(f"switch 44 {max_iterations_per_timestep}")

        self.pop_switches = switch_strings


    def other_switches(
        self,
        population_calculation=None,
        subcycle_maximum=None,
        do_kinetics_zone_centered=None,
        resonant_absorption_fraction=None,
        control_calc_thermal_conduct=None,
        population_control=None):
        
        switch_mappings = {
            (2,"population_calculation"): {
                "assuming steady state diffusion": 0,
                "time dependent diffusion": 1,
            },
            (47,"resonant_absorption_fraction"): {
                "constant value for each ray from lasray": 0,
                "Ginzburg formula": 1,
                "Ginzburg formula + smooth resonant absorption over neighboring zones": -1,
                "tabulated values": 0.5,
                "tabulated values + smooth resonant absorption over neighboring zones": -0.5,
            },
            (49,"control_calc_thermal_conduct"): {
                "no thermal conduction": 0,
                "include thermal conduction": 1,
                "use iccg": 2,
                "use ilur": 3,
                "use gmres with diagonal preconditioning": 4,
                "use gmres with iccg preconditioning": 5,
                "use gmres with ilur preconditioning": 6,
                "use gmres with no preconditioning": 7,
            },
            (20,"population_control"): {
                "Calculate LTE populations": 0,
                "Calculate NLTE populations (fixed electron density)": -1,
                "Calculate NLTE populations (fixed ion densities)": 1,
                "Calculate NLTE populations using rate matrices (intensities from continuum transfer)": 1,
                "Calculate NLTE populations using rate matrices (intensities from xfile)": 1,
                "Calculate NLTE populations using rate matrices (zero intensities)": 1,
                "Calculate NLTE populations using Planckian intensities (Te with multiplier)": 2,
                "Calculate NLTE populations using Planckian intensities (Tr with multiplier)": 3,
            },
        }

        switch_strings = switch_loop(switch_mappings, locals())

        if subcycle_maximum is not None:
            switch_strings.append(f"switch 3 {subcycle_maximum}")

        if do_kinetics_zone_centered is not None:
            switch_strings.append(f"switch 10 {int(do_kinetics_zone_centered)}")

        self.ot_switches = switch_strings

    def parameters(
        self,
        scattering_multiplier=None,
        initial_timestep=None,
        minimum_timestep=None,
        maximum_timestep=None,
        time_between_snapshots=None
    ):
            param_mappings = {
                "scattering_multiplier": ("param 5", scattering_multiplier),
                "initial_timestep": ("param 41", initial_timestep),
                "minimum_timestep": ("param 44", minimum_timestep),
                "maximum_timestep": ("param 45", maximum_timestep),
                "time_between_snapshots": ("param 40", time_between_snapshots),
            }

            param_strings = []

            for arg_name, (param_name, arg_value) in param_mappings.items():
                if arg_value is not None:
                    param_strings.append(f"{param_name} {arg_value}")

            self.pop_parameters = param_strings
           


    def add_plot(self, title:str, xvars, yvars):
        types = [type({}), type([])]
        if not type(title)== type('') or not type(xvars) in types or not type(yvars) in types:
            raise Exception('title is type string and vars are type list or type dict')
        xvars, yvars = make_dict(xvars), make_dict(yvars)

        all_xvars = 'cycle,iter,time,ir,r,cdens,x2d,y2d,z2d,x3d,y3d,z3d,xy,k,kx,ky,kz,kr,l,lx,ly,lz,lr,m,mx,my,mz,mr,ifr,energy,freq,wvl,ebins,fbins,wbins,ifrline,evline,isp,sp_energy,sp_freq,sp_nu,sp_wvl,ie,iso,level,elev'.split(',')
        if len(xvars) not in [1,2]:
            raise Exception('plot functionality only supported for 1 (regular plot) or 2 (heatplot) x variables')
        
        with open(f"{paths.to_folder_cretin()}/edit_naming2.json", 'r') as file:
            all_commands= json.load(file)

        for command, variables in xvars.items():
            if command not in  all_xvars:
                raise Exception(f'xvars must be in {all_xvars}')
            if len(variables) != len(all_commands[command]):
                raise Exception(f'{command} requires the {len(all_commands[command])} options: {all_commands[command]}')
            
        for command, variables in yvars.items():
            if command not in all_commands.keys():
                raise Exception(f'{command} is not a valid yvar see edit_naming.json for options')
            if len(variables) != len(all_commands[command]):
                raise Exception(f'{command} requires the {len(all_commands[command])} options: {all_commands[command]}')
            
        self.plots.append([title, xvars, yvars])
            

        


#################################################################################################################################################

def make_dict(data):
    if type(data)==type({}):
        return data
    dic = {}
    for entry in data:
        dic[entry] = []
    return dic


def switch_loop(switch_mappings, localz):
    switch_strings =[]
    for (switch_number, dict_name), dict in switch_mappings.items():
        if dict_name in localz and dict is not None and dict_name is not None:
            user_input = localz.get(dict_name)
            if user_input is not None:
                switch_strings.append(f'switch {switch_number} {dict[user_input]}')

    return switch_strings



def list_input_requirement(lis):
    for input in lis: 
        if input != None: 
            if len(input) != 2: 
                raise Exception("list of size 2 required")
            for value in input:
                if (type(value) != type(1)) and (type(value) != type(1.)): 
                    raise Exception('list must contain int or float')

def string_input_requirement(string: str, options: list):
    opt = ', '.join(options)
    if string not in options: 
        fstrin = f'{string} is not one of: {opt}'
        raise Exception(fstrin)

def element_input_requirement(element: str):
    if 'element_list' not in globals():
        global element_list
        df = pd.read_csv(f'{paths.to_folder_cretin()}/periodic_table.csv')
        element_list = df['Symbol'].to_string(index = False)

    new = []
    for entry in element_list:
        entry = ''.join(entry.split())
        entry = entry.upper()
        new.append(entry)

    element_list = new
    element = element.upper()
    if element not in element_list: 
        #raise Exception('must be one of H, HE, LI, BE ...')
        pass

def interger_input_requirement(inter : int, options : list):
    if inter not in options:
        fstrin = f'{inter} is not one of: {options}'
        raise Exception(fstrin)
    

def recursive_search(item, target):
    if isinstance(item, list):
        for sub_item in item:
            if recursive_search(sub_item, target):
                return True
    elif item == target:
        return True
    return False

