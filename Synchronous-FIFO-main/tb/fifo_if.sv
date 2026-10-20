interface fifo_if #(parameter DATA_WIDTH=8) (
    input logic clk, input logic rst_n
);
    logic wr_en;
    logic [DATA_WIDTH-1:0] din;
    
    // Read Interface
    logic                  rd_en;
    logic [DATA_WIDTH-1:0] dout;
    
    // Status Flags
    logic                  full;
    logic                  empty;

endinterface