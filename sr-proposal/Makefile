##############################################################################
################ Makefile Definitions
################################################################################

########### Generic Env Defs ############
#########################################
# TOP is name of module to compile and run, e.g.
#   - make TOP=fftgen for fftgen test
#   - make TOP=clock to test clock.vp module only.
#TOP := fftgen
TOP := pe

# "realpath" does not work for make version < 3.81
MAKEFILE_PATH:=$(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))
DESIGN_HOME:=$(shell cd $(dir $(MAKEFILE_PATH)); pwd -P)
$(warning Home dir set to $(DESIGN_HOME))

# RUNDIR is where we are actually running
RUNDIR := $(shell cd ./; pwd -P)
$(warning Work started at $(RUNDIR)) 

# this line enables a local Makefile to override values of the main makefile
-include Makefile.local

############# For Genesis2 ##############
#########################################
# GENESIS_TOP = top_$(TOP)
GENESIS_TOP = top_$(TOP)
GENESIS_SYNTH_TOP_PATH = $(GENESIS_TOP).$(TOP)


# list src folders and include folders
GENESIS_SRC := 	-srcpath ./			\
		-srcpath $(DESIGN_HOME)/rtl	\
		-srcpath $(DESIGN_HOME)/tst			

GENESIS_INC := 	-incpath ./			\
		-incpath $(DESIGN_HOME)/rtl	\
		-incpath $(DESIGN_HOME)/tst


GENESIS_LIB := 	-perl_libs ./			\
		-perl_libs $(DESIGN_HOME)/rtl	\
		-perl_libs $(DESIGN_HOME)/tst


GENESIS_CFG := 	-cfgpath ./			\
		-cfgpath $(DESIGN_HOME)/SysCfgs


# vpath directive tells where to search for *.vp and *.vph files
vpath %.vp   $(GENESIS_SRC)
vpath %.svp  $(GENESIS_SRC)

vpath %.vph  $(GENESIS_INC)
vpath %.svph $(GENESIS_INC)

vpath %.cfg $(GENESIS_CFG)
vpath %.xml $(GENESIS_CFG)


# Now list all inputs to genesis: 
GENESIS_PRIMITIVES :=	

GENESIS_ENV :=		$(wildcard $(DESIGN_HOME)/tst/*.vp) $(wildcard $(DESIGN_HOME)/tst/*.svp)
GENESIS_ENV :=		$(notdir $(GENESIS_ENV)) 

GENESIS_DESIGN := 	$(wildcard $(DESIGN_HOME)/rtl/*.vp) $(wildcard $(DESIGN_HOME)/rtl/*.svp)
GENESIS_DESIGN := 	$(notdir $(GENESIS_DESIGN))

GENESIS_INPUTS :=	$(GENESIS_PRIMITIVES) $(GENESIS_ENV) $(GENESIS_DESIGN) 

# debug level
GENESIS_DBG_LEVEL := 0

# List of generated verilog files
GENESIS_VLOG_LIST := genesis_vlog.vf
GENESIS_SYNTH_LIST := $(GENESIS_VLOG_LIST:%.vf=%.synth.vf)
GENESIS_VERIF_LIST := $(GENESIS_VLOG_LIST:%.vf=%.tst.vf)

# Input xml/cfg files, input parameters
GENESIS_CFG_XML	:=
GENESIS_CFG_SCRIPT	:=
GENESIS_PARAMS	:=

# output xml hierarchy file
ifndef GENESIS_HIERARCHY
GENESIS_HIERARCHY := $(TOP).xml
else
  $(warning WARNING: GENESIS_HIERARCHY set to $(GENESIS_HIERARCHY))
endif

# For more Genesis parsing options, type 'Genesis2.pl -help'
#        [-parse]                    ---   should we parse input file to generate perl modules?
#        [-sources|srcpath dir]      ---   Where to find source files
#        [-includes|incpath dir]     ---   Where to find included files
#        [-input file1 .. filen]     ---   List of top level files
#                                    ---   The default is STDIN, but some functions
#                                    ---   (such as "for" or "while")
#                                    ---   may not work properly.
#        [-perl_modules modulename]  ---   Additional perl modules to load
GENESIS_PARSE_FLAGS := 	-parse $(GENESIS_SRC) $(GENESIS_INC) $(GENESIS_LIB) -input $(GENESIS_INPUTS) 		

# For more Genesis parsing options, type 'Genesis2.pl -help'
#        [-generate]                 ---   should we generate a verilog hierarchy?
#        [-top topmodule]            ---   Name of top module to start generation from
#        [-depend filename]          ---   Should Genesis2 generate a dependency file list? (list of input files)
#        [-product filename]         ---   Should Genesis2 generate a product file list? (list of output files)
#        [-hierarchy filename]       ---   Should Genesis2 generate a hierarchy representation tree?
#        [-cfgpath|configs dir]		# Where to find config files (xml/scripts)
#        [-xml filename]             ---   Input XML representation of definitions
#        [-cfg filename]                 # Config file to specify parameter values as a Perl script (overrides xml definitions)
#	 [-parameter path.to.prm1=value1 path.to.another.prm2=value2] --- List of parameter override definitions
#					  				  from command line (overrides xml and cfg definitions)
GENESIS_GEN_FLAGS :=	-gen -top $(GENESIS_TOP) 				\
			-synthtop $(GENESIS_SYNTH_TOP_PATH)			\
			-depend depend.list					\
			-product $(GENESIS_VLOG_LIST)				\
			-hierarchy $(GENESIS_HIERARCHY)				\
			$(GENESIS_CFG)


# What the hell...?
ifneq ($(strip $(GENESIS_CFG_SCRIPT)),)
  GENESIS_GEN_FLAGS	:= $(GENESIS_GEN_FLAGS) -cfg $(GENESIS_CFG_SCRIPT)
  $(warning WARNING: GENESIS_CFG_SCRIPT set to $(GENESIS_CFG_SCRIPT))
endif
ifneq ($(strip $(GENESIS_CFG_XML)),)
  GENESIS_GEN_FLAGS	:= $(GENESIS_GEN_FLAGS) -xml $(GENESIS_CFG_XML)
  $(warning WARNING: GENESIS_CFG_XML set to $(GENESIS_CFG_XML))
endif
ifneq ($(strip $(GENESIS_PARAMS)),)
  GENESIS_GEN_FLAGS	:= $(GENESIS_GEN_FLAGS) -parameter $(GENESIS_PARAMS)
  $(warning WARNING: GENESIS_PARAMS set to $(GENESIS_PARAMS))
endif


##### FLAGS FOR SYNOPSYS VCS COMPILATION #####
##############################################
SIMV = $(RUNDIR)/simv

SIM_TOP = top_$(TOP)
#SIM_TOP = top_clock
#SIM_TOP = clock

VERILOG_ENV :=		 

VERILOG_DESIGN :=	

VERILOG_FILES :=  	$(VERILOG_ENV)	$(VERILOG_DESIGN)					

SYNOPSYS := /hd/cad/synopsys/dc_shell/latest

VERILOG_LIBS := 	-y $(RUNDIR) +incdir+$(RUNDIR)			\
			-y $(SYNOPSYS)/dw/sim_ver/			\
			+incdir+$(SYNOPSYS)/dw/sim_ver/			\
			-y $(SYNOPSYS)/packages/gtech/src_ver/		\
			+incdir+$(SYNOPSYS)/packages/gtech/src_ver/

ifndef TCBN45GS_VERILOG
  $(warn WARNING TCBN45GS_VERILOG not defined)
endif
ifndef TCBN45GSLVT_VERILOG
  $(warn WARNING TCBN45GSLVT_VERILOG not defined)
endif
ifndef TCBN45GSHVT_VERILOG
  $(warn WARNING TCBN45GSHVT_VERILOG not defined)
endif

VERILOG_GATE_LIBS :=	-v $(TCBN45GS_VERILOG)                          \
			-v $(TCBN45GSLVT_VERILOG)                       \
			-v $(TCBN45GSHVT_VERILOG)


# "-sverilog" enables system verilog
# "+lint=PCWM" enables linting error messages (Port connect width mismatch)
# "+lint=all,noVCDE" enables ALL linting error messages except "Verilog compiler directive encountered"
# "+libext+.v" specifies that library files (imported by the "-y" directive) ends with ".v"
# "-notice" used to get details when ports are coerced to inout
# "-full64" for 64 bit compilation and simulation
# "+v2k" for verilog 2001 constructs such as generate and "mecbk" (below)
# "-timescale=1ns/1ns" sets the time unit and time precision for the entire design
# "+noportcoerce" compile-time option to shut off the port coercion for the entire design
# "-top topModuleName" specifies the top module
# "-f verilogFiles.list" specifies a file that contains list of verilog files to compile
# "+memcbk" Enables callbacks for memories and multi-dimensional arrays (MDAs). 

#				+lint=PCWM					\

VERILOG_COMPILE_FLAGS := 	-sverilog 					\
				+cli 						\
                                +memcbk                                         \
				+lint=all,noVCDE				\
				+libext+.v					\
				-notice						\
				-full64						\
				+v2k						\
				-debug_pp					\
				-timescale=1ps/1ps				\
				+noportcoerce         				\
				+vcs+lic+wait					\
				-licqueue					\
				-ld $(VCS_CC) 					\
				-top $(SIM_TOP)					\
				$(VERILOG_FILES) $(VERILOG_LIBS)

# "+vpdbufsize+100" limit the internal buffer to 100MB (forces flushing to disk)
# "+vpdports" Record information about ports (signal/in/out)
# "+vpdfileswitchsize+1000" limits the wave file to 1G (then switch to next file)
VERILOG_SIMULATION_FLAGS := 	$(VERILOG_SIMULATION_FLAGS) 			\
				-l simv.log					\
				+vcs+lic+wait					\
				+vpdbufsize+100					\
				+vpdfileswitchsize+100

##### END OF FLAGS FOR SYNOPSYS COMPILATION ####

##### FLAGS FOR SYNOPSYS DC-SHELL #####
#######################################
### See Makefile.synth for synthesis crap that would otherwise go here...
### -include Makefile.synth
######## END OF FLAGS FOR SYNOPSYS DC-SHELL #####


################################################################################
################ Makefile Rules
################################################################################
#default rule: 
all: run


###### Genesis2 rules: ######
#############################
# phony rules for verilog generation process
.PHONY: gen genesis_clean
gen: $(GENESIS_VLOG_LIST) $(GENESIS_SYNTH_LIST) $(GENESIS_VERIF_LIST)

# This is the rule to activate Genesis2 generator to generate verilog 
# files (_unqN.v) from the genesis (.vp) program.
# Use "make gen GEN=<genesis2_gen_flags>" to add elaboration time flags
GENESIS=Genesis2.pl
$(GENESIS_VLOG_LIST) $(GENESIS_SYNTH_LIST) $(GENESIS_VERIF_LIST): $(GENESIS_INPUTS) $(GENESIS_CFG_XML) $(GENESIS_CFG_SCRIPT)
#	Check for existence of Genesis2.pl
	@if ! `command -v $(GENESIS) > /dev/null`; then echo;\
	 echo 'ERROR Cannot find Genesis2.pl';\
         echo 'ERROR Did you source /horowitz/users/steveri/gui/configs/setup_stanford.cshrc?';\
	 echo; false; fi
	@echo ""
	@echo Making $@ because of $?
	@echo ==================================================
	$(GENESIS) $(GENESIS_GEN_FLAGS) $(GEN) $(GENESIS_PARSE_FLAGS) -debug $(GENESIS_DBG_LEVEL) 
#	locDesignMap.pl TCL=gen_params.tcl INPUT_XML=small_$(GENESIS_HIERARCHY) DESIGN_FILE=BB_clock.design LOC_DESIGN_MAP_FILE=/dev/null PARAM_LIST_FILE=/dev/null PARAM_ATTRIBUTE_FILE=/dev/null > /dev/null

genesis_clean:
	@echo ""
	@echo Cleaning previous runs of Genesis
	@echo ===================================
	@if test -f "genesis_clean.cmd"; then 	\
		 ./genesis_clean.cmd;		\
	fi
	\rm -rf $(GENESIS_VLOG_LIST) $(GENESIS_SYNTH_LIST) $(GENESIS_VERIF_LIST)
###### END OF Genesis2 Rules #######



# VCS compile rules:
#####################
# compile rules:
# use "make COMP=+define+<compile_time_flag[=value]>" to add compile time flags
.PHONY: comp
comp: $(SIMV)

#$(SIMV):$(GENESIS_VLOG_LIST) clock.v
$(SIMV):$(GENESIS_VLOG_LIST)
	@echo ""
	@echo Making $@ because of $?
	@echo ==================================================
	sleep 1;
#	vcs  $(VERILOG_COMPILE_FLAGS) clock.v $(COMP) 2>&1 | tee comp_bb.log 
#	vcs  $(VERILOG_COMPILE_FLAGS) -f $(RUNDIR)/$(GENESIS_VLOG_LIST) $(COMP) 2>&1 | tee comp_bb.log 
	export VCS_ARCH_OVERRIDE=linux;\
	vcs  $(VERILOG_COMPILE_FLAGS) -f $(RUNDIR)/$(GENESIS_VLOG_LIST) $(COMP)


# Simulation rules:
#####################
# use "make run RUN=+<runtime_flag[=value]>" to add runtime flags
.PHONY: run
run: $(SIMV)
	@echo ""
	@echo Now Running simv
	@echo ==================================================
	$(SIMV) $(VERILOG_SIMULATION_FLAGS) $(RUN)


# DC & ICC Run rules: See Makefile.synth
########################################
-include Makefile.synth

# # Something for the GUI: "make gui_info" gives the gui everything it needs to know.
# gui_info:
# 	@echo Hello GUI how are you?
# 	$(DESIGN_HOME)/bin/tmp_hello_gui.csh

# Cleanup rules:
#####################
.PHONY: clean cleanall 
#clean: genesis_clean synthesis_clean
clean:
	@echo ""
	@echo Cleaning old files, objects, logs and garbage
	@echo ==================================================
	\rm -f depend.list
	\rm -f vcdplus.vpd
	\rm -rf $(SIMV) simv.*
	\rm -f *.tcl
	\rm -f *.info
	\rm -rf csrc
	\rm -rf *.daidir
	\rm -rf *.log
	\rm -rf *.pvl
	\rm -rf *.syn
	\rm -rf *.mr
	\rm -rf *.pvk
	\rm -rf *.flc
	\rm -rf ucli.key
	\rm -rf *~
	\rm -rf top.v
	\rm -rf top_*.v
	\rm -f graph_*.m
#	\rm -rf $(IBM_TRGT_DIR)
	\rm -f $(SAIF_FILE)

cleanall: clean 
	\rm -rf depend.list
	\rm -rf DVE*
	\rm -rf vcdplus.vpd
	\rm -rf genesis*
	\rm -f TEST_PASS
	\rm -f TEST_FAIL
