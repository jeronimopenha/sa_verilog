

module sa_64 #
(
  parameter C_S_AXI_CONTROL_ADDR_WIDTH = 12,
  parameter C_S_AXI_CONTROL_DATA_WIDTH = 32,
  parameter C_M_AXI_ADDR_WIDTH = 64,
  parameter C_M_AXI_DATA_WIDTH = 16
)
(
  input ap_clk,
  input ap_rst_n,
  input s_axi_control_awvalid,
  output s_axi_control_awready,
  input [C_S_AXI_CONTROL_ADDR_WIDTH-1:0] s_axi_control_awaddr,
  input s_axi_control_wvalid,
  output s_axi_control_wready,
  input [C_S_AXI_CONTROL_DATA_WIDTH-1:0] s_axi_control_wdata,
  input [C_S_AXI_CONTROL_DATA_WIDTH/8-1:0] s_axi_control_wstrb,
  input s_axi_control_arvalid,
  output s_axi_control_arready,
  input [C_S_AXI_CONTROL_ADDR_WIDTH-1:0] s_axi_control_araddr,
  output s_axi_control_rvalid,
  input s_axi_control_rready,
  output [C_S_AXI_CONTROL_DATA_WIDTH-1:0] s_axi_control_rdata,
  output [2-1:0] s_axi_control_rresp,
  output s_axi_control_bvalid,
  input s_axi_control_bready,
  output [2-1:0] s_axi_control_bresp,
  output interrupt,
  output m00_axi_awvalid,
  input m00_axi_awready,
  output [C_M_AXI_ADDR_WIDTH-1:0] m00_axi_awaddr,
  output [8-1:0] m00_axi_awlen,
  output m00_axi_wvalid,
  input m00_axi_wready,
  output [C_M_AXI_DATA_WIDTH-1:0] m00_axi_wdata,
  output [C_M_AXI_DATA_WIDTH/8-1:0] m00_axi_wstrb,
  output m00_axi_wlast,
  input m00_axi_bvalid,
  output m00_axi_bready,
  output m00_axi_arvalid,
  input m00_axi_arready,
  output [C_M_AXI_ADDR_WIDTH-1:0] m00_axi_araddr,
  output [8-1:0] m00_axi_arlen,
  input m00_axi_rvalid,
  output m00_axi_rready,
  input [C_M_AXI_DATA_WIDTH-1:0] m00_axi_rdata,
  input m00_axi_rlast
);

  (* DONT_TOUCH = "yes" *)
  reg areset;
  wire ap_start;
  wire ap_idle;
  wire ap_done;
  wire ap_ready;
  wire [32-1:0] in_s0;
  wire [32-1:0] out_s0;
  wire [64-1:0] in0;
  wire [64-1:0] out0;

  always @(posedge ap_clk) begin
    areset <= ~ap_rst_n;
  end

  (* keep_hierarchy = "yes" *)

  control_s_axi_1
  #(
    .C_S_AXI_ADDR_WIDTH(C_S_AXI_CONTROL_ADDR_WIDTH),
    .C_S_AXI_DATA_WIDTH(C_S_AXI_CONTROL_DATA_WIDTH)
  )
  control_s_axi_inst
  (
    .aclk(ap_clk),
    .areset(areset),
    .aclk_en(1'b1),
    .awvalid(s_axi_control_awvalid),
    .awready(s_axi_control_awready),
    .awaddr(s_axi_control_awaddr),
    .wvalid(s_axi_control_wvalid),
    .wready(s_axi_control_wready),
    .wdata(s_axi_control_wdata),
    .wstrb(s_axi_control_wstrb),
    .arvalid(s_axi_control_arvalid),
    .arready(s_axi_control_arready),
    .araddr(s_axi_control_araddr),
    .rvalid(s_axi_control_rvalid),
    .rready(s_axi_control_rready),
    .rdata(s_axi_control_rdata),
    .rresp(s_axi_control_rresp),
    .bvalid(s_axi_control_bvalid),
    .bready(s_axi_control_bready),
    .bresp(s_axi_control_bresp),
    .interrupt(interrupt),
    .ap_start(ap_start),
    .ap_done(ap_done),
    .ap_ready(ap_ready),
    .ap_idle(ap_idle),
    .in_s0(in_s0),
    .out_s0(out_s0),
    .in0(in0),
    .out0(out0)
  );

  (* keep_hierarchy = "yes" *)

  app_top
  #(
    .C_M_AXI_ADDR_WIDTH(C_M_AXI_ADDR_WIDTH),
    .C_M_AXI_DATA_WIDTH(C_M_AXI_DATA_WIDTH)
  )
  app_inst
  (
    .ap_clk(ap_clk),
    .ap_rst_n(ap_rst_n),
    .ap_start(ap_start),
    .ap_done(ap_done),
    .ap_idle(ap_idle),
    .ap_ready(ap_ready),
    .in_s0(in_s0),
    .out_s0(out_s0),
    .in0(in0),
    .out0(out0),
    .m00_axi_awvalid(m00_axi_awvalid),
    .m00_axi_awready(m00_axi_awready),
    .m00_axi_awaddr(m00_axi_awaddr),
    .m00_axi_awlen(m00_axi_awlen),
    .m00_axi_wvalid(m00_axi_wvalid),
    .m00_axi_wready(m00_axi_wready),
    .m00_axi_wdata(m00_axi_wdata),
    .m00_axi_wstrb(m00_axi_wstrb),
    .m00_axi_wlast(m00_axi_wlast),
    .m00_axi_bvalid(m00_axi_bvalid),
    .m00_axi_bready(m00_axi_bready),
    .m00_axi_arvalid(m00_axi_arvalid),
    .m00_axi_arready(m00_axi_arready),
    .m00_axi_araddr(m00_axi_araddr),
    .m00_axi_arlen(m00_axi_arlen),
    .m00_axi_rvalid(m00_axi_rvalid),
    .m00_axi_rready(m00_axi_rready),
    .m00_axi_rdata(m00_axi_rdata),
    .m00_axi_rlast(m00_axi_rlast)
  );


  initial begin
    areset = 1'b1;
  end


endmodule



module control_s_axi_1 #
(
  parameter C_S_AXI_ADDR_WIDTH = 6,
  parameter C_S_AXI_DATA_WIDTH = 32
)
(
  input aclk,
  input areset,
  input aclk_en,
  input [C_S_AXI_ADDR_WIDTH-1:0] awaddr,
  input awvalid,
  output awready,
  input [C_S_AXI_DATA_WIDTH-1:0] wdata,
  input [C_S_AXI_DATA_WIDTH/8-1:0] wstrb,
  input wvalid,
  output wready,
  output [2-1:0] bresp,
  output bvalid,
  input bready,
  input [C_S_AXI_ADDR_WIDTH-1:0] araddr,
  input arvalid,
  output arready,
  output [C_S_AXI_DATA_WIDTH-1:0] rdata,
  output [2-1:0] rresp,
  output rvalid,
  input rready,
  output interrupt,
  output ap_start,
  input ap_done,
  input ap_ready,
  input ap_idle,
  output [32-1:0] in_s0,
  output [32-1:0] out_s0,
  output [64-1:0] in0,
  output [64-1:0] out0
);

  localparam ADDR_AP_CTRL = 6'h0;
  localparam ADDR_GIE = 6'h4;
  localparam ADDR_IER = 6'h8;
  localparam ADDR_ISR = 6'hc;
  localparam ADDR_IN_S0_DATA_0 = 6'h10;
  localparam ADDR_IN_S0_CTRL = 6'h14;
  localparam ADDR_OUT_S0_DATA_0 = 6'h18;
  localparam ADDR_OUT_S0_CTRL = 6'h1c;
  localparam ADDR_IN0_DATA_0 = 6'h20;
  localparam ADDR_IN0_DATA_1 = 6'h24;
  localparam ADDR_IN0_CTRL = 6'h28;
  localparam ADDR_OUT0_DATA_0 = 6'h2c;
  localparam ADDR_OUT0_DATA_1 = 6'h30;
  localparam ADDR_OUT0_CTRL = 6'h34;
  localparam WRIDLE = 2'd0;
  localparam WRDATA = 2'd1;
  localparam WRRESP = 2'd2;
  localparam WRRESET = 2'd3;
  localparam RDIDLE = 2'd0;
  localparam RDDATA = 2'd1;
  localparam RDRESET = 2'd2;
  localparam ADDR_BITS = 6;
  reg [2-1:0] wstate;
  reg [2-1:0] wnext;
  reg [ADDR_BITS-1:0] waddr;
  wire [32-1:0] wmask;
  wire aw_hs;
  wire w_hs;
  reg [2-1:0] rstate;
  reg [2-1:0] rnext;
  reg [32-1:0] rrdata;
  wire ar_hs;
  wire [ADDR_BITS-1:0] raddr;
  reg int_ap_idle;
  reg int_ap_ready;
  reg int_ap_done;
  reg int_ap_start;
  reg int_auto_restart;
  reg int_gie;
  reg [2-1:0] int_ier;
  reg [2-1:0] int_isr;
  reg [32-1:0] int_in_s0;
  reg [32-1:0] int_out_s0;
  reg [64-1:0] int_in0;
  reg [64-1:0] int_out0;
  assign awready = wstate == WRIDLE;
  assign wready = wstate == WRDATA;
  assign bresp = 2'b0;
  assign bvalid = wstate == WRRESP;
  assign wmask = { { 8{ wstrb[3] } }, { 8{ wstrb[2] } }, { 8{ wstrb[1] } }, { 8{ wstrb[0] } } };
  assign aw_hs = awvalid & awready;
  assign w_hs = wvalid & wready;

  always @(posedge aclk) begin
    if(areset) begin
      wstate <= WRRESET;
    end else begin
      if(aclk_en) begin
        wstate <= wnext;
      end
    end
  end


  always @(*) begin
    case(wstate)
      WRIDLE: begin
        if(awvalid) begin
          wnext <= WRDATA;
        end else begin
          wnext <= WRIDLE;
        end
      end
      WRDATA: begin
        if(wvalid) begin
          wnext <= WRRESP;
        end else begin
          wnext <= WRDATA;
        end
      end
      WRRESP: begin
        if(bready) begin
          wnext <= WRIDLE;
        end else begin
          wnext <= WRRESP;
        end
      end
      default: begin
        wnext <= WRIDLE;
      end
    endcase
  end


  always @(posedge aclk) begin
    if(aclk_en) begin
      if(aw_hs) begin
        waddr <= awaddr[ADDR_BITS-1:0];
      end
    end
  end

  assign arready = rstate == RDIDLE;
  assign rdata = rrdata;
  assign rresp = 2'b0;
  assign rvalid = rstate == RDDATA;
  assign ar_hs = arvalid & arready;
  assign raddr = araddr[ADDR_BITS-1:0];

  always @(posedge aclk) begin
    if(areset) begin
      rstate <= RDRESET;
    end else begin
      if(aclk_en) begin
        rstate <= rnext;
      end
    end
  end


  always @(*) begin
    case(rstate)
      RDIDLE: begin
        if(arvalid) begin
          rnext <= RDDATA;
        end else begin
          rnext <= RDIDLE;
        end
      end
      RDDATA: begin
        if(rready & rvalid) begin
          rnext <= RDIDLE;
        end else begin
          rnext <= RDDATA;
        end
      end
      default: begin
        rnext <= RDIDLE;
      end
    endcase
  end


  always @(posedge aclk) begin
    if(aclk_en) begin
      if(ar_hs) begin
        rrdata <= 1'b0;
        case(raddr)
          ADDR_AP_CTRL: begin
            rrdata[0] <= int_ap_start;
            rrdata[1] <= int_ap_done;
            rrdata[2] <= int_ap_idle;
            rrdata[3] <= int_ap_ready;
            rrdata[7] <= int_auto_restart;
          end
          ADDR_GIE: begin
            rrdata <= int_gie;
          end
          ADDR_IER: begin
            rrdata <= int_ier;
          end
          ADDR_ISR: begin
            rrdata <= int_isr;
          end
          ADDR_IN_S0_DATA_0: begin
            rrdata <= int_in_s0[31:0];
          end
          ADDR_OUT_S0_DATA_0: begin
            rrdata <= int_out_s0[31:0];
          end
          ADDR_IN0_DATA_0: begin
            rrdata <= int_in0[31:0];
          end
          ADDR_IN0_DATA_1: begin
            rrdata <= int_in0[63:32];
          end
          ADDR_OUT0_DATA_0: begin
            rrdata <= int_out0[31:0];
          end
          ADDR_OUT0_DATA_1: begin
            rrdata <= int_out0[63:32];
          end
        endcase
      end
    end
  end

  assign interrupt = int_gie & |int_isr;
  assign ap_start = int_ap_start;
  assign in_s0 = int_in_s0;
  assign out_s0 = int_out_s0;
  assign in0 = int_in0;
  assign out0 = int_out0;

  always @(posedge aclk) begin
    if(areset) begin
      int_ap_start <= 1'b0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_AP_CTRL) && wstrb[0] && wdata[0]) begin
          int_ap_start <= 1'b1;
        end else if(ap_ready) begin
          int_ap_start <= int_auto_restart;
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_ap_done <= 1'b0;
    end else begin
      if(aclk_en) begin
        if(ap_done) begin
          int_ap_done <= 1'b1;
        end else if(ar_hs && (raddr == ADDR_AP_CTRL)) begin
          int_ap_done <= 1'b0;
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_ap_idle <= 1'b1;
    end else begin
      if(aclk_en) begin
        int_ap_idle <= ap_idle;
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_ap_ready <= 1'b0;
    end else begin
      if(aclk_en) begin
        int_ap_ready <= ap_ready;
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_auto_restart <= 1'b0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_AP_CTRL) && wstrb[0]) begin
          int_auto_restart <= wdata[7];
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_gie <= 1'b0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_GIE) && wstrb[0]) begin
          int_gie <= wdata[0];
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_ier <= 2'b0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_IER) && wstrb[0]) begin
          int_ier <= wdata[1:0];
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_isr[0] <= 1'b0;
    end else begin
      if(aclk_en) begin
        if(int_ier[0] & ap_done) begin
          int_isr[0] <= 1'b1;
        end else if(w_hs && (waddr == ADDR_ISR) && wstrb[0]) begin
          int_isr[0] <= int_isr[0] ^ wdata[0];
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_isr[1] <= 1'b0;
    end else begin
      if(aclk_en) begin
        if(int_ier[1] & ap_ready) begin
          int_isr[1] <= 1'b1;
        end else if(w_hs && (waddr == ADDR_ISR) && wstrb[0]) begin
          int_isr[1] <= int_isr[1] ^ wdata[1];
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_in_s0[31:0] <= 32'd0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_IN_S0_DATA_0)) begin
          int_in_s0[31:0] <= wdata[31:0] & wmask | int_in_s0[31:0] & ~wmask;
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_out_s0[31:0] <= 32'd0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_OUT_S0_DATA_0)) begin
          int_out_s0[31:0] <= wdata[31:0] & wmask | int_out_s0[31:0] & ~wmask;
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_in0[31:0] <= 32'd0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_IN0_DATA_0)) begin
          int_in0[31:0] <= wdata[31:0] & wmask | int_in0[31:0] & ~wmask;
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_in0[63:32] <= 32'd0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_IN0_DATA_1)) begin
          int_in0[63:32] <= wdata[31:0] & wmask | int_in0[63:32] & ~wmask;
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_out0[31:0] <= 32'd0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_OUT0_DATA_0)) begin
          int_out0[31:0] <= wdata[31:0] & wmask | int_out0[31:0] & ~wmask;
        end
      end
    end
  end


  always @(posedge aclk) begin
    if(areset) begin
      int_out0[63:32] <= 32'd0;
    end else begin
      if(aclk_en) begin
        if(w_hs && (waddr == ADDR_OUT0_DATA_1)) begin
          int_out0[63:32] <= wdata[31:0] & wmask | int_out0[63:32] & ~wmask;
        end
      end
    end
  end


  initial begin
    wstate = WRRESET;
    wnext = 0;
    waddr = 0;
    rstate = RDRESET;
    rnext = 0;
    rrdata = 0;
    int_ap_idle = 1'b1;
    int_ap_ready = 0;
    int_ap_done = 0;
    int_ap_start = 0;
    int_auto_restart = 0;
    int_gie = 0;
    int_ier = 0;
    int_isr = 0;
    int_in_s0 = 0;
    int_out_s0 = 0;
    int_in0 = 0;
    int_out0 = 0;
  end


endmodule



module app_top #
(
  parameter C_M_AXI_ADDR_WIDTH = 64,
  parameter C_M_AXI_DATA_WIDTH = 16
)
(
  input ap_clk,
  input ap_rst_n,
  output m00_axi_awvalid,
  input m00_axi_awready,
  output [C_M_AXI_ADDR_WIDTH-1:0] m00_axi_awaddr,
  output [8-1:0] m00_axi_awlen,
  output m00_axi_wvalid,
  input m00_axi_wready,
  output [C_M_AXI_DATA_WIDTH-1:0] m00_axi_wdata,
  output [C_M_AXI_DATA_WIDTH/8-1:0] m00_axi_wstrb,
  output m00_axi_wlast,
  input m00_axi_bvalid,
  output m00_axi_bready,
  output m00_axi_arvalid,
  input m00_axi_arready,
  output [C_M_AXI_ADDR_WIDTH-1:0] m00_axi_araddr,
  output [8-1:0] m00_axi_arlen,
  input m00_axi_rvalid,
  output m00_axi_rready,
  input [C_M_AXI_DATA_WIDTH-1:0] m00_axi_rdata,
  input m00_axi_rlast,
  input ap_start,
  output ap_idle,
  output ap_done,
  output ap_ready,
  input [32-1:0] in_s0,
  input [32-1:0] out_s0,
  input [64-1:0] in0,
  input [64-1:0] out0
);

  localparam LP_NUM_EXAMPLES = 1;
  localparam LP_RD_MAX_OUTSTANDING = 16;
  localparam LP_WR_MAX_OUTSTANDING = 16;
  (* KEEP = "yes" *)
  reg reset;
  reg ap_idle_r;
  reg ap_done_r;
  wire [LP_NUM_EXAMPLES-1:0] rd_ctrl_done;
  wire [LP_NUM_EXAMPLES-1:0] wr_ctrl_done;
  reg [LP_NUM_EXAMPLES-1:0] acc_user_done_rd_data;
  reg [LP_NUM_EXAMPLES-1:0] acc_user_done_wr_data;
  wire [LP_NUM_EXAMPLES-1:0] acc_user_request_read;
  wire [LP_NUM_EXAMPLES-1:0] acc_user_read_data_valid;
  wire [C_M_AXI_DATA_WIDTH*LP_NUM_EXAMPLES-1:0] acc_user_read_data;
  wire [LP_NUM_EXAMPLES-1:0] acc_user_available_write;
  wire [LP_NUM_EXAMPLES-1:0] acc_user_request_write;
  wire [C_M_AXI_DATA_WIDTH*LP_NUM_EXAMPLES-1:0] acc_user_write_data;
  wire acc_user_done;
  wire rd_tvalid0;
  wire rd_tready0;
  wire rd_tlast0;
  wire [C_M_AXI_DATA_WIDTH-1:0] rd_tdata0;
  wire wr_tvalid0;
  wire wr_tready0;
  wire [C_M_AXI_DATA_WIDTH-1:0] wr_tdata0;
  reg [2-1:0] fsm_reset;
  reg areset;
  reg ap_start_pulse;
  localparam FSM_STATE_START = 2'b0;
  localparam FSM_STATE_RESET = 2'b1;
  localparam FSM_STATE_RUNNING = 2'b10;

  always @(posedge ap_clk) begin
    reset <= ~ap_rst_n;
  end


  always @(posedge ap_clk) begin
    if(reset) begin
      areset <= 1'b0;
      fsm_reset <= FSM_STATE_START;
      ap_start_pulse <= 1'b0;
    end else begin
      areset <= 1'b0;
      ap_start_pulse <= 1'b0;
      case(fsm_reset)
        FSM_STATE_START: begin
          if(ap_start) begin
            areset <= 1'b1;
            fsm_reset <= FSM_STATE_RESET;
          end
        end
        FSM_STATE_RESET: begin
          ap_start_pulse <= 1'b1;
          fsm_reset <= FSM_STATE_RUNNING;
        end
        FSM_STATE_RUNNING: begin
          if(~ap_start) begin
            fsm_reset <= FSM_STATE_START;
          end
        end
      endcase
    end
  end


  always @(posedge ap_clk) begin
    if(areset) begin
      ap_idle_r <= 1'b1;
    end else begin
      ap_idle_r <= (ap_done)? 1'b1 :
                   (ap_start_pulse)? 1'b0 : ap_idle;
    end
  end

  assign ap_idle = ap_idle_r;

  always @(posedge ap_clk) begin
    if(areset) begin
      ap_done_r <= 1'b0;
    end else begin
      ap_done_r <= (ap_done)? 1'b0 : ap_done_r | acc_user_done;
    end
  end

  assign ap_done = ap_done_r;
  assign ap_ready = ap_done;
  integer i;

  always @(posedge ap_clk) begin
    if(areset) begin
      acc_user_done_rd_data <= { LP_NUM_EXAMPLES{ 1'b0 } };
      acc_user_done_wr_data <= { LP_NUM_EXAMPLES{ 1'b0 } };
    end else begin
      for(i=0; i<LP_NUM_EXAMPLES; i=i+1) begin
        acc_user_done_rd_data[i] <= (rd_ctrl_done[i])? 1'b1 : acc_user_done_rd_data[i];
        acc_user_done_wr_data[i] <= (wr_ctrl_done[i])? 1'b1 : acc_user_done_wr_data[i];
      end
    end
  end

  assign rd_tready0 = acc_user_request_read[0];
  assign acc_user_read_data_valid = {rd_tvalid0};
  assign acc_user_read_data = {rd_tdata0};

  assign acc_user_available_write = {wr_tready0};
  assign wr_tvalid0 = acc_user_request_write[0];
  assign wr_tdata0 = acc_user_write_data[1*C_M_AXI_DATA_WIDTH-1:0*C_M_AXI_DATA_WIDTH];
  (* keep_hierarchy = "yes" *)

  axi_reader_wrapper
  #(
    .C_M_AXI_ADDR_WIDTH(C_M_AXI_ADDR_WIDTH),
    .C_M_AXI_DATA_WIDTH(C_M_AXI_DATA_WIDTH),
    .C_XFER_SIZE_WIDTH(32),
    .C_MAX_OUTSTANDING(LP_RD_MAX_OUTSTANDING),
    .C_INCLUDE_DATA_FIFO(1)
  )
  axi_reader_0
  (
    .aclk(ap_clk),
    .areset(areset),
    .ctrl_start(ap_start_pulse),
    .ctrl_done(rd_ctrl_done[0]),
    .ctrl_addr_offset(in0),
    .ctrl_xfer_size_in_bytes(in_s0),
    .m_axi_arvalid(m00_axi_arvalid),
    .m_axi_arready(m00_axi_arready),
    .m_axi_araddr(m00_axi_araddr),
    .m_axi_arlen(m00_axi_arlen),
    .m_axi_rvalid(m00_axi_rvalid),
    .m_axi_rready(m00_axi_rready),
    .m_axi_rdata(m00_axi_rdata),
    .m_axi_rlast(m00_axi_rlast),
    .m_axis_aclk(ap_clk),
    .m_axis_areset(areset),
    .m_axis_tvalid(rd_tvalid0),
    .m_axis_tready(rd_tready0),
    .m_axis_tlast(rd_tlast0),
    .m_axis_tdata(rd_tdata0)
  );

  (* keep_hierarchy = "yes" *)

  axi_writer_wrapper
  #(
    .C_M_AXI_ADDR_WIDTH(C_M_AXI_ADDR_WIDTH),
    .C_M_AXI_DATA_WIDTH(C_M_AXI_DATA_WIDTH),
    .C_XFER_SIZE_WIDTH(32),
    .C_MAX_OUTSTANDING(LP_WR_MAX_OUTSTANDING),
    .C_INCLUDE_DATA_FIFO(1)
  )
  axi_writer_0
  (
    .aclk(ap_clk),
    .areset(areset),
    .ctrl_start(ap_start_pulse),
    .ctrl_done(wr_ctrl_done[0]),
    .ctrl_addr_offset(out0),
    .ctrl_xfer_size_in_bytes(out_s0),
    .m_axi_awvalid(m00_axi_awvalid),
    .m_axi_awready(m00_axi_awready),
    .m_axi_awaddr(m00_axi_awaddr),
    .m_axi_awlen(m00_axi_awlen),
    .m_axi_wvalid(m00_axi_wvalid),
    .m_axi_wready(m00_axi_wready),
    .m_axi_wdata(m00_axi_wdata),
    .m_axi_wstrb(m00_axi_wstrb),
    .m_axi_wlast(m00_axi_wlast),
    .m_axi_bvalid(m00_axi_bvalid),
    .m_axi_bready(m00_axi_bready),
    .s_axis_aclk(ap_clk),
    .s_axis_areset(areset),
    .s_axis_tvalid(wr_tvalid0),
    .s_axis_tready(wr_tready0),
    .s_axis_tdata(wr_tdata0)
  );

  (* keep_hierarchy = "yes" *)

  sa_100_acc
  acc
  (
    .clk(ap_clk),
    .rst(areset),
    .start(ap_start_pulse),
    .acc_user_done_rd_data(acc_user_done_rd_data),
    .acc_user_done_wr_data(acc_user_done_wr_data),
    .acc_user_request_read(acc_user_request_read),
    .acc_user_read_data_valid(acc_user_read_data_valid),
    .acc_user_read_data(acc_user_read_data),
    .acc_user_available_write(acc_user_available_write),
    .acc_user_request_write(acc_user_request_write),
    .acc_user_write_data(acc_user_write_data),
    .acc_user_done(acc_user_done)
  );


  initial begin
    reset = 1'b1;
    ap_idle_r = 1'b1;
    ap_done_r = 0;
    acc_user_done_rd_data = 0;
    acc_user_done_wr_data = 0;
    fsm_reset = FSM_STATE_START;
    areset = 1'b1;
    ap_start_pulse = 0;
  end


endmodule



module axi_reader_wrapper #
(
  parameter C_M_AXI_ADDR_WIDTH = 64,
  parameter C_M_AXI_DATA_WIDTH = 16,
  parameter C_XFER_SIZE_WIDTH = 64,
  parameter C_MAX_OUTSTANDING = 16,
  parameter C_INCLUDE_DATA_FIFO = 0
)
(
  input aclk,
  input areset,
  input ctrl_start,
  output ctrl_done,
  input [C_M_AXI_ADDR_WIDTH-1:0] ctrl_addr_offset,
  input [C_XFER_SIZE_WIDTH-1:0] ctrl_xfer_size_in_bytes,
  output m_axi_arvalid,
  input m_axi_arready,
  output [C_M_AXI_ADDR_WIDTH-1:0] m_axi_araddr,
  output [8-1:0] m_axi_arlen,
  input m_axi_rvalid,
  output m_axi_rready,
  input [C_M_AXI_DATA_WIDTH-1:0] m_axi_rdata,
  input m_axi_rlast,
  input m_axis_aclk,
  input m_axis_areset,
  output m_axis_tvalid,
  input m_axis_tready,
  output [C_M_AXI_DATA_WIDTH-1:0] m_axis_tdata,
  output m_axis_tlast
);

  axi_reader #(
            .C_M_AXI_ADDR_WIDTH  ( C_M_AXI_ADDR_WIDTH  ) ,
            .C_M_AXI_DATA_WIDTH  ( C_M_AXI_DATA_WIDTH  ) ,
            .C_XFER_SIZE_WIDTH   ( C_XFER_SIZE_WIDTH   ) ,
            .C_MAX_OUTSTANDING   ( C_MAX_OUTSTANDING   ) ,
            .C_INCLUDE_DATA_FIFO ( C_INCLUDE_DATA_FIFO )
          )
          inst_axi_reader (
            .aclk                    ( aclk                   ) ,
            .areset                  ( areset                 ) ,
            .ctrl_start              ( ctrl_start             ) ,
            .ctrl_done               ( ctrl_done              ) ,
            .ctrl_addr_offset        ( ctrl_addr_offset       ) ,
            .ctrl_xfer_size_in_bytes ( ctrl_xfer_size_in_bytes) ,
            .m_axi_arvalid           ( m_axi_arvalid          ) ,
            .m_axi_arready           ( m_axi_arready          ) ,
            .m_axi_araddr            ( m_axi_araddr           ) ,
            .m_axi_arlen             ( m_axi_arlen            ) ,
            .m_axi_rvalid            ( m_axi_rvalid           ) ,
            .m_axi_rready            ( m_axi_rready           ) ,
            .m_axi_rdata             ( m_axi_rdata            ) ,
            .m_axi_rlast             ( m_axi_rlast            ) ,
            .m_axis_aclk             ( m_axis_aclk            ) ,
            .m_axis_areset           ( m_axis_areset          ) ,
            .m_axis_tvalid           ( m_axis_tvalid          ) ,
            .m_axis_tready           ( m_axis_tready          ) ,
            .m_axis_tlast            ( m_axis_tlast           ) ,
            .m_axis_tdata            ( m_axis_tdata           )
          );

endmodule



module axi_writer_wrapper #
(
  parameter C_M_AXI_ADDR_WIDTH = 64,
  parameter C_M_AXI_DATA_WIDTH = 16,
  parameter C_XFER_SIZE_WIDTH = 64,
  parameter C_MAX_OUTSTANDING = 16,
  parameter C_INCLUDE_DATA_FIFO = 1
)
(
  input aclk,
  input areset,
  input ctrl_start,
  output ctrl_done,
  input [C_M_AXI_ADDR_WIDTH-1:0] ctrl_addr_offset,
  input [C_XFER_SIZE_WIDTH-1:0] ctrl_xfer_size_in_bytes,
  output m_axi_awvalid,
  input m_axi_awready,
  output [C_M_AXI_ADDR_WIDTH-1:0] m_axi_awaddr,
  output [8-1:0] m_axi_awlen,
  output m_axi_wvalid,
  input m_axi_wready,
  output [C_M_AXI_DATA_WIDTH-1:0] m_axi_wdata,
  output [C_M_AXI_DATA_WIDTH/8-1:0] m_axi_wstrb,
  output m_axi_wlast,
  input m_axi_bvalid,
  output m_axi_bready,
  input s_axis_aclk,
  input s_axis_areset,
  input s_axis_tvalid,
  output s_axis_tready,
  input [C_M_AXI_DATA_WIDTH-1:0] s_axis_tdata
);

  axi_writer #(
            .C_M_AXI_ADDR_WIDTH  ( C_M_AXI_ADDR_WIDTH ) ,
            .C_M_AXI_DATA_WIDTH  ( C_M_AXI_DATA_WIDTH ) ,
            .C_XFER_SIZE_WIDTH   ( C_XFER_SIZE_WIDTH  ) ,
            .C_MAX_OUTSTANDING   ( C_MAX_OUTSTANDING  ) ,
            .C_INCLUDE_DATA_FIFO ( C_INCLUDE_DATA_FIFO)
          )
          inst_axi_writer (
            .aclk                    ( aclk                   ) ,
            .areset                  ( areset                 ) ,
            .ctrl_start              ( ctrl_start             ) ,
            .ctrl_done               ( ctrl_done              ) ,
            .ctrl_addr_offset        ( ctrl_addr_offset       ) ,
            .ctrl_xfer_size_in_bytes ( ctrl_xfer_size_in_bytes) ,
            .m_axi_awvalid           ( m_axi_awvalid) ,
            .m_axi_awready           ( m_axi_awready) ,
            .m_axi_awaddr            ( m_axi_awaddr ) ,
            .m_axi_awlen             ( m_axi_awlen  ) ,
            .m_axi_wvalid            ( m_axi_wvalid ) ,
            .m_axi_wready            ( m_axi_wready ) ,
            .m_axi_wdata             ( m_axi_wdata  ) ,
            .m_axi_wstrb             ( m_axi_wstrb  ) ,
            .m_axi_wlast             ( m_axi_wlast  ) ,
            .m_axi_bvalid            ( m_axi_bvalid ) ,
            .m_axi_bready            ( m_axi_bready ) ,
            .s_axis_aclk             ( s_axis_aclk  ) ,
            .s_axis_areset           ( s_axis_areset) ,
            .s_axis_tvalid           (s_axis_tvalid ) ,
            .s_axis_tready           (s_axis_tready ) ,
            .s_axis_tdata            (s_axis_tdata  )
          );

endmodule



module sa_100_acc
(
  input clk,
  input rst,
  input start,
  input [1-1:0] acc_user_done_rd_data,
  input [1-1:0] acc_user_done_wr_data,
  output [1-1:0] acc_user_request_read,
  input [1-1:0] acc_user_read_data_valid,
  input [16-1:0] acc_user_read_data,
  input [1-1:0] acc_user_available_write,
  output [1-1:0] acc_user_request_write,
  output [16-1:0] acc_user_write_data,
  output acc_user_done
);

  reg start_reg;
  wire [1-1:0] grn_aws_done;
  assign acc_user_done = &grn_aws_done;

  always @(posedge clk) begin
    if(rst) begin
      start_reg <= 0;
    end else begin
      start_reg <= start_reg | start;
    end
  end

  (* keep_hierarchy = "yes" *)

  grn_aws_1
  #(
    .grn_aws_pe_init_id(0)
  )
  grn_aws_1_0
  (
    .clk(clk),
    .rst(rst),
    .start(start_reg),
    .grn_aws_done_rd_data(acc_user_done_rd_data[0]),
    .grn_aws_done_wr_data(acc_user_done_wr_data[0]),
    .grn_aws_request_read(acc_user_request_read[0]),
    .grn_aws_read_data_valid(acc_user_read_data_valid[0]),
    .grn_aws_read_data(acc_user_read_data[15:0]),
    .grn_aws_available_write(acc_user_available_write[0]),
    .grn_aws_request_write(acc_user_request_write[0]),
    .grn_aws_write_data(acc_user_write_data[15:0]),
    .grn_aws_done(grn_aws_done[0])
  );


  initial begin
    start_reg = 0;
  end


endmodule





