module mod1 #(
  parameter ADDR = 22,
  DATA = 5
) (
  input reg [1:0] addr,
  input wire clk,
  input rst,
  output logic [DATA-1:0] data,
  output rdy,
  output [ADDR-1:3] newaddr
);

endmodule

module mod2 #(
  parameter ADDR = 22,
  DATA = 5,
  int WAIT = 10,
  int RDY
) (
  input reg [1:0] addr,
  input wire clk,
  input rst,
  output logic [DATA-1:0] data,
  output rdy,
  output [ADDR-1:3] newaddr
);

endmodule