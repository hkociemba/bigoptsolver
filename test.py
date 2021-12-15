import solver
import face
from cubie import CubieCube
from coord import CoordCube
from enums import Move as m
import array as ar
import defs



cbc = CubieCube()
cbc.move(m.U3)
fc = cbc.to_facelet_cube()
s = fc.to_string()
print(s)
s = solver.solve(s)
print(s)