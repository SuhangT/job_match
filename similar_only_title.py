import pandas as pd

"""
   匹配思路：
   对于招聘数据（zhaopin-1.xlsx），将"岗位"和"职位"合并在一起作为匹配关键词
   对于职业大典（中华人民共和国职业分类大典（2022年版）.xlsx），将"细分职业名称"作为匹配关键词
"""


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
