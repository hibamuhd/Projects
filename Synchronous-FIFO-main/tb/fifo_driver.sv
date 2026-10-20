

class fifo_driver #(parameter DATA_WIDTH = 8) extends uvm_driver #(fifo_seq_item #(DATA_WIDTH));
    
    
    `uvm_component_param_utils(fifo_driver #(DATA_WIDTH))

    virtual fifo_if #(DATA_WIDTH) vif; 

    function new(string name, uvm_component parent);
        super.new(name, parent);
    endfunction

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info("DRIVER","DRIVER build phase, agent is running",UVM_LOW)
        if(!uvm_config_db#(virtual fifo_if #(DATA_WIDTH))::get(this, "", "vif", vif)) begin
            `uvm_fatal("NO_VIF", "Virtual interface not found in Config DB")
        end
    endfunction

    task run_phase(uvm_phase phase);
        
        forever begin
            seq_item_port.get_next_item(req);
            @(posedge vif.clk);
            vif.wr_en <= req.wr_en;
            vif.rd_en <= req.rd_en;
            vif.din   <= req.din; // Works for 8, 32, or 64 bits!
            seq_item_port.item_done();
        end
    endtask

endclass