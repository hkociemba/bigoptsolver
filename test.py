import solver
import face
from cubie import CubieCube
from enums import Move as m


cbc = CubieCube()
cbc.move(m.U3)
fc = cbc.to_facelet_cube()
s = fc.to_string()
print(s)
s = solver.solve(s)
print(s)
