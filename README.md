# Using Genetic Algorithms for Automating ALKS Testing

This repository includes data and other artifacts supporting the results obtained for the paper "Using Genetic Algorithms for Automating ALKS Testing" submitted  and currently under review at the Journal of Software: Evolution and Process - Search-based Software Testing Special Issue.

## Paper Summary
### Needs to be updated 
In this paper, we outline an approach for the automatic generation of challenging road networks for virtual testing of an automated lane-keep system. Based on a set of control points, we construct a parametric curve that represents a road network, which defines the dynamic driving task, an automated lane-keep system equipped vehicle has to perform. Changing control points has a global influence on the resulting road geometry. Our approach uses search to find control point sets that result in a challenging road, eventually forcing the vehicle to leave the intended path. We apply our approach in different search variants and evaluate the performance regarding test efficiency and diversity of failing test cases. In addition, we evaluate different genetic meta-parameter configurations to investigate if certain configurations can be seen as optimal, hence leading to better results than others.

## Repository Structure

In the following a short overview of the repository structure is given.
### Folders:

- *empirical_evaluation_results*

    1. **gabe_control_parameter_results**: This folder contains the results obtained in our empirical evaluation of the 80 GA control-parameter configurations and their respective 10 test runs applied on *GA-Bézier Search Variant A*, *GA-Bézier Search Variant B*, and *GA-Bézier Search Variant C*. 
    Within each search variant folder, the following subfolders are included:
        
        1. **results_test_runs**: Within this folder the results of each of the 80 configurations and their respective 10 test runs are provided.

        2. **failing_TC**: This folder contains the failed test cases found for all 80 control-parameter configurations and within their respective 10 test runs.

        3. **surface_plots**: This folder includes the produced surface plots for each search variant that show the influence of population size, crossing probability and mutation probability on the discussed evaluation metrics, i.e., failure probability, Fréchet distance, sparseness and Time-to-Failure. In addition to the provided PDF plots, the folder includes also interactive plots as HTML files.

        4. **gabe_search_variant_<a/b/c>_Master_CSV.csv**: This file includes the complete results of the respective search variant in a single csv file. 

   
    2. **bezier_random_results**: This folder contains the results obtained within the 10 test runs of the *Bezier Random (RD_BEZ)* approach. The folder is structured in the same way as *gabe_control_parameter_results* (see above) with the only exception that here no surface plots are present.
    
    3. **random_tool_comp_results**: This folder contains the results obtained within the 10 test runs of the *Naive Random (RD_TC)* approach. The folder is structured in the same way as *gabe_control_parameter_results* (see above) with the only exception that here no surface plots are included.
    
    4. **frenetic_results**: This folder includes the *Frenetic_Master_CSV.csv* file which summarizes the results obtained within the 10 test runs of the *Frenetic* tool. 
    <br/><br/>

- *test_generators*: This folder contains the implementations of the different approaches, i.e., *GA-Bézier Search Variant A*, *GA-Bézier Search Variant B*, *GA-Bézier Search Variant C*, *Bezier Random (RD_BEZ)*, and *Naive Random (RD_TC)*. Each of the implementations can be directly used with the code-pipeline which was developed in the scope of the Cyber-Physical Systems Testing Tool Competition (SBST2021). 

    For setting up the simulation environment and code-pipeline we refer the interesting reader to the guides and examples included in https://github.com/se2p/tool-competition-av. It should be noted that a licence is required for the [BeamNG.tech](https://www.beamng.tech/) driving simulator.

