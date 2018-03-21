import os,inspect
from lxml import html
import requests
from lxml.html import fromstring, tostring
import json
from collections import defaultdict
import pprint

# Get the URL of required website
base_url = 'https://colnect.com/en/stamps/list/country/8662-Nepal/'
res = requests.get(base_url)
tree = html.fromstring(res.content)
dir_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

#Variants:
def variants(variant_link):
    group = []
    response1 = requests.get("https://colnect.com/%s/" % variant_link)
    tree1 = html.fromstring(response1.text)
    dl1 = tree1.xpath('//*[@id="plist_items"]/div/div/dl')
    for j, item in enumerate(dl1):
        # For Variant page:
        dt1 = item.xpath('//*[@id="plist_items"]/div' + str([j + 1]) + '/div[2]/dl/dt')
        for title1 in dt1:
            for value1 in title1.itersiblings():  # iterate over following siblings
                if value1.tag != 'dd':
                    break  # stop at the first element that is not a dd
                t_text = title1.text_content()
                t_text = t_text.split(':')[0]
                v_text = value1.text_content()
                if v_text.startswith('M'):
                    catalogcode = v_text
                    if 'Sn' in catalogcode:
                        sn = catalogcode.split(',')[1]
                        sn_value = sn.split(':')[1]
                        rem_np = sn_value.split(' ')[1]
                        group.append(rem_np)
    return v_text.replace(v_text, ', '.join(group))

# For all pages in Nepal stamps
page_number = tree.xpath("//div[@class='navigation_box']//a[.='»']/@href")[0].split("/")[-1]
for page in range(1, int(page_number) + 1):
    response = requests.get("https://colnect.com/en/stamps/list/country/8662-Nepal/page/%s/" % page)
    tree = html.fromstring(response.text)
    dl = tree.xpath('//*[@id="plist_items"]/div/div/dl')
    list_data = []
    for i, val in enumerate(dl):

        #For Scraping Details:
        dt = val.xpath('//*[@id="plist_items"]/div' + str([i + 1]) + '/div[2]/dl/dt')
        result = defaultdict(list)

        for title in dt:
            for value in title.itersiblings():  # iterate over following siblings
                if value.tag != 'dd':
                    break  # stop at the first element that is not a dd
                t_text = title.text_content()
                t_text = t_text.split(':')[0]
                v_text = value.text_content()

                if v_text.startswith('M'):
                    catalogcode = v_text
                    if 'Sn' in catalogcode:
                        sn = catalogcode.split(',')[1]
                        sn_value = sn.split(':')[1]
                        rem_np = sn_value.split(' ')[1]
                        result['Sn'].append(rem_np)
                    elif 'Yt' in catalogcode:
                        if 'Sn' not in catalogcode:
                            yt = catalogcode.split(',')[1]
                            yt_value = yt.split(':')[1]
                            rem_np1 = yt_value.split(' ')[1]
                            result['Sn'].append(rem_np1)

                elif '\t' in v_text:
                    slice1 = v_text.split('\t')[0]
                    result[t_text].append(slice1)
                    slice2 = v_text.split('\t')[1]
                    accu = slice2.split(':')[0]
                    low = slice2.split(':')[1]
                    low_space = slice2.split(' ')[1]
                    result[accu].append(low_space)

                elif '\r\n' in v_text:
                    slice3 = v_text.split('\r\n')[0]
                    slice4 = v_text.split('\r\n')[1]
                    joined = (slice3 + ' ' + slice4)
                    result[t_text].append(joined)

                elif '\u00bd' in v_text:
                    v_text.replace("\u00bd","½")


                elif '\u00be' in v_text:
                    v_text.replace("\u00be","¾")


                elif '\u00bc' in v_text:
                    v_text.replace("\u00bc","¼")


                elif '\u2019' in v_text:
                    v_text.replace("\u2019","'")


                elif '\u20a8' in v_text:
                    v_text.replace("\u20a8","Rs")


                elif 'Click to see variant' in v_text:
                    variant_link = val.xpath('//*[@id="plist_items"]/div' + str([i + 1]) + '/div/dl/dd[3]/strong/a/@href')
                    for elem in variant_link:
                        result[t_text].append(variants(elem))

                else:
                    result[t_text].append(v_text)

        # For Scraping the images:
        image = val.xpath('//*[@id="plist_items"]/div' + str([i + 1]) + '/div[1]/a/img')
        for link in image:
            #image1 = link.xpath('./@src') or link.xpath('./@data-src')
            image1 = link.xpath("./@data-src")[0].split("/")[-5]
            image2 = link.xpath("./@data-src")[0].split("/")[4:]
            image2 = '/'.join(image2)
            img = str(image1) + '/b/' + str(image2)
            image = "http://" + img
            #print(image)

            r2 = requests.get(image)
            img = os.path.split(image)[0]
            image_name = img1 = os.path.split(img)[1] + os.path.split(image)[1]
            # print(image_name)
            #with open("NepalStamps/" + image_name, "wb") as f:
                #f.write(r2.content)

        result['Image'].append(dir_path + "/NepalStamps/" + image_name)
        details = dict(result)

        dic1 = {k: v for k, v in details.items() if k != 'Buy Now'}
        data = {k: (''.join(v)) for k, v in dic1.items()}
        list_data.append(data)
    pprint.pprint(list_data)
    print('\n')
    with open('stampData.json', 'a') as f:
        json.dump(list_data, f, sort_keys=True, indent=2)
