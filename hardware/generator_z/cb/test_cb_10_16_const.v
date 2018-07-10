module top();

   reg [31:0] config_addr;
   reg [31:0] config_data;
   reg 	      config_en;
   
   reg 	      clk;
   reg 	      reset;

   reg [15:0] out;

   reg [15:0] in_0;
   reg [15:0] in_1;
   reg [15:0] in_2;
   reg [15:0] in_3;
   reg [15:0] in_4;

   reg [15:0] in_6;
   reg [15:0] in_7;
   reg [15:0] in_8;
   reg [15:0] in_9;   

   initial begin
      #1 config_addr = 0;
      #1 config_en = 0;

      #1 reset = 0;
      #1 reset = 1;
      #1 reset = 0;

      #1 config_en = 1;
      #1 config_data = 32'h1;
      
      #1 clk = 0;
      #1 clk = 1;

      #1 clk = 0;
      #1 clk = 1;
      
      #1 config_en = 0;

      #1 in_1 = 4;


      #2

      assert(out == 4);
      
      $finish();
   end

   cb connect_box(.clk(clk), .reset(reset), .config_addr(config_addr), .config_data(config_data), .config_en(config_en),
		  .in_0(in_0),
		  .in_1(in_1),
		  .in_2(in_2),
		  .in_3(in_3),
		  .in_4(in_4),

		  .in_6(in_6),
		  .in_7(in_7),
		  .in_8(in_8),
		  .in_9(in_9),

		  .out(out));
   
endmodule
