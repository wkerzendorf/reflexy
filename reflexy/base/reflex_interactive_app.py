import reflex

# This class presents the application interface


class PipelineInteractiveApp(reflex.ReflexIOParser):

    def __init__(self, enable_init_sop=False):
        reflex.ReflexIOParser.__init__(self)
        self.enable_init_sop = enable_init_sop
        # define inputs (Note: you must define at least long option)
        self.add_input("-i", "--in_sof", dest="in_sof", type='string')
        self.add_input("-p", "--in_sop", dest="in_sop", type='string')
        self.add_input("-g", "--in_sof_rec_orig",
                       dest="in_sof_rec_orig", type='string')
        self.add_input("-e", "--enable", dest="enable", default='false')
        # define outputs (Note: you must define at least long option)
        self.add_output("-o", "--out_sof", dest="out_sof")
        self.add_output("-q", "--out_sop", dest="out_sop")
        self.add_output("-f", "--out_sof_loop", dest="out_sof_loop")
        self.add_output("-l", "--out_sop_loop", dest="out_sop_loop")
        self.add_output("-c", "--iteration_complete",
                        dest="iteration_complete")
        self.add_output("-s", "--set_enable", dest="set_enable")
        if(enable_init_sop):
            self.add_output("-n", "--set_init_sop", dest="set_init_sop")

        # get inputs from the command line
        self.inputs = self.get_inputs()
        # get output variables
        self.outputs = self.get_outputs()

        # Initializing state
        self.continue_mode = None
        self.repeat_mode = None
        self.next_iteration_enable = None
        self.set_init_sop = False

        # Input validation
        if not (hasattr(self.inputs,'in_sof') and hasattr(self.inputs,'in_sop')
                and hasattr(self.inputs,'in_sof_rec_orig') ) :
            self.error("Options --in_sof, --in_sop and --in_sof_rec_orig "
                       "are needed")
        if self.inputs.enable.lower() not in ['true', 'false']:
            self.error(self, "Invalid --enable option. Use true or false")
#    if on_sof is not a sof.....

        self.gui_enabled = self.inputs.enable.lower() == 'true'

    def isGUIEnabled(self):
        if self.gui_enabled:
            try:
                from reflex_interactive_gui import ReflexInteractiveWxApp
            except (ImportError, NameError), e:
                print "Error importing modules: ", str(e)
                return False

        return self.gui_enabled

    def setEnableGUI(self, flag):
        if isinstance(flag, basestring):  # backward compat
            flag = flag.lower() == 'true'
        self.gui_enabled = bool(flag)
        self.inputs.enable = str(bool(self.gui_enabled)).upper()

    def setPlotManager(self, dataPlotManager):
        self.dataPlotManager = dataPlotManager

    def showGUI(self):
        try:
            from reflex_interactive_gui import ReflexInteractiveWxApp
            wxApp = ReflexInteractiveWxApp(self, self.dataPlotManager)
            wxApp.MainLoop()
        except (ImportError, NameError), e:
            print "Error importing modules: ", str(e)
            raise

    def is_init_sop_enable(self):
        return self.enable_init_sop

    def set_next_init_sop(self):
        self.set_init_sop = True

    def set_disable_next_iteration(self):
        self.next_iteration_enable = False

    def set_continue_mode(self):
        self.continue_mode = True

    def set_repeat_mode(self, user_edited_param):
        self.repeat_mode = True
        self.user_edited_param = user_edited_param

    def passProductsThrough(self):
        self.set_continue_mode()

    def print_outputs(self):
        if(self.continue_mode and self.repeat_mode):
            raise Exception(
                "Wrong mode: continue and repeat cannot be set at the same time")

        if(self.continue_mode):
            self.outputs.iteration_complete = 'true'
            self.outputs.out_sof = self.inputs.in_sof
            self.outputs.out_sop = self.inputs.in_sop
        elif(self.repeat_mode):
            self.outputs.iteration_complete = 'false'
            self.outputs.out_sof_loop = self.inputs.in_sof_rec_orig
            self.outputs.out_sop_loop = self.user_edited_param

        if self.next_iteration_enable is not None:
            if(self.next_iteration_enable):
                self.outputs.set_enable = 'true'
            else:
                self.outputs.set_enable = 'false'

        if self.enable_init_sop is not None:
            if(self.set_init_sop):
                if(self.continue_mode):
                    self.outputs.set_init_sop = self.outputs.out_sop
                if(self.repeat_mode):
                    self.outputs.set_init_sop = self.outputs.out_sop_loop

        self.write_outputs()
