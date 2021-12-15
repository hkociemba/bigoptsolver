from cubie import CubieCube
import solver as sv
import time


def test(n):
    """
    Optimally solve n random cubes with information about the solving process
    :param n: THe number of random cubes to solve
    """
    start_time = time.monotonic()
    cc = CubieCube()
    for i in range(n):
        cc.randomize()
        fc = cc.to_facelet_cube()
        s = fc.to_string()
        print(s)
        s = sv.solve(s)
        print(s)
        print()
    print('total time for '+ str(n) + ' cubes:' + str(round(time.monotonic() - start_time, 2)) + ' s')

