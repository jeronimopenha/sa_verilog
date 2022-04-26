

module test_random_generator
(

);


  //Standar I/O signals - Begin
  reg clk;
  reg rst;
  //Standar I/O signals - End

  // Random needs - Begin
  reg rnd_en;
  wire [11-1:0] rnd_rnd;
  wire [11-1:0] rnd_seed;
  assign rnd_seed = 11'b10100101010;
  // Random needs - end

  create_random_generator_11b
  create_random_generator_11b
  (
    .clk(clk),
    .rst(rst),
    .en(rnd_en),
    .seed(rnd_seed),
    .rnd(rnd_rnd)
  );


  initial begin
    clk = 0;
    rst = 1;
    rnd_en = 0;
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
    rnd_en = 1;
    #1000;
    $finish;
  end

  always #5clk=~clk;

  always @(posedge clk) begin
    if(rnd_en) begin
      $display("%d", rnd_rnd[3:0]);
    end 
  end


endmodule



module create_random_generator_11b
(
  input clk,
  input rst,
  input en,
  input [11-1:0] seed,
  output reg [11-1:0] rnd
);


  always @(posedge clk) begin
    if(rst) begin
      rnd <= seed;
    end else begin
      if(en) begin
        rnd <= { rnd[9:0], !(rnd[10] ^ rnd[9] ^ rnd[7] ^ rnd[1]) };
      end 
    end
  end


  initial begin
    rnd = 0;
  end


endmodule

