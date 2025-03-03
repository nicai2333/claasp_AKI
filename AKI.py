import random
import secrets
import numpy as np
import math as math
from enum import Enum
from operator import xor
from copy import deepcopy
from claasp.cipher import Cipher
from claasp import editor 

# 生成加密安全的128位无符号整数
def generate_random_number(size):
    random_bytes = secrets.token_bytes(size//8)
    return int.from_bytes(random_bytes, byteorder='big')

def bitwise_xor(a, b):
    return (a | b) - (a & b)

class AKI:

    """
    INPUT:

    - ``cipher`` -- the cipher to be computed, define the number of the round in advance
    - ``word_size`` -- the word_size of the cipher
    - ``number_of_rounds`` -- **integer**  The number of rounds where the intermediate status value resides 
    - ``the_position`` -- **integer** The position of the intermediate status value in the round

    sage: from claasp.ciphers.block_ciphers.speck_block_cipher import SpeckBlockCipher
    sage: from claasp.cipher_modules.statistical_tests.AKI import AKI
    sage: path = AKI(SpeckBlockCipher(number_of_rounds=3))
    sage: result = path.computate_path_generate(the_position=3,word_size=16)

    sage: from claasp.ciphers.block_ciphers.aes_block_cipher import AESBlockCipher
    sage: from claasp.cipher_modules.statistical_tests.AKI import AKI
    sage: path = AKI(AESBlockCipher(number_of_rounds=3))
    sage: path.computate_path_generate(the_position=127,word_size=8)

    Since the short round aes in claasp is composed of the whitening key XOR and
    the last round of encryption without mixcolumns, the difference on one byte in the aes_inverse propagates one more round


    """    
    
    def __init__(self, cipher):
        self.cipher = cipher
        str_of_inputs_bit_size = list(map(str, cipher.inputs_bit_size))
        self._cipher_primitive = cipher.id + "_" + "_".join(str_of_inputs_bit_size)

    def computate_path_generate(self, the_position, word_size):

        if(self.cipher.inputs[0]=='plaintext') :
            block_size=self.cipher.inputs_bit_size[0]
            key_size = self.cipher.inputs_bit_size[1]
        else :
            block_size=self.cipher.inputs_bit_size[1]
            key_size = self.cipher.inputs_bit_size[0]
        
        KEY = generate_random_number(key_size)

        zero_block_size = 0
        mask = 1 << the_position
        begin = zero_block_size | mask
        cipher_inv = self.cipher.cipher_inverse()

        if (cipher_inv.inputs[1]=='key'): 
            result1=cipher_inv.evaluate([zero_block_size,KEY],intermediate_output=True)
            result2=cipher_inv.evaluate([begin,KEY],intermediate_output=True)
        else:
            result1=cipher_inv.evaluate([KEY,zero_block_size],intermediate_output=True)
            result2=cipher_inv.evaluate([KEY,begin],intermediate_output=True)
        result3 = []
        for i in range(self.cipher.number_of_rounds-1):
            temp = bitwise_xor (result1[1]['round_output'][i],result2[1]['round_output'][i])
            result3.append(temp)
        result3.append(bitwise_xor (result1[1]['plaintext'][0],result2[1]['plaintext'][0]))

        binary_list = []
        for num in result3:
            binary_list.append( format(num, '0%db' %(block_size)))

        result4 = []
        for j in range(len(binary_list)):
            for i in range(0, len(binary_list[j]), word_size):
                if ((binary_list[j][i:i+word_size])!='0'*word_size):
                    result4.append('K_%d_%d_%d' %(len(binary_list)-j-1,(i//word_size)//4,(i//word_size)%4))
        
        return result4
