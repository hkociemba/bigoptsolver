# RubiksCube-BigOptimalSolver
## Overview 
This project is similar to the [RubiksCube-Optimalsolver](https://github.com/hkociemba/RubiksCube-OptimalSolver)
project and optimally solves a given Rubik's cube.   
But the pruning table is 35 times larger because it includes the UD_corners, RL_corners and FB_corners coordinates. 
The 0 <= UD_corners < Binomial(8,4)/2 = 35 describes for example the position of the U-corners and is 0 if the four 
U-corners are all in the U-face or all in the D-face.

The program needs 30 GB of memory which is more than a standard PC has. It is highly recommended to use PyPy instead
of the standard CPython interpreter. Only with PyPy the table creation completes within about 12 hours and the
optimal solving process takes less than 30 seconds on average.
## Usage
To run the program from a Python console make sure that all files are in your PATH and do a

```python
>>> import solver as sv
```

This creates the necessary tables which are stored as files, so you should also have about 30 GB of disk space available.  

A cube is defined by its cube definition string. A solved cube has the string 'UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB'.   
```python
>>> cubestring = 'DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL'
```
See https://github.com/hkociemba/RubiksCube-TwophaseSolver/blob/master/enums.py for the exact  format.
```python
>>> sv.solve(cubestring)
```
This optimally solves the cube described by the definition string. After about 6 s (using PyPy) we get
```python
'U1 B2 D3 B3 R3 L3 U1 L2 B2 R1 D3 R3 B1 L3 U2 B2 R1 D3 (18f*)'
```

U, R, F, D, L and B denote the Up, Right, Front, Down, Left and Back face of the cube. 1, 2, and 3 denote a 90°, 180°
and 270° clockwise rotation of the corresponding face. (18f*) means that the solution has 18 moves in the face turn
metric and the star indicates that it is an optimal solution.


You can test the performance of the algorithm on your machine with something similar to
```python
>>> import performance as pf
>>> pf.test(10)
```
This will for example generate 10 random cubes and gives information about the solving process. 

## Performance results

We solved 10 random cubes with PyPy (pypy3). All computations were done on a Windows 10 machine with an AMD Ryzen 7 3700X 3.59 GHz.

#### Table creation time (to be performed only once)
PyPy: about 12 hours

#### Solving statistics for 10 random cubes
The optimal solving time was in a range between 1 s and 77 s, the total time for the 10 cubes was 276 s. The average
optimal solving length was 17.80

1. BFDFUDLURULLURBBRUFFBFFLRURFRDBDDDBLULDULRRDUBDLLBBFRF  
depth 15 done in 0.16 s, 53916 nodes generated, about 345394 nodes/s  
depth 16 done in 0.77 s, 746985 nodes generated, about 975049 nodes/s  
depth 17 done in 0.84 s, 1250510 nodes generated, about 1481471 nodes/s  
total time: 1.84 s, nodes generated: 2055605  
U2 B2 U1 D2 F3 R3 L1 F1 D1 B2 D1 F3 R2 U1 R3 F3 B1 (17f*)    
  

2. LBLDUFULURLDDRBLRRBUFDFRFUURFBBDULBDDLRRLFFRDFUBLBFBDU  
depth 15 done in 0.17 s, 48150 nodes generated, about 281414 nodes/s  
depth 16 done in 0.64 s, 659136 nodes generated, about 1028133 nodes/s  
depth 17 done in 5.36 s, 9147162 nodes generated, about 1706847 nodes/s  
depth 18 done in 21.95 s, 40305974 nodes generated, about 1835920 nodes/s  
total time: 28.17 s, nodes generated: 50163938  
R3 U3 L1 D2 R2 B3 U2 B2 D1 R3 F1 L3 U3 B3 U3 R2 L1 F3 (18f*)  
  

3. LDFDUDDBLURRFRLLBDFRFDFUBRBUFDUDLRUBFBRFLFBRLULDUBLRBU  
depth 15 done in 0.03 s, 48741 nodes generated, about 1567235 nodes/s  
depth 16 done in 0.34 s, 693081 nodes generated, about 2014185 nodes/s  
depth 17 done in 4.99 s, 9653457 nodes generated, about 1936462 nodes/s  
depth 18 done in 70.64 s, 133116840 nodes generated, about 1884437 nodes/s  
depth 19 done in 0.64 s, 1191496 nodes generated, about 1858518 nodes/s  
total time: 76.64 s, nodes generated: 144707425  
U1 R1 U2 L3 U3 F1 D1 F3 D1 L1 U1 L2 F2 R1 U2 L3 D1 L1 D1 (19f*)  
  

4. UBULURLUURFBBRRFBDUFFRFUDUDBLRDDDFRBBDFFLBLFLLLRUBLRDD  
depth 15 done in 0.02 s, 36969 nodes generated, about 2448278 nodes/s  
depth 16 done in 0.28 s, 526734 nodes generated, about 1867189 nodes/s  
depth 17 done in 4.05 s, 7560855 nodes generated, about 1868216 nodes/s  
depth 18 done in 36.33 s, 67375670 nodes generated, about 1854643 nodes/s  
total time: 40.67 s, nodes generated: 75503012  
D2 L2 F2 U2 B1 R1 U2 B2 D3 L3 D2 F1 U1 L3 D1 R1 L2 F1 (18f*)  
  

5. DBDDUFLURUUBLRLLLFBRBFFBLLDUFFFDUDRRBBUULDRRFRRLDBBUDF  
depth 15 done in 0.03 s, 62904 nodes generated, about 2022637 nodes/s  
depth 16 done in 0.45 s, 859860 nodes generated, about 1897727 nodes/s  
depth 17 done in 0.66 s, 1242421 nodes generated, about 1893646 nodes/s  
total time: 1.16 s, nodes generated: 2169982  
U2 F3 L1 D2 F3 U2 R1 U2 L2 B1 R1 U3 R3 B3 U1 F2 D2 (17f*)  
  

6. UFRBURDRRBUFBRFDLFBFDDFDBUFUBLLDBFLUBRLLLRRDLDDRUBULFU  
depth 15 done in 0.02 s, 32706 nodes generated, about 2031429 nodes/s  
depth 16 done in 0.28 s, 508701 nodes generated, about 1809680 nodes/s  
depth 17 done in 4.06 s, 7572603 nodes generated, about 1864209 nodes/s  
depth 18 done in 8.17 s, 15475124 nodes generated, about 1893653 nodes/s  
total time: 12.53 s, nodes generated: 23591405  
U3 L1 B3 D1 R3 F2 D1 B1 L1 D3 B3 L2 F1 L1 D3 F1 B1 D1 (18f*)  
  

7. LDDRUFLLBDDFFRBRRUBURDFUDBBFLUDDFBLFUUUBLLDBRLRFUBRRFL  
depth 15 done in 0.03 s, 52698 nodes generated, about 1694469 nodes/s  
depth 16 done in 0.41 s, 725814 nodes generated, about 1782889 nodes/s  
depth 17 done in 5.44 s, 9903435 nodes generated, about 1821455 nodes/s  
depth 18 done in 51.34 s, 94051700 nodes generated, about 1831792 nodes/s  
total time: 57.22 s, nodes generated: 104738015  
D3 L3 B2 D3 R3 B3 U2 F3 L3 B3 R2 F2 U1 R1 D2 R3 L3 D2 (18f*)  
  

8. RDBDURBDDLBLFRFFRBLRFUFDDUUFBLBDFFFUBLDRLLRLRUBDLBURUU  
depth 15 done in 0.06 s, 104532 nodes generated, about 1683285 nodes/s  
depth 16 done in 0.7 s, 1273731 nodes generated, about 1811593 nodes/s  
depth 17 done in 3.53 s, 6431696 nodes generated, about 1821443 nodes/s  
total time: 4.3 s, nodes generated: 7820126  
R3 L2 F3 B2 R3 U2 F1 U3 B2 U1 R1 F2 L3 U1 R1 D1 L1 (17f*)  
  

9. UUFDUUBULBLDLRRRLDLRURFBLFBURULDFLFBRFDBLBDDFRBFDBDRUF  
depth 15 done in 0.03 s, 72216 nodes generated, about 2322058 nodes/s  
depth 16 done in 0.52 s, 952608 nodes generated, about 1845782 nodes/s  
depth 17 done in 6.75 s, 12569142 nodes generated, about 1862068 nodes/s  
depth 18 done in 19.5 s, 36180053 nodes generated, about 1855378 nodes/s  
total time: 26.81 s, nodes generated: 49779680  
R1 F3 U2 R2 L1 D3 R3 F1 D3 B1 D3 R2 U3 F3 U3 L2 B1 R1 (18f*)  
  

10. DDUDUUBUFLRFDRFBLRUBUUFBRLUDURLDBBBDLRLRLFDFFRLFDBFBRL
depth 15 done in 0.05 s, 89469 nodes generated, about 1899554 nodes/s  
depth 16 done in 0.63 s, 1171254 nodes generated, about 1873707 nodes/s  
depth 17 done in 8.16 s, 15289401 nodes generated, about 1874597 nodes/s  
depth 18 done in 18.0 s, 34011066 nodes generated, about 1889493 nodes/s  
total time: 26.83 s, nodes generated: 50567973  
U3 L2 F2 R3 B2 U1 R3 F3 U1 R2 F3 D3 F3 U3 F1 R2 F1 D1 (18f*)  



#### Conclusion:
Optimally solving Rubik's Cube with Python using PyPy is done within seconds if you have enough RAM to run a program
which consumes about 30 GB of memory.


 
 