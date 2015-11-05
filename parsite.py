# coding: utf-8

import csv
import inspect
import ConfigParser
from _parsingMethods2 import get_lxml_document_from_url


class StateMixin(object):
    ''' allows to save adnd retrieve state of variables from .cfg'''
    project = 'state_mixin_default'
    config_section_name = "state"

    def __init__(self, spec_name=None):
        if spec_name:
            self.project=spec_name
        self.config = ConfigParser.ConfigParser()
        self.conf_file_name = ''.join((self.project,'.cfg'))
        self.config.read(self.conf_file_name)

    def name_set_state(self, variables):
        self.check_config_exists()
        if not self.config.has_section(self.config_section_name):
            self.config.add_section(self.config_section_name)
        for key, value in variables.iteritems():
            self.config.set(self.config_section_name, key, value)
        with open(self.conf_file_name, 'wb') as configfile:
            self.config.write(configfile)            

    def set_state(self, *args):
        #---magic to get args of function
        get_rid_of = ['set_state(', ',', ')', '\n']
        calling_code = inspect.getouterframes(inspect.currentframe())[1][4][0]
        calling_code = calling_code[calling_code.index('set_state'):]
        for garbage in get_rid_of:
            calling_code = calling_code.replace(garbage, '')
        var_names, var_values = calling_code.split(), args
        dyn_dict = {var_name: var_value for var_name, var_value in
                    zip(var_names, var_values)}
        #---
        self.name_set_state(dyn_dict)

    def read_config(self, raise_error=True):
        self.check_config_exists()
        self.config.read(self.conf_file_name)
        self.check_section_exists(raise_error)

    def name_get_state(self, key):
        self.read_config()
        return self.config.get(self.config_section_name, key)

    def check_config_exists(self):
        if not self.config:
            raise Exception('config error', 'Maybe allow_resuming is not set!')

    def check_section_exists(self, raise_error=True):
        if not self.config.has_section(self.config_section_name):
            if raise_error:
                raise Exception('config error', 'no state saved')
            return False
        return True

    def get_state(self, *args):
        self.read_config()
        #---magic to get args of function
        get_rid_of = ['get_state(', ',', ')', '\n']
        calling_code = inspect.getouterframes(inspect.currentframe())[1][4][0]
        calling_code = calling_code[calling_code.index('get_state'):]
        for garbage in get_rid_of:
            calling_code = calling_code.replace(garbage, '')
        var_names, var_values = calling_code.split(), args
        dyn_dict = {var_name: var_value for var_name, var_value in
                    zip(var_names, var_values)}
        #---
        variables = dyn_dict
        result = []
        for key, value in variables.iteritems():
            try:
                result.append(self.config.get(self.config_section_name, key))
            except:
                result.append(value)
        if len(variables) == 1:
            result = result[0]
        return result


#=============================================================
class ParSite(StateMixin):
    ''' Simple parse one page '''
    use_proxy = False
    allow_resuming = False
    project = 'default_parsite_project4'
    config_section_name = "state"

    def __init__(self, spec_name=None):
        if spec_name:
            self.project=spec_name
        if self.allow_resuming:
	    super(ParSite, self).__init__(spec_name)            
            
    def get_page(self, url):
        return get_lxml_document_from_url(url, use_proxy=self.use_proxy)

    def parse_page(self):
        ''' Write your page parsing data here) '''
        page = self.get_page(self.url)
        return page
        
    def parse_ready(self):
        if not self.url:
            raise Exception('No url specified!', self)
        print 'Starting to parse %s' % self.project
        return True

    def parse(self):
        if not self.parse_ready():
            return False
        return self.parse_page()


#=======================================================================
class ParseListOfListings(ParSite):
    ''' Parse several pages when many nodes of data'''
    def parse(self):
        if not self.parse_ready():
            return False
        self.categories_list = self.get_listing_urls()
        return self.run_categories_list(self.categories_list)

    def run_categories_list(self, listings_urls):
        parsed_data = []
        for url_id, listing_url in enumerate(listings_urls):
            print 'Progress: {0:.0f}%'.format(((url_id+1) * 100 / len(listings_urls)))
            page_result = self.parse_listing_page(listing_url)
            if page_result:
                parsed_data.extend(page_result)
        return parsed_data

    def get_listing_urls(self, url):
        '''  write your code to return list of urls of listings'''
        return []

    def parse_listing_page(self, listing_url):
        '''  write your code to parse data from listing'''
        listing_page = self.get_page(listing_url)
        print 'Warning: listing_page is not overrided!'
        return listing_page

    def work_item(self,item):
        print 'Warning: wort_item is not overrided!'
        return []

    def get_item_data(self, item, constant_data=None):
        data = self.work_item(item)
        if constant_data:
            for key, value in constant_data.iteritems():
                if constant_data[key]>'':
                    data[key] = value
        return data

    def work_items(self, items, constant_data=None):
        data_list = []
        for item in items:
            data_list.append(self.get_item_data(item, constant_data))
        return data_list


class ResumeMixin(object):

    def resume(self):
        ''' do we resuming old parsing '''
        result = False
        if self.allow_resuming:
            self.status = 'Start'
            if self.check_section_exists(raise_error=False):
                self.status = self.get_state(self.status)
            if self.status == 'Pending':
                result = True
        return result

    def get_resume_status(self):
        if self.resume():
            self.status = 'Resuming'
            print 'Resuming from old state...'
        else:   
            self.status = 'Pending'
            self.set_state(self.status)
            print 'Starting parsing from scratch...'
        return self.status

    def set_finish_status(self):
        self.status = 'Finish'
        self.set_state(self.status)

    def iterate_resuming(self, items_dict, item_worker, show_progress=False, constant_data=None, last_parse_level=False):
        ''' do iteraring though items_dict with resume 
        items_dict is a dict with only one key which value is a list
        to iterate through '''
        result = []
        key, items = items_dict.popitem()
        items_range = len(items)
        items_cntr = 0
        if self.allow_resuming and self.status == 'Resuming':
            items_cntr = int(self.name_get_state(key))
            print 'Resuming %s #%s' % (key, items_cntr)
            if last_parse_level:
                items_cntr += 1
                self.status = 'Pending'
        for i in range(items_cntr, items_range):
            if constant_data:
                item_result = item_worker(items[i], constant_data)
            else:
                item_result = item_worker(items[i])
            if item_result:
                result.append(item_result)
	    if self.allow_resuming:
                listing_cntr = i
                self.name_set_state({key : listing_cntr})
            if show_progress:
                print 'Progress: {0:.0f}%'.format((i+1) * 100 / items_range)
        return result 
                                                      

class ParseListOfListingsToCsv(ParseListOfListings, ResumeMixin):
    ''' Parse several pages when many nodes of data
        writing to csv file immidietally
        (to avoid data loss on errors) '''
    csv_writer = None
    csvfile = None

    def __init__(self, spec_name=None):
        super(ParseListOfListingsToCsv, self).__init__(spec_name)
        if self.resume():        
            self.csvfile = open(''.join((self.project, '.csv')), 'a')
            resume = True
        else:            
            self.csvfile = open(''.join((self.project, '.csv')), 'w')
            resume = False
        self.csv_writer = csv.DictWriter(self.csvfile, self.fieldnames,
            delimiter=';',
            extrasaction = 'ignore',
            lineterminator = '\n',)
        if not resume:
            self.csv_writer.writeheader()
                
    def write_csv_data(self, data_dict):
        for k in data_dict.keys():
            try:
                data_dict[k] = data_dict[k].encode('utf-8')
            except:
                pass
        self.csv_writer.writerow(data_dict)
        if self.allow_resuming:
            self.csvfile.flush()

    def work_listing_url(self, listing_url):
        return self.parse_listing_page(listing_url)
        
    #add state writing and reading if needed
    def run_categories_list(self, listings_urls):
        return self.iterate_resuming(
            {'listings_urls' : listings_urls},
            self.work_listing_url,
            show_progress=True)
        
    def parse(self):
        if self.allow_resuming:
            self.get_resume_status()
        result = super(ParseListOfListingsToCsv, self).parse()
        if self.allow_resuming:
            self.set_finish_status()
        return result

    def work_on_item(self, item, constant_data=None):
        data = self.get_item_data(item, constant_data)
        self.write_csv_data(data)
        return data        
        
    def work_items(self, items, constant_data=None):
        return self.iterate_resuming(
            {'items' : items},
            self.work_on_item, last_parse_level=True, constant_data=constant_data)


#=======================================================
class ParseListingPagesByParam(ParSite, ResumeMixin):
    ''' Parse listing with items, paginated by get param '''
    def parse(self):
        if not self.parse_ready():
            print "not ready!"
            return False
        if self.allow_resuming:
            self.get_resume_status()
        result = self.run_pages()
        if self.allow_resuming:
            self.set_finish_status()
        return result

    def work_page_num(self, page_num):
        if page_num == 1:
            return self.parse_listing_page(self.first_page)
        url = self.generate_page_url(page_num)
        return self.parse_listing_page(self.get_page(url))

    def run_pages(self):
        self.first_page = self.get_page(self.url)
        self.last_page_num = self.get_max_page_num()
        page_nums = range(1, self.last_page_num)
        return self.iterate_resuming(
            {'page_nums' : page_nums},
            self.work_page_num,
            show_progress=True)

    def generate_page_url(self, page_num):
        '''  write your code to return list of urls of listings'''
        if not self.url_template:
            raise Exception('No url_template!', url)
	url = self.url_template.replace('{N_PAGE}', str(page_num))
	if url == self.url_template:
            raise Exception('Url template doesnt work!', url_template)
	return url

    def parse_listing_page(self, page_document):
        '''  write your code to parse data from listing'''
        print 'Warning: listing_page is not overrided!'
        return listing_page

    def get_max_page_num():
        print 'Warning: get_max_pages is not overrided!'
        return 0

    def work_item(self,item):
        print 'Warning: wort_item is not overrided!'
        return []

    def get_item_data(self, item, constant_data=None):
        data = self.work_item(item)
        if constant_data:
            for key, value in constant_data.iteritems():
                if constant_data[key]>'':
                    data[key] = value
        return data

    def work_on_item(self, item, constant_data=None):
        return self.get_item_data(item, constant_data)
        
    def work_items(self, items, constant_data=None):
        return self.iterate_resuming(
            {'items' : items},
            self.work_on_item, last_parse_level=True, constant_data=constant_data)


class ParseListingPagesByParamToCsv(ParseListingPagesByParam, ResumeMixin):
    ''' As ParseListingPagesByParam but 
        writing to csv file immidietally
        (to avoid data loss on errors) '''
    csv_writer = None
    csvfile = None

    def __init__(self, spec_name=None):
        super(ParseListingPagesByParamToCsv, self).__init__(spec_name)
        self.csvfile = open(''.join((self.project, '.csv')), 'w')
        self.csv_writer = csv.DictWriter(self.csvfile, self.fieldnames,
            delimiter=';',
            extrasaction = 'ignore',
            lineterminator = '\n')
        self.csv_writer.writeheader()
                
    def write_csv_data(self, data_dict):
        for k in data_dict.keys():
            try:
                data_dict[k] = data_dict[k].encode('utf-8')
            except:
                pass
        self.csv_writer.writerow(data_dict)

    def work_on_item(self, item, constant_data=None):
        data = super(ParseListingPagesByParamToCsv, self).work_on_item(item, constant_data)
        self.write_csv_data(data)
        return data        

