class fifo_coverage #(parameter DATA_WIDTH = 8) extends uvm_subscriber #(fifo_seq_item #(DATA_WIDTH));
    `uvm_component_param_utils(fifo_coverage #(DATA_WIDTH))

    fifo_seq_item #(DATA_WIDTH) item;

    covergroup fifo_cg;
        option.per_instance = 1;

        cp_wr_en: coverpoint item.wr_en;
        cp_rd_en: coverpoint item.rd_en;
        cp_empty: coverpoint item.empty;
    endgroup

    function new(string name, uvm_component parent);
        super.new(name, parent);
        fifo_cg = new();
        fifo_cg.set_inst_name({get_full_name(), ".fifo_cg"});
    endfunction

    function void write(fifo_seq_item #(DATA_WIDTH) t);
        item = t;
        fifo_cg.sample();
    endfunction

    function void report_phase(uvm_phase phase);
        `uvm_info("COV", $sformatf("Functional Coverage: %.2f%%", fifo_cg.get_coverage()), UVM_LOW)
    endfunction
endclass