
class fifo_random_seq #(parameter DATA_WIDTH = 8) extends uvm_sequence #(fifo_seq_item #(DATA_WIDTH));

    `uvm_object_param_utils(fifo_random_seq #(DATA_WIDTH))

    function new(string name = "fifo_random_seq");
        super.new(name);
    endfunction

    task body();
        fifo_seq_item #(DATA_WIDTH) req;
        
        `uvm_info("SEQ", "Starting exhaustive coverage sequence...", UVM_LOW)

        // 1. Fill the FIFO and attempt write when full to trigger expression coverage
        // Write 00, FF, AA, 55 repeatedly to hit all toggle bits on `din`
        for (int i = 0; i < 18; i++) begin
            logic [DATA_WIDTH-1:0] toggle_data;
            if (i % 4 == 0) toggle_data = {DATA_WIDTH{1'b0}};
            else if (i % 4 == 1) toggle_data = {DATA_WIDTH{1'b1}};
            else if (i % 4 == 2) toggle_data = {DATA_WIDTH/2{2'b10}};
            else toggle_data = {DATA_WIDTH/2{2'b01}};

            `uvm_do_with(req, {
                wr_en == 1;
                rd_en == 0;
                din == toggle_data;
            })
        end

        // 2. Empty the FIFO and attempt read when empty to trigger expression coverage
        for (int i = 0; i < 18; i++) begin
            `uvm_do_with(req, {
                wr_en == 0;
                rd_en == 1;
            })
        end

        // 3. Simultaneous Read and Write
        repeat(5) begin
             `uvm_do_with(req, {
                wr_en == 1;
                rd_en == 1;
            })
        end

        // 4. Random Activity to hit any remaining generic states
        repeat(50) begin
            `uvm_do_with(req, {
                (wr_en || rd_en) == 1;
            })
        end
        
        `uvm_info("SEQ", "Generation Done!", UVM_LOW)
    endtask

endclass