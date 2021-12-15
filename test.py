# import solver
import face
from cubie import CubieCube
from coord import CoordCube
from enums import Move as m
import array as ar
import defs

cbc = CubieCube()
coc1 = CoordCube()
coc2 = CoordCube()

# coc1.move(m.R1)
# coc1.move(m.F2)
# coc1.move(m.U3)
# print(coc1)

coc2.move(m.B1)
coc2.move(m.R2)
coc2.move(m.F2)
coc2.move(m.U3)
print(coc2)



# for i in range(35):
#     cbc.set_dcorners(i)
#     print(cbc.get_dcorners())
#     # print(cbc)
#     cbc.udcorners_swap()
#     print(cbc.get_dcorners())
#     print()
