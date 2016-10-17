'''Hyperparameter optimizer'''

import os
import sys
import time

import numpy as np

from equivariant import run

def random_independent(n_trials=3, fixedParams = True):
	y_best = 0.
	best_params = {}
	best_num_filters = 0
	if fixedParams:
		learning_rates = np.load("trialParams/learning_rates.npy")
		batch_sizes = np.load("trialParams/batch_sizes.npy")
		stddev_multipliers = np.load("trialParams/stddev_multipliers.npy")
		#for debug
		print("learning rates:", learning_rates)
		print("batch sizes:", batch_sizes)
		print("stddevs:", stddev_multipliers)
		#make sure user parameters agree
		if n_trials != learning_rates.shape[0]:
			print("WARNING: Setting ntrials to loaded experiment files: ", learning_rates.shape[0])
			ntrials = learning_rates.shape[0]
	#number of filters to try
	filters = [2, 4, 6, 8, 10, 12, 14]

	for f in filters:
		print("Processsing for num Filters:", f)
		for i in xrange(n_trials):
			n_epochs = 500
			n_filters = [2, 4, 6, 8, 10, 12, 14]

			#switch here as well
			if fixedParams:
				lr = learning_rates[i]
				batch_size = batch_sizes[i]
				std_mult = stddev_multipliers[i]
			else:
				lr = log_uniform_rand(1e-2, 1e-4)
				batch_size = int(log_uniform_rand(64,256))
				std_mult = uniform_rand(0.05, 1.0)
			print
			print('Learning rate: %f' % (lr,))
			print('Batch size: %f' % (batch_size,))
			print('Stddev multiplier: %f' % (std_mult,))
			print
			y = run(model='conv_so2',
				lr=lr,
				batch_size=batch_size,
				std_mult=std_mult,
				n_epochs=n_epochs,
				n_filters=n_filters,
				trial_num=i,
				combine_train_val=False)
			if y > y_best:
				y_best = y
				best_params['lr'] = lr
				best_params['batch_size'] = batch_size
				best_params['std_mult'] = std_mult
				best_num_filters = f

		print
		print
		print('Best y so far')
		print y_best
		print('Best params so far')	
		print best_params
		print
		print

	print('Best y overall')
	print y_best
	print('Best params overall')	
	print best_params

	y = []
	for i in xrange(5):
		y.append(run(model='conv_so2',
			lr=best_params['lr'],
			batch_size=best_params['batch_size'],
			std_mult=best_params['std_mult'],
			n_epochs=n_epochs,
			n_filters=best_num_filters,
			trial_num='T-'+str(i),
			combine_train_val=True))
		print
		print('Current y: %f' % (y[i],))
		print

	print('Best num filters:', best_num_filters)
	print('Best y overall')
	print y_best
	print('Best params overall')	
	print best_params
	# Compute statistics
	print y
	y = np.asarray(y)
	mean = np.mean(y)
	print('Mean: %f' % (mean,))
	print('Std: %f' % (np.std(y),))

def binary_thinning(n_trials=256):
	y_best = 0.
	best_params = {}
	n_rounds = int(np.log2(n_trials))
	print n_rounds
	
	# Generate parameters
	params = {}
	for trial in xrange(n_trials):
		params[trial] = {}
		params[trial]['lr'] = log_uniform_rand(5e-2, 1e-4)
		params[trial]['batch_size'] = int(uniform_rand(50, 500))
		params[trial]['n_filters'] = int(uniform_rand(10,40))
	
	# For each trial in list, run experiment
	results = np.zeros((n_trials,))
	sorted_args = np.argsort(-results)
	for j in xrange(n_rounds):
		i = 0
		for trial in sorted_args[:(n_trials/(2**j))]:
			print params[trial]
			params[trial]['y'] = run(model='deep_steer',
									 lr=params[trial]['lr'],
									 batch_size=params[trial]['batch_size'],
									 n_epochs=10*(2**j),
									 n_filters=params[trial]['n_filters'],
									 trial_num=str(j)+'-'+str(i))
			results[trial] = params[trial]['y']
			if params[trial]['y'] > y_best:
				y_best = params[trial]['y']
				best_trial = trial
			print
			print
			print('Best y so far')
			print params[best_trial]
			print
			print
			i += 1
		
		# Sort and reset running best
		sorted_args = np.argsort(-results)
		y_best = 0.
	
	print('Best y in this batch')
	print params[best_trial]

def uniform_rand(min_, max_):
	gap = max_ - min_
	return gap*np.random.rand() + min_

def log_uniform_rand(min_, max_, size=1):
	if size > 1:
		output = []
		for i in xrange(size):
			output.append(10**uniform_rand(np.log10(min_), np.log10(max_)))
	else:
		output = 10**uniform_rand(np.log10(min_), np.log10(max_))
	return output



if __name__ == '__main__':
	random_independent(n_trials=24, fixedParams=True)
	#binary_thinning(64)