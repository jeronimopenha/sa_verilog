

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

  wire [10-1:0] dist_table [0:2**8-1];
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
  assign dist_table[16] = 1;
  assign dist_table[17] = 0;
  assign dist_table[18] = 1;
  assign dist_table[19] = 2;
  assign dist_table[20] = 3;
  assign dist_table[21] = 4;
  assign dist_table[22] = 5;
  assign dist_table[23] = 6;
  assign dist_table[24] = 7;
  assign dist_table[32] = 2;
  assign dist_table[33] = 1;
  assign dist_table[34] = 0;
  assign dist_table[35] = 1;
  assign dist_table[36] = 2;
  assign dist_table[37] = 3;
  assign dist_table[38] = 4;
  assign dist_table[39] = 5;
  assign dist_table[40] = 6;
  assign dist_table[48] = 3;
  assign dist_table[49] = 2;
  assign dist_table[50] = 1;
  assign dist_table[51] = 0;
  assign dist_table[52] = 1;
  assign dist_table[53] = 2;
  assign dist_table[54] = 3;
  assign dist_table[55] = 4;
  assign dist_table[56] = 5;
  assign dist_table[64] = 4;
  assign dist_table[65] = 3;
  assign dist_table[66] = 2;
  assign dist_table[67] = 1;
  assign dist_table[68] = 0;
  assign dist_table[69] = 1;
  assign dist_table[70] = 2;
  assign dist_table[71] = 3;
  assign dist_table[72] = 4;
  assign dist_table[80] = 5;
  assign dist_table[81] = 4;
  assign dist_table[82] = 3;
  assign dist_table[83] = 2;
  assign dist_table[84] = 1;
  assign dist_table[85] = 0;
  assign dist_table[86] = 1;
  assign dist_table[87] = 2;
  assign dist_table[88] = 3;
  assign dist_table[96] = 6;
  assign dist_table[97] = 5;
  assign dist_table[98] = 4;
  assign dist_table[99] = 3;
  assign dist_table[100] = 2;
  assign dist_table[101] = 1;
  assign dist_table[102] = 0;
  assign dist_table[103] = 1;
  assign dist_table[104] = 2;
  assign dist_table[112] = 7;
  assign dist_table[113] = 6;
  assign dist_table[114] = 5;
  assign dist_table[115] = 4;
  assign dist_table[116] = 3;
  assign dist_table[117] = 2;
  assign dist_table[118] = 1;
  assign dist_table[119] = 0;
  assign dist_table[120] = 1;
  assign dist_table[128] = 8;
  assign dist_table[129] = 7;
  assign dist_table[130] = 6;
  assign dist_table[131] = 5;
  assign dist_table[132] = 4;
  assign dist_table[133] = 3;
  assign dist_table[134] = 2;
  assign dist_table[135] = 1;
  assign dist_table[136] = 0;

endmodule

