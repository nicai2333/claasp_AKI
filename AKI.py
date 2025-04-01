import random
import secrets
import numpy as np
import math as math
import claasp
from enum import Enum
from operator import xor
from copy import deepcopy
from claasp.cipher import Cipher
from claasp import editor 
from claasp.cipher_modules.inverse_cipher import *
from sympy import Matrix, GF,zeros,ones
from sympy.abc import x

# 生成加密安全的128位无符号整数
def generate_random_number(size):
    random_bytes = secrets.token_bytes(size//8)
    return int.from_bytes(random_bytes, byteorder='big')

def bitwise_xor(a, b):
    return (a | b) - (a & b)

def listswap(x0,pos1,pos2):
    tmp = x0[pos2]
    x0[pos2] = x0[pos1]
    x0[pos1] = tmp

def find_zero_matrix(matrix,number_of_cols):
    rows = matrix.rows
    cols = matrix.cols
    for i in range(rows):
        mat = matrix[i:rows,0:cols-number_of_cols+1]
        if mat.is_zero_matrix :
            return i
        
def is_zero_col(matrix,col):
    rows = matrix.rows
    cols = matrix.cols
    flag = True
    for i in range(rows):
        if matrix(i,col)!=0:
            flag = False
    return flag

def partial_gauss_eliminate(mat1,cols=None):
    """对矩阵 `mat` 的指定列 `cols` 进行高斯消元（行阶梯形，非简化行阶梯形）。
    
    参数:
        mat (Matrix): 输入矩阵。
        cols (list, optional): 需要消元的列索引列表（默认处理所有列）。
        
    返回:
        Matrix: 部分高斯消元后的矩阵。
    """
    if cols is None:
        cols = list(range(mat1.cols))
    
    aug = mat1.copy()
    n = mat1.rows  # 行数
    
    for col in cols:
        # 寻找主元行（从当前行 `col` 开始）
        pivot_row = None
        for r in range(col, n):
            if aug[r, col] != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue  # 该列为自由变量，跳过
        
        # 交换主元行到当前行 `col`
        aug.row_swap(col,pivot_row)
        
        # 归一化主元行（将主元位置变为1）
        pivot_val = aug[col, col]
        inv_pivot = pivot_val ** (-1) if pivot_val != 0 else 1
        aug.row_op(col, lambda v,j: inv_pivot*aug[col,j])
        
        # 消去其他行在该列的非零元素
        for r in range(n):
            if r != col and aug[r, col] != 0:
                factor = aug[r, col]
                # aug.elementary_row_op('n->n+km',r,-1*factor,col)
                aug.row_op(r,lambda v, j:v-factor*aug[col,j])
                
    return aug

def matrix_namelist_col_swap(matrix,namelist,target_derived,partial_cols,num,col):
    target_derived.append(namelist[col])
    matrix.col_swap(col,len(partial_cols)-1)
    listswap(namelist,col,len(partial_cols)-1)
    if num == 1:
        partial_cols = partial_cols[:-1]
    elif num == 2 :
        target_derived.append('S'+namelist[col])
        tmpcol = namelist.index('S'+namelist[col])
        matrix.col_swap(tmpcol,len(partial_cols)-2)
        listswap(namelist,tmpcol,len(partial_cols)-2)
        partial_cols = partial_cols[:-2]

class AKI:

    """
    INPUT:

    - ``cipher`` -- the cipher to be computed, define the number of the round in advance
    - ``word_size`` -- the word_size of the cipher
    - ``number_of_rounds`` -- **integer**  The number of rounds where the intermediate status value resides 
    - ``the_position`` -- **integer** The position of the intermediate status value in the round

    sage: from claasp.ciphers.block_ciphers.aes_block_cipher import AESBlockCipher
    sage: from claasp.cipher_modules.statistical_tests.AKI import AKI
    sage: path = AKI(AESBlockCipher(number_of_rounds=2))
    sage: target = path.computate_path_generate(the_position=127,word_size=8)
    sage: target
    ['K_0_0', 'K_0_5', 'K_0_10', 'K_0_15']
    sage: key_path, AKI_res = path.actual_key_information(computate_path=target,word_size=8)
    sage: AKI_res
    5
    sage: key_path
    ['K_0_0', 'K_0_5', 'K_0_10', 'K_0_15']

    sage: from claasp.ciphers.block_ciphers.aes_block_cipher import PresentBlockCipher
    sage: from claasp.cipher_modules.statistical_tests.AKI import AKI
    sage: path = AKI(PresentBlockCipher(number_of_rounds=5))
    sage: target = path.computate_path_generate(the_position=63,word_size=1)
    sage: key_path, AKI_res = path.actual_key_information(computate_path=target,word_size=1)
    
   
    Since the short round aes in claasp is composed of the whitening key XOR and
    the last round of encryption without mixcolumns, the difference on one byte in the aes_inverse propagates one more round
    """    
    
    def __init__(self, cipher):
        self.cipher = cipher
        str_of_inputs_bit_size = list(map(str, cipher.inputs_bit_size))
        self._cipher_primitive = cipher.id + "_" + "_".join(str_of_inputs_bit_size)
        self.matrix=[]
        self.namelist = []

    def computate_path_generate(self, the_position, word_size, cipher_type=1):
        """
        According function, the differential's diffusion path in backward 

        INPUT:

        ``the_position`` --- the bit that differential exist
        ``word_size`` --- the word_size of the cipher 
        """

        if(self.cipher.inputs[0]=='plaintext') :
            block_size=self.cipher.inputs_bit_size[0]
            key_size = self.cipher.inputs_bit_size[1]
        else :
            block_size=self.cipher.inputs_bit_size[1]
            key_size = self.cipher.inputs_bit_size[0]
        
        KEY = [0]

        zero_block_size = 0
        mask = 1 << the_position
        begin = zero_block_size | mask
        cipher_inv = self.cipher.cipher_inverse()
        cipher_inv_no_ksa = cipher_inv.remove_key_schedule()
        cipher_output_index=0
        for i in cipher_inv_no_ksa.inputs:
            if i.split('_')[0]=='cipher':
                cipher_output_index = cipher_inv_no_ksa.inputs.index(i)
                break
        
        if (cipher_output_index==0): 
            num_sub_key = len(cipher_inv_no_ksa.inputs)-1
            result1=cipher_inv_no_ksa.evaluate([zero_block_size]+KEY*num_sub_key,intermediate_output=True)
            result2=cipher_inv_no_ksa.evaluate([begin]+KEY*num_sub_key,intermediate_output=True)
        else:
            num_sub_key = len(cipher_inv_no_ksa.inputs)-1
            result1=cipher_inv_no_ksa.evaluate(KEY*num_sub_key+[zero_block_size],intermediate_output=True)
            result2=cipher_inv_no_ksa.evaluate(KEY*num_sub_key+[begin],intermediate_output=True)
        xor_result = []
        
        if ('round_output' in result1[1]):
            num_of_rounds_output = len(result1[1]['round_output'])
            for i in range(num_of_rounds_output):
                if i == 0 : continue
                temp = bitwise_xor (result1[1]['round_output'][i],result2[1]['round_output'][i])
                xor_result.append(temp)
            xor_result.append(bitwise_xor (result1[1]['plaintext'][0],result2[1]['plaintext'][0]))

        if xor_result==[]:
            return []

        binary_res = []
        for num in xor_result:
            binary_res.append( format(num, '0%db' %(block_size)))

        fin_result = []
        for j in range(len(binary_res)):
            for i in range(0, len(binary_res[j]), word_size):
                if ((binary_res[j][i:i+word_size])!='0'*word_size):
                    fin_result.append('K_%d_%d' %(len(binary_res)-j-1,i//word_size))
        
        return fin_result
    
    def actual_key_information(self, computate_path, word_size):

        KSA = self.cipher.key_schedule_algorithm()
        key_size = self.cipher.output_bit_size
        mask = (1<<128)-1
        key_path = []

        if computate_path == []: return [], 0

        current_round = int(computate_path[0].split('_')[-2])
        is_the_same_in_rounds = False
        for c in computate_path:

            tmp_round = int(c.split('_')[-2])
            if tmp_round == 0:
                if c not in key_path:
                    key_path.append(c)
                continue
            if tmp_round !=current_round: 
                current_round=tmp_round
                is_the_same_in_rounds=False
            else:
                is_the_same_in_rounds = True

            if is_the_same_in_rounds == False or c == computate_path[0]:
                KSA_reduced = KSA.reduce_key_schedule_algorithm_rounds(current_round)
                KSA_inv = KSA_reduced.key_schedule_inverse()
                if word_size >1:
                    KSA_inv_cor = KSA_inv.correlated_key_schedule('word')
                else:
                    KSA_inv_cor = KSA_inv.correlated_key_schedule('bit')
        
        #每个compute_path的元素都加密一遍，流程还能进一步优化
            original_key = 0 
            if word_size >1:
                pos = key_size - int(c.split('_')[-1])*word_size-1
                key = (original_key | (1<<pos)) & mask
            else :
                pos = key_size - int(c.split('_')[-1])-1
                key = (original_key | (1<<pos)) & mask

            cipher_text = KSA_inv_cor.evaluate([key])
            binary_res=( format(cipher_text, '0%db' %(key_size)))

            for j in range(0, len(binary_res), (word_size)):
                if ((binary_res[j:j+word_size])!='0'*word_size):
                    ele = 'K_0_%d' %(j//word_size)
                    if ele in key_path:
                        continue
                    else:
                        key_path.append(ele)

        AKI_res = len(key_path)
        return key_path,AKI_res

    def judge_situation_in_row(self,matrix,namelist,num_partial_col,row):
        """
        To judge the situation after guass elimination in a row,
        which include a row only have an non-zero variable x ,
        and a row have two non-zero variable x and S(x).

        INPUT:

        ``matrix`` --- the matrix after guass elimination
        ``namelist`` --- the namelist of the matrix, which swap the element the same as the swap of the matrix's cols
        ``num_partial_col`` --- the number of the elements which going to be derived
        ``row`` --- the row which is waiting to be judge  
        """
        if (matrix[row,row]!=0) :
            flag1 = True
            flag2 = False
            for j in range(row+1,num_partial_col):
                if matrix[row,j] != 0:
                    flag2 = True
                    flag1 = False
                    if 'S'+namelist[row] == namelist[j]:  
                        for k in range (j+1,num_partial_col):
                            if matrix[row,k]!=0 :
                                flag2 = False
                                break
                        if flag2 == True:
                            return row,j
                    else: break
            if flag1 == True : return row,row
        return None,None

    def judge_situation_in_rows(self,matrix,namelist,num_partial_col,row):
        """
        To judge the situation after guass elimination in 2 rows, 
        whether the variables x and S(x) are both pivot element

        INPUT:

        ``matrix`` --- the matrix after guass elimination
        ``namelist`` --- the namelist of the matrix, which swap the element the same as the swap of the matrix's cols
        ``num_partial_col`` --- the number of the elements which going to be derived
        """
        if matrix.rows > num_partial_col:
            long = matrix.rows
            short = num_partial_col
        else :
            long = num_partial_col
            short = matrix.rows

        i = row
        if matrix[i,i]==0 :return None,None
        for j in range(i+1,short):
            if (matrix[j,j]!=0) :
                if('S'+namelist[i]==namelist[j]): 
                    c = matrix[i,i]/matrix[j,j]
                    flag = True
                    for k in range(i+1,j):
                        if matrix[i,k] != 0 or matrix[j,k] != 0:
                            flag = False
                    for k in range(j+1,num_partial_col):
                        if matrix[i,k] != c*matrix[j,k]:
                            flag = False
                    if flag == True :return i,j
        return None,None
            

    def knowledge_propagation(self,target,word_size,key_size):   
        """
        According Key schedule, devired elements which are related to target elements.

        INPUT:

        ``target`` --- the target elements 
        ``word_size`` --- the words size of the Key schedule
        ``key_size`` --- the size of the key
        """

        number_of_round = int(target[0][2])
        number_of_word = key_size // word_size
        matrix = zeros(number_of_round*number_of_word,2*(number_of_round+1)*number_of_word)
        namelist = []
        for i in range(number_of_round+1):
            for j in range(number_of_word):
                namelist.append('K_%d_%d' %(i,j))           #for aes
                # print(namelist)
                if i>=1:
                    if j % 4 ==0 :
                        if ('K_%d_%d' %(i,j)) in target:
                            target.append('K_%d_%d' %(i-1,j))
                            target.append('SK_%d_%d' %(i-1,(j+7)%16))
                        matrix[(i-1)*number_of_word+j,i*number_of_word+j] = 1 
                        matrix[(i-1)*number_of_word+j,(i-1)*number_of_word+j]=1
                        matrix[(i-1)*number_of_word+j,(i-1)*number_of_word+(j+7)%16+(number_of_round+1)*number_of_word]=1
                    else:
                        if ('K_%d_%d' %(i,j)) in target:
                            target.append('K_%d_%d' %(i-1,j))
                            target.append('SK_%d_%d' %(i,j-1))
                        matrix[(i-1)*number_of_word+j,i*number_of_word+j]=1
                        matrix[(i-1)*number_of_word+j,(i-1)*number_of_word+j]=1
                        matrix[(i-1)*number_of_word+j,i*number_of_word+j-1]=1
        for i in range(number_of_round+1):
            for j in range(number_of_word):
                namelist.append('SK_%d_%d' %(i,j))
        
        for i in range(len(target)):
            target_i = target[i]
            target.append('S'+target[i])
            posi=namelist.index(target_i)
            pos_si = namelist.index('S'+target_i)
            matrix.col_swap(posi,2*(number_of_round+1)*number_of_word-2*i-1)
            listswap(namelist,posi,2*(number_of_round+1)*number_of_word-2*i-1)
            matrix.col_swap(pos_si,2*(number_of_round+1)*number_of_word-2*i-2)
            listswap(namelist,pos_si,2*(number_of_round+1)*number_of_word-2*i-2)
        
        target_derived = target.copy()
        partial_cols = [i for i in range(2*(number_of_round+1)*number_of_word - len(target_derived))]

        for i in range(matrix.rows):
                x,y=self.judge_situation_in_row(matrix,namelist,len(partial_cols),i)
                # print(x,y)
                if (x==i and y ==i and 'S'+namelist[i] not in target_derived) or (x==i and x!=y):
                    Flag = True
                    matrix_namelist_col_swap(matrix,namelist,target_derived,partial_cols,2,i)

                elif x==i and y==i and 'S'+namelist[i] in target_derived:
                    Flag = True
                    matrix_namelist_col_swap(matrix,namelist,target_derived,partial_cols,1,i)
                    

        for i in range(matrix.rows):
                x,y = self.judge_situation_in_rows(matrix,namelist,len(partial_cols),i)
                if x!=y:
                    Flag = True
                    matrix_namelist_col_swap(matrix,namelist,target_derived,partial_cols,2,i)
                    

        Flag = True
        while Flag == True:
            Flag = False
            matrix = partial_gauss_eliminate(matrix,partial_cols)
            # print(namelist)
            for i in range(matrix.rows):
                for j in range(matrix.cols-len(partial_cols)):
                    # print(len(partial_cols))
                    x,y=self.judge_situation_in_row(matrix,namelist,len(partial_cols),i)
                    # print(x,y)

                    if (x==i and y ==i and 'S'+namelist[i] not in target_derived) or (x==i and x!=y):
                        Flag = True
                        matrix_namelist_col_swap(matrix,namelist,target_derived,partial_cols,2,i)

                    elif x==i and y==i and 'S'+namelist[i] in target_derived:
                        Flag = True
                        matrix_namelist_col_swap(matrix,namelist,target_derived,partial_cols,1,i)
            
            for i in range(matrix.rows):
                x,y = self.judge_situation_in_rows(matrix,namelist,len(partial_cols),i)
                if x!=y:
                    Flag = True
                    matrix_namelist_col_swap(matrix,namelist,target_derived,partial_cols,2,i)
        
        print(target_derived)
        return target_derived, matrix,namelist,target
    
    def relation_derivation(self,target,target_derived,matrix,namelist):
        """
        Return the relation between the target elements and the derived target elements 

        INPUT:

        ``target`` --- the original target elements 
        ``target_derived`` --- the elements which are derived from target elements 
        ``matrix`` --- the matrix after guass elimination
        ``namelist`` --- the namelist of the matrix, which swap the element the same as the swap of the matrix's cols
        """
        rows = matrix.rows
        cols = matrix.cols
        zeros_rows=find_zero_matrix(matrix,len(target_derived))
        rel_matrix = matrix[zeros_rows:rows,cols-len(target_derived):cols]
        rel_namelist = namelist[cols-len(target_derived):cols]
        rel_cols = rel_matrix.cols
        rel_rows = rel_matrix.rows

        partial_cols = [i for i in range(len(target_derived)-len(target))]

        for i in range(len(target)):
            index = rel_namelist.index(target[i])
            rel_matrix.col_swap(index,rel_cols-i)
            listswap(rel_namelist,index,rel_cols-i)
        
        Flag = True
        while Flag == True :
            Flag = False
            rel_matrix=partial_gauss_eliminate(rel_matrix,partial_cols)
            addition_lin_relation = 0
            for i in range(rel_rows):
                x,y = self.judge_situation_in_row(rel_matrix,rel_namelist,len(partial_cols),i)
                if x==i and y ==i :
                    Flag = True
                    lin_relation = True
                    if is_zero_col(rel_matrix,i):
                        addition_lin_relation+=1
                        rel_namelist.append('S_-1_alr%d' %addition_lin_relation)
                        rel_namelist.append('S_-1_%d_%d' %(rel_namelist[i][3],rel_namelist[i][5]))
                        V = Matrix.zeros(rel_rows,2)
                        W = Matrix.zeros(1,rel_cols+1)
                        rel_matrix = rel_matrix.col_insert(rel_cols,V)
                        rel_matrix = rel_matrix.row_insert(rel_rows,W)
                        rel_rows = rel_matrix.rows
                        rel_cols = rel_matrix.cols

                        rel_matrix[rel_rows-1,rel_cols-1]=1
                        rel_matrix[rel_rows-1,rel_cols-2]=1

                        target.append('S_-1_alr%d' %addition_lin_relation)
                        target_derived.append('S_-1_alr%d' %addition_lin_relation)
                    else:
                        addition_lin_relation+=1
                        rel_namelist.append('S_1_alr%d' %addition_lin_relation)
                        V = Matrix.zeros(rel_rows,1)
                        W = Matrix.zeros(1,rel_cols+1)
                        rel_matrix = rel_matrix.col_insert(rel_cols,V)
                        rel_matrix = rel_matrix.row_insert(rel_rows,W)
                        rel_rows = rel_matrix.rows
                        rel_cols = rel_matrix.cols

                        rel_matrix[rel_rows-1,rel_cols-1]=1
                        rel_matrix[rel_rows-1,rel_namelist.index('S'+rel_namelist[i])]=1

                        target.append('S_1_alr%d' %addition_lin_relation)
                        target_derived.append('S_1_alr%d' %addition_lin_relation)
        RelationSet = []
        rel_matrix=partial_gauss_eliminate(rel_matrix)


        zeros_rows=find_zero_matrix(rel_matrix,len(target_derived)-len(target))
        res_matrix = rel_matrix[zeros_rows:rel_rows,rel_cols-len(target_derived):rel_cols]
        res_namelist = rel_namelist[rel_cols-len(target_derived):rel_cols]
        res_cols = res_matrix.cols
        res_rows = res_matrix.rows

        for i in range(res_rows):
            for j in range(res_cols):
                tmp = []
                if res_matrix[i,j]!=0:
                    tmp.append(res_namelist[j])
            RelationSet.append(tmp)
        
        return RelationSet
                





                    


                

