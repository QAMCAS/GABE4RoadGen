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

from deap import algorithms
from deap import base
from deap import creator
from deap import tools

from code_pipeline.tests_generation import RoadTestFactory

class GABE_SVB_CP_TestGenerator():
	def __init__(self, time_budget=None, executor=None, map_size=None, timestamp_id=time.strftime("%d%m%Y-%H%M%S"), pop_size=75, cxpb=0.8, mutpb=0.1):
		
		self.time_budget = time_budget
		self.executor = executor
		self.map_size = map_size
		self.number_of_controlpoints = 7
		self.step_size = int(self.map_size/self.number_of_controlpoints)
		self.POP_SIZE = pop_size
		self.NGEN = 100000 
		self.max_oob_percentage = 0.0
		self.min_oob_distance = 2.0
		self.timestamp_id = timestamp_id
		self.cxpb = cxpb
		self.mutpb = mutpb
		self.fail_cnt = 0
		
		creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
		creator.create("Individual", list, fitness=creator.FitnessMin)
		
		self.toolbox = base.Toolbox()
		self.toolbox.register("individual", self._create_control_point_individual, creator.Individual)
		self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
		self.toolbox.register("evaluate", self._evaluate_control_point_individual)
		self.toolbox.register("mate", tools.cxTwoPoint)
		self.toolbox.register("mutate", self._control_point_mutation, indpb=0.5)
		self.toolbox.register("select", tools.selTournament, tournsize=3)

		# specify where the results should be stored
		self.csv_results_path = 'empirical_evaluation_results\\gabe_control_parameter_results\\gabe_search_variant_b'
		self.evaluation_folder_path = os.path.join(self.csv_results_path, "results_test_runs", "POP-{}_cxpb-{}_mutpb-{}".format(self.POP_SIZE, self.cxpb, self.mutpb))
		self.failing_TC_folder_path = os.path.join(self.csv_results_path, "failing_TC", "POP-{}_cxpb-{}_mutpb-{}".format(self.POP_SIZE, self.cxpb, self.mutpb))
		
		try:
			os.makedirs(self.evaluation_folder_path, exist_ok=True)
		except OSError as error:
			print("Directory '{}' can not be created".format(self.evaluation_folder_path))

		try:
			os.makedirs(self.failing_TC_folder_path, exist_ok=True)
		except OSError as error:
			print("Directory '{}' can not be created".format(self.failing_TC_folder_path))

		run_nr = len(os.listdir(self.evaluation_folder_path))
		
		self.unique_filename = '{}-RUN_POP-{}_cxpb-{}_mutpb-{}_{}'.format(run_nr, self.POP_SIZE, self.cxpb, self.mutpb, self.timestamp_id)

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
	
	def _create_control_point_individual(self,icls):
	
		control_point_individual = self._initial_controlpoints()
		
		return icls(control_point_individual)
   
	def _evaluate_control_point_individual(self,individual):

		self.bezier_set = self._bezier_calculation(individual)
		self.road_points = []
		for i in range(len(self.bezier_set[0])):
			x_bezier = self.bezier_set[0][i]
			y_bezier = self.bezier_set[1][i]

			self.road_points.append((x_bezier, y_bezier))

		the_test = RoadTestFactory.create_road_test(self.road_points)
		
		self.test_outcome, self.description, self.execution_data = self.executor.execute_test(the_test)

		if self.test_outcome == 'FAIL':
			print("TESTCASE FAILED - RESTARTING GA")

			oob_percentage = [state.oob_percentage for state in self.execution_data]
			self.max_oob_percentage = max(oob_percentage)
			log.info("Collected %d percentage states information. Max is %.3f", len(oob_percentage), max(oob_percentage))

			oob_distance = [state.oob_distance for state in self.execution_data]
			self.min_oob_distance = min(oob_distance)
			log.info("Collected %d distance states information. Max is %.3f", len(oob_distance), min(oob_distance))
			

			log.info("test_outcome %s", self.test_outcome)
			log.info("description %s", self.description)

			if self.executor.road_visualizer:
				sleep(5)
			
			self._csv_writer(individual)
			
			# RESTARTING THE GA
			self.control_point_set = self._initial_controlpoints()
			self.hof = self._geneticalgorithm()
			
		log.info("test_outcome %s", self.test_outcome)
		log.info("description %s", self.description)

		if self.executor.road_visualizer:
				sleep(5)
		
		if self.test_outcome != 'ERROR' and self.test_outcome != 'INVALID':
			oob_percentage = [state.oob_percentage for state in self.execution_data]
			self.max_oob_percentage = max(oob_percentage)
			log.info("Collected %d percentage states information. Max is %.3f", len(oob_percentage), max(oob_percentage))
			
			oob_distance = [state.oob_distance for state in self.execution_data]
			self.min_oob_distance = min(oob_distance)
			log.info("Collected %d distance states information. Min is %.3f", len(oob_distance), min(oob_distance))

			oob = self.min_oob_distance
			
		else:
			self.max_oob_percentage = 0.0
			self.min_oob_distance = 2.0
			oob = self.min_oob_distance
			
		self._csv_writer(individual)
		
		log.info("Remaining Time: %s", str(self.executor.get_remaining_time()))
		return (oob),
   
	def _control_point_mutation(self,individual, indpb):

		cpx_mutation_range = (self.map_size/40) # Mutate cpx within range (dep. on mapsize) around old value 
		cpy_mutation_range = (self.map_size/40) # Mutate cpx within range (dep. on mapsize) around old value 

		max_guesses = 1000
		
		for cp in range(len(individual[0])):
			if not cp == 0: # Don't mutate the first control point to avoid map boundary violations
				if not cp == (len(individual[0]) - 1): # Don't mutate the last control point to avoid map boundary violations

					if random.uniform(0,1) < indpb: #Check independent probability for every chromosom (controlpoint) pair 
						cp_x = individual[0][cp]
						if random.uniform(0,1) > 0.5: #Increase cp_x value during mutation
							new_value_x = cp_x + random.uniform(0, cpx_mutation_range)
							guess_cnt = 0
							while  new_value_x >= self.map_size: # Check if new_value_x is within map boundaries 
								guess_cnt += 1
								new_value_x = cp_x + random.uniform(0, cpx_mutation_range)
								if guess_cnt > max_guesses:
									#old cp_x as new individual value when max guesses are made
									new_value_x = cp_x
									#print("MAX GUESSES ACHIEVED-1. New Value is: ", new_value_x)

							individual[0][cp] = new_value_x
							#print("mutated cp_x Nr_{}: ".format(cp), individual[0][cp])

						else: # Decrease cp_x Value during Mutation
							new_value_x = cp_x - random.uniform(0, cpx_mutation_range)
							guess_cnt = 0
							while  new_value_x <= 0: # Check if new_value_x is within map boundaries 
								guess_cnt += 1
								new_value_x = cp_x - random.uniform(0, cpx_mutation_range)
								if guess_cnt > max_guesses:
									#old cp_x as new individual value when max guesses are made
									new_value_x = cp_x
									#print("MAX GUESSES ACHIEVED-2. New Value is: ", new_value_x)
								  
							individual[0][cp] = new_value_x
							#print("mutated cp_x Nr_{}: ".format(cp), individual[0][cp])

						#print("cp_y: Nr_{}: ".format(cp), individual[1][cp])
						cp_y = individual[1][cp]
						if random.uniform(0,1) > 0.5: #Increase cp_y value during mutation
							new_value_y = cp_y + random.uniform(0, cpy_mutation_range)
							guess_cnt = 0
							while  new_value_y >= self.map_size: # Check if new_value_y is within map boundaries 
								guess_cnt += 1
								new_value_y = cp_y + random.uniform(0, cpy_mutation_range)
								if guess_cnt > max_guesses:
									#old cp_y as new individual value when max guesses are made
									new_value_y = cp_y
									#print("MAX GUESSES ACHIEVED-3. New Value is: ", new_value_y)

							individual[1][cp] = new_value_y
							#print("mutated cp_y Nr_{}: ".format(cp), individual[1][cp])

						else: # Decrease cp_y Value during Mutation
							new_value_y = cp_y - random.uniform(0, cpy_mutation_range)
							guess_cnt = 0
							while  new_value_y <= 0: # Check if new_value_y is within map boundaries 
								guess_cnt += 1
								new_value_y = cp_y - random.uniform(0, cpy_mutation_range)
								if guess_cnt > max_guesses:
									#old cp_y as new individual value when max guesses are made
									new_value_y = cp_y
									#print("MAX GUESSES ACHIEVED-4. New Value is: ", new_value_y)

							individual[1][cp] = new_value_y
							#print("mutated cp_y Nr_{}: ".format(cp), individual[1][cp])


		return (individual),

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
 
	def _geneticalgorithm(self):
		pop = self.toolbox.population(n=self.POP_SIZE)
		hof = tools.HallOfFame(1)
		stats = tools.Statistics(lambda ind: ind.fitness.values)
		stats.register("min", np.min)
		stats.register("max", np.max)

		pop = algorithms.eaSimple(pop, self.toolbox, cxpb=self.cxpb, mutpb=self.mutpb, ngen=self.NGEN, stats=stats, halloffame=hof, verbose=True) 

		return hof

	def start(self):

		# Some debugging
		log.info("Starting test generation. Remaining time %s", self.executor.get_remaining_time())

		self.step_size = int(self.map_size/self.number_of_controlpoints)
		
		self.control_point_set = self._initial_controlpoints()

		self.hof = self._geneticalgorithm()
