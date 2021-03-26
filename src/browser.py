from time import sleep

from config import WEB_DRIVER_WAIT_TIME
from selenium import webdriver
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from utils.custom_error import NoPopupError
from webdriver_manager.chrome import ChromeDriverManager
from abc import ABCMeta
from typing import Optional


class Browser(metaclass=ABCMeta):
    def __init__(self):
        self.EC = expected_conditions
        self.By = By
        self.__url = None
        self.__web_driver: Optional[webdriver.Chrome] = None

    @property
    def web_driver(self):
        self.__raise_property(self.__web_driver)
        return self.__web_driver

    @property
    def url(self):
        if self.__url is None:
            raise NotImplementedError
        return self.__url

    @url.setter
    def url(self, url):
        self.__url = url

    def __raise_property(self, value):
        if value is None:
            raise ValueError("start_chrome 함수를 호출한 뒤에 사용가능합니다.")

    def start_chrome(
            self,
            show_window: bool = True,
    ):
        chrome_options = self.__set_chrome_options(show_window)
        try:
            web_driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
            web_driver.get(self.url)
            self.__web_driver = web_driver
            return self
        except PermissionError:
            return self.start_chrome(show_window)

    def __set_chrome_options(self, show_window: bool):
        chrome_options = webdriver.ChromeOptions()
        if not show_window:
            chrome_options.add_argument("--headless")
        return chrome_options

    def clear_child_window(self, remain_url=None) -> None:
        is_exist_child = 1 < len(self.__web_driver.window_handles)
        if is_exist_child:
            main_window = self.__web_driver.window_handles[0]
            for handle in self.__web_driver.window_handles:
                self.__web_driver.switch_to.window(handle)
                if remain_url is None:
                    main_window = self.__terminate_all_except_match_url_window(handle, self.url)
                else:
                    main_window = self.__terminate_all_except_match_url_window(handle, remain_url)
            return self.__web_driver.switch_to.window(main_window)

    def __terminate_all_except_match_url_window(self, handle, url):
        main_window = self.__web_driver.window_handles[0]
        if self.__web_driver.current_url == url:
            main_window = handle
        else:
            self.__web_driver.close()
        return main_window

    def web_driver_wait(
            self,
            target: tuple,
            wait_type=expected_conditions.element_to_be_clickable
    ) -> WebDriverWait:
        return WebDriverWait(self.__web_driver, WEB_DRIVER_WAIT_TIME).until(
            wait_type(target)
        )

    def close_alert(self, is_accept: bool, callback=lambda alert: alert):
        try:
            alert = self.__web_driver.switch_to.alert
            result = callback(alert)
            if is_accept:
                alert.accept()
            else:
                alert.dismiss()
            return result
        except NoAlertPresentException:
            pass

    def switch_window(self, current_window_close: bool = False):
        current_window = self.__web_driver.current_window_handle
        if current_window_close:
            self.__web_driver.close()
        for handle in self.__web_driver.window_handles:
            if handle != current_window:
                return self.__web_driver.switch_to.window(handle)
        raise NoPopupError()

    def wait_page_load(self):
        count = 0
        while True:
            web_condition = self.__web_driver.execute_script("return document.readyState")
            if web_condition == "complete":
                return
            if count > 20:
                raise TimeoutError("페이지가 로딩되지 않았습니다.")
            count += 1
            sleep(0.2)

    def is_find_element(self, by: By, path: str) -> bool:
        try:
            if by == self.By.XPATH:
                self.web_driver.find_element_by_xpath(path)
            elif by == self.By.ID:
                self.web_driver.find_element_by_id(path)
            elif by == self.By.CLASS_NAME:
                self.web_driver.find_element_by_class_name(path)
            elif by == self.By.NAME:
                self.web_driver.find_element_by_name(path)
            elif by == self.By.LINK_TEXT:
                self.web_driver.find_element_by_link_text(path)
            elif by == self.By.PARTIAL_LINK_TEXT:
                self.web_driver.find_element_by_partial_link_text(path)
            elif by == self.By.TAG_NAME:
                self.web_driver.find_element_by_tag_name(path)
            return True
        except NoSuchElementException:
            return False
