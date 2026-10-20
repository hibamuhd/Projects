class fifo_test extends uvm_test;

    `uvm_component_utils(fifo_test)

    fifo_env #(DATA_WIDTH) env;

    function new(string name = "fifo_test", uvm_component parent = null);
        super.new(name,parent);
    endfunction: new

    function void build_phase(uvm_phase phase);
        super.build_phase(phase);
        // Create the environment
        env = fifo_env#(DATA_WIDTH)::type_id::create("env", this);
    endfunction

    task run_phase(uvm_phase phase);
        fifo_random_seq #(DATA_WIDTH) seq;
        phase.raise_objection(this);
        `uvm_info("TEST","Hello! The UVM env is running.",UVM_LOW)
        `uvm_info(
                "TEST",
                $sformatf("Running %0d-bit FIFO Test...", DATA_WIDTH),
                UVM_LOW
        )
        #100;

        seq = fifo_random_seq #(DATA_WIDTH)::type_id::create("seq");
        seq.start(env.agt.sqr);
        phase.drop_objection(this);
    endtask: run_phase

endclass