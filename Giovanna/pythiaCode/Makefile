# Makefile for displaced searches for ANTLIA
PYTHIA8=/home/gfcottin/HEPSoftware/pythia8311
FASTJET3=/home/gfcottin/HEPSoftware/fastjet-install
PYTHIALIB=$(PYTHIA8)/lib
PYTHIAINC=$(PYTHIA8)/include/
FJINC=$(FASTJET3)/include
FJLIB=$(FASTJET3)/lib
OBJECTS=HNL_kinematics.o

INCLUDE=-I$(PYTHIAINC) -I./ -I$(FJINC)

#Need to do in MAC
# export DYLD_LIBRARY_PATH=/PATH/TO/pythia8308/lib:...../PATH/TO/fastjet-3.4.0-install/lib

HNL_kinematics: $(OBJECTS)
	$(CXX) -o HNL_kinematics $(OBJECTS) -L$(PYTHIALIB) -lpythia8 \
	-L$(FJLIB) -lfastjet -lz -Wl,-rpath $(PYTHIALIB) -Wl,-rpath $(FJLIB)

%.o: %.cc
	$(CXX) -c $^ $(INCLUDE) -std=c++11 
#Need to do in MAC
# export DYLD_LIBRARY_PATH=/Users/chubicottin/Desktop/Phenomenology/pythia8303/lib:/Users/chubicottin/Desktop/Phenomenology/fastjet-install/lib:Users/chubicottin/Desktop/Phenomenology/lhapdf-install/lib
# export LIBRARY_PATH=/Users/chubicottin/Desktop/Phenomenology/pythia8303/lib
# in laptop (NOW in PATH .bash_profile)
# export DYLD_LIBRARY_PATH=/Users/chubicottin/Desktop/PhenoSoftware/pythia8309/lib:/Users/chubicottin/Desktop/PhenoSoftware/fastjet-install/lib
# export LIBRARY_PATH=/Users/chubicottin/Desktop/PhenoSoftware/pythia8309/lib

#in cluster AONIKENK
# export DYLD_LIBRARY_PATH=/home/gfcottin/HEPSoftware/pythia8311/lib:/home/gfcottin/HEPSoftware/fastjet-install/lib
# export LIBRARY_PATH=/home/gfcottin/HEPSoftware/pythia8311/lib

#in cluster ANTLIA
#https://stackoverflow.com/questions/480764/linux-error-while-loading-shared-libraries-cannot-open-shared-object-file-no-s
#LD_LIBRARY_PATH=/home/gfcottin/HEPSoftware/pythia8311/lib:/home/gfcottin/HEPSoftware/fastjet-install/lib
#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/gfcottin/HEPSoftware/pythia8311/lib:/home/gfcottin/HEPSoftware/fastjet-install/lib
