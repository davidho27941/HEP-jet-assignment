"""
Author: David Ho
Institute: National Tsing Hua university, Department of Physics, Hsinchu, Taiwan 
Mail: davidho@gapp.nthu.edu.tw
"""
import numpy as np
import itertools, uproot, sys, os, tqdm
import pandas as pd

class pdgid():
    def __init__(self):
        self.w_plus = 24
        self.w_minus = -24
        self.down = 1
        self.anti_down = -1 
        self.up = 2
        self.anti_up = -2 
        self.strange = 3 
        self.anti_strange = -3
        self.charm = 4
        self.anti_charm = -4
        self.bottom = 5 
        self.anti_bottom = -5
        self.top = 6
        self.anti_top = -6
        self.higgs = 25
        self.electron = 11 
        self.positron = -11
        self.electron_neutrino = 12
        self.anti_electron_neutrino = -12
        self.muon = 13
        self.anti_muon = -13
        self.muon_neutrino = 14
        self.anti_muon_neutrino = -14
        self.tau = 17 
        self.anti_tau = -17
        self.tau_neutrino = 18
        self.anti_tau_neutrino = -18

PID = pdgid()

def deltaPhi(phi1,phi2):
    phi = phi1-phi2
    while phi >= np.pi: phi -= np.pi*2.
    while phi < -np.pi: phi += np.pi*2.
    return phi

def delta_R(eta1, phi1, eta2, phi2):
    return np.sqrt(deltaPhi(phi1,phi2)**2+(eta1-eta2)**2)

def gaussian_fit(target):
    mean = np.average(target)
    _sigma = 0
    for i in range(len(target)):
        _sigma += (target[i] - mean)**2
    sigma = np.sqrt(_sigma/len(target))

    return mean, sigma 

def to_matrix(target_1, target_2):
    len_parton = len(target_1)
    len_jet = len(target_2)
    _matrix = np.zeros(len_parton*len_jet)
    matrix =  _matrix.reshape((len_parton, len_jet))
    for x in range(len_parton):
        _value = int(target_1[x])
        matrix[x][_value] = 1
            
    return matrix

def event_selection(PT, ETA, PHI, BTAG, LEPTON_PT, LEPTON_ETA, LEPTON_PHI, MODEL):
    marker_event = []
    marker_jet = []
    marker_btag = []
    print("MODE: {0}, len of pt: {1}".format(MODEL, len(PT)))

    if MODEL == "ttbar":
        print("Start jet marking.")
        for i in tqdm.trange(len(PT)):
        
            _marker_jet = []
            _marker_btag = []
            
            for j in range(len(PT[i])):
                if BTAG[i][j] == 1 and PT[i][j] > 25 and np.abs(ETA[i][j]) < 2.5:
                    _marker_btag.append(1) 
                else: 
                    _marker_btag.append(0) 
            
                if PT[i][j] > 25 and np.abs(ETA[i][j]) <= 2.5:
                    _marker_jet.append(1)
                else:
                    _marker_jet.append(0)
                
            marker_jet.append(np.asanyarray(_marker_jet, dtype=object))
            marker_btag.append(np.asanyarray(_marker_btag, dtype=object))
            
        marker_jet = np.asanyarray(marker_jet, dtype=object)
        marker_btag = np.asanyarray(marker_btag, dtype=object)
        print("Start event marking.")
        for i in tqdm.trange(len(PT)):
        
            if np.sum(marker_jet[i] == 1) >= 6 and np.sum(marker_btag[i] == 1) >= 2 :
                marker_event.append(1)
            else:
                marker_event.append(0)
        marker_event = np.asanyarray(marker_event, dtype=object)

    elif MODEL == "ttH":
        print("Start jet marking.")
        for i in tqdm.trange(len(PT)):
            _marker_event = []
            _marker_jet = []
            _marker_btag = []
            for j in range(len(PT[i])):
                if BTAG[i][j] == 1 and PT[i][j] > 25 and np.abs(ETA[i][j]) < 2.5:
                    _marker_btag.append(1) 
                else: 
                    _marker_btag.append(0) 
            
                if PT[i][j] > 25 and np.abs(ETA[i][j]) <= 2.5:
                    _marker_jet.append(1)
                else:
                    _marker_jet.append(0)
            marker_jet.append(np.asanyarray(_marker_jet, dtype=object))
            marker_btag.append(np.asanyarray(_marker_btag, dtype=object))
        
        marker_jet = np.asanyarray(marker_jet, dtype=object)
        marker_btag = np.asanyarray(marker_btag, dtype=object)

        print("Start event marking.")
        for i in tqdm.trange(len(PT)):
            if np.sum(marker_jet[i] == 1) >= 8 and np.sum(marker_btag[i] == 1) >= 2 :
                marker_event.append(1)
            else:
                marker_event.append(0)
        marker_event = np.asanyarray(marker_event, dtype=object)
    elif MODEL == "four_top":
        print("Start jet marking.")
        for i in tqdm.trange(len(PT)):
            _marker_event = []
            _marker_jet = []
            _marker_btag = []
            for j in range(len(PT[i])):
                if BTAG[i][j] == 1 and PT[i][j] > 25 and np.abs(ETA[i][j]) < 2.5:
                    _marker_btag.append(1) 
                else: 
                    _marker_btag.append(0) 
            
                if PT[i][j] > 25 and np.abs(ETA[i][j]) <= 2.5:
                    _marker_jet.append(1)
                else:
                    _marker_jet.append(0)
            marker_jet.append(np.asanyarray(_marker_jet, dtype=object))
            marker_btag.append(np.asanyarray(_marker_btag, dtype=object))

        marker_jet = np.asanyarray(marker_jet, dtype=object)
        marker_btag = np.asanyarray(marker_btag, dtype=object)
        print("Start event marking.")
        for i in tqdm.trange(len(PT)):
            if np.sum(marker_jet[i] == 1) >= 12 and np.sum(marker_btag[i] == 1) >= 2 :
                marker_event.append(1)
            else:
                marker_event.append(0)
        marker_event = np.asanyarray(marker_event, dtype=object)
    elif MODEL == 'ttbar_lep_left' or MODEL == "ttbar_lep_right":
        marker_lepton = []
        print("Start jet marking.")
        for i in tqdm.trange(len(PT)):
            _marker_event = []
            _marker_jet = []
            _marker_btag = []
            for j in range(len(PT[i])):
                if BTAG[i][j] == 1 and PT[i][j] > 25 and np.abs(ETA[i][j]) < 2.5:
                    _marker_btag.append(1) 
                else: 
                    _marker_btag.append(0) 
            
                if PT[i][j] > 25 and np.abs(ETA[i][j]) <= 2.5:
                    _marker_jet.append(1)
                else:
                    _marker_jet.append(0)
            marker_jet.append(np.asanyarray(_marker_jet, dtype=object))
            marker_btag.append(np.asanyarray(_marker_btag, dtype=object))
        
        marker_jet = np.asanyarray(marker_jet, dtype=object)
        marker_btag = np.asanyarray(marker_btag, dtype=object)
        
        #Remove electron from jets catogary
        for i in range(len(PT)):
            
            for j in range(len(PT[i])):
                for k in range(len(LEPTON_PT[i])):
                    if delta_R(ETA[i][j], PHI[i][j], LEPTON_ETA[i][k], LEPTON_PHI[i][k]) < 0.4:
                        marker_jet[i][j] = 0
                        
                    else : pass 
        
        for i in tqdm.trange(len(LEPTON_PT)):
            _marker_lepton = []
            for j in range(len(LEPTON_PT[i])):
                if LEPTON_PT[i][j] > 25 and np.abs(LEPTON_ETA[i][j]) < 2.5:
                    _marker_lepton.append(1)
                else :
                    _marker_lepton.append(0)
            marker_lepton.append(np.asanyarray(_marker_lepton, dtype=object))
        marker_lepton = np.asanyarray(marker_lepton, dtype=object)
        print("Start event marking.")
        for i in tqdm.trange(len(PT)):
            if np.sum(marker_jet[i] == 1) >= 4 and np.sum(marker_btag[i] == 1) >= 2 and np.sum(marker_lepton[i] ==1) == 1 and len(marker_lepton[i]) == 1:
                marker_event.append(1)
            else:
                marker_event.append(0)
        marker_event = np.asanyarray(marker_event, dtype=object)

    else:
        print("Please select a correct mode. The mode available:\n1. ttbar.\n2. ttH\n3. four_top")
    
    return marker_event, marker_jet, marker_btag


def shifted_particle_tracing(dataset, PID_daughter, idx):
    if (dataset.iloc[idx,6] == PID_daughter):
        return dataset.iloc[idx,4]

def particle_tracing(dataset, PID, STATUS, MODEL):
    if MODEL == 'ttbar' or MODEL == 'ttH' or MODEL == "ttbar_lep_right" or MODEL == "ttbar_lep_left":
        for i in range(len(dataset)):
            if(dataset.iloc[i,1] == STATUS and dataset.iloc[i,6] == PID ): 
                daughter_index = int(dataset.iloc[i,0])
        if( dataset.iloc[daughter_index,6] == PID ):
            shifted_particle_index = dataset.iloc[daughter_index, 4]


        while dataset.iloc[shifted_particle_index,6] == PID:
            init_shifted_particle_index = shifted_particle_index
            shifted_particle_index = shifted_particle_tracing(dataset, PID, init_shifted_particle_index)       

        dauthter_idx_1 = dataset.iloc[init_shifted_particle_index, 4]
        daughter_pid_1 = dataset.iloc[dauthter_idx_1, 6]

        dauthter_idx_2 = dataset.iloc[init_shifted_particle_index, 5]
        daughter_pid_2 = dataset.iloc[dauthter_idx_2, 6]

        return init_shifted_particle_index, dauthter_idx_1, daughter_pid_1, dauthter_idx_2, daughter_pid_2
    elif MODEL == 'four_top':
        daughter_index = []
        for i in range(len(dataset)):
            if(dataset.iloc[i,1] == STATUS and dataset.iloc[i,6] == PID ): 
                daughter_index.append(int(dataset.iloc[i,0]))
        daughter_index_1, daughter_index_2 = daughter_index[0], daughter_index[1]

        if( dataset.iloc[daughter_index_1,6] == PID ):
            shifted_particle_index_1 = dataset.iloc[daughter_index_1, 4]
        if( dataset.iloc[daughter_index_2,6] == PID ):
            shifted_particle_index_2 = dataset.iloc[daughter_index_2, 4]


        while dataset.iloc[shifted_particle_index_1,6] == PID:
            init_shifted_particle_index_1 = shifted_particle_index_1
            shifted_particle_index_1 = shifted_particle_tracing(dataset, PID, init_shifted_particle_index_1)       

        while dataset.iloc[shifted_particle_index_2,6] == PID:
            init_shifted_particle_index_2 = shifted_particle_index_2
            shifted_particle_index_2 = shifted_particle_tracing(dataset, PID, init_shifted_particle_index_2)

        dauthter_idx_1_1 = dataset.iloc[init_shifted_particle_index_1, 4]
        daughter_pid_1_1 = dataset.iloc[dauthter_idx_1_1, 6]

        dauthter_idx_1_2 = dataset.iloc[init_shifted_particle_index_1, 5]
        daughter_pid_1_2 = dataset.iloc[dauthter_idx_1_2, 6]

        dauthter_idx_2_1 = dataset.iloc[init_shifted_particle_index_2, 4]
        daughter_pid_2_1 = dataset.iloc[dauthter_idx_2_1, 6]

        dauthter_idx_2_2 = dataset.iloc[init_shifted_particle_index_2, 5]
        daughter_pid_2_2 = dataset.iloc[dauthter_idx_2_2, 6]

        return init_shifted_particle_index_1, init_shifted_particle_index_2, dauthter_idx_1_1, daughter_pid_1_1, dauthter_idx_1_2, daughter_pid_1_2, dauthter_idx_2_1, daughter_pid_2_1, dauthter_idx_2_2, daughter_pid_2_2
    elif MODEL == 'four_top':
        print("Work in progress")
    else :
        print("Plese select a correct model.")

#tracing the daughters
#Input two daughter of top/top_bar and find their daughter
def quark_finder(dataset, mother_idx_1, mother_idx_2):
    
    #Specific two daughter of top
    def W_b_specifier(dataset, input_1_idx, input_2_idx):
        if dataset.iloc[int(input_1_idx),6] == PID.w_plus or dataset.iloc[int(input_1_idx),6] == PID.w_minus :
            return int(input_1_idx), int(dataset.iloc[int(input_1_idx),6]), int(input_2_idx)
        elif dataset.iloc[int(input_1_idx),6] == PID.bottom or dataset.iloc[int(input_1_idx),6] == PID.anti_bottom :
            return  int(input_2_idx), int(dataset.iloc[int(input_1_idx),6]), int(input_1_idx)
        else :
            pass
            #print("Please check your data.")
    
    W_boson_idx, mother_pid, b_quark_idx = W_b_specifier(dataset, mother_idx_1, mother_idx_2)
    
    #Find the two daughters of boson
    
    daughter_1_idx = dataset.iloc[W_boson_idx, 4]
    daughter_1_pid = dataset.iloc[daughter_1_idx, 6]
    daughter_2_idx = dataset.iloc[W_boson_idx, 5]
    daughter_2_pid = dataset.iloc[daughter_2_idx, 6]

    
    if daughter_1_pid == mother_pid or daughter_2_pid == mother_pid:

        init_idx = W_boson_idx
        daughter_pid = daughter_1_pid
        if daughter_2_pid == mother_pid:
            daughter_pid = daughter_2_pid
        while daughter_pid == mother_pid :
            daughter_1_idx = dataset.iloc[int(init_idx), 4]
            daughter_2_idx = dataset.iloc[int(init_idx), 5]

            daughter_1_pid = dataset.iloc[int(daughter_1_idx), 6]
            daughter_2_pid = dataset.iloc[int(daughter_2_idx), 6]

            daughter_pid = daughter_1_pid
            init_idx = daughter_1_idx
            if daughter_2_pid == mother_pid:
                daughter_pid = daughter_2_pid
                init_idx = daughter_2_idx
    
    return  b_quark_idx, daughter_1_idx, daughter_2_idx


def deltaR_matching(NUM_OF_PARTON, NUM_OF_JET, PARTON_ETA, PARTON_PHI, JET_ETA, JET_PHI, CUTS, MODEL):
    """
    PARTON_ETA: Array, a list of partons's eta in a event.
    PARTON_PHI: Array, a list of partons's phi in a event.
    JET_ETA: Array, a list of jet's eta in a event.
    JET_PHI: Array, a list of jet's phi in a event.
    """
    
    _dR_between_parton_jet = []

    _parton_jet_index = [int(999999999*i/i) for i in range(1, NUM_OF_PARTON+1)]
    _jet_parton_index = [int(999999999*i/i) for i in range(1, NUM_OF_JET+1)]

    
    _jet_to_parton_list = np.zeros(len(PARTON_ETA))
    _parton_to_jet_list = np.zeros(len(JET_ETA))


    j = 0
    a = 0
    b = 0
    while a < NUM_OF_PARTON :
        for b in range( NUM_OF_JET ):
            _dR_between_parton_jet.append(delta_R( PARTON_ETA[a], PARTON_PHI[a], JET_ETA[b], JET_PHI[b]))
            j +=1
        a += 1 

    array = np.reshape(np.array(_dR_between_parton_jet), [NUM_OF_PARTON, NUM_OF_JET])
    array_index = [x for x in range(len(PARTON_ETA))]

    _dataset = pd.DataFrame(index = array_index, data = array).T
    
    for j in range(len(PARTON_ETA)):
        min_val = _dataset.stack().min()
        if min_val < CUTS:
            min_idx, min_col = _dataset.stack().idxmin()
            
            _jet_to_parton_list[j] = int(min_idx)
            _parton_to_jet_list[j] = int(min_col)
            _dataset = _dataset.drop([min_col], axis=1)
            _dataset = _dataset.drop([min_idx], axis=0)

        else:
            _jet_to_parton_list[j] = 'Nan'
            _parton_to_jet_list[j] = 'Nan'
    for k in range(NUM_OF_PARTON, NUM_OF_JET):
        _parton_to_jet_list[k] = 'Nan'
    
    
    if MODEL == 'ttbar':
        for j in range(len(JET_ETA)):
            if _parton_to_jet_list[j] == 0 :
                _parton_jet_index[0] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 1 :
                _parton_jet_index[1] = int(_jet_to_parton_list[j])
            else: 
                pass
            if _parton_to_jet_list[j] == 2 :
                _parton_jet_index[2] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 3 :
                _parton_jet_index[3] = int(_jet_to_parton_list[j])
            else:
                pass

            if _parton_to_jet_list[j] == 4 :
                _parton_jet_index[4] = int(_jet_to_parton_list[j])
            else:
                pass

            if _parton_to_jet_list[j] == 5 :
                _parton_jet_index[5] = int(_jet_to_parton_list[j])
            else: 
                pass
    elif MODEL == 'ttH':
        for j in range(len(JET_ETA)):
            if _parton_to_jet_list[j] == 0 :
                _parton_jet_index[0] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 1 :
                _parton_jet_index[1] = int(_jet_to_parton_list[j])
            else: 
                pass
            if _parton_to_jet_list[j] == 2 :
                _parton_jet_index[2] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 3 :
                _parton_jet_index[3] = int(_jet_to_parton_list[j])
            else:
                pass

            if _parton_to_jet_list[j] == 4 :
                _parton_jet_index[4] = int(_jet_to_parton_list[j])
            else:
                pass

            if _parton_to_jet_list[j] == 5 :
                _parton_jet_index[5] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 6 :
                _parton_jet_index[6] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 7 :
                _parton_jet_index[7] = int(_jet_to_parton_list[j])
            else: 
                pass
    elif MODEL == 'four_top':
        for j in range(len(JET_ETA)):
            if _parton_to_jet_list[j] == 0 :
                _parton_jet_index[0] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 1 :
                _parton_jet_index[1] = int(_jet_to_parton_list[j])
            else: 
                pass
            if _parton_to_jet_list[j] == 2 :
                _parton_jet_index[2] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 3 :
                _parton_jet_index[3] = int(_jet_to_parton_list[j])
            else:
                pass

            if _parton_to_jet_list[j] == 4 :
                _parton_jet_index[4] = int(_jet_to_parton_list[j])
            else:
                pass

            if _parton_to_jet_list[j] == 5 :
                _parton_jet_index[5] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 6 :
                _parton_jet_index[6] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 7 :
                _parton_jet_index[7] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 8 :
                _parton_jet_index[8] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 9 :
                _parton_jet_index[9] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 10 :
                _parton_jet_index[10] = int(_jet_to_parton_list[j])
            else: 
                pass
            
            if _parton_to_jet_list[j] == 11 :
                _parton_jet_index[11] = int(_jet_to_parton_list[j])
            else: 
                pass
    elif MODEL == 'ttbar_lep_left' or MODEL == 'ttbar_lep_right':
        for j in range(len(JET_ETA)):
            if _parton_to_jet_list[j] == 0 :
                _parton_jet_index[0] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 1 :
                _parton_jet_index[1] = int(_jet_to_parton_list[j])
            else: 
                pass
            if _parton_to_jet_list[j] == 2 :
                _parton_jet_index[2] = int(_jet_to_parton_list[j])
            else: 
                pass

            if _parton_to_jet_list[j] == 3 :
                _parton_jet_index[3] = int(_jet_to_parton_list[j])
            else:
                pass
    else:
        print("Delta R matching faild, please check your model.")

    ll = len(JET_ETA)
    for k in range(NUM_OF_PARTON):
        for m in range(ll):
            if _jet_to_parton_list[k] == int(m):
                _jet_parton_index[int(m)] = _parton_to_jet_list[k]
            else: pass

    for l in range(NUM_OF_JET):
        if _jet_parton_index[l] > NUM_OF_PARTON:
            _jet_parton_index[l] = 'nan'
    for l in range(NUM_OF_PARTON): 
        if _parton_jet_index[l] > NUM_OF_JET:
            _parton_jet_index[l] = 'Nan'
    
    return np.asanyarray(_jet_parton_index, dtype=object), np.asanyarray(_parton_jet_index, dtype=object)

def barcode_recorder(SOURCE, MODEL):
    _jet_barcode = [0*i for i in range(len(SOURCE))]
    # print(_jet_barcode)
    if MODEL == "ttbar":
        barcode = np.array([34, 40, 40, 17, 20, 20])
        for i in range(len(SOURCE)):
            for j in range(len(barcode)):
                if SOURCE[i] == int(j):
                    _jet_barcode[i] = barcode[int(j)]
                else :
                    _jet_barcode[i] = 'Nan'
    elif MODEL == "ttH":
        barcode = np.array([68, 80, 80, 34, 40, 40, 1, 1])
        for i in range(len(SOURCE)):
            for j in range(len(barcode)):
                if SOURCE[i] == int(j):
                    _jet_barcode[i] = barcode[int(j)]
                else :
                    _jet_barcode[i] = 'Nan'

    elif MODEL == "four_top":
        barcode = np.array([2056, 2176, 2176, 516, 576, 576, 1028, 1056, 1056, 257, 272, 272])
        for i in range(len(SOURCE)):
            for j in range(len(barcode)):
                if SOURCE[i] == int(j):
                    _jet_barcode[i] = barcode[int(j)]
                else :
                    _jet_barcode[i] = 'Nan'
    elif MODEL == 'ttbar_lep_left': 
        barcode = np.array([34, 17, 20, 20])
        for i in range(len(SOURCE)):
            for j in range(len(barcode)):
                if SOURCE[i] == int(j):
                    _jet_barcode[i] = barcode[int(j)]
                else :
                    _jet_barcode[i] = 'Nan'
    elif MODEL == 'ttbar_lep_right': 
        barcode = np.array([34, 40, 40, 17])
        for i in range(len(SOURCE)):
            for j in range(len(barcode)):
                if SOURCE[i] == int(j):
                    _jet_barcode[i] = barcode[int(j)]
                else :
                    _jet_barcode[i] = 'Nan'
    else:
        print("Please select a correct model.")
    
    return np.asanyarray(_jet_barcode, dtype=object)

def chi_square_minimizer( jet_pt_chi2, jet_eta_chi2, jet_phi_chi2, jet_btag_chi2, jet_mass_chi2, MODEL, EXTRA):
    
    num_of_btag = np.sum(np.array(jet_btag_chi2) ==1)

    class jet_cand_properties():
        def __init__(self, idx):
            self.idx = idx
            self.pt = jet_pt_chi2[self.idx]
            self.eta = jet_eta_chi2[self.idx]
            self.phi = jet_phi_chi2[self.idx]
            self.mass = jet_mass_chi2[self.idx]
            # scale = -0.0008228230613626063 * self.pt - 0.051359995969670155
            # scale = 1 - (scale/2)
            scale = 1

            tmp_px = self.pt*np.cos(self.phi)
            tmp_py = self.pt*np.sin(self.phi)
            tmp_pz = self.pt*np.sinh(self.eta)

            self.px = tmp_px*scale
            self.py = tmp_py*scale
            self.pz = tmp_pz*scale
            self.e = np.sqrt( (self.px**2 + self.py**2 + self.pz**2) + self.mass**2 )

    def cal_two_parton_inv(jet1, jet2):
        part_1 = (jet1.e + jet2.e)**2
        part_2 = (jet1.px + jet2.px)**2
        part_3 = (jet1.py + jet2.py)**2
        part_4 = (jet1.pz + jet2.pz)**2
        return np.sqrt( part_1 - part_2 - part_3 - part_4 )

    def cal_three_parton_inv(jet1, jet2, jet3):
        part_1 = (jet1.e + jet2.e + jet3.e)**2
        part_2 = (jet1.px + jet2.px + jet3.px)**2
        part_3 = (jet1.py + jet2.py + jet3.py)**2
        part_4 = (jet1.pz + jet2.pz + jet3.pz)**2
        return np.sqrt( part_1 - part_2 - part_3 - part_4 )

    if MODEL == 'ttbar':
        _bjet_list = []
        
        bjet = []
        _jet_list = []

        min_chi2 = -1
        m_W = 81.3
        m_top = 172.7
        sigma_W = 12.3
        sigma_t = 26.3

        _parton_jet_index = np.array(['Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan'])
        
        _jet_index = []
        for i in range(len(jet_pt_chi2)):
            _jet_index.append(i)

        for i in range(len(jet_btag_chi2)):
            if jet_btag_chi2[i] == 1:
                _bjet_list.append(i)
            else :
                _jet_list.append(i)
                
        _bjet = itertools.combinations(_bjet_list, 2)
        
        for a in _bjet:
            bjet.append(a)

        bjet = np.array(bjet, dtype='object')

        jet_index_candidate = []

        for i in range(len(bjet)):

            jet = []
            
            tmp_jet_index = _bjet_list.copy()
            for c in range(len(bjet[i])): 
                
                _tmp = bjet[i][c]
                tmp_jet_index.remove(_tmp)
            
            tmp_jet_list = _jet_list.copy()

            for d in tmp_jet_index:
                tmp_jet_list.append(d)
            
            _jet = itertools.permutations(tmp_jet_list, 4)

            for b in _jet:
                jet.append(b)

            jet = np.array(jet, dtype='object')

            
            for j in range(len(jet)):
            
                _jet_index_candidate = []
                _jet_index_candidate.append(bjet[i][0])
                _jet_index_candidate.append(bjet[i][1])
                _jet_index_candidate.append(jet[j][0])
                _jet_index_candidate.append(jet[j][1])
                _jet_index_candidate.append(jet[j][2])
                _jet_index_candidate.append(jet[j][3])
                jet_index_candidate.append(_jet_index_candidate)
        _cand_record  = []
        _chi2_value = []
        for i in range(len(jet_index_candidate)):

            b_1_idx = jet_index_candidate[i][0]
            b_2_idx = jet_index_candidate[i][1]

            j_1_idx = jet_index_candidate[i][2]
            j_2_idx = jet_index_candidate[i][3]
            j_3_idx = jet_index_candidate[i][4]
            j_4_idx = jet_index_candidate[i][5]

            bjet_1 = jet_cand_properties(b_1_idx)
            bjet_2 = jet_cand_properties(b_2_idx)

            jet_1 = jet_cand_properties(j_1_idx)
            jet_2 = jet_cand_properties(j_2_idx)
            jet_3 = jet_cand_properties(j_3_idx)
            jet_4 = jet_cand_properties(j_4_idx)
            
            W_1_inv = cal_two_parton_inv(jet_1, jet_2)
            W_2_inv = cal_two_parton_inv(jet_3, jet_4)
            top_1_inv = cal_three_parton_inv(bjet_1, jet_1, jet_2)
            top_2_inv = cal_three_parton_inv(bjet_2, jet_3, jet_4)
            
            if EXTRA == "normal":
                chi2_part_1 = (top_1_inv - top_2_inv)**2
                chi2_part_2 = (W_1_inv - m_W)**2
                chi2_part_3 = (W_2_inv - m_W)**2

                chi2_tmp = chi2_part_1/(2*(sigma_t**2)) + chi2_part_2/sigma_W**2 + chi2_part_3/sigma_W**2
            elif EXTRA == "mtop_base":
                chi2_part_1 = (top_1_inv - m_top)**2
                chi2_part_2 = (top_2_inv - m_top)**2
                chi2_part_3 = (W_1_inv - m_W)**2
                chi2_part_4 = (W_2_inv - m_W)**2
                
                chi2_tmp = chi2_part_1/sigma_t**2 + chi2_part_2/sigma_t**2  + chi2_part_3/sigma_W**2 + chi2_part_4/sigma_W**2
            else: print("Please input a available extra option")
                
            
            if (min_chi2 < 0 or chi2_tmp < min_chi2 ):
                min_chi2 = chi2_tmp
                jet_1_best_idx = j_1_idx
                jet_2_best_idx = j_2_idx
                jet_3_best_idx = j_3_idx
                jet_4_best_idx = j_4_idx
                b_1_best_idx = b_1_idx
                b_2_best_idx = b_2_idx
                _cand_record.append([[b_1_best_idx, jet_1_best_idx, jet_2_best_idx, b_2_best_idx, jet_3_best_idx, jet_4_best_idx]])
                _chi2_value.append(min_chi2)
                _parton_jet_index = np.array([b_1_best_idx, jet_1_best_idx, jet_2_best_idx, b_2_best_idx, jet_3_best_idx, jet_4_best_idx])
            else: 
                pass
        _jet_parton_index = [9999999*i/i for i in range(1, len(jet_pt_chi2)+1)]
    
        chi2_value = _chi2_value[-10:]
        cand_record = _cand_record[-10:]
        del _chi2_value, _cand_record
        for k in range(len(jet_pt_chi2)):
            for l in range(len(_parton_jet_index)):
                if _parton_jet_index[l] == int(k):
                    _jet_parton_index[k] = int(l)
                else :
                    pass
        
        for k in range(len(_jet_parton_index)):
                if _jet_parton_index[k] == 9999999:
                    _jet_parton_index[k] = 'Nan'
                else : 
                    pass
        
        return min_chi2, np.asanyarray(_parton_jet_index, dtype=object), np.asanyarray(_jet_parton_index, dtype=object), np.asanyarray(cand_record, dtype=object), np.asanyarray(chi2_value, dtype=object)
        
    elif MODEL == 'ttH':
        tmp_jet_list = []
        tmp_bjet_list = []

        min_chi2 = -1
        m_W = 81.3
        m_h = 125
        sigma_W = 18.7
        sigma_t = 28.8
        sigma_h = 22.3

        _parton_jet_index = np.array(['Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan'])
        
        _jet_index = []

        for i in range(len(jet_pt_chi2)):
            _jet_index.append(i)

        for i in range(len(jet_btag_chi2)):
            if jet_btag_chi2[i] == 1:
                tmp_bjet_list.append(i)
            else :
                tmp_jet_list.append(i)
        
        if num_of_btag == 4:
            b_jet = []
            jet = []
            _bjet = itertools.combinations(tmp_bjet_list, 4)
            _jet = itertools.combinations(tmp_jet_list, 4)
            for a, b in zip(_bjet, _jet):
                b_jet.append(a)
                jet.append(b)
            b_jet = np.array(b_jet, dtype='object')
            jet = np.array(jet, dtype='object')

            jet_index_candidate = []

            for i in range(len(b_jet)):
                for j in range(len((jet))):
                    _jet_index_candidate = []
                    _jet_index_candidate.append(b_jet[i][0])
                    _jet_index_candidate.append(b_jet[i][1])
                    _jet_index_candidate.append(b_jet[i][2])
                    _jet_index_candidate.append(b_jet[i][3])
                    _jet_index_candidate.append(jet[j][0])
                    _jet_index_candidate.append(jet[j][1])
                    _jet_index_candidate.append(jet[j][2])
                    _jet_index_candidate.append(jet[j][3])
                    jet_index_candidate.append(_jet_index_candidate)
        elif num_of_btag != 4:
            
            require_num_bjet = 4
            lack_of_bjet = require_num_bjet - num_of_btag 
            if lack_of_bjet > 0:
                _jet_for_append = itertools.combinations(tmp_jet_list, lack_of_bjet)
                
                jet_for_append = []
                for b in _jet_for_append:
                    jet_for_append.append(b)

                jet_for_append = np.array(jet_for_append, dtype='object')
                for i in range(len(jet_for_append)):
                    b_jet = []
                    jet = []
                    tmp_jet_index = tmp_jet_list.copy()
                    for c in range(len(jet_for_append[i])): 
                        _tmp = jet_for_append[i][c]
                        tmp_jet_index.remove(_tmp)
                    
                    tmp_bjet_index = tmp_bjet_list.copy()

                    for d in jet_for_append[i]:                    
                        tmp_bjet_index.append(int(d))
                    

                    _bjet = itertools.permutations(tmp_bjet_index, 4)
                    _jet = itertools.permutations(tmp_jet_index, 4)
                    
                    for a, b in zip(_jet, _bjet):
                        jet.append(a)
                        b_jet.append(b)
                    
                    jet = np.array(jet, dtype='object')
                    b_jet = np.array(b_jet, dtype='object')

                    jet_index_candidate = []

                    for j in range(len(b_jet)):
                        for k in range(len((jet))):
                            _jet_index_candidate = []
                            _jet_index_candidate.append(b_jet[j][0])
                            _jet_index_candidate.append(b_jet[j][1])
                            _jet_index_candidate.append(b_jet[j][2])
                            _jet_index_candidate.append(b_jet[j][3])
                            _jet_index_candidate.append(jet[k][0])
                            _jet_index_candidate.append(jet[k][1])
                            _jet_index_candidate.append(jet[k][2])
                            _jet_index_candidate.append(jet[k][3])
                            jet_index_candidate.append(_jet_index_candidate)

            elif lack_of_bjet < 0:
                b_jet = []
                jet = []
                _bjet = itertools.combinations(tmp_bjet_list, 4)
        
                for a in _bjet:
                    b_jet.append(a)

                b_jet = np.array(b_jet, dtype='object')

                jet_index_candidate = []

                for i in range(len(b_jet)):

                    jet = []
                    
                    tmp_jet_index = tmp_bjet_list.copy()
                    for c in range(len(b_jet[i])): 
                        
                        _tmp = b_jet[i][c]
                        tmp_jet_index.remove(_tmp)
                    
                    _tmp_jet_list = tmp_jet_list.copy()

                    for d in tmp_jet_index:
                        _tmp_jet_list.append(d)
                    
                    _jet = itertools.permutations(_tmp_jet_list, 4)

                    for b in _jet:
                        jet.append(b)

                    jet = np.array(jet, dtype='object')

                    for j in range(len(jet)):
                    
                        _jet_index_candidate = []
                        _jet_index_candidate.append(b_jet[i][0])
                        _jet_index_candidate.append(b_jet[i][1])
                        _jet_index_candidate.append(b_jet[i][2])
                        _jet_index_candidate.append(b_jet[i][3])
                        _jet_index_candidate.append(jet[j][0])
                        _jet_index_candidate.append(jet[j][1])
                        _jet_index_candidate.append(jet[j][2])
                        _jet_index_candidate.append(jet[j][3])
                        jet_index_candidate.append(_jet_index_candidate)
                        
        _cand_record  = []
        _chi2_value = []
        for i in range(len(jet_index_candidate)):
            b_1_idx = jet_index_candidate[i][0]
            b_2_idx = jet_index_candidate[i][1]
            b_3_idx = jet_index_candidate[i][2]
            b_4_idx = jet_index_candidate[i][3]
            j_1_idx = jet_index_candidate[i][4]
            j_2_idx = jet_index_candidate[i][5]
            j_3_idx = jet_index_candidate[i][6]
            j_4_idx = jet_index_candidate[i][7]

            bjet_1 = jet_cand_properties(b_1_idx)
            bjet_2 = jet_cand_properties(b_2_idx)
            bjet_3 = jet_cand_properties(b_3_idx)
            bjet_4 = jet_cand_properties(b_4_idx)
            jet_1 = jet_cand_properties(j_1_idx)
            jet_2 = jet_cand_properties(j_2_idx)
            jet_3 = jet_cand_properties(j_3_idx)
            jet_4 = jet_cand_properties(j_4_idx)
            
            W_1_inv = cal_two_parton_inv(jet_1, jet_2)
            W_2_inv = cal_two_parton_inv(jet_3, jet_4)
            top_1_inv = cal_three_parton_inv(bjet_1, jet_1, jet_2)
            top_2_inv = cal_three_parton_inv(bjet_2, jet_3, jet_4)
            higgs_inv = cal_two_parton_inv(bjet_3, bjet_4)
            
            chi2_part_1 = (top_1_inv - top_2_inv)**2
            chi2_part_2 = (W_1_inv - m_W)**2
            chi2_part_3 = (W_2_inv - m_W)**2
            chi2_part_4 = (higgs_inv - m_h)**2
            
            chi2_tmp = chi2_part_1/(2*(sigma_t**2)) + chi2_part_2/sigma_W**2 + chi2_part_3/sigma_W**2 + (chi2_part_4)/sigma_h**2
            
            _chi2_value.append(chi2_tmp)
            _cand_record.append([[b_1_idx, j_1_idx, j_2_idx, b_2_idx, j_3_idx, j_4_idx, b_3_idx, b_4_idx]])
            if (min_chi2 < 0 or chi2_tmp < min_chi2 ):
                min_chi2 = chi2_tmp
                jet_1_best_idx = j_1_idx
                jet_2_best_idx = j_2_idx
                jet_3_best_idx = j_3_idx
                jet_4_best_idx = j_4_idx
                b_1_best_idx = b_1_idx
                b_2_best_idx = b_2_idx
                b_3_best_idx = b_3_idx
                b_4_best_idx = b_4_idx
                _cand_record.append([[b_1_best_idx, jet_1_best_idx, jet_2_best_idx, b_2_best_idx, jet_3_best_idx, jet_4_best_idx, b_3_best_idx, b_4_best_idx]])
                _chi2_value.append(min_chi2)
                _parton_jet_index = np.array([b_1_best_idx, jet_1_best_idx, jet_2_best_idx, b_2_best_idx, jet_3_best_idx, jet_4_best_idx, b_3_best_idx, b_4_best_idx])
            else: 
                pass
        _jet_parton_index = [9999999*i/i for i in range(1, len(jet_pt_chi2)+1)]
        
        chi2_value = _chi2_value[-10:]
        cand_record = _cand_record[-10:]
        del _chi2_value, _cand_record
        for k in range(len(jet_pt_chi2)):
            for l in range(len(_parton_jet_index)):
                if _parton_jet_index[l] == int(k):
                    _jet_parton_index[k] = int(l)
                else :
                    pass
        
        for k in range(len(_jet_parton_index)):
                if _jet_parton_index[k] == 9999999:
                    _jet_parton_index[k] = 'Nan'
                else : 
                    pass
        
        return min_chi2, np.asanyarray(_parton_jet_index, dtype=object), np.asanyarray(_jet_parton_index, dtype=object), np.asanyarray(cand_record, dtype=object), np.asanyarray(chi2_value, dtype=object)
    elif MODEL == "four_top":
        tmp_jet_list = []
        tmp_bjet_list = []

        min_chi2 = -1
        m_W = 81.3
        m_top = 172.7
        sigma_W = 18.7
        sigma_t = 28.8


        _parton_jet_index = np.array(['Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan', 'Nan'])
        
        _jet_index = []

        for i in range(len(jet_pt_chi2)):
            _jet_index.append(i)

        for i in range(len(jet_btag_chi2)):
            if jet_btag_chi2[i] == 1:
                tmp_bjet_list.append(i)
            else :
                tmp_jet_list.append(i)
        
        if num_of_btag == 4:
            b_jet = []
            jet = []
            _bjet = itertools.combinations(tmp_bjet_list, 4)
            _jet = itertools.combinations(tmp_jet_list, 8)
            for a, b in zip(_bjet, _jet):
                b_jet.append(a)
                jet.append(b)
            b_jet = np.array(b_jet, dtype='object')
            jet = np.array(jet, dtype='object')

            jet_index_candidate = []

            for i in range(len(b_jet)):
                for j in range(len((jet))):
                    _jet_index_candidate = []
                    _jet_index_candidate.append(b_jet[i][0])
                    _jet_index_candidate.append(b_jet[i][1])
                    _jet_index_candidate.append(b_jet[i][2])
                    _jet_index_candidate.append(b_jet[i][3])
                    _jet_index_candidate.append(jet[j][0])
                    _jet_index_candidate.append(jet[j][1])
                    _jet_index_candidate.append(jet[j][2])
                    _jet_index_candidate.append(jet[j][3])
                    _jet_index_candidate.append(jet[j][4])
                    _jet_index_candidate.append(jet[j][5])
                    _jet_index_candidate.append(jet[j][6])
                    _jet_index_candidate.append(jet[j][7])
                    
                    jet_index_candidate.append(_jet_index_candidate)
        elif num_of_btag != 4:
            
            require_num_bjet = 4
            lack_of_bjet = require_num_bjet - num_of_btag 
            if lack_of_bjet > 0:
                _jet_for_append = itertools.combinations(tmp_jet_list, lack_of_bjet)
                
                jet_for_append = []
                for b in _jet_for_append:
                    jet_for_append.append(b)

                jet_for_append = np.array(jet_for_append, dtype='object')
                for i in range(len(jet_for_append)):
                    b_jet = []
                    jet = []
                    tmp_jet_index = tmp_jet_list.copy()
                    for c in range(len(jet_for_append[i])): 
                        _tmp = jet_for_append[i][c]
                        tmp_jet_index.remove(_tmp)
                    
                    tmp_bjet_index = tmp_bjet_list.copy()

                    for d in jet_for_append[i]:                    
                        tmp_bjet_index.append(int(d))
                    

                    _bjet = itertools.permutations(tmp_bjet_index, 4)
                    _jet = itertools.permutations(tmp_jet_index, 8)
                    
                    for a, b in zip(_jet, _bjet):
                        jet.append(a)
                        b_jet.append(b)
                    
                    jet = np.array(jet, dtype='object')
                    b_jet = np.array(b_jet, dtype='object')

                    jet_index_candidate = []

                    for j in range(len(b_jet)):
                        for k in range(len((jet))):
                            _jet_index_candidate = []
                            _jet_index_candidate.append(b_jet[j][0])
                            _jet_index_candidate.append(b_jet[j][1])
                            _jet_index_candidate.append(b_jet[j][2])
                            _jet_index_candidate.append(b_jet[j][3])
                            _jet_index_candidate.append(jet[k][0])
                            _jet_index_candidate.append(jet[k][1])
                            _jet_index_candidate.append(jet[k][2])
                            _jet_index_candidate.append(jet[k][3])
                            _jet_index_candidate.append(jet[j][4])
                            _jet_index_candidate.append(jet[j][5])
                            _jet_index_candidate.append(jet[j][6])
                            _jet_index_candidate.append(jet[j][7])
                            jet_index_candidate.append(_jet_index_candidate)

            elif lack_of_bjet < 0:
                b_jet = []
                jet = []
                _bjet = itertools.combinations(tmp_bjet_list, 4)
        
                for a in _bjet:
                    b_jet.append(a)

                b_jet = np.array(b_jet, dtype='object')

                jet_index_candidate = []

                for i in range(len(b_jet)):

                    jet = []
                    
                    tmp_jet_index = tmp_bjet_list.copy()
                    for c in range(len(b_jet[i])): 
                        
                        _tmp = b_jet[i][c]
                        tmp_jet_index.remove(_tmp)
                    
                    _tmp_jet_list = tmp_jet_list.copy()

                    for d in tmp_jet_index:
                        _tmp_jet_list.append(d)
                    
                    _jet = itertools.permutations(_tmp_jet_list, 8)

                    for b in _jet:
                        jet.append(b)

                    jet = np.array(jet, dtype='object')

                    for j in range(len(jet)):
                    
                        _jet_index_candidate = []
                        _jet_index_candidate.append(b_jet[i][0])
                        _jet_index_candidate.append(b_jet[i][1])
                        _jet_index_candidate.append(b_jet[i][2])
                        _jet_index_candidate.append(b_jet[i][3])
                        _jet_index_candidate.append(jet[j][0])
                        _jet_index_candidate.append(jet[j][1])
                        _jet_index_candidate.append(jet[j][2])
                        _jet_index_candidate.append(jet[j][3])
                        _jet_index_candidate.append(jet[j][4])
                        _jet_index_candidate.append(jet[j][5])
                        _jet_index_candidate.append(jet[j][6])
                        _jet_index_candidate.append(jet[j][7])
                        jet_index_candidate.append(_jet_index_candidate)
                        
        _cand_record  = []
        _chi2_value = []
        for i in range(len(jet_index_candidate)):
            b_1_idx = jet_index_candidate[i][0]
            b_2_idx = jet_index_candidate[i][1]
            b_3_idx = jet_index_candidate[i][2]
            b_4_idx = jet_index_candidate[i][3]
            j_1_idx = jet_index_candidate[i][4]
            j_2_idx = jet_index_candidate[i][5]
            j_3_idx = jet_index_candidate[i][6]
            j_4_idx = jet_index_candidate[i][7]
            j_5_idx = jet_index_candidate[i][8]
            j_6_idx = jet_index_candidate[i][9]
            j_7_idx = jet_index_candidate[i][10]
            j_8_idx = jet_index_candidate[i][11]
            

            bjet_1 = jet_cand_properties(b_1_idx)
            bjet_2 = jet_cand_properties(b_2_idx)
            bjet_3 = jet_cand_properties(b_3_idx)
            bjet_4 = jet_cand_properties(b_4_idx)
            jet_1 = jet_cand_properties(j_1_idx)
            jet_2 = jet_cand_properties(j_2_idx)
            jet_3 = jet_cand_properties(j_3_idx)
            jet_4 = jet_cand_properties(j_4_idx)
            jet_5 = jet_cand_properties(j_5_idx)
            jet_6 = jet_cand_properties(j_6_idx)
            jet_7 = jet_cand_properties(j_7_idx)
            jet_8 = jet_cand_properties(j_8_idx)
            
            
            W_1_inv = cal_two_parton_inv(jet_1, jet_2)
            W_2_inv = cal_two_parton_inv(jet_3, jet_4)
            W_3_inv = cal_two_parton_inv(jet_5, jet_7)
            W_4_inv = cal_two_parton_inv(jet_7, jet_8)
            
            top_1_inv = cal_three_parton_inv(bjet_1, jet_1, jet_2)
            top_2_inv = cal_three_parton_inv(bjet_2, jet_3, jet_4)
            top_3_inv = cal_three_parton_inv(bjet_3, jet_5, jet_6)
            top_4_inv = cal_three_parton_inv(bjet_4, jet_7, jet_8)
            
            chi2_part_1 = (top_1_inv - m_top)**2
            chi2_part_2 = (top_2_inv - m_top)**2
            chi2_part_3 = (W_1_inv - m_W)**2
            chi2_part_4 = (W_2_inv - m_W)**2
            chi2_part_5 = (top_3_inv - m_top)**2
            chi2_part_6 = (top_4_inv - m_top)**2
            chi2_part_7 = (W_3_inv - m_W)**2
            chi2_part_8 = (W_4_inv - m_W)**2
            
            chi2_tmp =  chi2_part_1/sigma_t**2 + chi2_part_2/sigma_t**2  + chi2_part_3/sigma_W**2 + chi2_part_4/sigma_W**2 +  chi2_part_5/sigma_t**2 + chi2_part_6/sigma_t**2  + chi2_part_7/sigma_W**2 + chi2_part_8/sigma_W**2
            
            _chi2_value.append(chi2_tmp)
            _cand_record.append([[b_1_idx, j_1_idx, j_2_idx, b_2_idx, j_3_idx, j_4_idx, b_3_idx, j_5_idx, j_6_idx, b_4_idx, j_7_idx, j_8_idx]])
            if (min_chi2 < 0 or chi2_tmp < min_chi2 ):
                min_chi2 = chi2_tmp
                jet_1_best_idx = j_1_idx
                jet_2_best_idx = j_2_idx
                jet_3_best_idx = j_3_idx
                jet_4_best_idx = j_4_idx
                jet_5_best_idx = j_5_idx
                jet_6_best_idx = j_6_idx
                jet_7_best_idx = j_7_idx
                jet_8_best_idx = j_8_idx
                
                b_1_best_idx = b_1_idx
                b_2_best_idx = b_2_idx
                b_3_best_idx = b_3_idx
                b_4_best_idx = b_4_idx
                _cand_record.append([[b_1_best_idx, jet_1_best_idx, jet_2_best_idx, b_2_best_idx, jet_3_best_idx, jet_4_best_idx, b_3_best_idx, jet_5_best_idx, jet_6_best_idx, b_4_best_idx,  jet_7_best_idx, jet_8_best_idx]])
                _chi2_value.append(min_chi2)
                _parton_jet_index = np.array([b_1_best_idx, jet_1_best_idx, jet_2_best_idx, b_2_best_idx, jet_3_best_idx, jet_4_best_idx, b_3_best_idx, jet_5_best_idx, jet_6_best_idx, b_4_best_idx,  jet_7_best_idx, jet_8_best_idx])
            else: 
                pass
        _jet_parton_index = [9999999*i/i for i in range(1, len(jet_pt_chi2)+1)]
        
        chi2_value = _chi2_value[-10:]
        cand_record = _cand_record[-10:]
        del _chi2_value, _cand_record
        for k in range(len(jet_pt_chi2)):
            for l in range(len(_parton_jet_index)):
                if _parton_jet_index[l] == int(k):
                    _jet_parton_index[k] = int(l)
                else :
                    pass
        
        for k in range(len(_jet_parton_index)):
                if _jet_parton_index[k] == 9999999:
                    _jet_parton_index[k] = 'Nan'
                else : 
                    pass
        
        return min_chi2, np.asanyarray(_parton_jet_index, dtype=object), np.asanyarray(_jet_parton_index, dtype=object), np.asanyarray(cand_record, dtype=object), np.asanyarray(chi2_value, dtype=object)

def purity_classifier(prediction, truth_match, mode, model):
    if model == 'ttbar':
        if mode == "pair":
            left_truth_match = truth_match[:3]
            right_truth_match = truth_match[3:]

            left_prediction = prediction[:3]    
            right_prediction = prediction[3:]    

            b_1_truth_match = left_truth_match[0]
            b_2_truth_match = right_truth_match[0]
            j_12_truth_match = set(left_truth_match[1:])
            j_34_truth_match = set(right_truth_match[1:])
            truth_match_b_pair = [b_1_truth_match, b_2_truth_match]

            b_1_prediction = left_prediction[0]
            b_2_prediction = right_prediction[0]
            j_12_prediction = set(left_prediction[1:])
            j_34_prediction = set(right_prediction[1:])
            prediction_b_pair = [b_1_prediction, b_2_prediction]
            
            if truth_match_b_pair[0] == prediction_b_pair[0] and truth_match_b_pair[1] == prediction_b_pair[1]:
                _case = 1
            elif truth_match_b_pair[0] == prediction_b_pair[1] and truth_match_b_pair[1] == prediction_b_pair[0]:
                _case = 2
            elif truth_match_b_pair[0] == prediction_b_pair[0] and truth_match_b_pair[1] != prediction_b_pair[1]:
                _case = 3
            elif truth_match_b_pair[0] != prediction_b_pair[0] and truth_match_b_pair[1] == prediction_b_pair[1]:
                _case = 4
            elif truth_match_b_pair[0] == prediction_b_pair[1] and truth_match_b_pair[1] != prediction_b_pair[0]:
                _case = 5
            elif truth_match_b_pair[0] != prediction_b_pair[1] and truth_match_b_pair[1] == prediction_b_pair[0]:
                _case = 6
            else: 
                _case = 7
            
            if _case == 1:
                if j_12_truth_match == j_12_prediction and j_34_truth_match == j_34_prediction:
                    _correct_left = _correct_right = 1
                elif j_12_truth_match != j_12_prediction and j_34_truth_match == j_34_prediction:
                    _correct_left = 0 
                    _correct_right = 1
                elif j_12_truth_match == j_12_prediction and j_34_truth_match != j_34_prediction:
                    _correct_left = 1
                    _correct_right = 0
                elif j_12_truth_match != j_12_prediction and j_34_truth_match != j_34_prediction:
                    _correct_left = _correct_right = 0
                else:
                    print("Error occur in function.")

            elif _case == 2:
                if j_12_truth_match == j_34_prediction and j_34_truth_match == j_12_prediction:
                    _correct_left = _correct_right = 1
                elif j_12_truth_match != j_34_prediction and j_34_truth_match == j_12_prediction:
                    _correct_left = 0 
                    _correct_right = 1
                elif j_12_truth_match == j_34_prediction and j_34_truth_match != j_12_prediction:
                    _correct_left = 1
                    _correct_right = 0
                elif j_12_truth_match != j_34_prediction and j_34_truth_match != j_12_prediction:
                    _correct_left = _correct_right = 0
                else:
                    print("Error occur in function.")
            elif _case == 3:
                _correct_right = 0
                if j_12_truth_match == j_12_prediction:
                    _correct_left = 1
                else:
                    _correct_left = 0
            elif _case == 4:
                _correct_left = 0
                if j_34_truth_match == j_34_prediction:
                    _correct_right = 1
                else:
                    _correct_right = 0
            elif _case == 5:
                _correct_right = 0
                if j_12_truth_match == j_34_prediction:
                    _correct_left = 1
                else:
                    _correct_left = 0
            elif _case == 6:
                _correct_left = 0
                if j_34_truth_match == j_12_prediction:
                    _correct_right = 1
                else:
                    _correct_right = 0
            elif _case == 7:
                _correct_left  = _correct_right = 0
            else: 
                pass

            return _correct_left, _correct_right
        
        elif mode == "left":
            left_truth_match = set(truth_match[:3])
            left_prediction = set(prediction[:3])
            right_prediction = set(prediction[3:])

            if left_truth_match == left_prediction: 
                _correct_left = 1
            elif left_truth_match == right_prediction: 
                _correct_left = 1
            else: 
                _correct_left = 0
                
            return _correct_left
        elif mode == "right":
            right_truth_match = set(truth_match[3:])
            right_prediction = set(prediction[3:])
            left_prediction = set(prediction[:3])
            
            if right_truth_match == right_prediction: 
                _correct_right = 1
            elif  right_truth_match == left_prediction: 
                _correct_right = 1
            else: 
                _correct_right = 0
            return  _correct_right
        else: 
            print("Error occur in function")
    else: 
        print("Please select a available model. (Only ttbar model(fully hadronic decay) available currently.)")

