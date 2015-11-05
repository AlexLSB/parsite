parsite - website parsing library v1.0

usage example :

class MyParserClass(ParSite)
    url = 'http://example.com'

    def parse_page
        page = super(super(ParSite, self).parse_page
        print page  #  <- here to extract data from page
        return page


myParser = MyParserClass()
print myParser.parse()


Classes:

  ParSite- get information from one page
  ParseListingPagesByParam - Listings parsing
  ParseListingPagesByParamToCsv - Listings parsing writing to csv
  ParseListOfListings - Parse listing pages which urls are already known
  ParseListOfListingsToCsv - ParseListOfListings writing to csv


================ Russian =============================


parsite - библиотека для парсинга parsite v1.0

Выберите наиболее подходящий класс и унаследуйте его,
 переопределив методы, и задав параметры.


Пример запуска:

myParser = MyParserClass()
data = myParser.parse()

 -это пример когда пармер собирает данные парсинга в переменную data


Классы:

  ParSite - Парсинг информации с одной страницы. Когда нужно собрать
данные с одной страницы или с листинга.
  определить параметр:
  url - адрес страницы

  переопределить метод parse_page:
   получает и распарсивает страницу, отдает результат парсинга



  ParseListingPagesByParam - Парсинг информации с листингов (например,
информация от товарах, на странице, где много товаров), где нужно
переходить с листинга на листинг при помощи гет параметра. Например:
http://site.ru/index.php?route=product/search&keyword=&page=1

в этом примере нужно ходить по листингам результатов поиска при помощи
параметра page (класс настроен менять

в этом классе нужно переопределить:
    параметры project, url, url_template, fieldnames
    для насшего примера
    url_template = "http://site.ru/index.php?route=product/search&keyword=&page={N_PAGE}"
    методы:
        get_max_page_num - должен возвращать максимальное значение page
числом.
        parse_listing_page - должен возвращать данные о товарах


  ParseListingPagesByParamToCsv - то же самое что
ParseListingPagesByParam, но с записью в csv
  в методе parse_listing_page нужно вызывать self.write_csv_data(data) для
каждого товара чтобы данные записались в csv

  ParseListOfListings - отпарсить несколько листингов, когда список их урл
уже есть, либо его можно получить списком

переопределить переменные
    project
    url
    fieldnames

    методы
       get_listing_urls - должен возвращать списком урлы листингов
       parse_listing_page - возвращать отпарсенные с листинга данные


  ParseListOfListingsToCsv - то же что и ParseListOfListings но записывает
в csv во время парсинга
  в методе parse_listing_page нужно вызывать self.write_csv_data(data) для
каждого товара чтобы данные записались в csv