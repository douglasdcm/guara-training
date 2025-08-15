import pytest
from selenium import webdriver
from guara.transaction import Application, IAssertion
from guara import it
from guara.transaction import AbstractTransaction
from selenium.webdriver.common.by import By


def hard_wait(seconds: int):
    """A simple hard wait to ensure the page is loaded."""
    import time

    time.sleep(seconds)


class AddTask(AbstractTransaction):
    """Add a task with the given title and return the result message.

    Args:
        with_title (str): The title of the task to be added.
    Returns:
        str: The message confirming the task creation, including its ID.
    """

    def __init__(self, driver):
        self._driver: webdriver.Chrome = driver
        self._task_id = None

    def do(self, with_title: str):
        self._driver.get("file:///home/douglas/repo/guara-training/index.html")
        self._driver.find_element(By.ID, "taskTitle").send_keys(with_title)
        self._driver.find_element(By.CSS_SELECTOR, "body > section:nth-child(2) > button").click()
        result = self._driver.find_element(By.ID, "addMessage").text
        self._task_id = result.replace("The task with ID ", "").replace(" was created", "")
        return result

    def undo(self):
        self._driver.find_element(By.ID, "removeId").send_keys(self._task_id)
        self._driver.find_element(By.CSS_SELECTOR, "body > section:nth-child(4) > button").click()
        self._driver.find_element(By.ID, "removeMessage").text


class SearchTask(AbstractTransaction):
    """Search for a task by title and return its ID.

    Args:
        with_title (str): The title of the task to search for.

    Returns:
        str: The ID of the task found.
    """

    def __init__(self, driver):
        self._driver: webdriver.Chrome = driver

    def do(self, with_title: str):
        self._driver.find_element(By.ID, "searchTitle").send_keys(with_title)
        self._driver.find_element(
            By.CSS_SELECTOR, "body > section:nth-child(3) > button:nth-child(4)"
        ).click()
        return self._driver.find_element(
            By.CSS_SELECTOR, "#taskTable > tbody > tr > td:nth-child(1)"
        ).text


class IsEqualToVariationsOf(IAssertion):
    """Custom assertion to check if the actual value matches expected variations."""

    def asserts(self, actual, expected):
        if actual.lower() == expected.lower():
            return True
        raise AssertionError


@pytest.fixture(scope="function")
def todo():
    app = Application(webdriver.Chrome())
    yield app
    app.undo()


def test_demo(todo: Application):
    todo.when(AddTask, with_title="do something").asserts(
        IsEqualToVariationsOf, "the task with ID 1 was created"
    )
    todo.when(SearchTask, with_title="do something").asserts(it.IsEqualTo, "1")
