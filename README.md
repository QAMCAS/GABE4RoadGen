# Automatic Generation of Challenging Road Networks for ALKS Testing based on Bézier Curves and Search

This repository includes data and other artifacts supporting the results obtained for the paper "Automatic Generation of Challenging Road Networks for ALKS Testing based on Bézier Curves and Search" submitted  and currently under review at the Journal of Software: Evolution and Process - Search-based Software Testing Special Issue.

## Paper Summary
In this paper, we outline an approach for automatic generation of challenging road networks for virtual testing of an automated lane keep system. Based on a set of control points, we construct a parametric curve that represents a road network, which defines the dynamic driving task, an automated lane keep system equipped vehicle has to perform. Changing control points has global influence on the resulting road geometry. Our approach uses search to find control point sets that result in a challenging road geometry, eventually forcing the vehicle to leave the intended path. We apply our approach in different search variants and evaluate the performance regarding test efficiency and diversity of failing test cases. In addition, we evaluate different genetic meta-parameter configurations to investigate if certain configurations can be seen as optimal, hence lead to better results than others.

## Repository Structure

In the following a short overview of the repository structure is given.
### Folders:

- *empirical_evaluation_results*

    1. **gabe_search_variants_results**: This folder contains the results obtained for our evaluation of the *GA-Bézier Search Variant A*, *GA-Bézier Search Variant B*, and *GA-Bézier Search Variant C*. Each search variant folder contains two additional subfolders:
    
        1. **results_test_runs**: Within this folder the detailed results for the respective 20 test runs are included. 

        2. **failing_TC**: This folder contains the failed test cases found for the respective search variant and within the 20 test runs. In addition to that, within *Failing_Road_Networks*, figures depicting the failing road networks within each test run are included. *Frechet_Distance_Results* contains the heatmaps representing the diversity of the failing test cases for each test run. 
    <br/><br/>
    1. **gabe_meta_parameter_results**: This folder contains the results obtained for our empirical evaluation of the 64 GA meta-parameter combinations and their respective 20 test runs applied on *GA-Bézier Search Variant A*.
        
        1. **results_test_runs**: Within this folder the detailed results for the respective 20 test runs are included.

        2. **failing_TC**: This folder contains the failed test cases found for all 64 meta-parameter combinations and within their respective 20 runs.

- *figures*: This folder contains additional figures used for our result evaluation which are included in the paper.

## Additional Information
The results provided within this repository represent and support the findings of the study. Source code related data and artefacts of the study are available from the authors upon reasonable request.
