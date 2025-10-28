from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class MySeleniumTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        opts = Options()
        opts.add_argument("--headless")
        cls.selenium = WebDriver(options=opts)
        cls.selenium.implicitly_wait(5)
        
        # Crear usuario staff isard/pirineus con permisos para Questions
        user = User.objects.create_user("isard", "isard@isardvdi.com", "pirineus")
        user.is_staff = True
        user.save()
        
        # Dar permisos para Questions (add y view)
        content_type = ContentType.objects.get(app_label='polls', model='question')
        add_perm = Permission.objects.get(content_type=content_type, codename='add_question')
        view_perm = Permission.objects.get(content_type=content_type, codename='view_question')
        user.user_permissions.add(add_perm, view_perm)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def test_staff_permissions(self):
        # Login como usuario staff isard/pirineus
        self.selenium.get(f"{self.live_server_url}/admin/login/")
        self.selenium.find_element(By.NAME, "username").send_keys('isard')
        self.selenium.find_element(By.NAME, "password").send_keys('pirineus')
        self.selenium.find_element(By.XPATH, '//input[@value="Log in"]').click()

        # Comprobar que SÍ puede crear Questions
        try:
            self.selenium.find_element(By.XPATH, "//a[contains(@href, '/admin/polls/question/add/')]")
        except NoSuchElementException:
            self.fail("No puede crear Questions")

        # Comprobar que NO puede crear Users
        try:
            self.selenium.find_element(By.XPATH, "//a[contains(@href, '/admin/auth/user/add/')]")
            self.fail("PUEDE crear Users - ERROR")
        except NoSuchElementException:
            pass  # Correcto - no puede crear users
