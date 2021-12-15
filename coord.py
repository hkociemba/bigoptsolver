# ######################################### The cube on the coordinate level. ##########################################
import cubie as cb
from enums import Move
import moves as mv
import pruning as pr
import symmetries as sy
from defs import N_PERM_4, N_FLIP, N_TWIST, N_MOVE, BIG_TABLE

SOLVED = 0  # 0 is index of the solved state


class CoordCube:
    """Represent a cube on the coordinate level. There are 16 symmetries of a cube which keep the UD-axis fixed
    (point group D4h) and these can be used to reduce the size of the pruning tables

    0 <= corners < 8! describes the corner permutation.
    0 <= UD_twist < 3^7 describes the corner twist of the 8 corners relative to the UD-axis
    0 <= UD_flip < 2^11 describes the edge flip of the 12 edges relative to the UD-axis

    0 <= UD_slice_sorted < Binomial(12,4)*4! describes the position and permutation of the 4 UD-slice edges
    0 <= RL_slice_sorted < Binomial(12,4)*4! describes the position and permutation of the 4 RL-slice edges
    in a position of the cube which is rotated by 120° along the URF-DLB axis (the rotation that moves the RL-slice
    to the UD-slice)
    0 <= FB_slice_sorted < Binomial(12,4)*4! describes the position and permutation of the 4 FB-slice edges
    in a position of the cube which is rotated by 240° along the URF-DLB axis  (the rotation that moves the FB-slice
    to the UD-slice)

    0 <= UD_slice_sorted//4! = UD_slice < Binomial(12,4) just describes the position of the 4 UD-slice edges
    0 <= RL_slice_sorted//4! = RL_slice < Binomial(12,4) just describes the position of the 4 RL-slice edges
    0 <= FB_slice_sorted//4! = FB_slice < Binomial(12,4)  just describes the position of the 4 FB-slice edges

    The flip and the slice coordinate are combined to a flipslice coordinate in the range 0...1.013.760.
    0 <= UD_flipslice = 2^11*UD_slice + UD_flip < 2^11*Binomial(12,4) = 1.013.760 then is symmetry-reduced by the 16
     symmetries of D4h, which means in this case that you get 64430 equivalence classes (roughly 1.013.760//16) and
     most equivalence classes contain 16 positions which are related by D4h symmetry: s^-1*pos1*s = pos2 for some
     symmetry s from D4h and pos1 and pos2 in this class.
     For an UD_flipslice coordinate X then:
     flipslice_classidx[X] gives the index 0 <= clsidx < 64430 of the equivalence class that contains the
     UD_flipslice coordinate X and
     flipslice_sym[X] gives the symmetry 0 <= sym < 16 such that X = sym^-1*rep*sym, where rep is the representant
     of the class. We choose the representant to be the element with the smallest UD_flipslice coordinate in the
     equivalence class. The same applies for RL_flipslice and FB_flipslice.

     The pruning table then has 64430*3^7 entries and holds the information about the *shortest* distance of any position
     to some  position where flip = twist = slice = 0. The solved cube is one of these positions so the distance to a solved
     cube is at least the table distance. The pruning table can be used for all three orientations related
     by a 12O° rotation of the cube simultaneously. Only 2 bits are used per entry since the distance is only stored
     modulo 3 which still keeps all information.
    """

    def __init__(self, cc: cb.CubieCube = None):  # init CoordCube from CubieCube
        if cc is None:  # ID-Cube
            # The phase 1 slice coordinate is given by slice_sorted // 24

            self.corners = SOLVED  # corner permutation.

            self.UD_twist = SOLVED  # twist of corners relative to UD-axis
            self.UD_flip = SOLVED  # flip of edges relative to UD-axis
            self.UD_slice_sorted = SOLVED  # Position of FR, FL, BL, BR edges (<11880)
            self.UD_corners = SOLVED  # location of the four U or four D corners

            self.RL_twist = SOLVED  # twist of corners relative to RL-axis
            self.RL_flip = SOLVED  # flip of edges relative to RL-axis
            self.RL_slice_sorted = SOLVED  # Position of UF, UB, DB, DF edges (<11880)
            self.RL_corners = SOLVED  # location of the four R or four L corners

            self.FB_twist = SOLVED  # twist of corners relative to FB-axis
            self.FB_flip = SOLVED  # flip of edges
            self.FB_slice_sorted = SOLVED  # Position of UR, DR, DL, UL edges (<11880)
            self.FB_corners = SOLVED  # location of the four F or four B corners

            self.UD_phasex24_depth = 0
            self.RL_phasex24_depth = 0
            self.FB_phasex24_depth = 0

            self.corner_depth = 0
        else:

            self.corners = cc.get_corners()

            self.UD_twist = cc.get_twist()
            self.UD_flip = cc.get_flip()
            self.UD_slice_sorted = cc.get_slice_sorted()
            self.UD_corners = cc.get_dcorners()

            syc = sy.symCube[16]  # 120° rotation along URF-DBL axis
            ss = cb.CubieCube(syc.cp, syc.co, syc.ep, syc.eo)  # create copy of symCube[16]
            ss.multiply(cc)
            ss.multiply(sy.symCube[32])  # ss = symCube[16]*cc*symCube[16]^-1
            self.RL_twist = ss.get_twist()
            self.RL_flip = ss.get_flip()
            self.RL_slice_sorted = ss.get_slice_sorted()
            self.RL_corners = cc.get_dcorners()

            syc = sy.symCube[32]  # -120° rotation along URF-DBL axis
            ss = cb.CubieCube(syc.cp, syc.co, syc.ep, syc.eo)  # create copy of symCube[32]
            ss.multiply(cc)
            ss.multiply(sy.symCube[16])  # ss = symCube[32]*cc*symCube[32]^-1
            self.FB_twist = ss.get_twist()
            self.FB_flip = ss.get_flip()
            self.FB_slice_sorted = ss.get_slice_sorted()
            self.FB_corners = cc.get_dcorners()

            # symmetry reduced flipslicesorted coordinates, coord = sym^-1*rep*sym
            self.UD_flipslicesorted_clsidx = sy.flipslicesorted_classidx[N_FLIP * self.UD_slice_sorted + self.UD_flip]
            self.UD_flipslicesorted_sym = sy.flipslicesorted_sym[N_FLIP * self.UD_slice_sorted + self.UD_flip]
            self.UD_flipslicesorted_rep = sy.flipslicesorted_rep[self.UD_flipslicesorted_clsidx]

            self.RL_flipslicesorted_clsidx = sy.flipslicesorted_classidx[N_FLIP * self.RL_slice_sorted + self.RL_flip]
            self.RL_flipslicesorted_sym = sy.flipslicesorted_sym[N_FLIP * self.RL_slice_sorted + self.RL_flip]
            self.RL_flipslicesorted_rep = sy.flipslicesorted_rep[self.RL_flipslicesorted_clsidx]

            self.FB_flipslicesorted_clsidx = sy.flipslicesorted_classidx[N_FLIP * self.FB_slice_sorted + self.FB_flip]
            self.FB_flipslicesorted_sym = sy.flipslicesorted_sym[N_FLIP * self.FB_slice_sorted + self.FB_flip]
            self.FB_flipslicesorted_rep = sy.flipslicesorted_rep[self.FB_flipslicesorted_clsidx]

            self.UD_phasex24_depth = self.get_phasex24_depth(0)  # since we store the depth mod 3, retrieving the
            self.RL_phasex24_depth = self.get_phasex24_depth(1)  # initial absolute depth is a bit involved
            self.FB_phasex24_depth = self.get_phasex24_depth(2)

            self.UD_phasex24x35_depth = self.get_phasex24x35_depth(0)  # since we store the depth mod 3, retrieving the
            self.RL_phasex24x35_depth = self.get_phasex24x35_depth(1)  # initial absolute depth is a bit involved
            self.FB_phasex24x35_depth = self.get_phasex24x35_depth(2)

            self.corner_depth = pr.corner_depth[self.corners]  # for corners we store just the depth

    def __str__(self):
        s = '(UD_twist: ' + str(self.UD_twist) + ', UD_flip: ' + str(self.UD_flip) + ', UD_slice_sorted: ' + str(
            self.UD_slice_sorted) + ')'
        s = s + '\n' + 'UD classidx, sym, rep ' + str(self.UD_flipslicesorted_clsidx) + ' ' + \
            str(self.UD_flipslicesorted_sym) + ' ' + str(self.UD_flipslicesorted_rep)

        s = s + '\n' + '(RL_twist: ' + str(self.RL_twist) + ', RL_flip: ' + str(
            self.RL_flip) + ', RL_slice_sorted: ' + str(self.RL_slice_sorted) + ')'
        s = s + '\n' + 'RL classidx, sym, rep ' + str(self.RL_flipslicesorted_clsidx) + ' ' + \
            str(self.RL_flipslicesorted_sym) + ' ' + str(self.RL_flipslicesorted_rep)

        s = s + '\n' + '(FB_twist: ' + str(self.FB_twist) + ', FB_flip: ' + str(
            self.FB_flip) + ', FB_slice_sorted: ' + str(self.FB_slice_sorted) + ')'
        s = s + '\n' + ' FB_classidx, sym, rep ' + str(self.FB_flipslicesorted_clsidx) + ' ' + \
            str(self.FB_flipslicesorted_sym) + ' ' + str(self.FB_flipslicesorted_rep)

        s = s + '\n' + 'Corner_perm: ' + str(self.corners) + ', UD_corners: ' + str(
            self.UD_corners) + ', RL_corners: ' + str(self.RL_corners) + ', FB_corners: ' + str(self.FB_corners)

        s = s + '\n' + str(self.UD_phasex24x35_depth) + ' ' + str(self.RL_phasex24x35_depth) + ' ' + str(
            self.FB_phasex24x35_depth)
        return s + '\n'

    def move(self, m):
        """
        Update coordinates when move m is applied
        :param m: Move to be applied
        """
        self.corners = mv.corners_move[N_MOVE * self.corners + m]

        self.UD_twist = mv.twist_move[N_MOVE * self.UD_twist + m]
        self.UD_flip = mv.flip_move[N_MOVE * self.UD_flip + m]
        self.UD_slice_sorted = mv.slice_sorted_move[N_MOVE * self.UD_slice_sorted + m]

        self.UD_flipslicesorted_clsidx = sy.flipslicesorted_classidx[N_FLIP * self.UD_slice_sorted + self.UD_flip]
        self.UD_flipslicesorted_sym = sy.flipslicesorted_sym[N_FLIP * self.UD_slice_sorted + self.UD_flip]
        self.UD_flipslicesorted_rep = sy.flipslicesorted_rep[self.UD_flipslicesorted_clsidx]

        self.UD_corners = mv.udcorners_move[N_MOVE * self.UD_corners + m]

        m = sy.conj_move[N_MOVE * 16 + m]  # move changes too viewed from 120° rotated position
        self.RL_twist = mv.twist_move[N_MOVE * self.RL_twist + m]
        self.RL_flip = mv.flip_move[N_MOVE * self.RL_flip + m]
        self.RL_slice_sorted = mv.slice_sorted_move[N_MOVE * self.RL_slice_sorted + m]

        self.RL_flipslicesorted_clsidx = sy.flipslicesorted_classidx[N_FLIP * self.RL_slice_sorted + self.RL_flip]
        self.RL_flipslicesorted_sym = sy.flipslicesorted_sym[N_FLIP * self.RL_slice_sorted + self.RL_flip]
        self.RL_flipslicesorted_rep = sy.flipslicesorted_rep[self.RL_flipslicesorted_clsidx]

        self.RL_corners = mv.udcorners_move[N_MOVE * self.RL_corners + m]

        m = sy.conj_move[N_MOVE * 16 + m]  # move changes too viewed from 240° rotated position
        self.FB_twist = mv.twist_move[N_MOVE * self.FB_twist + m]
        self.FB_flip = mv.flip_move[N_MOVE * self.FB_flip + m]
        self.FB_slice_sorted = mv.slice_sorted_move[N_MOVE * self.FB_slice_sorted + m]

        self.FB_flipslicesorted_clsidx = sy.flipslicesorted_classidx[N_FLIP * self.FB_slice_sorted + self.FB_flip]
        self.FB_flipslicesorted_sym = sy.flipslicesorted_sym[N_FLIP * self.FB_slice_sorted + self.FB_flip]
        self.FB_flipslicesorted_rep = sy.flipslicesorted_rep[self.FB_flipslicesorted_clsidx]

        self.FB_corners = mv.udcorners_move[N_MOVE * self.FB_corners + m]

        self.UD_phasex24_depth = self.get_phasex24_depth(0)
        self.RL_phasex24_depth = self.get_phasex24_depth(1)
        self.FB_phasex24_depth = self.get_phasex24_depth(2)

        self.UD_phasex24x35_depth = self.get_phasex24x35_depth(0)
        self.RL_phasex24x35_depth = self.get_phasex24x35_depth(1)
        self.FB_phasex24x35_depth = self.get_phasex24x35_depth(2)

        self.corner_depth = pr.corner_depth[self.corners]  # for corners we store just the depth

    # def get_phase1_depth(self, position):
    #     """
    #     Compute the distance to the cube subgroup H where flip=slice=twist=0
    #     :param position: The current cube state
    #     :return: The distance to H
    #     """
    #     if position == 0:
    #         slice_ = self.UD_slice_sorted // N_PERM_4
    #         flip = self.UD_flip
    #         twist = self.UD_twist
    #     elif position == 1:
    #         slice_ = self.RL_slice_sorted // N_PERM_4
    #         flip = self.RL_flip
    #         twist = self.RL_twist
    #     else:
    #         slice_ = self.FB_slice_sorted // N_PERM_4
    #         flip = self.FB_flip
    #         twist = self.FB_twist
    #
    #     flipslice = N_FLIP * slice_ + flip
    #     classidx = sy.flipslice_classidx[flipslice]
    #     sym = sy.flipslice_sym[flipslice]
    #     depth_mod3 = pr.get_flipslice_twist_depth3(N_TWIST * classidx + sy.twist_conj[(twist << 4) + sym])
    #
    #     depth = 0
    #     while flip != SOLVED or slice_ != SOLVED or twist != SOLVED:
    #         if depth_mod3 == 0:
    #             depth_mod3 = 3
    #         for m in Move:  # we can use the same m in all 3 rotational positions
    #             twist1 = mv.twist_move[N_MOVE * twist + m]
    #             flip1 = mv.flip_move[N_MOVE * flip + m]
    #             slice1 = mv.slice_sorted_move[N_MOVE * slice_ * N_PERM_4 + m] // N_PERM_4  # we may set perm=0 here
    #             flipslice1 = N_FLIP * slice1 + flip1
    #             classidx1 = sy.flipslice_classidx[flipslice1]
    #             sym = sy.flipslice_sym[flipslice1]
    #             if pr.get_flipslice_twist_depth3(
    #                     N_TWIST * classidx1 + sy.twist_conj[(twist1 << 4) + sym]) == depth_mod3 - 1:
    #                 depth += 1
    #                 twist = twist1
    #                 flip = flip1
    #                 slice_ = slice1
    #                 depth_mod3 -= 1
    #                 break
    #     return depth

    def get_phasex24_depth(self, position):
        """
         Compute the distance to the cube subgroup  where flip=slicesorted=twist=0
        :param position:
        :return:
        """
        # find initial distance from given position
        if position == 0:
            slicesorted = self.UD_slice_sorted
            flip = self.UD_flip
            twist = self.UD_twist
        elif position == 1:
            slicesorted = self.RL_slice_sorted
            flip = self.RL_flip
            twist = self.RL_twist
        else:
            slicesorted = self.FB_slice_sorted
            flip = self.FB_flip
            twist = self.FB_twist

        flipslicesorted = N_FLIP * slicesorted + flip
        classidx = sy.flipslicesorted_classidx[flipslicesorted]
        sym = sy.flipslicesorted_sym[flipslicesorted]
        depth_mod3 = pr.get_flipslicesorted_twist_depth3(N_TWIST * classidx + sy.twist_conj[(twist << 4) + sym])

        depth = 0
        while flip != SOLVED or slicesorted != SOLVED or twist != SOLVED:
            if depth_mod3 == 0:
                depth_mod3 = 3
            for m in Move:  # we can use the same m in all 3 rotational positions
                twist1 = mv.twist_move[N_MOVE * twist + m]
                flip1 = mv.flip_move[N_MOVE * flip + m]
                slicesorted1 = mv.slice_sorted_move[N_MOVE * slicesorted + m]
                flipslicesorted1 = N_FLIP * slicesorted1 + flip1
                classidx1 = sy.flipslicesorted_classidx[flipslicesorted1]
                sym = sy.flipslicesorted_sym[flipslicesorted1]
                if pr.get_flipslicesorted_twist_depth3(
                        N_TWIST * classidx1 + sy.twist_conj[(twist1 << 4) + sym]) == depth_mod3 - 1:
                    depth += 1
                    twist = twist1
                    flip = flip1
                    slicesorted = slicesorted1
                    depth_mod3 -= 1
                    break
        return depth

    def get_phasex24x35_depth(self, position):
        """
         Compute the distance to the cube subgroup  where flip=slicesorted=twist=0
        :param position:
        :return:
        """
        # find initial distance from given position
        if position == 0:
            slicesorted = self.UD_slice_sorted
            flip = self.UD_flip
            twist = self.UD_twist
            corners = self.UD_corners
        elif position == 1:
            slicesorted = self.RL_slice_sorted
            flip = self.RL_flip
            twist = self.RL_twist
            corners = self.RL_corners
        else:
            slicesorted = self.FB_slice_sorted
            flip = self.FB_flip
            twist = self.FB_twist
            corners = self.FB_corners
        flipslicesorted = N_FLIP * slicesorted + flip
        classidx = sy.flipslicesorted_classidx[flipslicesorted]
        sym = sy.flipslicesorted_sym[flipslicesorted]
        # depth_mod3 = pr.get_flipslicesorted_twist_depth3(N_TWIST * classidx + sy.twist_conj[(twist << 4) + sym])
        depth_mod3 = pr.get_fsstc_depth3(sy.udcorners_conj[(corners << 4) + sym],
                                         N_TWIST * classidx + sy.twist_conj[(twist << 4) + sym])
        depth = 0
        while flip != SOLVED or slicesorted != SOLVED or twist != SOLVED or corners != SOLVED:
            if depth_mod3 == 0:
                depth_mod3 = 3
            for m in Move:  # we can use the same m in all 3 rotational positions
                twist1 = mv.twist_move[N_MOVE * twist + m]
                corners1 = mv.udcorners_move[N_MOVE * corners + m]
                flip1 = mv.flip_move[N_MOVE * flip + m]
                slicesorted1 = mv.slice_sorted_move[N_MOVE * slicesorted + m]
                flipslicesorted1 = N_FLIP * slicesorted1 + flip1
                classidx1 = sy.flipslicesorted_classidx[flipslicesorted1]
                sym = sy.flipslicesorted_sym[flipslicesorted1]
                # if pr.get_flipslicesorted_twist_depth3(
                #        N_TWIST * classidx1 + sy.twist_conj[(twist1 << 4) + sym]) == depth_mod3 - 1:
                if pr.get_fsstc_depth3(sy.udcorners_conj[(corners1 << 4) + sym],
                                       N_TWIST * classidx1 + sy.twist_conj[(twist1 << 4) + sym]) == depth_mod3 - 1:
                    depth += 1
                    twist = twist1
                    corners = corners1
                    flip = flip1
                    slicesorted = slicesorted1
                    depth_mod3 -= 1
                    break
        return depth
