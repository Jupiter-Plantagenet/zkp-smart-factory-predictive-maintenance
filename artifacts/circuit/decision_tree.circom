pragma circom 2.1.5;

// Decision tree circuit generated programmatically
// Model used: decision_tree_model.joblib

include "node_modules/circomlib/circuits/comparators.circom";

template DecisionTree(numFeatures) {
    // --- Inputs ---
    // Expected order: Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Type_H, Type_L, Type_M
    // Values should be scaled and multiplied by 10000
    signal input features[numFeatures];

    // --- Output ---
    // 0 for No Failure, 1 for Failure
    signal output out_prediction;

    // --- Comparators for Split Nodes ---
    // Node 0: If Rotational speed [rpm] (features[2]) <= ... (Original Threshold: -0.8446, Fixed: -8446)
    component comp_node0 = LessEqThan(32);
    comp_node0.in[0] <== features[2];
    comp_node0.in[1] <== -8446;
    signal comp_node0_out <== comp_node0.out; // 1 if true (left), 0 if false (right)

    // Node 1: If Air temperature [K] (features[0]) <= ... (Original Threshold: 0.7735, Fixed: 7735)
    component comp_node1 = LessEqThan(32);
    comp_node1.in[0] <== features[0];
    comp_node1.in[1] <== 7735;
    signal comp_node1_out <== comp_node1.out; // 1 if true (left), 0 if false (right)

    // Node 2: If Torque [Nm] (features[3]) <= ... (Original Threshold: 2.0009, Fixed: 20009)
    component comp_node2 = LessEqThan(32);
    comp_node2.in[0] <== features[3];
    comp_node2.in[1] <== 20009;
    signal comp_node2_out <== comp_node2.out; // 1 if true (left), 0 if false (right)

    // Node 3: If Tool wear [min] (features[4]) <= ... (Original Threshold: 1.2705, Fixed: 12705)
    component comp_node3 = LessEqThan(32);
    comp_node3.in[0] <== features[4];
    comp_node3.in[1] <== 12705;
    signal comp_node3_out <== comp_node3.out; // 1 if true (left), 0 if false (right)

    // Node 4: If Torque [Nm] (features[3]) <= ... (Original Threshold: 0.1693, Fixed: 1693)
    component comp_node4 = LessEqThan(32);
    comp_node4.in[0] <== features[3];
    comp_node4.in[1] <== 1693;
    signal comp_node4_out <== comp_node4.out; // 1 if true (left), 0 if false (right)

    // Node 7: If Type_L (features[6]) <= ... (Original Threshold: 0.5000 for binary Type_L, Effective Fixed Threshold for '==0' logic: 0)
    component comp_node7 = LessEqThan(32);
    comp_node7.in[0] <== features[6];
    comp_node7.in[1] <== 0;
    signal comp_node7_out <== comp_node7.out; // 1 if true (left), 0 if false (right)

    // Node 10: If Torque [Nm] (features[3]) <= ... (Original Threshold: 2.4949, Fixed: 24949)
    component comp_node10 = LessEqThan(32);
    comp_node10.in[0] <== features[3];
    comp_node10.in[1] <== 24949;
    signal comp_node10_out <== comp_node10.out; // 1 if true (left), 0 if false (right)

    // Node 11: If Tool wear [min] (features[4]) <= ... (Original Threshold: 1.0583, Fixed: 10583)
    component comp_node11 = LessEqThan(32);
    comp_node11.in[0] <== features[4];
    comp_node11.in[1] <== 10583;
    signal comp_node11_out <== comp_node11.out; // 1 if true (left), 0 if false (right)

    // Node 14: If Rotational speed [rpm] (features[2]) <= ... (Original Threshold: -1.4055, Fixed: -14055)
    component comp_node14 = LessEqThan(32);
    comp_node14.in[0] <== features[2];
    comp_node14.in[1] <== -14055;
    signal comp_node14_out <== comp_node14.out; // 1 if true (left), 0 if false (right)

    // Node 17: If Process temperature [K] (features[1]) <= ... (Original Threshold: 1.5169, Fixed: 15169)
    component comp_node17 = LessEqThan(32);
    comp_node17.in[0] <== features[1];
    comp_node17.in[1] <== 15169;
    signal comp_node17_out <== comp_node17.out; // 1 if true (left), 0 if false (right)

    // Node 18: If Rotational speed [rpm] (features[2]) <= ... (Original Threshold: -0.8778, Fixed: -8778)
    component comp_node18 = LessEqThan(32);
    comp_node18.in[0] <== features[2];
    comp_node18.in[1] <== -8778;
    signal comp_node18_out <== comp_node18.out; // 1 if true (left), 0 if false (right)

    // Node 19: If Process temperature [K] (features[1]) <= ... (Original Threshold: 0.3677, Fixed: 3677)
    component comp_node19 = LessEqThan(32);
    comp_node19.in[0] <== features[1];
    comp_node19.in[1] <== 3677;
    signal comp_node19_out <== comp_node19.out; // 1 if true (left), 0 if false (right)

    // Node 22: If Tool wear [min] (features[4]) <= ... (Original Threshold: 0.2958, Fixed: 2958)
    component comp_node22 = LessEqThan(32);
    comp_node22.in[0] <== features[4];
    comp_node22.in[1] <== 2958;
    signal comp_node22_out <== comp_node22.out; // 1 if true (left), 0 if false (right)

    // Node 25: If Torque [Nm] (features[3]) <= ... (Original Threshold: 1.6665, Fixed: 16665)
    component comp_node25 = LessEqThan(32);
    comp_node25.in[0] <== features[3];
    comp_node25.in[1] <== 16665;
    signal comp_node25_out <== comp_node25.out; // 1 if true (left), 0 if false (right)

    // Node 26: If Tool wear [min] (features[4]) <= ... (Original Threshold: -1.0877, Fixed: -10877)
    component comp_node26 = LessEqThan(32);
    comp_node26.in[0] <== features[4];
    comp_node26.in[1] <== -10877;
    signal comp_node26_out <== comp_node26.out; // 1 if true (left), 0 if false (right)

    // Node 29: If Tool wear [min] (features[4]) <= ... (Original Threshold: 0.5159, Fixed: 5159)
    component comp_node29 = LessEqThan(32);
    comp_node29.in[0] <== features[4];
    comp_node29.in[1] <== 5159;
    signal comp_node29_out <== comp_node29.out; // 1 if true (left), 0 if false (right)

    // Node 32: If Tool wear [min] (features[4]) <= ... (Original Threshold: 1.5221, Fixed: 15221)
    component comp_node32 = LessEqThan(32);
    comp_node32.in[0] <== features[4];
    comp_node32.in[1] <== 15221;
    signal comp_node32_out <== comp_node32.out; // 1 if true (left), 0 if false (right)

    // Node 33: If Torque [Nm] (features[3]) <= ... (Original Threshold: -2.4557, Fixed: -24557)
    component comp_node33 = LessEqThan(32);
    comp_node33.in[0] <== features[3];
    comp_node33.in[1] <== -24557;
    signal comp_node33_out <== comp_node33.out; // 1 if true (left), 0 if false (right)

    // Node 34: If Torque [Nm] (features[3]) <= ... (Original Threshold: -2.6503, Fixed: -26503)
    component comp_node34 = LessEqThan(32);
    comp_node34.in[0] <== features[3];
    comp_node34.in[1] <== -26503;
    signal comp_node34_out <== comp_node34.out; // 1 if true (left), 0 if false (right)

    // Node 35: If Torque [Nm] (features[3]) <= ... (Original Threshold: -2.7601, Fixed: -27601)
    component comp_node35 = LessEqThan(32);
    comp_node35.in[0] <== features[3];
    comp_node35.in[1] <== -27601;
    signal comp_node35_out <== comp_node35.out; // 1 if true (left), 0 if false (right)

    // Node 38: If Air temperature [K] (features[0]) <= ... (Original Threshold: -0.5036, Fixed: -5036)
    component comp_node38 = LessEqThan(32);
    comp_node38.in[0] <== features[0];
    comp_node38.in[1] <== -5036;
    signal comp_node38_out <== comp_node38.out; // 1 if true (left), 0 if false (right)

    // Node 41: If Torque [Nm] (features[3]) <= ... (Original Threshold: 1.7014, Fixed: 17014)
    component comp_node41 = LessEqThan(32);
    comp_node41.in[0] <== features[3];
    comp_node41.in[1] <== 17014;
    signal comp_node41_out <== comp_node41.out; // 1 if true (left), 0 if false (right)

    // Node 42: If Tool wear [min] (features[4]) <= ... (Original Threshold: 1.4906, Fixed: 14906)
    component comp_node42 = LessEqThan(32);
    comp_node42.in[0] <== features[4];
    comp_node42.in[1] <== 14906;
    signal comp_node42_out <== comp_node42.out; // 1 if true (left), 0 if false (right)

    // Node 45: If Torque [Nm] (features[3]) <= ... (Original Threshold: 1.9110, Fixed: 19110)
    component comp_node45 = LessEqThan(32);
    comp_node45.in[0] <== features[3];
    comp_node45.in[1] <== 19110;
    signal comp_node45_out <== comp_node45.out; // 1 if true (left), 0 if false (right)

    // Node 48: If Torque [Nm] (features[3]) <= ... (Original Threshold: 0.5237, Fixed: 5237)
    component comp_node48 = LessEqThan(32);
    comp_node48.in[0] <== features[3];
    comp_node48.in[1] <== 5237;
    signal comp_node48_out <== comp_node48.out; // 1 if true (left), 0 if false (right)

    // Node 49: If Torque [Nm] (features[3]) <= ... (Original Threshold: 0.1344, Fixed: 1344)
    component comp_node49 = LessEqThan(32);
    comp_node49.in[0] <== features[3];
    comp_node49.in[1] <== 1344;
    signal comp_node49_out <== comp_node49.out; // 1 if true (left), 0 if false (right)

    // Node 50: If Tool wear [min] (features[4]) <= ... (Original Threshold: 1.9937, Fixed: 19937)
    component comp_node50 = LessEqThan(32);
    comp_node50.in[0] <== features[4];
    comp_node50.in[1] <== 19937;
    signal comp_node50_out <== comp_node50.out; // 1 if true (left), 0 if false (right)

    // Node 53: If Torque [Nm] (features[3]) <= ... (Original Threshold: 0.4189, Fixed: 4189)
    component comp_node53 = LessEqThan(32);
    comp_node53.in[0] <== features[3];
    comp_node53.in[1] <== 4189;
    signal comp_node53_out <== comp_node53.out; // 1 if true (left), 0 if false (right)

    // Node 56: If Tool wear [min] (features[4]) <= ... (Original Threshold: 1.5535, Fixed: 15535)
    component comp_node56 = LessEqThan(32);
    comp_node56.in[0] <== features[4];
    comp_node56.in[1] <== 15535;
    signal comp_node56_out <== comp_node56.out; // 1 if true (left), 0 if false (right)

    // Node 58: If Torque [Nm] (features[3]) <= ... (Original Threshold: 1.1225, Fixed: 11225)
    component comp_node58 = LessEqThan(32);
    comp_node58.in[0] <== features[3];
    comp_node58.in[1] <== 11225;
    signal comp_node58_out <== comp_node58.out; // 1 if true (left), 0 if false (right)

    // --- Path Conditions and Leaf Value Aggregation ---
    signal leaf5_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf5_pathprod_step1 <== leaf5_pathprod_step0 * comp_node2_out;
    signal leaf5_pathprod_step2 <== leaf5_pathprod_step1 * comp_node3_out;
    signal leaf5_pathprod_step3 <== leaf5_pathprod_step2 * comp_node4_out;
    signal path_leaf5_active <== leaf5_pathprod_step3;
    // Leaf 5: Prediction=0, PathSignal: path_leaf5_active
    signal leaf5_contribution <== path_leaf5_active * 0;
    signal leaf6_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf6_pathprod_step1 <== leaf6_pathprod_step0 * comp_node2_out;
    signal leaf6_pathprod_step2 <== leaf6_pathprod_step1 * comp_node3_out;
    signal leaf6_pathprod_step3 <== leaf6_pathprod_step2 * (1 - comp_node4_out);
    signal path_leaf6_active <== leaf6_pathprod_step3;
    // Leaf 6: Prediction=0, PathSignal: path_leaf6_active
    signal leaf6_contribution <== path_leaf6_active * 0;
    signal leaf8_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf8_pathprod_step1 <== leaf8_pathprod_step0 * comp_node2_out;
    signal leaf8_pathprod_step2 <== leaf8_pathprod_step1 * (1 - comp_node3_out);
    signal leaf8_pathprod_step3 <== leaf8_pathprod_step2 * comp_node7_out;
    signal path_leaf8_active <== leaf8_pathprod_step3;
    // Leaf 8: Prediction=0, PathSignal: path_leaf8_active
    signal leaf8_contribution <== path_leaf8_active * 0;
    signal leaf9_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf9_pathprod_step1 <== leaf9_pathprod_step0 * comp_node2_out;
    signal leaf9_pathprod_step2 <== leaf9_pathprod_step1 * (1 - comp_node3_out);
    signal leaf9_pathprod_step3 <== leaf9_pathprod_step2 * (1 - comp_node7_out);
    signal path_leaf9_active <== leaf9_pathprod_step3;
    // Leaf 9: Prediction=1, PathSignal: path_leaf9_active
    signal leaf9_contribution <== path_leaf9_active * 1;
    signal leaf12_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf12_pathprod_step1 <== leaf12_pathprod_step0 * (1 - comp_node2_out);
    signal leaf12_pathprod_step2 <== leaf12_pathprod_step1 * comp_node10_out;
    signal leaf12_pathprod_step3 <== leaf12_pathprod_step2 * comp_node11_out;
    signal path_leaf12_active <== leaf12_pathprod_step3;
    // Leaf 12: Prediction=1, PathSignal: path_leaf12_active
    signal leaf12_contribution <== path_leaf12_active * 1;
    signal leaf13_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf13_pathprod_step1 <== leaf13_pathprod_step0 * (1 - comp_node2_out);
    signal leaf13_pathprod_step2 <== leaf13_pathprod_step1 * comp_node10_out;
    signal leaf13_pathprod_step3 <== leaf13_pathprod_step2 * (1 - comp_node11_out);
    signal path_leaf13_active <== leaf13_pathprod_step3;
    // Leaf 13: Prediction=1, PathSignal: path_leaf13_active
    signal leaf13_contribution <== path_leaf13_active * 1;
    signal leaf15_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf15_pathprod_step1 <== leaf15_pathprod_step0 * (1 - comp_node2_out);
    signal leaf15_pathprod_step2 <== leaf15_pathprod_step1 * (1 - comp_node10_out);
    signal leaf15_pathprod_step3 <== leaf15_pathprod_step2 * comp_node14_out;
    signal path_leaf15_active <== leaf15_pathprod_step3;
    // Leaf 15: Prediction=1, PathSignal: path_leaf15_active
    signal leaf15_contribution <== path_leaf15_active * 1;
    signal leaf16_pathprod_step0 <== comp_node0_out * comp_node1_out;
    signal leaf16_pathprod_step1 <== leaf16_pathprod_step0 * (1 - comp_node2_out);
    signal leaf16_pathprod_step2 <== leaf16_pathprod_step1 * (1 - comp_node10_out);
    signal leaf16_pathprod_step3 <== leaf16_pathprod_step2 * (1 - comp_node14_out);
    signal path_leaf16_active <== leaf16_pathprod_step3;
    // Leaf 16: Prediction=1, PathSignal: path_leaf16_active
    signal leaf16_contribution <== path_leaf16_active * 1;
    signal leaf20_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf20_pathprod_step1 <== leaf20_pathprod_step0 * comp_node17_out;
    signal leaf20_pathprod_step2 <== leaf20_pathprod_step1 * comp_node18_out;
    signal leaf20_pathprod_step3 <== leaf20_pathprod_step2 * comp_node19_out;
    signal path_leaf20_active <== leaf20_pathprod_step3;
    // Leaf 20: Prediction=1, PathSignal: path_leaf20_active
    signal leaf20_contribution <== path_leaf20_active * 1;
    signal leaf21_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf21_pathprod_step1 <== leaf21_pathprod_step0 * comp_node17_out;
    signal leaf21_pathprod_step2 <== leaf21_pathprod_step1 * comp_node18_out;
    signal leaf21_pathprod_step3 <== leaf21_pathprod_step2 * (1 - comp_node19_out);
    signal path_leaf21_active <== leaf21_pathprod_step3;
    // Leaf 21: Prediction=1, PathSignal: path_leaf21_active
    signal leaf21_contribution <== path_leaf21_active * 1;
    signal leaf23_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf23_pathprod_step1 <== leaf23_pathprod_step0 * comp_node17_out;
    signal leaf23_pathprod_step2 <== leaf23_pathprod_step1 * (1 - comp_node18_out);
    signal leaf23_pathprod_step3 <== leaf23_pathprod_step2 * comp_node22_out;
    signal path_leaf23_active <== leaf23_pathprod_step3;
    // Leaf 23: Prediction=0, PathSignal: path_leaf23_active
    signal leaf23_contribution <== path_leaf23_active * 0;
    signal leaf24_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf24_pathprod_step1 <== leaf24_pathprod_step0 * comp_node17_out;
    signal leaf24_pathprod_step2 <== leaf24_pathprod_step1 * (1 - comp_node18_out);
    signal leaf24_pathprod_step3 <== leaf24_pathprod_step2 * (1 - comp_node22_out);
    signal path_leaf24_active <== leaf24_pathprod_step3;
    // Leaf 24: Prediction=1, PathSignal: path_leaf24_active
    signal leaf24_contribution <== path_leaf24_active * 1;
    signal leaf27_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf27_pathprod_step1 <== leaf27_pathprod_step0 * (1 - comp_node17_out);
    signal leaf27_pathprod_step2 <== leaf27_pathprod_step1 * comp_node25_out;
    signal leaf27_pathprod_step3 <== leaf27_pathprod_step2 * comp_node26_out;
    signal path_leaf27_active <== leaf27_pathprod_step3;
    // Leaf 27: Prediction=0, PathSignal: path_leaf27_active
    signal leaf27_contribution <== path_leaf27_active * 0;
    signal leaf28_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf28_pathprod_step1 <== leaf28_pathprod_step0 * (1 - comp_node17_out);
    signal leaf28_pathprod_step2 <== leaf28_pathprod_step1 * comp_node25_out;
    signal leaf28_pathprod_step3 <== leaf28_pathprod_step2 * (1 - comp_node26_out);
    signal path_leaf28_active <== leaf28_pathprod_step3;
    // Leaf 28: Prediction=0, PathSignal: path_leaf28_active
    signal leaf28_contribution <== path_leaf28_active * 0;
    signal leaf30_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf30_pathprod_step1 <== leaf30_pathprod_step0 * (1 - comp_node17_out);
    signal leaf30_pathprod_step2 <== leaf30_pathprod_step1 * (1 - comp_node25_out);
    signal leaf30_pathprod_step3 <== leaf30_pathprod_step2 * comp_node29_out;
    signal path_leaf30_active <== leaf30_pathprod_step3;
    // Leaf 30: Prediction=1, PathSignal: path_leaf30_active
    signal leaf30_contribution <== path_leaf30_active * 1;
    signal leaf31_pathprod_step0 <== comp_node0_out * (1 - comp_node1_out);
    signal leaf31_pathprod_step1 <== leaf31_pathprod_step0 * (1 - comp_node17_out);
    signal leaf31_pathprod_step2 <== leaf31_pathprod_step1 * (1 - comp_node25_out);
    signal leaf31_pathprod_step3 <== leaf31_pathprod_step2 * (1 - comp_node29_out);
    signal path_leaf31_active <== leaf31_pathprod_step3;
    // Leaf 31: Prediction=1, PathSignal: path_leaf31_active
    signal leaf31_contribution <== path_leaf31_active * 1;
    signal leaf36_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf36_pathprod_step1 <== leaf36_pathprod_step0 * comp_node33_out;
    signal leaf36_pathprod_step2 <== leaf36_pathprod_step1 * comp_node34_out;
    signal leaf36_pathprod_step3 <== leaf36_pathprod_step2 * comp_node35_out;
    signal path_leaf36_active <== leaf36_pathprod_step3;
    // Leaf 36: Prediction=1, PathSignal: path_leaf36_active
    signal leaf36_contribution <== path_leaf36_active * 1;
    signal leaf37_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf37_pathprod_step1 <== leaf37_pathprod_step0 * comp_node33_out;
    signal leaf37_pathprod_step2 <== leaf37_pathprod_step1 * comp_node34_out;
    signal leaf37_pathprod_step3 <== leaf37_pathprod_step2 * (1 - comp_node35_out);
    signal path_leaf37_active <== leaf37_pathprod_step3;
    // Leaf 37: Prediction=1, PathSignal: path_leaf37_active
    signal leaf37_contribution <== path_leaf37_active * 1;
    signal leaf39_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf39_pathprod_step1 <== leaf39_pathprod_step0 * comp_node33_out;
    signal leaf39_pathprod_step2 <== leaf39_pathprod_step1 * (1 - comp_node34_out);
    signal leaf39_pathprod_step3 <== leaf39_pathprod_step2 * comp_node38_out;
    signal path_leaf39_active <== leaf39_pathprod_step3;
    // Leaf 39: Prediction=1, PathSignal: path_leaf39_active
    signal leaf39_contribution <== path_leaf39_active * 1;
    signal leaf40_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf40_pathprod_step1 <== leaf40_pathprod_step0 * comp_node33_out;
    signal leaf40_pathprod_step2 <== leaf40_pathprod_step1 * (1 - comp_node34_out);
    signal leaf40_pathprod_step3 <== leaf40_pathprod_step2 * (1 - comp_node38_out);
    signal path_leaf40_active <== leaf40_pathprod_step3;
    // Leaf 40: Prediction=0, PathSignal: path_leaf40_active
    signal leaf40_contribution <== path_leaf40_active * 0;
    signal leaf43_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf43_pathprod_step1 <== leaf43_pathprod_step0 * (1 - comp_node33_out);
    signal leaf43_pathprod_step2 <== leaf43_pathprod_step1 * comp_node41_out;
    signal leaf43_pathprod_step3 <== leaf43_pathprod_step2 * comp_node42_out;
    signal path_leaf43_active <== leaf43_pathprod_step3;
    // Leaf 43: Prediction=0, PathSignal: path_leaf43_active
    signal leaf43_contribution <== path_leaf43_active * 0;
    signal leaf44_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf44_pathprod_step1 <== leaf44_pathprod_step0 * (1 - comp_node33_out);
    signal leaf44_pathprod_step2 <== leaf44_pathprod_step1 * comp_node41_out;
    signal leaf44_pathprod_step3 <== leaf44_pathprod_step2 * (1 - comp_node42_out);
    signal path_leaf44_active <== leaf44_pathprod_step3;
    // Leaf 44: Prediction=0, PathSignal: path_leaf44_active
    signal leaf44_contribution <== path_leaf44_active * 0;
    signal leaf46_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf46_pathprod_step1 <== leaf46_pathprod_step0 * (1 - comp_node33_out);
    signal leaf46_pathprod_step2 <== leaf46_pathprod_step1 * (1 - comp_node41_out);
    signal leaf46_pathprod_step3 <== leaf46_pathprod_step2 * comp_node45_out;
    signal path_leaf46_active <== leaf46_pathprod_step3;
    // Leaf 46: Prediction=1, PathSignal: path_leaf46_active
    signal leaf46_contribution <== path_leaf46_active * 1;
    signal leaf47_pathprod_step0 <== (1 - comp_node0_out) * comp_node32_out;
    signal leaf47_pathprod_step1 <== leaf47_pathprod_step0 * (1 - comp_node33_out);
    signal leaf47_pathprod_step2 <== leaf47_pathprod_step1 * (1 - comp_node41_out);
    signal leaf47_pathprod_step3 <== leaf47_pathprod_step2 * (1 - comp_node45_out);
    signal path_leaf47_active <== leaf47_pathprod_step3;
    // Leaf 47: Prediction=1, PathSignal: path_leaf47_active
    signal leaf47_contribution <== path_leaf47_active * 1;
    signal leaf51_pathprod_step0 <== (1 - comp_node0_out) * (1 - comp_node32_out);
    signal leaf51_pathprod_step1 <== leaf51_pathprod_step0 * comp_node48_out;
    signal leaf51_pathprod_step2 <== leaf51_pathprod_step1 * comp_node49_out;
    signal leaf51_pathprod_step3 <== leaf51_pathprod_step2 * comp_node50_out;
    signal path_leaf51_active <== leaf51_pathprod_step3;
    // Leaf 51: Prediction=1, PathSignal: path_leaf51_active
    signal leaf51_contribution <== path_leaf51_active * 1;
    signal leaf52_pathprod_step0 <== (1 - comp_node0_out) * (1 - comp_node32_out);
    signal leaf52_pathprod_step1 <== leaf52_pathprod_step0 * comp_node48_out;
    signal leaf52_pathprod_step2 <== leaf52_pathprod_step1 * comp_node49_out;
    signal leaf52_pathprod_step3 <== leaf52_pathprod_step2 * (1 - comp_node50_out);
    signal path_leaf52_active <== leaf52_pathprod_step3;
    // Leaf 52: Prediction=0, PathSignal: path_leaf52_active
    signal leaf52_contribution <== path_leaf52_active * 0;
    signal leaf54_pathprod_step0 <== (1 - comp_node0_out) * (1 - comp_node32_out);
    signal leaf54_pathprod_step1 <== leaf54_pathprod_step0 * comp_node48_out;
    signal leaf54_pathprod_step2 <== leaf54_pathprod_step1 * (1 - comp_node49_out);
    signal leaf54_pathprod_step3 <== leaf54_pathprod_step2 * comp_node53_out;
    signal path_leaf54_active <== leaf54_pathprod_step3;
    // Leaf 54: Prediction=0, PathSignal: path_leaf54_active
    signal leaf54_contribution <== path_leaf54_active * 0;
    signal leaf55_pathprod_step0 <== (1 - comp_node0_out) * (1 - comp_node32_out);
    signal leaf55_pathprod_step1 <== leaf55_pathprod_step0 * comp_node48_out;
    signal leaf55_pathprod_step2 <== leaf55_pathprod_step1 * (1 - comp_node49_out);
    signal leaf55_pathprod_step3 <== leaf55_pathprod_step2 * (1 - comp_node53_out);
    signal path_leaf55_active <== leaf55_pathprod_step3;
    // Leaf 55: Prediction=1, PathSignal: path_leaf55_active
    signal leaf55_contribution <== path_leaf55_active * 1;
    signal leaf57_pathprod_step0 <== (1 - comp_node0_out) * (1 - comp_node32_out);
    signal leaf57_pathprod_step1 <== leaf57_pathprod_step0 * (1 - comp_node48_out);
    signal leaf57_pathprod_step2 <== leaf57_pathprod_step1 * comp_node56_out;
    signal path_leaf57_active <== leaf57_pathprod_step2;
    // Leaf 57: Prediction=0, PathSignal: path_leaf57_active
    signal leaf57_contribution <== path_leaf57_active * 0;
    signal leaf59_pathprod_step0 <== (1 - comp_node0_out) * (1 - comp_node32_out);
    signal leaf59_pathprod_step1 <== leaf59_pathprod_step0 * (1 - comp_node48_out);
    signal leaf59_pathprod_step2 <== leaf59_pathprod_step1 * (1 - comp_node56_out);
    signal leaf59_pathprod_step3 <== leaf59_pathprod_step2 * comp_node58_out;
    signal path_leaf59_active <== leaf59_pathprod_step3;
    // Leaf 59: Prediction=1, PathSignal: path_leaf59_active
    signal leaf59_contribution <== path_leaf59_active * 1;
    signal leaf60_pathprod_step0 <== (1 - comp_node0_out) * (1 - comp_node32_out);
    signal leaf60_pathprod_step1 <== leaf60_pathprod_step0 * (1 - comp_node48_out);
    signal leaf60_pathprod_step2 <== leaf60_pathprod_step1 * (1 - comp_node56_out);
    signal leaf60_pathprod_step3 <== leaf60_pathprod_step2 * (1 - comp_node58_out);
    signal path_leaf60_active <== leaf60_pathprod_step3;
    // Leaf 60: Prediction=1, PathSignal: path_leaf60_active
    signal leaf60_contribution <== path_leaf60_active * 1;
    signal prediction_partial_sum_0 <== leaf5_contribution + leaf6_contribution;
    signal prediction_partial_sum_1 <== prediction_partial_sum_0 + leaf8_contribution;
    signal prediction_partial_sum_2 <== prediction_partial_sum_1 + leaf9_contribution;
    signal prediction_partial_sum_3 <== prediction_partial_sum_2 + leaf12_contribution;
    signal prediction_partial_sum_4 <== prediction_partial_sum_3 + leaf13_contribution;
    signal prediction_partial_sum_5 <== prediction_partial_sum_4 + leaf15_contribution;
    signal prediction_partial_sum_6 <== prediction_partial_sum_5 + leaf16_contribution;
    signal prediction_partial_sum_7 <== prediction_partial_sum_6 + leaf20_contribution;
    signal prediction_partial_sum_8 <== prediction_partial_sum_7 + leaf21_contribution;
    signal prediction_partial_sum_9 <== prediction_partial_sum_8 + leaf23_contribution;
    signal prediction_partial_sum_10 <== prediction_partial_sum_9 + leaf24_contribution;
    signal prediction_partial_sum_11 <== prediction_partial_sum_10 + leaf27_contribution;
    signal prediction_partial_sum_12 <== prediction_partial_sum_11 + leaf28_contribution;
    signal prediction_partial_sum_13 <== prediction_partial_sum_12 + leaf30_contribution;
    signal prediction_partial_sum_14 <== prediction_partial_sum_13 + leaf31_contribution;
    signal prediction_partial_sum_15 <== prediction_partial_sum_14 + leaf36_contribution;
    signal prediction_partial_sum_16 <== prediction_partial_sum_15 + leaf37_contribution;
    signal prediction_partial_sum_17 <== prediction_partial_sum_16 + leaf39_contribution;
    signal prediction_partial_sum_18 <== prediction_partial_sum_17 + leaf40_contribution;
    signal prediction_partial_sum_19 <== prediction_partial_sum_18 + leaf43_contribution;
    signal prediction_partial_sum_20 <== prediction_partial_sum_19 + leaf44_contribution;
    signal prediction_partial_sum_21 <== prediction_partial_sum_20 + leaf46_contribution;
    signal prediction_partial_sum_22 <== prediction_partial_sum_21 + leaf47_contribution;
    signal prediction_partial_sum_23 <== prediction_partial_sum_22 + leaf51_contribution;
    signal prediction_partial_sum_24 <== prediction_partial_sum_23 + leaf52_contribution;
    signal prediction_partial_sum_25 <== prediction_partial_sum_24 + leaf54_contribution;
    signal prediction_partial_sum_26 <== prediction_partial_sum_25 + leaf55_contribution;
    signal prediction_partial_sum_27 <== prediction_partial_sum_26 + leaf57_contribution;
    signal prediction_partial_sum_28 <== prediction_partial_sum_27 + leaf59_contribution;
    signal prediction_partial_sum_29 <== prediction_partial_sum_28 + leaf60_contribution;
    out_prediction <== prediction_partial_sum_29;

}

// To use this, instantiate it in a main component
component main {public [features]} = DecisionTree(8);