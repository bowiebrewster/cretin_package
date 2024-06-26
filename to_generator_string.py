# this file turns the cretin generator object into a .gen file(string)

class Text_generator():
    def __init__(self, user_input):
        self.user_input = user_input
        self.dict = self.user_input.__dict__.keys()

    # generates a "chapter" string in the generator file
    def start_chapter(self, name : str):
        deliniator = 'c ------------------------------------------------------------'
        header = f'\n{deliniator} \nc   {name}\n{deliniator}\n'
        return header
    
    # int list to string
    def ilts(self, lis:list):
        return_lis = []
        for x in lis:
            if x != None:
                if type(x) == type([]):
                    x = x[0]
                return_lis.append(str(x))
        return ' '.join(return_lis)
    
    #flatten
    def flat(self, lis:list):
        return [item for sublist in lis for item in sublist]
    
    def materials(self):
        string = self.start_chapter('Materials')

        if 'atoms' in self.dict:
            atoms = self.user_input.atoms
            # materials_atom

            for atom in atoms:
                atom0, modeltype = atom

                if atom0[2] == None:
                    atom0[2] = ''

                if atom0[1] == None:
                    line = f'atoms hydrogenic {atom0[0]} \n'
                else:
                    line = f'atoms hydrogenic_{atom0[1]} {atom0[0]} \n'
                    
                string += line

                if 'isorange' in self.dict:
                    isorange = self.user_input.isorange
                    string += f'\tisorange {self.ilts(isorange)}\n'

                if len(modeltype) > 0:
                    modeltype0 = modeltype[0]
                    if len(modeltype0)>0:
                        line = f'\tmodeltype '

                        for model in modeltype0:
                            if model != None:
                                line +=f' {model}'
                        string += line

        if 'regions' in self.dict:
            regions  = self.user_input.regions
            for region in regions:
                region0, element_of_region, material_of_region, rho_of_region, background_of_region, qstart = region
                strings0 = ['region','regionkl','regionklm']
                string += f'\n{strings0[region0[0]-1]} {self.ilts(region0[1])} {self.ilts(region0[2:])}'

                for el in element_of_region:
                    string += f'\n\telement {self.ilts(el)}'

                for mat in material_of_region:
                    string += f'\n\tmaterial {self.ilts(mat)}'

                for rho in rho_of_region:
                    string += f'\n\trho {str(rho_of_region[0])}'

                for bac in background_of_region:
                    string += f'\n\tbackground {self.ilts(background_of_region[0])}'

                if qstart:
                    string += f'\n\tqstart'
        return string

    def geometry(self):
        string = self.start_chapter('Geometry')
        if 'geometry0' in self.dict:
            string += f'\ngeometry {str(self.user_input.geometry0)}'

        if 'geom_nodes' in self.dict:
            nodes = self.user_input.geom_nodes
            nodes0 = f"{nodes[0]}{nodes[1]} {self.ilts(nodes[2])} {self.ilts(nodes[3])}  "

            string +='\n' + nodes0
            for val in nodes[4:]:
                if val != None:
                    string += f"{val} "
        
        if 'geom_quad' in self.dict:
            quad = self.flat(self.user_input.geom_quad)
            string += f'\nquad {self.ilts(quad)}'

        return string

    def radiation(self):
        string = self.start_chapter('Radiation')
        if 'rad_line' in self.dict:
            rad_lin = self.user_input.rad_line

            string += f'line {self.ilts(rad_lin[0:2])} {self.ilts(rad_lin[2])} {self.ilts(rad_lin[3])}'
        
            if 'rad_lbins' in self.dict:
                lbins = self.user_input.rad_lbins
                string += '\n\tlbins ' + self.ilts(lbins[0])

        if 'rad_ebins' in self.dict:
            ebins = self.user_input.rad_ebins
            string += '\nebins ' + self.ilts(ebins)

        if 'rad_angles' in self.dict:
            angles = self.user_input.rad_angles
            string += '\nangles ' + self.ilts(angles)

        return string
    
    def sources(self):
        if 'sources' not in self.dict:
            return ''

        string = self.start_chapter('Sources')
        sources = self.user_input.sources
        for source in sources:
            if source[0] == 'laser':
                string += f'source {source[0]} {source[1]}x {source[2]} {source[3]} {self.ilts(source[4])} {self.ilts(source[-1])}'
            elif source[0]== 'jbndry':
                add = '' if source[-1] == None else self.ilts(source[-1])
                string += f'source {source[0]} {source[1]} {self.ilts(source[2])} {source[3]} {source[4]} {self.ilts(source[5])} {add}'
            elif source[0]== 'jnu':
                string += f'source {source[0]} {self.ilts(source[1])} {source[2]} {source[3]} {self.ilts(source[-2])} {self.ilts(source[-1])}'
            else:
                raise Exception("Source must be type 'jbndry', 'jnu' or 'laser' ")
            
        string += '\n'

        if 'lasers' in self.dict:

            lasers = self.user_input.lasers
            for laser in lasers:
                string += f'laser {laser[0]} {laser[1]}x {laser[2]} {laser[3]} {laser[4]} {laser[5]}'
                if laser[6] != None:
                    string += f' {laser[6]}'

                lasrays = laser[-1]
                for lasray in lasrays:
                    string += f'\n\tlasray {self.ilts(lasray)}'
                    
            string += '\n'

        if 'source_bound' in self.dict:
            bound = self.user_input.source_bound
            last = '' if bound[-1] == None else bound[-1]
            string += f'boundary {bound[0]} {bound[1]} {self.ilts(bound[2])} {bound[3]} {last}'

        if 'source_histories' in self.dict:
            for entry in self.user_input.source_histories:
                string += f'\nhistory {self.ilts(entry)}'


        if 'controls_hist' in self.dict:
            controls_hist = self.user_input.controls_hist
            string += f'\nhistory {self.ilts(controls_hist[0:3])}'

            if 'tv' in self.dict:
                for pair in self.user_input.tv:
                    string += f'\n\ttv {pair[0]} {pair[1]}'


        if 'source_rswitch0' in self.dict:
            pop = self.user_input.source_rswitch0
            for string0 in pop:
                if string0 != None:
                    string += f'\n{string0}'

        return string 
    
    def controls(self):
        if 'control' in self.dict:
            control = self.user_input.control
            string = self.start_chapter('Controls')
            string += '\ntstart '+str(control[0])
            string += '\ntquit '+str(control[1])
            if control[2]:
                string += '\n\nrestart '
            if control[3]:
                string += '\n edits'

        else:
            string = self.start_chapter('Controls')

        if 'data_dumps' in self.dict:
            data_dumps = self.user_input.data_dumps
            if 'all' in data_dumps:
                string += '\n\ndump all'
            if 'spectral' in data_dumps:
                string += '\n\nsdump'
        return string
    
    def switches(self):

        string = self.start_chapter('Switches and Parameters')
        string = self.switchloop(string, 'pop_switches')
        string = self.switchloop(string, 'ot_switches')
        string = self.switchloop(string, 'pop_parameters')
        string = self.switchloop(string, 'radswitches')

        if string == self.start_chapter('Switches and Parameters'):
            return ''

        return string
    
    def switchloop(self, string:str, switch_type_name:str):
        if switch_type_name in self.dict:
            switches = getattr(self.user_input, switch_type_name)
            for switch in switches:
                if switch != None:
                    string += f'\n{switch}'
        return string 
    
    def edits(self):
        if 'plots' not in self.dict:
            return ''
        if len(self.user_input.plots) ==0:
            return ''
        string = self.start_chapter('Edits')
        for plot in self.user_input.plots:
            [title, xvars, yvars] = plot

            string += f'\n\nplot "{title}"'
            for command, variables in xvars.items():
                string +=f'\n\txvar {command} {self.ilts(variables)}'
            for command, variables in yvars.items():
                string +=f'\n\tyvar {command} {self.ilts(variables)}'


        return string


    
    def execute(self):
        output = ''
        for func in [self.materials, self.geometry, self.radiation, self.sources, self.controls, self.switches, self.edits]:
            output += func()+'\n'
        return output