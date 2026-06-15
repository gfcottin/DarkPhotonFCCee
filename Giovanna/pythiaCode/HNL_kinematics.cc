//////////////////////////////////////////////////////////////
// Some kinematics for HNL events 
// Inputs needed for decay probability formulas
// Written by Giovanna Cottin (gfcottin@gmail.com)////////////
//////////////////////////////////////////////////////////////

#include "Pythia8/Pythia.h"

#include <vector>
#include <string>
#include <iterator>
#include <algorithm>

using namespace Pythia8;


int main(int argc, char *argv[]) {

  string a = argv[1];
  string b = argv[2];
  // string c = argv[3];

  // You can always read an plain LHE file,
  // but if you ran "./configure --with-gzip" before "make"
  // then you can also read a gzipped LHE file.
  #ifdef GZIPSUPPORT
  bool useGzip = true;
  #else
  bool useGzip = false;
  #endif
  cout << " useGzip = " << useGzip << endl;

  Pythia pythia;
  Event& event = pythia.event;
  // Initialize Les Houches Event File run. List initialization information.
  pythia.readString("Beams:frameType = 4");
  /////////////////////////////////////////////////////////////////////////////////////
 // ADAPT TO FILE 
 //  pythia.readString("Beams:LHEF =/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp30_isr2/MG5_GRID_U1BL_mu-"+a+"-"+b+"/Events/run_01_decayed_1/unweighted_events.lhe.gz");
 // pythia.readString("Beams:LHEF =/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp50_isr2/MG5_GRID_U1BL_mu-"+a+"-"+b+"/Events/run_01_decayed_1/unweighted_events.lhe.gz");
//  pythia.readString("Beams:LHEF =/data1/hep-shared/HNLsFCCee/UBL/lhe/mZp70_isr2/MG5_GRID_U1BL_mu-"+a+"-"+b+"/Events/run_01_decayed_1/unweighted_events.lhe.gz");
  pythia.readString("Beams:LHEF =/data1/hep-shared/HNLsFCCee/UBL/lhe/coupled_isr2/MG5_GRID_U1BL_mu-"+a+"-"+b+"/Events/run_01_decayed_1/unweighted_events.lhe.gz");

  // int nEvent   = pythia.mode("Main:numberOfEvents");
  // int nAbort   = pythia.mode("Main:timesAllowErrors"); 
  int nEvent = 10000;//FROM LHE File
  int nAbort = 50;   

  ////// Initialize.
  pythia.init();


  ofstream decayKinematics;
 // decayKinematics.open("/data1/hep-shared/HNLsFCCee/UBL/pythiaOutput/mZp30_isr2/decayKinematics_GRID-"+a+"-"+b+".dat"); 
 // decayKinematics.open("/data1/hep-shared/HNLsFCCee/UBL/pythiaOutput/mZp50_isr2/decayKinematics_GRID-"+a+"-"+b+".dat"); 
 //decayKinematics.open("/data1/hep-shared/HNLsFCCee/UBL/pythiaOutput/mZp70_isr2/decayKinematics_GRID-"+a+"-"+b+".dat"); 
 decayKinematics.open("/data1/hep-shared/HNLsFCCee/UBL/pythiaOutput/coupled_isr2/decayKinematics_GRID-"+a+"-"+b+".dat"); 

  //////////////////////////////////
  // width = 3.*1e11*6.581e-25/ctau
  // width in GeV, ctau in mm
  //////////////////////////////////
  int iAbort = 0;

  // Begin event loop; generate until none left in input file.
  for (int iEvent = 0; ; ++iEvent) {
    // Generate events, and check whether generation failed.
    if (!pythia.next()) {
      // If failure because reached end of file then exit event loop.
      if (pythia.info.atEndOfFile()) break;
      // First few failures write off as "acceptable" errors, then quit.
      if (++iAbort < nAbort) continue;
      break;
    }

    /////////////////////////////////////
    //Get displaced neutrinos from events
    /////////////////////////////////////  
    std::vector<int> motherIndices;   
    for (int i= 0; i < event.size(); i++){
      if (abs(event[i].id()) == 9910014){ // SELECT DISPLACED HNL
	    double trux = event[i].xDec() - event[i].xProd();
	    double truy = event[i].yDec() - event[i].yProd();
	    double truz = event[i].zDec() - event[i].zProd();    
	    double vProd = sqrt(pow2(event[i].xProd())+pow2(event[i].yProd())+pow2(event[i].zProd()));     
      	double HNLdecayLength = sqrt(pow2(trux) + pow2(truy) + pow2(truz));
      	double HNLp = sqrt(pow2(event[i].px())+pow2(event[i].py())+pow2(event[i].pz()));
      	double HNLe = event[i].e();
      	double HNLmass = event[i].m(); // should de same as "a" input from LHE files
        double HNLeta = fabs(event[i].eta());
        double HNLphi = event[i].phi();
        double HNLtheta = event[i].theta();
      	double HNLgamma = HNLe/HNLmass;
        double HNLbeta = sqrt(1.0-pow2(HNLmass/HNLe));
        double HNLbeta_z = fabs(event[i].pz()/HNLe);
      	// Pythia stores energy units in GeV, with c=1. For tau0, is in units of mm 
      	double dist = event[i].vDec().pAbs();//is equal to decayLenght

        decayKinematics<<HNLmass<<" "<<a<<" "<<b<<" "<<HNLdecayLength<<" "<<HNLgamma<<" "<<HNLbeta_z<<" "<<HNLe<<" "<<HNLp<<" "<<HNLbeta<<" "<<HNLeta<<" "<<HNLtheta<<" "<<HNLphi<<endl;
      }    
    }
  }//End of event loop.
  /////////////////////////////////////////////////////////////////////////

  decayKinematics.close();
  return 0;
}

