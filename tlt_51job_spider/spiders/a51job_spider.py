# -*- coding: utf-8 -*-
import re

import scrapy


class A51jobSpiderSpider(scrapy.Spider):
    name = "51job"
    start_urls = [
        'https://search.51job.com/list/000000,000000,0000,00,9,99,%2520,2,1.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=',
    ]

    def parse(self, response):
        for jobitem in response.xpath("//div[@id='resultList']//div[@class='el']"):
            yield scrapy.Request(jobitem.xpath("p/span/a/@href").get(), callback=self.jobPageParse)
            # yield {
            #     'job_title': jobitem.xpath("p/span/a/@title").get(),
            #     'job_url': jobitem.xpath("p/span/a/@href").get(),
            #     'company_title': jobitem.xpath("span[@class='t2']/a/@title").get(),
            #     'company_url': jobitem.xpath("span[@class='t2']/a/@href").get(),
            #     'location':jobitem.xpath("span[@class='t3']/text()").get(),
            #     'salary':jobitem.xpath("span[@class='t4']/text()").get(),
            #     'date': jobitem.xpath("span[@class='t5']/text()").get(),
            # }

        next_page = response.xpath("//*[contains(text(),'下一页')]/@href").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def jobPageParse(self, response):
        categories = response.xpath("//*[contains(text(),'职能类别：')]/..//a//text()").getall()
        salaryString = response.xpath("//div[@class='in']//div[@class='cn']/strong/text()").get()

        featuresUnformated = response.xpath("//p[@class='msg ltype']/text()").getall()
        features = stringListParser(featuresUnformated)

        yield {
            "website_url": response.url,
            "job_title": ''.join(response.xpath("//div[@class='in']//div[@class='cn']/h1/text()").getall()).replace(
                '\r', '').replace('\n', '').replace('\t', ''),
            "max_salary": maxSalaryParser(salaryString),
            "min_salary": minSalaryParser(salaryString),
            "experience_year": experienceYearParser(features),
            "education_needed": educationNeededParser(features),
            "publish_date": publishDateParser(features),
            "number_of_people": numberOfPeopleParser(features),
            "province": features[0],
            "city": features[0],
            "district": features[0],
            "position_info": ''.join(response.xpath("//div[@class='tCompany_main']//text()").getall()).replace('\r',
                                                                                                               '').replace(
                '\n', '').replace('\t', '').replace('\xa0',''),
            "job_advantage_tag": response.xpath("//*[@class='sp4']/text()").getall(),
            "functional_category": stringListParser(categories),
            "key_words": response.xpath("//*[contains(text(),'关键字：')]/..//a//text()").getall(),
            "company": {

                "company_id": response.xpath("//*[@class='com_name ' or @class='com_name himg']/@href").get().split('/')[4].replace('.html', ''),
                "company_name": response.xpath("//*[@class='com_name ']/p/text()").get(),
                "company_type": response.xpath("//*[@class='i_flag']/../@title").get(),
                "company_scale": response.xpath("//*[@class='i_people']/../@title").get(),
                "company_industry": response.xpath("//*[@class='i_trade']/../@title").get()
            }
        }


def stringListParser(categories):
    result = []
    for category in categories:
        category = category.replace('\r', '').replace('\n', '').replace('\t', '').replace('\xa0', '')
        result.append(category)
    return result


def minSalaryParser(salayString):
    if salayString == None:
        return 0

    if salayString.find('-') >= 0:
        temp = re.split("/|-", salayString)
        number = float(temp[0])
        unit = re.sub('\d+', '', temp[1]).replace('.', '')
        every = temp[2]
        if unit == '千':
            number *= 1000;
        elif unit == '万':
            number *= 10000;
        time = 1
        if every == '天':
            time = 365;
        elif every == '月':
            time = 12
        elif every == '年':
            time = 1
        return int(time * number);
    elif salayString.find('以下') >= 0:
        return 0
    else:

        temp = re.split("/|-", salayString)
        number = float(re.findall(r'-?\d+\.?\d*e?-?\d*?', temp[0])[0])
        every = temp[1]
        unit = re.sub('\d+', '', temp[0]).replace('.', '')
        if unit == '千':
            number *= 1000
        elif unit == '万':
            number *= 10000
        elif unit == '元':
            number *= 1
        time = 1
        if every == '天':
            time = 365
        elif every == '月':
            time = 12
        elif every == '年':
            time = 1
        return int(time * number)


def maxSalaryParser(salayString):
    if salayString == None:
        return 0
    print(salayString)
    if salayString.find('-') >= 0:
        temp = re.split("/|-", salayString)
        number = float(re.findall(r'-?\d+\.?\d*e?-?\d*?', temp[1])[0])
        unit = re.sub('\d+', '', temp[1]).replace('.', '')
        every = temp[2]
        if unit == '千':
            number *= 1000
        elif unit == '万':
            number *= 10000
        elif unit == '元':
            number *= 1
        time = 1
        if every == '天':
            time = 365
        elif every == '月':
            time = 12
        elif every == '年':
            time = 1
        return int(time * number)
    elif salayString.find('以下') >= 0:
        temp = re.split("/|-", salayString.replace('以下', ''))
        number = float(re.findall(r'-?\d+\.?\d*e?-?\d*?', temp[0])[0])
        every = temp[1]
        unit = re.sub('\d+', '', temp[0]).replace('.', '')
        if unit == '千':
            number *= 1000
        elif unit == '万':
            number *= 10000
        elif unit == '元':
            number *= 1
        time = 1
        if every == '天':
            time = 365
        elif every == '月':
            time = 12
        elif every == '年':
            time = 1
        return int(time * number)
    else:
        temp = re.split("/|-", salayString)
        number = float(re.findall(r'-?\d+\.?\d*e?-?\d*?', temp[0])[0])
        every = temp[1]
        unit = re.sub('\d+', '', temp[0]).replace('.', '')
        if unit == '千':
            number *= 1000
        elif unit == '万':
            number *= 10000
        elif unit == '元':
            number *= 1
        time = 1
        if every == '天':
            time = 365
        elif every == '月':
            time = 12
        elif every == '年':
            time = 1
        return int(time * number)


def experienceYearParser(features):
    experience_str = ''
    for feature in features:
        if feature.find('经验') >= 0:
            experience_str = feature
            break

    print(experience_str)

    if experience_str.find('无工作经验') >= 0:
        return 0
    elif experience_str.find('-')>=0:
        return experience_str.split('-')[1].replace('年经验', '')
    else:
        return experience_str.replace('年经验', '')
    # return int(re.findall(r'-?\d+\.?\d*e?-?\d*?', experience_str)[0])


def educationNeededParser(features):
    for feature in features:
        if feature.find('本科') >= 0:
            return feature
        if feature.find('大专') >= 0:
            return feature
        if feature.find('中专') >= 0:
            return feature
        if feature.find('中技') >= 0:
            return feature
        if feature.find('高中') >= 0:
            return feature
        if feature.find('初中及以下') >= 0:
            return feature
        if feature.find('士') >= 0:
            return feature
    return ''


def publishDateParser(features):
    publish_date_str = ''
    for feature in features:
        if feature.find('发布') >= 0:
            publish_date_str = feature
            break

    return '2019-' + publish_date_str.replace('发布', '')


def numberOfPeopleParser(features):
    number_of_peopel_str = ''
    for feature in features:
        if feature.find('人') >= 0 and feature.find('招') >= 0:
            number_of_peopel_str = feature
            break

    if number_of_peopel_str.find('招若干人') >= 0:
        return 0

    return int(re.findall("\d+", number_of_peopel_str)[0])

#
# def province(features):
#
#
# def city(features):
#
#
# def district(features):
