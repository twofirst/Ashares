# coding=utf-8

import re
import string
import unicodedata
import jieba.posseg
import numpy as np
import re
from collections import Counter

stopwords = ['的', '后']
s = '项目投资;教育咨询、文化咨询、投资咨询、企业管理咨询;投资管理;销售自行开发后的产品;软件开发;企业策划;影视策划;文艺创作;组织文化艺术交流活动;承办展览展示活动;技术开发、技术转让、技术咨询、技术服务;设计、制作、代理、发布广告。(“1、未经有关部门批准,不得以公开方式募集资金;2、不得公开开展证券类产品和金融衍生品交易活动;3、不得发放贷款;4、不得对所投资企业以外的其他企业提供担保;5、不得向投资者承诺投资本金不受损失或者承诺最低收益”;企业依法自主选择经营项目,开展经营活动;;。)'
print(s)
s = re.sub('\([^\)]*\)', '', unicodedata.normalize('NFKC', s) if isinstance(s, str) else s)
print(s)
punc = string.punctuation + '、。【】'
ss = re.split(f'[{punc}]', s)
terms = [w for w in ss if w != '']
print(terms)
word_weight = {}
for i in range(len(terms)):
    term = terms[i]
    weight = 1 - i / len(terms)
    for w in jieba.cut(term):
        if w not in stopwords:
            if w not in word_weight.keys():
                word_weight[w] = weight
            else:
                word_weight[w] += + weight
    # print(term, [w for w in jieba.cut(term)])

print(word_weight)
weight_sum = sum(word_weight.values())
# sorted_pairs=sorted(word_weight.items(), key=lambda item: item[1], reverse=True)
# normed_pairs = [(pair[0],pair[1]/weight_sum) for pair in sorted_pairs]
# print(normed_pairs)

# for k,v in word_weight.items():
#     word_weight[k]=v/weight_sum
word_weight = {k: v / weight_sum for k, v in word_weight.items()}
print(word_weight)

print([w for w in jieba.cut(s)])
print([w for w in jieba.cut_for_search(s)])
print([w for w in jieba.cut_for_search('机器人')])
print([w for w in jieba.cut_for_search('北斗大数据有限公司')])