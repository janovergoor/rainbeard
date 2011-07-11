import cPickle as pickle
import sys

datafolder = "rainbeard/data/"  # data folder

# Contains auxillary functions for importing and exporting data into the system. 
# Most data is handled through Django fixtures, the confidant network through
# Python pickles. Data is stored in and retrieved from the data folder.


#
#
# Identities
# 
#


# (todo: load & save identities with fixtures)
# (todo: load & save tags with fixtures)


#
#
# Confidant Network
#
#

# Stores the confidant network as a pickle on disc. The default location is
# ./network.p, but this can be adjusted with the fn parameter.
def SaveConfidantNetwork(network, filename="network"):
  pickle.dump(network, open(datafolder + filename + ".p", "wb"))
  
# Retrieves a confidant network from a pickle on disc. The default location is
  # ./network.p, but this can be adjusted with the fn parameter.
def LoadConfidantNetwork(filename="network"):
  network = pickle.load(open(datafolder + filename + ".p"))
  if type(network) != dict:
    raise TypeError('Pickle file does not have the right format.')
  return network
