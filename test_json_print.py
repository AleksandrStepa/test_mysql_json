import requests
import json
import re
import pymysql
from natsort import natsorted


try:
    url = r'http://84.201.129.203:4545/get_structure_course'
    results = requests.post(url).json()
except Exception as erorr:
    print(erorr)


chapter_list = []
# Наполнение списка заголовками верхнего уровня
for key, value in list(results['blocks'].items()):
    # Блоки в названии которых есть "chapter" содержат заголовки
    if 'chapter' in key:
        chapter_list.append(value['display_name'])

# Удаление слова Модуль/Модули в названии заголовка, для корректной сортировки
pattern = re.compile(r'Модул[ьи]\s')
for i in range(len(chapter_list)):
    chapter_list[i] = re.sub(pattern, '', chapter_list[i])
# Сортировка по строковому значению содержащему числа
# Sorted не подходит так как 10 будет впереди 2
chapter_list = natsorted(chapter_list)

# Список вида [[id_module,name_module],[id_module,name_module]...]
# понадобится для заполнения БД
structure_course_list = []

'''
1.Из остсортированного списка верхних заголовков выбирается название
2.Выводится на экрана
3.Проверяется наличие подзаголовков
4.При наличи подзаголовка осуществляется вывод на экран
5.У подзаголовка проверяется наличие следующего подзаголовка и т.д.
'''

# Из остсортированного списка верхних заголовков выбирается название
for chapter in chapter_list:

 # Поиск этого названия в каждом блоке
 for key, value in list(results['blocks'].items()):
  if (chapter in value['display_name']) & ('chapter' in key):
   print(value['display_name']+' - '+ value['block_id'])
   # Наполнение списка для БД
   structure_course_list.append([value['block_id'],
                                value['display_name']])

   # Если в блоке есть информация о дочерних подзаголовках, осуществляется
   # поиск и вывод этих заголовков (также поочередно, с проверкой подзаголовков)
   if 'children' in value.keys():
    for value_children_1 in list(value['children']):
     print(' ' + results['blocks'][value_children_1]['display_name']
           + ' - ' + results['blocks'][value_children_1]['block_id'])
     # Наполнение списка для БД
     structure_course_list.append([results['blocks'][value_children_1]['block_id'],
                                  results['blocks'][value_children_1]['display_name']])


     # Если в блоке есть информация о дочерних подзаголовках, осуществляется
     # поиск и вывод этих заголовков
     if 'children' in results['blocks'][value_children_1].keys():
      for value_children_2 in results['blocks'][value_children_1]['children']:
       print('   ' + results['blocks'][value_children_2]['display_name']
            + ' - ' + results['blocks'][value_children_2]['block_id'])
       # Наполнение списка для БД
       structure_course_list.append([results['blocks'][value_children_2]['block_id'],
                                    results['blocks'][value_children_2]['display_name']])

       # Если в блоке есть информация о дочерних подзаголовках, осуществляется
       # поиск и вывод этих заголовков
       if 'children' in results['blocks'][value_children_2].keys():
        for value_children_3 in results['blocks'][value_children_2]['children']:
         print('     ' + results['blocks'][value_children_3]['display_name']
              + ' - ' + results['blocks'][value_children_3]['block_id'])
         # Наполнение списка для БД
         structure_course_list.append([results['blocks'][value_children_3]['block_id'],
                                      results['blocks'][value_children_3]['display_name']])
 # Для удобства чтения с экрана
 input('Чтобы продолжить нажми Enter')

print ('подключение к базе данных MySQL...')
try:
    con = pymysql.connect('35.232.21.1',
    'basefortest',
    '12345678',
    'dbtest'
    )
    print ('Выполнено')

    cur = con.cursor()
    cur.execute('DROP TABLE IF EXISTS test;')
    cur.execute('''CREATE TABLE test
    (id_module VARCHAR(35) PRIMARY KEY NOT NULL,
    name_module VARCHAR(120));''')

    for id_name in structure_course_list:
       cur.execute(f"""INSERT INTO test (id_module, name_module)
       VALUES
       ('{id_name[0]}', '{id_name[1]}')""")

except Exception as erorr:
    print(erorr)
cur.close()
con.close()
