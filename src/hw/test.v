

module distance_memory
(
  input clk,
  input rst,
  input input_config_valid,
  input [8-1:0] input_config,
  input re,
  input [4-1:0] rd_pe_1,
  input [4-1:0] rd_pe_2,
  output [80-1:0] pe_1_out,
  output [80-1:0] pe_2_out,
  output rdy
);

  //input_Registers
  reg input_config_valid_r;
  reg [8-1:0] input_config_r;
  reg re_r;
  reg [4-1:0] rd_pe_1_r;
  reg [4-1:0] rd_pe_2_r;
  //---------------
  //Config controler
  reg [10-1:0] config_column_counter;
  reg [80-1:0] config_data;
  reg mem_we;
  reg [4-1:0] mem_waddr;
  //---------------
  //Registering the inputs

  always @(posedge clk) begin
    input_config_valid_r <= input_config_valid;
    input_config_r <= input_config;
    re_r <= re;
    rd_pe_1_r <= rd_pe_1;
    rd_pe_2_r <= rd_pe_2;
  end

  //---------------
  //Configuration algorithm

  always @(posedge clk) begin
    if(rst) begin
      rdy <= 0;
      config_column_counter <= 1;
      mem_we <= 0;
    end else begin
      if(input_config_valid_r) begin
        config_data <= { input_config, config_data[79:8] };
        if(config_column_counter[9]) begin
          mem_we <= 1;
          config_column_counter <= { config_column_counter[8:0], 1'b1 };
        end else begin
          mem_we <= 0;
          config_column_counter <= { config_column_counter[8:0], 1'b0 };
        end
      end 
    end
  end

  //---------------
  //Main memory to be used for the distance memory

  memory_dual_read_rd_sync
  #(
    .data_width(80),
    .addr_width(4)
  )
  memory_dual_read_rd_sync
  (
    .clk(clk),
    .we(mem_we),
    .re(re_r),
    .raddr1(rd_pe_1_r),
    .raddr2(rd_pe_2_r),
    .waddr(mem_waddr),
    .din(config_data),
    .dout1(pe_1_out),
    .dout2(pe_2_out)
  );

  //---------------

endmodule



module memory_dual_read_rd_sync #
(
  parameter init_file = "mem_file.txt",
  parameter data_width = 32,
  parameter addr_width = 8
)
(
  input clk,
  input we,
  input re,
  input [addr_width-1:0] raddr1,
  input [addr_width-1:0] raddr2,
  input [addr_width-1:0] waddr,
  input [data_width-1:0] din,
  output reg [data_width-1:0] dout1,
  output reg [data_width-1:0] dout2
);

  (* ramstyle = "AUTO, no_rw_check" *) reg  [data_width-1:0] mem[0:2**addr_width-1];
  /*
  reg [data_width-1:0] mem [0:2**addr_width-1];
  */

  always @(posedge clk) begin
    if(we) begin
      mem[waddr] <= din;
    end 
    if(re) begin
      dout1 <= mem[raddr1];
      dout2 <= mem[raddr2];
    end 
  end

  //synthesis translate_off
  integer i;

  initial begin
    dout1 = 0;
    dout2 = 0;
    for(i=0; i<2**addr_width; i=i+1) begin
      mem[i] = 0;
    end
    $readmemh(init_file, mem);
  end

  //synthesis translate_on

endmodule

