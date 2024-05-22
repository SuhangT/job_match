

## 1 项目概况



### 1.1 项目背景

目前我们有两个文件，一个是网络中公开的招聘数据 `zhaopin-1.xlsx`，另一个是国家标准职业大典 `中华人民共和国职业分类大典（2022年版）.xlsx`，两个表的数据结构如下：



<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>公司名称</th>
      <th>关联公司名称</th>
      <th>公司地址</th>
      <th>工作地点</th>
      <th>工作地点所在区域</th>
      <th>岗位</th>
      <th>职位</th>
      <th>描述</th>
      <th>职位标签</th>
      <th>所属部门</th>
      <th>相关福利</th>
      <th>招聘人数</th>
      <th>待遇</th>
      <th>语言要求</th>
      <th>发布时间</th>
      <th>纳税人识别号</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>科飞环保有限公司</td>
      <td>科飞环保有限公司</td>
      <td>贵阳市金阳观山湖区绿地联盟铂金大厦11栋19楼3号</td>
      <td>贵州省</td>
      <td>贵阳市</td>
      <td>会计/财务/审计/税务</td>
      <td>会计</td>
      <td>岗位职责1、专业人员职位，在上级的领导和监督下定期完成量化的工作要求，并能独立处理和解决所负...</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>1</td>
      <td></td>
      <td>NaN</td>
      <td>2016-04-20 16:00:00</td>
      <td>915201007705722679</td>
    </tr>
  </tbody>
</table>



<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>大类职业代码</th>
      <th>大类职业名称</th>
      <th>大类职业描述</th>
      <th>中类职业代码</th>
      <th>中类职业名称</th>
      <th>中类职业描述</th>
      <th>小类职业代码</th>
      <th>小类职业名称</th>
      <th>小类职业描述</th>
      <th>细分职业代码</th>
      <th>细分职业名称</th>
      <th>细分职业描述</th>
      <th>2015-2022变化</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>GBM20000</td>
      <td>专业技术人员</td>
      <td>专业技术人员从事科学研究和专业技术工作的人员。</td>
      <td>GBM20100</td>
      <td>科学研究人员</td>
      <td>科学研究人员    从事社会科学和自然科学研究工作的专业人员</td>
      <td>GBM20101</td>
      <td>哲学研究人员</td>
      <td>哲学研究人员   从事自然、社会与思维一般规律研究的专业人员。</td>
      <td>2-01-01-00</td>
      <td>哲学研究人员</td>
      <td>从事自然、社会与思维一般规律研究的专业人员。主要工作任务:1.研究马克思主义哲学原理、马克思...</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>

我们希望将招聘数据中每一个岗位，一一对应到国家职业大典中的"细分职业名称"，即将招聘数据岗位标准化。

### 1.2 我们的尝试

我们根据主机掌握到的浅薄的NLP知识进行了一些处理，主要通过词向量的方式解决，具体的数据和代码可查看

[SuhangT/job_match (github.com)](https://github.com/SuhangT/job_match)

这里简要说一下不同的Python文件的思路

#### （1）仅用职业名称匹配

`similar_only_title.py`

>匹配思路
>
>- 对于招聘数据（zhaopin-1.xlsx），将"岗位"和"职位"合并在一起作为匹配关键词
>- 对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"细分职业名称"作为匹配关键词
>  

```python
import pandas as pd


def get_character_frequency_vector(text: str) -> dict:
    """
    获取文本中每个字符的频率
    :param text:
    :return: 每个字符的频率的字典
    """
    frequency_vector = {}
    for character in text:
        if character in frequency_vector:
            frequency_vector[character] += 1
        else:
            frequency_vector[character] = 1
    return frequency_vector


def calculate(text1: str, text2: str) -> float:
    """
    计算两个文本的相似度
    :param text1:
    :param text2:
    :return: 相似度数据
    """
    vector1 = get_character_frequency_vector(text1)
    vector2 = get_character_frequency_vector(text2)

    dot_product = 0
    magnitude1 = 0
    magnitude2 = 0

    for key in vector1.keys():
        if key in vector2:
            dot_product += vector1[key] * vector2[key]
        magnitude1 += vector1[key] ** 2

    for key in vector2.keys():
        magnitude2 += vector2[key] ** 2

    magnitude1 = magnitude1 ** 0.5
    magnitude2 = magnitude2 ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    return dot_product / (magnitude1 * magnitude2)


def find_most_similar_word(input_text: str, words: dict, top: int) -> list:
    """
    查找与输入文本最相似的词
    :param input_text: 输入的文本
    :param words: 要匹配的标准文本的字典
    :param top: 相似度最高的top个文本
    :return: 匹配出来的列表，每一个元素是一个元组，包含匹配的职业代码和相似度
    """
    code = ''
    max_similarity = 0
    top_dict = []
    for key, value in words.items():
        similarity = calculate(input_text, value)
        if similarity > max_similarity:
            max_similarity = similarity
            code = key
        if max_similarity >= 0.9:
            continue
        top_dict.append((key, similarity))
    top_dict = sorted(top_dict, key=lambda x: x[1], reverse=True)[:top]
    return top_dict


def excel_to_key_value(filepath: str):
    """
    将excel文件转换为字典，key为职业代码，value为职业名称
    :param filepath: 职业大典的路径
    :return: 职业文本字典
    """
    dic = {}
    worksheet = pd.read_excel(filepath)
    for index, row in worksheet.iterrows():
        key = row['细分职业代码']
        dic[key] = row['细分职业名称']
    return dic


def process_excel(filepath: str, dic: dict):
    """
    处理招聘数据，将匹配结果写入excel
    :param filepath: 招聘数据的路径
    :param dic: 职业文本字典
    :return: 写入新的excel
    """
    worksheet = pd.read_excel(filepath)
    for index, row in worksheet.iterrows():
        text_title = ' '.join([str(row['岗位']), str(row['职位']), str(row['职位']), str(row['职位'])])
        top_title = find_most_similar_word(input_text=text_title, words=dic, top=1)

        code = top_title[0][0]
        print(f'{row["岗位"]}- {row["职位"]} - {code} - {dic[code]}')
        worksheet.at[index, '职业代码'] = code
        worksheet.at[index, '职业名称'] = dic[code]
    worksheet.to_excel('zhaopin-1-only-title.xlsx', index=False)


if __name__ == '__main__':
    dic = excel_to_key_value('中华人民共和国职业分类大典（2022年版）.xlsx')
    process_excel(filepath='zhaopin-1.xlsx', dic=dic)
```



#### （2）用职业名称和职业描述匹配

`similar_description.py`

> 匹配思路
>
> - 对于招聘数据（zhaopin-1.xlsx），将"岗位"、"职位"和"描述"合并在一起作为匹配关键词
> - 对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"细分职业名称"和"细分职业描述"作为匹配关键词
> - 采用jieba分词处理输入文本

```python
import pandas as pd
import jieba


def get_character_frequency_vector(text: str) -> dict:
    """
    获取文本中每个字符的频率
    :param text:
    :return: 每个字符串的频率的字典
    """
    seg_list = jieba.cut(text, cut_all=False)
    frequency_vector = {}
    for character in seg_list:
        if character in frequency_vector:
            frequency_vector[character] += 1
        else:
            frequency_vector[character] = 1
    return frequency_vector


def calculate(text1: str, text2: str) -> float:
    """
        计算两个文本的相似度
        :param text1:
        :param text2:
        :return: 相似度数据
        """
    vector1 = get_character_frequency_vector(text1)
    vector2 = get_character_frequency_vector(text2)

    dot_product = 0
    magnitude1 = 0
    magnitude2 = 0

    for key in vector1.keys():
        if key in vector2:
            dot_product += vector1[key] * vector2[key]
        magnitude1 += vector1[key] ** 2

    for key in vector2.keys():
        magnitude2 += vector2[key] ** 2

    magnitude1 = magnitude1 ** 0.5
    magnitude2 = magnitude2 ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    return dot_product / (magnitude1 * magnitude2)


def find_most_similar_word(input_text: str, words: dict, top: int) -> list:
    """
        查找与输入文本最相似的词
        :param input_text: 输入的文本
        :param words: 要匹配的标准文本的字典
        :param top: 相似度最高的top个文本
        :return: 匹配出来的列表，每一个元素是一个元组，包含匹配的职业代码和相似度
        """
    code = ''
    max_similarity = 0

    top_dict = []

    for key, value in words.items():
        similarity = calculate(input_text, value[0])
        if similarity > max_similarity:
            max_similarity = similarity
            code = key
        if max_similarity >= 0.9:
            continue
        top_dict.append((key, similarity))
    top_dict = sorted(top_dict, key=lambda x: x[1], reverse=True)[:top]
    # if max_similarity < 0.2:
    #     code = f'相似度:{max_similarity}'
    return top_dict


def excel_to_key_value(filepath: str):
    """
        将excel文件转换为字典，key为职业代码，value为职业名称
        :param filepath: 职业大典的路径
        :return: 职业文本字典
        """
    dic = {}
    worksheet = pd.read_excel(filepath)
    for index, row in worksheet.iterrows():
        key = row['细分职业代码']
        value = ' '.join([row['细分职业名称'], row['细分职业描述']])
        dic[key] = (value, row['细分职业名称'])
    return dic


def process_excel(filepath: str, dic: dict):
    """
        处理招聘数据，将匹配结果写入excel
        :param filepath: 招聘数据的路径
        :param dic: 职业文本字典
        :return: 写入新的excel
        """
    worksheet = pd.read_excel(filepath)
    for index, row in worksheet.iterrows():
        text_title = ' '.join([str(row['岗位']), str(row['职位'])])
        top_title = find_most_similar_word(input_text=text_title, words=dic, top=10)
        top_dict = {x[0]: dic[x[0]] for x in top_title}
        text_content = ' '.join([str(row['岗位']), str(row['职位']), str(row['描述']), str(row['职位标签'])])
        top_content = find_most_similar_word(input_text=text_content, words=top_dict, top=1)
        code = top_content[0][0]
        print(f'{row["岗位"]}- {row["职位"]} - {code} - {top_dict[code][1]}')
        worksheet.at[index, '职业代码'] = code
        worksheet.at[index, '职业名称'] = top_dict[code][1]
    worksheet.to_excel('demo/zhaopin-1-jieba.xlsx', index=False)


if __name__ == '__main__':
    dic = excel_to_key_value('中华人民共和国职业分类大典（2022年版）.xlsx')
    process_excel(filepath='demo/zhaopin-1.xlsx', dic=dic)

```

#### （3）分级匹配

`similar_jieba_class.py`

>匹配思路
>
>
>1. 先匹配小类职业
>  - 对于招聘数据（zhaopin-1.xlsx），将"岗位"作为匹配关键词
>  - 对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"小类职业名称"作为匹配关键词
>2. 再匹配细分职业
>   - 对于招聘数据（zhaopin-1.xlsx），将"职位"作为匹配关键词
>   - 对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"细分职业名称"作为匹配关键词
>3. 最后匹配细分职业描述
>   - 对于招聘数据（zhaopin-1.xlsx），将"描述"作为匹配关键词
>   - 对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"细分职业描述"作为匹配关键词
>   - 采用jieba分词处理输入文本
>

```python
import pandas as pd
import jieba


def get_character_frequency_vector(text: str) -> dict:
    """
        获取文本中每个字符的频率
        :param text:
        :return: 每个字符串的频率的字典
        """
    seg_list = jieba.cut(text, cut_all=False)
    frequency_vector = {}
    for character in seg_list:
        if character in frequency_vector:
            frequency_vector[character] += 1
        else:
            frequency_vector[character] = 1
    return frequency_vector


def calculate(text1: str, text2: str) -> float:
    """
        计算两个文本的相似度
        :param text1:
        :param text2:
        :return: 相似度数据
        """
    vector1 = get_character_frequency_vector(text1)
    vector2 = get_character_frequency_vector(text2)

    dot_product = 0
    magnitude1 = 0
    magnitude2 = 0

    for key in vector1.keys():
        if key in vector2:
            dot_product += vector1[key] * vector2[key]
        magnitude1 += vector1[key] ** 2

    for key in vector2.keys():
        magnitude2 += vector2[key] ** 2

    magnitude1 = magnitude1 ** 0.5
    magnitude2 = magnitude2 ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0

    return dot_product / (magnitude1 * magnitude2)


def find_most_similar_word(input_text: str, words: dict, top: int, position: int) -> list:
    """
        查找与输入文本最相似的词
        :param input_text: 输入的文本
        :param words: 要匹配的标准文本的字典
        :param top: 相似度最高的top个文本
        :param position: 匹配的位置，0表示匹配小类职业名称，1表示匹配细分职业名称，2表示匹配细分职业描述
        :return: 匹配出来的列表，每一个元素是一个元组，包含匹配的职业代码和相似度
        """
    code = ''
    max_similarity = 0

    top_dict = []

    for key, value in words.items():
        similarity = calculate(input_text, value[position])
        if similarity > max_similarity:
            max_similarity = similarity
            code = key
        if max_similarity >= 0.9:
            continue
        top_dict.append((key, similarity))
    top_dict = sorted(top_dict, key=lambda x: x[1], reverse=True)[:top]
    # if max_similarity < 0.2:
    #     code = f'相似度:{max_similarity}'
    return top_dict


def excel_to_key_value(filepath: str):
    """
        将excel文件转换为字典，key为职业代码，value为职业名称
        :param filepath: 职业大典的路径
        :return: 职业文本字典
        """
    dic_detail = {}
    dic_small = {}
    worksheet = pd.read_excel(filepath)
    for index, row in worksheet.iterrows():
        key = row['细分职业代码']
        dic_detail[key] = (row['细分职业名称'], row['细分职业描述'], row['小类职业代码'], row['小类职业名称'])
    worksheet.drop_duplicates(subset=['小类职业代码'], keep='first', inplace=True)
    for index, row in worksheet.iterrows():
        key = row['小类职业代码']
        dic_small[key] = (row['小类职业代码'], row['小类职业名称'])
    return dic_detail, dic_small


def process_excel(filepath: str, dic_detail: dict, dic_small: dict):
    """
        处理招聘数据，将匹配结果写入excel
        :param filepath: 招聘数据的路径
        :param dic: 职业文本字典
        :return: 写入新的excel
        """
    worksheet = pd.read_excel(filepath)
    for index, row in worksheet.iterrows():
        employ_ind = str(row['岗位'])
        employ_job = str(row['职位'])
        employ_des = str(row['描述'])

        top_ind = find_most_similar_word(input_text=employ_ind, words=dic_small, top=3, position=1)
        top_ind_code = [x[0] for x in top_ind]
        dic_filtered_detail = {}
        for key, value in dic_detail.items():
            if value[2] in top_ind_code:
                dic_filtered_detail[key] = value
        top_job = find_most_similar_word(input_text=employ_job, words=dic_filtered_detail, top=5, position=0)
        top_dict = {x[0]: dic_filtered_detail[x[0]] for x in top_job}
        top_content = find_most_similar_word(input_text=employ_des, words=top_dict, top=1, position=1)
        code = top_content[0][0] if top_content else ''
        job = '' if not code else top_dict[code][0]
        print(f'{employ_ind}- {employ_job} - {code} - {job}')
        worksheet.at[index, '职业代码'] = code
        worksheet.at[index, '职业名称'] = job
    worksheet.to_excel('demo/zhaopin-1-jieba-class.xlsx', index=False)


if __name__ == '__main__':
    dic_detail, dic_small = excel_to_key_value('中华人民共和国职业分类大典（2022年版）.xlsx')
    process_excel(filepath='demo/zhaopin-1.xlsx', dic_detail=dic_detail, dic_small=dic_small)
```

## 2 问题描述

以上的三种匹配方式获得了一定的准确率，尤其是仅用名称匹配的方法最为准确，但是部分职业的匹配还是不太理想。

以下公众号的文章为我们提供了一个新的计算文本相似度的思路——sentence-bert句向量嵌入方法

https://mp.weixin.qq.com/s/r65qr_8OCbRu-PaJktjZKw

这篇公众号的具体描述为：

>首先，我们需要将每一个岗位的具体职能和任务进行评分，判断他们到底是不是暴露在大模型替代风险中。然而我们需要处理**五千万**条招聘岗位，以及从其中划分出的**2.3亿**条具体的岗位任务，这个数量级的数据，即使用大模型也难以处理。
>
>好在O*net数据库和《中国职业大典》已经根据不同职业的工作划分出了2万余条具体的任务，使用sentence-bert句向量嵌入方法，我们将从招聘数据中抽取出的2.3亿条具体的岗位任务，匹配到2万余种标准岗位上，下表就是一个例子，我们将20条具体任务映射到了2种标准任务上。

后来我们还找到了一个sentence-bert句向量嵌入方法的开源库

[UKPLab/sentence-transformers: Multilingual Sentence & Image Embeddings with BERT (github.com)](https://github.com/UKPLab/sentence-transformers)

然而在具体的实践中我们遇到了以下几个问题：

- 如何从招聘数据的岗位描述中抽取出具体的岗位任务，若直接采用标点符号分割会得到很多和具体任务不相关的句子
- 抽取出来如何根据任务的匹配将岗位名称一一对应
- 我们怀疑这个开源库可能存在一些冗余模型加载导致计算速度极慢，不知道是否有替代方法实现sentence-bert句向量嵌入而不使用这个开源库，或者有什么其他办法提高计算效率

