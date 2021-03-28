from datetime import datetime
from time import sleep

from selenium.common.exceptions import NoSuchElementException

from browser import Browser
from config import GOOGLE_PW, GOOGLE_ID, COMMENT
from model.enums import Language
from model.video import Video


class Main(Browser):
    url = "https://www.youtube.com/gaming/trending"

    def __init__(self, language=Language.EN):
        super().__init__()
        self.language = language
        self.start_video = 0
        self.scroll_down_number = 1
        self.index = 0

    def process(self):
        self.chrome_options.add_argument("--start-maximized")
        self.start_chrome()
        self.login()
        self.click_videos()

    def login(self):
        sign_in_text = "Sign in" if self.language == Language.EN else "로그인"
        sign_in_button = self.web_driver.find_element_by_css_selector(f"[aria-label='{sign_in_text}']")
        sign_in_button.click()
        id_input = self.web_driver.find_element_by_css_selector("input[type='email']")
        id_input.send_keys(GOOGLE_ID)
        next_button = self.web_driver.find_element_by_css_selector("button[jsname='LgbsSe']")
        next_button.click()
        self.web_driver_wait((self.By.CSS_SELECTOR, "input[type='password']"))
        password_input = self.web_driver.find_element_by_css_selector("input[type='password']")
        password_input.send_keys(GOOGLE_PW)
        next_button = self.web_driver.find_element_by_css_selector("button[jsname='LgbsSe']")
        next_button.click()

    def click_videos(self):
        while True:
            try:
                self.web_driver_wait((self.By.TAG_NAME, "ytd-grid-video-renderer"))
                videos = self.web_driver.find_elements_by_tag_name("ytd-grid-video-renderer")
                video = videos[self.index]
                video.click()
                sleep(2)
                self.mute_sound()
                self.insert_comment()
                self.insert_video_info_into_db()
                self.web_driver.back()
                self.index += 1
                # sleep(3)
            except IndexError as e:
                self.save_web_page("page")

    def mute_sound(self):
        try:
            mute_button = self.web_driver.find_element_by_css_selector("button[aria-label='Mute (m)']")
            mute_button.click()
        except NoSuchElementException:
            return False

    def insert_comment(self):
        self.web_driver.execute_script("window.scrollTo(0, 500)")
        self.web_driver_wait((self.By.TAG_NAME, "ytd-comment-simplebox-renderer"))
        comment_box = self.web_driver.find_element_by_tag_name("ytd-comment-simplebox-renderer")
        comment_box.click()
        self.web_driver_wait((self.By.ID, "contenteditable-root"))
        comment_input = self.web_driver.find_element_by_id("contenteditable-root")
        comment_input.send_keys(COMMENT)
        comment_text = "Comment" if self.language == Language.EN else "댓글"
        self.web_driver_wait((self.By.CSS_SELECTOR, f"paper-button[aria-label='{comment_text}']"))
        comment_button = self.web_driver.find_element_by_css_selector(f"paper-button[aria-label='{comment_text}']")
        # comment_button.click()

    def insert_video_info_into_db(self):
        title = self.web_driver.find_element_by_css_selector("h1.title").text
        user_container = self.web_driver.find_element_by_tag_name("ytd-video-owner-renderer").text
        channel_name = user_container.split("\n")[0].strip()

        url = self.web_driver.current_url
        Video(
            title,
            channel_name,
            url,
            COMMENT,
            datetime.now()
        ).insert()

    def scroll_down(self):
        # for i in range(self.scroll_down_number):
        scroll_height = self.web_driver.execute_script("return document.documentElement.scrollHeight")
        self.web_driver.execute_script(f"window.scrollTo(0, {scroll_height})")
        sleep(5)


if __name__ == '__main__':
    Main(Language.EN).process()
