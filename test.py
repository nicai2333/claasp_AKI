
# from sympy import Matrix, GF
# from sympy.abc import x
# from sympy import Matrix

# def partial_gauss_eliminate(mat, cols=None):
#     """对矩阵 `mat` 的指定列 `cols` 进行高斯消元（行阶梯形，非简化行阶梯形）。
    
#     参数:
#         mat (Matrix): 输入矩阵。
#         cols (list, optional): 需要消元的列索引列表（默认处理所有列）。
        
#     返回:
#         Matrix: 部分高斯消元后的矩阵。
#     """
#     if cols is None:
#         cols = list(range(mat.cols))
    
#     aug = mat.copy()
#     n = mat.rows  # 行数
    
#     for col in cols:
#         # 寻找主元行（从当前行 `col` 开始）
#         pivot_row = None
#         for r in range(col, n):
#             if aug[r, col] != 0:
#                 pivot_row = r
#                 break
#         if pivot_row is None:
#             continue  # 该列为自由变量，跳过
        
#         # 交换主元行到当前行 `col`
#         aug.row_swap(col,pivot_row)
#         print(aug)
        
#         # 归一化主元行（将主元位置变为1）
#         pivot_val = aug[col, col]
#         inv_pivot = pivot_val ** (-1) if pivot_val != 0 else 1
#         print(inv_pivot)
#         aug.row_op(col, lambda v,j: inv_pivot*aug[col,j])
#         print(1)
#         print(aug)
        
#         # 消去其他行在该列的非零元素
#         for r in range(n):
#             if r != col and aug[r, col] != 0:
#                 factor = aug[r, col]
#                 # aug.elementary_row_op('n->n+km',r,-1*factor,col)
#                 aug.row_op(r,lambda v, j:v-factor*aug[col,j])
                
#     return aug

# # 原始矩阵（4x4）
# matrix = Matrix([
#     [1, 2, 3, 4,5],
#     [1,2,3,4,5],
#     [9, 11, 13, 11,19],
#     [2, 4, 8, 16,32]
# ])

# print(matrix)
# result = partial_gauss_eliminate(matrix)
# print("部分 RREF 结果（保留所有列）:")
# print(result)
# result = result.row_insert(pos=2,other=Matrix([[0,3,4,5,6]]))
# print(result)

# class NamedMatrix:
#     def __init__(self, data, rows, cols):
#         self.data = data
#         self.rows = rows
#         self.cols = cols

#     def __repr__(self):
#         return f"NamedMatrix({self.data}, rows={self.rows}, cols={self.cols})"

# # 使用示例
# matrix = [
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9]
# ]
# nm = NamedMatrix(matrix, rows=['Row1', 'Row2', 'Row3'], cols=['ColA', 'ColB', 'ColC'])
# print(nm)


# from sympy import Matrix, GF
# from sympy.abc import x
# from sympy import Matrix

# matrix = Matrix([
#     [1, 2, 3, 4, 5],
#     [1, 2, 3, 4, 5],
#     [9, 11, 13, 11, 19],
#     [2, 4, 8, 16, 32]
# ])
# matrix[0,0]=5

# from sympy import Matrix,ones

# def find_zero_submatrices(matrix):
#     rows = matrix.rows
#     cols = matrix.cols
#     zero_submatrices = []
    
#     # 遍历所有可能的子矩阵起始和结束位置
#     for start_row in range(rows-1):
#         for end_row in range(start_row + 1, rows):
#             for start_col in range(cols-1):
#                 for end_col in range(start_col + 1, cols):
#                     # 提取子矩阵
                    
#                     sub = matrix.extract([i for i in range(start_row,end_row+1)], [j for j in range(start_col,end_col+1)])
#                     # 检查是否全为零
#                     if sub.is_zero_matrix :
#                         zero_submatrices.append([start_row, end_row, start_col, end_col])
#     return zero_submatrices

# def find_zero_matrix(matrix,number_of_cols):
#     rows = matrix.rows
#     cols = matrix.cols
#     for i in range(rows):
#         mat = matrix[i:rows,0:cols-number_of_cols+1]
#         if mat.is_zero_matrix :
#             return i

# 示例矩阵
# mat = Matrix([
#     [ 1,  2,  3,  4],
#     [ 5,  6,  7,  8],
#     [ 0, 1, 1, 12],
#     [1, 1, 1, 16]
# ])

# # 查找所有全零子矩阵
# results = find_zero_submatrices(mat)
# print(results)

# # 输出结果（包含位置信息和子矩阵）
# for res in results:
#     print(f"位置: 行{res[0]}-{res[1]}, 列{res[2]}-{res[3]}")
#     print()

# x = find_zero_matrix(mat,3)
# v = Matrix([1,1,1,1])
# V = ones(1,4)
# matrix = mat.row_insert(1,V)
# print(mat)
# print(matrix)
# print(x)

# def listswap(x0,pos1,pos2):
#     tmp = x0[pos2]
#     x0[pos2] = x0[pos1]
#     x0[pos1] = tmp

# from sympy import Matrix,zeros,ones
# key_size = 128
# word_size = 8
# target = ['K_2_0','K_1_0','K_1_5','K_1_10','K_1_15']
# target_derived = target
# number_of_round = int(target_derived[0][2])
# number_of_word = key_size // word_size
# matrix = zeros(number_of_round*number_of_word,2*(number_of_round+1)*number_of_word)
# namelist = []
# for i in range(number_of_round+1):
#     for j in range(number_of_word):
#         namelist.append('K_%d_%d' %(i,j))           #for aes
#         if i>=1:
#             if j % 4 ==0 :
#                 matrix[(i-1)*number_of_word+j,i*number_of_word+j] = 1 
#                 matrix[(i-1)*number_of_word+j,(i-1)*number_of_word+j]=1
#                 matrix[(i-1)*number_of_word+j,(i-1)*number_of_word+(j+7)%16+(number_of_round+1)*number_of_word]=1
#             else:
#                 matrix[(i-1)*number_of_word+j,i*number_of_word+j]=1
#                 matrix[(i-1)*number_of_word+j,(i-1)*number_of_word+j]=1
#                 matrix[(i-1)*number_of_word+j,i*number_of_word+j-1]=1
# for i in range(number_of_round+1):
#     for j in range(number_of_word):
#         namelist.append('SK_%d_%d' %(i,j))
# # print(matrix)
# print(namelist)

# for i in range(len(target_derived)):
#     target_i = target_derived[i]
#     posi=namelist.index(target_i)
#     print(posi)
#     pos_si = namelist.index('S'+target_i)
#     print(pos_si)
#     # matrix.col_swap(posi,2*number_of_word*number_of_round-2*i)
#     print(2*(number_of_round+1)*number_of_word-2*i)
#     listswap(namelist,posi,2*(number_of_round+1)*number_of_word-2*i-1)
#     print(1)
#     # matrix.col_swap(pos_si,2*number_of_word*number_of_round-2*i-1)
#     listswap(namelist,pos_si,2*(number_of_round+1)*number_of_word-2*i-2)

# print(namelist)


from sympy import Matrix,eye,ones,zeros

# matrix = Matrix([[1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0], [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, -1], [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1], [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -2, -1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]])
# namelist = ['K_0_0', 'K_0_1', 'K_0_2', 'K_0_3', 'K_0_4', 'K_0_5', 'K_0_6', 'K_0_7', 'K_0_8', 'K_0_9', 'K_0_10', 'K_0_11', 'K_0_12', 'K_0_13', 'K_0_14', 'K_0_15', 'SK_2_13', 'K_1_1', 'K_1_2', 'K_1_3', 'K_1_4', 'K_1_5', 'K_1_6', 'K_1_7', 'K_1_8', 'K_1_9', 'K_1_10', 'K_1_11', 'K_1_12', 'K_1_13', 'K_1_14', 'K_1_15', 'SK_2_15', 'K_2_1', 'K_2_2', 'K_2_3', 'K_2_4', 'K_2_5', 'K_2_6', 'K_2_7', 'K_2_8', 'K_2_9', 'K_2_10', 'K_2_11', 'K_2_12', 'K_2_13', 'K_2_14', 'K_2_15', 'SK_0_0', 'SK_0_1', 'SK_0_2', 'SK_0_3', 'SK_0_4', 'SK_0_5', 'SK_0_6', 'SK_0_7', 'SK_0_8', 'SK_0_9', 'SK_0_10', 'SK_0_11', 'SK_0_12', 'SK_0_13', 'SK_0_14', 'SK_0_15', 'SK_2_12', 'SK_1_1', 'SK_1_2', 'SK_1_3', 'SK_1_4', 'SK_1_5', 'SK_1_6', 'SK_1_7', 'SK_1_8', 'SK_1_9', 'SK_1_10', 'SK_1_11', 'SK_1_12', 'SK_1_13', 'SK_1_14', 'SK_1_15', 'SK_2_14', 'SK_2_1', 'SK_2_2', 'SK_2_3', 'SK_2_4', 'SK_2_5', 'SK_2_6', 'SK_2_7', 'SK_2_8', 'SK_2_9', 'SK_2_10', 'SK_2_11', 'SK_1_0', 'K_1_0', 'SK_2_0', 'K_2_0']
# matrix = Matrix.zeros(2,3)
# matrix[0,0]=1
# matrix[0,2]=1
# namelist = ['K_2_0','K_1_0','SK_2_0']
# def judge_situation_in_row(matrix,namelist,num_partial_col,row):
#     if (matrix[row,row]!=0) :
#             flag1 = True
#             flag2 = False
#             for j in range(row+1,num_partial_col):
#                 if matrix[row,j] != 0:
#                     flag2 = True
#                     flag1 = False
#                     if 'S'+namelist[row] == namelist[j]:  
#                         for k in range (j+1,num_partial_col):
#                             if matrix[row,k]!=0 :
#                                 flag2 = False
#                                 break
#                         if flag2 == True:
#                             return row,j
#                     else: break
#             if flag1 == True : return row,row
#     return None,None

# for i in range(5):
#     x,y = judge_situation_in_row(matrix,namelist,48,i)
#     print(x)
#     print(y)
#     print()

# from claasp.ciphers.block_ciphers.aes_block_cipher import AESBlockCipher
# from claasp.cipher_modules.statistical_tests.AKI import AKI
# path = AKI(AESBlockCipher(number_of_rounds=3))
# # path.computate_path_generate(the_position=127,word_size=8)
# target = ['K_2_0','K_1_0']
# path.knowledge_propagation(target,8,128)

from claasp.ciphers.block_ciphers.klein_block_cipher import KleinBlockCipher
from claasp.ciphers.block_ciphers.aes_block_cipher import AESBlockCipher
from claasp.cipher_modules.inverse_cipher import get_key_schedule_component_ids,get_cipher_components
klein = KleinBlockCipher(number_of_rounds=3)
KSA_component = get_key_schedule_component_ids(klein)
KSA = klein.key_schedule_algorithm()
res1= KSA.evaluate([0x0000000000000000])
res_hex = 0xb7703777c0f7700
KSA_inv,x = KSA.key_schedule_inverse()
KSA_inv.inputs

# def replace_second_number(s, new_num):
#     parts = s.split('_')
#     if len(parts) < 3:
#         raise ValueError("字符串必须包含至少两个下划线")
#     parts[2] = str(new_num)
#     return '_'.join(parts)

# # 使用示例
# original_str1 = "K_0_2"
# new_str1 = replace_second_number(original_str1, 5)
# print(new_str1)  # 输出: K_0_5

# original_str2 = "SK_10_23"
# new_str2 = replace_second_number(original_str2, 45)
# print(new_str2)  # 输出: SK_10_45


