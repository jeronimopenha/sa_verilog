

module distance_table_9_9
(
  input [8-1:0] opa0,
  input [8-1:0] opa1,
  input opav,
  input [8-1:0] opb0,
  input [8-1:0] opb1,
  input opbv,
  output [10-1:0] da,
  output [10-1:0] db
);

  wire [10-1:0] dist_table [0:81-1];
  wire [10-1:0] da_t;
  wire [10-1:0] db_t;

  assign da_t = dist_table[{ opa1[3:0], opa0[3:0] }] + dist_table[{ opa1[7:4], opa0[7:4] }];
  assign db_t = dist_table[{ opb1[3:0], opb0[3:0] }] + dist_table[{ opb1[7:4], opb0[7:4] }];

  assign da = (opav)? da_t : 0;
  assign db = (opbv)? db_t : 0;

  assign dist_table[0] = 0;
  assign dist_table[1] = 1;
  assign dist_table[2] = 2;
  assign dist_table[3] = 3;
  assign dist_table[4] = 4;
  assign dist_table[5] = 5;
  assign dist_table[6] = 6;
  assign dist_table[7] = 7;
  assign dist_table[8] = 8;
  assign dist_table[9] = 1;
  assign dist_table[10] = 0;
  assign dist_table[11] = 1;
  assign dist_table[12] = 2;
  assign dist_table[13] = 3;
  assign dist_table[14] = 4;
  assign dist_table[15] = 5;
  assign dist_table[16] = 6;
  assign dist_table[17] = 7;
  assign dist_table[18] = 2;
  assign dist_table[19] = 1;
  assign dist_table[20] = 0;
  assign dist_table[21] = 1;
  assign dist_table[22] = 2;
  assign dist_table[23] = 3;
  assign dist_table[24] = 4;
  assign dist_table[25] = 5;
  assign dist_table[26] = 6;
  assign dist_table[27] = 3;
  assign dist_table[28] = 2;
  assign dist_table[29] = 1;
  assign dist_table[30] = 0;
  assign dist_table[31] = 1;
  assign dist_table[32] = 2;
  assign dist_table[33] = 3;
  assign dist_table[34] = 4;
  assign dist_table[35] = 5;
  assign dist_table[36] = 4;
  assign dist_table[37] = 3;
  assign dist_table[38] = 2;
  assign dist_table[39] = 1;
  assign dist_table[40] = 0;
  assign dist_table[41] = 1;
  assign dist_table[42] = 2;
  assign dist_table[43] = 3;
  assign dist_table[44] = 4;
  assign dist_table[45] = 5;
  assign dist_table[46] = 4;
  assign dist_table[47] = 3;
  assign dist_table[48] = 2;
  assign dist_table[49] = 1;
  assign dist_table[50] = 0;
  assign dist_table[51] = 1;
  assign dist_table[52] = 2;
  assign dist_table[53] = 3;
  assign dist_table[54] = 6;
  assign dist_table[55] = 5;
  assign dist_table[56] = 4;
  assign dist_table[57] = 3;
  assign dist_table[58] = 2;
  assign dist_table[59] = 1;
  assign dist_table[60] = 0;
  assign dist_table[61] = 1;
  assign dist_table[62] = 2;
  assign dist_table[63] = 7;
  assign dist_table[64] = 6;
  assign dist_table[65] = 5;
  assign dist_table[66] = 4;
  assign dist_table[67] = 3;
  assign dist_table[68] = 2;
  assign dist_table[69] = 1;
  assign dist_table[70] = 0;
  assign dist_table[71] = 1;
  assign dist_table[72] = 8;
  assign dist_table[73] = 7;
  assign dist_table[74] = 6;
  assign dist_table[75] = 5;
  assign dist_table[76] = 4;
  assign dist_table[77] = 3;
  assign dist_table[78] = 2;
  assign dist_table[79] = 1;
  assign dist_table[80] = 0;

endmodule

