import sys, json
from esgcet.mapfile import ESGPubMapConv
import configparser as cfg

from datetime import datetime, timedelta

from esgcet.settings import *
from pathlib import Path
from esgcet.mk_dataset import ESGPubMakeDataset

class ESGPubMKDCreateIP(ESGPubMakeDataset):

    def init_project(self, s, l):

        self.project = "CREATE-IP"
        if s in self.source_ids:
            self.DRS = DRS["CREATE-IP-src"]
        elif l == 7:
            self.DRS = DRS["CREATE-IP-model"]
        else:
            self.DRS = DRS["CREATE-IP-exp"]

    def __init__(self, data_node, index_node, replica, globus, data_roots, dtn, silent=False, verbose=False, limit_exceeded=False, user_project=None):
        self.silent = silent
        self.verbose = verbose
        self.data_roots = data_roots
        self.globus = globus
        self.data_node = data_node
        self.index_node = index_node
        self.replica = replica
        self.dtn = dtn
        self.limit_exceeded = limit_exceeded

        self.mapconv = ESGPubMapConv("")
        self.dataset = {}
        self.project = None
        self.user_project = user_project
        self.DRS = None
        self.CONST_ATTR = None
        self.variable_name = "variable"
        self.variable = None

        self.source_ids = ["CCSM-CAM", "CFSR", "CREATE-MRE2models", "CREATE-MRE3models", "CREATE-MREmodels", "GEOS-5",
                   "IFS-Cy31r2", "IFS-Cy41r2", "JRA-25", "JRA-55", "MITgcm", "MOM3", "MOM4", "MRICOMv3",
                   "NCEP-Global-Operational-Model", "NEMOv3", "NEMOv32-LIM2", "NEMOv34-LIM2", "ORAmodels", "ensda-v351"]

    def get_dataset(self, mapdata, scanobj):

        master_id, version = mapdata.split('#')

        parts = master_id.split('.')
        exp_src = parts[3]

        projkey = parts[0]
        scandata = scanobj['dataset']

        if self.project:
            projkey = self.project
        self.init_project(exp_src, len(parts))

        facets = self.DRS  # depends on Init_project to initialize

        assert(facets)
        self.variable = list(scanobj["variables"].keys())[-1]
        self.eprint(self.variable)

        for i, f in enumerate(facets):
            if f in scandata:
                ga_val = scandata[f]
                if not parts[i] == ga_val:
                    if f == "source_id" and ga_val not in self.source_ids:
                        self.dataset["experiment"] = ga_val
                    elif f == "experiment" and ga_val in self.source_ids:
                        self.dataset["source_id"] = ga_val
                    elif not self.silent:
                        self.eprint("WARNING: {} does not agree!".format(f))
                        self.eprint(ga_val)
            self.dataset[f] = parts[i]
        self.dataset[self.variable_name] = self.variable

        self.global_attributes(projkey, scandata)
        self.global_attr_mapped(projkey, scandata)
        self.const_attr()
        self.assign_dset_values(projkey, master_id, version)

    def aggregate_datasets(self, datasets, limit=False):
        vids = []
        v_long_names = []
        cf_std_names = []
        v_units = []
        last_dset = None
        last_rec = None
        for data in datasets:
            if data[0]["type"] == "Dataset":
                idx = 0
            elif data[-1]["type"] == "Dataset":
                idx = -1
            else:
                self.eprint("No dataset record found. Exiting")
                exit(-4)
            dataset = data[idx]
            if "variable" in dataset and dataset["variable"] not in vids:
                print(dataset["variable"])
                if dataset["variable"] == "time_bnds":
                    continue
                vids.append(dataset["variable"])
            if "variable_long_name" in dataset and dataset["variable_long_name"] not in v_long_names:
                v_long_names.append(dataset["variable_long_name"])
            if "cf_standard_name" in dataset and dataset["cf_standard_name"] not in cf_std_names:
                cf_std_names.append(dataset["cf_standard_name"])
            if "variable_units" in dataset and dataset["variable_units"] not in v_units:
                v_units.append(dataset["variable_units"])
            last_rec = data
            last_dset = dataset
        if limit:
            last_dset["variable"] = "Multiple"
            last_dset["variable_long_name"] = "Multiple"
            last_dset["cf_standard_name"] = "Multiple"
            last_dset["variable_units"] = "Multiple"
        else:
            last_dset["variable"] = vids
            last_dset["variable_long_name"] = v_long_names
            last_dset["cf_standard_name"] = cf_std_names
            last_dset["variable_units"] = v_units
        last_rec[idx] = last_dset
        if self.verbose:
            self.eprint("Aggregate record:")
            self.eprint(json.dumps(last_dset, indent=4))
        return last_rec
