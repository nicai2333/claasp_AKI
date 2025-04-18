
# ****************************************************************************
# Copyright 2023 Technology Innovation Institute
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ****************************************************************************


from claasp.cipher import Cipher
from claasp.name_mappings import INPUT_KEY, INPUT_PLAINTEXT

PARAMETERS_CONFIGURATION_LIST = [{'word_size': 8, 'state_size': 4, 'number_of_rounds': 10}]


class AESBlockCipherSkinnySbox(Cipher):
    """
    Return a cipher object of AES Block Cipher.

    INPUT:

    - ``number_of_rounds`` -- **integer** (default: `10`); number of rounds of the cipher
    - ``word_size`` -- **integer** (default: `8`); size of each word of the state. Must be equal to 2, 3, 4 or 8
    - ``state_size`` -- **integer** (default: `4`); number of rows of the state represented as a matrix.
      Must be equal to 2, 3 or 4

    EXAMPLES::

        sage: from claasp.ciphers.block_ciphers.aes_block_cipher import AESBlockCipher
        sage: aes = AESBlockCipher()
        sage: key = 0x2b7e151628aed2a6abf7158809cf4f3c
        sage: plaintext = 0x6bc1bee22e409f96e93d7e117393172a
        sage: ciphertext = 0x3ad77bb40d7a3660a89ecaf32466ef97
        sage: aes.evaluate([key, plaintext]) == ciphertext
        True
    """

    def __init__(self, number_of_rounds=10, word_size=8, state_size=4, key_size=-1):

        if word_size not in [2, 3, 4, 8]:
            raise ValueError("word_size incorrect (should be in [2,3,4,8])")
        if state_size not in [2, 3, 4]:
            raise ValueError("state_size incorrect (should be in [2,3,4])")

        # cipher dictionary initialize
        self.CIPHER_BLOCK_SIZE = state_size ** 2 * word_size
        if key_size == -1 :
            self.KEY_BLOCK_SIZE = self.CIPHER_BLOCK_SIZE
        else :
            self.KEY_BLOCK_SIZE = key_size
        self.NROUNDS = number_of_rounds
        self.SBOX_BIT_SIZE = 4
        self.NUM_SBOXES = state_size ** 2
        self.NUM_ROWS = state_size
        self.ROW_SIZE = state_size * word_size

        super().__init__(family_name="aes_block_cipher_skinny_sbox",
                         cipher_type="block_cipher",
                         cipher_inputs=[INPUT_KEY, INPUT_PLAINTEXT],
                         cipher_inputs_bit_size=[self.KEY_BLOCK_SIZE, self.CIPHER_BLOCK_SIZE],
                         cipher_output_bit_size=self.CIPHER_BLOCK_SIZE)

        # In function of wordsize
        self.sbox = [0xc,0x6,0x9,0x0,0x1,0xa,0x2,0xb,0x3,0x8,0x5,0xd,0x4,0xe,0x7,0xf]
        # self.sbox = [0x0,0x1,0x2,0x3,0x4,0x5,0x6,0x7,0x8,0x9,0xa,0xb,0xc,0xd,0xe,0xf]
        

        # self.permutation_box = [5,2,3,8,9,6,7,12,13,10,11,0,1,14,15,4]
        # self.permutation_box = [0,2,3,8,9,6,7,12,13,10,11,5,1,14,15,4] 
        # self.permutation_box = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15] 

        # In function of wordsize
        self.ROUND_CONSTANT = {
            2: [
                "0b01000000", "0b10000000", "0b11000000", "0b01000000", "0b10000000", "0b11000000", "0b01000000",
                "0b10000000",
                "0b11000000", "0b01000000", "0b10000000", "0b11000000", "0b01000000", "0b10000000", "0b11000000",
                "0b01000000",
            ],
            3: [
                "0b001000000000", "0b010000000000", "0b100000000000", "0b011000000000", "0b110000000000",
                "0b111000000000", "0b101000000000", "0b001000000000",
                "0b010000000000", "0b100000000000", "0b011000000000", "0b110000000000", "0b111000000000",
                "0b101000000000", "0b001000000000", "0b010000000000",
            ],
            4: [
                "0x1000", "0x2000", "0x4000", "0x8000", "0x3000", "0x6000", "0xc000", "0xb000",
                "0x5000", "0xa000", "0x7000", "0xe000", "0xf000", "0xd000", "0x9000", "0x1000",
            ],
            8: {
                4: [
                    "0x01000000", "0x02000000", "0x04000000", "0x08000000", "0x10000000", "0x20000000", "0x40000000",
                    "0x80000000", "0x1B000000", "0x36000000", "0x36000000", "0x6C000000", "0xD8000000", "0xAB000000",
                    "0x4D000000",
                    "0x9A000000"
                ],
                3: [
                    "0x010000", "0x020000", "0x040000", "0x080000", "0x100000", "0x200000", "0x400000",
                    "0x800000", "0x1B0000", "0x360000", "0x360000", "0x6C0000", "0xD80000", "0xAB0000", "0x4D0000",
                    "0x9A0000"
                ],
                2: [
                    "0x0100", "0x0200", "0x0400", "0x0800", "0x1000", "0x2000", "0x4000",
                    "0x8000", "0x1B00", "0x3600", "0x3600", "0x6C00", "0xD800", "0xAB00", "0x4D00",
                    "0x9A00"
                ]
            }
        }

        # In function of (wordsize, statesize)
        self.AES_matrix = {
            (2, 2): [[0x02, 0x03], [0x03, 0x02]],
            (3, 2): [[0x02, 0x03], [0x03, 0x02]],
            (4, 2): [[0x02, 0x03], [0x03, 0x02]],
            (8, 2): [[0x02, 0x03], [0x03, 0x02]],
            (2, 3): [[0x01, 0x02, 0x02], [0x02, 0x01, 0x02], [0x02, 0x02, 0x01]],
            (3, 3): [[0x01, 0x02, 0x05], [0x05, 0x06, 0x05], [0x05, 0x05, 0x01]],
            (4, 3): [[0x08, 0x03, 0x04], [0x0a, 0x06, 0x09], [0x03, 0x04, 0x0c]],
            (8, 3): [[0x01, 0x02, 0x05], [0x05, 0x06, 0x05], [0x05, 0x05, 0x01]],
            (2, 4): [[0x02, 0x03, 0x01, 0x01], [0x01, 0x02, 0x03, 0x01], [0x01, 0x01, 0x02, 0x03],
                     [0x03, 0x01, 0x01, 0x02]],
            (3, 4): [[0x01, 0x07, 0x05, 0x05], [0x07, 0x02, 0x01, 0x03], [0x06, 0x03, 0x01, 0x02],
                     [0x07, 0x05, 0x05, 0x07]],
            (4, 4): [[0x02, 0x03, 0x01, 0x01], [0x01, 0x02, 0x03, 0x01], [0x01, 0x01, 0x02, 0x03],
                     [0x03, 0x01, 0x01, 0x02]],
            (8, 4): [[0x02, 0x03, 0x01, 0x01], [0x01, 0x02, 0x03, 0x01], [0x01, 0x01, 0x02, 0x03],
                     [0x03, 0x01, 0x01, 0x02]]
        }

        # In function of wordsize
        self.irreducible_polynomial = {
            2: 0x7,
            3: 0xb,
            4: 0x13,
            8: 0x11b,
        }

        # In function of wordsize
        self.AES_matrix_description = {
            2: [self.AES_matrix[(word_size, state_size)], self.irreducible_polynomial[word_size], word_size],
            3: [self.AES_matrix[(word_size, state_size)], self.irreducible_polynomial[word_size], word_size],
            4: [self.AES_matrix[(word_size, state_size)], self.irreducible_polynomial[word_size], word_size],
            8: [self.AES_matrix[(word_size, state_size)], self.irreducible_polynomial[word_size], word_size],
        }

        # In function of statesize
        self.number_of_components_per_round = {
            2: 15,
            3: 24,
            4: 35,
        }

        # Rounds definition:
        # Round 0 different from others since it starts with first_add_round_key
        self.add_round()
        first_add_round_key = self.add_XOR_component([INPUT_KEY, INPUT_PLAINTEXT],
                                                     [[i for i in range(self.CIPHER_BLOCK_SIZE)],
                                                      [i for i in range(self.CIPHER_BLOCK_SIZE)]],
                                                     int(self.CIPHER_BLOCK_SIZE))
        add_round_key = None
        # key_updated = None
        remaining_xors = None
        xor1 = None
        xor2 = None
        
        for round_number in range(number_of_rounds):
            sboxes_components = self.create_sbox_components(add_round_key, first_add_round_key, round_number, word_size)
            shift_row_components = self.create_shift_row_components(sboxes_components, word_size)
            mix_column_components = self.create_mix_column_components(round_number, shift_row_components, word_size)
            key_rotation = self.create_rotate_component(remaining_xors, round_number, word_size)
            key_sboxes_components = self.create_key_sbox_components(key_rotation, word_size)
            constant = self.create_constant_component(round_number, state_size, word_size)
            remaining_xors, xor1 = self.create_xor_components(constant, key_sboxes_components,
                                                              remaining_xors, xor1, round_number)
            self.add_intermediate_output_component([remaining_xors[i].id for i in range(self.NUM_ROWS)],
                                                   [[i for i in range(self.ROW_SIZE)] for _ in range(self.NUM_ROWS)],
                                                   self.KEY_BLOCK_SIZE,
                                                   "round_key_output")
            add_round_key = self.create_round_key(mix_column_components, remaining_xors,
                                                  round_number, shift_row_components)
            self.create_round_output_component(add_round_key, number_of_rounds, round_number)

    def create_sbox_components(self, add_round_key, first_add_round_key, round_number, word_size):
        if word_size != 8 :
            raise ValueError("word_size incorrect (should be 8)")
        sboxes_components = []
        for j in range(self.NUM_SBOXES * 2):
            if round_number == 0:
                sbox = self.add_SBOX_component(
                    [first_add_round_key.id],
                    [[i for i in range(j * self.SBOX_BIT_SIZE, (j + 1) * self.SBOX_BIT_SIZE)]],
                    self.SBOX_BIT_SIZE, self.sbox)
            else:
                sbox = self.add_SBOX_component(
                    [add_round_key.id],
                    [[i for i in range(j * self.SBOX_BIT_SIZE, (j + 1) * self.SBOX_BIT_SIZE)]],
                    self.SBOX_BIT_SIZE, self.sbox)
            sboxes_components.append(sbox)

        return sboxes_components

    def create_shift_row_components(self, sboxes_components, word_size):
        sbox_order = []
        for group in range(4):
            start =  2 * group
            current_group = []
            for sub in range(4):
                subgroup_start = start + 8 * sub
                current_group.extend([subgroup_start + i for i in range(2)])
            sbox_order.append(current_group)

        # print(sbox_order)

        shift_row_components = []
        for j in range(self.NUM_ROWS):
            rotation = self.add_rotate_component(
                [sboxes_components[sbox_order[j][i]].id for i in range(8)],
                [[i for i in range(self.SBOX_BIT_SIZE)] for _ in range(self.NUM_ROWS * 2)],
                self.ROW_SIZE,
                -word_size * j)
            shift_row_components.append(rotation)

        return shift_row_components

    def create_mix_column_components(self, round_number, shift_row_components, word_size):
        mix_column_components = []
        if round_number != self.NROUNDS - 1:
            for j in range(self.NUM_ROWS):
                mix_column = self.add_mix_column_component(
                    [shift_row_components[i].id for i in range(self.NUM_ROWS)],
                    [[i for i in range(j * self.SBOX_BIT_SIZE*2, (j + 1) * self.SBOX_BIT_SIZE*2)] for _ in
                     range(self.NUM_ROWS)],
                    self.ROW_SIZE,
                    self.AES_matrix_description[word_size])
                mix_column_components.append(mix_column)

        return mix_column_components
    
    def create_key_permutation(self, key_updated_old,round_number,word_size):
        if word_size != 8: 
            raise ValueError("word_size incorrect (should be 8)")
        permutation_order = []
        for i in range(16):
            tmp = [j+self.permutation_box[i]*8 for j in range(8)]
            permutation_order = permutation_order + tmp

        # print(permutation_order)

        if round_number == 0:
            key_updated = self.add_permutation_component([INPUT_KEY],[[i for i in range(self.KEY_BLOCK_SIZE)]],
                                                         self.KEY_BLOCK_SIZE,
                                                         permutation_order)
        else:
            key_updated = self.add_permutation_component([key_updated_old.id],[[i for i in range(self.KEY_BLOCK_SIZE)]],
                                                         self.KEY_BLOCK_SIZE,
                                                         permutation_order)
        return key_updated


    def create_rotate_component(self, remaining_xors, round_number, word_size):
        if round_number == 0:
            key_rotation = self.add_rotate_component(
                [INPUT_KEY],
                [[i for i in range(self.KEY_BLOCK_SIZE - self.ROW_SIZE, self.KEY_BLOCK_SIZE)]],
                self.ROW_SIZE,
                -word_size)
        else:
            key_rotation = self.add_rotate_component(
                [remaining_xors[-1].id],
                [[i for i in range(self.ROW_SIZE)]],
                self.ROW_SIZE,
                -word_size)

        return key_rotation

    def create_key_sbox_components(self, key_rotation, word_size):
        if word_size != 8:
            raise ValueError("word_size incorrect (should be 8)")
        key_sboxes_components = []
        for i in range(8):
            key_sub = self.add_SBOX_component(
                [key_rotation.id],
                [[j for j in range(i * self.SBOX_BIT_SIZE, (i + 1) * self.SBOX_BIT_SIZE)]],
                self.SBOX_BIT_SIZE,
                self.sbox)
            key_sboxes_components.append(key_sub)

        return key_sboxes_components

    def create_constant_component(self, round_number, state_size, word_size):
        if word_size != 8:
            if self.ROUND_CONSTANT[word_size][round_number][:2] == '0b':
                constant = self.add_constant_component(len(self.ROUND_CONSTANT[word_size][round_number]) - 2,
                                                       int(self.ROUND_CONSTANT[word_size][round_number], 2))
            elif self.ROUND_CONSTANT[word_size][round_number][:2] == '0x':
                constant = self.add_constant_component(self.ROW_SIZE,
                                                       int(self.ROUND_CONSTANT[word_size][round_number], 16))
            else:
                print("Error : Constant format")
        else:
            constant = self.add_constant_component(self.ROW_SIZE,
                                                   int(self.ROUND_CONSTANT[word_size][state_size][round_number],
                                                       16))

        return constant

    def create_xor_components(self, constant, key_sboxes_components, remaining_xors, xor1, round_number, successor=False):

        # if self.KEY_BLOCK_SIZE == 256 and successor == True:
        #     if round_number == 0: 
        #         xor1 = self.add_XOR_component(
        #         [key_sboxes_components[i].id for i in range(self.NUM_ROWS)] + [INPUT_KEY],
        #         [[i for i in range(self.SBOX_BIT_SIZE)] for _ in range(4)]+[[i for i in range(128,160)]],
        #         self.ROW_SIZE)
        #     else :
        #         xor1 = self.add_XOR_component(
        #         [key_sboxes_components[i].id for i in range(self.NUM_ROWS)] + [xor1.id],
        #         [[i for i in range(self.SBOX_BIT_SIZE)] for _ in range(4)]+[[i for i in range(self.ROW_SIZE)]],
        #         self.ROW_SIZE)
        # else :
        xor_tmp = self.add_XOR_component(
        [key_sboxes_components[i].id for i in range(self.NUM_ROWS*2)] + [constant.id],
        [[i for i in range(self.SBOX_BIT_SIZE)] for _ in range(self.NUM_ROWS*2)] + [[i for i in range(self.ROW_SIZE)]],
        self.ROW_SIZE).id
        if round_number == 0:
                xor1 = self.add_XOR_component(
                [xor_tmp, INPUT_KEY],
                [[i for i in range(self.ROW_SIZE)] for _ in range(2)],
                self.ROW_SIZE)
        else:
                xor1 = self.add_XOR_component(
                [xor_tmp, xor1.id],
                [[i for i in range(self.ROW_SIZE)] for _ in range(2)],
                self.ROW_SIZE)
        tmp_remaining_xors = [xor1]

        if self.KEY_BLOCK_SIZE == 192:
            key_columns_begin = 0
            key_columns_end  = 6
        elif self.KEY_BLOCK_SIZE == 256 and successor == False:
            key_columns_begin = 0
            key_columns_end  = 4
        elif self.KEY_BLOCK_SIZE == 256 and successor == True:
            key_columns_begin = 4
            key_columns_end = 8
        else:
            key_columns_begin = 0
            key_columns_end = self.NUM_ROWS

        for i in range(key_columns_begin,key_columns_end - 1):
            if i < 4: 
                tmpi = i
            else :
                tmpi = i-4 
            if round_number == 0:
                # if i <4:
                    xor = self.add_XOR_component(
                    [tmp_remaining_xors[tmpi].id, INPUT_KEY],
                    [[i for i in range(self.ROW_SIZE)],
                     [i for i in range((i + 1) * self.ROW_SIZE, (i + 2) * self.ROW_SIZE)]],
                    self.ROW_SIZE)
                # else:
                #     xor = self.add_XOR_component(
                #     [tmp_remaining_xors[tmpi].id]+[INPUT_KEY],
                #     [[i for i in range(self.ROW_SIZE)]]+[
                #     [i for i in range((i + 1) * self.ROW_SIZE, (i + 2) * self.ROW_SIZE)]],
                #     self.ROW_SIZE)
            else:
                xor = self.add_XOR_component(
                    [tmp_remaining_xors[tmpi].id, remaining_xors[i + 1].id],
                    [[i for i in range(self.ROW_SIZE)], [i for i in range(self.ROW_SIZE)]],
                    self.ROW_SIZE)
            
            # if self.KEY_BLOCK_SIZE == 256 and successor == True:
            #     tmp_remaining_xors_256.append(xor)
            tmp_remaining_xors.append(xor)
        
        remaining_xors = list(tmp_remaining_xors)
        
        # if successor == True:
        return remaining_xors, remaining_xors[0]
        # else:
        #     return remaining_xors, xor1

    def create_round_key(self, mix_column_components, remaining_xors, round_number, shift_row_components):
        if round_number != self.NROUNDS - 1:
            add_round_key = self.add_XOR_component(
                [mix_column_components[i].id for i in range(self.NUM_ROWS)] + [remaining_xors[i].id for i in
                                                                               range(self.NUM_ROWS)],
                [[i for i in range(self.ROW_SIZE)] for _ in range(2 * self.NUM_ROWS)],
                self.CIPHER_BLOCK_SIZE)
        else:
            
            shift_rows_ids = []
            for i in range(self.NUM_ROWS):
                shift_rows_ids.extend([shift_row_components[j].id for j in range(self.NUM_ROWS)])
            shift_rows_input_position_lists = []
            for i in range(self.NUM_ROWS):
                shift_rows_input_position_lists.extend(
                    [[j for j in range(i * self.SBOX_BIT_SIZE*2, (i + 1) * self.SBOX_BIT_SIZE*2)] for _ in
                     range(self.NUM_ROWS)])
            add_round_key = self.add_XOR_component(
                shift_rows_ids + [remaining_xors[i].id for i in range(self.NUM_ROWS)],
                shift_rows_input_position_lists + [[i for i in range(self.ROW_SIZE)] for _ in range(self.NUM_ROWS)],
                self.CIPHER_BLOCK_SIZE)


        return add_round_key

    def create_round_output_component(self, add_round_key, number_of_rounds, round_number):
        self.add_intermediate_output_component([add_round_key.id],
                                                   [[i for i in range(self.CIPHER_BLOCK_SIZE)]],
                                                   self.CIPHER_BLOCK_SIZE,
                                                   "round_output")
        if round_number == number_of_rounds - 1:
            self.add_cipher_output_component([add_round_key.id],
                                             [[i for i in range(self.CIPHER_BLOCK_SIZE)]],
                                             self.CIPHER_BLOCK_SIZE)
        else:
            self.add_round()
