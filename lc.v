

module lc_table_9_9
(
  input [7-1:0] c1,
  input [7-1:0] c2,
  output [8-1:0] lc1,
  output [8-1:0] lc2
);

  wire [8-1:0] lc_table [0:81-1];
  assign lc1 = lc_table[c1];
  assign lc2 = lc_table[c2];
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

