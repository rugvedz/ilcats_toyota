# -*- coding: utf-8 -*-
import scrapy
import json
from ilcats_toyota.items import IlcatsToyotaItem

class ToyotaSpider(scrapy.Spider):
    name = 'toyota'
    # allowed_domains = ['sdfs']
    # start_urls = ['http://sdfs/']

    def start_requests(self):
        url = 'https://www.ilcats.ru/lexus&language=en/'
        yield scrapy.Request(url)

    def parse(self, response):
        country_xpath = response.xpath("//div[@class='List']/div[@class='name']/a")
        # print("response", country_xpath)

        for i in country_xpath:
            name = i.xpath(".//text()").get()
            href = i.xpath(".//@href").get()
            yield scrapy.Request(url = "https://www.ilcats.ru" + href, callback = self.parse_models, meta = {"region_name" : name})
            # yield{
            #     "href" : href,
            #     "name" : name
            # }


    def parse_models(self, response):
        region_name = response.request.meta['region_name']

        models_xpath = response.xpath("//div[@class='List']")

        for i in models_xpath:
            model_header = i.xpath(".//div[@class='Header']/div[@class='name']/text()").get()

            for n in i.xpath(".//div[@class='List ']/div[@class='List']/div[@class='id']"):
                submodel = n.xpath(".//a/text()").get()
                date_range = i.xpath(".//div[@class='dateRange']/text()").get()
                model_code = i.xpath(".//div[@class='modelCode']/text()").get()
                href = n.xpath(".//a/@href").get()
                car_info = {"model" : model_header, "submodel" : submodel, "date_range" : date_range, "model_code" : model_code, "region_name" : region_name}
                # yield{"car_info" : car_info, "href" : href}
                yield scrapy.Request(url = "https://www.ilcats.ru" + href, callback = self.parse_submodels, meta = {"car_info" : car_info})



    def parse_submodels(self, response):
        # submodel_xpath = response.xpath("//div[@class='caption']/a")
        car_info = response.request.meta['car_info']

        table = response.xpath("//table")

        table_headers = table.xpath(".//tr/th")
        # print("Length:", len(table_headers))
        headers = []
        for i in table_headers:
            headers.append(i.xpath(".//text()").get())
        # print(table_headers)
        # print("HEADERS", headers)
        table_rows = table.xpath(".//tr")
        # print(table_rows)

        for i in table_rows:
            # href = i.xpath(".//div[@class='caption']/@href").get()
            td = i.xpath(".//td")
            row_obj = {}
            row_obj.update(car_info)
            # row_obj.update({td[0].xpath(".//div[@class='caption']/@href")}).get()
            for n in range(len(table_headers)):

                try:
                    if td[0].xpath(".//@href"):
                        row_obj.update({"href" : td[0].xpath(".//@href").get()})
                    row_obj.update({headers[n] : td[n].xpath(".//div/text()").get()})
                except:
                    pass
                    # row_obj.update({headers[n] : td[n].xpath(".//div[@class='caption']/@href").get()})
            # print("ROW OBJ", row_obj)
            try:
                href = row_obj['href']
                yield scrapy.Request(url = "https://www.ilcats.ru" + href, callback = self.parse_category, meta = {"car_info" : row_obj})
                # yield{
                #         # "href" : i.xpath(".//@href").get()
                #         "row_obj" : row_obj
                #     }
            except:
                pass


    def parse_category(self, response):
        car_info = response.request.meta['car_info']
        category_xpath = response.xpath("//div[@class='name']/a")

        for i in category_xpath:
            href = i.xpath(".//@href").get()
            category_name = i.xpath(".//text()").get()
            yield scrapy.Request(url = "https://www.ilcats.ru" + href, callback = self.parse_subcategory, meta = {"car_info" : car_info, "category_name" : category_name})
            # yield{
            #     "href" : i.xpath(".//@href").get(),
            #     "car_info" : car_info
            # }



    def parse_subcategory(self, response):
        car_info = response.request.meta['car_info']
        category_name = response.request.meta['category_name']
        category_xpath = response.xpath("//div[@class='name']/a")

        for i in category_xpath:
            href = i.xpath(".//@href").get()
            subcategory_name = i.xpath(".//text()").get()
            category_tree = {"category_name" : category_name, "subcategory_name" : subcategory_name}
            yield scrapy.Request(url = "https://www.ilcats.ru" + href, callback = self.parse_part_page, meta = {"car_info" : car_info, "category_tree" : category_tree})
            # yield{
            #     "href" : i.xpath(".//@href").get(),
            #     "car_info" : car_info,
            #     "category_tree" : category_tree
            # }



    def parse_part_page(self, response):

        car_info = response.request.meta['car_info']
        category_tree = response.request.meta['category_tree']
        # print(car_info)
        image = response.xpath("//div[@class='Image']/img/@src").get()

        table_headers = []
        headers_xpath = response.xpath("//table[1]/tr[1]")
        for i in headers_xpath:
            th = i.xpath(".//th")
            for n in th:
                table_headers.append(n.xpath(".//text()").get())

        data_id = response.xpath("//table[1]/tr") #[starts-with(@class, 'Active']
        part_name_dict = {}
        for i in data_id: 
            data_id = (i.xpath(".//@data-id").get())
            part_name = (i.xpath(".//th[@colspan='4']/text()").get())
            if part_name is not None:
                part_name_dict.update({data_id : part_name}) # GETS PART NAME BASED ON DATA ID FROM A DIFFERENT BLOCK
        # print(part_name_dict)

        # parts_df = pd.DataFrame()
        # part_update_list = []
        parts_rows = response.xpath("//table[1]/tr")
        for i in parts_rows:
            td = i.xpath(".//td")
            data_id = i.xpath(".//@data-id").get()
            # print(data_id)
            try:
                part_name = (part_name_dict[data_id])
                part_row_data = {}
                part_information = {}
                part_row_data.update({"image" : image, "car_info" : json.dumps(car_info), "url" : response.url, "category_tree" : json.dumps(category_tree)})
                replaced_by_number = td.xpath(".//div[@class='replaceNumber']/a/text()").get()
                if replaced_by_number:
                    part_information.update({"replaced_by_number" : replaced_by_number})
                else:
                    part_information.update({"replaced_by_number" : None})
                # print(len(td))
                try:
                    for n in range(len(table_headers)):
                        # pass
                        part_information.update({table_headers[n] : td[n].xpath(".//text()").get(), "part_name" : part_name})
                        # parts_df = parts_df.append(pd.DataFrame(data = [part_row_data]))
                    # part_update_list.append(json.dumps(part_row_data))
                    # print("Response url:", part_row_data['url'])
                    part_row_data.update({"part_information" : json.dumps(part_information)})
                    # print("part_information:", part_row_data['part_information'])
                    # print("category_tree:", part_row_data['category_tree'])
                    # print("Column names:", part_row_data.keys())
                    # yield{"data" : part_row_data}

                    item_loader = IlcatsToyotaItem(
                        part_information = part_row_data['part_information'],
                        car_info = part_row_data['car_info'],
                        url = part_row_data['url'],
                        category_tree = part_row_data['category_tree'],
                        image = part_row_data['image']
                    )
                    # print("Insert")
                    yield item_loader

                except:
                    pass
                # print(part_row_data)
            except:
                pass

