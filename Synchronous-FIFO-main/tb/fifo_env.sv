class fifo_env #(parameter DATA_WIDTH = 8) extends uvm_env;
    `uvm_component_param_utils(fifo_env #(DATA_WIDTH))
    
    fifo_agent #(DATA_WIDTH) agt;
    fifo_scoreboard #(DATA_WIDTH) scb;
    fifo_coverage #(DATA_WIDTH) cov;

    function new(string name, uvm_component parent);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info("ENV","Environment started building",UVM_LOW)
        agt = fifo_agent#(DATA_WIDTH)::type_id::create("agt", this);
        scb = fifo_scoreboard#(DATA_WIDTH)::type_id::create("scb",this);
        cov = fifo_coverage#(DATA_WIDTH)::type_id::create("cov",this);
    endfunction

    function void connect_phase(uvm_phase phase);
        agt.mon.mon_analysis_port.connect(scb.scb_export);
        agt.mon.mon_analysis_port.connect(cov.analysis_export);
    endfunction

endclass