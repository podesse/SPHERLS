#ifndef MAIN_H
#define MAIN_H

/** @file
  
  Header file for \ref main.cpp.
  
*/

//#include "fftw++.h"
#include <fftw3.h>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <exception>
#include <sys/stat.h>
#include <cmath>
#include "exception2.h"
#include <csignal>
#include <fenv.h>
#include <limits>
#include <vector>

int nM;/**<
  Index of \f$M_r\f$ in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nTheta;/**<
  Index of \f$\theta\f$ in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nPhi;/**<
  Index of \f$\phi\f$ in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nDM;/**<
  Index of \f$\delta M\f$ in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nR;/**<
  Index of \f$R\f$, radius, in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nD;/**<
  Index of \f$\rho\f$, density, in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nU;/**<
  Index of \f$u\f$,radial velocity, in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nU0;/**<
  Index of \f$u_0\f$, radial grid velocity, in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nV;/**<
  Index of \f$v\f$, theta velocity in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nW;/**<
  Index of \f$w\f$, phi velocity, in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nE;/**<
  Index of \f$E\f$, internal energy, in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nT;/**<
  Index of \f$T\f$, temperature, in grids,
  This should be the same as that used in SPHERLS defined in global.h
  */
int nP;/**<
  Index of \f$P\f$, pressure
  */
int nQ;/**<
  Index of the artificial viscosity in grids. 
  */
int nKappa;/**<
  Index of the opacity in grids. 
  */
int nGamma;/**<
  Index of the adiabatic gamma. 
  */
int nL;/**<
  Index of the Luminosity.
  */
int nKE;/**<
  Index of the Kinetic energy.
  */

//variables
int  nPrecisionAscii=16;/**<
  Set presicsion of ascii output
  */
bool bScientific=true;/**<
  Output ascii files in scientific format
  */
const double dPi=3.1415926535897932384626433832795;/**<
  Pi
  */
const double dSigma=5.67040040E-5;/**<
  Boltzman constant
  */
const double dLSun=3.839e33;/**<
  Luminosity of the sun in erg/s
  */
const int nDumpFileVersion=1;/**<
  Version of the dump file supported
  */
  
//functions
void convertDistBinToAscii(std::string sFileNameBase);
void combineBinFiles(std::string sFileNameBase);
void convertCollBinToAscii(std::string sFileName);
void convertCollAsciiToBin(std::string sFileName);
void makeRadialProFromColBin(std::string sFileName);
void printHelp();
bool bFileExists(std::string strFilename);
void fpSignalHandler(int nSig);
void make2DSlice(std::string sFileName,int nPlane,int nPlaneIndex);
void computeFourierTrans(std::string sInFileName,std::string sOutFileName);
void convertBinToLNA(std::string sFileName);
void computeFourierTransFromList(std::string sInFileName,std::string sOutFileName);
struct watchzone{
  std::vector<double> vecdT;//2
  std::vector<double> vecdU_ip1half;//3
  std::vector<double> vecdU_im1half;//4
  std::vector<double> vecdU0_ip1half;//5
  std::vector<double> vecdU0_im1half;//6
  std::vector<double> vecdQ0;//7
  std::vector<double> vecdV_jp1half;//8
  std::vector<double> vecdV_jm1half;//9
  std::vector<double> vecdQ1;//10
  std::vector<double> vecdW_kp1half;//11
  std::vector<double> vecdW_km1half;//12
  std::vector<double> vecdQ2;//13
  std::vector<double> vecdR_ip1half;//14
  std::vector<double> vecdR_im1half;//15
  std::vector<double> vecdDensity;//16
  std::vector<double> vecdDensityAve;//17
  std::vector<double> vecdE;//18
  std::vector<double> vecdP;//19
  std::vector<double> vecdTemp;//20
  std::vector<double> vecdDelM_r_t0;//21
  std::vector<double> vecdDelM_r;//22
  std::vector<double> vecdErrorDelM_r;//23
};
#endif
