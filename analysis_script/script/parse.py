"""
Author: David Ho
Institute: National Tsing Hua university, Department of Physics, Hsinchu, Taiwan 
Mail: davidho@gapp.nthu.edu.tw
"""
#Import packages
import uproot
import pandas as pd 
import numpy as np 
from script.particle import particle_properties  #import particle properties helper function from particle_properties.py
from script.jet import jet_properties  #import jet properties helper function from jet_properties.py
from script.MissingET import Missing_ET_properties
from script.electron import electron_properties
from script.muon import muon_properties
import h5py, sys, traceback, os, tqdm, time
from script.utilize import delta_R, deltaPhi, pdgid, quark_finder, deltaR_matching, deltaPhi, particle_tracing, event_selection
import multiprocessing as mp

def parse(INPUT_FILE, OUTPUT_FILE, MODEL, PROCESS, GENERATOR, SINGLE=True):

    PID = pdgid()
    # Setting `STATUS_CODE` for different shower generator.
    if GENERATOR == 'py8':
        STATUS_CODE = 22
    elif GENERATOR == 'herwig7':
        STATUS_CODE = 11
    else: 
        print("Please select a correct shower generator. 1. py8, 2. herwig7.")

    MAX_NUM_OF_JETS = 20

    # Setting barcode, `NUM_OF_PARTON`, and `NUM_OF_DAUGHTER` for different model
    if MODEL == "ttbar":
        """
        Barcode system
        t t~ W+ W- b b~ 
        0 0  0  0  0 0
        daughter of top and W+: 101000 ----> 40
        daughter of top and b: 101000 ----> 34
        daughter of anti top and W-: 100100 ----> 20
        daughter of anti top and b~: 100001 ----> 17
        """
        barcode = np.array([34, 40, 40, 17, 20, 20])
        NUM_OF_PARTON = 6
        NUM_OF_DAUGHTER = 6
    elif MODEL == "ttbar_lep_left":
        """
        Barcode system
        t t~ W+ W- b b~ 
        0 0  0  0  0 0
        daughter of top and W+: 101000 ----> 40
        daughter of top and b: 101000 ----> 34
        daughter of anti top and W-: 100100 ----> 20
        daughter of anti top and b~: 100001 ----> 17
        """
        barcode = np.array([34, 40, 40, 17, 20, 20])
        NUM_OF_PARTON = 4
        NUM_OF_DAUGHTER = 6
    elif MODEL == "ttbar_lep_right":
        """
        Barcode system
        t t~ W+ W- b b~ 
        0 0  0  0  0 0
        daughter of top and W+: 101000 ----> 40
        daughter of top and b: 101000 ----> 34
        daughter of anti top and W-: 100100 ----> 20
        daughter of anti top and b~: 100001 ----> 17
        """
        barcode = np.array([34, 40, 40, 17, 20, 20])
        NUM_OF_PARTON = 4
        NUM_OF_DAUGHTER = 6
    elif MODEL == "ttH":
        """
        Barcode system
        t t~ W+ W- b b~ H
        0 0  0  0  0 0  0
        daughter of t and b = 1000100  ----> 68
        daughter of t and W+ = 1010000 ----> 80
        daughter of t~ and W- = 0101000 ----> 34
        daughter of t~ and b~ = 0100010 ----> 40
        daughter of H = 0000001 ----> 1
        """
        barcode = np.array([68, 80, 80, 34, 40, 40, 1, 1])
        NUM_OF_PARTON = 8
        NUM_OF_DAUGHTER = 8
    elif MODEL == "four_top":
        """
        Barcode system
        t1 t2 t1~ t2~ W+1 W-1 W+2 W-2 b1 b2 b1~ b2~             describe          barcode   sequence
        0  0   0   0   0   0   0   0  0  0   0   0

        1  0   0   0   1   0   0   0  0  0   0   0  <--- daughter of t1 and W+1   2176         2,3
        1  0   0   0   0   0   0   0  1  0   0   0  <--- daughter of t1 and b1    2056          1
        0  0   1   0   0   1   0   0  0  0   0   0  <--- daughter of t1~ and W-1  576          5,6
        0  0   1   0   0   0   0   0  0  1   0   0  <--- daughter of t1~ and b1~  516           4

        0  1   0   0   0   0   1   0  0  0   0   0  <--- daughter of t2 and W+2   1056         7,8
        0  1   0   0   0   0   0   0  0  1   0   0  <--- daughter of t2 and b2    1028          9
        0  0   0   1   0   0   0   1  0  0   0   0  <--- daughter of t2~ and W-2  272          11.12
        0  0   0   1   0   0   0   0  0  0   0   1  <--- daughter of t2~ and b2~  257           10

        """
        barcode = np.array([2056, 2176, 2176, 516, 576, 576, 1028, 1056, 1056, 257, 272, 272])
        NUM_OF_PARTON = 12
        NUM_OF_DAUGHTER = 12
    elif MODEL == "ZH":
        """
        Barcode system
        Z H W+ W- b b~ 
        0 0  0  0  0 0
        daughter of higgs and W+: 011000 ----> 24
        daughter of higgs and W-: 010100 ----> 20
        daughter of Z and b: 100010 ----> 34
        daughter of Z and b~: 100001 ----> 33
        """
        barcode = np.array([24, 24, 20, 20, 34, 33])
        NUM_OF_PARTON = 6
        NUM_OF_DAUGHTER = 6
    else:
        print("Please select a correct model.")

    print("+------------------------------------------------------------------------------------------------------+")
    print("Start loading dataset.")
    print("+------------------------------------------------------------------------------------------------------+")
    print(SINGLE)
    if SINGLE:
        data = uproot.open(INPUT_FILE)['Delphes']
        particle = particle_properties(data)
        jet = jet_properties(data)
        if MODEL == 'ttbar_lep_left' or MODEL == "ttbar_lep_right":
            electron = electron_properties(data)
            muon = muon_properties(data)
            missing_et = Missing_ET_properties(data)
    else: 
        files = os.listdir(INPUT_FILE)
        PATH = []
        for a in files:
            PATH.append(os.path.join(INPUT_FILE, a))
        particle = particle_properties(PATH, single=False)
        jet = jet_properties(PATH, single=False)
        if MODEL == 'ttbar_lep_left' or MODEL == "ttbar_lep_right":
            electron = electron_properties(PATH, single=False)
            muon = muon_properties(PATH, single=False)
            missing_et = Missing_ET_properties(PATH, single=False)
    print("+------------------------------------------------------------------------------------------------------+")
    print("Dataset loaded.")
    print("+------------------------------------------------------------------------------------------------------+")

    print("+------------------------------------------------------------------------------------------------------+")
    print("Start event selection.")
    print("+------------------------------------------------------------------------------------------------------+")

    if MODEL == 'ttbar_lep_left' or MODEL == "ttbar_lep_right":
        marker_event, marker_jet, marker_btag, marker_lepton = event_selection(MODEL, 
                                                                    pt=jet.pt, 
                                                                    eta=jet.eta, 
                                                                    phi=jet.phi,
                                                                    btag=jet.btag,
                                                                    electron_pt=electron.pt,
                                                                    electron_eta=electron.eta,
                                                                    electron_phi=electron.phi,
                                                                    muon_pt=muon.pt,
                                                                    muon_eta=muon.eta,
                                                                    muon_phi=muon.phi,
                                                                    )
    else:
        marker_event, marker_jet, marker_btag = event_selection(MODEL, pt=jet.pt, eta=jet.eta, btag=jet.btag)
    del marker_jet, marker_btag, marker_lepton
    passed = np.where(marker_event == 1)[0]
    print("+------------------------------------------------------------------------------------------------------+")
    print("Jet selection done. {0} events has been selected.".format(len(passed)))
    print("+------------------------------------------------------------------------------------------------------+")

    print("+------------------------------------------------------------------------------------------------------+")
    print("Recording the kinematics variables of jets in the selected event.")
    print("+------------------------------------------------------------------------------------------------------+")
    if MODEL == 'ttbar_lep_left' or MODEL == "ttbar_lep_right":
        # Initialize the numpy.ndarray for jet, leptons, and MET
        jet_pt = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_eta = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_phi = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_mass = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_btag = np.zeros((len(passed), MAX_NUM_OF_JETS), dtype=np.int8)
        jet_num_of_jets = np.zeros((len(passed)), dtype=np.int8)
        
        # Since we require only 1 lepton can exists in each event, so we don't need second dimension.
        lepton_pt = np.zeros((len(passed)))
        lepton_eta = np.zeros((len(passed)))
        lepton_phi = np.zeros((len(passed)))
        lepton_pdgid = np.zeros((len(passed)))

        # Since the stucture of MET only have 1 element in each event, so we don't need second dimension.
        MET = np.zeros((len(passed)))
        MET_ETA = np.zeros((len(passed)))
        MET_PHI = np.zeros((len(passed)))

        # Storing MissingET data
        for i in range(len(passed)):
            idx = int(passed[i])
            MET[i] = missing_et.MET[idx]
            MET_ETA[i] = missing_et.eta[idx]
            MET_PHI[i] = missing_et.phi[idx]

        # Storing lepton data
        for i in tqdm.trange(len(passed)):
            idx = int(passed[i])
            if len(electron.pt[idx]) != 0 and len(muon.pt[idx]) == 0:
                lepton_pt[i] = electron.pt[idx][0]
                lepton_eta[i] = electron.eta[idx][0]
                lepton_phi[i] = electron.phi[idx][0]
                lepton_pdgid[i] = PID.electron
            elif len(electron.pt[idx]) == 0 and len(muon.pt[idx]) != 0: 
                lepton_pt[i] = muon.pt[idx][0]
                lepton_eta[i] = muon.eta[idx][0]
                lepton_phi[i] = muon.phi[idx][0]
                lepton_pdgid[i] = PID.muon
            else: 
                print(f"There exist more than 1 leptons in event {idx}, please check your selection.")

        # Storing jet data with lepton-jet removal (cut: deltaR(jet, lepton) > 0.4)
        for i in tqdm.trange(len(passed)):
            idx = int(passed[i])
            for j in range(len(jet.pt[idx])):
                if delta_R(jet.eta[idx][j], jet.phi[idx][j], lepton_eta[i], lepton_phi[i]) > 0.4: 
                    jet_pt[i][j] = jet.pt[idx][j]
                    jet_eta[i][j] = jet.eta[idx][j]
                    jet_phi[i][j] = jet.phi[idx][j]
                    jet_mass[i][j] = jet.mass[idx][j]
                    jet_btag[i][j] = jet.btag[idx][j]
                else: 
                    jet_pt[i][j] = -100
                    jet_eta[i][j] = -100
                    jet_phi[i][j] = -100
                    jet_mass[i][j] = -100
                    jet_btag[i][j] = -100
            jet_num_of_jets[i] = jet.num_of_jets[idx]
            
    else:
        # Initialize the numpy.ndarray for jet
        jet_pt = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_eta = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_phi = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_mass = np.zeros((len(passed), MAX_NUM_OF_JETS))
        jet_btag = np.zeros((len(passed), MAX_NUM_OF_JETS), dtype=np.int8)
        jet_num_of_jets = np.zeros((len(passed)), dtype=np.int8)

        # Storing jet data
        for i in tqdm.trange(len(passed)):
            idx = int(passed[i])
            for j in range(len(jet.pt[idx])):
                jet_pt[i][j] = jet.pt[idx][j]
                jet_eta[i][j] = jet.eta[idx][j]
                jet_phi[i][j] = jet.phi[idx][j]
                jet_mass[i][j] = jet.mass[idx][j]
                jet_btag[i][j] = jet.btag[idx][j]
            jet_num_of_jets[i] = jet.num_of_jets[idx]
    print("+------------------------------------------------------------------------------------------------------+")
    print("Finished to record the kinematics variables of jets in the selected event.")
    print("+------------------------------------------------------------------------------------------------------+")

    print("+------------------------------------------------------------------------------------------------------+")
    print("Starting parton tracing and looking for its daughter.")
    print("+------------------------------------------------------------------------------------------------------+")
    #Particle tracing and daughter finding section
    start = time.time()
    if MODEL == 'ttbar' or MODEL == 'ttbar_lep_left' or MODEL =='ttbar_lep_right':
        
        _src_top  = [ list([particle.dataframelize(i), PID.top, STATUS_CODE, MODEL]) for i in passed ]
        _src_anti_top  = [ list([particle.dataframelize(i), PID.anti_top, STATUS_CODE, MODEL]) for i in passed ]

        print("Using {0} process for accelerating speed.".format(PROCESS))
        with mp.Pool(PROCESS) as p:
            _result_top = p.starmap(particle_tracing, _src_top)
            p.close()
            p.join()
        print("Top tracing finished.")
        with mp.Pool(PROCESS) as p:
            _result_anti_top = p.starmap(particle_tracing, _src_anti_top)
            p.close()
            p.join()
        print("Anti-Top tracing finished.")
        _result_top = np.array(_result_top)
        _result_anti_top = np.array(_result_anti_top)

        # top_idx = _result_top[:,0]
        top_daughter_idx_1 = _result_top[:,1]
        # top_daughter_pid_1 = _result_top[:,2]
        top_daughter_idx_2 = _result_top[:,3]
        # top_daughter_pid_2 = _result_top[:,4]
        
        # top_bar_idx = _result_anti_top[:,0]
        top_bar_daughter_idx_1 = _result_anti_top[:,1]
        # top_bar_daughter_pid_1 = _result_anti_top[:,2]
        top_bar_daughter_idx_2 = _result_anti_top[:,3]
        # top_bar_daughter_pid_2 = _result_anti_top[:,4]

        del _src_top, _src_anti_top


        _src_top_d, _src_anti_top_d = [list([particle.dataframelize(passed[i]), top_daughter_idx_1[i], top_daughter_idx_2[i]]) for i in range(len(passed))], [list([particle.dataframelize(passed[i]), top_bar_daughter_idx_1[i], top_bar_daughter_idx_2[i]]) for i in range(len(passed))]
        parton_array = np.zeros([ len(passed) , NUM_OF_DAUGHTER])

        with mp.Pool(PROCESS) as p:
            _result_top = p.starmap(quark_finder, _src_top_d)
            p.close()
            p.join()
        print("Daughter of Top's daughters found.")
        with mp.Pool(PROCESS) as p:
            _result_anti_top = p.starmap(quark_finder, _src_anti_top_d)
            p.close()
            p.join()
        print("Daughter of Anti-Top's daughters found.")
        _result_top = np.array(_result_top)
        _result_anti_top = np.array(_result_anti_top)

        del _src_anti_top_d, _src_top_d


        parton_array[:, 0] = _result_top[:, 0]
        parton_array[:, 1] = _result_top[:, 1]
        parton_array[:, 2] = _result_top[:, 2]
        parton_array[:, 3] = _result_anti_top[:, 0]
        parton_array[:, 4] = _result_anti_top[:, 1]
        parton_array[:, 5] = _result_anti_top[:, 2]

        print("+------------------------------------------------------------------------------------------------------+")
        print("Parton tracing section complete. The daughter of W+/W- and bbbar has been found. Cost: {0:.1f} s".format(time.time()-start))
        print("+------------------------------------------------------------------------------------------------------+")

    elif MODEL == 'ttH':
        
        _src_top  = [ list([particle.dataframelize(i), PID.top, STATUS_CODE, MODEL]) for i in passed ]
        _src_anti_top  = [ list([particle.dataframelize(i), PID.anti_top, STATUS_CODE, MODEL]) for i in passed ]
        _src_higgs  = [ list([particle.dataframelize(i), PID.higgs, STATUS_CODE, MODEL]) for i in passed ]


        print("Using {0} process for accelerating speed.".format(PROCESS))
        with mp.Pool(PROCESS) as p:
            _result_top = p.starmap(particle_tracing, _src_top)
            p.close()
            p.join()
        print("Top tracing finished.")
        with mp.Pool(PROCESS) as p:
            _result_anti_top = p.starmap(particle_tracing, _src_anti_top)
            p.close()
            p.join()
        print("Anti-Top tracing finished.")
        with mp.Pool(PROCESS) as p:
            _result_h = p.starmap(particle_tracing, _src_higgs)
            p.close()
            p.join()
        print("Higgs tracing finished.")
        _result_top = np.array(_result_top)
        _result_anti_top = np.array(_result_anti_top)
        _result_h = np.array(_result_h)

        # top_idx = _result_top[:,0]
        top_daughter_idx_1 = _result_top[:,1]
        # top_daughter_pid_1 = _result_top[:,2]
        top_daughter_idx_2 = _result_top[:,3]
        # top_daughter_pid_2 = _result_top[:,4]
        
        # top_bar_idx = _result_anti_top[:,0]
        top_bar_daughter_idx_1 = _result_anti_top[:,1]
        # top_bar_daughter_pid_1 = _result_anti_top[:,2]
        top_bar_daughter_idx_2 = _result_anti_top[:,3]
        # top_bar_daughter_pid_2 = _result_anti_top[:,4]

        _src_top_d, _src_anti_top_d = [list([particle.dataframelize(passed[i]), top_daughter_idx_1[i], top_daughter_idx_2[i]]) for i in range(len(passed))], [list([particle.dataframelize(passed[i]), top_bar_daughter_idx_1[i], top_bar_daughter_idx_2[i]]) for i in range(len(passed))]
        parton_array = np.zeros([ len(passed) , NUM_OF_DAUGHTER])

        with mp.Pool(PROCESS) as p:
            _result_top = p.starmap(quark_finder, _src_top_d)
            p.close()
            p.join()
        print("Daughter of Top's daughters found.")
        with mp.Pool(PROCESS) as p:
            _result_anti_top = p.starmap(quark_finder, _src_anti_top_d)
            p.close()
            p.join()
        print("Daughter of Anti-Top's daughters found.")
        _result_top = np.array(_result_top)
        _result_anti_top = np.array(_result_anti_top)

        del _src_anti_top_d, _src_top_d

        parton_array[:, 0] = _result_top[:, 0]
        parton_array[:, 1] = _result_top[:, 1]
        parton_array[:, 2] = _result_top[:, 2]
        parton_array[:, 3] = _result_anti_top[:, 0]
        parton_array[:, 4] = _result_anti_top[:, 1]
        parton_array[:, 5] = _result_anti_top[:, 2]
        parton_array[:, 6], parton_array[:, 7] = _result_h[:,1], _result_h[:,3]
        print("+------------------------------------------------------------------------------------------------------+")
        print("Parton tracing section complete. The daughter of W+/W-, bbbar, and Higgs has been found. Cost: {0:.1f} s".format(time.time()-start))
        print("+------------------------------------------------------------------------------------------------------+")

    elif MODEL == 'four_top':

        _src_top  = [ list([particle.dataframelize(i), PID.top, STATUS_CODE, MODEL]) for i in passed ]
        _src_anti_top  = [ list([particle.dataframelize(i), PID.anti_top, STATUS_CODE, MODEL]) for i in passed ]

        print("Using {0} process for accelerating speed.".format(PROCESS))
        with mp.Pool(PROCESS) as p:
            _result_top = p.starmap(particle_tracing, _src_top)
            p.close()
            p.join()
        print("Top tracing finished.")
        with mp.Pool(PROCESS) as p:
            _result_anti_top = p.starmap(particle_tracing, _src_anti_top)
            p.close()
            p.join()
        print("Anti-Top tracing finished.")
        _result_top = np.array(_result_top)
        _result_anti_top = np.array(_result_anti_top)

        del _src_top, _src_anti_top

        # top_1_idx = _result_top[:,0]
        # top_2_idx = _result_top[:,1]
        top_1_daughter_idx_1 = _result_top[:,2]
        # top_1_daughter_pid_1 = _result_top[:,3]
        top_1_daughter_idx_2 = _result_top[:,4]
        # top_1_daughter_pid_2 = _result_top[:,5]
        top_2_daughter_idx_1 = _result_top[:,6]
        # top_2_daughter_pid_1 = _result_top[:,7]
        top_2_daughter_idx_2 = _result_top[:,8]
        # top_2_daughter_pid_2 = _result_top[:,9]

        # top_1_bar_idx = _result_anti_top[:,0]
        # top_2_bar_idx = _result_anti_top[:,1]
        top_1_bar_daughter_idx_1 = _result_anti_top[:,2]
        # top_1_bar_daughter_pid_1 = _result_anti_top[:,3]
        top_1_bar_daughter_idx_2 = _result_anti_top[:,4]
        # top_1_bar_daughter_pid_2 = _result_anti_top[:,5]
        top_2_bar_daughter_idx_1 = _result_anti_top[:,6]
        # top_2_bar_daughter_pid_1 = _result_anti_top[:,7]
        top_2_bar_daughter_idx_2 = _result_anti_top[:,8]
        # top_2_bar_daughter_pid_2 = _result_anti_top[:,9]
        
        _src_top_d_1, _src_top_d_2 = [list([particle.dataframelize(passed[i]), top_1_daughter_idx_1[i], top_1_daughter_idx_2[i]]) for i in range(len(passed))], [list([particle.dataframelize(passed[i]), top_2_daughter_idx_1[i], top_2_daughter_idx_2[i]]) for i in range(len(passed))]
        _src_anti_top_d_1, _src_anti_top_d_2 = [list([particle.dataframelize(passed[i]), top_1_bar_daughter_idx_1[i], top_1_bar_daughter_idx_2[i]]) for i in range(len(passed))], [list([particle.dataframelize(passed[i]), top_2_bar_daughter_idx_1[i], top_2_bar_daughter_idx_2[i]]) for i in range(len(passed))]
        
        parton_array = np.zeros([ len(passed) , NUM_OF_DAUGHTER])

        with mp.Pool(PROCESS) as p:
            _result_top_1 = p.starmap(quark_finder, _src_top_d_1)
            p.close()
            p.join()
        print("Daughter of Top_1's daughters found.") 
        with mp.Pool(PROCESS) as p:
            _result_top_2 = p.starmap(quark_finder, _src_top_d_2)
            p.close()
            p.join()
        print("Daughter of Top_2's daughters found.") 
        with mp.Pool(PROCESS) as p:
            _result_anti_top_1 = p.starmap(quark_finder, _src_anti_top_d_1)
            p.close()
            p.join()
        print("Daughter of Anti-Top_1's daughters found.") 
        with mp.Pool(PROCESS) as p:
            _result_anti_top_2 = p.starmap(quark_finder, _src_anti_top_d_2)
            p.close()
            p.join()
        print("Daughter of Anti-Top_2's daughters found.") 
        _result_top_1 = np.array(_result_top_1)
        _result_top_2 = np.array(_result_top_2)
        _result_anti_top_1 = np.array(_result_anti_top_1)
        _result_anti_top_2 = np.array(_result_anti_top_2)

        del _src_top_d_1, _src_top_d_2, _src_anti_top_d_1, _src_anti_top_d_2

        parton_array[:, 0] = _result_top[:, 0]
        parton_array[:, 1] = _result_top[:, 1]
        parton_array[:, 2] = _result_top[:, 2]
        parton_array[:, 3] = _result_top_2[:, 0]
        parton_array[:, 4] = _result_top_2[:, 1]
        parton_array[:, 5] = _result_top_2[:, 2]
        parton_array[:, 6] = _result_anti_top_1[:, 0]
        parton_array[:, 7] = _result_anti_top_1[:, 1]
        parton_array[:, 8] = _result_anti_top_1[:, 2]
        parton_array[:, 9] = _result_anti_top_2[:, 0]
        parton_array[:, 10] = _result_anti_top_2[:, 1]
        parton_array[:, 11] = _result_anti_top_2[:, 2]

        print("+------------------------------------------------------------------------------------------------------+")
        print("Parton tracing section complete. The daughter of W+/W- and bbbar has been found. Cost: {0:.1f} s".format(time.time()-start))
        print("+------------------------------------------------------------------------------------------------------+")
    elif MODEL == 'ZH':
        
        _src_Z  = [ list([particle.dataframelize(i), PID.z_plus, STATUS_CODE, MODEL]) for i in passed ]
        _src_higgs  = [ list([particle.dataframelize(i), PID.higgs, STATUS_CODE, MODEL]) for i in passed ]


        print("Using {0} process for accelerating speed.".format(PROCESS))
        with mp.Pool(PROCESS) as p:
            _result_z = p.starmap(particle_tracing, _src_Z)
            p.close()
            p.join()
        print("Z tracing finished.")
        with mp.Pool(PROCESS) as p:
            _result_h = p.starmap(particle_tracing, _src_higgs)
            p.close()
            p.join()
        print("Higgs tracing finished.")
        _result_z = np.array(_result_z)
        _result_h = np.array(_result_h)

        z_idx = _result_z[:,0]
        z_daughter_idx_1 = _result_z[:,1]
        # z_daughter_pid_1 = _result_z[:,2]
        z_daughter_idx_2 = _result_z[:,3]
        # z_daughter_pid_2 = _result_z[:,4]

        h_idx = _result_h[:,0]
        h_daughter_idx_1 = _result_h[:,1]
        # h_daughter_pid_1 = _result_h[:,2]
        h_daughter_idx_2 = _result_h[:,3]
        # h_daughter_pid_2 = _result_h[:,4]

        _src_h_d = [list([particle.dataframelize(passed[i]), h_daughter_idx_1[i], h_daughter_idx_2[i]]) for i in range(len(passed))]
        parton_array = np.zeros([ len(passed) , NUM_OF_DAUGHTER])

        with mp.Pool(PROCESS) as p:
            _result_h = p.starmap(quark_finder, _src_h_d)
            p.close()
            p.join()
        print("Daughter of Higgs's daughters found.")
        _result_h = np.array(_result_h)

        del _src_h_d

        parton_array[:, 0] = _result_h[:, 0]
        parton_array[:, 1] = _result_h[:, 1]
        parton_array[:, 2] = _result_h[:, 2]
        parton_array[:, 3] = _result_h[:, 0]
        parton_array[:, 4] = _result_z[:, 1]
        parton_array[:, 5] = _result_z[:, 3]
        print("+------------------------------------------------------------------------------------------------------+")
        print("Parton tracing section complete. The daughter of W+/W-, bbbar, and Higgs has been found. Cost: {0:.1f} s".format(time.time()-start))
        print("+------------------------------------------------------------------------------------------------------+")
    else :
        print("Please select a correct model.")

    print("+------------------------------------------------------------------------------------------------------+")
    print("Recording the kinematics variables of partons in the selected event.")
    print("+------------------------------------------------------------------------------------------------------+")
    parton_pdgid = np.zeros((len(passed), NUM_OF_DAUGHTER), dtype=np.int8)
    parton_barcode = np.zeros((len(passed), NUM_OF_DAUGHTER), dtype=np.int8)
    parton_pt = np.zeros((len(passed), NUM_OF_DAUGHTER))
    parton_eta = np.zeros((len(passed), NUM_OF_DAUGHTER))
    parton_phi = np.zeros((len(passed), NUM_OF_DAUGHTER))
    parton_mass = np.zeros((len(passed), NUM_OF_DAUGHTER))

    for i in tqdm.trange(len(passed)):
        idx = passed[i]
        for j in range(NUM_OF_DAUGHTER):
            ix = int(parton_array[i][j])
            parton_pdgid[i][j] = particle.pid[idx][ix]
            parton_barcode[i][j] = barcode[j]
            parton_pt[i][j] = particle.pt[idx][ix]
            parton_eta[i][j] = particle.eta[idx][ix]
            parton_phi[i][j] = particle.phi[idx][ix]
            parton_mass[i][j] = particle.mass[idx][ix]

    if MODEL == 'ttbar_lep_left' or MODEL == "ttbar_lep_right":
        print("Recording simulation lepton kinematic properties.")
        simulation_lepton_pdgid = np.zeros(len(passed))
        simulation_lepton_barcode = np.zeros(len(passed))
        simulation_lepton_pt = np.zeros(len(passed))
        simulation_lepton_eta = np.zeros(len(passed))
        simulation_lepton_phi = np.zeros(len(passed))
        simulation_lepton_mass = np.zeros(len(passed))
        simulation_neutrino_pdgid = np.zeros(len(passed))
        simulation_neutrino_barcode = np.zeros(len(passed))
        simulation_neutrino_pt = np.zeros(len(passed))
        simulation_neutrino_eta = np.zeros(len(passed))
        simulation_neutrino_phi = np.zeros(len(passed))
        simulation_neutrino_mass = np.zeros(len(passed))

        if MODEL == 'ttbar_lep_left':
            for i in tqdm.trange(len(passed)):
                for j in range(1,3):
                    if parton_pdgid[i][j] == -11 or parton_pdgid[i][j] == -13:
                        simulation_lepton_pdgid[i] = parton_pdgid[i][j]
                        simulation_lepton_barcode[i] = parton_barcode[i][j]
                        simulation_lepton_pt[i] = parton_pt[i][j]
                        simulation_lepton_eta[i] = parton_eta[i][j]
                        simulation_lepton_phi[i] = parton_phi[i][j]
                        simulation_lepton_mass[i] = parton_mass[i][j]
                        
                    else: 
                        simulation_neutrino_pdgid[i] = parton_pdgid[i][j]
                        simulation_neutrino_barcode[i] = parton_barcode[i][j]
                        simulation_neutrino_pt[i] = parton_pt[i][j]
                        simulation_neutrino_eta[i] = parton_eta[i][j]
                        simulation_neutrino_phi[i] = parton_phi[i][j]
                        simulation_neutrino_mass[i] = parton_mass[i][j]

            parton_pdgid = np.delete(parton_pdgid, [1,2], 1)
            parton_barcode = np.delete(parton_barcode, [1,2], 1)
            parton_pt = np.delete(parton_pt, [1,2], 1)
            parton_eta = np.delete(parton_eta, [1,2], 1)
            parton_phi = np.delete(parton_phi, [1,2], 1)
            parton_mass = np.delete(parton_mass, [1,2], 1)

        elif MODEL == "ttbar_lep_right":
            for i in tqdm.trange(len(passed)):
                for j in range(4,6):
                    if parton_pdgid[i][j] == 11 or parton_pdgid[i][j] == 13:
                        simulation_lepton_pdgid[i] = parton_pdgid[i][j]
                        simulation_lepton_barcode[i] = parton_barcode[i][j]
                        simulation_lepton_pt[i] = parton_pt[i][j]
                        simulation_lepton_eta[i] = parton_eta[i][j]
                        simulation_lepton_phi[i] = parton_phi[i][j]
                        simulation_lepton_mass[i] = parton_mass[i][j]
                    else: 
                        simulation_neutrino_pdgid[i] = parton_pdgid[i][j]
                        simulation_neutrino_barcode[i] = parton_barcode[i][j]
                        simulation_neutrino_pt[i] = parton_pt[i][j]
                        simulation_neutrino_eta[i] = parton_eta[i][j]
                        simulation_neutrino_phi[i] = parton_phi[i][j]
                        simulation_neutrino_mass[i] = parton_mass[i][j]
            parton_pdgid = np.delete(parton_pdgid, [4, 5], 1)
            parton_barcode = np.delete(parton_barcode, [4, 5], 1)
            parton_pt = np.delete(parton_pt, [4, 5], 1)
            parton_eta = np.delete(parton_eta, [4, 5], 1)
            parton_phi = np.delete(parton_phi, [4, 5], 1)
            parton_mass = np.delete(parton_mass, [4, 5], 1)
        else: 
            print("Wrong model, please check your model setting.")
    print("+------------------------------------------------------------------------------------------------------+")
    print("Finished to record the kinematics variables of partons in the selected event.")
    print("+------------------------------------------------------------------------------------------------------+")
    
    print("+------------------------------------------------------------------------------------------------------+")
    print("Starting parton-jet matching.")
    print("+------------------------------------------------------------------------------------------------------+")
    start = time.time()

    _src_delta_R = [list([NUM_OF_PARTON, len(jet_pt[i]), parton_eta[i], parton_phi[i], jet_eta[i], jet_phi[i], 0.4, MODEL]) for i in range(len(jet_pt))]
    print("Using {0} process for accelerating speed.".format(PROCESS))
    with mp.Pool(PROCESS) as p:
        _result_delta_R = p.starmap(deltaR_matching, _src_delta_R)
        p.close()
        p.join()
    _result_delta_R = np.array(_result_delta_R)

    jet_parton_index = np.array([ a for a in _result_delta_R[:, 0]])
    parton_jet_index = np.array([ a for a in _result_delta_R[:, 1]])

    print("+------------------------------------------------------------------------------------------------------+")
    print("Parton-jet matching finished. Cost: {0:.1f} s".format(time.time()-start))
    print("+------------------------------------------------------------------------------------------------------+")

    if MODEL == 'ttbar_lep_left' or MODEL == "ttbar_lep_right":
        print("+------------------------------------------------------------------------------------------------------+")
        print("Starting lepton matching.")
        print("+------------------------------------------------------------------------------------------------------+")
        lepton_delta_R_result = np.zeros(len(simulation_lepton_pt))
        for i in range(len(simulation_lepton_pt)):
            _delta_R = delta_R(simulation_lepton_eta[i], simulation_lepton_phi[i], lepton_eta[i], lepton_phi[i])
            if _delta_R < 0.4:
                lepton_delta_R_result[i] = 1
            else : 
                lepton_delta_R_result[i] = 0
        print("+------------------------------------------------------------------------------------------------------+")
        print("Lepton matching finished.")
        print("+------------------------------------------------------------------------------------------------------+") 
        
        print("+------------------------------------------------------------------------------------------------------+")
        print("Starting neutrino matching.")
        print("+------------------------------------------------------------------------------------------------------+")
        MET_delta_R_result = np.zeros(len(simulation_neutrino_eta))
        for i in range(len(simulation_neutrino_eta)):
            _delta_R = deltaPhi(simulation_neutrino_phi[i], MET_PHI[i])
            if np.abs(_delta_R) < 0.4:
                MET_delta_R_result[i] = 1
            else : 
                MET_delta_R_result[i] = 0
        print("+------------------------------------------------------------------------------------------------------+")
        print("Neutrino matching finished.")
        print("+------------------------------------------------------------------------------------------------------+") 
    print("+------------------------------------------------------------------------------------------------------+")
    print("Recording barcode information.")
    print("+------------------------------------------------------------------------------------------------------+")

    jet_barcode = jet_parton_index.copy()

    for i in range(len(barcode)):
        jet_barcode = np.where(jet_barcode == i, barcode[i], jet_barcode) 
    
    print("+------------------------------------------------------------------------------------------------------+")
    print("Barcode information has beed record.")
    print("+------------------------------------------------------------------------------------------------------+")

    if MODEL == 'ttH':
        target = [i for i in range(6)]
        N_match_top_in_event = np.zeros([len(jet_pt)])
        for i in tqdm.trange(len(jet_parton_index)):
            intersetion = set(target).intersection(jet_parton_index[i])
            if intersetion.intersection(set([0, 1, 2])) == {0,1,2} and intersetion.intersection(set([3, 4, 5])) == {3,4,5} :
                N_match_top_in_event[i] = 2
            elif intersetion.intersection(set([0, 1, 2])) != {0,1,2} or intersetion.intersection(set([3, 4, 5])) != {3,4,5}:
                N_match_top_in_event[i] = 1
            elif intersetion.intersection(set([0, 1, 2])) != {0,1,2} and intersetion.intersection(set([3, 4, 5])) != {3,4,5}:
                N_match_top_in_event[i] = 0
            else : pass

        N_match_higgs_in_event = np.zeros([len(jet_pt)])
        for i in range(len(jet_parton_index)):
            if 7 in jet_parton_index[i]:
                if 6 in jet_parton_index[i]:
                    N_match_higgs_in_event[i] = 1
        print("+------------------------------------------------------------------------------------------------------+")
        print("Jet-parton matching section complete.\nFound {0} events with 1 ttbar candidate exist.\nFound {1} events with 2 ttbar candidate exist.".format( np.sum(N_match_top_in_event == 1), np.sum(N_match_top_in_event == 2)  ))
        print("+------------------------------------------------------------------------------------------------------+")
    elif MODEL == 'ttbar':
        target = [i for i in range(NUM_OF_PARTON)]
        N_match_top_in_event = np.zeros([len(jet_pt)])
        for i in tqdm.trange(len(jet_parton_index)):
        
            intersetion = set(target).intersection(jet_parton_index[i])
            if intersetion.intersection(set([0, 1, 2])) == {0,1,2} and intersetion.intersection(set([3, 4, 5])) == {3,4,5} :
                N_match_top_in_event[i] = 2
            elif intersetion.intersection(set([0, 1, 2])) != {0,1,2} or intersetion.intersection(set([3, 4, 5])) != {3,4,5}:
                N_match_top_in_event[i] = 1
            elif intersetion.intersection(set([0, 1, 2])) != {0,1,2} and intersetion.intersection(set([3, 4, 5])) != {3,4,5}:
                N_match_top_in_event[i] = 0
        print("+------------------------------------------------------------------------------------------------------+")
        print("Jet-parton matching section complete.\nFound {0} events with 1 ttbar candidate exist.\nFound {1} events with 2 ttbar candidate exist.".format( np.sum(N_match_top_in_event == 1), np.sum(N_match_top_in_event == 2)  ))
        print("+------------------------------------------------------------------------------------------------------+")
    elif MODEL == 'four_top':

        target = [i for i in range(NUM_OF_PARTON)]
        N_match_top_in_event = np.zeros([len(jet_pt)])
        for i in tqdm.trange(len(jet_parton_index)):
            
            intersetion = set(target).intersection(jet_parton_index[i])
            count_inter = 0
            if intersetion.intersection(set([0, 1, 2])) == {0,1,2}:
                count_inter += 1
            if intersetion.intersection(set([3, 4, 5])) == {3,4,5}:
                count_inter += 1
            if intersetion.intersection(set([6, 7, 8])) == {6,7,8}:
                count_inter += 1
            if intersetion.intersection(set([9, 10, 11])) == {9,10,11}:
                count_inter += 1

            N_match_top_in_event[i] = count_inter
        print("+------------------------------------------------------------------------------------------------------+")
        print("Jet-parton matching section complete.\nFound {0} events with 1 ttbar candidate exist.\nFound {1} events with 2 ttbar candidate exist.\nFound {2} events with 3 ttbar candidate exist.\nFound {3} events with 4 ttbar candidate exist.".format( np.sum(N_match_top_in_event == 1), np.sum(N_match_top_in_event == 2), np.sum(N_match_top_in_event == 3), np.sum(N_match_top_in_event == 4)  ))
        print("+------------------------------------------------------------------------------------------------------+")
    elif MODEL == 'ttbar_lep_left' or MODEL == 'ttbar_lep_right':
        N_match_top_in_event = np.zeros([len(jet_pt)])
        target = [i for i in range(NUM_OF_PARTON)]
        for i in tqdm.trange(len(jet_parton_index)):
            intersetion = set(target).intersection(jet_parton_index[i])
            if MET_delta_R_result[i] == 1 and lepton_delta_R_result[i] == 1:              
                if len(intersetion) == 4:
                    N_match_top_in_event[i] = 2
                elif 3 in intersetion:
                    N_match_top_in_event[i] = 1
                elif intersetion.intersection(set([0, 1, 2])) == {0,1,2} and (3 in intersetion) == False:
                    N_match_top_in_event[i] = 1
            else: 
                if intersetion.intersection(set([0, 1, 2])) == {0, 1, 2}:
                    N_match_top_in_event[i] = 1
                else: pass
        print("+------------------------------------------------------------------------------------------------------+")
        print("Jet-parton matching section complete.\nFound {0} events with 1 ttbar candidate exist.\nFound {1} events with 2 ttbar candidate exist.".format( np.sum(N_match_top_in_event == 1), np.sum(N_match_top_in_event == 2) ))
        print("+------------------------------------------------------------------------------------------------------+")
    elif MODEL == 'ZH':
        target_Z = jet_parton_index[:, :4]
        target_H = jet_parton_index[:, 4:]
        check_Z = (target_Z == -1).sum(1)
        check_H = (target_H == -1).sum(1)
        check_Z = np.where(check_Z >=1, 1, check_Z)
        check_H = np.where(check_H >=1, 1, check_H)
        Num_of_matched_Z = ~check_Z 
        Num_of_matched_H = ~check_H

    else : pass

    print("+------------------------------------------------------------------------------------------------------+")
    print("Writing event record to the npz file.")
    print("+------------------------------------------------------------------------------------------------------+")

    if MODEL == 'ttbar' or MODEL == 'four_top':
        np.savez_compressed(OUTPUT_FILE, 
                            jet_parton_index=jet_parton_index,
                            jet_barcode=jet_barcode,
                            jet_pt=jet_pt,
                            jet_eta=jet_eta,
                            jet_phi=jet_phi,
                            jet_mass=jet_mass,
                            jet_btag=jet_btag,
                            jet_num_of_jets=jet_num_of_jets,
                            parton_jet_index=parton_jet_index,
                            parton_pdgid=parton_pdgid,
                            parton_barcode=parton_barcode,
                            parton_pt=parton_pt,
                            parton_eta=parton_eta,
                            parton_phi=parton_phi,
                            parton_mass=parton_mass,
                            N_match_top_in_event=N_match_top_in_event)
    if MODEL == 'ZH':
        np.savez_compressed(OUTPUT_FILE, 
                            jet_parton_index=jet_parton_index,
                            jet_barcode=jet_barcode,
                            jet_pt=jet_pt,
                            jet_eta=jet_eta,
                            jet_phi=jet_phi,
                            jet_mass=jet_mass,
                            jet_btag=jet_btag,
                            jet_num_of_jets=jet_num_of_jets,
                            parton_jet_index=parton_jet_index,
                            parton_pdgid=parton_pdgid,
                            parton_barcode=parton_barcode,
                            parton_pt=parton_pt,
                            parton_eta=parton_eta,
                            parton_phi=parton_phi,
                            parton_mass=parton_mass,
                            # Num_of_matched_Z=Num_of_matched_Z,
                            # Num_of_matched_H=Num_of_matched_H,
                            )
    elif MODEL == 'ttH':
        np.savez_compressed(OUTPUT_FILE, 
                            jet_parton_index=jet_parton_index,
                            jet_barcode=jet_barcode,
                            jet_pt=jet_pt,
                            jet_eta=jet_eta,
                            jet_phi=jet_phi,
                            jet_mass=jet_mass,
                            jet_btag=jet_btag,
                            jet_num_of_jets=jet_num_of_jets,
                            parton_jet_index=parton_jet_index,
                            parton_pdgid=parton_pdgid,
                            parton_barcode=parton_barcode,
                            parton_pt=parton_pt,
                            parton_eta=parton_eta,
                            parton_phi=parton_phi,
                            parton_mass=parton_mass,
                            N_match_top_in_event=N_match_top_in_event,
                            N_match_higgs_in_event=N_match_higgs_in_event)
    elif MODEL == 'ttbar_lep_left' or MODEL == 'ttbar_lep_right':
        np.savez_compressed(OUTPUT_FILE, 
                            jet_parton_index=jet_parton_index,
                            jet_barcode=jet_barcode,
                            jet_pt=jet_pt,
                            jet_eta=jet_eta,
                            jet_phi=jet_phi,
                            jet_mass=jet_mass,
                            jet_btag=jet_btag,
                            jet_num_of_jets=jet_num_of_jets,
                            parton_jet_index=parton_jet_index,
                            parton_pdgid=parton_pdgid,
                            parton_barcode=parton_barcode,
                            parton_pt=parton_pt,
                            parton_eta=parton_eta,
                            parton_phi=parton_phi,
                            parton_mass=parton_mass,
                            N_match_top_in_event=N_match_top_in_event,
                            lepton_pt=lepton_pt,
                            lepton_eta=lepton_eta,
                            lepton_phi=lepton_phi,
                            lepton_pdgid=lepton_pdgid,
                            MET=MET,
                            MET_ETA=MET_ETA,
                            MET_PHI=MET_PHI,
                            simulation_neutrino_pt=simulation_neutrino_pt,
                            simulation_neutrino_eta=simulation_neutrino_eta,
                            simulation_neutrino_phi=simulation_neutrino_phi,
                            simulation_neutrino_pdgid=simulation_neutrino_pdgid,
                            simulation_neutrino_barcode=simulation_neutrino_barcode,
                            simulation_neutrino_mass=simulation_neutrino_mass,
                            simulation_lepton_pt=simulation_lepton_pt,
                            simulation_lepton_eta=simulation_lepton_eta,
                            simulation_lepton_phi=simulation_lepton_phi,
                            simulation_lepton_pdgid=simulation_lepton_pdgid,
                            simulation_lepton_mass=simulation_lepton_mass,
                            simulation_lepton_barcode=simulation_lepton_barcode)

    print("+------------------------------------------------------------------------------------------------------+")
    print("Event record has been send to {0}.npz.".format(OUTPUT_FILE))
    print("+------------------------------------------------------------------------------------------------------+")
