import glob
import os
import numpy as np
from .utils import Atom, Residue, ActiveSite, save_pickle, load_pickle, flatten_metrics
import numpy as np
from itertools import combinations as combo  
from copy import deepcopy
  

def read_active_sites(dir):
    """
    Read in all of the active sites from the given directory.

    Input: directory
    Output: list of ActiveSite instances
    """
    files = glob.glob(dir + '/*.pdb')

    active_sites = []
    # iterate over each .pdb file in the given directory
    for filepath in glob.iglob(os.path.join(dir, "*.pdb")):

        active_sites.append(read_active_site(filepath))

    print("Read in %d active sites"%len(active_sites))

    return active_sites


def read_active_site(filepath):
    """
    Read in a single active site given a PDB file

    Input: PDB file path
    Output: ActiveSite instance
    """
    basename = os.path.basename(filepath)
    name = os.path.splitext(basename)

    if name[1] != ".pdb":
        raise IOError("%s is not a PDB file"%filepath)

    active_site = ActiveSite(name[0])

    r_num = 0

    # open pdb file
    with open(filepath, "r") as f:
        # iterate over each line in the file
        for line in f:
            if line[0:3] != 'TER':
                # read in an atom
                atom_type = line[13:17].strip()
                x_coord = float(line[30:38])
                y_coord = float(line[38:46])
                z_coord = float(line[46:54])
                atom = Atom(atom_type)
                atom.coords = (x_coord, y_coord, z_coord)

                residue_type = line[17:20]
                residue_number = int(line[23:26])

                # make a new residue if needed
                if residue_number != r_num:
                    residue = Residue(residue_type, residue_number)
                    r_num = residue_number

                # add the atom to the residue
                residue.atoms.append(atom)

            else:  # I've reached a TER card
                active_site.residues.append(residue)

    return active_site


def write_clustering(filename, clusters):
    """
    Write the clustered ActiveSite instances out to a file.

    Input: a filename and a clustering of ActiveSite instances
    Output: none
    """

    out = open(filename, 'w')

    for i in range(len(clusters)):
        out.write("\nCluster %d\n--------------\n" % i)
        for j in range(len(clusters[i])):
            out.write("%s\n" % clusters[i][j])

    out.close()


def write_mult_clusterings(filename, clusterings):
    """
    Write a series of clusterings of ActiveSite instances out to a file.

    Input: a filename and a list of clusterings of ActiveSite instances
    Output: none
    """

    out = open(filename, 'w')

    for i in range(len(clusterings)):
        clusters = clusterings[i]

        for j in range(len(clusters)):
            out.write("\nCluster %d\n------------\n" % j)
            for k in range(len(clusters[j])):
                out.write("%s\n" % clusters[j][k])

    out.close()
    
def gen_mean_dev_normalizations():
    """
    Used to generate Mean and Deviation dictionaries for similarity function.
        -generates values from all PDB files in data folder
        -stores them in pickled format
    """
    activeSites = read_active_sites('data')

    #initialize
    means = deepcopy(activeSites[0].get_raw_metrics())
    devs = deepcopy(activeSites[0].get_raw_metrics())

    #sum (with scale for auto-mean)
    for i in range(len(activeSites)):
        
        site = activeSites[i]
    
        siteMetrics = site.get_raw_metrics()
    
        for metric, value in siteMetrics.items():
            if i==0:
                means[metric] /= float(len(activeSites))
            else:
                means[metric] += siteMetrics[metric]/float(len(activeSites))
            

    #now get mean absolute deviation
    for i in range(len(activeSites)):
        
        site = activeSites[i]
    
        siteMetrics = site.get_raw_metrics()
    
        for metric, value in siteMetrics.items():        
            if i==0:
                devs[metric] = 0
            devs[metric] += abs(siteMetrics[metric]-means[metric])/float(len(activeSites))
                        
                
    save_pickle(means,'means_dict')
    save_pickle(devs,'devs_dict')

    #now flatten and save reference arrays
    save_pickle(flatten_metrics(means),'means_arr')
    save_pickle(flatten_metrics(devs),'devs_arr')
    
    return means, devs

