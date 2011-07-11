""" Data import module. """

import cPickle as pickle
import sys

datafolder = 'rainbeard/data/'  # data folder


# Todo: load & save identities with fixtures.
# Todo: load & save tags with fixtures.


def SaveConfidantNetwork(network, filename='network'):
    """
    Stores the confidant network as a pickle on disc. The default location 
    is /network.p, but this can be adjusted with the fn parameter.
    """
    
    pickle.dump(network, open(datafolder + filename + '.p', 'wb'))


def LoadConfidantNetwork(filename='network'):
    """
    Retrieves a confidant network from a pickle on disc. The default location
    is ./network.p, but this can be adjusted with the fn parameter.
    """
    
    network = pickle.load(open(datafolder + filename + '.p'))
    if type(network) != dict:
        raise TypeError("Pickle file does not have the right format.")
    return network
