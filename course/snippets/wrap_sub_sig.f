	subroutine phipol(j,mm,nodes,wei,nn,x,phi,wrk)
	
	implicit real *8 (a-h, o-z)
	real *8 nodes(*),wei(*),x(*),wrk(*),phi(*)
	real *8 sum, one, two, half
