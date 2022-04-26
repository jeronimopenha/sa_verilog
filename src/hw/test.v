

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
        rnd <= { rnd[9:0], rnd[11] ^ rnd[10] ^ rnd[9] ^ rnd[7] };
      end 
    end
  end


  initial begin
    rnd = 0;
  end


endmodule

