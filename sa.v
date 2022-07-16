

module sa_4threads_4cells_4neighbors
(
  input clk,
  input rst
);

  reg start;

  always @(posedge clk) begin
    if(rst) begin
      start <= 0;
    end else begin
      start <= 1;
    end
  end

  wire th_done;
  wire th_v;
  wire [2-1:0] th;
  wire [2-1:0] th_cell0;
  wire [2-1:0] th_cell1;

  threads_controller_4th_4cells
  threads_controller_4th_4cells
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .done(th_done),
    .v(th_v),
    .th(th),
    .cell0(th_cell0),
    .cell1(th_cell1)
  );


  cell0_exec_4threads_4cells_4neighbors
  cell0_exec_4threads_4cells_4neighbors
  (
    .clk(clk),
    .th_done_in(th_done),
    .th_v_in(th_v),
    .th_in(th),
    .th_cell0_in(th_cell0),
    .th_cell1_in(th_cell1)
  );


  initial begin
    start = 0;
  end


endmodule



module threads_controller_4th_4cells
(
  input clk,
  input rst,
  input start,
  output reg done,
  output reg [2-1:0] th,
  output reg v,
  output reg [2-1:0] cell0,
  output reg [2-1:0] cell1
);

  reg m_rd;
  reg [2-1:0] m_rd_addr;
  wire [4-1:0] m_out;
  reg m_wr;
  reg [2-1:0] m_wr_addr;
  reg [4-1:0] m_wr_data;
  wire [4-1:0] sum;
  reg [4-1:0] init_mem;
  reg [4-1:0] done_mem;
  reg [2-1:0] p_addr;
  reg p_rd;

  always @(posedge clk) begin
    if(rst) begin
      done <= 0;
    end else begin
      done <= &done_mem;
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      m_rd_addr <= 3;
      m_rd <= 0;
      p_rd <= 0;
      p_addr <= 0;
    end else begin
      if(start) begin
        m_rd <= 1;
        p_addr <= m_rd_addr;
        p_rd <= m_rd;
        if(m_rd_addr == 3) begin
          m_rd_addr <= 0;
        end else begin
          m_rd_addr <= m_rd_addr + 1;
        end
      end 
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      init_mem <= 0;
      done_mem <= 0;
      v <= 0;
      cell0 <= 0;
      cell1 <= 0;
    end else begin
      if(p_rd) begin
        if(init_mem[p_addr]) begin
          cell0 <= m_out[1:0];
          cell1 <= m_out[3:2];
          m_wr_data <= m_out + 1;
        end else begin
          init_mem[p_addr] <= 1;
          cell0 <= 1;
          cell1 <= 0;
          m_wr_data <= 2;
        end
        if(m_out == 14) begin
          done_mem[p_addr] <= 1;
        end 
        m_wr_addr <= p_addr;
        m_wr <= 1;
        th <= p_addr;
        v <= (done_mem[p_addr])? 0 : 1;
      end 
    end
  end


  mem_2r_1w_width4_depth2
  mem_2r_1w_width4_depth2
  (
    .clk(clk),
    .rd(m_rd),
    .rd_addr0(m_rd_addr),
    .out0(m_out),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  initial begin
    done = 0;
    th = 0;
    v = 0;
    cell0 = 0;
    cell1 = 0;
    m_rd = 0;
    m_rd_addr = 0;
    m_wr = 0;
    m_wr_addr = 0;
    m_wr_data = 0;
    init_mem = 0;
    done_mem = 0;
    p_addr = 0;
    p_rd = 0;
  end


endmodule



module mem_2r_1w_width4_depth2 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input rd,
  input [2-1:0] rd_addr0,
  input [2-1:0] rd_addr1,
  output reg [4-1:0] out0,
  output reg [4-1:0] out1,
  input wr,
  input [2-1:0] wr_addr,
  input [4-1:0] wr_data
);

  reg [4-1:0] mem [0:4-1];

  always @(posedge clk) begin
    if(rd) begin
      out0 <= mem[rd_addr0];
      out1 <= mem[rd_addr1];
    end 
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off
  integer i;

  initial begin
    out0 = 0;
    out1 = 0;
    for(i=0; i<2**2; i=i+1) begin
      mem[i] = 0;
    end
    $readmemh(init_file, mem);
  end

  //synthesis translate_on

endmodule



module cell0_exec_4threads_4cells_4neighbors
(
  input clk,
  input th_done_in,
  input th_v_in,
  input [2-1:0] th_in,
  input [2-1:0] th_cell0_in,
  input [2-1:0] th_cell1_in
);

  wire cn_th_done_out;
  wire cn_th_v_out;
  wire [2-1:0] cn_th_out;
  wire [2-1:0] cn_th_cell0_out;
  wire [2-1:0] cn_th_cell1_out;
  wire [2-1:0] cn_th_ch_in;
  wire cn_flag_ch_in;
  wire [2-1:0] cn_th_ch_out;
  wire cn_flag_ch_out;
  wire [3-1:0] cn_node;

  cell_node_pipe_4th_4cells
  cn0_cell_node_pipe_4th_4cells
  (
    .clk(clk),
    .th_done_in(th_done_in),
    .th_v_in(th_v_in),
    .th_in(th_in),
    .th_cell0_in(th_cell0_in),
    .th_cell1_in(th_cell1_in),
    .th_done_out(cn_th_done_out),
    .th_v_out(cn_th_v_out),
    .th_out(cn_th_out),
    .th_cell0_out(cn_th_cell0_out),
    .th_cell1_out(cn_th_cell1_out),
    .th_ch_in(cn_th_ch_in),
    .flag_ch_in(cn_flag_ch_in),
    .th_ch_out(cn_th_ch_out),
    .flag_ch_out(cn_flag_ch_out),
    .node(cn_node)
  );

  wire [4-1:0] n_th_done_out;
  wire [4-1:0] n_th_v_out;
  wire [2-1:0] n_th_out [0:4-1];
  wire [2-1:0] n_th_cell0_out [0:4-1];
  wire [2-1:0] n_th_cell1_out [0:4-1];
  wire [3-1:0] n_th_node_out [0:4-1];
  wire [2-1:0] n_th_ch_out [0:4-1];
  wire [4-1:0] n_flag_ch_out;
  wire [3-1:0] n_neighbor [0:4-1];

  neighbors_pipe_4cells_4neighbors
  neighbors_pipe_4cells_4neighbors_0
  (
    .clk(clk),
    .th_done_in(cn_th_done_out),
    .th_v_in(cn_th_v_out),
    .th_in(cn_th_out),
    .th_cell0_in(cn_th_cell0_out),
    .th_cell1_in(cn_th_cell1_out),
    .th_node_in(cn_node),
    .th_ch_in(cn_th_ch_out),
    .flag_ch_in(cn_flag_ch_out),
    .th_done_out(n_th_done_out[0]),
    .th_v_out(n_th_v_out[0]),
    .th_out(n_th_out[0]),
    .th_cell0_out(n_th_cell0_out[0]),
    .th_cell1_out(n_th_cell1_out[0]),
    .th_node_out(n_th_node_out[0]),
    .th_ch_out(n_th_ch_out[0]),
    .flag_ch_out(n_flag_ch_out[0]),
    .neighbor(n_neighbor[0])
  );


  neighbors_pipe_4cells_4neighbors
  neighbors_pipe_4cells_4neighbors_1
  (
    .clk(clk),
    .th_done_in(n_th_done_out[0]),
    .th_v_in(n_th_v_out[0]),
    .th_in(n_th_out[0]),
    .th_cell0_in(n_th_cell0_out[0]),
    .th_cell1_in(n_th_cell1_out[0]),
    .th_node_in(n_th_node_out[0]),
    .th_ch_in(n_th_ch_out[0]),
    .flag_ch_in(n_flag_ch_out[0]),
    .th_done_out(n_th_done_out[1]),
    .th_v_out(n_th_v_out[1]),
    .th_out(n_th_out[1]),
    .th_cell0_out(n_th_cell0_out[1]),
    .th_cell1_out(n_th_cell1_out[1]),
    .th_node_out(n_th_node_out[1]),
    .th_ch_out(n_th_ch_out[1]),
    .flag_ch_out(n_flag_ch_out[1]),
    .neighbor(n_neighbor[1])
  );


  neighbors_pipe_4cells_4neighbors
  neighbors_pipe_4cells_4neighbors_2
  (
    .clk(clk),
    .th_done_in(n_th_done_out[1]),
    .th_v_in(n_th_v_out[1]),
    .th_in(n_th_out[1]),
    .th_cell0_in(n_th_cell0_out[1]),
    .th_cell1_in(n_th_cell1_out[1]),
    .th_node_in(n_th_node_out[1]),
    .th_ch_in(n_th_ch_out[1]),
    .flag_ch_in(n_flag_ch_out[1]),
    .th_done_out(n_th_done_out[2]),
    .th_v_out(n_th_v_out[2]),
    .th_out(n_th_out[2]),
    .th_cell0_out(n_th_cell0_out[2]),
    .th_cell1_out(n_th_cell1_out[2]),
    .th_node_out(n_th_node_out[2]),
    .th_ch_out(n_th_ch_out[2]),
    .flag_ch_out(n_flag_ch_out[2]),
    .neighbor(n_neighbor[2])
  );


  neighbors_pipe_4cells_4neighbors
  neighbors_pipe_4cells_4neighbors_3
  (
    .clk(clk),
    .th_done_in(n_th_done_out[2]),
    .th_v_in(n_th_v_out[2]),
    .th_in(n_th_out[2]),
    .th_cell0_in(n_th_cell0_out[2]),
    .th_cell1_in(n_th_cell1_out[2]),
    .th_node_in(n_th_node_out[2]),
    .th_ch_in(n_th_ch_out[2]),
    .flag_ch_in(n_flag_ch_out[2]),
    .th_done_out(n_th_done_out[3]),
    .th_v_out(n_th_v_out[3]),
    .th_out(n_th_out[3]),
    .th_cell0_out(n_th_cell0_out[3]),
    .th_cell1_out(n_th_cell1_out[3]),
    .th_node_out(n_th_node_out[3]),
    .th_ch_out(n_th_ch_out[3]),
    .flag_ch_out(n_flag_ch_out[3]),
    .neighbor(n_neighbor[3])
  );


endmodule



module cell_node_pipe_4th_4cells
(
  input clk,
  input th_done_in,
  input th_v_in,
  input [2-1:0] th_in,
  input [2-1:0] th_cell0_in,
  input [2-1:0] th_cell1_in,
  output reg th_done_out,
  output reg th_v_out,
  output reg [2-1:0] th_out,
  output reg [2-1:0] th_cell0_out,
  output reg [2-1:0] th_cell1_out,
  input [2-1:0] th_ch_in,
  input flag_ch_in,
  input [2-1:0] th_ch_out,
  output reg flag_ch_out,
  output [3-1:0] node
);

  reg m0_wr;
  reg [4-1:0] m0_wr_addr;
  reg [4-1:0] m0_wr_data;
  wire [3-1:0] m0_out0;
  wire [3-1:0] m0_out1;

  reg m1_wr;
  reg [4-1:0] m1_wr_addr;
  reg [4-1:0] m1_wr_data;
  wire [3-1:0] m1_out0;
  wire [3-1:0] m1_out1;

  reg p_wr1;
  reg [4-1:0] p_wr_addr1;
  reg p_wr_data;
  wire p_out0;
  wire p_out1;

  reg ch_wr;
  reg [2-1:0] ch_wr_addr;
  reg [12-1:0] ch_wr_data;
  wire [12-1:0] ch_out;

  wire [3-1:0] n0;
  wire [3-1:0] n1;
  wire p0;
  wire p1;
  wire [2-1:0] ch_cell0;
  wire [2-1:0] ch_cell1;

  wire [3-1:0] node0;
  wire [3-1:0] node1;
  assign node = node0;
  assign node0 = (p_out0)? m1_out0 : m0_out0;
  assign node1 = (p_out1)? m1_out1 : m0_out1;

  assign p0 = ch_out[0];
  assign p1 = ch_out[1];
  assign n0 = ch_out[4:2];
  assign n1 = ch_out[7:5];
  assign ch_cell0 = ch_out[9:8];
  assign ch_cell1 = ch_out[11:10];

  always @(posedge clk) begin
    ch_wr <= 0;
    if(th_v_out) begin
      ch_wr <= 1;
      ch_wr_addr <= th_out;
      ch_wr_data <= { th_cell1_out, th_cell0_out, node1, node0, p_out1, p_out0 };
    end 
    m0_wr <= 0;
    m1_wr <= 0;
    p_wr1 <= 0;
    if(flag_ch_out) begin
      m0_wr <= 1;
      m1_wr <= 1;
      if(p0) begin
        m0_wr_addr <= { th_ch_out, ch_cell0 };
        m0_wr_data <= n0;
        m1_wr_addr <= { th_ch_out, ch_cell1 };
        m1_wr_data <= n1;
      end else begin
        m0_wr_addr <= { th_ch_out, ch_cell1 };
        m0_wr_data <= n1;
        m1_wr_addr <= { th_ch_out, ch_cell0 };
        m1_wr_data <= n0;
      end
      if(~^{ p0, p1 }) begin
        p_wr1 <= 1;
        p_wr_addr1 <= { th_ch_out, ch_cell1 };
        p_wr_data <= ~p1;
      end 
    end 
  end


  always @(posedge clk) begin
    th_done_out <= th_done_in;
    th_v_out <= th_v_in;
    th_out <= th_in;
    th_cell0_out <= th_cell0_in;
    th_cell1_out <= th_cell1_in;
    th_ch_out <= th_ch_in;
    flag_ch_out <= flag_ch_in;
  end


  mem_2r_1w_width3_depth4
  m0_mem_2r_1w_width3_depth4
  (
    .clk(clk),
    .rd(1),
    .rd_addr0(th_cell0_in),
    .rd_addr1(th_cell1_in),
    .out0(m0_out0),
    .out1(m0_out1),
    .wr(m0_wr),
    .wr_addr(m0_wr_addr),
    .wr_data(m0_wr_data)
  );


  mem_2r_1w_width3_depth4
  m1_mem_2r_1w_width3_depth4
  (
    .clk(clk),
    .rd(1),
    .rd_addr0(th_cell0_in),
    .rd_addr1(th_cell1_in),
    .out0(m1_out0),
    .out1(m1_out1),
    .wr(m1_wr),
    .wr_addr(m1_wr_addr),
    .wr_data(m1_wr_data)
  );


  mem_2r_1w_width1_depth4
  p_mem_2r_1w_width1_depth4
  (
    .clk(clk),
    .rd(1),
    .rd_addr0(th_cell0_in),
    .rd_addr1(th_cell1_in),
    .out0(p_out0),
    .out1(p_out1),
    .wr(p_wr1),
    .wr_addr(p_wr_addr1),
    .wr_data(p_wr_data)
  );


  mem_2r_1w_width12_depth2
  ch_mem_2r_1w_width12_depth2
  (
    .clk(clk),
    .rd(1),
    .rd_addr0(th_in),
    .out0(ch_out),
    .wr(ch_wr),
    .wr_addr(ch_wr_addr),
    .wr_data(ch_wr_data)
  );


  initial begin
    th_done_out = 0;
    th_v_out = 0;
    th_out = 0;
    th_cell0_out = 0;
    th_cell1_out = 0;
    flag_ch_out = 0;
    m0_wr = 0;
    m0_wr_addr = 0;
    m0_wr_data = 0;
    m1_wr = 0;
    m1_wr_addr = 0;
    m1_wr_data = 0;
    p_wr1 = 0;
    p_wr_addr1 = 0;
    p_wr_data = 0;
    ch_wr = 0;
    ch_wr_addr = 0;
    ch_wr_data = 0;
  end


endmodule



module mem_2r_1w_width3_depth4 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input rd,
  input [4-1:0] rd_addr0,
  input [4-1:0] rd_addr1,
  output reg [3-1:0] out0,
  output reg [3-1:0] out1,
  input wr,
  input [4-1:0] wr_addr,
  input [3-1:0] wr_data
);

  reg [3-1:0] mem [0:16-1];

  always @(posedge clk) begin
    if(rd) begin
      out0 <= mem[rd_addr0];
      out1 <= mem[rd_addr1];
    end 
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off
  integer i;

  initial begin
    out0 = 0;
    out1 = 0;
    for(i=0; i<2**4; i=i+1) begin
      mem[i] = 0;
    end
    $readmemh(init_file, mem);
  end

  //synthesis translate_on

endmodule



module mem_2r_1w_width1_depth4 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input rd,
  input [4-1:0] rd_addr0,
  input [4-1:0] rd_addr1,
  output reg [1-1:0] out0,
  output reg [1-1:0] out1,
  input wr,
  input [4-1:0] wr_addr,
  input [1-1:0] wr_data
);

  reg [1-1:0] mem [0:16-1];

  always @(posedge clk) begin
    if(rd) begin
      out0 <= mem[rd_addr0];
      out1 <= mem[rd_addr1];
    end 
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off
  integer i;

  initial begin
    out0 = 0;
    out1 = 0;
    for(i=0; i<2**4; i=i+1) begin
      mem[i] = 0;
    end
    $readmemh(init_file, mem);
  end

  //synthesis translate_on

endmodule



module mem_2r_1w_width12_depth2 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input rd,
  input [2-1:0] rd_addr0,
  input [2-1:0] rd_addr1,
  output reg [12-1:0] out0,
  output reg [12-1:0] out1,
  input wr,
  input [2-1:0] wr_addr,
  input [12-1:0] wr_data
);

  reg [12-1:0] mem [0:4-1];

  always @(posedge clk) begin
    if(rd) begin
      out0 <= mem[rd_addr0];
      out1 <= mem[rd_addr1];
    end 
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off
  integer i;

  initial begin
    out0 = 0;
    out1 = 0;
    for(i=0; i<2**2; i=i+1) begin
      mem[i] = 0;
    end
    $readmemh(init_file, mem);
  end

  //synthesis translate_on

endmodule



module neighbors_pipe_4cells_4neighbors
(
  input clk,
  input th_done_in,
  input th_v_in,
  input [2-1:0] th_in,
  input [2-1:0] th_cell0_in,
  input [2-1:0] th_cell1_in,
  input [3-1:0] th_node_in,
  output reg th_done_out,
  output reg th_v_out,
  output reg [2-1:0] th_out,
  output reg [2-1:0] th_cell0_out,
  output reg [2-1:0] th_cell1_out,
  output reg [3-1:0] th_node_out,
  input [2-1:0] th_ch_in,
  input flag_ch_in,
  input [2-1:0] th_ch_out,
  output reg flag_ch_out,
  output [3-1:0] neighbor
);

  wire [3-1:0] m_out0;

  assign neighbor = (th_node_out[3])? m_out0 : 0;

  always @(posedge clk) begin
    th_done_out <= th_done_in;
    th_v_out <= th_v_in;
    th_out <= th_in;
    th_cell0_out <= th_cell0_in;
    th_cell1_out <= th_cell1_in;
    th_ch_out <= th_ch_in;
    flag_ch_out <= flag_ch_in;
    th_node_out <= th_node_in;
  end


  mem_2r_1w_width3_depth2
  m_mem_2r_1w_width3_depth2
  (
    .clk(clk),
    .rd(1),
    .rd_addr0(th_node_in[1:0]),
    .out0(m_out0),
    .wr(0),
    .wr_addr(0),
    .wr_data(0)
  );


  initial begin
    th_done_out = 0;
    th_v_out = 0;
    th_out = 0;
    th_cell0_out = 0;
    th_cell1_out = 0;
    th_node_out = 0;
    flag_ch_out = 0;
  end


endmodule



module mem_2r_1w_width3_depth2 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input rd,
  input [2-1:0] rd_addr0,
  input [2-1:0] rd_addr1,
  output reg [3-1:0] out0,
  output reg [3-1:0] out1,
  input wr,
  input [2-1:0] wr_addr,
  input [3-1:0] wr_data
);

  reg [3-1:0] mem [0:4-1];

  always @(posedge clk) begin
    if(rd) begin
      out0 <= mem[rd_addr0];
      out1 <= mem[rd_addr1];
    end 
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off
  integer i;

  initial begin
    out0 = 0;
    out1 = 0;
    for(i=0; i<2**2; i=i+1) begin
      mem[i] = 0;
    end
    $readmemh(init_file, mem);
  end

  //synthesis translate_on

endmodule

