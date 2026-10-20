`timescale 1ns/1ns
package fifo_tb_pkg;
    
    

    import uvm_pkg::*;
    `include "uvm_macros.svh"


    import fifo_params_pkg::*;

    `include "fifo_seq_item.sv"
    `include "fifo_driver.sv"
    `include "fifo_monitor.sv"
    `include "fifo_agent.sv"
    `include "fifo_scoreboard.sv"
    `include "fifo_coverage.sv"
    `include "fifo_env.sv"
    
    
    `include "fifo_sequence.sv"
    
    `include "../tests/test.sv"

endpackage