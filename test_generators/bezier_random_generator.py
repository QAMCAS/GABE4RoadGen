"""
Copyright (C) 2022, F. Klück and L. Klampfl.
This code intentional usage is for obtaining rusults for the paper "Using Genetic Algorithms for Automating ALKS Testing" 
submitted and currently under review in the Journal of Software: Evolution and Process - Search-based testing Special Issue.

"""

import random
import numpy as np
import scipy.interpolate as si
import matplotlib.pyplot as plt
from scipy.special import binom
from shutil import copyfile
import xml.etree.ElementTree as ET
import os
from time import sleep
import time
import logging as log
import csv

from code_pipeline.tests_generation import RoadTestFactory

class Bezier_Random_TestGenerator():
    def __init__(self, time_budget=None, executor=None, map_size=None, timestamp_id=time.strftime("%d%m%Y-%H%M%S")):
        
        self.time_budget = time_budget
        self.executor = executor
        self.map_size = map_size
        self.number_of_controlpoints = 7
        self.step_size = int(self.map_size/self.number_of_controlpoints)
        self.max_oob_percentage = 0.0
        self.min_oob_distance = 2.0
        self.timestamp_id = timestamp_id
        self.fail_cnt = 0
        
        # specify where the results should be stored
        self.csv_results_path = 'empirical_evaluation_results\\bezier_random'
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
 

    def _Bernstein(self, n, k):
        """Bernstein polynomial.
        """
        coeff = binom(n, k)

        def _bpoly(x):
            return coeff * x ** k * (1 - x) ** (n - k)

        return _bpoly
    
    def _Bezier(self, points, num=200): #max permissable number of roadpoints is 500
        """Build Bézier curve from points.

        """
        N = len(points)
        t = np.linspace(0, 1, num=num)
        curve = np.zeros((num, 2))
        for ii in range(N):
            curve += np.outer(self._Bernstein(N - 1, ii)(t), points[ii])

        return curve
        
    def _bezier_calculation(self, control_point_set):
        bezier_set = []

        for i in range(0,len(control_point_set),2):
            x_control = np.asarray(control_point_set[i])
            y_control = np.asarray(control_point_set[i+1])
            x_bezier, y_bezier = self._Bezier(list(zip(x_control, y_control)), num = 200).T #max permissable number of roadpoints is 500
            bezier_set.append(x_bezier)
            bezier_set.append(y_bezier)   

        return bezier_set

    
    def _initial_controlpoints(self):
        loop_cnt = 0
        control_point_set = []
        x_control_points = []
        y_control_points = []
        for cp in range(self.number_of_controlpoints):
            
            if cp == 0: # Fixed coordinates for cp_0
                x_cp = random.uniform( ((self.map_size/2)-(self.map_size/10)), ((self.map_size/2)+(self.map_size/10)))  # Set first Control Point in x direction in range around map middle
                y_cp = (self.map_size/40) # y_cp slightly above map-boundary 
            if cp != 0:
                x_cp = random.randint(10, self.map_size-5)
                y_cp = cp * self.step_size

            x_control_points.append(x_cp)
            y_control_points.append(y_cp)

        control_point_set.append(x_control_points)
        control_point_set.append(y_control_points)

        return control_point_set
    
    def _evaluate_control_point_individual(self,individual):

        self.bezier_set = self._bezier_calculation(individual)
        self.road_points = []
        for i in range(len(self.bezier_set[0])):
            x_bezier = self.bezier_set[0][i]
            y_bezier = self.bezier_set[1][i]
            #print(x_bezier)
            #print(y_bezier)
            self.road_points.append((x_bezier, y_bezier))

        #log.info("Generated test using: %s", self.road_points)
        the_test = RoadTestFactory.create_road_test(self.road_points)
        
        self.test_outcome, self.description, self.execution_data = self.executor.execute_test(the_test)
     
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
                ftc_writer.writerow([individual, self.road_points, self.test_outcome, self.description, timestr])
        
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
        self.step_size = int(self.map_size/self.number_of_controlpoints)
        
        while self.executor.get_remaining_time() > 0:
            # Some debugging
            log.info("Starting test generation. Remaining time %s", self.executor.get_remaining_time())

            self.control_point_set = self._initial_controlpoints()

            self._evaluate_control_point_individual(self.control_point_set)




        