from getpass import getpass  # For getting the User's password
from selenium import webdriver  # Gives access to the browser
from selenium.webdriver.support.ui import WebDriverWait  # Allows the browser to pause
from selenium.webdriver.support import expected_conditions as ec  # Make browser get conditions
from selenium.webdriver.common.by import By  # Get methods of identifying elements
import selenium.common.exceptions as exceptions  # The exceptions module of Selenium
import json  # For reading credentials file

credentials_file_name = '.credentials.json'

def setup():
    print('Opening Browser')
    browser = webdriver.Safari()
    print('Browser opened')


def wait_for(text, delay=10, by=By.XPATH, check_again_limit=3, one_as_list=True):
    check = 0
    try:
        elements = WebDriverWait(browser, delay).until(ec.presence_of_all_elements_located((by, text)))
    except exceptions.TimeoutException:
        if check < check_again_limit:
            elements = WebDriverWait(browser, delay).until(ec.presence_of_all_elements_located((by, text)))
        else:
            return None
        check += 1
    if len(elements) == 0:
        return None
    elif len(elements) == 1:
        if one_as_list:
            return browser.find_elements(by, text)
        else:
            return elements[0]
    return elements


# Logging in function
def login_info():
    try:
        # Try to open the file in read mode
        # if it doesn't exist it throws an exception
        with open(credentials_file_name) as credentials_file:
            credentials = json.load(credentials_file)
            user_name = credentials['user']
            user_pass = credentials['password']
    except FileNotFoundError:
        with open(credentials_file_name, 'w+') as credentials_file:
            # For sure the file had nothing, therefore
            user_name = str(input("Username: "))
            user_pass = getpass()
            json.dump(
                {'user': user_name,
                 'password': user_pass
                 },
                credentials_file
            )

    return user_name, user_pass


def login(email_elem_xpath, password_elem_xpath, submit_elem_xpath):
    email_elem = wait_for(email_elem_xpath, one_as_list=False)
    password_elem = wait_for(password_elem_xpath, one_as_list=False)
    print('At the login page')
    username, password = login_info()
    email_elem.send_keys(username)
    print('Username entered')
    password_elem.send_keys(password)
    print('Password entered')
    wait_for(submit_elem_xpath, one_as_list=False).click()
    print('Logging in')


def get_course_links():
    wait_for('social-app-links-div', by=By.CLASS_NAME)
    course_elements = wait_for('enter-course', by=By.CLASS_NAME, one_as_list=False)
    course_links = []
    print('Getting course links')
    for course_elem in course_elements:
        course_links.append(course_elem.get_attribute('href'))
    return course_links


def only_space(word_group):
    for c in word_group:
        if c is not " ":
            return False
    return True


def strip_extra_whitespace(text):
    actual_text = ''
    word_groups_1 = text.split('\n')
    for word_groups_2 in word_groups_1:
        word_groups_2 = word_groups_2.split(' ')
        for word_group in word_groups_2:
            if not only_space(word_group):
                actual_text += word_group + ' '
    return actual_text[:-1]  # Remove additional white space


def get_saved_courses():
    try:
        # Try to open the file in read mode
        # if it doesn't exist it throws an exception
        with open(courses_file_name) as courses_file:
            saved_courses = json.load(courses_file)
    except FileNotFoundError:
        # The file didn't exist therefore we should create it
        open(courses_file_name, 'w+')
        saved_courses = {}
    return saved_courses


def get_unchecked_links(course_links, saved_courses):
    unchecked_links = []
    for course_link in course_links:
        if course_link[:-7] not in str(saved_courses):
            unchecked_links.append(course_link)
    return unchecked_links


def get_course_data(course_links):
    courses = get_saved_courses()
    course_links = get_unchecked_links(course_links, courses)
    for i in range(len(course_links)):
        print('Going to course', i + 1, 'of', len(course_links))
        browser.get(course_links[i])
        course_title = wait_for('page-title', by=By.CLASS_NAME, one_as_list=False).text
        courses[course_title] = {}
        print(course_title)
        main_xpath = '//*[@id="course-outline-block-tree"]/li'
        section_elements = wait_for(main_xpath + '/button/h3')
        for i in range(len(section_elements)):
            section_title = strip_extra_whitespace(section_elements[i].text)
            courses[course_title][section_title] = {}
            sub_section_xpath = main_xpath + '[' + str(i + 1) + ']/ol/li'
            sub_section_elements = wait_for(sub_section_xpath + '/button/h4')
            for j in range(len(sub_section_elements)):
                sub_section_title = strip_extra_whitespace(sub_section_elements[j].text)
                courses[course_title][section_title][sub_section_title] = {}
                item_xpath = sub_section_xpath + '[' + str(j + 1) + ']/ol/li/a'
                item_links = wait_for(item_xpath)
                items = wait_for(item_xpath + '/div/div')
                for k in range(len(items)):
                    item_title = strip_extra_whitespace(items[k].text)
                    item_link = item_links[k].get_attribute('href')
                    courses[course_title][section_title][sub_section_title][item_title] = item_link

    return courses


def main():
    print('Going to Website')
    browser.get('https://edx.org/dashboard')
    login(
        '//*[@id="login-email"]',
        '//*[@id="login-password"]',
        '//*[@id="login"]/button'
    )
    course_links = get_course_links()
    courses = get_course_data(course_links)
    with open(courses_file_name, 'w') as courses_file:
        json.dump(courses, courses_file, indent=4)


main()

print('Closing Browser')
browser.quit()
print('Browser closed')
