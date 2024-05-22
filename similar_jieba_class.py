import pandas as pd
import jieba

"""
   匹配思路：
   1. 先匹配小类职业
   对于招聘数据（zhaopin-1.xlsx），将"岗位"作为匹配关键词
   对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"小类职业名称"作为匹配关键词
   2.再匹配细分职业
   对于招聘数据（zhaopin-1.xlsx），将"职位"作为匹配关键词
   对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"细分职业名称"作为匹配关键词
   3.最后匹配细分职业描述
   对于招聘数据（zhaopin-1.xlsx），将"描述"作为匹配关键词
   对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"细分职业描述"作为匹配关键词
   采用jieba分词处理输入文本
"""


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
