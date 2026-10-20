class fifo_scoreboard #(parameter DATA_WIDTH = 8) extends uvm_scoreboard;
    `uvm_component_param_utils(fifo_scoreboard #(DATA_WIDTH))

    uvm_analysis_imp #(fifo_seq_item #(DATA_WIDTH), fifo_scoreboard #(DATA_WIDTH)) scb_export;
    bit [DATA_WIDTH-1:0] queue [$];
    
    // NEW: Variables to handle 1-cycle latency
    bit                  check_next_cycle;
    bit [DATA_WIDTH-1:0] deferred_expected_data;

    function new(string name, uvm_component parent);
        super.new(name, parent);
        scb_export = new("scb_export", this);
        check_next_cycle = 0; // Initialize
    endfunction

    function void write(fifo_seq_item #(DATA_WIDTH) item);
        
        // -------------------------------------------------------
        // STEP 1: Check Data from the PREVIOUS Read (Latency Fix)
        // -------------------------------------------------------
        if (check_next_cycle) begin
            if (item.dout !== deferred_expected_data) begin
                 `uvm_error("SCB", $sformatf("MISMATCH! Exp=%0h, Got=%0h", 
                                             deferred_expected_data, item.dout))
            end else begin
                 `uvm_info("SCB", $sformatf("MATCH! Data=%0h", item.dout), UVM_LOW)
            end
            check_next_cycle = 0; // Reset flag
        end

        // -------------------------------------------------------
        // STEP 2: Handle New Writes
        // -------------------------------------------------------
        if (item.wr_en && !item.full) begin
            queue.push_back(item.din);
            `uvm_info("SCB", $sformatf("Write: %0h (Queue Size: %0d)", item.din, queue.size()), UVM_LOW)
        end

        // -------------------------------------------------------
        // STEP 3: Handle New Reads (Set up check for NEXT cycle)
        // -------------------------------------------------------
        if (item.rd_en && !item.empty) begin
            if (queue.size() == 0) begin
                `uvm_error("SCB", "Read on Empty Internal Queue! (Test/Design Mismatch)")
            end else begin
                // Pop the data NOW, but verify it LATER
                deferred_expected_data = queue.pop_front();
                check_next_cycle = 1; // Tell scoreboard to check next time
                `uvm_info("SCB", "Read Detected: Waiting 1 cycle for data...", UVM_LOW)
            end
        end
    endfunction
endclass