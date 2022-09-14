

module st4_lcf_6th_81cells
(
  input clk,
  input rst,
  input [3-1:0] idx_in,
  input v_in,
  input [7-1:0] ca_in,
  input [7-1:0] cb_in,
  input [28-1:0] cva_in,
  input [4-1:0] cva_v_in,
  input [28-1:0] cvb_in,
  input [4-1:0] cvb_v_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [8-1:0] lca_out,
  output reg [8-1:0] lcb_out,
  output reg [32-1:0] lcva_out,
  output reg [4-1:0] lcva_v_out,
  output reg [32-1:0] lcvb_out,
  output reg [4-1:0] lcvb_v_out
);

  wire [8-1:0] lca_t;
  wire [8-1:0] lcb_t;
  wire [32-1:0] lcva_t;
  wire [32-1:0] lcvb_t;

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    lca_out <= lca_t;
    lcb_out <= lcb_t;
    lcva_out <= lcva_t;
    lcva_v_out <= cva_v_in;
    lcvb_out <= lcvb_t;
    lcvb_v_out <= cvb_v_in;
  end


  lc_table_9_9
  lc_table_9_9_c
  (
    .ca(ca_in),
    .cb(cb_in),
    .lca(lca_t),
    .lcb(lcb_t)
  );


  lc_table_9_9
  lc_table_9_9_v_0
  (
    .ca(cva_in[6:0]),
    .cb(cvb_in[6:0]),
    .lca(lcva_t[7:0]),
    .lcb(lcvb_t[7:0])
  );


  lc_table_9_9
  lc_table_9_9_v_1
  (
    .ca(cva_in[13:7]),
    .cb(cvb_in[13:7]),
    .lca(lcva_t[15:8]),
    .lcb(lcvb_t[15:8])
  );


  lc_table_9_9
  lc_table_9_9_v_2
  (
    .ca(cva_in[20:14]),
    .cb(cvb_in[20:14]),
    .lca(lcva_t[23:16]),
    .lcb(lcvb_t[23:16])
  );


  lc_table_9_9
  lc_table_9_9_v_3
  (
    .ca(cva_in[27:21]),
    .cb(cvb_in[27:21]),
    .lca(lcva_t[31:24]),
    .lcb(lcvb_t[31:24])
  );


  initial begin
    idx_out = 0;
    v_out = 0;
    lca_out = 0;
    lcb_out = 0;
    lcva_out = 0;
    lcva_v_out = 0;
    lcvb_out = 0;
    lcvb_v_out = 0;
  end


endmodule



module lc_table_9_9
(
  input [7-1:0] ca,
  input [7-1:0] cb,
  output [8-1:0] lca,
  output [8-1:0] lcb
);

  wire [8-1:0] lc_table [0:81-1];
  assign lca = lc_table[ca];
  assign lcb = lc_table[cb];
  assign lc_table[0] = { 4'd0, 4'd0 };
  assign lc_table[1] = { 4'd0, 4'd1 };
  assign lc_table[2] = { 4'd0, 4'd2 };
  assign lc_table[3] = { 4'd0, 4'd3 };
  assign lc_table[4] = { 4'd0, 4'd4 };
  assign lc_table[5] = { 4'd0, 4'd5 };
  assign lc_table[6] = { 4'd0, 4'd6 };
  assign lc_table[7] = { 4'd0, 4'd7 };
  assign lc_table[8] = { 4'd0, 4'd8 };
  assign lc_table[9] = { 4'd1, 4'd0 };
  assign lc_table[10] = { 4'd1, 4'd1 };
  assign lc_table[11] = { 4'd1, 4'd2 };
  assign lc_table[12] = { 4'd1, 4'd3 };
  assign lc_table[13] = { 4'd1, 4'd4 };
  assign lc_table[14] = { 4'd1, 4'd5 };
  assign lc_table[15] = { 4'd1, 4'd6 };
  assign lc_table[16] = { 4'd1, 4'd7 };
  assign lc_table[17] = { 4'd1, 4'd8 };
  assign lc_table[18] = { 4'd2, 4'd0 };
  assign lc_table[19] = { 4'd2, 4'd1 };
  assign lc_table[20] = { 4'd2, 4'd2 };
  assign lc_table[21] = { 4'd2, 4'd3 };
  assign lc_table[22] = { 4'd2, 4'd4 };
  assign lc_table[23] = { 4'd2, 4'd5 };
  assign lc_table[24] = { 4'd2, 4'd6 };
  assign lc_table[25] = { 4'd2, 4'd7 };
  assign lc_table[26] = { 4'd2, 4'd8 };
  assign lc_table[27] = { 4'd3, 4'd0 };
  assign lc_table[28] = { 4'd3, 4'd1 };
  assign lc_table[29] = { 4'd3, 4'd2 };
  assign lc_table[30] = { 4'd3, 4'd3 };
  assign lc_table[31] = { 4'd3, 4'd4 };
  assign lc_table[32] = { 4'd3, 4'd5 };
  assign lc_table[33] = { 4'd3, 4'd6 };
  assign lc_table[34] = { 4'd3, 4'd7 };
  assign lc_table[35] = { 4'd3, 4'd8 };
  assign lc_table[36] = { 4'd4, 4'd0 };
  assign lc_table[37] = { 4'd4, 4'd1 };
  assign lc_table[38] = { 4'd4, 4'd2 };
  assign lc_table[39] = { 4'd4, 4'd3 };
  assign lc_table[40] = { 4'd4, 4'd4 };
  assign lc_table[41] = { 4'd4, 4'd5 };
  assign lc_table[42] = { 4'd4, 4'd6 };
  assign lc_table[43] = { 4'd4, 4'd7 };
  assign lc_table[44] = { 4'd4, 4'd8 };
  assign lc_table[45] = { 4'd5, 4'd0 };
  assign lc_table[46] = { 4'd5, 4'd1 };
  assign lc_table[47] = { 4'd5, 4'd2 };
  assign lc_table[48] = { 4'd5, 4'd3 };
  assign lc_table[49] = { 4'd5, 4'd4 };
  assign lc_table[50] = { 4'd5, 4'd5 };
  assign lc_table[51] = { 4'd5, 4'd6 };
  assign lc_table[52] = { 4'd5, 4'd7 };
  assign lc_table[53] = { 4'd5, 4'd8 };
  assign lc_table[54] = { 4'd6, 4'd0 };
  assign lc_table[55] = { 4'd6, 4'd1 };
  assign lc_table[56] = { 4'd6, 4'd2 };
  assign lc_table[57] = { 4'd6, 4'd3 };
  assign lc_table[58] = { 4'd6, 4'd4 };
  assign lc_table[59] = { 4'd6, 4'd5 };
  assign lc_table[60] = { 4'd6, 4'd6 };
  assign lc_table[61] = { 4'd6, 4'd7 };
  assign lc_table[62] = { 4'd6, 4'd8 };
  assign lc_table[63] = { 4'd7, 4'd0 };
  assign lc_table[64] = { 4'd7, 4'd1 };
  assign lc_table[65] = { 4'd7, 4'd2 };
  assign lc_table[66] = { 4'd7, 4'd3 };
  assign lc_table[67] = { 4'd7, 4'd4 };
  assign lc_table[68] = { 4'd7, 4'd5 };
  assign lc_table[69] = { 4'd7, 4'd6 };
  assign lc_table[70] = { 4'd7, 4'd7 };
  assign lc_table[71] = { 4'd7, 4'd8 };
  assign lc_table[72] = { 4'd8, 4'd0 };
  assign lc_table[73] = { 4'd8, 4'd1 };
  assign lc_table[74] = { 4'd8, 4'd2 };
  assign lc_table[75] = { 4'd8, 4'd3 };
  assign lc_table[76] = { 4'd8, 4'd4 };
  assign lc_table[77] = { 4'd8, 4'd5 };
  assign lc_table[78] = { 4'd8, 4'd6 };
  assign lc_table[79] = { 4'd8, 4'd7 };
  assign lc_table[80] = { 4'd8, 4'd8 };

endmodule

