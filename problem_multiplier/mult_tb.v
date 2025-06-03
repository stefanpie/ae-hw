module multiplier_tb;
    reg  [15:0] a, b;
    wire [31:0] product;

    multiplier uut (
        .A(a),
        .B(b),
        .PRODUCT(product)
    );

    task run_test;
        input [15:0] ta, tb;
        input [31:0] expected;
        begin
            a = ta; b = tb;
            #1; // small delay for assignment
            if (product === expected)
                $display("PASS: a=%0d b=%0d product=%0d EXPECTED=%0d", a, b, product, expected);
            else
                $display("FAIL: a=%0d b=%0d product=%0d EXPECTED=%0d", a, b, product, expected);
        end
    endtask

    initial begin
        $display("Starting 16-bit multiplier testbench...");

        // You can use 8-bit test cases for a 16-bit multiplier
        run_test(16'd0,     16'd0,      32'd0      );
        run_test(16'd15,    16'd3,      32'd45     );
        run_test(16'd25,    16'd10,     32'd250    );
        run_test(16'd255,   16'd2,      32'd510    );
        run_test(16'd128,   16'd128,    32'd16384  );
        run_test(16'd200,   16'd50,     32'd10000  );

        // Add some wider 16-bit tests to exercise upper bits
        run_test(16'd40000, 16'd2,      32'd80000  );
        run_test(16'd65535, 16'd65535,  32'd4294836225);

        $finish;
    end
endmodule
