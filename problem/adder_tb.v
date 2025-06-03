module adder_tb;

  // Inputs
  reg [63:0] A;
  reg [63:0] B;

  // Outputs
  wire [64:0] SUM;

  // Instantiate two counter variables for the test loop
  integer count;
  integer count2;

  // Instantiate the Unit Under Test (UUT)
  adder_64 uut
  (
    .A(A),
    .B(B),
    .SUM(SUM)
  );

  initial begin

    // Loops over the possible combinations for the inputs A and B
    for (count = 0; count <= 32; count = count + 1) begin
      A = count;
      for (count2 = 0; count2 <= 32; count2 = count2 + 1) begin
        B = count2;
        #1; // Let the result settle

        // Check result and print pass/fail
        if (SUM === (A + B))
          $display("PASS: %d + %d = %d", A, B, SUM);
        else
          $display("FAIL: %d + %d = %d (expected %d)", A, B, SUM, A+B);

      end
    end
  end

  initial #4000 $finish; // The test will run for a total interval of 4000 nanoseconds
endmodule
