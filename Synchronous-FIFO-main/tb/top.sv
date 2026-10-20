import uvm_pkg::*;
`include "uvm_macros.svh"
import fifo_params_pkg::*;
import fifo_tb_pkg::*;

module top;
    logic clk;
    logic rst_n;

    initial begin
        clk = 0;
        forever begin
            #5 clk = ~clk;
        end
    end

    initial begin
        rst_n = 0;
        #20 rst_n = 1;
    end

    fifo_if #(.DATA_WIDTH(DATA_WIDTH)) intf (
        .clk(clk),
        .rst_n(rst_n)
    );

    fifo #(
        .DATA_WIDTH(DATA_WIDTH),
        .DEPTH(DEPTH)
    ) dut (
        .clk (intf.clk),
        .rst_n (intf.rst_n),
        .wr_en (intf.wr_en),
        .din   (intf.din),
        .rd_en (intf.rd_en),
        .dout  (intf.dout),
        .full  (intf.full),
        .empty (intf.empty)
    );


    initial begin
        uvm_config_db #(virtual fifo_if #(DATA_WIDTH))::set(null,"*","vif",intf);

        run_test("fifo_test");
    end



endmodule: top