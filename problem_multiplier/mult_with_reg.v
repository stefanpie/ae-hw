verilog
module multiplier (
    input  [15:0] A,
    input  [15:0] B,
    output [31:0] PRODUCT
);

    reg [31:0] product_internal;
    integer i;

    always @(*) begin
        product_internal = 0;
        for (i = 0; i < 16; i = i + 1) begin
            if (B[i]) begin
                product_internal = product_internal + (A << i);
            end
        end
    end

    assign PRODUCT = product_internal;
endmodule