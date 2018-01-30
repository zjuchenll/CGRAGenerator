#!/bin/tcsh
set RTL_FOLDER="../../top/genesis_verif"
rm -rf INCA_libs irun.*
irun -top tb -timescale 1ns/1ps -l irun.log -access +rwc -notimingchecks -input cmd.tcl tb.v /nobackup/nikhil3/arm_mems/arm/tsmc/cln40g/sram_sp_hsc_rvt_hvt_rvt/r10p2/sram_512w_16b/sram_512w_16b.v ${RTL_FOLDER}/cb_unq1.v ${RTL_FOLDER}/cb_unq2.v ${RTL_FOLDER}/cb_unq3.v ${RTL_FOLDER}/global_controller_unq1.v ${RTL_FOLDER}/global_signal_tile_unq1.v ${RTL_FOLDER}/io16bit_unq1.v ${RTL_FOLDER}/io16bit_unq2.v ${RTL_FOLDER}/io16bit_unq3.v ${RTL_FOLDER}/io16bit_unq4.v ${RTL_FOLDER}/io1bit_unq1.v ${RTL_FOLDER}/io1bit_unq2.v ${RTL_FOLDER}/io1bit_unq3.v ${RTL_FOLDER}/io1bit_unq4.v ${RTL_FOLDER}/jtag_unq1.v ${RTL_FOLDER}/memory_core_unq1.v ${RTL_FOLDER}/memory_tile_unq1.v ${RTL_FOLDER}/mem_unq1.v ${RTL_FOLDER}/pe_tile_new_unq1.v ${RTL_FOLDER}/pe_tile_new_unq2.v ${RTL_FOLDER}/sb_unq1.v ${RTL_FOLDER}/sb_unq2.v ${RTL_FOLDER}/sb_unq3.v ${RTL_FOLDER}/sb_unq4.v ${RTL_FOLDER}/sb_unq5.v ${RTL_FOLDER}/test_cmpr.sv ${RTL_FOLDER}/test_full_add.sv ${RTL_FOLDER}/test_lut.sv ${RTL_FOLDER}/test_mult_add.sv ${RTL_FOLDER}/test_opt_reg.sv ${RTL_FOLDER}/test_pe_comp_unq1.sv ${RTL_FOLDER}/test_pe_unq1.sv ${RTL_FOLDER}/test_shifter_unq1.sv ${RTL_FOLDER}/top.v
