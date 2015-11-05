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


parsite - ���������� ��� �������� parsite v1.0

�������� �������� ���������� ����� � ����������� ���,
 ������������� ������, � ����� ���������.


������ �������:

myParser = MyParserClass()
data = myParser.parse()

 -��� ������ ����� ������ �������� ������ �������� � ���������� data


������:

  ParSite - ������� ���������� � ����� ��������. ����� ����� �������
������ � ����� �������� ��� � ��������.
  ���������� ��������:
  url - ����� ��������

  �������������� ����� parse_page:
   �������� � ������������ ��������, ������ ��������� ��������



  ParseListingPagesByParam - ������� ���������� � ��������� (��������,
���������� �� �������, �� ��������, ��� ����� �������), ��� �����
���������� � �������� �� ������� ��� ������ ��� ���������. ��������:
http://site.ru/index.php?route=product/search&keyword=&page=1

� ���� ������� ����� ������ �� ��������� ����������� ������ ��� ������
��������� page (����� �������� ������

� ���� ������ ����� ��������������:
    ��������� project, url, url_template, fieldnames
    ��� ������� �������
    url_template = "http://site.ru/index.php?route=product/search&keyword=&page={N_PAGE}"
    ������:
        get_max_page_num - ������ ���������� ������������ �������� page
������.
        parse_listing_page - ������ ���������� ������ � �������


  ParseListingPagesByParamToCsv - �� �� ����� ���
ParseListingPagesByParam, �� � ������� � csv
  � ������ parse_listing_page ����� �������� self.write_csv_data(data) ���
������� ������ ����� ������ ���������� � csv

  ParseListOfListings - ��������� ��������� ���������, ����� ������ �� ���
��� ����, ���� ��� ����� �������� �������

�������������� ����������
    project
    url
    fieldnames

    ������
       get_listing_urls - ������ ���������� ������� ���� ���������
       parse_listing_page - ���������� ����������� � �������� ������


  ParseListOfListingsToCsv - �� �� ��� � ParseListOfListings �� ����������
� csv �� ����� ��������
  � ������ parse_listing_page ����� �������� self.write_csv_data(data) ���
������� ������ ����� ������ ���������� � csv