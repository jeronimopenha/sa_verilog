

module test_bench_sa_pipeline
(

);

  reg clk;
  reg rst;
  reg start;
  wire done;

  sa_pipeline_6th_16cells
  sa_pipeline_6th_16cells
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .n_exec(16'd1),
    .rd(0),
    .done(done)
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
    #40000;
    $finish;
  end

  always #5clk=~clk;

  always @(posedge clk) begin
    if(done) begin
      $display("ACC DONE!");
      $finish;
    end 
  end


  //Simulation sector - End

endmodule



module sa_pipeline_6th_16cells
(
  input clk,
  input rst,
  input start,
  input [16-1:0] n_exec,
  output reg done,
  input st1_wr,
  input [7-1:0] st1_wr_addr,
  input [5-1:0] st1_wr_data,
  input [4-1:0] st2_wr,
  input [4-1:0] st2_wr_addr,
  input [5-1:0] st2_wr_data,
  input st3_wr,
  input [7-1:0] st3_wr_addr,
  input [4-1:0] st3_wr_data,
  input rd,
  input [7-1:0] rd_addr,
  output out_v,
  output [5-1:0] out_data
);

  // basic control inputs
  // -----
  wire pipe_start;
  reg [17-1:0] counter_total;
  // Threads controller output wires
  wire [3-1:0] th_idx;
  wire th_v;
  wire [4-1:0] th_ca;
  wire [4-1:0] th_cb;
  // -----

  always @(posedge clk) begin
    if(rst) begin
      counter_total <= 0;
      done <= 0;
    end else begin
      if(pipe_start) begin
        if((th_idx == 5) && ~th_v && &{ th_ca, th_cb }) begin
          counter_total <= counter_total + 1;
        end 
        if(counter_total == n_exec) begin
          done <= 1;
        end 
      end 
    end
  end

  // st1 output wires
  wire st1_rdy;
  wire [3-1:0] st1_idx;
  wire st1_v;
  wire [4-1:0] st1_ca;
  wire [4-1:0] st1_cb;
  wire [4-1:0] st1_na;
  wire st1_na_v;
  wire [4-1:0] st1_nb;
  wire st1_nb_v;
  wire st1_sw;
  wire [12-1:0] st1_wa;
  wire [12-1:0] st1_wb;
  // -----
  // st2 output wires
  wire [3-1:0] st2_idx;
  wire st2_v;
  wire [4-1:0] st2_ca;
  wire [4-1:0] st2_cb;
  wire [4-1:0] st2_na;
  wire st2_na_v;
  wire [4-1:0] st2_nb;
  wire st2_nb_v;
  wire [16-1:0] st2_va;
  wire [4-1:0] st2_va_v;
  wire [16-1:0] st2_vb;
  wire [4-1:0] st2_vb_v;
  wire st2_sw;
  wire [12-1:0] st2_wa;
  wire [12-1:0] st2_wb;
  // -----
  // st3 output wires
  wire [3-1:0] st3_idx;
  wire st3_v;
  wire [4-1:0] st3_ca;
  wire [4-1:0] st3_cb;
  wire [16-1:0] st3_cva;
  wire [4-1:0] st3_cva_v;
  wire [16-1:0] st3_cvb;
  wire [4-1:0] st3_cvb_v;
  wire [12-1:0] st3_wb;
  // -----
  // st4 output wires
  wire [3-1:0] st4_idx;
  wire st4_v;
  wire [4-1:0] st4_lca;
  wire [4-1:0] st4_lcb;
  wire [16-1:0] st4_lcva;
  wire [4-1:0] st4_lcva_v;
  wire [16-1:0] st4_lcvb;
  wire [4-1:0] st4_lcvb_v;
  // -----
  // st5 output wires
  wire [3-1:0] st5_idx;
  wire st5_v;
  wire [4-1:0] st5_lca;
  wire [4-1:0] st5_lcb;
  wire [16-1:0] st5_lcva;
  wire [4-1:0] st5_lcva_v;
  wire [16-1:0] st5_lcvb;
  wire [4-1:0] st5_lcvb_v;
  wire [28-1:0] st5_dvac;
  wire [28-1:0] st5_dvbc;
  // -----
  // st6 output wires
  wire [3-1:0] st6_idx;
  wire st6_v;
  wire [14-1:0] st6_dvac;
  wire [14-1:0] st6_dvbc;
  wire [28-1:0] st6_dvas;
  wire [28-1:0] st6_dvbs;
  // -----
  // st7 output wires
  wire [3-1:0] st7_idx;
  wire st7_v;
  wire [7-1:0] st7_dvac;
  wire [7-1:0] st7_dvbc;
  wire [14-1:0] st7_dvas;
  wire [14-1:0] st7_dvbs;
  // -----
  // st8 output wires
  wire [3-1:0] st8_idx;
  wire st8_v;
  wire [7-1:0] st8_dc;
  wire [7-1:0] st8_dvas;
  wire [7-1:0] st8_dvbs;
  // st9 output wires
  wire [3-1:0] st9_idx;
  wire st9_v;
  wire [7-1:0] st9_dc;
  wire [7-1:0] st9_ds;
  // -----
  // st10 output wires
  wire [3-1:0] st10_idx;
  wire st10_v;
  wire st10_sw;
  // -----
  assign pipe_start = &{ start, st1_rdy };

  th_controller_6th_16cells
  th_controller_6th_16cells
  (
    .clk(clk),
    .rst(rst),
    .start(pipe_start),
    .done(done),
    .idx_out(th_idx),
    .v_out(th_v),
    .ca_out(th_ca),
    .cb_out(th_cb)
  );


  st1_c2n_6th_16cells
  st1_c2n_6th_16cells
  (
    .st1_wr(st1_wr),
    .st1_wr_addr(st1_wr_addr),
    .st1_wr_data(st1_wr_data),
    .rd(rd),
    .rd_addr(rd_addr),
    .out_v(out_v),
    .out_data(out_data),
    .clk(clk),
    .rst(rst),
    .rdy(st1_rdy),
    .idx_in(th_idx),
    .v_in(th_v),
    .ca_in(th_ca),
    .cb_in(th_cb),
    .sw_in(st10_sw),
    .st1_wb_in(st1_wb),
    .idx_out(st1_idx),
    .v_out(st1_v),
    .ca_out(st1_ca),
    .cb_out(st1_cb),
    .na_out(st1_na),
    .na_v_out(st1_na_v),
    .nb_out(st1_nb),
    .nb_v_out(st1_nb_v),
    .sw_out(st1_sw),
    .wa_out(st1_wa),
    .wb_out(st1_wb)
  );


  st2_n_6th_16cells
  st2_n_6th_16cells
  (
    .st2_wr(st2_wr),
    .st2_wr_addr(st2_wr_addr),
    .st2_wr_data(st2_wr_data),
    .clk(clk),
    .idx_in(st1_idx),
    .v_in(st1_v),
    .ca_in(st1_ca),
    .cb_in(st1_cb),
    .na_in(st1_na),
    .na_v_in(st1_na_v),
    .nb_in(st1_nb),
    .nb_v_in(st1_nb_v),
    .sw_in(st1_sw),
    .wa_in(st1_wa),
    .wb_in(st1_wb),
    .idx_out(st2_idx),
    .v_out(st2_v),
    .ca_out(st2_ca),
    .cb_out(st2_cb),
    .na_out(st2_na),
    .na_v_out(st2_na_v),
    .nb_out(st2_nb),
    .nb_v_out(st2_nb_v),
    .va_out(st2_va),
    .va_v_out(st2_va_v),
    .vb_out(st2_vb),
    .vb_v_out(st2_vb_v),
    .sw_out(st2_sw),
    .wa_out(st2_wa),
    .wb_out(st2_wb)
  );


  st3_n2c_6th_16cells
  st3_n2c_6th_16cells
  (
    .st3_wr(st3_wr),
    .st3_wr_addr(st3_wr_addr),
    .st3_wr_data(st3_wr_data),
    .clk(clk),
    .rst(rst),
    .idx_in(st2_idx),
    .v_in(st2_v),
    .ca_in(st2_ca),
    .cb_in(st2_cb),
    .na_in(st2_na),
    .na_v_in(st2_na_v),
    .nb_in(st2_nb),
    .nb_v_in(st2_nb_v),
    .va_in(st2_va),
    .va_v_in(st2_va_v),
    .vb_in(st2_vb),
    .vb_v_in(st2_vb_v),
    .st3_wb_in(st3_wb),
    .sw_in(st2_sw),
    .wa_in(st2_wa),
    .wb_in(st2_wb),
    .idx_out(st3_idx),
    .v_out(st3_v),
    .ca_out(st3_ca),
    .cb_out(st3_cb),
    .cva_out(st3_cva),
    .cva_v_out(st3_cva_v),
    .cvb_out(st3_cvb),
    .cvb_v_out(st3_cvb_v),
    .wb_out(st3_wb)
  );


  st4_lcf_6th_16cells
  st4_lcf_6th_16cells
  (
    .clk(clk),
    .idx_in(st3_idx),
    .v_in(st3_v),
    .ca_in(st3_ca),
    .cb_in(st3_cb),
    .cva_in(st3_cva),
    .cva_v_in(st3_cva_v),
    .cvb_in(st3_cvb),
    .cvb_v_in(st3_cvb_v),
    .idx_out(st4_idx),
    .v_out(st4_v),
    .lca_out(st4_lca),
    .lcb_out(st4_lcb),
    .lcva_out(st4_lcva),
    .lcva_v_out(st4_lcva_v),
    .lcvb_out(st4_lcvb),
    .lcvb_v_out(st4_lcvb_v)
  );


  st5_d1_6th_16cells
  st5_d1_6th_16cells
  (
    .clk(clk),
    .idx_in(st4_idx),
    .v_in(st4_v),
    .lca_in(st4_lca),
    .lcb_in(st4_lcb),
    .lcva_in(st4_lcva),
    .lcva_v_in(st4_lcva_v),
    .lcvb_in(st4_lcvb),
    .lcvb_v_in(st4_lcvb_v),
    .idx_out(st5_idx),
    .v_out(st5_v),
    .lca_out(st5_lca),
    .lcb_out(st5_lcb),
    .lcva_out(st5_lcva),
    .lcva_v_out(st5_lcva_v),
    .lcvb_out(st5_lcvb),
    .lcvb_v_out(st5_lcvb_v),
    .dvac_out(st5_dvac),
    .dvbc_out(st5_dvbc)
  );


  st6_d2_s1_6th_16cells
  st6_d2_s1_6th_16cells
  (
    .clk(clk),
    .idx_in(st5_idx),
    .v_in(st5_v),
    .lca_in(st5_lca),
    .lcb_in(st5_lcb),
    .lcva_in(st5_lcva),
    .lcva_v_in(st5_lcva_v),
    .lcvb_in(st5_lcvb),
    .lcvb_v_in(st5_lcvb_v),
    .dvac_in(st5_dvac),
    .dvbc_in(st5_dvbc),
    .idx_out(st6_idx),
    .v_out(st6_v),
    .dvac_out(st6_dvac),
    .dvbc_out(st6_dvbc),
    .dvas_out(st6_dvas),
    .dvbs_out(st6_dvbs)
  );


  st7_s2_6th_16cells
  st7_s2_6th_16cells
  (
    .clk(clk),
    .idx_in(st6_idx),
    .v_in(st6_v),
    .dvac_in(st6_dvac),
    .dvbc_in(st6_dvbc),
    .dvas_in(st6_dvas),
    .dvbs_in(st6_dvbs),
    .idx_out(st7_idx),
    .v_out(st7_v),
    .dvac_out(st7_dvac),
    .dvbc_out(st7_dvbc),
    .dvas_out(st7_dvas),
    .dvbs_out(st7_dvbs)
  );


  st8_s3_6th_16cells
  st8_s3_6th_16cells
  (
    .clk(clk),
    .idx_in(st7_idx),
    .v_in(st7_v),
    .dvac_in(st7_dvac),
    .dvbc_in(st7_dvbc),
    .dvas_in(st7_dvas),
    .dvbs_in(st7_dvbs),
    .idx_out(st8_idx),
    .v_out(st8_v),
    .dc_out(st8_dc),
    .dvas_out(st8_dvas),
    .dvbs_out(st8_dvbs)
  );


  st9_s4_6th_16cells
  st9_s4_6th_16cells
  (
    .clk(clk),
    .idx_in(st8_idx),
    .v_in(st8_v),
    .dc_in(st8_dc),
    .dvas_in(st8_dvas),
    .dvbs_in(st8_dvbs),
    .idx_out(st9_idx),
    .v_out(st9_v),
    .dc_out(st9_dc),
    .ds_out(st9_ds)
  );


  st10_cmp_6th_16cells
  st10_cmp_6th_16cells
  (
    .clk(clk),
    .idx_in(st9_idx),
    .v_in(st9_v),
    .dc_in(st9_dc),
    .ds_in(st9_ds),
    .idx_out(st10_idx),
    .v_out(st10_v),
    .sw_out(st10_sw)
  );


  initial begin
    done = 0;
    counter_total = 0;
  end


endmodule



module th_controller_6th_16cells
(
  input clk,
  input rst,
  input start,
  input done,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [4-1:0] ca_out,
  output reg [4-1:0] cb_out
);

  reg [6-1:0] flag_f_exec;
  reg [6-1:0] v_r;
  reg [3-1:0] idx_r;
  wire [8-1:0] counter;
  wire [8-1:0] counter_t;
  wire [8-1:0] counter_wr;
  wire [4-1:0] ca_out_t;
  wire [4-1:0] cb_out_t;
  assign counter_t = (flag_f_exec[idx_r])? 0 : counter;
  assign counter_wr = (&counter_t)? 0 : counter_t + 1;
  assign ca_out_t = counter_t[3:0];
  assign cb_out_t = counter_t[7:4];

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
        v_out <= (done)? 1'b0 : v_r[idx_r];
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


  mem_2r_1w_width8_depth3
  #(
    .init_file("./th.rom"),
    .read_f(1),
    .write_f(0)
  )
  mem_2r_1w_width8_depth3
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



module mem_2r_1w_width8_depth3 #
(
  parameter read_f = 0,
  parameter init_file = "mem_file.txt",
  parameter write_f = 0,
  parameter output_file = "mem_out_file.txt"
)
(
  input clk,
  input [3-1:0] rd_addr0,
  input [3-1:0] rd_addr1,
  output [8-1:0] out0,
  output [8-1:0] out1,
  input wr,
  input [3-1:0] wr_addr,
  input [8-1:0] wr_data
);

  (*rom_style = "block" *) reg [8-1:0] mem[0:2**3-1];
  /*
  reg [8-1:0] mem [0:2**3-1];
  */
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off

  always @(posedge clk) begin
    if(wr && write_f) begin
      $writememb(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemb(init_file, mem);
    end 
  end


endmodule



module st1_c2n_6th_16cells
(
  input clk,
  input rst,
  input st1_wr,
  input [7-1:0] st1_wr_addr,
  input [5-1:0] st1_wr_data,
  input rd,
  input [7-1:0] rd_addr,
  output reg out_v,
  output reg [5-1:0] out_data,
  input [3-1:0] idx_in,
  input v_in,
  input [4-1:0] ca_in,
  input [4-1:0] cb_in,
  input sw_in,
  input [12-1:0] st1_wb_in,
  output reg rdy,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [4-1:0] ca_out,
  output reg [4-1:0] cb_out,
  output reg [4-1:0] na_out,
  output reg na_v_out,
  output reg [4-1:0] nb_out,
  output reg nb_v_out,
  output reg sw_out,
  output reg [12-1:0] wa_out,
  output reg [12-1:0] wb_out
);

  reg flag;
  reg [4-1:0] counter;
  reg fifo_init;
  wire [4-1:0] na_t;
  wire na_v_t;
  wire [4-1:0] nb_t;
  wire nb_v_t;
  wire [12-1:0] wa_t;
  wire [12-1:0] wb_t;
  wire fifoa_wr_en;
  wire fifoa_rd_en;
  wire [12-1:0] fifoa_data;
  wire fifob_wr_en;
  wire fifob_rd_en;
  wire [12-1:0] fifob_data;
  wire [3-1:0] wa_idx;
  wire [4-1:0] wa_c;
  wire [4-1:0] wa_n;
  wire wa_n_v;
  wire [3-1:0] wb_idx;
  wire [4-1:0] wb_c;
  wire [4-1:0] wb_n;
  wire wb_n_v;
  wire m_wr;
  wire [7-1:0] m_wr_addr;
  wire [5-1:0] m_wr_data;
  assign fifoa_data = { idx_in, ca_in, nb_v_t, nb_t };
  assign fifob_data = { idx_in, cb_in, na_v_t, na_t };
  assign fifoa_rd_en = &{ rdy, v_in };
  assign fifob_rd_en = &{ rdy, v_in };
  assign fifoa_wr_en = |{ &{ rdy, v_in }, fifo_init };
  assign fifob_wr_en = |{ &{ rdy, v_in }, fifo_init };
  assign wa_n = wa_t[3:0];
  assign wa_n_v = wa_t[4];
  assign wa_c = wa_t[8:5];
  assign wa_idx = wa_t[11:9];
  assign wb_n = st1_wb_in[3:0];
  assign wb_n_v = st1_wb_in[4];
  assign wb_c = st1_wb_in[8:5];
  assign wb_idx = st1_wb_in[11:9];
  assign m_wr = sw_in;
  assign m_wr_addr = (flag)? { wa_idx, wa_c } : { wb_idx, wb_c };
  assign m_wr_data = (flag)? { wa_n_v, wa_n } : { wb_n_v, wb_n };

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    ca_out <= ca_in;
    cb_out <= cb_in;
    na_out <= na_t;
    na_v_out <= na_v_t;
    nb_out <= nb_t;
    nb_v_out <= nb_v_t;
    sw_out <= sw_in;
    wa_out <= wa_t;
    wb_out <= wb_t;
    out_v <= rd;
    out_data <= { na_v_t, na_t };
  end


  always @(posedge clk) begin
    if(rst) begin
      flag <= 1;
    end else begin
      if(sw_in) begin
        flag <= ~flag;
      end 
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      rdy <= 0;
      fifo_init <= 0;
      counter <= 0;
    end else begin
      if(counter == 4) begin
        rdy <= 1;
        fifo_init <= 0;
      end else begin
        counter <= counter + 1;
        fifo_init <= 1;
      end
    end
  end


  mem_2r_1w_width5_depth7
  #(
    .init_file("./c_n.rom"),
    .read_f(1),
    .write_f(1),
    .output_file("./c_n_out.rom")
  )
  mem_2r_1w_width5_depth7
  (
    .clk(clk),
    .rd_addr0((rd)? rd_addr : { idx_in, ca_in }),
    .rd_addr1({ idx_in, cb_in }),
    .out0({ na_v_t, na_t }),
    .out1({ nb_v_t, nb_t }),
    .wr(|{ m_wr, st1_wr }),
    .wr_addr((st1_wr)? st1_wr_addr : m_wr_addr),
    .wr_data((st1_wr)? st1_wr_data : m_wr_data)
  );


  fifo
  #(
    .FIFO_WIDTH(12),
    .FIFO_DEPTH_BITS(3)
  )
  fifo_a
  (
    .clk(clk),
    .rst(rst),
    .write_enable(fifoa_wr_en),
    .input_data(fifoa_data),
    .output_read_enable(fifoa_rd_en),
    .output_data(wa_t)
  );


  fifo
  #(
    .FIFO_WIDTH(12),
    .FIFO_DEPTH_BITS(3)
  )
  fifo_b
  (
    .clk(clk),
    .rst(rst),
    .write_enable(fifob_wr_en),
    .input_data(fifob_data),
    .output_read_enable(fifob_rd_en),
    .output_data(wb_t)
  );


  initial begin
    out_v = 0;
    out_data = 0;
    rdy = 0;
    idx_out = 0;
    v_out = 0;
    ca_out = 0;
    cb_out = 0;
    na_out = 0;
    na_v_out = 0;
    nb_out = 0;
    nb_v_out = 0;
    sw_out = 0;
    wa_out = 0;
    wb_out = 0;
    flag = 0;
    counter = 0;
    fifo_init = 0;
  end


endmodule



module mem_2r_1w_width5_depth7 #
(
  parameter read_f = 0,
  parameter init_file = "mem_file.txt",
  parameter write_f = 0,
  parameter output_file = "mem_out_file.txt"
)
(
  input clk,
  input [7-1:0] rd_addr0,
  input [7-1:0] rd_addr1,
  output [5-1:0] out0,
  output [5-1:0] out1,
  input wr,
  input [7-1:0] wr_addr,
  input [5-1:0] wr_data
);

  (*rom_style = "block" *) reg [5-1:0] mem[0:2**7-1];
  /*
  reg [5-1:0] mem [0:2**7-1];
  */
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off

  always @(posedge clk) begin
    if(wr && write_f) begin
      $writememb(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemb(init_file, mem);
    end 
  end


endmodule



module fifo #
(
  parameter FIFO_WIDTH = 32,
  parameter FIFO_DEPTH_BITS = 8,
  parameter FIFO_ALMOSTFULL_THRESHOLD = 2 ** FIFO_DEPTH_BITS - 4,
  parameter FIFO_ALMOSTEMPTY_THRESHOLD = 4
)
(
  input clk,
  input rst,
  input write_enable,
  input [FIFO_WIDTH-1:0] input_data,
  input output_read_enable,
  output reg output_valid,
  output reg [FIFO_WIDTH-1:0] output_data,
  output reg empty,
  output reg almostempty,
  output reg full,
  output reg almostfull,
  output reg [FIFO_DEPTH_BITS+1-1:0] data_count
);

  reg [FIFO_DEPTH_BITS-1:0] read_pointer;
  reg [FIFO_DEPTH_BITS-1:0] write_pointer;
  (*rom_style = "block" *) reg [FIFO_WIDTH-1:0] mem[0:2**FIFO_DEPTH_BITS-1];
  /*
  reg [FIFO_WIDTH-1:0] mem [0:2**FIFO_DEPTH_BITS-1];
  */

  always @(posedge clk) begin
    if(rst) begin
      empty <= 1;
      almostempty <= 1;
      full <= 0;
      almostfull <= 0;
      read_pointer <= 0;
      write_pointer <= 0;
      data_count <= 0;
    end else begin
      case({ write_enable, output_read_enable })
        3: begin
          read_pointer <= read_pointer + 1;
          write_pointer <= write_pointer + 1;
        end
        2: begin
          if(~full) begin
            write_pointer <= write_pointer + 1;
            data_count <= data_count + 1;
            empty <= 0;
            if(data_count == FIFO_ALMOSTEMPTY_THRESHOLD - 1) begin
              almostempty <= 0;
            end 
            if(data_count == 2 ** FIFO_DEPTH_BITS - 1) begin
              full <= 1;
            end 
            if(data_count == FIFO_ALMOSTFULL_THRESHOLD - 1) begin
              almostfull <= 1;
            end 
          end 
        end
        1: begin
          if(~empty) begin
            read_pointer <= read_pointer + 1;
            data_count <= data_count - 1;
            full <= 0;
            if(data_count == FIFO_ALMOSTFULL_THRESHOLD) begin
              almostfull <= 0;
            end 
            if(data_count == 1) begin
              empty <= 1;
            end 
            if(data_count == FIFO_ALMOSTEMPTY_THRESHOLD) begin
              almostempty <= 1;
            end 
          end 
        end
      endcase
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      output_valid <= 0;
    end else begin
      output_valid <= 0;
      if(write_enable == 1) begin
        mem[write_pointer] <= input_data;
      end 
      if(output_read_enable == 1) begin
        output_data <= mem[read_pointer];
        output_valid <= 1;
      end 
    end
  end


endmodule



module st2_n_6th_16cells
(
  input clk,
  input [4-1:0] st2_wr,
  input [4-1:0] st2_wr_addr,
  input [5-1:0] st2_wr_data,
  input [3-1:0] idx_in,
  input v_in,
  input [4-1:0] ca_in,
  input [4-1:0] cb_in,
  input [4-1:0] na_in,
  input na_v_in,
  input [4-1:0] nb_in,
  input nb_v_in,
  input sw_in,
  input [12-1:0] wa_in,
  input [12-1:0] wb_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [4-1:0] ca_out,
  output reg [4-1:0] cb_out,
  output reg [4-1:0] na_out,
  output reg na_v_out,
  output reg [4-1:0] nb_out,
  output reg nb_v_out,
  output reg [16-1:0] va_out,
  output reg [4-1:0] va_v_out,
  output reg [16-1:0] vb_out,
  output reg [4-1:0] vb_v_out,
  output reg sw_out,
  output reg [12-1:0] wa_out,
  output reg [12-1:0] wb_out
);


  wire [16-1:0] va_t;
  wire [4-1:0] va_v_t;
  wire [4-1:0] va_v_m;
  wire [16-1:0] vb_t;
  wire [4-1:0] vb_v_t;
  wire [4-1:0] vb_v_m;
  assign va_v_t = (na_v_in)? va_v_m : 4'b0;
  assign vb_v_t = (nb_v_in)? vb_v_m : 4'b0;

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    ca_out <= ca_in;
    cb_out <= cb_in;
    na_out <= na_in;
    na_v_out <= na_v_in;
    nb_out <= nb_in;
    nb_v_out <= nb_v_in;
    sw_out <= sw_in;
    wa_out <= wa_in;
    wb_out <= wb_in;
    va_out <= va_t;
    va_v_out <= va_v_t;
    vb_out <= vb_t;
    vb_v_out <= vb_v_t;
  end


  mem_2r_1w_width5_depth4
  #(
    .init_file("./n0.rom"),
    .read_f(1),
    .write_f(0)
  )
  mem_2r_1w_width5_depth4_0
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[0], va_t[3:0] }),
    .out1({ vb_v_m[0], vb_t[3:0] }),
    .wr(st2_wr[0]),
    .wr_addr(st2_wr_addr),
    .wr_data(st2_wr_data)
  );


  mem_2r_1w_width5_depth4
  #(
    .init_file("./n1.rom"),
    .read_f(1),
    .write_f(0)
  )
  mem_2r_1w_width5_depth4_1
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[1], va_t[7:4] }),
    .out1({ vb_v_m[1], vb_t[7:4] }),
    .wr(st2_wr[1]),
    .wr_addr(st2_wr_addr),
    .wr_data(st2_wr_data)
  );


  mem_2r_1w_width5_depth4
  #(
    .init_file("./n2.rom"),
    .read_f(1),
    .write_f(0)
  )
  mem_2r_1w_width5_depth4_2
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[2], va_t[11:8] }),
    .out1({ vb_v_m[2], vb_t[11:8] }),
    .wr(st2_wr[2]),
    .wr_addr(st2_wr_addr),
    .wr_data(st2_wr_data)
  );


  mem_2r_1w_width5_depth4
  #(
    .init_file("./n3.rom"),
    .read_f(1),
    .write_f(0)
  )
  mem_2r_1w_width5_depth4_3
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[3], va_t[15:12] }),
    .out1({ vb_v_m[3], vb_t[15:12] }),
    .wr(st2_wr[3]),
    .wr_addr(st2_wr_addr),
    .wr_data(st2_wr_data)
  );


  initial begin
    idx_out = 0;
    v_out = 0;
    ca_out = 0;
    cb_out = 0;
    na_out = 0;
    na_v_out = 0;
    nb_out = 0;
    nb_v_out = 0;
    va_out = 0;
    va_v_out = 0;
    vb_out = 0;
    vb_v_out = 0;
    sw_out = 0;
    wa_out = 0;
    wb_out = 0;
  end


endmodule



module mem_2r_1w_width5_depth4 #
(
  parameter read_f = 0,
  parameter init_file = "mem_file.txt",
  parameter write_f = 0,
  parameter output_file = "mem_out_file.txt"
)
(
  input clk,
  input [4-1:0] rd_addr0,
  input [4-1:0] rd_addr1,
  output [5-1:0] out0,
  output [5-1:0] out1,
  input wr,
  input [4-1:0] wr_addr,
  input [5-1:0] wr_data
);

  (*rom_style = "block" *) reg [5-1:0] mem[0:2**4-1];
  /*
  reg [5-1:0] mem [0:2**4-1];
  */
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off

  always @(posedge clk) begin
    if(wr && write_f) begin
      $writememb(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemb(init_file, mem);
    end 
  end


endmodule



module st3_n2c_6th_16cells
(
  input clk,
  input rst,
  input st3_wr,
  input [7-1:0] st3_wr_addr,
  input [4-1:0] st3_wr_data,
  input [3-1:0] idx_in,
  input v_in,
  input [4-1:0] ca_in,
  input [4-1:0] cb_in,
  input [4-1:0] na_in,
  input na_v_in,
  input [4-1:0] nb_in,
  input nb_v_in,
  input [16-1:0] va_in,
  input [4-1:0] va_v_in,
  input [16-1:0] vb_in,
  input [4-1:0] vb_v_in,
  input [12-1:0] st3_wb_in,
  input sw_in,
  input [12-1:0] wa_in,
  input [12-1:0] wb_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [4-1:0] ca_out,
  output reg [4-1:0] cb_out,
  output reg [16-1:0] cva_out,
  output reg [4-1:0] cva_v_out,
  output reg [16-1:0] cvb_out,
  output reg [4-1:0] cvb_v_out,
  output reg [12-1:0] wb_out
);

  reg flag;
  wire [16-1:0] cva_t;
  wire [16-1:0] cvb_t;
  wire [3-1:0] wa_idx;
  wire [4-1:0] wa_c;
  wire [4-1:0] wa_n;
  wire wa_n_v;
  wire [3-1:0] wb_idx;
  wire [4-1:0] wb_c;
  wire [4-1:0] wb_n;
  wire wb_n_v;
  wire m_wr;
  wire [7-1:0] m_wr_addr;
  wire [4-1:0] m_wr_data;
  assign wa_n = wa_in[3:0];
  assign wa_n_v = wa_in[4];
  assign wa_c = wa_in[8:5];
  assign wa_idx = wa_in[11:9];
  assign wb_n = st3_wb_in[3:0];
  assign wb_n_v = st3_wb_in[4];
  assign wb_c = st3_wb_in[8:5];
  assign wb_idx = st3_wb_in[11:9];
  assign m_wr = (flag)? &{ sw_in, wa_n_v } : &{ sw_in, wb_n_v };
  assign m_wr_addr = (flag)? { wa_idx, wa_n } : { wb_idx, wb_n };
  assign m_wr_data = (flag)? wa_c : wb_c;

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    ca_out <= ca_in;
    cb_out <= cb_in;
    cva_out <= cva_t;
    cva_v_out <= va_v_in;
    cvb_out <= cvb_t;
    cvb_v_out <= vb_v_in;
    wb_out <= wb_in;
  end


  always @(posedge clk) begin
    if(rst) begin
      flag <= 1;
    end else begin
      if(sw_in) begin
        flag <= ~flag;
      end 
    end
  end


  mem_2r_1w_width4_depth7
  #(
    .init_file("./n_c.rom"),
    .read_f(1),
    .write_f(1),
    .output_file("./n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_0
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[3:0] }),
    .rd_addr1({ idx_in, vb_in[3:0] }),
    .out0(cva_t[3:0]),
    .out1(cvb_t[3:0]),
    .wr(|{ m_wr, st3_wr }),
    .wr_addr((st3_wr)? st3_wr_addr : m_wr_addr),
    .wr_data((st3_wr)? st3_wr_data : m_wr_data)
  );


  mem_2r_1w_width4_depth7
  #(
    .init_file("./n_c.rom"),
    .read_f(1),
    .write_f(0),
    .output_file("./n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_1
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[7:4] }),
    .rd_addr1({ idx_in, vb_in[7:4] }),
    .out0(cva_t[7:4]),
    .out1(cvb_t[7:4]),
    .wr(|{ m_wr, st3_wr }),
    .wr_addr((st3_wr)? st3_wr_addr : m_wr_addr),
    .wr_data((st3_wr)? st3_wr_data : m_wr_data)
  );


  mem_2r_1w_width4_depth7
  #(
    .init_file("./n_c.rom"),
    .read_f(1),
    .write_f(0),
    .output_file("./n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_2
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[11:8] }),
    .rd_addr1({ idx_in, vb_in[11:8] }),
    .out0(cva_t[11:8]),
    .out1(cvb_t[11:8]),
    .wr(|{ m_wr, st3_wr }),
    .wr_addr((st3_wr)? st3_wr_addr : m_wr_addr),
    .wr_data((st3_wr)? st3_wr_data : m_wr_data)
  );


  mem_2r_1w_width4_depth7
  #(
    .init_file("./n_c.rom"),
    .read_f(1),
    .write_f(0),
    .output_file("./n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_3
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[15:12] }),
    .rd_addr1({ idx_in, vb_in[15:12] }),
    .out0(cva_t[15:12]),
    .out1(cvb_t[15:12]),
    .wr(|{ m_wr, st3_wr }),
    .wr_addr((st3_wr)? st3_wr_addr : m_wr_addr),
    .wr_data((st3_wr)? st3_wr_data : m_wr_data)
  );


  initial begin
    idx_out = 0;
    v_out = 0;
    ca_out = 0;
    cb_out = 0;
    cva_out = 0;
    cva_v_out = 0;
    cvb_out = 0;
    cvb_v_out = 0;
    wb_out = 0;
    flag = 0;
  end


endmodule



module mem_2r_1w_width4_depth7 #
(
  parameter read_f = 0,
  parameter init_file = "mem_file.txt",
  parameter write_f = 0,
  parameter output_file = "mem_out_file.txt"
)
(
  input clk,
  input [7-1:0] rd_addr0,
  input [7-1:0] rd_addr1,
  output [4-1:0] out0,
  output [4-1:0] out1,
  input wr,
  input [7-1:0] wr_addr,
  input [4-1:0] wr_data
);

  (*rom_style = "block" *) reg [4-1:0] mem[0:2**7-1];
  /*
  reg [4-1:0] mem [0:2**7-1];
  */
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end

  //synthesis translate_off

  always @(posedge clk) begin
    if(wr && write_f) begin
      $writememb(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemb(init_file, mem);
    end 
  end


endmodule



module st4_lcf_6th_16cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [4-1:0] ca_in,
  input [4-1:0] cb_in,
  input [16-1:0] cva_in,
  input [4-1:0] cva_v_in,
  input [16-1:0] cvb_in,
  input [4-1:0] cvb_v_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [4-1:0] lca_out,
  output reg [4-1:0] lcb_out,
  output reg [16-1:0] lcva_out,
  output reg [4-1:0] lcva_v_out,
  output reg [16-1:0] lcvb_out,
  output reg [4-1:0] lcvb_v_out
);

  wire [4-1:0] lca_t;
  wire [4-1:0] lcb_t;
  wire [16-1:0] lcva_t;
  wire [16-1:0] lcvb_t;

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


  lc_table_4_4
  lc_table_4_4_c
  (
    .ca(ca_in),
    .cb(cb_in),
    .lca(lca_t),
    .lcb(lcb_t)
  );


  lc_table_4_4
  lc_table_4_4_v_0
  (
    .ca(cva_in[3:0]),
    .cb(cvb_in[3:0]),
    .lca(lcva_t[3:0]),
    .lcb(lcvb_t[3:0])
  );


  lc_table_4_4
  lc_table_4_4_v_1
  (
    .ca(cva_in[7:4]),
    .cb(cvb_in[7:4]),
    .lca(lcva_t[7:4]),
    .lcb(lcvb_t[7:4])
  );


  lc_table_4_4
  lc_table_4_4_v_2
  (
    .ca(cva_in[11:8]),
    .cb(cvb_in[11:8]),
    .lca(lcva_t[11:8]),
    .lcb(lcvb_t[11:8])
  );


  lc_table_4_4
  lc_table_4_4_v_3
  (
    .ca(cva_in[15:12]),
    .cb(cvb_in[15:12]),
    .lca(lcva_t[15:12]),
    .lcb(lcvb_t[15:12])
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



module lc_table_4_4
(
  input [4-1:0] ca,
  input [4-1:0] cb,
  output [4-1:0] lca,
  output [4-1:0] lcb
);

  wire [4-1:0] lc_table [0:16-1];
  assign lca = lc_table[ca];
  assign lcb = lc_table[cb];
  assign lc_table[0] = { 2'd0, 2'd0 };
  assign lc_table[1] = { 2'd0, 2'd1 };
  assign lc_table[2] = { 2'd0, 2'd2 };
  assign lc_table[3] = { 2'd0, 2'd3 };
  assign lc_table[4] = { 2'd1, 2'd0 };
  assign lc_table[5] = { 2'd1, 2'd1 };
  assign lc_table[6] = { 2'd1, 2'd2 };
  assign lc_table[7] = { 2'd1, 2'd3 };
  assign lc_table[8] = { 2'd2, 2'd0 };
  assign lc_table[9] = { 2'd2, 2'd1 };
  assign lc_table[10] = { 2'd2, 2'd2 };
  assign lc_table[11] = { 2'd2, 2'd3 };
  assign lc_table[12] = { 2'd3, 2'd0 };
  assign lc_table[13] = { 2'd3, 2'd1 };
  assign lc_table[14] = { 2'd3, 2'd2 };
  assign lc_table[15] = { 2'd3, 2'd3 };

endmodule



module st5_d1_6th_16cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [4-1:0] lca_in,
  input [4-1:0] lcb_in,
  input [16-1:0] lcva_in,
  input [4-1:0] lcva_v_in,
  input [16-1:0] lcvb_in,
  input [4-1:0] lcvb_v_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [4-1:0] lca_out,
  output reg [4-1:0] lcb_out,
  output reg [16-1:0] lcva_out,
  output reg [4-1:0] lcva_v_out,
  output reg [16-1:0] lcvb_out,
  output reg [4-1:0] lcvb_v_out,
  output reg [28-1:0] dvac_out,
  output reg [28-1:0] dvbc_out
);

  wire [4-1:0] lcac;
  wire [4-1:0] lcbc;
  wire [28-1:0] dvac_t;
  wire [28-1:0] dvbc_t;
  assign lcac = lca_in;
  assign lcbc = lcb_in;

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    lca_out <= lca_in;
    lcb_out <= lcb_in;
    lcva_out <= lcva_in;
    lcva_v_out <= lcva_v_in;
    lcvb_out <= lcvb_in;
    lcvb_v_out <= lcvb_v_in;
    dvac_out <= dvac_t;
    dvbc_out <= dvbc_t;
  end


  distance_table_4_4
  distance_table_4_4_dac_0
  (
    .opa0(lcac),
    .opa1(lcva_in[3:0]),
    .opav(lcva_v_in[0]),
    .opb0(lcac),
    .opb1(lcva_in[7:4]),
    .opbv(lcva_v_in[1]),
    .da(dvac_t[6:0]),
    .db(dvac_t[13:7])
  );


  distance_table_4_4
  distance_table_4_4_dac_1
  (
    .opa0(lcac),
    .opa1(lcva_in[11:8]),
    .opav(lcva_v_in[2]),
    .opb0(lcac),
    .opb1(lcva_in[15:12]),
    .opbv(lcva_v_in[3]),
    .da(dvac_t[20:14]),
    .db(dvac_t[27:21])
  );


  distance_table_4_4
  distance_table_4_4_dbc_0
  (
    .opa0(lcbc),
    .opa1(lcvb_in[3:0]),
    .opav(lcvb_v_in[0]),
    .opb0(lcbc),
    .opb1(lcvb_in[7:4]),
    .opbv(lcvb_v_in[1]),
    .da(dvbc_t[6:0]),
    .db(dvbc_t[13:7])
  );


  distance_table_4_4
  distance_table_4_4_dbc_1
  (
    .opa0(lcbc),
    .opa1(lcvb_in[11:8]),
    .opav(lcvb_v_in[2]),
    .opb0(lcbc),
    .opb1(lcvb_in[15:12]),
    .opbv(lcvb_v_in[3]),
    .da(dvbc_t[20:14]),
    .db(dvbc_t[27:21])
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
    dvac_out = 0;
    dvbc_out = 0;
  end


endmodule



module distance_table_4_4
(
  input [4-1:0] opa0,
  input [4-1:0] opa1,
  input opav,
  input [4-1:0] opb0,
  input [4-1:0] opb1,
  input opbv,
  output [7-1:0] da,
  output [7-1:0] db
);

  wire [7-1:0] dist_table [0:2**4-1];
  wire [7-1:0] da_t;
  wire [7-1:0] db_t;

  assign da_t = dist_table[{ opa1[1:0], opa0[1:0] }] + dist_table[{ opa1[3:2], opa0[3:2] }];
  assign db_t = dist_table[{ opb1[1:0], opb0[1:0] }] + dist_table[{ opb1[3:2], opb0[3:2] }];

  assign da = (opav)? da_t : 0;
  assign db = (opbv)? db_t : 0;

  assign dist_table[0] = 0;
  assign dist_table[1] = 1;
  assign dist_table[2] = 2;
  assign dist_table[3] = 3;
  assign dist_table[4] = 1;
  assign dist_table[5] = 0;
  assign dist_table[6] = 1;
  assign dist_table[7] = 2;
  assign dist_table[8] = 2;
  assign dist_table[9] = 1;
  assign dist_table[10] = 0;
  assign dist_table[11] = 1;
  assign dist_table[12] = 3;
  assign dist_table[13] = 2;
  assign dist_table[14] = 1;
  assign dist_table[15] = 0;

endmodule



module st6_d2_s1_6th_16cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [4-1:0] lca_in,
  input [4-1:0] lcb_in,
  input [16-1:0] lcva_in,
  input [4-1:0] lcva_v_in,
  input [16-1:0] lcvb_in,
  input [4-1:0] lcvb_v_in,
  input [28-1:0] dvac_in,
  input [28-1:0] dvbc_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [14-1:0] dvac_out,
  output reg [14-1:0] dvbc_out,
  output reg [28-1:0] dvas_out,
  output reg [28-1:0] dvbs_out
);

  wire [4-1:0] lcas;
  wire [4-1:0] lcbs;
  wire [16-1:0] opva;
  wire [16-1:0] opvb;
  wire [14-1:0] dvac_t;
  wire [14-1:0] dvbc_t;
  wire [28-1:0] dvas_t;
  wire [28-1:0] dvbs_t;
  assign lcas = lcb_in;
  assign lcbs = lca_in;
  assign dvac_t[6:0] = dvac_in[6:0] + dvac_in[13:7];
  assign dvac_t[13:7] = dvac_in[20:14] + dvac_in[27:21];
  assign dvbc_t[6:0] = dvbc_in[6:0] + dvbc_in[13:7];
  assign dvbc_t[13:7] = dvbc_in[20:14] + dvbc_in[27:21];
  assign opva[3:0] = (lcva_in[3:0] == lcas)? lcbs : lcva_in[3:0];
  assign opva[7:4] = (lcva_in[7:4] == lcas)? lcbs : lcva_in[7:4];
  assign opva[11:8] = (lcva_in[11:8] == lcas)? lcbs : lcva_in[11:8];
  assign opva[15:12] = (lcva_in[15:12] == lcas)? lcbs : lcva_in[15:12];
  assign opvb[3:0] = (lcvb_in[3:0] == lcbs)? lcas : lcvb_in[3:0];
  assign opvb[7:4] = (lcvb_in[7:4] == lcbs)? lcas : lcvb_in[7:4];
  assign opvb[11:8] = (lcvb_in[11:8] == lcbs)? lcas : lcvb_in[11:8];
  assign opvb[15:12] = (lcvb_in[15:12] == lcbs)? lcas : lcvb_in[15:12];

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    dvac_out <= dvac_t;
    dvbc_out <= dvbc_t;
    dvas_out <= dvas_t;
    dvbs_out <= dvbs_t;
  end


  distance_table_4_4
  distance_table_4_4_das_0
  (
    .opa0(lcas),
    .opa1(opva[3:0]),
    .opav(lcva_v_in[0]),
    .opb0(lcas),
    .opb1(opva[7:4]),
    .opbv(lcva_v_in[1]),
    .da(dvas_t[6:0]),
    .db(dvas_t[13:7])
  );


  distance_table_4_4
  distance_table_4_4_das_1
  (
    .opa0(lcas),
    .opa1(opva[11:8]),
    .opav(lcva_v_in[2]),
    .opb0(lcas),
    .opb1(opva[15:12]),
    .opbv(lcva_v_in[3]),
    .da(dvas_t[20:14]),
    .db(dvas_t[27:21])
  );


  distance_table_4_4
  distance_table_4_4_dbs_0
  (
    .opa0(lcbs),
    .opa1(opvb[3:0]),
    .opav(lcvb_v_in[0]),
    .opb0(lcbs),
    .opb1(opvb[7:4]),
    .opbv(lcvb_v_in[1]),
    .da(dvbs_t[6:0]),
    .db(dvbs_t[13:7])
  );


  distance_table_4_4
  distance_table_4_4_dbs_1
  (
    .opa0(lcbs),
    .opa1(opvb[11:8]),
    .opav(lcvb_v_in[2]),
    .opb0(lcbs),
    .opb1(opvb[15:12]),
    .opbv(lcvb_v_in[3]),
    .da(dvbs_t[20:14]),
    .db(dvbs_t[27:21])
  );


  initial begin
    idx_out = 0;
    v_out = 0;
    dvac_out = 0;
    dvbc_out = 0;
    dvas_out = 0;
    dvbs_out = 0;
  end


endmodule



module st7_s2_6th_16cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [14-1:0] dvac_in,
  input [14-1:0] dvbc_in,
  input [28-1:0] dvas_in,
  input [28-1:0] dvbs_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [7-1:0] dvac_out,
  output reg [7-1:0] dvbc_out,
  output reg [14-1:0] dvas_out,
  output reg [14-1:0] dvbs_out
);

  wire [7-1:0] dvac_t;
  wire [7-1:0] dvbc_t;
  wire [14-1:0] dvas_t;
  wire [14-1:0] dvbs_t;
  assign dvac_t = dvac_in[6:0] + dvac_in[13:7];
  assign dvbc_t = dvbc_in[6:0] + dvbc_in[13:7];
  assign dvas_t[6:0] = dvas_in[6:0] + dvas_in[13:7];
  assign dvas_t[13:7] = dvas_in[20:14] + dvas_in[27:21];
  assign dvbs_t[6:0] = dvbs_in[6:0] + dvbs_in[13:7];
  assign dvbs_t[13:7] = dvbs_in[20:14] + dvbs_in[27:21];

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    dvac_out <= dvac_t;
    dvbc_out <= dvbc_t;
    dvas_out <= dvas_t;
    dvbs_out <= dvbs_t;
  end


  initial begin
    idx_out = 0;
    v_out = 0;
    dvac_out = 0;
    dvbc_out = 0;
    dvas_out = 0;
    dvbs_out = 0;
  end


endmodule



module st8_s3_6th_16cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [7-1:0] dvac_in,
  input [7-1:0] dvbc_in,
  input [14-1:0] dvas_in,
  input [14-1:0] dvbs_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [7-1:0] dc_out,
  output reg [7-1:0] dvas_out,
  output reg [7-1:0] dvbs_out
);

  wire [7-1:0] dc_t;
  wire [7-1:0] dvas_t;
  wire [7-1:0] dvbs_t;
  assign dc_t = dvac_in + dvbc_in;
  assign dvas_t = dvas_in[6:0] + dvas_in[13:7];
  assign dvbs_t = dvbs_in[6:0] + dvbs_in[13:7];

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    dc_out <= dc_t;
    dvas_out <= dvas_t;
    dvbs_out <= dvbs_t;
  end


  initial begin
    idx_out = 0;
    v_out = 0;
    dc_out = 0;
    dvas_out = 0;
    dvbs_out = 0;
  end


endmodule



module st9_s4_6th_16cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [7-1:0] dc_in,
  input [7-1:0] dvas_in,
  input [7-1:0] dvbs_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [7-1:0] dc_out,
  output reg [7-1:0] ds_out
);

  wire [7-1:0] ds_t;
  assign ds_t = dvas_in + dvbs_in;

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    dc_out <= dc_in;
    ds_out <= ds_t;
  end


  initial begin
    idx_out = 0;
    v_out = 0;
    dc_out = 0;
    ds_out = 0;
  end


endmodule



module st10_cmp_6th_16cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [7-1:0] dc_in,
  input [7-1:0] ds_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg sw_out
);

  wire sw_t;
  assign sw_t = ds_in < dc_in;

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    sw_out <= sw_t;
  end


  initial begin
    idx_out = 0;
    v_out = 0;
    sw_out = 0;
  end


endmodule

