module fifo #(
    parameter DATA_WIDTH = 8,
    parameter DEPTH      = 16
)(
    input  logic                  clk,
    input  logic                  rst_n,
    
    // Write Interface
    input  logic                  wr_en,
    input  logic [DATA_WIDTH-1:0] din,
    
    // Read Interface
    input  logic                  rd_en,
    output logic [DATA_WIDTH-1:0] dout,
    
    // Status Flags
    output logic                  full,
    output logic                  empty
);

    // --- Internal Constants & Signals ---
    
    // Calculate address width based on depth (e.g., Depth 16 -> 4 bits)
    localparam ADDR_WIDTH = $clog2(DEPTH);   //$clog2 is a built in function that returns the ceiling of base-2 log. if i/p is 7 it returns 3 because 2^3>7 and if input is 17 it returns 5 because 2^4<17<2^5
    
    logic [DATA_WIDTH-1:0] mem [DEPTH-1:0];
    
    // Pointers have 1 extra bit (MSB) to distinguish Full vs Empty
    // Example: If Depth is 16 (0-15), pointer counts 0-31.
    // 0-15 is the first pass, 16-31 is the "wrapped" pass.
    logic [ADDR_WIDTH:0]   wr_ptr; 
    logic [ADDR_WIDTH:0]   rd_ptr; 

    // --- Write Logic ---
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            wr_ptr <= '0;
        end else if (wr_en && !full) begin
            // We write to the memory index (excluding the extra MSB bit)
            mem[wr_ptr[ADDR_WIDTH-1:0]] <= din;
            wr_ptr <= wr_ptr + 1;
        end
    end

    // --- Read Logic ---
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            rd_ptr <= '0;
            dout   <= '0;
        end else if (rd_en && !empty) begin
            // Read from memory index (excluding the extra MSB bit)
            dout   <= mem[rd_ptr[ADDR_WIDTH-1:0]];
            rd_ptr <= rd_ptr + 1;
        end
    end

    // --- Status Flags Logic ---
    
    // EMPTY: Pointers are exactly the same (both loop bit and address match)
    assign empty = (wr_ptr == rd_ptr);

    // FULL: Pointers match in address, but MSB (loop bit) is different.
    // This means Write pointer has wrapped around and caught up to Read.
    //  could illustrate this wrapping concept.
    assign full  = (wr_ptr[ADDR_WIDTH-1:0] == rd_ptr[ADDR_WIDTH-1:0]) && 
                   (wr_ptr[ADDR_WIDTH]     != rd_ptr[ADDR_WIDTH]);

endmodule