# -*- coding utf-8 -*-

# This script gathers the routines to extract kilosort/phy (kwikteam) generated units features,
# stored in an instance of DataManager():
# - Sampling rate (30Khz)
# - Spike times in sample units
# - Spikes times in seconds
# - Spikes clusters, cluster corresponding to each spike of Spike times
# - Clusters indexes, array of the cluster indexes (one occurence of each)
# - attributed Spike times and Spike samples, lists of n_clusters np arrays of the form [[cluster_idx1, t1, t2...tn], ...] with t1... in seconds or samples
# - Instantaneous Firing rate, lists of n_clusters np arrays of the form [[cluster_idx1, IFR1, IFR2...IFRn], ...]
# - CrossCorrelograms between units
# - Vizualisation tool

# >> How to use it: <<
# Store this script in the folder which also contains the 1) params.py file 2) spike_times.npy file and 3) spike_clusters.npy file,
# all being generated by kilosort and exploited/modified by phy (kikteam).
# Then launch python or ipython from any terminal, and "import FeaturesExtraction". Here it is, you can instanciate DataManager by doing "data = DataManager()".
# Then visualize the Mean Firing Rate, the Instantaneous Firing Rate and the auto/cross correlograms of units thanks to the visualization() method.

# Maxime Beau, 2017-05-10



import numpy as np
from scipy import signal

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')

import os, sys
sys.path.append("/Users/maximebeau/phy")
from phy.utils._types import _as_array # phy, kwikteam
from phy.io.array import _index_of, _unique # phy, kwikteam

def indices(a, func):
    return [i for (i, val) in enumerate(a) if func(val)]

def _increment(arr, indices):
    """Increment some indices in a 1D vector of non-negative integers.
    Repeated indices are taken into account."""
    arr = _as_array(arr)
    indices = _as_array(indices)
    bbins = np.bincount(indices)
    arr[:len(bbins)] += bbins
    return arr


def _diff_shifted(arr, steps=1):
    arr = _as_array(arr)
    return arr[steps:] - arr[:len(arr) - steps]


def _create_correlograms_array(n_clusters, winsize_bins):
	'''3D matrix of n_clusters x n_clusters x window size in amount of bins'''
	return np.zeros((n_clusters, n_clusters, winsize_bins // 2 + 1), dtype=np.int32)

def _symmetrize_correlograms(correlograms):
    """Return the symmetrized version of the CCG arrays."""

    n_clusters, _, n_bins = correlograms.shape
    assert n_clusters == _

    # We symmetrize c[i, j, 0].
    # This is necessary because the algorithm in correlograms()
    # is sensitive to the order of identical spikes.
    correlograms[..., 0] = np.maximum(correlograms[..., 0],
                                      correlograms[..., 0].T)

    sym = correlograms[..., 1:][..., ::-1]
    sym = np.transpose(sym, (1, 0, 2))

    return np.dstack((sym, correlograms))

class DataManager():
	'''Has to be informed of the directory of kilosort output (files reshaped by phy).
	The directory can be provided as argument. If no argument is provided, the used directory is the current working directory.

	methods() -> attributes:

	chdir() -> .__dir__: directory to seek for data and generate plots.

	load_sampleRate() -> .sample_rate: Sampling rate (30Khz)

	load_spsamples() -> .spike_samples: Spike times in sample units

	calcul_sptimes() -> .spike_times: Spikes times in seconds

	load_spclusters() -> .spike_clusters: Spikes clusters, cluster corresponding to each spike of Spike times

	extract_cIds() -> .clusters, .spike_clusters_i: Clusters numbers (unique occurence) and indexes in the array

	attribute_spikeSamples_Times() -> .attributed_spikeSamples, .attributed_spikeTimes: attributed Spike times and Spike samples, lists of n_clusters np arrays of the form [[cluster_idx1, t1, t2...tn], ...] with t1... in seconds or samples

	InstFR() -> .IFR: Instantaneous Firing rate, lists of n_clusters np arrays of the form [[cluster_idx1, IFR1, IFR2...IFRn], ...]

	MeanFR() -> .MFR: Mean Firing rate, lists of n_clusters np arrays of the form [[cluster_idx1, MFR], ...]

	CCG() -> .correlograms: all crossCorrelograms in a n_clusters x n_clusters x winsize_bins matrix.

	visualize() -> Vizualisation tool'''

	def __init__(self, directory=None):
		if directory==None:
			directory = os.getcwd()
		os.chdir(directory)
		self.__dir__ = directory

	def chdir(self, directory="/Volumes/DK_students1/2017-04-08/"):
		'''chdir() -> .__dir__: directory to seek for data and generate plots.'''
		os.chdir(directory)
		self.__dir__ = directory

	def load_sampleRate(self):
		'''load_sampleRate() -> .sample_rate: Sampling rate (30Khz)'''
		try:
			print("Sample rate already loaded: ", self.sample_rate)
		except:
			import params
			self.sample_rate = params.sample_rate
			print("Sample rate loaded.")
		return self.sample_rate

	def load_spsamples(self):
		'''load_spsamples() -> .spike_samples: Spike times in sample units'''
		try:
			print("Spike samples already loaded. Array shape:", self.spike_samples.shape)
		except:
			self.spike_samples = np.load("spike_times.npy")
			self.spike_samples = self.spike_samples.flatten()
			self.spike_samples = np.asarray(self.spike_samples, dtype=np.float64)
			print("Spike samples loaded.")
		return self.spike_samples

	def calcul_sptimes(self):
		'''calcul_sptimes() -> .spike_times: Spikes times in seconds'''
		try:
			print("Spike times already calculated. Array shape:", self.spike_times.shape)
		except:
			self.load_sampleRate()
			self.load_spsamples()
			self.spike_times = self.spike_samples/self.sample_rate
			self.spike_times = np.asarray(self.spike_times, dtype=np.float64)
			print("Spike times calculated.")
		return self.spike_times

	def load_spclusters(self):
		'''load_spclusters() -> .spike_clusters: Spikes clusters, cluster corresponding to each spike of Spike times'''
		try:
			print("Spike clusters already loaded. Array shape:", self.spike_clusters.shape)
		except:
			self.spike_clusters = np.load("spike_clusters.npy")
			print("Spike clusters loaded.")
		return self.spike_clusters

	def extract_cIds(self):
		'''extract_cIds() -> .clusters, .spike_clusters_i: Clusters numbers (unique occurence) and indexes in the array'''
		try:
			print("Cluster Ids already extracted. Array shape:", self.clusters.shape)
		except:
			self.load_spclusters()
			self.clusters = _unique(self.spike_clusters)
			self.spike_clusters_i = _index_of(self.spike_clusters, self.clusters)
			self.clusters = np.asarray(self.clusters, dtype=np.float64)
			self.spike_clusters_i = np.asarray(self.spike_clusters_i, dtype=np.float64)
			print("Cluster Ids extracted.")
		return self.clusters, self.spike_clusters_i

	def attribute_spikeSamples_Times(self):
		'''attribute_spikeSamples_Times() -> .attributed_spikeSamples, .attributed_spikeTimes: 
		attributed Spike times and Spike samples, lists of n_clusters np arrays of the form 
		[[cluster_idx1, t1, t2...tn], ...] 
		with t1... in seconds or samples'''
		try:
			print("Spike samples and times already attributed. List length:", len(self.attributed_spikeTimes))
		except:
			self.calcul_sptimes()
			self.extract_cIds()
			self.attributed_spikeSamples = []
			for clust in self.clusters:
				d = np.where(self.spike_clusters==clust)
				cluster = np.array([clust], dtype=np.float64)
				arr = np.append(cluster, self.spike_samples[d])
				self.attributed_spikeSamples.append(arr)

			# self.attributed_spikeSamples = [[i[0], [el*self.sample_rate for el in i[1:]]] for i in self.attributed_spikeTimes] # makes a list
			self.attributed_spikeTimes = [x.copy() for x in self.attributed_spikeSamples]
			for i, x in enumerate(self.attributed_spikeTimes):
				self.attributed_spikeTimes[i][1:] = x[1:]/self.sample_rate
			print("Spike samples and times attributed.")
		return self.attributed_spikeSamples, self.attributed_spikeTimes

	def InstFR(self, sd = 10):
		'''InstFR() -> .IFR: Instantaneous Firing rate, lists of n_clusters np arrays of the form [[cluster_idx1, IFR1, IFR2...IFRn], ...]'''
		try:
			print("IFR already calculated. List length:", len(self.IFR))
		except:
			self.attribute_spikeSamples_Times()
			gaussian = signal.gaussian(90, sd)
			self.IFRhist = self.attributed_spikeSamples.copy()
			self.IFR = self.attributed_spikeSamples.copy()
			binEdges = np.arange(0, self.spike_samples[-1], 60)
			for i, x in enumerate(self.attributed_spikeSamples):
				hist = np.histogram(x[1:], binEdges)
				conv = np.convolve(hist[0], gaussian)
				clust = x[0]
				self.IFRhist[i] = np.append(clust, hist[0])
				self.IFR[i] = np.append(clust, conv)
			print("Instantaneous Firing rates calculated.")
		return self.IFR

	def MeanFR(self):
		'''MeanFR() -> .MFR: Mean Firing rate, lists of n_clusters np arrays of the form [[cluster_idx1, MFR], ...]'''
		try:
			print("MFR already calculated. List length:", len(self.MFR))
		except:
			self.attribute_spikeSamples_Times()
			recordLen = self.spike_times[-1] #Approximately length of the whole recording, in seconds
			self.MFR = []
			for i, x in enumerate(self.attributed_spikeTimes):
				self.MFR.append(np.array([self.attributed_spikeTimes[i][0], float(len(self.attributed_spikeTimes[i][1:]))/recordLen]))
			print("Mean firing rate calculated.")
		return self.MFR

	def CCG(self, bin_size=0.0005, window_size=0.080, symmetrize=True):
		'''CCG() -> .correlograms: all crossCorrelograms in a n_clusters x n_clusters x winsize_bins matrix.'''
		try:
			print("CrossCorrelograms already computed.", len(self.correlograms))
		except:
			self.calcul_sptimes()
			self.extract_cIds()
			assert self.sample_rate > 0.
			assert np.all(np.diff(self.spike_times) >= 0), ("The spike times must be increasing.")
			assert self.spike_samples.ndim == 1
			assert self.spike_samples.shape == self.spike_clusters.shape
			bin_size = np.clip(bin_size, 1e-5, 1e5)  # in seconds
			binsize = int(self.sample_rate * bin_size)  # in samples
			assert binsize >= 1

			window_size = np.clip(window_size, 1e-5, 1e5)  # in seconds
			winsize_bins = 2 * int(.5 * window_size / bin_size) + 1
			assert winsize_bins >= 1
			assert winsize_bins % 2 == 1


			n_clusters = len(self.clusters)

			# Shift between the two copies of the spike trains.
			shift = 1

		    # At a given shift, the mask precises which spikes have matching spikes
		    # within the correlogram time window.
			mask = np.ones_like(self.spike_samples, dtype=np.bool)

			self.correlograms = _create_correlograms_array(n_clusters, winsize_bins)
			print("winsize_bins = ", winsize_bins)

		    # The loop continues as long as there is at least one spike with
		    # a matching spike.
			while mask[:-shift].any():
		        # Number of time samples between spike i and spike i+shift.
				spike_diff = _diff_shifted(self.spike_samples, shift)

		        # Binarize the delays between spike i and spike i+shift.
				spike_diff_b = spike_diff // binsize

		        # Spikes with no matching spikes are masked.
				mask[:-shift][spike_diff_b > (winsize_bins // 2)] = False

		        # Cache the masked spike delays.
				m = mask[:-shift].copy()
				d = spike_diff_b[m]

		        # # Update the masks given the clusters to update.
		        # m0 = np.in1d(spike_clusters[:-shift], clusters)
		        # m = m & m0
		        # d = spike_diff_b[m]
				d = spike_diff_b[m]

		        # Find the indices in the raveled correlograms array that need
		        # to be incremented, taking into account the spike clusters.
				indices = np.ravel_multi_index((self.spike_clusters_i[:-shift][m],
		                                        self.spike_clusters_i[+shift:][m],
		                                        d),
		                                       self.correlograms.shape)

		        # Increment the matching spikes in the correlograms array.
				_increment(self.correlograms.ravel(), indices)

				shift += 1
			
			# Remove ACG peaks
			self.correlograms[np.arange(n_clusters),
	                 np.arange(n_clusters),
	                 0] = 0

			if symmetrize:
				self.correlograms = _symmetrize_correlograms(self.correlograms)
			print("CrossCorrelograms computed.")
		return self.correlograms


	def visualize(self, unitsList=None, featuresList=None, SHOW=True, bin_size=0.0005, window_size=0.080):
		'''Visualization tool.
		Argument1: list of clusters whose features need to be visualized (int or float). [unit1, unit2...]
		Argument2: list of features to visualize (str). Can contain "IFR": Instantaneous Firing Rate, "MFR": Mean Firing Rate, "CCG": CrossCorreloGrams.'''
		EXIT = False
		while 1:
			self.extract_cIds()

			if unitsList == None or unitsList == []:
				unitsList = []

				while 1:
					idx = input("\n\nPlease dial a cluster index ; dial <d> if you are done: ")

					if idx == "d":
						break
					else:
						try:
							idx = int(idx) # input() only returns strings
							if idx in self.clusters:
								unitsList.append(idx)
							else:
								print("\nThis index is not detected in the cluster indexes of this directory's data. Try another one.")
						except:
							print("\nYou must dial a floatting point number or an integer.")

				if unitsList==[]:
					print("\nYou didn't provide any cluster index, you b*tch. Ciao.")
					EXIT = True

			if (featuresList == None or featuresList == []) and EXIT == False:
				featuresList = []

				while 1:
					idx = input("\n\nPlease dial a feature to visualize - <MFR>, <IFR> or <CCG> ; dial <d> if you are done: ")
					
					if idx == "d":
						break
					if idx == 'MFR' or idx == 'IFR' or idx == 'CCG':
						featuresList.append(idx)
					else:
						print("\nYou must dial <MFR>, <IFR> or <CCG>.")

				if featuresList==[]:
					print("\nYou didn't provide any feature, you b*tch. Ciao.")
					EXIT = True

			if EXIT==True:
				print("\n\nSee you man, thanks for using Max's tools.")
				break




			if "MFR" in featuresList:
				self.MeanFR()
				MFRList = []
				for i in unitsList:
					MFRidx = np.where(self.clusters==i)[0][0]
					MFRList.append(self.MFR[MFRidx][1])
				unitsListStr = [str(i) for i in unitsList]
				assert len(unitsListStr) == len(MFRList)

				dfMFR = pd.DataFrame(data=MFRList, index=unitsListStr, columns=["Mean Firing rate (Hz)"])
				axMFR = dfMFR.plot.bar()  # s is an instance of Series
				figMFR = axMFR.get_figure()
				if not os.path.exists(self.__dir__+'visMFRs/'):
					os.makedirs(self.__dir__+'visMFRs/')
				figMFRpath = self.__dir__+'visMFRs/'+'MFR'
				for i in unitsListStr:
					figMFRpath+=', '
					figMFRpath+=i
				figMFR.savefig(figMFRpath+'.eps')
				figMFR.savefig(figMFRpath+'.png')


			elif "IFR" in featuresList:
				self.InstFR()
				IFRDic = {}
				for i in unitsList:
					IFRidx = np.where(self.clusters==i)[0][0]
					IFRDic[self.IFR[IFRidx][0]] = pd.Series(self.IFR[IFRidx][1:], index=np.arange(len(self.IFR[IFRidx][1:])))
				unitsListStr = [str(i) for i in unitsList]
				#for i in range(len(IFRlist[0])):

				assert len(unitsListStr) == len(IFRList)

				dfIFR = pd.DataFrame(data=IFRDic, index=np.arange(len(IFRList[0])), columns=unitsListStr)
				axIFR = dfIFR.plot(subplots=True)  # s is an instance of Series
				figIFR = axIFR.get_figure()
				if not os.path.exists(self.__dir__+'visIFRs/'):
					os.makedirs(self.__dir__+'visIFRs/')
				figIFRpath = self.__dir__+'visIFRs/'+'IFR'
				for i in unitsListStr:
					figIFRpath+=', '
					figIFRpath+=i
				figIFR.savefig(figIFRpath+'.eps')
				figIFR.savefig(figIFRpath+'.png')

			elif "CCG" in featuresList:
				self.CCG()


			if SHOW == True:
				#plt.show()
				pass

if __name__ == '__main__':
	data = DataManager()
