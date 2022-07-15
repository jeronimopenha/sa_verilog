

module testbench_threads_controller_6threads_4cells
(

);

  reg clk;
  reg rst;
  reg start;

  th_controller_6th_4cells
  th_controller_6th_4cells
  (
    .clk(clk),
    .rst(rst),
    .start(start)
  );


  initial begin
    clk = 0;
    rst = 1;
    start = 0;
  end


  initial begin
    $dumpfile("uut.vcd");
    $dumpvars(0);
  end


  initial begin
    @(posedge clk);
    @(posedge clk);
    @(posedge clk);
    rst = 0;
    start = 1;
    #4000;
    $finish;
  end

  always #5clk=~clk;

endmodule



module th_controller_6th_4cells
(
  input clk,
  input rst,
  input start,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [2-1:0] ca_out,
  output reg [2-1:0] cb_out
);

  reg [6-1:0] flag_f_exec;
  reg [6-1:0] v_r;
  reg [3-1:0] idx_r;
  wire [4-1:0] counter;
  wire [4-1:0] counter_t;
  wire [4-1:0] counter_wr;
  wire [2-1:0] ca_out_t;
  wire [2-1:0] cb_out_t;
  assign counter_t = (flag_f_exec[idx_r])? 0 : counter;
  assign counter_wr = (&counter_t)? 0 : counter_t + 1;
  assign ca_out_t = counter_t[1:0];
  assign cb_out_t = counter_t[3:2];

  always @(posedge clk) begin
    if(rst) begin
      idx_out <= 0;
      v_out <= 0;
      ca_out <= 0;
      cb_out <= 0;
      idx_r <= 0;
      flag_f_exec <= 6'b111111;
      v_r <= 6'b111111;
    end else begin
      if(start) begin
        idx_out <= idx_r;
        v_out <= v_r[idx_r];
        ca_out <= ca_out_t;
        cb_out <= cb_out_t;
        v_r[idx_r] <= ~v_r[idx_r];
        if(!v_r[idx_r]) begin
          flag_f_exec[idx_r] <= 0;
          if(idx_r == 5) begin
            idx_r <= 0;
          end else begin
            idx_r <= idx_r + 1;
          end
        end 
      end 
    end
  end


  mem_2r_1w_width4_depth3
  mem_2r_1w_width4_depth3
  (
    .clk(clk),
    .rd_addr0(idx_r),
    .out0(counter),
    .wr(~v_r[idx_r]),
    .wr_addr(idx_r),
    .wr_data(counter_wr)
  );


  initial begin
    idx_out = 0;
    v_out = 0;
    ca_out = 0;
    cb_out = 0;
    flag_f_exec = 0;
    v_r = 0;
    idx_r = 0;
  end


endmodule



module mem_2r_1w_width4_depth3 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input [3-1:0] rd_addr0,
  input [3-1:0] rd_addr1,
  output [4-1:0] out0,
  output [4-1:0] out1,
  input wr,
  input [3-1:0] wr_addr,
  input [4-1:0] wr_data
);

  reg [4-1:0] mem [0:2**3-1];
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end


endmodule

