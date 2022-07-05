"""
Copyright (C) 2022, F. Klück and L. Klampfl.
This code intentional usage is for obtaining rusults for the paper "Using Genetic Algorithms for Automating ALKS Testing" 
submitted and currently under review in the Journal of Software: Evolution and Process - Search-based testing Special Issue.

"""

import os
from time import sleep
import time
import logging as log
import csv
from random import randint
import time


from code_pipeline.tests_generation import RoadTestFactory

class Random_Tool_Comp_TestGenerator():
    def __init__(self, time_budget=None, executor=None, map_size=None, timestamp_id=time.strftime("%d%m%Y-%H%M%S"),):
        
        self.time_budget = time_budget
        self.executor = executor
        self.map_size = map_size
        self.max_oob_percentage = 0.0
        self.min_oob_distance = 2.0
        self.timestamp_id = timestamp_id
        self.fail_cnt = 0
        
        # specify where the results should be stored
        self.csv_results_path = 'empirical_evaluation_results\\random_tool_comp'
        self.evaluation_folder_path = os.path.join(self.csv_results_path, "results_test_runs")
        self.failing_TC_folder_path = os.path.join(self.csv_results_path, "failing_TC")
        
        try:
            os.makedirs(self.evaluation_folder_path, exist_ok=True)
        except OSError as error:
            print("Directory '{}' can not be created".format(self.evaluation_folder_path))

        try:
            os.makedirs(self.failing_TC_folder_path, exist_ok=True)
        except OSError as error:
            print("Directory '{}' can not be created".format(self.failing_TC_folder_path))

        run_nr = len(os.listdir(self.evaluation_folder_path))
        
        self.unique_filename = '{}-RUN_Random_{}'.format(run_nr, self.timestamp_id)

        self.csv_failing_filepath = os.path.join(self.failing_TC_folder_path,self.unique_filename + '.csv')
        
        with open(self.csv_failing_filepath, mode='w', newline='') as file:
            ftc_writer = csv.writer(file, delimiter=',')
            ftc_writer.writerow(["individual", "road_points", "test_outcome", "description", "timestamp"])


        self.csv_eval_filepath = os.path.join(self.evaluation_folder_path, self.unique_filename + '.csv')
        with open(self.csv_eval_filepath, mode='a', newline='') as file:
                eval_writer = csv.writer(file, delimiter=',')
                eval_writer.writerow(["min_oob_distance", "max_oob_percentage", "test_outcome", "description", "timestamp"])
 

    def _initial_controlpoints(self):
        
        # Taken from tool competitions sample_test_generators and integrated here.
        # Pick up random points from the map. They will be interpolated anyway to generate the road
        road_points = []
        for i in range(0, 3):
            road_points.append((randint(0, self.map_size), randint(0, self.map_size))) 

        return road_points
    
    def _evaluate_control_point_individual(self,individual):


        #log.info("Generated test using: %s", self.road_points)
        self.the_test = RoadTestFactory.create_road_test(individual)
        
        self.test_outcome, self.description, self.execution_data = self.executor.execute_test(self.the_test)
  

        log.info("test_outcome %s", self.test_outcome)
        log.info("description %s", self.description)

        if self.executor.road_visualizer:
                sleep(5)
        
        if self.test_outcome != 'ERROR' and self.test_outcome != 'INVALID':
            # Plot the OOB_Percentage: How much the car is outside the road?
            oob_percentage = [state.oob_percentage for state in self.execution_data]
            self.max_oob_percentage = max(oob_percentage)
            log.info("Collected %d percentage states information. Max is %.3f", len(oob_percentage), max(oob_percentage))
            
            # Plot the OOB_distance: How much the car is outside the road?
            oob_distance = [state.oob_distance for state in self.execution_data]
            self.min_oob_distance = min(oob_distance)
            log.info("Collected %d distance states information. Min is %.3f", len(oob_distance), min(oob_distance))

            #oob = self.max_oob_percentage
            oob = self.min_oob_distance
            
        else:
            self.max_oob_percentage = 0.0
            self.min_oob_distance = 2.0
            #oob = self.max_oob_percentage
            oob = self.min_oob_distance
            
   
        self._csv_writer(individual)
        
        log.info("Remaining Time: %s", str(self.executor.get_remaining_time()))
        #return (oob),
   
    def _csv_writer(self, individual):
        timestr = time.strftime("%d%m%Y-%H%M%S")
        #writing failed testcases to csv file
        if self.test_outcome != 'PASS' and self.test_outcome != 'ERROR' and self.test_outcome != 'INVALID':

            print("Max OOB percentage in last simulation: ", self.max_oob_percentage)
            print("OOB distance in last simulation: ", self.min_oob_distance)

            
            with open(self.csv_failing_filepath, mode='a', newline='') as file:
                ftc_writer = csv.writer(file, delimiter=',')
                ftc_writer.writerow([individual, self.the_test, self.test_outcome, self.description, timestr])
        
        elif self.test_outcome == 'PASS':
            print("Max OOB percentage in last simulation: ", self.max_oob_percentage)
            print("OOB distance in last simulation: ", self.min_oob_distance)
        else:
            self.max_oob_percentage = 0.0
            self.min_oob_distance = 2
            print("Max OOB percentage in last simulation: ", self.max_oob_percentage)
            print("OOB distance in last simulation: ", self.min_oob_distance)
        
        with open(self.csv_eval_filepath, mode='a', newline='') as file:
                eval_writer = csv.writer(file, delimiter=',')
                eval_writer.writerow([self.min_oob_distance, self.max_oob_percentage, self.test_outcome, self.description, timestr])
 
    def start(self):
        
        while self.executor.get_remaining_time() > 0:
            # Some debugging
            log.info("Starting test generation. Remaining time %s", self.executor.get_remaining_time())

            self.control_point_set = self._initial_controlpoints()

            self._evaluate_control_point_individual(self.control_point_set)




        