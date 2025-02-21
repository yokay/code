L 15[mm] ""
H 50[mm] ""
f0 4[MHz] ""
T0 1/f0 ""
c0 1500[m/s] ""
lmd0 c0/f0 ""
hmax lmd0/10 ""
F 11[mm] ""
delta 2[mm] ""
Tmax sqrt(F^2+(delta*4)^2)/c0 ""
w 1[mm] ""
n Tmax/T0 ""
k 1 ""
d0 3.8[nm] 换能器的位移大小
z_tissue 24.6[mm] 生体组织的起始位置
alpha_water 0.025[1/m] 水的吸声系数
alpha_tissue 8.55[1/m] 生体组织的吸声系数
ro 1000[kg/m^3] ""
u 1[m/s] ""
Rmax 7[mm] ""
N 6 ""
difL lmd0*0.6 ""
maxArea pi*Rmax^2 ""
avgArea "(maxArea-(N-1)*2*pi*Rmax/2*difL) / N" ""
maxDif difL ""
Rin0 0[mm] ""
Rout0 sqrt(avgArea/pi+Rin0^2) ""
Rc0 rn(Rin0,Rout0) ""
Rin1 Rout0+maxDif ""
Rout1 sqrt(Rin1^2+Rout0^2) ""
Rc1 rn(Rin1,Rout1) ""
wc1 Rout1-Rin1 ""
Rin2 Rout1+maxDif ""
Rout2 sqrt(Rin2^2+Rout0^2) ""
Rc2 rn(Rin2,Rout2) ""
wc2 Rout2-Rin2 ""
Rin3 Rout2+maxDif ""
Rout3 sqrt(Rin3^2+Rout0^2) ""
Rc3 rn(Rin3,Rout3) ""
wc3 Rout3-Rin3 ""
Rin4 Rout3+maxDif ""
Rout4 sqrt(Rin4^2+Rout0^2) ""
Rc4 rn(Rin4,Rout4) ""
wc4 Rout4-Rin4 ""
Rin5 Rout4+maxDif ""
Rout5 sqrt(Rin5^2+Rout0^2) ""
Rc5 rn(Rin5,Rout5) ""
wc5 Rout5-Rin5 ""

delay5 (sqrt((F^2+Rc5^2)))/c0 ""
delay0 delay5-(sqrt((F^2+Rc0^2)))/c0 ""
delay1 delay5-(sqrt((F^2+Rc1^2)))/c0 ""
delay2 delay5-(sqrt((F^2+Rc2^2)))/c0 ""
delay3 delay5-(sqrt((F^2+Rc3^2)))/c0 ""
delay4 delay5-(sqrt((F^2+Rc4^2)))/c0 ""
p0 ro*c0*u ""
phi0 -2*pi*f0*delay0 "Phase change"
phi1 -2*pi*f0*delay1 "Phase change"
phi2 -2*pi*f0*delay2 "Phase change"
phi3 -2*pi*f0*delay3 "Phase change"
phi4 -2*pi*f0*delay4 "Phase change"
phi5 -2*pi*f0*delay5 "Phase change"

2/3*(Rout^3-Rin^3)/(Rout^2-Rin^2)


# Created by COMSOL Multiphysics.

# Major & minor version
0 1 
1 # number of tags
# Tags
3 fin 
1 # number of types
# Types
3 obj 

# --------- Object 0 ----------

0 0 1 
5 Geom2 # class
2 # version
2 # type
1 # voidsLabeled
1e-10 # gtol
0.0001 # resTol

27 # number of vertices
# Vertices
# X Y dom tol
0 0 -1 NAN 
0 5 -1 NAN 
0 10 -1 1e-10 
0 35 -1 1e-10 
0 50 -1 NAN 
0 50.5 -1 NAN 
1.5 10 -1 NAN 
1.5 35 -1 1.1102230246251565e-16 
2.6180463454008347 0 -1 1.0000000693889391e-10 
2.8430463454008348 0 -1 1.0000000693889391e-10 
3.8648517680195322 0 -1 1.0000002775557562e-10 
4.0898517680195328 0 -1 1.0000001387778781e-10 
4.8560327584396674 0 -1 1e-10 
5.081032758439668 0 -1 1.0000001387778781e-10 
5.7158604390768399 0 -1 1e-10 
5.9408604390768405 0 -1 1e-10 
6.4921482903007472 0 -1 1e-10 
6.7171482903007496 0 -1 1e-10 
7.2093167374278222 0 -1 1.0000002775557562e-10 
15 0 -1 NAN 
15 5 -1 1.0000005551115123e-10 
15 50 -1 1.1102230246251565e-16 
15 50.5 -1 1.1102230246251565e-16 
15.5 0 -1 NAN 
15.5 5 -1 1.0000002775557562e-10 
15.5 50 -1 3.1086244689504383e-15 
15.5 50.5 -1 NAN 

33 # number of edges
# Edges
# vtx1 vtx2 s1 s2 up down curve tol
1 2 0 1 0 1 1 NAN 
9 1 0 1 0 1 2 NAN 
2 3 0 1 0 2 3 NAN 
21 2 0 1 1 2 4 NAN 
3 4 0 1 0 3 5 NAN 
7 3 0 1 2 3 6 NAN 
4 5 0 1 0 2 7 NAN 
4 8 0 1 2 3 8 NAN 
5 6 0 1 0 4 9 NAN 
5 22 0 1 4 2 10 NAN 
6 23 0 1 0 4 11 NAN 
8 7 0 1 2 3 12 NAN 
10 9 0 1 0 1 13 NAN 
11 10 0 1 0 1 14 NAN 
12 11 0 1 0 1 15 NAN 
13 12 0 1 0 1 16 NAN 
14 13 0 1 0 1 17 NAN 
15 14 0 1 0 1 18 NAN 
16 15 0 1 0 1 19 NAN 
17 16 0 1 0 1 20 NAN 
18 17 0 1 0 1 21 NAN 
19 18 0 1 0 1 22 NAN 
20 19 0 1 0 1 23 NAN 
21 20 0 1 5 1 24 NAN 
24 20 0 1 0 5 25 NAN 
22 21 0 1 6 2 26 NAN 
21 25 0 1 6 5 27 NAN 
23 22 0 1 7 4 28 NAN 
22 26 0 1 7 6 29 NAN 
23 27 0 1 0 7 30 NAN 
25 24 0 1 0 5 31 NAN 
26 25 0 1 0 6 32 NAN 
27 26 0 1 0 7 33 NAN 

33 # number of curves
# Curves

# Curve 1
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 0 
0 5 

# Curve 2
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
2.6180463454008351 0 
0 0 

# Curve 3
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 5 
0 10 

# Curve 4
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 5 
0 5 

# Curve 5
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 10 
0 35 

# Curve 6
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
1.5 10 
0 10 

# Curve 7
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 35 
0 50 

# Curve 8
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 35 
1.5 35 

# Curve 9
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 50 
0 50.5 

# Curve 10
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 50 
15 50 

# Curve 11
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
0 50.5 
15 50.5 

# Curve 12
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
1.5 35 
1.5 10 

# Curve 13
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
2.8430463454008352 0 
2.6180463454008351 0 

# Curve 14
11 BezierCurve # class
1 # version
2 # sdim
1 # rational?
1 # degree
# homogeneous control points
3.8648517680195322 0 1 
2.8430463454008348 0 1 

# Curve 15
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
4.0898517680195319 0 
3.8648517680195331 0 

# Curve 16
11 BezierCurve # class
1 # version
2 # sdim
1 # rational?
1 # degree
# homogeneous control points
4.8560327584396674 0 1 
4.0898517680195328 0 1 

# Curve 17
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
5.081032758439668 0 
4.8560327584396674 0 

# Curve 18
11 BezierCurve # class
1 # version
2 # sdim
1 # rational?
1 # degree
# homogeneous control points
5.7158604390768399 0 1 
5.081032758439668 0 1 

# Curve 19
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
5.9408604390768405 0 
5.7158604390768399 0 

# Curve 20
11 BezierCurve # class
1 # version
2 # sdim
1 # rational?
1 # degree
# homogeneous control points
6.4921482903007472 0 1 
5.9408604390768405 0 1 

# Curve 21
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
6.7171482903007496 0 
6.4921482903007472 0 

# Curve 22
11 BezierCurve # class
1 # version
2 # sdim
1 # rational?
1 # degree
# homogeneous control points
7.2093167374278222 0 1 
6.7171482903007496 0 1 

# Curve 23
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 0 
7.2093167374278204 0 

# Curve 24
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 5 
15 0 

# Curve 25
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15.5 0 
15 0 

# Curve 26
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 50 
15 5 

# Curve 27
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 5 
15.5 5 

# Curve 28
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 50.5 
15 50 

# Curve 29
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 50 
15.5 50 

# Curve 30
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15 50.5 
15.5 50.5 

# Curve 31
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15.5 4.9999999999999991 
15.5 0 

# Curve 32
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15.5 50 
15.5 4.9999999999999991 

# Curve 33
11 BezierCurve # class
1 # version
2 # sdim
0 # rational?
1 # degree
# control points
15.5 50.5 
15.5 50 
# Attributes
0 # nof attributes
