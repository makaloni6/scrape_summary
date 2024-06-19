class Echidna:
    def __init__(self, driver):
        self.driver = driver
    
    def get_status(self):

        raise NotImplementedError

    def scrape(self):

        raise NotImplementedError