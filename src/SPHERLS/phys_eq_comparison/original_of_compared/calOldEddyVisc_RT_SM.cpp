void calOldEddyVisc_RT_SM(Grid &grid, Parameters &parameters){
  
  int nIInt;//i+1/2 index
  int nJInt;//j+1/2 index
  double d1;//term 1
  double d2;//term 2
  double d3;//term 3
  double d7;//term 7
  double d8;//term 8
  double d9;//term 9
  double dA;//term A
  double dB;//term B
  double dD;//term D
  double dE;//term E
  double dTerms;
  double dR_ip1half_np1half;
  double dR_im1half_np1half;
  double dR_i_np1half;
  double dU_ip1halfjk_np1half;
  double dU_im1halfjk_np1half;
  double dU_ijp1halfk_np1half;
  double dU_ijm1halfk_np1half;
  double dU_ijk_np1half;
  double dV_ijk_np1half;
  double dV_ip1halfjk_np1half;
  double dV_im1halfjk_np1half;
  double dV_ijp1halfk_np1half;
  double dV_ijm1halfk_np1half;
  double dDelR_i_np1half;
  double dConstantSq=parameters.dEddyViscosity*parameters.dEddyViscosity/pow(2.0,0.5);
  double dLengthScaleSq;
  double dU0_i_np1half;
  double dU0_ip1half_np1half;
  double dU0_im1half_np1half;
  
  //main grid explicit
  for(int i=grid.nStartUpdateExplicit[grid.nEddyVisc][0];
    i<grid.nEndUpdateExplicit[grid.nEddyVisc][0];i++){
      
    //calculate i for interface centered quantities
    nIInt=i+grid.nCenIntOffset[0];
    dR_ip1half_np1half=grid.dLocalGridOld[grid.nR][nIInt][0][0];
    dR_im1half_np1half=grid.dLocalGridOld[grid.nR][nIInt-1][0][0];
    dR_i_np1half=(dR_ip1half_np1half+dR_im1half_np1half)*0.5;
    dDelR_i_np1half=dR_ip1half_np1half-dR_im1half_np1half;
    dU0_ip1half_np1half=grid.dLocalGridOld[grid.nU0][nIInt][0][0];
    dU0_im1half_np1half=grid.dLocalGridOld[grid.nU0][nIInt-1][0][0];
    dU0_i_np1half=(grid.dLocalGridOld[grid.nU0][nIInt][0][0]
      +grid.dLocalGridOld[grid.nU0][nIInt-1][0][0])*0.5;
      
    for(int j=grid.nStartUpdateExplicit[grid.nEddyVisc][1];
      j<grid.nEndUpdateExplicit[grid.nEddyVisc][1];j++){
      
      nJInt=j+grid.nCenIntOffset[1];
      
      for(int k=grid.nStartUpdateExplicit[grid.nEddyVisc][2];
        k<grid.nEndUpdateExplicit[grid.nEddyVisc][2];k++){
        
        dLengthScaleSq=dDelR_i_np1half*dR_i_np1half*grid.dLocalGridOld[grid.nDTheta][0][j][0];
        
        //interpolate
        dU_ip1halfjk_np1half=grid.dLocalGridOld[grid.nU][nIInt][j][k];
        dU_im1halfjk_np1half=grid.dLocalGridOld[grid.nU][nIInt-1][j][k];
        dU_ijk_np1half=(grid.dLocalGridOld[grid.nU][nIInt][j][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j][k])*0.5;
        dU_ijp1halfk_np1half=(grid.dLocalGridOld[grid.nU][nIInt][j][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j][k]+grid.dLocalGridOld[grid.nU][nIInt][j+1][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j+1][k])*0.25;
        dU_ijm1halfk_np1half=(grid.dLocalGridOld[grid.nU][nIInt][j][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j][k]+grid.dLocalGridOld[grid.nU][nIInt][j-1][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j-1][k])*0.25;
        dV_ijk_np1half=(grid.dLocalGridOld[grid.nV][i][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i][nJInt-1][k])*0.5;
        dV_ip1halfjk_np1half=(grid.dLocalGridOld[grid.nV][i][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i][nJInt-1][k]+grid.dLocalGridOld[grid.nV][i+1][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i+1][nJInt-1][k])*0.25;
        dV_im1halfjk_np1half=(grid.dLocalGridOld[grid.nV][i][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i][nJInt-1][k]+grid.dLocalGridOld[grid.nV][i-1][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i-1][nJInt-1][k])*0.25;
        dV_ijp1halfk_np1half=grid.dLocalGridOld[grid.nV][i][nJInt][k];
        dV_ijm1halfk_np1half=grid.dLocalGridOld[grid.nV][i][nJInt-1][k];
        
        //term 1
        d1=((dU_ip1halfjk_np1half-dU0_ip1half_np1half)-(dU_im1halfjk_np1half-dU0_im1half_np1half))
          /(dR_ip1half_np1half-dR_im1half_np1half);
        
        //term 2
        d2=1.0/dR_i_np1half*(dU_ijp1halfk_np1half-dU_ijm1halfk_np1half)
          /grid.dLocalGridOld[grid.nDTheta][0][j][0];
        
        //term 3
        d3=dV_ijk_np1half/dR_i_np1half;
        
        //term 7
        d7=(dV_ip1halfjk_np1half-dV_im1halfjk_np1half)/dDelR_i_np1half;
        
        //term 8
        d8=1.0/dR_i_np1half*(dV_ijp1halfk_np1half-dV_ijm1halfk_np1half)
          /grid.dLocalGridOld[grid.nDTheta][0][j][0];
        
        //term 9
        d9=(dU_ijk_np1half-dU0_i_np1half)/dR_i_np1half;
        
        //term A
        dA=2.0*d1*d1;
        
        //term B
        dB=(d2+d1-d3)*(d2-d3);
        
        //term D
        dD=d7*(d2+d7-d3);
        
        //term E
        dE=d8+d9;
        dE=2.0*dE*dE;
        
        //term F
        
        dTerms=dA+dB+dD+dE;
        grid.dLocalGridOld[grid.nEddyVisc][i][j][k]=dLengthScaleSq*dConstantSq
          *grid.dLocalGridOld[grid.nD][i][j][k]*pow(dTerms,0.5);
      }
    }
  }
  
  //inner radial ghost cells, set to zero
  for(int i=0;i<grid.nNumGhostCells;i++){
    for(int j=grid.nStartUpdateExplicit[grid.nEddyVisc][1];
      j<grid.nEndUpdateExplicit[grid.nEddyVisc][1];j++){
      for(int k=grid.nStartUpdateExplicit[grid.nEddyVisc][2];
        k<grid.nEndUpdateExplicit[grid.nEddyVisc][2];k++){
        grid.dLocalGridOld[grid.nEddyVisc][i][j][k]=0.0;
      }
    }
  }
  
  //outter radial ghost cells,explicit
  for(int i=grid.nStartGhostUpdateExplicit[grid.nEddyVisc][0][0];
    i<grid.nEndGhostUpdateExplicit[grid.nEddyVisc][0][0];i++){
      
    //calculate i for interface centered quantities
    nIInt=i+grid.nCenIntOffset[0];
    dR_ip1half_np1half=grid.dLocalGridOld[grid.nR][nIInt][0][0];
    dR_im1half_np1half=grid.dLocalGridOld[grid.nR][nIInt-1][0][0];
    dR_i_np1half=(dR_ip1half_np1half+dR_im1half_np1half)*0.5;
    dDelR_i_np1half=dR_ip1half_np1half-dR_im1half_np1half;
    dU0_ip1half_np1half=grid.dLocalGridOld[grid.nU0][nIInt][0][0];
    dU0_im1half_np1half=grid.dLocalGridOld[grid.nU0][nIInt-1][0][0];
    dU0_i_np1half=(grid.dLocalGridOld[grid.nU0][nIInt][0][0]
      +grid.dLocalGridOld[grid.nU0][nIInt-1][0][0])*0.5;
    
    for(int j=grid.nStartGhostUpdateExplicit[grid.nEddyVisc][0][1];
      j<grid.nEndGhostUpdateExplicit[grid.nEddyVisc][0][1];j++){
      
      nJInt=j+grid.nCenIntOffset[1];
      
      for(int k=grid.nStartGhostUpdateExplicit[grid.nEddyVisc][0][2];
        k<grid.nEndGhostUpdateExplicit[grid.nEddyVisc][0][2];k++){
        
        dLengthScaleSq=dDelR_i_np1half*dR_i_np1half*grid.dLocalGridOld[grid.nDTheta][0][j][0];
        
        //interpolate
        dU_ip1halfjk_np1half=grid.dLocalGridOld[grid.nU][nIInt][j][k];
        dU_im1halfjk_np1half=grid.dLocalGridOld[grid.nU][nIInt-1][j][k];
        dU_ijk_np1half=(grid.dLocalGridOld[grid.nU][nIInt][j][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j][k])*0.5;
        dU_ijp1halfk_np1half=(grid.dLocalGridOld[grid.nU][nIInt][j][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j][k]+grid.dLocalGridOld[grid.nU][nIInt][j+1][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j+1][k])*0.25;
        dU_ijm1halfk_np1half=(grid.dLocalGridOld[grid.nU][nIInt][j][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j][k]+grid.dLocalGridOld[grid.nU][nIInt][j-1][k]
          +grid.dLocalGridOld[grid.nU][nIInt-1][j-1][k])*0.25;
        dV_ijk_np1half=(grid.dLocalGridOld[grid.nV][i][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i][nJInt-1][k])*0.5;
        dV_ip1halfjk_np1half=(grid.dLocalGridOld[grid.nV][i][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i][nJInt-1][k])*0.25;
        dV_im1halfjk_np1half=(grid.dLocalGridOld[grid.nV][i][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i][nJInt-1][k]+grid.dLocalGridOld[grid.nV][i-1][nJInt][k]
          +grid.dLocalGridOld[grid.nV][i-1][nJInt-1][k])*0.25;
        dV_ijp1halfk_np1half=grid.dLocalGridOld[grid.nV][i][nJInt][k];
        dV_ijm1halfk_np1half=grid.dLocalGridOld[grid.nV][i][nJInt-1][k];
        
        //term 1
        d1=((dU_ip1halfjk_np1half-dU0_ip1half_np1half)-(dU_im1halfjk_np1half-dU0_im1half_np1half))
          /(dR_ip1half_np1half-dR_im1half_np1half);
        
        //term 2
        d2=1.0/dR_i_np1half*(dU_ijp1halfk_np1half-dU_ijm1halfk_np1half)
          /grid.dLocalGridOld[grid.nDTheta][0][j][0];
        
        //term 3
        d3=dV_ijk_np1half/dR_i_np1half;
        
        //term 7
        d7=(dV_ip1halfjk_np1half-dV_im1halfjk_np1half)/dDelR_i_np1half;
        
        //term 8
        d8=1.0/dR_i_np1half*(dV_ijp1halfk_np1half-dV_ijm1halfk_np1half)
          /grid.dLocalGridOld[grid.nDTheta][0][j][0];
        
        //term 9
        d9=(dU_ijk_np1half-dU0_i_np1half)/dR_i_np1half;
        
        //term A
        dA=2.0*d1*d1;
        
        //term B
        dB=(d2+d1-d3)*(d2-d3);
        
        //term D
        dD=d7*(d2+d7-d3);
        
        //term E
        dE=d8+d9;
        dE=2.0*dE*dE;
        
        dTerms=dA+dB+dD+dE;
        grid.dLocalGridOld[grid.nEddyVisc][i][j][k]=dLengthScaleSq*dConstantSq
          *grid.dLocalGridOld[grid.nD][i][j][k]*pow(dTerms,0.5);
      }
    }
  }
}
