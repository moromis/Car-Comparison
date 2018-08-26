from bs4 import BeautifulSoup
import requests, csv, re, threading
from pathlib import Path


# IMPORTANT:
# Toggle this variable depending on if you wanted multi-threaded
# or not. You probably want multi-threaded in production only, and
# not when you're testing, so your breakpoints don't get fsvked
multi_threaded = True

# The domain we will be scraping from. It's important to note
# that the entire scraping process differs based on a website's
# structure, so this can't actually be changed, it's just here
# so it's global and doesn't need to be rewritten
domain = "https://www.autobytel.com"

# The data points we're interested in. These will be both the column
# names in our exported CSV files as well as what we search for on
# the specs pages - so these should be exact. We can always rename
# them later
fieldnames =    [
                'make', 'model', 'year', 'city', 'highway',\
                'fuel tank capacity', 'total seating capacity',\
                'max cargo capacity', 'drive type', 'cylinder configuration',\
                'engine liters', 'horsepower', 'transmission', 'torque', 'abs',\
                'size'
                ]

def init_file_header (file_name):
    #header fields
    f = open(file_name,'w', newline='')
    writer = csv.DictWriter(f, fieldnames= fieldnames)
    writer.writeheader()
    f.close()

def print_to_file (file_name, data_to_write):

    file = Path(file_name)
    if not file.exists():
        init_file_header(file_name)

    f = open(file_name, 'a+', newline='')
    writer = csv.DictWriter(f, fieldnames = fieldnames)
    writer.writerow(data_to_write)
    f.close()
        
def get_all_model_links (car_make):

    # manufacture a url based on the car model
    url = "%s/%s" % (domain, car_make.lower())

    # preallocate our results list
    result_list = list()

    # build and execute the request for the webpage
    # through beautifulsoup
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')

    # find the main div that we're interested in
    main_div = soup.find('div', {'class': 'temp2-col-main'})

    # find all the sections for the car model we're interested in
    # these will be things like `%car model% SUVs`, `%car model%
    # Luxury Cars`, etc.
    model_sections = main_div.find_all('div', {'class': 'general-list'})

    # we're only interested in SUVs
    # it wouldn't be too hard to change this to work off a list
    # of nouns you're interested in, and then do a second for loop
    # to iterate through both the car type and then the links for
    # that car type
    suvs = list()

    for section in model_sections:
        header = section.find('h2', {'class': 'header-label'})
        if ('suv' in header.text.lower()):
            suvs.append(section.find('ul').find_all('li'))

    # find each car model link
    if (suvs):
        for suv_type in suvs:
            for list_item in suv_type:
                links = list_item.find_all('a')
                for link in links:
                    html_url = "%s%s" % (domain, link['href'])
                    result_list.append(html_url)

    else:
        print('ERROR: No SUVs were found at %s - skipping' % (url))

    return result_list

def get_all_specs_links (model_links):

    # preallocate our results list
    result_list = list()

    for url in model_links:

        # build and execute the request for the webpage
        # through beautifulsoup
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html5lib')

        model_years_div = soup.find('div', {'class': 'grid-2-5'})
        model_year_lis = model_years_div.find_all('li')

        # find each car model year specification link
        if (model_year_lis):
            for list_item in model_year_lis:
                links = list_item.find_all('a')
                for link in links:
                    spec_url = "%s%sspecifications/" % (domain, link['href'])
                    result_list.append(spec_url)

        else:
            print('ERROR: No model years were found' % (url))

    return result_list

def clean(st):
    l = ['\n','\t', ':']
    for c in l:
        st = st.replace(c,'')
    return st.lower()

def scrape_specs(url):
    # Given a full URL path to a html page scape the data from the page and
    # return a dictionary containig the various elements
    
    ret_data = dict()
    
    r = requests.get(url)
    soup = BeautifulSoup(r.text,'html5lib')

    # put initial data (make, model, year) into the dictionary
    ret_data['make'] = soup.find(itemprop="manufacturer").get("content")
    ret_data['model'] = soup.find(itemprop="model").get("content")
    ret_data['year'] = soup.find(itemprop="releaseDate").get("content")

    main_div = soup.find('div', {'class': 'subnav-content'} )
    data_sections = main_div.find_all('ul', {'class': 'list-1-2'})
    
    for section in data_sections:
        data_points = section.find_all('li')
        for data_point in data_points:
            title = clean(data_point.find('span', {'class': 'x-smaller'}).text)
            data = clean(data_point.find('span', {'class': 'smaller'}).text)
            if title in fieldnames:
                ret_data[title] = data

    return ret_data
     
def run_scrape(car_make):

    print('[+][%s] Gathering all model links...' % car_make.upper())
    model_links = get_all_model_links(car_make)

    print('[+][%s] Gathering all specs links...' % car_make.upper())
    specs_links = get_all_specs_links(model_links)
    
    #set up the headers for the csv file
    print('[+][%s] Creating the csv file...' % car_make.upper())
    f_name = "%s_specs.csv" % car_make.lower()

    #for each link in the list above scrape the data
    # counter = 0
    print('[+][%s] Starting scraping data for %s link(s)' % (car_make.upper(), len(specs_links)))
    for each_link in specs_links:
            specs_dictionary = scrape_specs(each_link)
            print_to_file(f_name, specs_dictionary)
    print('[+][%s] Finished scraping for %s ' % (car_make.upper(), car_make))
    print('[+][%s] Your file\'s name is: %s' % (car_make.upper(), f_name))


def run_threaded(func_job):
    thread_job = threading.Thread(target=func_job)
    thread_job.start()

def main(car_makes):

    if (multi_threaded):
        jobs = []
        for make in car_makes:
            thread = threading.Thread(target=run_scrape,args=(make,))
            jobs.append(thread)
        for job in jobs:
            job.start()

        for job in jobs:
            job.join()
    else:
        for car_make in car_makes:
            run_scrape(car_make)
		
car_makes_list = ['Acura', 'Alfa-Romeo', 'Aston-Martin', 'Audi', 'Bentley', 'BMW', 'buick', 'Cadillac',\
                'Chevrolet', 'Chrysler', 'Citroen', 'Dacia', 'Daewoo', 'Dodge', 'Ferrari', 'Fiat', 'Ford', \
                'genesis', 'gmc', 'infiniti', 'lincoln', 'lotus', 'ram',\
                'Honda', 'Hyundai', 'Jaguar', 'Jeep', 'Kia', 'Lamborghini', 'Lancia', 'Land', 'Rover', \
                'Lexus', 'Maserati', 'Mazda', 'McLaren', 'Mercedes-Benz', 'Mini', 'Mitsubishi',\
                'Nissan', 'Opel', 'Peugeot', 'Porsche', 'Renault', 'Rolls-Royce', 'land-rover', 'Saab', \
                'Seat', 'Skoda', 'Smart', 'Subaru', 'suzuki', 'Tesla', 'Toyota', 'Vauxhall', 'Volkswagen', 'Volvo']


main(car_makes_list)
