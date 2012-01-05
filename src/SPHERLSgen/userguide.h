/** @file
  contains the text for the userguide
**/

/**
  @mainpage Using and Modifying SPHERLSgen
  
  This manual is divided into two main parts the current chapter, and the rest of the chapters. All chapters other than the current, contain specific reference material for the SPHERLS code while the current chapter contains a more descriptive how-to approach explaining the usage and modification of SPHERLS. The chapters following chapter 1 will serve as a usefull reference when specific details need to be found for example, a discription of a particular variable in the code. The current chapter on the other hand is the best place to go to get a quick understanding of SPHERLS that will enable you to use it.
  
  @section overview Overview
  
  SPHERLS stands for Stellar Pulsation with a Horizontal Eulearian Radial Lagrangian Scheme. There are three components to SPHERLS, SPHERLS itself which does the hydodynamics calculations, SPHERLSgen which creates starting models, and SPHERLSanal which is able to manipulate the output files. Both SPHERLSgen and SPHERLSanal have there own manuals which can be consulted for their specific uses.
  
  @subsection basics The Basics
  SPHERLS calculates the radial pulsation motions together with the horizontal convective flow. The radial pulsation can be described by a radial grid velocity \ref Grid::nU0, moving the grid inward and outward with the pulsation. The movement of the grid is defined by the motion required to maintaining the mass in a spherical shell through out the calculation. This motion is determined by so that it will change the volume of the shell so the newly calculated density when multiplied with the new volume will produce the same shell mass. The total motion of the stellar material is simply the three velocity components radial, \ref Grid::nU, theta, \ref Grid::nV, and phi velocities, \ref Grid::nW.  The convective motion is the radial velocity minus the grid velocity, combined with the theta and phi velocities. This is because the grid velocity describes the bulk motion of the pulsation so subtracting it out leaves only the convective motions.
  
  SPHERLS solves the normal hydodynamic equations of, mass, momentum, and energy conservation. The form of the mass equation, momentum conservation, and energy conservation are:
  
  \f[
  \frac{d M}{d t} + \oint_{\mathbb{S}} \left(\rho\vec v\right)\cdot\hat{n}d\sigma=0
  \f]
  
  \f[
  \frac{\partial \vec{v}}{\partial t}+(\vec{v}\cdot\nabla)\vec{v}=-\frac{1}{\rho}\nabla P + \nabla\cdot\boldsymbol{\tau}-\nabla \phi
  \f]
  
  \f[
\frac{\partial E}{\partial t}+(\vec{v}\cdot\nabla)E+P\frac{d\mathbb{V}}{dt}=\epsilon+\frac{1}{\rho}\left[-\nabla\cdot F+\nabla\cdot\left(\boldsymbol{\tau}\cdot\vec{v}\right)-\left(\nabla\cdot\boldsymbol{\tau}\right)\cdot\vec{v}\right]
  \f]
  where \f$\boldsymbol{\tau}\f$ is the stress tensor for zero bulk viscosity, \f$E\f$ is the specific internal energy, \f$\mathbb{V}\f$ is the specific volume, and \f$F\f$ is the radiative flux. In addition to these conservation equations an equation of state is needed, in this case the OPAL equation of state and opacities, and the Alaxander opacities at low temperatures are used. The equation of state tables are functions of density and temperature, and produce the energy, pressure, opacity, and adiabatic index of the gas for a given temperature and density.

    The simulation grid is broken up into two main sections, the 1D region towards the center of the star, the multi-dimensional region towards the surface. The inner part of the multi-dimensional region solves all the conservation equations explicitly, in that the new values for the conserved quantities are directly calculated from the information in the previous time step. In the outter parts of the multi-dimensional region the energy conservation equation is calculated semi-implicitly, which means that the new values are dependent on the new values averaged with the old values to correctly time cetner the equation. This semi-implicit energy conservervation equation can be preturbed and linearized producing a set of linear equations the size of the region being solved implicitly. The solution of these linear equations provide corrections for the temperature which can be applied until the value of the new temperature converges. The equation of state is a funciton of temperature and not energy which is why the temperature is pretubed and not the energy. This set of equations is solved using the PETSC library.
    
    - Explain what SPHERLS does
      - Equations
      - Roughly how it solves them
      - The order
    - Different ways in which SPHERLS can be used, 1D,2D,3D, Adiabatic,Non-adiabatic, implicit, debugging options/test
  
  @section installation Compiling SPHERLS
    Once the correct libraries are installed, and their paths added to your \verbatim LD_LIBRARY_PATH\endverbatim environment varible, it should just require typing make in the correct directories. SPHERLS is broken up into 3 main codes. SPHERLS it self, which is the main hydrodynamics code which integrates the initial static model, SPHERLSgen which creates the static model, and SPHERLSanal which is used for processing the output of SPHERLS and SPHERLSgen.
    
    To Add
    - example .bashrc entries, showing LD_LIBRARY_PATH additions, and other SPHERLS related configuration options
    - also the make files will need to know where the paths for the libraries are, either describe how the user can do this, or automate it some how.
    
    @subsection requirements Requirements
      - openMPI
      - gcc
      - PETSc library
      - python for analysis scripts
      - fftw library for analysis
    @subsection installPETSC Installing PETSC Library
      - Download PETSc library, from the PETSc 
        <a href="http://www.mcs.anl.gov/petsc/petsc-as/download/index.html">website</a>. Version 
        petsc-lite-3.1-p8 has been tested to work with SPHERLS.
      - The downloaded PETSc file  (e.g. petsc-lite-3.1-p8-tar.gz) will need to be unziped to do so
      type <tt>gunzip petsc-lite-3.1-p8.tar.gz</tt>
      - Then untar it with <tt>tar -xf petsc-lite-3.1-p8.tar</tt>
      - To install the library change into the directory made when you extracted the archive
        and type the following commands:
        -# \verbatim ./configure --prefix=<path-to-final-location-of-library> --with-c++-support --with-c-support
 --with-shared --download-f-blas-lapack=1 \endverbatim
        -# \verbatim make all \endverbatim
        -# \verbatim make install \endverbatim
        -# \verbatim make PETSC_DIR=<path-to-final-location-of-library> test \endverbatim
    @subsection installFFTW Installing FFTW Library
      - Download the FFTW Library from the FFTS <a href="http://www.fftw.org/download.html">website</a>. Version fftw-3.2.2 has been tested to work with SPHERLS.
      - The downloaded FFTW file (e.g. fftw-3.2.2.tar.gz) will need to be unziped to do so type <tt>gunzip fftw-3.2.2.tar.gz</tt>
      - Then untar it with <tt>tar -xf fftw-3.2.2.tar.gz</tt>
      - To install the library change into the directory made when you extracted the archive
        and type the following commands:
        -# \verbatim ./configure --prefix=<path-to-final-location-of-library> \endverbatim
        -# \verbatim make \endverbatim
        -# \verbatim make install \endverbatim
    
  @section usage Using SPHERLS
    - Generating a starting model
      - Using SPHERLSgen
    - The XML configuration file
    - Starting a calculation and the "makeFile"
    - analysis of results (using premade anaylsis scripts)
      - watchzones
      - peak KE tracking
      - model dumps
  
  @section modding Modifing or Developing SPHERLS
    - Basic layout/design of the code
      - model output
      - data monitoring
        - watch zones
        - peak KE tracking
      - internal/versus external variables
      - message passing
      - grid layout
      - ranges of grids
      - boundary regions
      - grid updating
    - How to document SPHERLS
    - How to modify SPHERLS
      - Common changes
        - How to add a new internal variable
          -# <b>Add to the internal variable count:</b> Decide in what cases the variable will be needed, 1D calculations, 2D calculations, when there is a gamma law gas or a tabulated equation of state, adiabatic or non-adiabatic etc. Then once decided it can be added to the total number of internal variables \ref Grid::nNumIntVars by increasing the value by one in the function \ref modelRead in the section below the comment "set number of internal variables ..." under the appropriate if block. If the specific if block for the situation you need isn't there, you can create your own, and add it there.
          -# <b>Create a new variable ID:</b> In the \ref grid.h file under the \ref Grid class are variable ID's. These ID's simply indicate the location of the variable in the array. One must add a new ID for the new variable as an integer. The value of the ID is set in the function \ref modelRead in the same section as the number of internal variables. The value used should be the last integer after the last pre-existing variable ID. This should also be \ref Grid::nNumVars + \ref Grid::nNumIntVars -1. The ID should also be initalized to -1, so that the code knows when it isn't being used. This is done in the grid class constructor, \ref Grid::Grid. Simply add a line in the constructor setting your new ID = -1.
          -# <b>Set variable infos:</b> Decide what the dimensions of the new variable will be. It can be cell centered it can be or interface centered, it can also be only 1D, 2D, or 3D. Of course it will be only 1D if the entire calculation is 1D, or 2D if the calculation is 2D, but if the calculation is 3D it could also only be 2D, or 1D, and if 2D it could be only 1D. Also decide if the variable will change with time, dependent variables are only initialized and not updated during the calculations. This information is given to SPHERLS in the \ref setInternalVarInf function in the \ref physEquations.cpp file. The variable that is set is \ref Grid::nVariables. It is a 2D array, the first index corresponds to the particular variable in question, the ID you made in the previous step can be used as the first index of this array. The second index referes to the three directions (0-2) and the time (3). If the variable is cenertered in the grid in direction 0 (r-direction) then this array element should have a value of 0. If the variable is interface centered in the grid in direction 0, then this array element should have a value of 1. If it isn't defined in direciton 0, for example the theta independent variable isn't defined in the 0 direction then it should be -1. This is the same for the other 2 directions. The last element (3) should be either 0 not updated every time step, or 1 if updated every timestep.
          -# <b>Add functions:</b> Finally to do anything usefull with your new internal variable functions must be added to initialize the values of the variables, and to update them with time if needed. Initiliazation functions are called within the \ref initInternalVars function in the \ref physEquations.cpp file. The details of these functions will depend on what the individual variables are intended for. Functions to be called every timestep must be called from the main program loop in the file \ref main.cpp in the appropriate order.
        - How to add a new external variable
        - How to add a new physics functions
          - Function naming conventions
          - Grid variables
          - indecies and their ranges
    - SPHERLS debugging tips
  
  @section messpass Message Passing
    - Explain message passing in SPHERLS
   
*/