#!/usr/bin/python

import sys
import re
import os

# Instead of
# sts = os.system("mycmd" + " myarg")
# must do
# sts = Popen("mycmd" + " myarg", shell=True).wait()

def my_syscall(cmd):
    DBG=0
    sys.stdout.flush()
    import subprocess
    if DBG: print "okay here we go with", cmd
    return subprocess.Popen(cmd, shell=True).wait()

VERBOSE = False # For real default value, see process_args() below
GENERATED=False # Only need to generate CGRA ONCE (idiot)

# Script dir is maybe '$gen/testdir/unit_tests'
mypath = os.path.realpath(__file__)
mydir  = os.path.dirname(mypath)
global PYPAT_DIR
PYPAT_DIR = mydir + '/../../../pe'
sys.path.insert(0, PYPAT_DIR)
import pe 

BINARY_OPS=[
    'add',
    'sub',
    'gte',
    'lte',
    'eq',
    'sel',
    'rshft',
    'lshft',
    'mul',
    'or',
    'and',
    'xor',
    ]

UNARY_OPS=[
    'abs',
]

LBUF_LIST=[
    'lbuf09',
    'lbuf10',
    ]

VERILATOR_DIR = ''
OPTIONS = {}

def main():
    DBG=0
    mypath = os.path.realpath(__file__)
    mydir  = os.path.dirname(mypath)
    if VERBOSE:
        print ""
        print "Script dir = '%s'" % mydir

    # Script dir is maybe '$gen/testdir/unit_tests'
    global VERILATOR_DIR
    VERILATOR_DIR = mydir + '/../../verilator/generator_z_tb'

#     os.chdir(mydir);
#     if DBG: os.system('pwd');

    process_args()
    show_options()

    # Always build all bsb and bsa files b/c why not
    my_syscall(mydir+'/gen_bsb_files.py')

    print ""
    sys.stdout.flush()

    if not os.path.exists('op_add.bsa'):
        my_syscall(mydir+'/gen_bsa_files.csh')
        print ""
    else:
        print "Skipping (redundant) bsa file generation b/w found 'op_add.bsa'"

    # n_iter = 'forever'
    # n_iter = 3

    i = 1
    n_iter = OPTIONS['repeat']
    while (True):
        print "----------------------------------------------------------------"
        print "Round %d of %s:" % (i, n_iter),
        do_one_round()
        print ""
        i = i + 1
        if n_iter == 'forever': continue
        elif i > int(n_iter): break

def show_options():
    print "OPTIONS"
    for i in OPTIONS:
        print "  OPTIONS['%-7s'] = %s" % (i, OPTIONS[i])
    print ""


def do_one_round():
    # Build input file 'test_in.raw'
    # Build one input file per iteration
    # gen_input_file_seq()
    gen_input_file()
    print ""

    t = OPTIONS['tests']
    # if t == 'all': tests = ['add','mul','lbuf09', 'lbuf10']
    if t == 'all': tests = LBUF_LIST + BINARY_OPS + UNARY_OPS

    # Do the broken one FIRST
    # if t == 'all': tests = ['lbuf09', 'lbuf10', 'add', 'abs', 'eq','lte','gte'] + tests

    else: tests = t.split(",")

    for test in tests:
        do_one_test(test)
        print ""


# E.g. test = 'add'
# bsa files have names like 'mem_lbuf09.bsa', 'op_add.bsa'
def do_one_test(test, DBG=0):
    print "Testing '%s'" % test

    # Find bsa file
    tname_op  = 'op_'  + test
    tname_mem = 'mem_' + test
    if   os.path.exists(tname_op  + '.bsa'): tname = tname_op
    elif os.path.exists(tname_mem + '.bsa'): tname = tname_mem
    else:
        assert False, 'Could not find bsa file'

    # Because 'abs' has delay zero, like our input file 'test_in.raw'
    print_raw_file_abbrev('INPUT ', 'abs', 'test_in.raw')

    gold_out = gen_output_file_gold(test, DBG=DBG)
    print_raw_file_abbrev('GOLD ', tname, gold_out)

    cgra_out = gen_output_file_cgra(tname, DBG=DBG)
    print_raw_file_abbrev('CGRA ', tname, cgra_out)

    # compare_outputs ends the program if comparison is bad...
    compare_outputs(tname, DBG=DBG)

def print_raw_file_abbrev(label, tname, filename):

    # Sample output from e.g.
    #   print_raw_file_abbrev('INPUT ', 'abs', 'test_in.raw') # ('abs' d1=0)
    #   print_raw_file_abbrev('GOLD ', 'add', gold_out)       # ('add' d1=1)
    #   print_raw_file_abbrev('CGRA ', 'add', cgra_out)       # ('add' d1=1)
    #
    #   INPUT   0   1   2   3   4   5   6   7   8   9 
    #   GOLD ---->  1   3   5   7   9  11  13  15  17
    #   CGRA ---->  1   3   5   7   9  11  13  15  17

    # d1,d2 are front-end, back-end delay respectively
    delay = find_delay(tname, DBG=0)
    (d1,d2) = delay.split(',')
    d1 = int(d1)

    print "  %s"   % label,
    if d1 < 40:
        # Align in/out cycles (unless delay is too darn big)
        for i in range(d1): sys.stdout.write('----')
        if d1: sys.stdout.write('>')

    print_raw_file(filename, first_line_only=True)


def compare_outputs(tname, DBG=0):
    gold_out = '%s_gold_out.raw' % tname
    cgra_out  = '%s_CGRA_out.raw' % tname
    cmd = 'cmp %s %s' % (gold_out,cgra_out)

    if VERBOSE:
        print "  Comparing %s and %s..." % (gold_out,cgra_out)
        print "  " + cmd

    err = my_syscall(cmd)
    if err:
        print "  OOPS thatsa no good: '%s' failed" % tname
        # sys.exit(13)
    else:
        if VERBOSE: print "   IT'S GOOD!!!"
        return True



##############################################################################
# FIXME this is whack.  Maybe should be a class or something?
# pypat['add'](1,3)[0] should yield '4' I think
GOLD = {}
# GOLD['add'] = pe.isa.add()
# print GOLD['add'](1,3)[0]

GOLD['add']   = pe.isa.add()
GOLD['sub']   = pe.isa.sub()
GOLD['abs']   = pe.isa.abs()

signed = False
GOLD['gte']   = pe.isa.ge(signed)
GOLD['lte']   = pe.isa.le(signed)
GOLD['eq']    = pe.isa.eq()

GOLD['sel']   = pe.isa.sel()
GOLD['rshft'] = pe.isa.lshr()
GOLD['lshft'] = pe.isa.lshl()
GOLD['or']    = pe.isa.or_()
GOLD['and']   = pe.isa.and_()
GOLD['xor']   = pe.isa.xor()




GOLD['lbuf09']   = (lambda a, b: [a,0])
GOLD['lbuf10']   = (lambda a, b: [a,0])

# Busted ops include, abs, mul, eq
GOLD['abs']   = (lambda a: [abs(a),0])
GOLD['mul']   = (lambda a, b: [a * b,0])

# Spec says 'eq' result is same as 'add'
GOLD['eq']    = GOLD['add']


# FIXME I couldn't figure out how to make gte/lte work with Pat's functions :(
def gold_gte(a,b):
    if (a>=b): return [a,-1]
    else:      return [b,-1]
GOLD['gte']   = gold_gte

def gold_lte(a,b):
    if (a<=b): return [a,-1]
    else:      return [b,-1]
GOLD['lte']   = gold_lte

##############################################################################


def gen_pixels_binary(tname): 
    outpixels = []
    for i in range(len(PIXELS)-1):
        (a,b) = (PIXELS[i], PIXELS[i+1])
        p = GOLD[tname](a,b)[0] & 0xFF
        outpixels.append(p)
    return outpixels

def gen_pixels_unary(tname): 
    outpixels = []
    for i in range(len(PIXELS)):
        a = PIXELS[i]
        p = GOLD[tname](a)[0] & 0xFF
        outpixels.append(p)
    return outpixels


def gen_output_file_gold(tname, DBG=0):
    if is_mem(tname): gold_out = 'mem_%s_gold_out.raw' % tname
    else:             gold_out =  'op_%s_gold_out.raw' % tname

    if   is_mem(tname):    outpixels = PIXELS
    elif is_unary(tname):  outpixels = gen_pixels_unary(tname)
    elif is_binary(tname): outpixels = gen_pixels_binary(tname)
    else: assert False
    # print outpixels

    filename = gold_out
    write_pixels(filename, outpixels)
    if DBG>1: print ''

    if VERBOSE:
        print "  gold-model output file '%s':" % filename
        my_syscall('od -t u1 ' + filename + " | egrep -v '^.......$' | sed 's/^/  /'")
        print ""

    return gold_out
    

def gen_output_file_cgra(tname, DBG=0):

    # Note this output name is 'magic' and directs run.csh to do things :(
    # Maybe (FIXME)
    cgra_out = '%s_CGRA_out.raw' % tname

    if VERBOSE:
        print "  Will use bsa file '%s.bsa' to generate '%s'" % (tname,cgra_out)
    if DBG: my_syscall('(cd %s; ls -l run.csh)' % VERILATOR_DIR)

    # Calculate the appropriate delay e.g. '1,0' for PE ops or '9,0' for 9-deep lbuf.
    delay = find_delay(tname, DBG=0)
    
    cwd = os.getcwd() + '/'
    config = cwd + tname+'.bsa'
    input  = cwd + "test_in.raw"
    output = cwd + cgra_out
    logfile = cwd + "run_csh.log"

    global GENERATED
    # GENERATED=True
    if not GENERATED: run_csh = './run.csh -v'
    else:             run_csh = './run.csh -v -nobuild'
    GENERATED=True
        
    # echo "./run.csh -hackmem -config $bsa -input $in -output $cout -delay $delay"
    cmd = "%s -hackmem -config %s -input %s -output %s -delay %s"\
          % (run_csh, config, input, output, delay)

    DBG=0
    if VERBOSE: savelog = ''
    else:       savelog = ' > ' + logfile + ' 2>&1'

    if VERBOSE:
        # How to redo on error:
        print ""
        print "  set d = " + cwd
        print "  cd " + VERILATOR_DIR
        print "  " + re.sub(cwd, '$d/', cmd)
        if savelog != '': print "  " + savelog
        print ""

    # (cd $v; ./run.csh -hackmem -config $bsa -input $in -output $cout -delay $delay ) || exit -1
    # my_syscall('(cd %s; %s%s)' % (VERILATOR_DIR, cmd, savelog))
    my_syscall('cd %s; %s%s' % (VERILATOR_DIR, cmd, savelog))
    # if not VERBOSE: my_syscall('egrep ^run.csh %s' % logfile)
    sys.stdout.flush()

    if VERBOSE:
        print "  CGRA output file '%s':" % cgra_out
        my_syscall('od -t u1 ' + cgra_out + " | egrep -v '^.......$' | sed 's/./  /'")

    return cgra_out



def find_delay(tname, DBG=0):
    # Calculate the appropriate delay e.g. '1,0' for PE ops or '9,0' for 9-deep lbuf.
    DBG=0
    if is_unary(tname):      delay = '0,0'
    elif tname[0:2] == "op": delay = '1,0'
    elif tname[0:8] == 'mem_lbuf':
        # E.g. name might be 'mem_lbuf09'
        d = int(tname[8:])
        delay = '%d,%d' % (d,d)
        # delay = '%d,0' % (d)
    if DBG: print "  delay should be " + delay
    return delay


def is_unary(tname):
    # Strip prefix e.g. 'op_abs' => 'abs'
    tname = re.sub('op_', '', tname)
    return tname in UNARY_OPS

def is_binary(tname):
    # Strip prefix e.g. 'op_abs' => 'abs'
    tname = re.sub('op_', '', tname)
    return tname in BINARY_OPS

def is_mem(tname):
    return re.search('lbuf|fifo|sram', tname)



# Generate an input file full of sequential 8-bit pixels {0,1,2,3,4,5,6,7,8,9}
def gen_input_file():
    nvecs = OPTIONS['nvecs']
    if OPTIONS['vectype'][0:3] == 'seq':
        print "using input file of %d sequential 8-bit vectors" % OPTIONS['nvecs']
        pixels =  gen_input_file_seq(nvecs)
    elif OPTIONS['vectype'][0:4] == 'rand':
        print "using input file of %d random 8-bit vectors" % OPTIONS['nvecs']
        pixels =  gen_input_file_rand(nvecs)

    # Save the pixels for later
    global PIXELS
    PIXELS = pixels


def gen_input_file_seq(nvecs):

    DBG=0
    pixels = range(nvecs)

    if DBG>1: print pixels
    filename = 'test_in.raw'
    write_pixels(filename, pixels)
    if DBG>1: print ''

    if VERBOSE:
        print "input file '%s':" % filename
        print_raw_file(filename)

    return pixels

def gen_input_file_rand(nvecs):
    import random

    seed = random.randint(1000000,9999999)
    print "seed=", seed
    random.seed(seed)

    DBG=0
    pixels = random.sample(range(0,255), nvecs)

    if DBG>1: print pixels
    filename = 'test_in.raw'
    write_pixels(filename, pixels)
    if DBG>1: print ''

    if VERBOSE:
        print "input file '%s':" % filename
        print_raw_file(filename)

    return pixels




def print_raw_file(filename, first_line_only = False):

    if not first_line_only:
        # The 'egrep' filter removes blank lines from output
        my_syscall('od -t u1 ' + filename + " | egrep -v '^.......$'")
    else:
        # cmd = 'echo "`od -t u1 ' + filename + " | head -n 1 | sed 's/^....... //'" +`'" ...'
        cmd_od   = "od -t u1 " + filename
        cmd_head = "head -n 1"
        cmd_sed  = "sed 's/^....... //'"
        cmd_pipe = "%s | %s | %s" % (cmd_od, cmd_head, cmd_sed)

        # If first line cannot contain entire file, add ellipsis...
        if len(PIXELS) > 16: cmd = 'echo -n "`%s`"...' % cmd_pipe
        else:                cmd = 'echo -n "`%s`"' % cmd_pipe

        my_syscall(cmd)
        print ""

def write_pixels(filename, pixels):
    import struct
    outputstream = my_open(filename, "wb")
    for p in pixels: outputstream.write(struct.pack('B', p))
    outputstream.close()

def my_open(filename, mode):
    no_overwrite = False
    if no_overwrite and os.path.exists(filename):
        sys.stderr.write("Don't wanna write over existing file '%s'" % filename)
        sys.exit(-1)
    return open(filename, mode)

def process_args():
    # Get name of this script
    scriptname = sys.argv[0]
    scriptname_tail = scriptname
    parse = re.search('([/].*$)', scriptname)
    parse = re.search('([^/]+$)', scriptname)
    if (parse): scriptname_tail = parse.group(1)
    args = sys.argv[1:] # shift

    usage = '''Run unit tests.

Usage:
   %s <testname> --repeat <nr> --vectype <vt> --nvecs <nv> --seed <s>

Where:
   <testname> = "all" (default) or one of
                {add,sub,abs,gte,lte,eq,sel,rshft,lshft,mul,or,and,xor}
                {lbuf09,lbuf10}

   <nr> = any integer or "forever" DEFAULT=1
   <vt> = seq, rand or drand       DEFAULT="rand"
   <nv> = any integer              DEFAULT=10
   <s>  = any integer              DEFAULT=none

Examples:
   # Run through all tests once w/sequential vectors
   %s --vectype seq

   # Run through all tests until error.
   %s --repeat forever
''' % (scriptname_tail, scriptname_tail, scriptname_tail)

    global VERBOSE
    VERBOSE=False

    global OPTIONS
    OPTIONS = {}
    OPTIONS['tests']   = 'all'
    OPTIONS['repeat']  = 1
    OPTIONS['vectype'] = 'random'
    OPTIONS['nvecs']   = 10
    OPTIONS['seed']    = False

    # cgra_filename = get_default_cgra_info_filename()
    while (len(args) > 0):
        if   (args[0] == '--help'): print usage; sys.exit(0);
        elif (args[0] == '-v'):
            print "VERBOSE=True"
            VERBOSE = True
        elif (args[0] == '--repeat'):
            OPTIONS['repeat'] = args[1]
            args = args[1:];
        elif (args[0] == '--vectype'):
            OPTIONS['vectype'] = args[1];
            args = args[1:];
        elif (args[0] == '--nvecs'):
            OPTIONS['nvecs'] = int(args[1])
            args = args[1:];
        elif (args[0] == '--seed'):
            OPTIONS['seed'] = int(args[1])
            args = args[1:];
        else:
            OPTIONS['tests'] = args[0];
        args = args[1:]

    if VERBOSE: print OPTIONS

main()
