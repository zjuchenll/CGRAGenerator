#!/bin/csh

# TODO: could create a makefile that produces a VERY SIMPLE run.csh given all these parms...

# CLEANUP
# if (-e obj_dir)         rm -rf obj_dir
# if (-e counter.vcd)     rm -f  counter.vcd
# if (-e tile_config.dat) rm -f  tile_config.dat

foreach f (obj_dir counter.cvd tile_config.dat)
  if (-e $f) rm -rf $f
end

# set gdir = /nobackup/steveri/github/CGRAGenerator/verilator/generator_zsr/top
# set gdir = /nobackup/steveri/github/CGRAGenerator/hardware/generator_z/top
# set gdir = /nobackup/steveri/github/CGRAGenerator/hardware/generator_z
# set gdir = ../../hardware/generator_z/top
  set gdir = ../../hardware/generator_z

set nclocks = ''

# Process command-line switches.
set GENERATE
while ($#argv)
  # echo "  found switch '$1'"
  if ("$1" == "-clean") then
    exit 0
  else if ("$1" == "-nogen") then
    unset GENERATE
  else if ("$1" == "-config") then
    shift
    set config = "$1"
  else if ("$1" == "-input") then
    shift
    set input = "$1"
  else if ("$1" == "-output") then
    shift
    set output = "$1"
  else if ("$1" == "-nclocks") then
    shift
    # will accept e.g. "1,000,031" or "41K" or "3M"
    set nclocks = `echo $1 | sed 's/,//g' | sed 's/K/000/' | sed 's/M/000000/'`
    set nclocks = "-nclocks $nclocks"
  else
    set testbench = "$1"
  endif
  shift argv
end

# set testbench = top_tb.cpp
# set testbench = $1
if (! -e "$testbench") then
  echo ""
  echo "ERROR: Testbench '$testbench' not found."
  echo ""
  echo "Maybe try one of these:"
  foreach f (*tb*.cpp)
    echo "  $0 $f"
  end
  exit -1
endif

# SETUP (not needed for travis)
# /home/travis/build/StanfordAHA/CGRAGenerator/platform/verilator
if (`hostname` == "kiwi") then
  setenv VERILATOR_ROOT /var/local/verilator-3.900
  set path = (/var/local/verilator-3.900/bin $path)
endif


if (! $?GENERATE) then
  echo "No generate!"
  goto NOGEN
endif

# GENERATE (not needed for travis)
# No need for GENERATE phase on travis because travis script does it already.
if (`hostname` == "kiwi") then
  pushd $gdir/top
    setenv SR_VERILATOR
    if (-e ./genesis_clean.cmd) ./genesis_clean.cmd
    # pwd; ls
    ./run.csh
  popd
endif

NOGEN:


set vdir = $gdir/top/genesis_verif
if (! -e $vdir) then
  echo "ERROR: Could not find vfile directory"
  echo "       $vdir"
  echo "Maybe do something like:"
  echo "    (cd $vdir:h; ./run.csh; popd) |& tee tmp.log"
  exit -1
endif

set top = top

# The old switcharoo
if ($testbench == "tbsr1.cpp") then
  mv $gdir/top/genesis_verif/top.v ./top.v.old
  cp ./top_sr.v $gdir/top/genesis_verif/top.v
endif

if ($testbench == "top_tb.cpp") then
  if (! $?config) set config = $gdir/top_tb/tile_config.dat
  echo "Copy latest config file from $config..."
  # set echo
  # pwd
  # ls -l
  # ls -l $config
  if (! -e "$config") then
    echo
    echo "ERROR Config file does not exist!"
    exit
  endif       
  cp $config tile_config.dat
endif

# set vdir = $gdir/genesis_verif

pushd $vdir >& /dev/null || echo Could not pushd $vdir
  # set vfiles = (*.v *.sv)
  set vfiles = (*.v)
popd >& /dev/null

# So many warnings it wants to DIE!
set myswitches = '-Wno-fatal'

echo
echo verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
  | fold -s | sed '2,$s/^/  /' | sed 's/$/  \\/'
echo

verilator $myswitches -Wall --cc --exe $testbench -y $vdir $vfiles --top-module $top \
  >& /tmp/verilator.out

set verilator_exit_status = $status

echo 'To get the flavor of all the warnings, just showing first 40 lines of output...'
head -n 40 /tmp/verilator.out

if ($verilator_exit_status != 0) exit -1


# cat << eof
# 
# ****************************************************
# NOTE: Currently (3/13) runscript only works to here.
# To get the rest to work, someone is gonna have to
# write a working test bench "tb.cpp" :)
# ****************************************************
# THEN: uncomment the got/bypass in run-travis.csh below.
# ****************************************************
# 
# eof

# echo NOT DOING: make -j -C obj_dir/ -f V${top}.mk V${top}
# echo NOT DOING: obj_dir/V${top}
# echo
# echo "Good-bye!"
# goto END

# build C++ project
# make -j -C obj_dir/ -f Vcounter.mk Vcounter
echo
echo "# Build testbench"
echo make -j -C obj_dir/ -f V${top}.mk V${top}
make -j -C obj_dir/ -f V${top}.mk V${top} || exit -1


# # set input = /tmp/input.raw
# set input = /tmp/gray_small.raw
# # stream io/gray_small.png $input
# # convert io/gray_small.png /tmp/input.raw
# io/myconvert.csh io/gray_small.png /tmp/gray_small.raw

# Prepare an input file

if (! $?input) then
  # testbench will use random numbers for its check (i think)
  set in = ''
endif

if ($?input) then
  if ("$input:e" == "png") then
    # Convert to raw format
    echo
    io/myconvert.csh $input /tmp/input.raw
    echo
  else if ("$input:e" == "raw") then
    cp $input /tmp/input.raw
  else
    echo "ERROR Input file '$input' has invalid extension"
    exit -1
  endif

  set in = "-input /tmp/input.raw"

  # echo "First few lines of input file for comparison..."
  # # set cmd = "od -t x1 /tmp/input.raw"
  # # echo $cmd
  # # $cmd | head
  # set echo
  #   od -t x1 /tmp/input.raw | head
  # unset echo >& /dev/null

endif

set out = ''
if ($?output) then
  set out = "-output $output"
endif

echo
echo "# Run executable simulation"
# echo "obj_dir/Vcounter"
# obj_dir/Vcounter
# echo "obj_dir/V${top}"
# obj_dir/V${top}
# obj_dir/V${top} -config tile_config.dat -input ifile || exit -1
# obj_dir/V${top} -config tile_config.dat -input $input || exit -1
# obj_dir/V${top} -config tile_config.dat $in || exit -1
set cmd = "obj_dir/V${top} -config tile_config.dat $in"

# echo $cmd
# $cmd || exit -1

#    -output /tmp/output.raw \


set echo
  obj_dir/V${top} \
    -config tile_config.dat \
    $in \
    $out \
    $nclocks \
    || exit -1
unset echo >& /dev/null

if ($?input) then
  echo
  set cmd = "od -t x1 /tmp/input.raw"
  set cmd = "od -t u1 /tmp/input.raw"
  echo $cmd; $cmd | head

  echo
  echo foo
  set cmd = "od -t u1 $output"
  echo $cmd; $cmd | head
endif




if (`hostname` == "kiwi") then
cat << eof

************************************************************************
NOTE: If you want to clean up after yourself you'll want to do this:

  ./run.csh -clean
  pushd $gdir/top; ./genesis_clean.cmd; popd

************************************************************************

eof
endif

# END:
