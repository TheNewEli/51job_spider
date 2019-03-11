# -*- coding: utf-8 -*-
import scrapy

class LiepinSpider(scrapy.Spider):
    name = "lpTalent"

    def start_requests(self):
        url = 'https://www.liepin.com/'
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        industry_list = response.css("ul[data-selector='hot-job'] div a::attr(href)").extract()
        print(industry_list)
        for next_url in industry_list:
            next_url = next_url.split('m/')[0] + 'm/career/' + next_url.split('m/')[1]
            yield scrapy.Request(url=next_url,callback=self.parse_detail_job)

    def parse_detail_job(self, response):
        item_urls = response.css(".job-info a[href*='https://www.liepin.com/job/']::attr(href)").extract()
        next_url = 'https://www.liepin.com' + response.xpath("//*[contains(text(),'下一页')]/@href").extract()[0]
        yield scrapy.Request(url=next_url, callback=self.parse_detail_job)
        for item_url in item_urls:
            yield scrapy.Request(url=item_url,callback=self.parse_detail_info)

    def parse_detail_info(self, response):
        website_url = response.url
        #工作名称
        job_title = response.css(".title-info h1::text").extract_first()
        #薪资
        salary = response.css(".job-item-title::text").extract_first()
        if('面议' in salary):
            max_salary = -1
            min_salary = -1
        else:
            max_salary = int(salary.split("万")[0].split("-")[1] + '0000')
            min_salary = int(salary.split("万")[0].split("-")[0] + '0000')
        #所需经验
        experience_year = response.css(".job-qualifications span::text").extract()[1]
        #所需学历
        education_needed = response.css(".job-qualifications span::text").extract()[0]
        #发布时间
        publish_date = response.css("time::attr(title)").extract_first().replace('年','-').replace('月','-').replace('日','')
        #招聘人数
        number_of_people = 1
        # 省市区
        place = response.css(".basic-infor a::text").extract_first()
        if('-' in place):
            province = ''
            city = place.split('-')[0]
            district = place.split('-')[1]
        else:
            province = ''
            city = place
            district = ''
        position_info = ''.join(response.xpath("//*[contains(text(),'职责描述')]//text()").getall()).strip()
        job_advantage_tag = response.css(".comp-tag-box ul span::text").extract()
        #职能类别处理
        str = response.css(".crumbs-link li a::text").extract_first()[:-2]
        functional_category = response.css(".crumbs-link li a::text").extract()[1][:-2].replace(str,'').split('/')
        #公司信息
        company_id = 'LP' + response.css(".about-position a::attr(href)").extract_first().split('/')[-2]
        company_name = response.css(".about-position a::text").extract_first()
        company_type = ''
        company_scale = ''
        company_industry = ''
        key_words = ['','']

        yield {
            "website_url": website_url,
            "job_title": job_title,
            "max_salary": max_salary,
            "min_salary": min_salary,
            "experience_year": experience_year,
            "education_needed": education_needed,
            "publish_date": publish_date,
            "number_of_people": number_of_people,
            "province": province,
            "city": city,
            "district": district,
            "position_info": position_info,
            "job_advantage_tag": job_advantage_tag,
            "functional_category": functional_category,
            "key_words": key_words,
            "company": {
                "company_id":company_id,
                "company_name": company_name,
                "company_type": company_type,
                "company_scale": company_scale,
                "company_industry": company_industry
            }
        }
        print(website_url)
        print(job_title)
        print(min_salary)
        print(max_salary)
        print(experience_year)
        print(education_needed)
        print(publish_date)
        print(number_of_people)
        print(province)
        print(city)
        print(district)
        print(position_info)
        print(job_advantage_tag)
        print(str)
        print(functional_category)
        print(company_id)
        print(company_name)