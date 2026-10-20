class fifo_seq_item #(parameter DATA_WIDTH = 8) extends uvm_sequence_item;

    rand bit wr_en;
    rand bit rd_en;
    // Use the parameter for the data width
    rand bit [DATA_WIDTH-1:0] din;   
    
    // --- OBSERVED SIGNALS (Outputs) ---
    bit [DATA_WIDTH-1:0]      dout;
    bit                       full;
    bit                       empty;

    `uvm_object_param_utils_begin(fifo_seq_item #(DATA_WIDTH))
        `uvm_field_int(wr_en, UVM_ALL_ON)
        `uvm_field_int(rd_en, UVM_ALL_ON)
        `uvm_field_int(din,   UVM_ALL_ON)
    `uvm_object_utils_end

    // 3. Constructor
    function new(string name = "fifo_seq_item");
        super.new(name);
    endfunction

    // 4. Constraints
    constraint valid_ctrl {
        // Let's randomize essentially 'active' transactions
        wr_en dist { 1:=50, 0:=50 }; 
        rd_en dist { 1:=50, 0:=50 };
        
        // Safety: Don't write and read at the same time (optional, but good for starting)
        // (wr_en && rd_en) == 0; 
    }

endclass