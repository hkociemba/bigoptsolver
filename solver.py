# ################### The SolverThread class solves implements the two phase algorithm #################################
import face
from defs import N_MOVE, N_FLIP, N_TWIST, N_PERM_4, BIG_TABLE
import cubie
import symmetries as sy
import coord
import enums as en
import moves as mv
import pruning as pr
import time

solfound = False  # global variable, True if solution is found
nodecount = 0  # number of nodes generated on certain level


def search(UD_flip, RL_flip, FB_flip, UD_twist, RL_twist, FB_twist, UD_slice_sorted, \
           RL_slice_sorted, FB_slice_sorted, UDcorn, RLcorn, FBcorn, corners, UD_dist, RL_dist, FB_dist, togo):
    global solfound, nodecount, cputime

    if solfound:
        return
    if togo == 0:
        if corners == 0:
            solfound = True
        return

    else:
        for m in en.Move:

            if len(sofar) > 0:
                diff = sofar[-1] // 3 - m // 3
                if diff in [0, 3]:  # successive moves on same face or on same axis with wrong order
                    continue

            nodecount += 1
            ################################################################################################################
            UD_twist1 = mv.twist_move[N_MOVE * UD_twist + m]
            UDcorn1 = mv.udcorners_move[N_MOVE * UDcorn + m]
            UD_flip1 = mv.flip_move[N_MOVE * UD_flip + m]
            UD_slice_sorted1 = mv.slice_sorted_move[N_MOVE * UD_slice_sorted + m]

            fs = N_FLIP * UD_slice_sorted1 + UD_flip1  # raw new flip_slicesorted coordinate
            # now representation as representant-symmetry pair
            fs_idx = sy.flipslicesorted_classidx[fs]  # index of representant
            fs_sym = sy.flipslicesorted_sym[fs]  # symmetry

            UD_dist1_mod3 = pr.get_fsstc_depth3(sy.udcorners_conj[(UDcorn1 << 4) + fs_sym],
                                                N_TWIST * fs_idx + sy.twist_conj[(UD_twist1 << 4) + fs_sym])
            UD_dist1 = pr.distance[3 * UD_dist + UD_dist1_mod3]

            ################################################################################################################
            mrl = sy.conj_move[N_MOVE * 16 + m]  # move viewed from 120° rotated position

            RL_twist1 = mv.twist_move[N_MOVE * RL_twist + mrl]
            RLcorn1 = mv.udcorners_move[N_MOVE * RLcorn + mrl]
            RL_flip1 = mv.flip_move[N_MOVE * RL_flip + mrl]
            RL_slice_sorted1 = mv.slice_sorted_move[N_MOVE * RL_slice_sorted + mrl]

            fs = N_FLIP * RL_slice_sorted1 + RL_flip1
            fs_idx = sy.flipslicesorted_classidx[fs]
            fs_sym = sy.flipslicesorted_sym[fs]

            RL_dist1_mod3 = pr.get_fsstc_depth3(sy.udcorners_conj[(RLcorn1 << 4) + fs_sym],
                                                N_TWIST * fs_idx + sy.twist_conj[(RL_twist1 << 4) + fs_sym])
            RL_dist1 = pr.distance[3 * RL_dist + RL_dist1_mod3]

            ################################################################################################################
            mfb = sy.conj_move[N_MOVE * 32 + m]  # move viewed from 240° rotated position

            FB_twist1 = mv.twist_move[N_MOVE * FB_twist + mfb]
            FBcorn1 = mv.udcorners_move[N_MOVE * FBcorn + mfb]
            FB_flip1 = mv.flip_move[N_MOVE * FB_flip + mfb]
            FB_slice_sorted1 = mv.slice_sorted_move[N_MOVE * FB_slice_sorted + mfb]

            fs = N_FLIP * FB_slice_sorted1 + FB_flip1
            fs_idx = sy.flipslicesorted_classidx[fs]
            fs_sym = sy.flipslicesorted_sym[fs]

            FB_dist1_mod3 = pr.get_fsstc_depth3(sy.udcorners_conj[(FBcorn1 << 4) + fs_sym],
                                                N_TWIST * fs_idx + sy.twist_conj[(FB_twist1 << 4) + fs_sym])
            FB_dist1 = pr.distance[3 * FB_dist + FB_dist1_mod3]

            ################################################################################################################

            corners1 = mv.corners_move[N_MOVE * corners + m]
            co_dist1 = pr.corner_depth[corners1]

            dist_new = max(UD_dist1, RL_dist1, FB_dist1)
            if UD_dist1 != 0 and UD_dist1 == RL_dist1 and RL_dist1 == FB_dist1:
                dist_new += 1  # not obvious but true
            dist_new = max(dist_new, co_dist1)

            if dist_new >= togo:  # impossible to reach subgroup H in togo_phase1 - 1 moves
                continue
            # timex = time.perf_counter()
            sofar.append(m)
            # cputime += (time.perf_counter() - timex)
            search(UD_flip1, RL_flip1, FB_flip1, UD_twist1, RL_twist1, FB_twist1, UD_slice_sorted1,
                   RL_slice_sorted1, FB_slice_sorted1, UDcorn1, RLcorn1, FBcorn1, corners1, UD_dist1, RL_dist1,
                   FB_dist1, togo - 1)
            if solfound:
                return
            sofar.pop(-1)


def solve(cubestring):
    """Solve a cube defined by its cube definition string.
     :param cubestring: The format of the string is given in the Facelet class defined in the file enums.py
    """
    global sofar  # the moves of the potential solution maneuver
    global solfound, nodecount, cputime
    fc = face.FaceCube()
    s = fc.from_string(cubestring)  # initialize fc
    if s != cubie.CUBE_OK:
        return s  # no valid cubestring, gives invalid facelet cube
    cc = fc.to_cubie_cube()
    s = cc.verify()
    if s != cubie.CUBE_OK:
        return s  # no valid facelet cube, gives invalid cubie cube

    coc = coord.CoordCube(cc)

    togo = max(coc.UD_phasex24x35_depth, coc.RL_phasex24x35_depth,
               coc.FB_phasex24x35_depth)  # lower bound for distance to solved
    solfound = False
    start_time = time.monotonic()
    totnodes = 0
    nodecount = 0
    while not solfound:
        sofar = []
        s_time = time.monotonic()
        totnodes += nodecount
        nodecount = 0
        search(coc.UD_flip, coc.RL_flip, coc.FB_flip, coc.UD_twist, coc.RL_twist, coc.FB_twist,
               coc.UD_slice_sorted, coc.RL_slice_sorted, coc.FB_slice_sorted, coc.UD_corners, coc.RL_corners,
               coc.FB_corners, coc.corners,
               coc.UD_phasex24x35_depth, coc.RL_phasex24x35_depth, coc.FB_phasex24x35_depth, togo)
        if togo > 14:
            t = time.monotonic() - s_time + 0.0001
            print('depth ' + str(togo) + ' done in ' + str(round(t, 2)) + ' s, ' + str(
                nodecount) + ' nodes generated, ' + 'about ' + str(round(nodecount / t)) + ' nodes/s')
        togo += 1
    print('total time: ' + str(
        round(time.monotonic() - start_time, 2)) + ' s, ' + 'nodes generated: ' + str(
        totnodes + nodecount))

    s = ''
    for m in sofar:
        s += m.name + ' '
    return s + '(' + str(len(s) // 3) + 'f*)'

########################################################################################################################
