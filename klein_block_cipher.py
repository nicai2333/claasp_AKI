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
from claasp.utils.utils import get_ith_word
from claasp.DTOs.component_state import ComponentState
from claasp.name_mappings import INPUT_PLAINTEXT, INPUT_KEY,KEY_SCHEDULE_ALGORITHM

input_types = [INPUT_KEY, INPUT_PLAINTEXT]
PARAMETERS_CONFIGURATION_LIST = [{'block_bit_size': 64, 'key_bit_size': 64, 'number_of_rounds': 12}]

def update_key_schedule(cipher, k, i,key_bit_size,SBOX):
        long = key_bit_size//2
        rot_k_1 = cipher.add_rotate_component([k],[list(range(long))],long,-8).id
        rot_k_2 = cipher.add_rotate_component([k],[list(range(long,key_bit_size))],long,-8).id
        xor0 = cipher.add_XOR_component([rot_k_1, rot_k_2], [list(range(long))]+[list(range(long))], long).id
        const = cipher.add_constant_component(8,i).id
        xor1 = cipher.add_XOR_component([rot_k_2,const],[list(range(16,24))]+[list(range(8))],8).id
        s0 = cipher.add_SBOX_component([xor0], [list(range(8,12))], 4, SBOX).id  #
        s1 = cipher.add_SBOX_component([xor0], [list(range(12,16))], 4, SBOX).id  #
        s2 = cipher.add_SBOX_component([xor0], [list(range(16,20))], 4, SBOX).id  #
        s3 = cipher.add_SBOX_component([xor0], [list(range(20,24))], 4, SBOX).id  #

        updated_key = cipher.add_intermediate_output_component([rot_k_2,xor1,rot_k_2,xor0,s0,s1,s2,s3,xor0],
                                                             [list(range(16)),list(range(8)),list(range(24,long)),
                                                              list(range(8)),list(range(4)),list(range(4)),
                                                                        list(range(4)),list(range(4)),list(range(24,long))], key_bit_size, 'updated_key')

        return updated_key.id

class KleinBlockCipher(Cipher):
    """
    Construct an instance of the KleinBlockCipher class.

    This class is used to store compact representations of a cipher,
    used to generate the corresponding cipher.

    INPUT:

    - ``block_bit_size`` -- **integer** (default: `64`); cipher input and output block bit size of the cipher
    - ``key_bit_size`` -- **integer** (default: `64`); cipher key bit size of the cipher, and both number of 80 and 96 are avaliable 
    - ``number_of_rounds`` -- **integer** (default: `12`); number of rounds of the cipher. When key_bit_size is 80 , the number of 
    rounds of the cipher is 16. When key_bite_size is 96, the number of rounds of the cipher is 20. 

    EXAMPLES::
        sage: from claasp.ciphers.block_ciphers.klein_block_cipher import KleinBlockCipher
        sage: klein=KleinBlockCipher()
        sage: plaintext = 0xffffffffffffffff
        sage: key = 0x0000000000000000
        sage: klein.evaluate([plaintext,key])
        14826049118395313086
        sage: hex(klein.evaluate([plaintext,key]))
        '0xcdc0b51f14722bbe'
    """

    def __init__(self, number_of_rounds=12, key_bit_size=64):
        self.block_bit_size = 64
        self.key_bit_size = key_bit_size
        self.WORD_SIZE = 4
        self.SBOX = [0x7,0x4,0xa,0x9,0x1,0xf,0xb,0x0,0xc,0x3,0x2,0x6,0x8,0xe,0xd,0x5]
                       
        super().__init__(family_name="klein",
                         cipher_type="block_cipher",
                         cipher_inputs=[INPUT_PLAINTEXT, INPUT_KEY],
                         cipher_inputs_bit_size=[self.block_bit_size, self.key_bit_size],
                         cipher_output_bit_size=self.block_bit_size)

        state = INPUT_PLAINTEXT
        key = INPUT_KEY

        if(number_of_rounds>12):
            if (key_bit_size==64): 
                raise ValueError("number_of_rounds incorrect (should be less then or equal to 12)")
            elif (key_bit_size==80 and number_of_rounds>16):   
                raise ValueError("number_of_rounds incorrect (should be less then or equal to 16)")
            elif (key_bit_size==96 and number_of_rounds>20):   
                raise ValueError("number_of_rounds incorrect (should be less then or equal to 20)")
        
        for round_i in range(1, number_of_rounds + 1):
            self.add_round()
            round_key = self.add_round_key_output_component([key], [list(range(64))], 64).id  #
            state = self.round_function(state, round_key)  
            key = self.update_key(key, round_i)
        round_key = self.add_round_key_output_component([key], [list(range(64))], 64).id
        state = self.add_XOR_component([state, round_key], [list(range(64))] + [list(range(64))], 64).id
        self.add_cipher_output_component([state], [list(range(64))], 64)

    def update_key(self, k, i):
        long = self.key_bit_size//2
        rot_k_1 = self.add_rotate_component([k],[list(range(long))],long,-8).id
        rot_k_2 = self.add_rotate_component([k],[list(range(long,self.key_bit_size))],long,-8).id
        xor0 = self.add_XOR_component([rot_k_1, rot_k_2], [list(range(long))]+[list(range(long))], long).id
        const = self.add_constant_component(8,i).id
        xor1 = self.add_XOR_component([rot_k_2,const],[list(range(16,24))]+[list(range(8))],8).id
        s0 = self.add_SBOX_component([xor0], [list(range(8,12))], 4, self.SBOX).id  #
        s1 = self.add_SBOX_component([xor0], [list(range(12,16))], 4, self.SBOX).id  #
        s2 = self.add_SBOX_component([xor0], [list(range(16,20))], 4, self.SBOX).id  #
        s3 = self.add_SBOX_component([xor0], [list(range(20,24))], 4, self.SBOX).id  #

        updated_key = self.add_intermediate_output_component([rot_k_2,xor1,rot_k_2,xor0,s0,s1,s2,s3,xor0],
                                                             [list(range(16)),list(range(8)),list(range(24,long)),
                                                              list(range(8)),list(range(4)),list(range(4)),
                                                                        list(range(4)),list(range(4)),list(range(24,long))], self.key_bit_size, 'updated_key')

        return updated_key.id

    def round_function(self, x, k):
        after_key_add = self.add_XOR_component([x, k], [list(range(64))] + [list(range(64))], 64).id
        sb_outputs = [self.add_SBOX_component([after_key_add], [list(range(i*4, (i+1)* 4))], 4,
                                              self.SBOX).id for i in range(16)]
        left_word_rotated = self.add_rotate_component(sb_outputs, [list(range(4)) for i in range(16)], 64, -16).id
        mix_columns_1 = self.add_mix_column_component([left_word_rotated],[list(range(32))],32,
                                                      [[[0x02, 0x03, 0x01, 0x01], [0x01, 0x02, 0x03, 0x01], [0x01, 0x01, 0x02, 0x03],
                     [0x03, 0x01, 0x01, 0x02]],283,8]).id
        mix_columns_2 = self.add_mix_column_component([left_word_rotated],[list(range(32,64))],32,
                                                      [[[0x02, 0x03, 0x01, 0x01], [0x01, 0x02, 0x03, 0x01], [0x01, 0x01, 0x02, 0x03],
                     [0x03, 0x01, 0x01, 0x02]],283,8]).id

        round_output = self.add_round_output_component([mix_columns_1, mix_columns_2], [list(range(32)), list(range(32))], 64).id
        return round_output
    
    def key_schedule(self,number_of_rounds=12 ):
        key = INPUT_KEY
        key_schedule_algorithm = Cipher(f"{self.id}{KEY_SCHEDULE_ALGORITHM}", f"{self.type}", 
                                        ['key'], [self.key_bit_size], self.key_bit_size)

        if(number_of_rounds>12):
            if (self.key_bit_size==64): 
                raise ValueError("number_of_rounds incorrect (should be less then or equal to 12)")
            elif (self.key_bit_size==80 and number_of_rounds>16):   
                raise ValueError("number_of_rounds incorrect (should be less then or equal to 16)")
            elif (self.key_bit_size==96 and number_of_rounds>20):   
                raise ValueError("number_of_rounds incorrect (should be less then or equal to 20)")
        
        for round_i in range(1, number_of_rounds + 1):
            key_schedule_algorithm.add_round()
            round_key = key_schedule_algorithm.add_round_key_output_component([key], [list(range(64))], 64).id  #
            key = update_key_schedule(key_schedule_algorithm,key, round_i,self.key_bit_size,self.SBOX)

        round_key = key_schedule_algorithm.add_round_key_output_component([key], [list(range(64))], 64).id
        key_schedule_algorithm.add_cipher_output_component([round_key], [list(range(64))], 64)
        return key_schedule_algorithm
    
    


