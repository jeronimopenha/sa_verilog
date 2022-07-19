

module test_bench_sa_acc
(

);

  reg clk;
  reg rst;
  reg start;
  reg sa_aws_done_rd_data;
  reg sa_aws_done_wr_data;
  wire sa_aws_request_read;
  reg sa_aws_read_data_valid;
  reg [16-1:0] sa_aws_read_data;
  reg sa_aws_available_write;
  wire sa_aws_request_write;
  wire [16-1:0] sa_aws_write_data;
  wire sa_aws_done;
  reg [2-1:0] fsm_produce_data;
  localparam fsm_produce = 0;
  localparam fsm_done = 1;

  always @(posedge clk) begin
    if(rst) begin
      start <= 0;
      sa_aws_read_data_valid <= 0;
      sa_aws_done_rd_data <= 0;
      sa_aws_done_wr_data <= 0;
      fsm_produce_data <= fsm_produce;
    end else begin
      start <= 1;
      case(fsm_produce_data)
        fsm_produce: begin
          sa_aws_read_data_valid <= 1;
          sa_aws_read_data <= 16'd1;
          if(sa_aws_request_read && sa_aws_read_data_valid) begin
            sa_aws_read_data_valid <= 0;
            fsm_produce_data <= fsm_done;
          end 
        end
        fsm_done: begin
          sa_aws_done_rd_data <= 1;
        end
      endcase
    end
  end

  reg [8-1:0] rd_counter;
  reg [2-1:0] fsm_consume_data;
  localparam fsm_consume_data_rd = 0;
  localparam fsm_consume_data_show = 1;
  localparam fsm_consume_data_done = 2;

  always @(posedge clk) begin
    if(rst) begin
      rd_counter <= 0;
      sa_aws_available_write <= 0;
      sa_aws_done_wr_data <= 0;
      fsm_consume_data <= fsm_consume_data_rd;
    end else begin
      case(fsm_consume_data)
        fsm_consume_data_rd: begin
          sa_aws_available_write <= 1;
          if(sa_aws_request_write) begin
            rd_counter <= rd_counter + 1;
            $display(sa_aws_write_data);
            if(rd_counter == 127) begin
              sa_aws_available_write <= 0;
              fsm_consume_data <= fsm_consume_data_done;
            end 
          end 
        end
        fsm_consume_data_done: begin
          sa_aws_done_wr_data <= 1;
        end
      endcase
    end
  end


  sa_aws
  sa_aws
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .sa_aws_done_rd_data(sa_aws_done_rd_data),
    .sa_aws_done_wr_data(sa_aws_done_wr_data),
    .sa_aws_request_read(sa_aws_request_read),
    .sa_aws_read_data_valid(sa_aws_read_data_valid),
    .sa_aws_read_data(sa_aws_read_data),
    .sa_aws_available_write(sa_aws_available_write),
    .sa_aws_request_write(sa_aws_request_write),
    .sa_aws_write_data(sa_aws_write_data)
  );


  initial begin
    clk = 0;
    rst = 1;
    start = 0;
    sa_aws_done_rd_data = 0;
    sa_aws_done_wr_data = 0;
    sa_aws_read_data_valid = 0;
    sa_aws_read_data = 0;
    sa_aws_available_write = 0;
    fsm_produce_data = 0;
    rd_counter = 0;
    fsm_consume_data = 0;
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
    #500;
    $finish;
  end

  always #5clk=~clk;

  always @(posedge clk) begin
    if(sa_aws_done) begin
      $display("ACC DONE!");
      $finish;
    end 
  end


  //Simulation sector - End

endmodule



module sa_aws
(
  input clk,
  input rst,
  input start,
  input sa_aws_done_rd_data,
  input sa_aws_done_wr_data,
  output sa_aws_request_read,
  input sa_aws_read_data_valid,
  input [16-1:0] sa_aws_read_data,
  input sa_aws_available_write,
  output reg sa_aws_request_write,
  output reg [16-1:0] sa_aws_write_data,
  output sa_aws_done
);

  assign sa_aws_done = &{ sa_aws_done_wr_data, sa_aws_done_rd_data };
  reg pop_data;
  wire available_pop;
  wire [16-1:0] data_out;
  reg [16-1:0] config_data;
  reg [2-1:0] fms_sd;
  localparam [2-1:0] fsm_sd_idle = 0;
  localparam [2-1:0] fsm_sd_send_data = 1;
  reg flag;
  wire sa_done;
  reg sa_rd;
  reg [5-1:0] sa_rd_addr;
  wire sa_out_v;
  wire [5-1:0] sa_out_data;

  always @(posedge clk) begin
    if(rst) begin
      pop_data <= 0;
      fms_sd <= fsm_sd_idle;
      flag <= 0;
    end else begin
      if(start) begin
        pop_data <= 0;
        flag <= 0;
        case(fms_sd)
          fsm_sd_idle: begin
            if(available_pop) begin
              pop_data <= 1;
              flag <= 1;
              fms_sd <= fsm_sd_send_data;
            end 
          end
          fsm_sd_send_data: begin
            if(available_pop | flag) begin
              config_data <= data_out;
              pop_data <= 1;
            end else begin
              fms_sd <= fsm_sd_idle;
            end
          end
        endcase
      end 
    end
  end


  //Data Consumer - Begin
  reg [2-1:0] fsm_consume;
  localparam fsm_consume_wait = 0;
  localparam fsm_consume_consume = 1;
  localparam fsm_consume_verify = 2;
  localparam fsm_consume_done = 3;

  always @(posedge clk) begin
    if(rst) begin
      sa_rd <= 0;
      sa_rd_addr <= 0;
      sa_aws_request_write <= 0;
      fsm_consume <= fsm_consume_wait;
    end else begin
      sa_rd <= 0;
      sa_aws_request_write <= 0;
      case(fsm_consume)
        fsm_consume_wait: begin
          if(sa_aws_available_write) begin
            if(sa_done) begin
              sa_rd <= 1;
              fsm_consume <= fsm_consume_consume;
            end 
          end 
        end
        fsm_consume_consume: begin
          if(sa_out_v) begin
            sa_aws_write_data <= sa_out_data;
            sa_rd_addr <= sa_rd_addr + 1;
            fsm_consume <= fsm_consume_verify;
          end 
        end
        fsm_consume_verify: begin
          if(sa_rd_addr == 128) begin
            fsm_consume <= fsm_consume_done;
          end else begin
            fsm_consume <= fsm_consume_wait;
          end
        end
        fsm_consume_done: begin
        end
      endcase
    end
  end

  //Data Consumer - Begin
  (* keep_hierarchy = "yes" *)

  fecth_data_16_16
  fecth_data_16_16
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .request_read(sa_aws_request_read),
    .data_valid(sa_aws_read_data_valid),
    .read_data(sa_aws_read_data),
    .pop_data(pop_data),
    .available_pop(available_pop),
    .data_out(data_out)
  );


  sa_pipeline_6th_16cells
  sa_pipeline_6th_16cells
  (
    .clk(clk),
    .rst(rst),
    .start(start),
    .n_exec(config_data),
    .done(sa_done),
    .rd(sa_rd),
    .rd_addr(sa_rd_addr),
    .out_v(sa_out_v),
    .out_data(sa_out_data)
  );


  initial begin
    sa_aws_request_write = 0;
    sa_aws_write_data = 0;
    pop_data = 0;
    config_data = 0;
    fms_sd = 0;
    flag = 0;
    sa_rd = 0;
    sa_rd_addr = 0;
    fsm_consume = 0;
  end


endmodule



module fecth_data_16_16
(
  input clk,
  input start,
  input rst,
  output reg request_read,
  input data_valid,
  input [16-1:0] read_data,
  input pop_data,
  output reg available_pop,
  output [16-1:0] data_out
);

  reg [1-1:0] fsm_read;
  reg [1-1:0] fsm_control;
  reg [16-1:0] data;
  reg [16-1:0] buffer;
  reg [1-1:0] count;
  reg has_buffer;
  reg buffer_read;
  reg en;

  assign data_out = data[15:0];

  always @(posedge clk) begin
    if(rst) begin
      en <= 1'b0;
    end else begin
      en <= (en)? en : start;
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      fsm_read <= 0;
      request_read <= 0;
      has_buffer <= 0;
    end else begin
      request_read <= 0;
      case(fsm_read)
        0: begin
          if(en & data_valid) begin
            buffer <= read_data;
            request_read <= 1;
            has_buffer <= 1;
            fsm_read <= 1;
          end 
        end
        1: begin
          if(buffer_read) begin
            has_buffer <= 0;
            fsm_read <= 0;
          end 
        end
      endcase
    end
  end


  always @(posedge clk) begin
    if(rst) begin
      fsm_control <= 0;
      available_pop <= 0;
      count <= 0;
      buffer_read <= 0;
    end else begin
      buffer_read <= 0;
      case(fsm_control)
        0: begin
          if(has_buffer) begin
            data <= buffer;
            count <= 1;
            buffer_read <= 1;
            available_pop <= 1;
            fsm_control <= 1;
          end 
        end
        1: begin
          if(pop_data & ~count[0]) begin
            count <= count << 1;
            data <= data[15:16];
          end 
          if(pop_data & count[0] & has_buffer) begin
            count <= 1;
            data <= buffer;
            buffer_read <= 1;
          end 
          if(count[0] & pop_data & ~has_buffer) begin
            count <= count << 1;
            data <= data[15:16];
            available_pop <= 0;
            fsm_control <= 0;
          end 
        end
      endcase
    end
  end


  initial begin
    request_read = 0;
    available_pop = 0;
    fsm_read = 0;
    fsm_control = 0;
    data = 0;
    buffer = 0;
    count = 0;
    has_buffer = 0;
    buffer_read = 0;
    en = 0;
  end


endmodule



module sa_pipeline_6th_16cells
(
  input clk,
  input rst,
  input start,
  input [16-1:0] n_exec,
  output reg done,
  input rd,
  input [4-1:0] rd_addr,
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
  wire [4-1:0] st4_ca;
  wire [4-1:0] st4_cb;
  wire [16-1:0] st4_cva;
  wire [4-1:0] st4_cva_v;
  wire [16-1:0] st4_cvb;
  wire [4-1:0] st4_cvb_v;
  wire [28-1:0] st4_dvac;
  wire [28-1:0] st4_dvbc;
  // -----
  // st5 output wires
  wire [3-1:0] st5_idx;
  wire st5_v;
  wire [14-1:0] st5_dvac;
  wire [14-1:0] st5_dvbc;
  wire [28-1:0] st5_dvas;
  wire [28-1:0] st5_dvbs;
  // -----
  // st6 output wires
  wire [3-1:0] st6_idx;
  wire st6_v;
  wire [7-1:0] st6_dvac;
  wire [7-1:0] st6_dvbc;
  wire [14-1:0] st6_dvas;
  wire [14-1:0] st6_dvbs;
  // -----
  // st7 output wires
  wire [3-1:0] st7_idx;
  wire st7_v;
  wire [7-1:0] st7_dc;
  wire [7-1:0] st7_dvas;
  wire [7-1:0] st7_dvbs;
  // st8 output wires
  wire [3-1:0] st8_idx;
  wire st8_v;
  wire [7-1:0] st8_dc;
  wire [7-1:0] st8_ds;
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


  st4_d1_6th_16cells
  st4_d1_6th_16cells
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


  st5_d2_s1_6th_16cells
  st5_d2_s1_6th_16cells
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
    .idx_out(st5_idx),
    .v_out(st5_v),
    .dvac_out(st5_dvac),
    .dvbc_out(st5_dvbc),
    .dvas_out(st5_dvas),
    .dvbs_out(st5_dvbs)
  );


  st6_s2_6th_16cells
  st6_s2_6th_16cells
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


  st7_s3_6th_16cells
  st7_s3_6th_16cells
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


  st8_s4_6th_16cells
  st8_s4_6th_16cells
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


  st9_cmp_6th_16cells
  st9_cmp_6th_16cells
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


  st10_reg_6th_16cells
  st10_reg_6th_16cells
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
    .init_file("./rom/th.rom"),
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

  reg [8-1:0] mem [0:2**3-1];
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
      $writememh(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemh(init_file, mem);
    end 
  end


endmodule



module st1_c2n_6th_16cells
(
  input clk,
  input rst,
  input rd,
  input [4-1:0] rd_addr,
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
    .init_file("./rom/c_n.rom"),
    .read_f(1),
    .write_f(1),
    .output_file("./rom/c_n_out.rom")
  )
  mem_2r_1w_width5_depth7
  (
    .clk(clk),
    .rd_addr0((rd)? rd_addr : { idx_in, ca_in }),
    .rd_addr1({ idx_in, cb_in }),
    .out0({ na_v_t, na_t }),
    .out1({ nb_v_t, nb_t }),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
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

  reg [5-1:0] mem [0:2**7-1];
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
      $writememh(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemh(init_file, mem);
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



module st2_n_6th_16cells
(
  input clk,
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
    .init_file("./rom/n0.rom"),
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
    .wr(1'b0),
    .wr_addr(4'b0),
    .wr_data(5'b0)
  );


  mem_2r_1w_width5_depth4
  #(
    .init_file("./rom/n1.rom"),
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
    .wr(1'b0),
    .wr_addr(4'b0),
    .wr_data(5'b0)
  );


  mem_2r_1w_width5_depth4
  #(
    .init_file("./rom/n2.rom"),
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
    .wr(1'b0),
    .wr_addr(4'b0),
    .wr_data(5'b0)
  );


  mem_2r_1w_width5_depth4
  #(
    .init_file("./rom/n3.rom"),
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
    .wr(1'b0),
    .wr_addr(4'b0),
    .wr_data(5'b0)
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

  reg [5-1:0] mem [0:2**4-1];
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
      $writememh(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemh(init_file, mem);
    end 
  end


endmodule



module st3_n2c_6th_16cells
(
  input clk,
  input rst,
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
    .init_file("./rom/n_c.rom"),
    .read_f(1),
    .write_f(1),
    .output_file("./rom/n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_0
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[3:0] }),
    .rd_addr1({ idx_in, vb_in[3:0] }),
    .out0(cva_t[3:0]),
    .out1(cvb_t[3:0]),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  mem_2r_1w_width4_depth7
  #(
    .init_file("./rom/n_c.rom"),
    .read_f(1),
    .write_f(0),
    .output_file("./rom/n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_1
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[7:4] }),
    .rd_addr1({ idx_in, vb_in[7:4] }),
    .out0(cva_t[7:4]),
    .out1(cvb_t[7:4]),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  mem_2r_1w_width4_depth7
  #(
    .init_file("./rom/n_c.rom"),
    .read_f(1),
    .write_f(0),
    .output_file("./rom/n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_2
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[11:8] }),
    .rd_addr1({ idx_in, vb_in[11:8] }),
    .out0(cva_t[11:8]),
    .out1(cvb_t[11:8]),
    .wr(m_wr),
    .wr_addr(m_wr_addr),
    .wr_data(m_wr_data)
  );


  mem_2r_1w_width4_depth7
  #(
    .init_file("./rom/n_c.rom"),
    .read_f(1),
    .write_f(0),
    .output_file("./rom/n_c_out.rom")
  )
  mem_2r_1w_width4_depth7_3
  (
    .clk(clk),
    .rd_addr0({ idx_in, va_in[15:12] }),
    .rd_addr1({ idx_in, vb_in[15:12] }),
    .out0(cva_t[15:12]),
    .out1(cvb_t[15:12]),
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

  reg [4-1:0] mem [0:2**7-1];
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
      $writememh(output_file, mem);
    end 
  end

  //synthesis translate_on

  initial begin
    if(read_f) begin
      $readmemh(init_file, mem);
    end 
  end


endmodule



module st4_d1_6th_16cells
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
  output reg [4-1:0] ca_out,
  output reg [4-1:0] cb_out,
  output reg [16-1:0] cva_out,
  output reg [4-1:0] cva_v_out,
  output reg [16-1:0] cvb_out,
  output reg [4-1:0] cvb_v_out,
  output reg [28-1:0] dvac_out,
  output reg [28-1:0] dvbc_out
);

  wire [4-1:0] cac;
  wire [4-1:0] cbc;
  wire [28-1:0] dvac_t;
  wire [28-1:0] dvbc_t;
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


  distance_rom_4_4
  distance_rom_4_4_dac_0
  (
    .opa0(cac),
    .opa1(cva_in[3:0]),
    .opav(cva_v_in[0]),
    .opb0(cac),
    .opb1(cva_in[7:4]),
    .opbv(cva_v_in[1]),
    .da(dvac_t[6:0]),
    .db(dvac_t[13:7])
  );


  distance_rom_4_4
  distance_rom_4_4_dac_1
  (
    .opa0(cac),
    .opa1(cva_in[11:8]),
    .opav(cva_v_in[2]),
    .opb0(cac),
    .opb1(cva_in[15:12]),
    .opbv(cva_v_in[3]),
    .da(dvac_t[20:14]),
    .db(dvac_t[27:21])
  );


  distance_rom_4_4
  distance_rom_4_4_dbc_0
  (
    .opa0(cbc),
    .opa1(cvb_in[3:0]),
    .opav(cvb_v_in[0]),
    .opb0(cbc),
    .opb1(cvb_in[7:4]),
    .opbv(cvb_v_in[1]),
    .da(dvbc_t[6:0]),
    .db(dvbc_t[13:7])
  );


  distance_rom_4_4
  distance_rom_4_4_dbc_1
  (
    .opa0(cbc),
    .opa1(cvb_in[11:8]),
    .opav(cvb_v_in[2]),
    .opb0(cbc),
    .opb1(cvb_in[15:12]),
    .opbv(cvb_v_in[3]),
    .da(dvbc_t[20:14]),
    .db(dvbc_t[27:21])
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



module distance_rom_4_4
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

  wire [7-1:0] mem [0:16**2-1];
  assign da = (opav)? mem[{ opa1, opa0 }] : 0;
  assign db = (opbv)? mem[{ opb1, opb0 }] : 0;
  assign mem[0] = 7'd0;
  assign mem[1] = 7'd1;
  assign mem[2] = 7'd2;
  assign mem[3] = 7'd3;
  assign mem[4] = 7'd1;
  assign mem[5] = 7'd2;
  assign mem[6] = 7'd3;
  assign mem[7] = 7'd4;
  assign mem[8] = 7'd2;
  assign mem[9] = 7'd3;
  assign mem[10] = 7'd4;
  assign mem[11] = 7'd5;
  assign mem[12] = 7'd3;
  assign mem[13] = 7'd4;
  assign mem[14] = 7'd5;
  assign mem[15] = 7'd6;
  assign mem[16] = 7'd1;
  assign mem[17] = 7'd0;
  assign mem[18] = 7'd1;
  assign mem[19] = 7'd2;
  assign mem[20] = 7'd2;
  assign mem[21] = 7'd1;
  assign mem[22] = 7'd2;
  assign mem[23] = 7'd3;
  assign mem[24] = 7'd3;
  assign mem[25] = 7'd2;
  assign mem[26] = 7'd3;
  assign mem[27] = 7'd4;
  assign mem[28] = 7'd4;
  assign mem[29] = 7'd3;
  assign mem[30] = 7'd4;
  assign mem[31] = 7'd5;
  assign mem[32] = 7'd2;
  assign mem[33] = 7'd1;
  assign mem[34] = 7'd0;
  assign mem[35] = 7'd1;
  assign mem[36] = 7'd3;
  assign mem[37] = 7'd2;
  assign mem[38] = 7'd1;
  assign mem[39] = 7'd2;
  assign mem[40] = 7'd4;
  assign mem[41] = 7'd3;
  assign mem[42] = 7'd2;
  assign mem[43] = 7'd3;
  assign mem[44] = 7'd5;
  assign mem[45] = 7'd4;
  assign mem[46] = 7'd3;
  assign mem[47] = 7'd4;
  assign mem[48] = 7'd3;
  assign mem[49] = 7'd2;
  assign mem[50] = 7'd1;
  assign mem[51] = 7'd0;
  assign mem[52] = 7'd4;
  assign mem[53] = 7'd3;
  assign mem[54] = 7'd2;
  assign mem[55] = 7'd1;
  assign mem[56] = 7'd5;
  assign mem[57] = 7'd4;
  assign mem[58] = 7'd3;
  assign mem[59] = 7'd2;
  assign mem[60] = 7'd6;
  assign mem[61] = 7'd5;
  assign mem[62] = 7'd4;
  assign mem[63] = 7'd3;
  assign mem[64] = 7'd1;
  assign mem[65] = 7'd2;
  assign mem[66] = 7'd3;
  assign mem[67] = 7'd4;
  assign mem[68] = 7'd0;
  assign mem[69] = 7'd1;
  assign mem[70] = 7'd2;
  assign mem[71] = 7'd3;
  assign mem[72] = 7'd1;
  assign mem[73] = 7'd2;
  assign mem[74] = 7'd3;
  assign mem[75] = 7'd4;
  assign mem[76] = 7'd2;
  assign mem[77] = 7'd3;
  assign mem[78] = 7'd4;
  assign mem[79] = 7'd5;
  assign mem[80] = 7'd2;
  assign mem[81] = 7'd1;
  assign mem[82] = 7'd2;
  assign mem[83] = 7'd3;
  assign mem[84] = 7'd1;
  assign mem[85] = 7'd0;
  assign mem[86] = 7'd1;
  assign mem[87] = 7'd2;
  assign mem[88] = 7'd2;
  assign mem[89] = 7'd1;
  assign mem[90] = 7'd2;
  assign mem[91] = 7'd3;
  assign mem[92] = 7'd3;
  assign mem[93] = 7'd2;
  assign mem[94] = 7'd3;
  assign mem[95] = 7'd4;
  assign mem[96] = 7'd3;
  assign mem[97] = 7'd2;
  assign mem[98] = 7'd1;
  assign mem[99] = 7'd2;
  assign mem[100] = 7'd2;
  assign mem[101] = 7'd1;
  assign mem[102] = 7'd0;
  assign mem[103] = 7'd1;
  assign mem[104] = 7'd3;
  assign mem[105] = 7'd2;
  assign mem[106] = 7'd1;
  assign mem[107] = 7'd2;
  assign mem[108] = 7'd4;
  assign mem[109] = 7'd3;
  assign mem[110] = 7'd2;
  assign mem[111] = 7'd3;
  assign mem[112] = 7'd4;
  assign mem[113] = 7'd3;
  assign mem[114] = 7'd2;
  assign mem[115] = 7'd1;
  assign mem[116] = 7'd3;
  assign mem[117] = 7'd2;
  assign mem[118] = 7'd1;
  assign mem[119] = 7'd0;
  assign mem[120] = 7'd4;
  assign mem[121] = 7'd3;
  assign mem[122] = 7'd2;
  assign mem[123] = 7'd1;
  assign mem[124] = 7'd5;
  assign mem[125] = 7'd4;
  assign mem[126] = 7'd3;
  assign mem[127] = 7'd2;
  assign mem[128] = 7'd2;
  assign mem[129] = 7'd3;
  assign mem[130] = 7'd4;
  assign mem[131] = 7'd5;
  assign mem[132] = 7'd1;
  assign mem[133] = 7'd2;
  assign mem[134] = 7'd3;
  assign mem[135] = 7'd4;
  assign mem[136] = 7'd0;
  assign mem[137] = 7'd1;
  assign mem[138] = 7'd2;
  assign mem[139] = 7'd3;
  assign mem[140] = 7'd1;
  assign mem[141] = 7'd2;
  assign mem[142] = 7'd3;
  assign mem[143] = 7'd4;
  assign mem[144] = 7'd3;
  assign mem[145] = 7'd2;
  assign mem[146] = 7'd3;
  assign mem[147] = 7'd4;
  assign mem[148] = 7'd2;
  assign mem[149] = 7'd1;
  assign mem[150] = 7'd2;
  assign mem[151] = 7'd3;
  assign mem[152] = 7'd1;
  assign mem[153] = 7'd0;
  assign mem[154] = 7'd1;
  assign mem[155] = 7'd2;
  assign mem[156] = 7'd2;
  assign mem[157] = 7'd1;
  assign mem[158] = 7'd2;
  assign mem[159] = 7'd3;
  assign mem[160] = 7'd4;
  assign mem[161] = 7'd3;
  assign mem[162] = 7'd2;
  assign mem[163] = 7'd3;
  assign mem[164] = 7'd3;
  assign mem[165] = 7'd2;
  assign mem[166] = 7'd1;
  assign mem[167] = 7'd2;
  assign mem[168] = 7'd2;
  assign mem[169] = 7'd1;
  assign mem[170] = 7'd0;
  assign mem[171] = 7'd1;
  assign mem[172] = 7'd3;
  assign mem[173] = 7'd2;
  assign mem[174] = 7'd1;
  assign mem[175] = 7'd2;
  assign mem[176] = 7'd5;
  assign mem[177] = 7'd4;
  assign mem[178] = 7'd3;
  assign mem[179] = 7'd2;
  assign mem[180] = 7'd4;
  assign mem[181] = 7'd3;
  assign mem[182] = 7'd2;
  assign mem[183] = 7'd1;
  assign mem[184] = 7'd3;
  assign mem[185] = 7'd2;
  assign mem[186] = 7'd1;
  assign mem[187] = 7'd0;
  assign mem[188] = 7'd4;
  assign mem[189] = 7'd3;
  assign mem[190] = 7'd2;
  assign mem[191] = 7'd1;
  assign mem[192] = 7'd3;
  assign mem[193] = 7'd4;
  assign mem[194] = 7'd5;
  assign mem[195] = 7'd6;
  assign mem[196] = 7'd2;
  assign mem[197] = 7'd3;
  assign mem[198] = 7'd4;
  assign mem[199] = 7'd5;
  assign mem[200] = 7'd1;
  assign mem[201] = 7'd2;
  assign mem[202] = 7'd3;
  assign mem[203] = 7'd4;
  assign mem[204] = 7'd0;
  assign mem[205] = 7'd1;
  assign mem[206] = 7'd2;
  assign mem[207] = 7'd3;
  assign mem[208] = 7'd4;
  assign mem[209] = 7'd3;
  assign mem[210] = 7'd4;
  assign mem[211] = 7'd5;
  assign mem[212] = 7'd3;
  assign mem[213] = 7'd2;
  assign mem[214] = 7'd3;
  assign mem[215] = 7'd4;
  assign mem[216] = 7'd2;
  assign mem[217] = 7'd1;
  assign mem[218] = 7'd2;
  assign mem[219] = 7'd3;
  assign mem[220] = 7'd1;
  assign mem[221] = 7'd0;
  assign mem[222] = 7'd1;
  assign mem[223] = 7'd2;
  assign mem[224] = 7'd5;
  assign mem[225] = 7'd4;
  assign mem[226] = 7'd3;
  assign mem[227] = 7'd4;
  assign mem[228] = 7'd4;
  assign mem[229] = 7'd3;
  assign mem[230] = 7'd2;
  assign mem[231] = 7'd3;
  assign mem[232] = 7'd3;
  assign mem[233] = 7'd2;
  assign mem[234] = 7'd1;
  assign mem[235] = 7'd2;
  assign mem[236] = 7'd2;
  assign mem[237] = 7'd1;
  assign mem[238] = 7'd0;
  assign mem[239] = 7'd1;
  assign mem[240] = 7'd6;
  assign mem[241] = 7'd5;
  assign mem[242] = 7'd4;
  assign mem[243] = 7'd3;
  assign mem[244] = 7'd5;
  assign mem[245] = 7'd4;
  assign mem[246] = 7'd3;
  assign mem[247] = 7'd2;
  assign mem[248] = 7'd4;
  assign mem[249] = 7'd3;
  assign mem[250] = 7'd2;
  assign mem[251] = 7'd1;
  assign mem[252] = 7'd3;
  assign mem[253] = 7'd2;
  assign mem[254] = 7'd1;
  assign mem[255] = 7'd0;

endmodule



module st5_d2_s1_6th_16cells
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
  input [28-1:0] dvac_in,
  input [28-1:0] dvbc_in,
  output reg [3-1:0] idx_out,
  output reg v_out,
  output reg [14-1:0] dvac_out,
  output reg [14-1:0] dvbc_out,
  output reg [28-1:0] dvas_out,
  output reg [28-1:0] dvbs_out
);

  wire [4-1:0] cas;
  wire [4-1:0] cbs;
  wire [16-1:0] opva;
  wire [16-1:0] opvb;
  wire [14-1:0] dvac_t;
  wire [14-1:0] dvbc_t;
  wire [28-1:0] dvas_t;
  wire [28-1:0] dvbs_t;
  assign cas = cb_in;
  assign cbs = ca_in;
  assign dvac_t[6:0] = dvac_in[6:0] + dvac_in[13:7];
  assign dvac_t[13:7] = dvac_in[20:14] + dvac_in[27:21];
  assign dvbc_t[6:0] = dvbc_in[6:0] + dvbc_in[13:7];
  assign dvbc_t[13:7] = dvbc_in[20:14] + dvbc_in[27:21];
  assign opva[3:0] = (cva_in[3:0] == cas)? cbs : cva_in[3:0];
  assign opva[7:4] = (cva_in[7:4] == cas)? cbs : cva_in[7:4];
  assign opva[11:8] = (cva_in[11:8] == cas)? cbs : cva_in[11:8];
  assign opva[15:12] = (cva_in[15:12] == cas)? cbs : cva_in[15:12];
  assign opvb[3:0] = (cvb_in[3:0] == cbs)? cas : cvb_in[3:0];
  assign opvb[7:4] = (cvb_in[7:4] == cbs)? cas : cvb_in[7:4];
  assign opvb[11:8] = (cvb_in[11:8] == cbs)? cas : cvb_in[11:8];
  assign opvb[15:12] = (cvb_in[15:12] == cbs)? cas : cvb_in[15:12];

  always @(posedge clk) begin
    idx_out <= idx_in;
    v_out <= v_in;
    dvac_out <= dvac_t;
    dvbc_out <= dvbc_t;
    dvas_out <= dvas_t;
    dvbs_out <= dvbs_t;
  end


  distance_rom_4_4
  distance_rom_4_4_das_0
  (
    .opa0(cas),
    .opa1(opva[3:0]),
    .opav(cva_v_in[0]),
    .opb0(cas),
    .opb1(opva[7:4]),
    .opbv(cva_v_in[1]),
    .da(dvas_t[6:0]),
    .db(dvas_t[13:7])
  );


  distance_rom_4_4
  distance_rom_4_4_das_1
  (
    .opa0(cas),
    .opa1(opva[11:8]),
    .opav(cva_v_in[2]),
    .opb0(cas),
    .opb1(opva[15:12]),
    .opbv(cva_v_in[3]),
    .da(dvas_t[20:14]),
    .db(dvas_t[27:21])
  );


  distance_rom_4_4
  distance_rom_4_4_dbs_0
  (
    .opa0(cbs),
    .opa1(opvb[3:0]),
    .opav(cvb_v_in[0]),
    .opb0(cbs),
    .opb1(opvb[7:4]),
    .opbv(cvb_v_in[1]),
    .da(dvbs_t[6:0]),
    .db(dvbs_t[13:7])
  );


  distance_rom_4_4
  distance_rom_4_4_dbs_1
  (
    .opa0(cbs),
    .opa1(opvb[11:8]),
    .opav(cvb_v_in[2]),
    .opb0(cbs),
    .opb1(opvb[15:12]),
    .opbv(cvb_v_in[3]),
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



module st6_s2_6th_16cells
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



module st7_s3_6th_16cells
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



module st8_s4_6th_16cells
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



module st9_cmp_6th_16cells
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



module st10_reg_6th_16cells
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

