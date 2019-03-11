# -*- coding:utf-8 -*-
import scrapy
import re


class ZhilianSpider(scrapy.Spider):
    name = "zhilian_spider"

    def start_requests(self):
        url = "https://jobs.zhaopin.com/"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        content_lists = response.css('div.main div[class="content clearfix"] .rightTab .content-list')
        for li in content_lists:
            urls = li.css('.listcon a::attr(href)').getall()
            for url in urls:
                yield response.follow(url, self.parse_detail_job)

    def parse_detail_job(self, response):

        is_page = response.css("div.returnpage h1::text").get() is None

        if is_page:
            urls = response.css(
                '.search_list div[class="details_container bg_container "] span.post a::attr(href)').getall()
            next_url = response.css('span.search_page_next a::attr(href)').get()
            yield response.follow(next_url, self.parse_detail_job)

            for url in urls:
                yield scrapy.Request(url, callback=self.parse_detail_info)

    def parse_detail_info(self, response):

        website_url = response.url
        job_title = response.css("h1.l::text").get()
        salary = response.css("div.info-money strong::text").get().split('元')[0].split('-')

        try:
            max_salary = int(salary[1]) * 12
            min_salary = int(salary[0]) * 12
        except:
            max_salary = int(salary[0]) * 12
            min_salary = int(salary[0]) * 12

        info = response.xpath("//*[@class='info-three l']/span").getall()
        experience_year = re.match('<span>(.*?)</span>', info[1]).group(1)

        education_needed = re.match('<span>(.*?)</span>', info[2]).group(1)
        number_of_people = re.match('<span>招(.*?)人</span>', info[3]).group(1)
        number_of_people = int(number_of_people)

        province = ""
        city = re.match('<span><a.*?>(.*?)</a>(.*?)</span>', info[0]).group(1)
        district = re.match('<span><a.*?>(.*?)</a>(.*?)</span>', info[0]).group(2).strip('-')

        position_info = response.xpath("//*/div[@class='pos-ul']/p/span/text()").getall()
        result = ""
        for position in position_info:
            result += position
        position_info = result

        job_advantage_tags = response.css('script:contains("JobWelfareTab")::text').get().split('\n')
        job_advantage_tag = job_advantage_tags[len(job_advantage_tags) - 3].strip(" ").strip("\r")
        job_advantage_tags = re.match("var.*?'(.*?)';", job_advantage_tag).group(1)
        job_advantage_tag = job_advantage_tags.split(",")

        functional_category = response.css("span.pos-name a::text").get().split("/")

        company_href = response.css("div.promulgator-info h3 a::attr(href)").get().split('/')
        company_htm = company_href[len(company_href) - 1].split('.')
        company_ht = company_htm[0].split('_')
        company_id = company_ht[len(company_ht) - 1]
        company_id = "ZL_" + company_id

        company_name = response.css("div.promulgator-info h3 a::text").get()

        company_info = response.css("ul.promulgator-ul li")
        company_type = company_info.css("strong::text").getall()[0]
        company_scale = company_info.css("strong::text").getall()[1]
        company_industry = company_info.css("strong a::text").get()

        yield {
            "website_url": website_url,
            "job_title": job_title,
            "max_salary": max_salary,
            "min_salary": min_salary,
            "experience_year": experience_year,
            "education_needed": education_needed,
            "publish_date": "2019-03-06",
            "number_of_people": number_of_people,
            "province": province,
            "city": city,
            "district": district,
            "position_info": position_info,
            "job_advantage_tag": job_advantage_tag,
            "functional_category": functional_category,
            "key_words": [
                ""
            ],
            "compay": {
                "company_id": company_id,
                "company_name": company_name,
                "company_type": company_type,
                "company_scale": company_scale,
                "company_industry": company_industry
            },
        }
