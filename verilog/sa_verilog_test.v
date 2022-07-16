

module testbench_sa_pipeline_6threads_4cells
(

);

  reg clk;
  reg rst;
  reg start;
  wire done;

  sa_pipeline_6th_4cells
  sa_pipeline_6th_4cells
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .n_exec(16'd2),
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
    #4000;
    $finish;
  end

  always #5clk=~clk;

endmodule



module sa_pipeline_6th_4cells
(
  input clk,
  input rst,
  input start,
  input [16-1:0] n_exec,
  output reg done
);

  // basic control inputs
  // -----
  wire pipe_start;
  reg [17-1:0] counter_total;
  // Threads controller output wires
  wire [3-1:0] th_idx;
  wire th_v;
  wire [2-1:0] th_ca;
  wire [2-1:0] th_cb;
  // -----

  always @(posedge clk) begin
    if(rst) begin
      counter_total <= 0;
      done <= 0;
    end else begin
      if((th_idx == 5) && ~th_v && &{ th_ca, th_cb }) begin
        counter_total <= counter_total + 1;
      end 
      if(counter_total == n_exec) begin
        done <= 1;
      end 
    end
  end

  // st1 output wires
  wire st1_rdy;
  wire [3-1:0] st1_idx;
  wire st1_v;
  wire [2-1:0] st1_ca;
  wire [2-1:0] st1_cb;
  wire [2-1:0] st1_na;
  wire st1_na_v;
  wire [2-1:0] st1_nb;
  wire st1_nb_v;
  wire st1_sw;
  wire [8-1:0] st1_wa;
  wire [8-1:0] st1_wb;
  // -----
  // st2 output wires
  wire [3-1:0] st2_idx;
  wire st2_v;
  wire [2-1:0] st2_ca;
  wire [2-1:0] st2_cb;
  wire [2-1:0] st2_na;
  wire st2_na_v;
  wire [2-1:0] st2_nb;
  wire st2_nb_v;
  wire [8-1:0] st2_va;
  wire [4-1:0] st2_va_v;
  wire [8-1:0] st2_vb;
  wire [4-1:0] st2_vb_v;
  wire st2_sw;
  wire [8-1:0] st2_wa;
  wire [8-1:0] st2_wb;
  // -----
  // st3 output wires
  wire [3-1:0] st3_idx;
  wire st3_v;
  wire [2-1:0] st3_ca;
  wire [2-1:0] st3_cb;
  wire [8-1:0] st3_cva;
  wire [4-1:0] st3_cva_v;
  wire [8-1:0] st3_cvb;
  wire [4-1:0] st3_cvb_v;
  wire [8-1:0] st3_wb;
  // -----
  // st4 output wires
  wire [3-1:0] st4_idx;
  wire st4_v;
  wire [2-1:0] st4_ca;
  wire [2-1:0] st4_cb;
  wire [8-1:0] st4_cva;
  wire [4-1:0] st4_cva_v;
  wire [8-1:0] st4_cvb;
  wire [4-1:0] st4_cvb_v;
  wire [20-1:0] st4_dvac;
  wire [20-1:0] st4_dvbc;
  // -----
  // st5 output wires
  wire [3-1:0] st5_idx;
  wire st5_v;
  wire [10-1:0] st5_dvac;
  wire [10-1:0] st5_dvbc;
  wire [20-1:0] st5_dvas;
  wire [20-1:0] st5_dvbs;
  // -----
  // st6 output wires
  wire [3-1:0] st6_idx;
  wire st6_v;
  wire [5-1:0] st6_dvac;
  wire [5-1:0] st6_dvbc;
  wire [10-1:0] st6_dvas;
  wire [10-1:0] st6_dvbs;
  // -----
  // st7 output wires
  wire [3-1:0] st7_idx;
  wire st7_v;
  wire [5-1:0] st7_dc;
  wire [5-1:0] st7_dvas;
  wire [5-1:0] st7_dvbs;
  // st8 output wires
  wire [3-1:0] st8_idx;
  wire st8_v;
  wire [5-1:0] st8_dc;
  wire [5-1:0] st8_ds;
  // -----
  // st9 output wires
  wire [3-1:0] st9_idx;
  wire st9_v;
  wire st9_sw;
  // -----
  // st10 output wires
  wire [3-1:0] st10_idx;
  wire st10_v;
  wire st10_sw;
  // -----
  assign pipe_start = &{ start, st1_rdy };

  th_controller_6th_4cells
  th_controller_6th_4cells
  (
    .clk(clk),
    .rst(rst),
    .start(pipe_start),
    .idx_out(th_idx),
    .v_out(th_v),
    .ca_out(th_ca),
    .cb_out(th_cb)
  );


  st1_c2n_6th_4cells
  st1_c2n_6th_4cells
  (
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


  st2_n_6th_4cells
  st2_n_6th_4cells
  (
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


  st3_n2c_6th_4cells
  st3_n2c_6th_4cells
  (
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


  st4_d1_6th_4cells
  st4_d1_6th_4cells
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
    .ca_out(st4_ca),
    .cb_out(st4_cb),
    .cva_out(st4_cva),
    .cva_v_out(st4_cva_v),
    .cvb_out(st4_cvb),
    .cvb_v_out(st4_cvb_v),
    .dvac_out(st4_dvac),
    .dvbc_out(st4_dvbc)
  );


  st5_d2_s1_6th_4cells
  st5_d2_s1_6th_4cells
  (
    .clk(clk),
    .idx_in(st4_idx),
    .v_in(st4_v),
    .ca_in(st4_ca),
    .cb_in(st4_cb),
    .cva_in(st4_cva),
    .cva_v_in(st4_cva_v),
    .cvb_in(st4_cvb),
    .cvb_v_in(st4_cvb_v),
    .dvac_in(st4_dvac),
    .dvbc_in(st4_dvbc),
    .idx_out(st4_idx),
    .v_out(st5_v),
    .dvac_out(st5_dvac),
    .dvbc_out(st5_dvbc),
    .dvas_out(st5_dvas),
    .dvbs_out(st5_dvbs)
  );


  st6_s2_6th_4cells
  st6_s2_6th_4cells
  (
    .clk(clk),
    .idx_in(st5_idx),
    .v_in(st5_v),
    .dvac_in(st5_dvac),
    .dvbc_in(st5_dvbc),
    .dvas_in(st5_dvas),
    .dvbs_in(st5_dvbs),
    .idx_out(st6_idx),
    .v_out(st6_v),
    .dvac_out(st6_dvac),
    .dvbc_out(st6_dvbc),
    .dvas_out(st6_dvas),
    .dvbs_out(st6_dvbs)
  );


  st7_s3_6th_4cells
  st7_s3_6th_4cells
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
    .dc_out(st7_dc),
    .dvas_out(st7_dvas),
    .dvbs_out(st7_dvbs)
  );


  st8_s4_6th_4cells
  st8_s4_6th_4cells
  (
    .clk(clk),
    .idx_in(st7_idx),
    .v_in(st7_v),
    .dc_in(st7_dc),
    .dvas_in(st7_dvas),
    .dvbs_in(st7_dvbs),
    .idx_out(st8_idx),
    .v_out(st8_v),
    .dc_out(st8_dc),
    .ds_out(st8_ds)
  );


  st9_cmp_6th_4cells
  st9_cmp_6th_4cells
  (
    .clk(clk),
    .idx_in(st8_idx),
    .v_in(st8_v),
    .dc_in(st8_dc),
    .ds_in(st8_ds),
    .idx_out(st9_idx),
    .v_out(st9_v),
    .sw_out(st9_sw)
  );


  st10_reg_6th_4cells
  st10_reg_6th_4cells
  (
    .clk(clk),
    .idx_in(st9_idx),
    .v_in(st9_v),
    .sw_in(st9_sw),
    .idx_out(st10_idx),
    .v_out(st10_v),
    .sw_out(st10_sw)
  );


  initial begin
    done = 0;
    counter_total = 0;
  end


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
  #(
    .init_file("../rom/th.rom")
  )
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


  initial begin
    $readmemh(init_file, mem);
  end


endmodule



module st1_c2n_6th_4cells
(
  input clk,
  input rst,
  input [3-1:0] idx_in,
  input v_in,
  input [2-1:0] ca_in,
  input [2-1:0] cb_in,
  input sw_in,
  input [8-1:0] st1_wb_in,
  output reg rdy,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [2-1:0] ca_out,
  output reg [2-1:0] cb_out,
  output reg [2-1:0] na_out,
  output reg na_v_out,
  output reg [2-1:0] nb_out,
  output reg nb_v_out,
  output reg sw_out,
  output reg [8-1:0] wa_out,
  output reg [8-1:0] wb_out
);

  reg flag;
  reg [4-1:0] counter;
  reg fifo_init;
  wire [2-1:0] na_t;
  wire na_v_t;
  wire [2-1:0] nb_t;
  wire nb_v_t;
  wire [8-1:0] wa_t;
  wire [8-1:0] wb_t;
  wire fifoa_wr_en;
  wire fifoa_rd_en;
  wire [8-1:0] fifoa_data;
  wire fifob_wr_en;
  wire fifob_rd_en;
  wire [8-1:0] fifob_data;
  wire [3-1:0] wa_idx;
  wire [2-1:0] wa_c;
  wire [2-1:0] wa_n;
  wire wa_n_v;
  wire [3-1:0] wb_idx;
  wire [2-1:0] wb_c;
  wire [2-1:0] wb_n;
  wire wb_n_v;
  wire m_wr;
  wire [5-1:0] m_wr_addr;
  wire [3-1:0] m_wr_data;
  assign fifoa_data = { idx_in, ca_in, nb_v_t, nb_t };
  assign fifob_data = { idx_in, cb_in, na_v_t, na_t };
  assign fifoa_rd_en = &{ rdy, v_in };
  assign fifob_rd_en = &{ rdy, v_in };
  assign fifoa_wr_en = |{ &{ rdy, v_in }, fifo_init };
  assign fifob_wr_en = |{ &{ rdy, v_in }, fifo_init };
  assign wa_n = wa_t[1:0];
  assign wa_n_v = wa_t[2];
  assign wa_c = wa_t[4:3];
  assign wa_idx = wa_t[7:5];
  assign wb_n = st1_wb_in[1:0];
  assign wb_n_v = st1_wb_in[2];
  assign wb_c = st1_wb_in[4:3];
  assign wb_idx = st1_wb_in[7:5];
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
      if(counter == 3) begin
        rdy <= 1;
        fifo_init <= 0;
      end else begin
        counter <= counter + 1;
        fifo_init <= 1;
      end
    end
  end


  mem_2r_1w_width3_depth5
  #(
    .init_file("../rom/c_n.rom")
  )
  mem_2r_1w_width3_depth5
  (
    .clk(clk),
    .rd_addr0({ idx_in, ca_in }),
    .rd_addr1({ idx_in, cb_in }),
    .out0({ na_v_t, na_t }),
    .out1({ nb_v_t, nb_t }),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  fifo
  #(
    .FIFO_WIDTH(8),
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
    .FIFO_WIDTH(8),
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



module mem_2r_1w_width3_depth5 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input [5-1:0] rd_addr0,
  input [5-1:0] rd_addr1,
  output [3-1:0] out0,
  output [3-1:0] out1,
  input wr,
  input [5-1:0] wr_addr,
  input [3-1:0] wr_data
);

  reg [3-1:0] mem [0:2**5-1];
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end


  initial begin
    $readmemh(init_file, mem);
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
  reg [FIFO_WIDTH-1:0] mem [0:2**FIFO_DEPTH_BITS-1];

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



module st2_n_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [2-1:0] ca_in,
  input [2-1:0] cb_in,
  input [2-1:0] na_in,
  input na_v_in,
  input [2-1:0] nb_in,
  input nb_v_in,
  input sw_in,
  input [8-1:0] wa_in,
  input [8-1:0] wb_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [2-1:0] ca_out,
  output reg [2-1:0] cb_out,
  output reg [2-1:0] na_out,
  output reg na_v_out,
  output reg [2-1:0] nb_out,
  output reg nb_v_out,
  output reg [8-1:0] va_out,
  output reg [4-1:0] va_v_out,
  output reg [8-1:0] vb_out,
  output reg [4-1:0] vb_v_out,
  output reg sw_out,
  output reg [8-1:0] wa_out,
  output reg [8-1:0] wb_out
);

  wire [8-1:0] va_t;
  wire [4-1:0] va_v_t;
  wire [4-1:0] va_v_m;
  wire [8-1:0] vb_t;
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


  mem_2r_1w_width3_depth2
  #(
    .init_file("../rom/n0.rom")
  )
  mem_2r_1w_width3_depth2_0
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[0], va_t[1:0] }),
    .out1({ vb_v_m[0], vb_t[1:0] }),
    .wr(1'b0),
    .wr_addr(2'b0),
    .wr_data(3'b0)
  );


  mem_2r_1w_width3_depth2
  #(
    .init_file("../rom/n1.rom")
  )
  mem_2r_1w_width3_depth2_1
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[1], va_t[3:2] }),
    .out1({ vb_v_m[1], vb_t[3:2] }),
    .wr(1'b0),
    .wr_addr(2'b0),
    .wr_data(3'b0)
  );


  mem_2r_1w_width3_depth2
  #(
    .init_file("../rom/n2.rom")
  )
  mem_2r_1w_width3_depth2_2
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[2], va_t[5:4] }),
    .out1({ vb_v_m[2], vb_t[5:4] }),
    .wr(1'b0),
    .wr_addr(2'b0),
    .wr_data(3'b0)
  );


  mem_2r_1w_width3_depth2
  #(
    .init_file("../rom/n3.rom")
  )
  mem_2r_1w_width3_depth2_3
  (
    .clk(clk),
    .rd_addr0(na_in),
    .rd_addr1(nb_in),
    .out0({ va_v_m[3], va_t[7:6] }),
    .out1({ vb_v_m[3], vb_t[7:6] }),
    .wr(1'b0),
    .wr_addr(2'b0),
    .wr_data(3'b0)
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



module mem_2r_1w_width3_depth2 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input [2-1:0] rd_addr0,
  input [2-1:0] rd_addr1,
  output [3-1:0] out0,
  output [3-1:0] out1,
  input wr,
  input [2-1:0] wr_addr,
  input [3-1:0] wr_data
);

  reg [3-1:0] mem [0:2**2-1];
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end


  initial begin
    $readmemh(init_file, mem);
  end


endmodule



module st3_n2c_6th_4cells
(
  input clk,
  input rst,
  input [3-1:0] idx_in,
  input v_in,
  input [2-1:0] ca_in,
  input [2-1:0] cb_in,
  input [2-1:0] na_in,
  input na_v_in,
  input [2-1:0] nb_in,
  input nb_v_in,
  input [8-1:0] va_in,
  input [4-1:0] va_v_in,
  input [8-1:0] vb_in,
  input [4-1:0] vb_v_in,
  input [8-1:0] st3_wb_in,
  input sw_in,
  input [8-1:0] wa_in,
  input [8-1:0] wb_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [2-1:0] ca_out,
  output reg [2-1:0] cb_out,
  output reg [8-1:0] cva_out,
  output reg [4-1:0] cva_v_out,
  output reg [8-1:0] cvb_out,
  output reg [4-1:0] cvb_v_out,
  output reg [8-1:0] wb_out
);

  reg flag;
  wire [8-1:0] cva_t;
  wire [8-1:0] cvb_t;
  wire [3-1:0] wa_idx;
  wire [2-1:0] wa_c;
  wire [2-1:0] wa_n;
  wire wa_n_v;
  wire [3-1:0] wb_idx;
  wire [2-1:0] wb_c;
  wire [2-1:0] wb_n;
  wire wb_n_v;
  wire m_wr;
  wire [5-1:0] m_wr_addr;
  wire [2-1:0] m_wr_data;
  assign wa_n = wa_in[1:0];
  assign wa_n_v = wa_in[2];
  assign wa_c = wa_in[4:3];
  assign wa_idx = wa_in[7:5];
  assign wb_n = st3_wb_in[1:0];
  assign wb_n_v = st3_wb_in[2];
  assign wb_c = st3_wb_in[4:3];
  assign wb_idx = st3_wb_in[7:5];
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


  mem_2r_1w_width2_depth5
  #(
    .init_file("../rom/n_c.rom")
  )
  mem_2r_1w_width2_depth5_0
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[1:0] }),
    .rd_addr1({ idx_in, vb_in[1:0] }),
    .out0(cva_t[1:0]),
    .out1(cvb_t[1:0]),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  mem_2r_1w_width2_depth5
  #(
    .init_file("../rom/n_c.rom")
  )
  mem_2r_1w_width2_depth5_1
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[3:2] }),
    .rd_addr1({ idx_in, vb_in[3:2] }),
    .out0(cva_t[3:2]),
    .out1(cvb_t[3:2]),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  mem_2r_1w_width2_depth5
  #(
    .init_file("../rom/n_c.rom")
  )
  mem_2r_1w_width2_depth5_2
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[5:4] }),
    .rd_addr1({ idx_in, vb_in[5:4] }),
    .out0(cva_t[5:4]),
    .out1(cvb_t[5:4]),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  mem_2r_1w_width2_depth5
  #(
    .init_file("../rom/n_c.rom")
  )
  mem_2r_1w_width2_depth5_3
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[7:6] }),
    .rd_addr1({ idx_in, vb_in[7:6] }),
    .out0(cva_t[7:6]),
    .out1(cvb_t[7:6]),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
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



module mem_2r_1w_width2_depth5 #
(
  parameter init_file = "mem_file.txt"
)
(
  input clk,
  input [5-1:0] rd_addr0,
  input [5-1:0] rd_addr1,
  output [2-1:0] out0,
  output [2-1:0] out1,
  input wr,
  input [5-1:0] wr_addr,
  input [2-1:0] wr_data
);

  reg [2-1:0] mem [0:2**5-1];
  assign out0 = mem[rd_addr0];
  assign out1 = mem[rd_addr1];

  always @(posedge clk) begin
    if(wr) begin
      mem[wr_addr] <= wr_data;
    end 
  end


  initial begin
    $readmemh(init_file, mem);
  end


endmodule



module st4_d1_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [2-1:0] ca_in,
  input [2-1:0] cb_in,
  input [8-1:0] cva_in,
  input [4-1:0] cva_v_in,
  input [8-1:0] cvb_in,
  input [4-1:0] cvb_v_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [2-1:0] ca_out,
  output reg [2-1:0] cb_out,
  output reg [8-1:0] cva_out,
  output reg [4-1:0] cva_v_out,
  output reg [8-1:0] cvb_out,
  output reg [4-1:0] cvb_v_out,
  output reg [20-1:0] dvac_out,
  output reg [20-1:0] dvbc_out
);

  wire [2-1:0] cac;
  wire [2-1:0] cbc;
  wire [20-1:0] dvac_t;
  wire [20-1:0] dvbc_t;
  assign cac = ca_in;
  assign cbc = cb_in;

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    ca_out <= ca_in;
    cb_out <= cb_in;
    cva_out <= cva_in;
    cva_v_out <= cva_v_in;
    cvb_out <= cvb_in;
    cvb_v_out <= cvb_v_in;
    dvac_out <= dvac_t;
    dvbc_out <= dvbc_t;
  end


  distance_rom_2_2
  distance_rom_2_2_dac_0
  (
    .opa0(cac),
    .opa1(cva_in[1:0]),
    .opav(cva_v_in[0]),
    .opb0(cac),
    .opb1(cva_in[3:2]),
    .opbv(cva_v_in[1]),
    .da(dvac_t[4:0]),
    .db(dvac_t[9:5])
  );


  distance_rom_2_2
  distance_rom_2_2_dac_1
  (
    .opa0(cac),
    .opa1(cva_in[5:4]),
    .opav(cva_v_in[2]),
    .opb0(cac),
    .opb1(cva_in[7:6]),
    .opbv(cva_v_in[3]),
    .da(dvac_t[14:10]),
    .db(dvac_t[19:15])
  );


  distance_rom_2_2
  distance_rom_2_2_dbc_0
  (
    .opa0(cbc),
    .opa1(cvb_in[1:0]),
    .opav(cvb_v_in[0]),
    .opb0(cbc),
    .opb1(cvb_in[3:2]),
    .opbv(cvb_v_in[1]),
    .da(dvbc_t[4:0]),
    .db(dvbc_t[9:5])
  );


  distance_rom_2_2
  distance_rom_2_2_dbc_1
  (
    .opa0(cbc),
    .opa1(cvb_in[5:4]),
    .opav(cvb_v_in[2]),
    .opb0(cbc),
    .opb1(cvb_in[7:6]),
    .opbv(cvb_v_in[3]),
    .da(dvbc_t[14:10]),
    .db(dvbc_t[19:15])
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
    dvac_out = 0;
    dvbc_out = 0;
  end


endmodule



module distance_rom_2_2
(
  input [2-1:0] opa0,
  input [2-1:0] opa1,
  input opav,
  input [2-1:0] opb0,
  input [2-1:0] opb1,
  input opbv,
  output [5-1:0] da,
  output [5-1:0] db
);

  wire [5-1:0] mem [0:4**2-1];
  assign da = (opav)? mem[{ opa1, opa0 }] : 0;
  assign db = (opbv)? mem[{ opb1, opb0 }] : 0;
  assign mem[0] = 5'd0;
  assign mem[1] = 5'd1;
  assign mem[2] = 5'd1;
  assign mem[3] = 5'd2;
  assign mem[4] = 5'd1;
  assign mem[5] = 5'd0;
  assign mem[6] = 5'd2;
  assign mem[7] = 5'd1;
  assign mem[8] = 5'd1;
  assign mem[9] = 5'd2;
  assign mem[10] = 5'd0;
  assign mem[11] = 5'd1;
  assign mem[12] = 5'd2;
  assign mem[13] = 5'd1;
  assign mem[14] = 5'd1;
  assign mem[15] = 5'd0;

endmodule



module st5_d2_s1_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [2-1:0] ca_in,
  input [2-1:0] cb_in,
  input [8-1:0] cva_in,
  input [4-1:0] cva_v_in,
  input [8-1:0] cvb_in,
  input [4-1:0] cvb_v_in,
  input [20-1:0] dvac_in,
  input [20-1:0] dvbc_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [10-1:0] dvac_out,
  output reg [10-1:0] dvbc_out,
  output reg [20-1:0] dvas_out,
  output reg [20-1:0] dvbs_out,
  input [8-1:0] opva,
  input [8-1:0] opvb
);

  wire [2-1:0] cas;
  wire [2-1:0] cbs;
  wire [10-1:0] dvac_t;
  wire [10-1:0] dvbc_t;
  wire [20-1:0] dvas_t;
  wire [20-1:0] dvbs_t;
  assign cas = cb_in;
  assign cbs = ca_in;
  assign dvac_t[4:0] = dvac_in[4:0] + dvac_in[9:5];
  assign dvac_t[9:5] = dvac_in[14:10] + dvac_in[19:15];
  assign dvbc_t[4:0] = dvbc_in[4:0] + dvbc_in[9:5];
  assign dvbc_t[9:5] = dvbc_in[14:10] + dvbc_in[19:15];
  assign opva[1:0] = (cva_in[1:0] == cas)? cbs : cva_in[1:0];
  assign opva[3:2] = (cva_in[3:2] == cas)? cbs : cva_in[3:2];
  assign opva[5:4] = (cva_in[5:4] == cas)? cbs : cva_in[5:4];
  assign opva[7:6] = (cva_in[7:6] == cas)? cbs : cva_in[7:6];

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    dvac_out <= dvac_t;
    dvbc_out <= dvbc_t;
    dvas_out <= dvas_t;
    dvbs_out <= dvbs_t;
  end


  distance_rom_2_2
  distance_rom_2_2_das_0
  (
    .opa0(cas),
    .opa1(opva[1:0]),
    .opav(cva_v_in[0]),
    .opb0(cas),
    .opb1(opva[3:2]),
    .opbv(cva_v_in[1]),
    .da(dvas_t[4:0]),
    .db(dvas_t[9:5])
  );


  distance_rom_2_2
  distance_rom_2_2_das_1
  (
    .opa0(cas),
    .opa1(opva[5:4]),
    .opav(cva_v_in[2]),
    .opb0(cas),
    .opb1(opva[7:6]),
    .opbv(cva_v_in[3]),
    .da(dvas_t[14:10]),
    .db(dvas_t[19:15])
  );


  distance_rom_2_2
  distance_rom_2_2_dbs_0
  (
    .opa0(cbs),
    .opa1(opvb[1:0]),
    .opav(cvb_v_in[0]),
    .opb0(cbs),
    .opb1(opvb[3:2]),
    .opbv(cvb_v_in[1]),
    .da(dvbs_t[4:0]),
    .db(dvbs_t[9:5])
  );


  distance_rom_2_2
  distance_rom_2_2_dbs_1
  (
    .opa0(cbs),
    .opa1(opvb[5:4]),
    .opav(cvb_v_in[2]),
    .opb0(cbs),
    .opb1(opvb[7:6]),
    .opbv(cvb_v_in[3]),
    .da(dvbs_t[14:10]),
    .db(dvbs_t[19:15])
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



module st6_s2_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [10-1:0] dvac_in,
  input [10-1:0] dvbc_in,
  input [20-1:0] dvas_in,
  input [20-1:0] dvbs_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [5-1:0] dvac_out,
  output reg [5-1:0] dvbc_out,
  output reg [10-1:0] dvas_out,
  output reg [10-1:0] dvbs_out
);

  wire [5-1:0] dvac_t;
  wire [5-1:0] dvbc_t;
  wire [10-1:0] dvas_t;
  wire [10-1:0] dvbs_t;
  assign dvac_t = dvac_in[4:0] + dvac_in[9:5];
  assign dvbc_t = dvbc_in[4:0] + dvbc_in[9:5];
  assign dvas_t[4:0] = dvas_in[4:0] + dvas_in[9:5];
  assign dvas_t[9:5] = dvas_in[14:10] + dvas_in[19:15];
  assign dvbs_t[4:0] = dvbs_in[4:0] + dvbs_in[9:5];
  assign dvbs_t[9:5] = dvbs_in[14:10] + dvbs_in[19:15];

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



module st7_s3_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [5-1:0] dvac_in,
  input [5-1:0] dvbc_in,
  input [10-1:0] dvas_in,
  input [10-1:0] dvbs_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [5-1:0] dc_out,
  output reg [5-1:0] dvas_out,
  output reg [5-1:0] dvbs_out
);

  wire [5-1:0] dc_t;
  wire [5-1:0] dvas_t;
  wire [5-1:0] dvbs_t;
  assign dc_t = dvac_in + dvbc_in;
  assign dvas_t = dvas_in[4:0] + dvas_in[9:5];
  assign dvbs_t = dvbs_in[4:0] + dvbs_in[9:5];

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



module st8_s4_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [5-1:0] dc_in,
  input [5-1:0] dvas_in,
  input [5-1:0] dvbs_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [5-1:0] dc_out,
  output reg [5-1:0] ds_out
);

  wire [5-1:0] ds_t;
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



module st9_cmp_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input [5-1:0] dc_in,
  input [5-1:0] ds_in,
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



module st10_reg_6th_4cells
(
  input clk,
  input [3-1:0] idx_in,
  input v_in,
  input sw_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg sw_out
);


  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    sw_out <= sw_in;
  end


  initial begin
    idx_out = 0;
    v_out = 0;
    sw_out = 0;
  end


endmodule

