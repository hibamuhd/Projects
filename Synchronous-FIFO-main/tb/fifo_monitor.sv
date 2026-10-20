

class fifo_monitor #(parameter DATA_WIDTH = 8) extends uvm_monitor;
    `uvm_component_param_utils(fifo_monitor #(DATA_WIDTH))

    virtual fifo_if #(DATA_WIDTH) vif;

    
    uvm_analysis_port #(fifo_seq_item #(DATA_WIDTH)) mon_analysis_port;  // The "Radio Transmitter" to broadcast data
 
    function new(string name, uvm_component parent);
        super.new(name, parent);
        mon_analysis_port = new("mon_analysis_port", this);
    endfunction

    function void build_phase(uvm_phase phase);
        `uvm_info("MONITOR","Monitor build phase, agent is running",UVM_LOW)
        super.build_phase(phase);
        if(!uvm_config_db#(virtual fifo_if #(DATA_WIDTH))::get(this, "", "vif", vif)) begin
            `uvm_fatal("MON", "Could not get vif")
        end
    endfunction

    task run_phase(uvm_phase phase);
        
        fifo_seq_item #(DATA_WIDTH) item;   // Temporary variable to hold captured data
        `uvm_info("MON", "Monitor run_phase started!", UVM_LOW)
        forever begin
            @(posedge vif.clk);
            
            // Only capture if Reset is NOT active
            if (vif.rst_n) begin
                
                // Check if there is ANY activity (Write or Read)
                if (vif.wr_en || vif.rd_en) begin
                    
                    // Create a new object to send
                    item = fifo_seq_item#(DATA_WIDTH)::type_id::create("item");
                    
                    // Sample the Interface signals
                    item.wr_en = vif.wr_en;
                    item.rd_en = vif.rd_en;
                    item.din   = vif.din;
                    item.dout  = vif.dout;
                    item.full  = vif.full;
                    item.empty = vif.empty;

                    // Broadcast the object!
                    `uvm_info("MON", $sformatf("Saw Item: WR=%0d RD=%0d DataIn=%0h DataOut=%0h", 
                              item.wr_en, item.rd_en, item.din, item.dout), UVM_LOW)
                    
                    mon_analysis_port.write(item);
                end
            end
        end
    endtask

endclass