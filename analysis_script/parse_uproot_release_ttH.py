"""
Author: David Ho
Institute: National Tsing Hua university, Department of Physics, Hsinchu, Taiwan 
Mail: davidho@gapp.nthu.edu.tw
"""

import uproot
import pandas as pd 
import numpy as np 
from particle_properties_uproot import particle_properties  #import particle properties helper function from particle_properties.py
from jet_properties_uproot import jet_properties  #import jet properties helper function from jet_properties.py
import h5py, tqdm, sys

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

try:
    data  = uproot.open(INPUT_FILE)['Delphes']
except:
    print('Please check input file path.')

particle = particle_properties(data)
jet = jet_properties(data)

Length = len(particle.event)
test_length = 10

PID_W_plus = 24 
PID_W_minus = -24
PID_DOWN = 1
PID_DOWN_VAR = -1
PID_UP = 2
PID_UP_BAR = -2
PID_STRANGE = 3
PID_STRANGE_BAR = -3
PID_CHARM = 4
PID_CHARM_BAR = -4
PID_BOTTOM = 5
PID_BOTTOM_BAR = -5
PID_TOP = 6
PID_TOP_BAR = -6
PID_HIGGS = 25

top_idx = np.zeros(len(particle.event))
top_daughter_idx_1 = np.zeros(len(particle.event))
top_daughter_pid_1 = np.zeros(len(particle.event))
top_daughter_idx_2 = np.zeros(len(particle.event))
top_daughter_pid_2 = np.zeros(len(particle.event))

top_bar_idx = np.zeros(len(particle.event))
top_bar_daughter_idx_1 = np.zeros(len(particle.event))
top_bar_daughter_pid_1 = np.zeros(len(particle.event))
top_bar_daughter_idx_2 = np.zeros(len(particle.event))
top_bar_daughter_pid_2 = np.zeros(len(particle.event))

higgs_idx = np.zeros(len(particle.event))
higgs_daughter_idx_1 = np.zeros(len(particle.event))
higgs_daughter_pid_1 = np.zeros(len(particle.event))
higgs_daughter_idx_2 = np.zeros(len(particle.event))
higgs_daughter_pid_2 = np.zeros(len(particle.event))

parton_array = np.zeros([ len(particle.event) , 8, 7])

#Generate maker for each stage(event selection and jet selection.)
marker_event = []
marker_jet = []
marker_bjet = []

for i in range(len(particle.event)):
    marker_event.append(0)
    marker_jet.append(np.zeros([len(jet.pt[i])]))
    marker_bjet.append(np.zeros([len(jet.pt[i])]))


marker_event = np.asanyarray(marker_event, dtype=object)
marker_jet = np.asanyarray(marker_jet, dtype=object)
marker_bjet = np.asanyarray(marker_bjet, dtype=object)

#Mark which jet in each event pass the selection.
print("+------------------------------------------------------------------------------------------------------+")
print("Start jet selection.")
print("+------------------------------------------------------------------------------------------------------+")
for i in tqdm.trange(len(particle.event)):
    for j in range(len(jet.pt[i])):
        if jet.btag[i][j] == 1 and jet.pt[i][j] > 25 and np.abs(jet.eta[i][j]) < 2.5:
            marker_bjet[i][j] = 1 
        else: pass 
    
        if jet.pt[i][j] > 25 and np.abs(jet.eta[i][j]) <= 2.5:
            marker_jet[i][j] = 1
        else: pass 

for i in tqdm.trange(len(particle.event)):
    if np.sum(marker_jet[i] == 1) >= 8 and np.sum(marker_bjet[i] == 1) >= 2 :
        marker_event[i] = 1 
print("+------------------------------------------------------------------------------------------------------+")
print("Jet selection doen. {0} events has been selected.".format(np.sum(marker_event == 1)))
print("+------------------------------------------------------------------------------------------------------+")

print("+------------------------------------------------------------------------------------------------------+")
print("Recording the kinematics variables of jets in the selected event.")
print("+------------------------------------------------------------------------------------------------------+")
#Record the kinematical variables of jet in the selected event.
jet_pt = []
jet_eta = []
jet_phi = []
jet_mass = []
jet_btag = []

for i in tqdm.trange(len(jet.event)):
    if marker_event[i] == 1:
        jet_pt_tmp = []
        jet_eta_tmp = []
        jet_phi_tmp = []
        jet_mass_tmp = []
        jet_btag_tmp = []
        for j in range(len(jet.pt[i])):
            jet_pt_tmp.append(jet.pt[i][j])
            jet_eta_tmp.append(jet.eta[i][j])
            jet_phi_tmp.append(jet.phi[i][j])
            jet_mass_tmp.append(jet.mass[i][j])
            jet_btag_tmp.append(jet.btag[i][j])

        jet_pt.append(jet_pt_tmp)
        jet_eta.append(jet_eta_tmp)
        jet_phi.append(jet_phi_tmp)
        jet_mass.append(jet_mass_tmp)
        jet_btag.append(jet_btag_tmp)
print("+------------------------------------------------------------------------------------------------------+")
print("Finished to record the kinematics variables of jets in the selected event.")
print("+------------------------------------------------------------------------------------------------------+")

print("+------------------------------------------------------------------------------------------------------+")
print("Starting parton tracing and looking for its daughter.")
print("+------------------------------------------------------------------------------------------------------+")
#Particle tracing and daughter finding section
def shift_particle_tracing(dataset, PID_d, idx):
    if (dataset.iloc[idx,6] == PID_d):
        return dataset.iloc[idx,4]

def particle_tracing(dataset, PID, STATUS):

    for i in range(len(dataset)):
        if(dataset.iloc[i,1] == STATUS and dataset.iloc[i,6] == PID ): 
            daughter_index = int(dataset.iloc[i,0])
    if( dataset.iloc[daughter_index,6] == PID ):
        shifted_particle_index = dataset.iloc[daughter_index, 4]


    while dataset.iloc[shifted_particle_index,6] == PID:
        init_shifted_particle_index = shifted_particle_index
        shifted_particle_index = shift_particle_tracing(dataset, PID, init_shifted_particle_index)       

    dauthter_idx_1 = dataset.iloc[init_shifted_particle_index, 4]
    daughter_pid_1 = dataset.iloc[dauthter_idx_1, 6]

    dauthter_idx_2 = dataset.iloc[init_shifted_particle_index, 5]
    daughter_pid_2 = dataset.iloc[dauthter_idx_2, 6]

    return init_shifted_particle_index, dauthter_idx_1, daughter_pid_1, dauthter_idx_2, daughter_pid_2

for i in tqdm.trange(len(particle.event)):
# for i in range(0,5):
    if marker_event[i] == 1:
        print("+------------------------------------------------------------------------------------------------------+")
        print("Start parsing event : {0}\nStart to trace top quark and find its daughters.".format(i))
        top_idx[i], top_daughter_idx_1[i], top_daughter_pid_1[i], top_daughter_idx_2[i], top_daughter_pid_2[i] = particle_tracing(particle.dataframelize(i), PID_TOP, 22)
        print("+------------------------------------------------------~-----------------------------------------------+")
        print("Start to find top_bar quark and its daughters.")
        top_bar_idx[i], top_bar_daughter_idx_1[i], top_bar_daughter_pid_1[i], top_bar_daughter_idx_2[i], top_bar_daughter_pid_2[i] = particle_tracing(particle.dataframelize(i), PID_TOP_BAR, 22)
        print("+------------------------------------------------------------------------------------------------------+")
        print("Start to find higgs boson and its daughters.")
        higgs_idx[i], higgs_daughter_idx_1[i], higgs_daughter_pid_1[i], higgs_daughter_idx_2[i], higgs_daughter_pid_2[i] = particle_tracing(particle.dataframelize(i), PID_HIGGS, 22)

#tracing the daughters
#Input two daughter of top/top_bar and find their daughter
def top_daughter_finder(dataset, mother_idx_1, mother_idx_2):
    
    #Specific two daughter of top
    def W_b_specifier(dataset, input_1_idx, input_2_idx):
        if dataset.iloc[int(input_1_idx),6] == PID_W_plus or dataset.iloc[int(input_1_idx),6] == PID_W_minus :
            return int(input_1_idx), int(dataset.iloc[int(input_1_idx),6]), int(input_2_idx)
        elif dataset.iloc[int(input_1_idx),6] == PID_BOTTOM or dataset.iloc[int(input_1_idx),6] == PID_BOTTOM_BAR :
            return  int(input_2_idx), int(dataset.iloc[int(input_1_idx),6]), int(input_1_idx)
        else :
            pass
    
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
    
    #print("Found daughter 1 index: {0}, PID: {1}.\nFound daughter 2 index: {2}, PID: {3}".format(daughter_1_idx, daughter_1_pid, daughter_2_idx, daughter_2_pid))
    return  b_quark_idx, daughter_1_idx, daughter_2_idx

for i in tqdm.trange(len(particle.event)):
    if marker_event[i] == 1 :
        print("+------------------------------------------------------------------------------------------------------+")
        print("Start parsing event : {0}\nStart to find top quark's daughters.".format(i))
        parton_array[i][0][0], parton_array[i][1][0], parton_array[i][2][0] = top_daughter_finder(particle.dataframelize(i), top_daughter_idx_1[i], top_daughter_idx_2[i])
        print("+------------------------------------------------------~-----------------------------------------------+")
        print("Start to find top_bar quark's daughters.")
        parton_array[i][3][0], parton_array[i][4][0], parton_array[i][5][0], = top_daughter_finder(particle.dataframelize(i), top_bar_daughter_idx_1[i], top_bar_daughter_idx_2[i])
        print("+------------------------------------------------------------------------------------------------------+")
        parton_array[i][6][0], parton_array[i][7][0] = higgs_daughter_idx_1[i], higgs_daughter_idx_2[i]
    elif marker_event[i] == 0 :
        parton_array[i] = 'Nan'
    else: pass
print("+------------------------------------------------------------------------------------------------------+")
print("Parton tracing section complete. The daughter of W+/W- and bbbar has been found.")
print("+------------------------------------------------------------------------------------------------------+")


# Barcode system
# t t~ W+ W- b b~ H
# 0 0  0  0  0 0  0

# i.e.
# daughter of t and b = 1000100
# daughter of t and W+ = 1010000
# daughter of t~ and W- = 0101000
# daughter of t~ and b~ = 0100010
# daughter of H = 0000001

print("+------------------------------------------------------------------------------------------------------+")
print("Recording the kinematics variables of partons in the selected event.")
print("+------------------------------------------------------------------------------------------------------+")
parton_pdgid = []
parton_barcode = []
parton_pt = []
parton_eta = []
parton_phi = []
parton_mass = []

barcode = np.array([68, 80, 80, 34, 40, 40, 1, 1])
for i in tqdm.trange(len(particle.event)):
    if marker_event[i] == 1:
        _parton_pdgid = []
        _parton_barcode = []
        _parton_pt = []
        _parton_eta = []
        _parton_phi = []
        _parton_mass = []
        for j in range(0,8):
            dataset = particle.dataframelize(i)

            _parton_pdgid.append(dataset.iloc[int(parton_array[i][j][0]), 6])
            _parton_barcode.append(barcode[j])
            _parton_pt.append(dataset.iloc[int(parton_array[i][j][0]), 7])
            _parton_eta.append(dataset.iloc[int(parton_array[i][j][0]), 8])
            _parton_phi.append(dataset.iloc[int(parton_array[i][j][0]), 9])
            _parton_mass.append(dataset.iloc[int(parton_array[i][j][0]), 10])


        parton_pdgid.append(_parton_pdgid)
        parton_barcode.append(_parton_barcode)
        parton_pt.append(_parton_pt)
        parton_eta.append(_parton_eta)
        parton_phi.append(_parton_phi)
        parton_mass.append(_parton_mass)
print("+------------------------------------------------------------------------------------------------------+")
print("Finished to record the kinematics variables of partons in the selected event.")
print("+------------------------------------------------------------------------------------------------------+")

print("+------------------------------------------------------------------------------------------------------+")
print("Computing delta_R between each jets and partons.")
print("+------------------------------------------------------------------------------------------------------+")
#Parton-jet matching section
def deltaPhi(phi1,phi2):
    phi = phi1-phi2
    while phi >= np.pi: phi -= np.pi*2.
    while phi < -np.pi: phi += np.pi*2.
    return phi

def delta_R(eta1, phi1, eta2, phi2):
    return np.sqrt(deltaPhi(phi1,phi2)**2+(eta1-eta2)**2)

dR_between_parton_jet = []
dR_between_parton_parton = []

for i in range(len(parton_pdgid)):
    dR_between_parton_jet.append(np.zeros([len(jet_pt[i]) * 8])) # # of connection = num of jet * num of parton
    dR_between_parton_parton.append(np.zeros([28])) # C^{8}_{2} = 28

dR_between_parton_jet = np.asanyarray(dR_between_parton_jet, dtype=object)
dR_between_parton_parton = np.asanyarray(dR_between_parton_parton, dtype=object)

max_num_of_jet_cand = []

for i in range(len(parton_pdgid)):
    max_num_of_jet_cand.append(len(jet_pt[i]))
max_num_of_jet_cand = np.asanyarray(max_num_of_jet_cand)
max_num_of_jet = max_num_of_jet_cand.max()
#print(max_num_of_jet)

matching_jet = []
matching_parton = []
for i in range(len(parton_pdgid)):
    matching_jet.append(np.zeros([len(jet_pt[i])]))
    matching_parton.append(np.zeros([8]))

matching_jet = np.array(matching_jet, dtype=object)
matching_parton = np.array(matching_parton, dtype=object)

#Computing delta_R between each parton and jet
for i in tqdm.trange(len(parton_pdgid)):
    j = 0
    a = 0
    b = 0
    while a < 8 :
        for b in range( len(jet_pt[i]) ):
            # print(i, j, a, b)
            #print(i, a, b)
            #print(delta_R( parton_array[i][a][4], parton_array[i][a][5], jet.eta[i][b], jet.phi[i][b]))
            dR_between_parton_jet[i][j] = delta_R( parton_eta[i][a], parton_phi[i][a], jet_eta[i][b], jet_phi[i][b])
            j +=1
        a += 1
print("+------------------------------------------------------------------------------------------------------+")
print("Finished to compute delta_R between each jets and partons.")
print("+------------------------------------------------------------------------------------------------------+")


#Matching jet and parton by finding the Min(dR(parton, jet))
print("+------------------------------------------------------------------------------------------------------+")
print("Starting parton-jet matching.")
print("+------------------------------------------------------------------------------------------------------+")
for i in tqdm.trange(len(parton_pt)):

    # print("+------------------------------------------------------------------------------------------------------+")
    # print(i)
    #print(dR_between_parton_jet.shape)
    array = np.reshape(dR_between_parton_jet[i], [8, len(jet_pt[i])])
    #print(array.shape)

    dataset = pd.DataFrame({'0': array[0,:],
                                '1': array[1,:],
                                '2': array[2,:],
                                '3': array[3,:],
                                '4': array[4,:],
                                '5': array[5,:],
                                '6': array[6,:],
                                '7': array[7,:],
                                })
    #print(dataset)

    for j in range(0,8):
        #print("+------------------------------------------------------------------------------------------------------+")
        min_val = dataset.stack().min()
        if min_val < 0.4:
            #print("Min val: {0}".format(min_val))
            min_idx, min_col = dataset.stack().idxmin()
            matching_parton[i][j] = int(min_idx)
            matching_jet[i][j] = int(min_col)
            #print("The position of minimun appears. Raw: {0}, Colume: {1}".format(min_idx, min_col))
            dataset = dataset.drop([min_col], axis=1)
            dataset = dataset.drop([min_idx], axis=0)
            # print("The dataset after delete the minimun's raw and colume:")
            # print(dataset)
        else:
            matching_parton[i][j] = 'Nan'
            matching_jet[i][j] = 'Nan'
    for k in range(8, len(jet_pt[i])):
        matching_jet[i][k] = 'Nan'
#Matching jet and parton by finding the Min(dR(parton, jet))
print("+------------------------------------------------------------------------------------------------------+")
print("Parton-jet matching complete.")
print("+------------------------------------------------------------------------------------------------------+")

parton_jet_index = np.zeros([len(parton_pdgid), 8])
jet_parton_index = []

print("+------------------------------------------------------------------------------------------------------+")
print("Rearranging pair information to consist sequence.")
print("+------------------------------------------------------------------------------------------------------+")

for i in range(len(parton_pdgid)):
    tmp = np.zeros([len(jet_pt[i])])
    tmp[:] = 9999999
    jet_parton_index.append(tmp)

jet_parton_index = np.array(jet_parton_index, dtype=object)

for i in range(len(parton_jet_index)):
    for j in range(len(parton_jet_index[i])):
        parton_jet_index[i][j] = 'nan'

for i in tqdm.trange(len(parton_pdgid)):
    for j in range(len(jet_pt[i])):
        if matching_jet[i][j] == 0 :
            parton_jet_index[i][0] = matching_parton[i][j]
        else:
            pass

        if matching_jet[i][j] == 1 :
            parton_jet_index[i][1] = matching_parton[i][j]
        else:
            pass
        if matching_jet[i][j] == 2 :
            parton_jet_index[i][2] = matching_parton[i][j]
        else:
            pass

        if matching_jet[i][j] == 3 :
            parton_jet_index[i][3] = matching_parton[i][j]
        else:
            pass

        if matching_jet[i][j] == 4 :
            parton_jet_index[i][4] = matching_parton[i][j]
        else:
            pass

        if matching_jet[i][j] == 5 :
            parton_jet_index[i][5] = matching_parton[i][j]
        else:
            pass

        if matching_jet[i][j] == 6 :
            parton_jet_index[i][6] = matching_parton[i][j]
        else:
            pass

        if matching_jet[i][j] == 7 :
            parton_jet_index[i][7] = matching_parton[i][j]
        else:
            pass

    ll = len(jet_pt[i])
    for k in range(0,8):
        for m in range(ll):
            if matching_parton[i][k] == int(m):
                jet_parton_index[i][int(m)] = matching_jet[i][k]
            else: pass

    for l in range(len(jet_pt[i])):
        if jet_parton_index[i][l] > 7:
            jet_parton_index[i][l] = 'Nan'
print("+------------------------------------------------------------------------------------------------------+")
print("Rearranging finished")
print("+------------------------------------------------------------------------------------------------------+")

print("+------------------------------------------------------------------------------------------------------+")
print("Recording barcode information.")
print("+------------------------------------------------------------------------------------------------------+")

jet_barcode = []
for i in range(len(parton_pdgid)):
    jet_barcode.append(np.zeros([len(jet_pt[i])]))

jet_barcode = np.array(jet_barcode)

for i in range(len(parton_pdgid)):
    for j in range(len(jet_parton_index[i])):
        if jet_parton_index[i][j] == 0:
            jet_barcode[i][j] = barcode[0]
        elif jet_parton_index[i][j] == 1:
            jet_barcode[i][j] = barcode[1]
        elif jet_parton_index[i][j] == 2:
            jet_barcode[i][j] = barcode[2]
        elif jet_parton_index[i][j] == 3:
            jet_barcode[i][j] = barcode[3]
        elif jet_parton_index[i][j] == 4:
            jet_barcode[i][j] = barcode[4]
        elif jet_parton_index[i][j] == 5:
            jet_barcode[i][j] = barcode[5]
        elif jet_parton_index[i][j] == 6:
            jet_barcode[i][j] = barcode[6]
        elif jet_parton_index[i][j] == 7:
            jet_barcode[i][j] = barcode[7]
        else :
            jet_barcode[i][j] = 'Nan'

print("+------------------------------------------------------------------------------------------------------+")
print("Barcode information has beed record.")
print("+------------------------------------------------------------------------------------------------------+")


N_match_top_in_event = np.zeros([len(jet_pt)])

for i in range(len(jet_parton_index)):
    if 0 in jet_parton_index[i]:
        if 1 in jet_parton_index[i]:
            if 2 in jet_parton_index[i]:
                N_match_top_in_event[i] += 1
    if 3 in jet_parton_index[i]:
        if 4 in jet_parton_index[i]:
            if 5 in jet_parton_index[i]:
                N_match_top_in_event[i] += 1
    # print(N_match_top_in_event[i])

N_match_higgs_in_event = np.zeros([len(jet_pt)])
# print("+------------------------------------------------------------------------------------------------------+")

for i in range(len(jet_parton_index)):
    if 7 in jet_parton_index[i]:
        if 6 in jet_parton_index[i]:
            N_match_higgs_in_event[i] = 1
    # print(N_match_higgs_in_event[i])
print("+------------------------------------------------------------------------------------------------------+")
print("Jet-parton matching section complete.\nFound {0} events with 1 ttbat candidate exist.\nFound {1} events with 2 ttbar candidate exist.".format( np.sum(N_match_top_in_event == 1), np.sum(N_match_top_in_event == 2)  ))
print("+------------------------------------------------------------------------------------------------------+")


#Save selected events

lene = len(parton_pdgid)

print("+------------------------------------------------------------------------------------------------------+")
print("Writing event record to the hdf5 file.")
print("+------------------------------------------------------------------------------------------------------+")

# #Save the event which pass the selection

with h5py.File(OUTPUT_FILE,'w') as f:
    dt = h5py.vlen_dtype(np.dtype('float16'))

    hdf5_jet_parton_index = f.create_dataset('jet_parton_index', (lene, ), dtype=dt)
    hdf5_jet_barcode = f.create_dataset('jet_barcode', (lene, ), dtype=dt)
    hdf5_jet_pt = f.create_dataset('jet_pt', (lene, ), dtype=dt)
    hdf5_jet_eta = f.create_dataset('jet_eta', (lene, ), dtype=dt)
    hdf5_jet_phi = f.create_dataset('jet_phi', (lene, ), dtype=dt)
    hdf5_jet_mass = f.create_dataset('jet_mass', (lene, ), dtype=dt)
    hdf5_jet_btag = f.create_dataset('jet_btag', (lene, ), dtype=dt)

    for i in range(lene):
        hdf5_jet_parton_index[i] = jet_parton_index[i]
        hdf5_jet_barcode[i] = jet_barcode[i]
        hdf5_jet_pt[i] = jet_pt[i]
        hdf5_jet_eta[i] = jet_eta[i]
        hdf5_jet_phi[i] = jet_phi[i]
        hdf5_jet_mass[i] = jet_mass[i]
        hdf5_jet_btag[i] = jet_btag[i]

    hdf5_parton_jet_index = f.create_dataset('parton_jet_index', (lene, ), dtype=dt)
    hdf5_parton_pdgid = f.create_dataset('parton_pdgid', (lene, ), dtype=dt)
    hdf5_parton_barcode = f.create_dataset('parton_barcode', (lene, ), dtype=dt)
    hdf5_parton_pt = f.create_dataset('parton_pt', (lene, ), dtype=dt)
    hdf5_parton_eta = f.create_dataset('parton_eta', (lene, ), dtype=dt)
    hdf5_parton_phi = f.create_dataset('parton_phi', (lene, ), dtype=dt)
    hdf5_parton_mass = f.create_dataset('parton_mass', (lene, ), dtype=dt)
    hdf5_N_match_top_in_event = f.create_dataset('N_match_top_in_event', data = N_match_top_in_event)
    N_match_higgs_in_event = f.create_dataset('N_match_higgs_in_event', data = N_match_higgs_in_event)

    for i in range(lene):
        hdf5_parton_jet_index[i] = parton_jet_index[i]
        hdf5_parton_pdgid[i] = parton_pdgid[i]
        hdf5_parton_barcode[i] = parton_barcode[i]
        hdf5_parton_pt[i] = parton_pt[i]
        hdf5_parton_eta[i] = parton_eta[i]
        hdf5_parton_phi[i] = parton_phi[i]
        hdf5_parton_mass[i] = parton_mass[i]

print("+------------------------------------------------------------------------------------------------------+")
print("Event record has been send to {0}.".format(OUTPUT_FILE))
print("+------------------------------------------------------------------------------------------------------+")