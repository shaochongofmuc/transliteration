
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
import os
#import math
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

file1 = open('yuan_train.bo', encoding='utf-8', errors='ignore')
file2 = open('yuan_train.cn', encoding='utf-8', errors='ignore')
outs = open('test0520.txt', 'w+', encoding='utf-8')

str_bo = ''
out_str = ''

list_alignnumber = []
count_cn = 0
count_bo = 0
countPair = 0
countpair = 0
countLine = 0
num = 0
iter_num = 1
max_num = 0
max_cn = 0
Epsilon = 1
S = 0
k_1 = 0
max = 0
p = 1
p_a = 0
p_b = 0
test = 0
lie = 0

list_cn = []
list_bo = []
list_cn_liquid = []
list_bo_liquid = []
list_num_cn = []
list_num_bo = []
list_result_cn = []
list_result_bo = []
list_liquid = []
list_startP = []
list_p = []
list_p_arr = []
list_col = []            #countPair所属列序列 
list_row = []            #countPair所属行序列
list_out = []
list_best = []

dict_cn = {}
dict_bo = {}
pairDic = {}
NewpairDic = {}
dict_line = {}
dict_split = {}
dict_A = {}

def combNumber(m, n, b,list_alignnumber):
    for i in range(m, n-1, -1):   
        b[n-1] = i
        if n-1>0:
            combNumber(i-1,n-1,b,list_alignnumber)
        else:
            res = b[:]
            res.pop()
            list_alignnumber.append(res)


for line_bo,line_cn in zip(file1,file2):
    list_bo = list(line_bo.split(' '))
    while '' in list_bo:
        list_bo.remove('')
    while '\n' in list_bo:
        list_bo.remove('\n')
    list_cn = list(line_cn.split(' '))
    while '' in list_cn:
        list_cn.remove('')
    while '\n' in list_cn:
        list_cn.remove('\n')
    for cn in list_cn:
        if cn not in dict_cn.keys():
            dict_cn[cn] = count_cn
            list_cn_liquid.append(cn)
            count_cn += 1
    combNumber(len(list_bo)-1,len(list_cn)-1,list(range(len(list_cn))),list_alignnumber)
    num = len(list_alignnumber)
    if num > max_num:
        max_num = num
    for i in list_alignnumber:
        lie = list_alignnumber.index(i)
        i.insert(0,'0')
        i.append(len(list_bo))
        i = list(map(int,i))
        for j in range(len(i)-1):
            for m in range(i[j],i[j+1]):
                str_bo = str_bo + str(list_bo[m])
            list_result_bo.append(str_bo)
            list_result_cn.append(list_cn[j])
            if str_bo not in dict_bo.keys():
                dict_bo[str_bo] = count_bo
                list_bo_liquid.append(str_bo)
                count_bo += 1
            pairDic[countPair] = (dict_cn[list_cn[j]],dict_bo[str_bo])
            dict_line[countPair] = countLine
            list_col.append(lie)
            list_row.append(j)
            list_num_cn.append(len(i)-1)
            countPair += 1
            str_bo = ''
    dict_split[countPair] = 0
    list_alignnumber = []
    list_bo = []
    list_cn = []
    countLine += 1
    totalNumberR = 0
    num = 0
count_cn -= 1
count_bo -= 1
list_bo = []
list_cn = []

  
for i in list_num_cn:
    if i > max_cn:
        max_cn = i
list_num_cn = []

list_liquid = list(set(pairDic.values()))
i = 0
for _tuple in list_liquid:
    NewpairDic[_tuple] = i
    i += 1
    countpair += 1


B = np.zeros([countpair+1,countpair],dtype='float16')
B_1 = np.zeros([countpair+1,countpair],dtype='float16')
C = np.zeros([countLine,max_num],dtype='float16')
dict_split[0] = 0

for i in range(countPair):
    if (list_col[i],dict_line[i]) not in dict_A:
        dict_A[list_col[i],dict_line[i]] = [NewpairDic[pairDic[i]]]
    else:
        dict_A[list_col[i],dict_line[i]].append(NewpairDic[pairDic[i]])
    if i in dict_split:
        B[countpair][NewpairDic[pairDic[i]]] += 1
    else:       
        B[NewpairDic[pairDic[i-1]]][NewpairDic[pairDic[i]]] += 1
np.maximum(B,0.0001)     
B1 = B.sum(axis=0)
B = B / B1
print('B is done!')

for i in range(countPair):
    if C[dict_line[i],list_col[i]] == 0:
        if i in dict_split:
            C[dict_line[i],list_col[i]] = 1 * B[countpair,NewpairDic[pairDic[i]]]
        else:
            C[dict_line[i],list_col[i]] = 1 * B[NewpairDic[pairDic[i-1]],NewpairDic[pairDic[i]]]
    else:
        if i in dict_split:
            C[dict_line[i],list_col[i]] *= B[countpair,NewpairDic[pairDic[i]]]
        else:
            C[dict_line[i],list_col[i]] *= B[NewpairDic[pairDic[i-1]]][NewpairDic[pairDic[i]]]
C1 = C.sum(axis = 0)
C = C / C1
list_p = []
print('C is done!')



while iter_num < 100:
    for i in range(countPair):
        if i in dict_split:
            B_1[countpair][NewpairDic[pairDic[i]]] += C[dict_line[i],list_col[i]]
        else:       
            B_1[NewpairDic[pairDic[i]]][NewpairDic[pairDic[i]]] += C[dict_line[i],list_col[i]]
    if np.allclose(B,B_1,0.0001,0.00001):
        print('B 已经收敛')
        iter_num = 100
        break;
    B = B_1
    print('B已更新')
    for i in range(countPair):
        if C[dict_line[i],list_col[i]] == 0:
            if i in dict_split:
                C[dict_line[i],list_col[i]] = 1 * B[countpair][NewpairDic[pairDic[i]]] 
            else:
                C[dict_line[i],list_col[i]] = 1 * B[NewpairDic[pairDic[i-1]]][NewpairDic[pairDic[i]]] 
        else:
            if i in dict_split:
                C[dict_line[i],list_col[i]] *= B[countpair][NewpairDic[pairDic[i]]] 
            else:
                C[dict_line[i],list_col[i]] *= B[NewpairDic[pairDic[i-1]]][NewpairDic[pairDic[i]]] 
    print('iter_num = ',iter_num)
    iter_num += 1

list_best = C.argmax(axis=1)
for i in range(countLine-1):
    print(C[i,:])
    list_out = dict_A[list_best[i],i]
    for j in range(len(list_out)):
        cn,bo = list_liquid[int(list_out[j])]
        out_str = out_str +  list_cn_liquid[cn] + '|' + list_bo_liquid[bo] + '    ' 
    out_str = out_str + '\n'
    outs.write(out_str)
    out_str = ''
    list_out = []
    test += 1
out_str = ''
print('success')
file1.close()
file2.close()
outs.close()

