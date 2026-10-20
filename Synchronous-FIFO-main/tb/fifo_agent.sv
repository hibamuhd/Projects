
class fifo_agent #(parameter DATA_WIDTH = 8) extends uvm_agent;
    `uvm_component_param_utils(fifo_agent #(DATA_WIDTH))

    fifo_driver #(DATA_WIDTH)                    drv;
    uvm_sequencer #(fifo_seq_item #(DATA_WIDTH)) sqr;
    fifo_monitor #(DATA_WIDTH)                   mon;

    function new(string name, uvm_component parent);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info("AGENT","AGENT build phase, agent is running",UVM_LOW)
        drv = fifo_driver#(DATA_WIDTH)::type_id::create("drv", this);
        sqr = uvm_sequencer#(fifo_seq_item#(DATA_WIDTH))::type_id::create("sqr", this);
        mon = fifo_monitor#(DATA_WIDTH)::type_id::create("mon", this);
        
    endfunction

    function void connect_phase(uvm_phase phase);
        drv.seq_item_port.connect(sqr.seq_item_export);
    endfunction

endclass